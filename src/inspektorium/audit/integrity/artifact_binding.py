"""Phase 7B — artifact / representation robustness: deterministic release gate.

Operates on a :class:`ForensicRecord` (the structured CLAIM → PROVENANCE → EVIDENCE →
INTERNAL FINDING → CLIENT FINDING chain) and enforces, **deterministically and without
any model call**, that a client-facing representation stays bound to its internally
validated parent. The mandatory Phase-7B representation-QA controls are:

- **finding / artifact binding** — a client finding must reference an existing parent
  finding, existing evidence, evidence that belongs to that finding's context, and the
  parent's frozen claim provenance (``artifact_source_binding_drift``);
- **summary-strength monotonicity** — a client summary may not assert a stronger
  evidential status than its parent finding allows (``summary_strength_escalation``);
- **evidence symmetry** — materially relevant evidence in an opposing / qualifying
  direction may not silently disappear from the client representation
  (``asymmetric_evidence_selection``);
- **value-origin provenance** — a system-derived value may not be represented as a
  source-reported literature fact (or vice versa), and an unresolved origin may not ship
  (``model_output_to_literature_fact`` / ``source_reported_to_modelled_fact`` /
  ``unresolved_value_origin``); source/derivation bindings must resolve;
- **search-scope binding** — a bounded negative finding may not be broadened into a
  global non-existence claim, a search-dependent assertion must resolve a basis, and a
  narrower client scope must resolve its narrower evidence basis
  (``search_scope_to_world_generalization`` / ``unresolved_search_scope`` /
  ``artifact_source_binding_drift``).

These controls are wired into one consolidated gate-evaluation entrypoint,
:func:`evaluate_artifact_release`, via the explicit ordered registry
:data:`MANDATORY_PHASE7B_CHECKS`. The gate collects ALL findings (no early exit), rolls
severities up deterministically using the existing
:class:`~inspektorium.audit.schemas.FailureSeverity` (no second severity taxonomy, no aggregate
score), and returns a machine-readable :class:`ReleaseReport`. Releasability requires
complete non-zero mandatory-gate coverage as well as no critical/major finding.
Prospective official output is written only by
:func:`inspektorium.audit.integrity.release_boundary.release_official_artifact`, which freshly executes and
authenticates this report before atomic promotion.

Scope discipline: the gate operates on the *structured* / pre-render artifact only — no
LLM critic, no PDF/HTML post-render extraction, no literature-search automation. These
pipeline-QA codes are a SEPARATE namespace and are never members of the frozen four-label
claim taxonomy. A PASS means Phase-7B contract compliance, NOT scientific truth or
evidence completeness.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from inspektorium.audit.forensics.forensic_report import (
    canonical_report_bytes,
    leakage_findings,
)
from inspektorium.audit.schemas import (
    ALLOWED_CLIENT_ORIGINS,
    ALLOWED_CLIENT_SCOPES,
    ASSERTION_SCOPES,
    CLIENT_ORIGIN_CLAIMS,
    SCOPE_DOCUMENTED_SEARCH,
    SCOPE_REVIEWED_SET,
    SCOPE_SOURCE_LOCAL,
    SEARCH_SCOPE_TYPES,
    SUMMARY_STRENGTH_ORDER,
    VALUE_ORIGIN_SOURCE_REPORTED,
    VALUE_ORIGIN_SYSTEM_DERIVED,
    VALUE_ORIGINS,
    EvidenceRole,
    FailureSeverity,
    ForensicRecord,
)
from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Pipeline-QA code namespace (NEVER a claim label)
# ---------------------------------------------------------------------------

QA_ASYMMETRIC_EVIDENCE_SELECTION = "asymmetric_evidence_selection"
QA_ARTIFACT_SOURCE_BINDING_DRIFT = "artifact_source_binding_drift"
# ``summary_strength_escalation`` is the client-strength specialization of the broader
# ``compression_overclaim`` code; kept explicit here because it maps to a distinct check.
QA_SUMMARY_STRENGTH_ESCALATION = "summary_strength_escalation"
# A system-derived value/proposition represented downstream as source-reported /
# published evidence (Phase-7B slice 2). SYSTEM-DERIVED VALUE ≠ SOURCE-REPORTED VALUE.
QA_MODEL_OUTPUT_TO_LITERATURE_FACT = "model_output_to_literature_fact"
# The reverse falsification: a source-reported value represented downstream as an Agent
# Arena modelled/derived value. Provenance is categorical — neither direction is allowed.
QA_SOURCE_REPORTED_TO_MODELLED_FACT = "source_reported_to_modelled_fact"
# A client-visible quantitative value whose internal origin is unresolved (fail-closed,
# curator hardening). NO VALUE ORIGIN ≠ SOURCE-REPORTED.
QA_UNRESOLVED_VALUE_ORIGIN = "unresolved_value_origin"
# A bounded search/result state represented downstream as a broader existence/non-
# existence claim than the documented search supports (Phase-7B slice 3).
# NOT FOUND ≠ DOES NOT EXIST.
QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION = "search_scope_to_world_generalization"
# A search-dependent negative assertion with no resolvable/substantiated search basis
# (fail-closed). MISSING SEARCH SCOPE ≠ GLOBAL SEARCH.
QA_UNRESOLVED_SEARCH_SCOPE = "unresolved_search_scope"

SYSTEM_QA_CODES = (
    QA_ASYMMETRIC_EVIDENCE_SELECTION,
    QA_ARTIFACT_SOURCE_BINDING_DRIFT,
    QA_SUMMARY_STRENGTH_ESCALATION,
    QA_MODEL_OUTPUT_TO_LITERATURE_FACT,
    QA_SOURCE_REPORTED_TO_MODELLED_FACT,
    QA_UNRESOLVED_VALUE_ORIGIN,
    QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION,
    QA_UNRESOLVED_SEARCH_SCOPE,
)

# The frozen claim taxonomy — QA codes must stay disjoint from it.
CLAIM_LABELS = (
    "solid",
    "overclaim",
    "correlation_vs_causation",
    "mechanism_vs_evidence",
)

# Code → severity. For this slice every gate failure is release-blocking (a wrong
# binding, a material omission, or a strength escalation each makes the artifact
# unsafe to release).
QA_CODE_SEVERITY = {
    QA_ASYMMETRIC_EVIDENCE_SELECTION: FailureSeverity.CRITICAL,
    QA_ARTIFACT_SOURCE_BINDING_DRIFT: FailureSeverity.CRITICAL,
    QA_SUMMARY_STRENGTH_ESCALATION: FailureSeverity.CRITICAL,
    QA_MODEL_OUTPUT_TO_LITERATURE_FACT: FailureSeverity.CRITICAL,
    QA_SOURCE_REPORTED_TO_MODELLED_FACT: FailureSeverity.CRITICAL,
    QA_UNRESOLVED_VALUE_ORIGIN: FailureSeverity.CRITICAL,
    QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION: FailureSeverity.CRITICAL,
    QA_UNRESOLVED_SEARCH_SCOPE: FailureSeverity.CRITICAL,
}

# Severities that block a release. "BLOCKER" maps to CRITICAL in the existing
# FailureSeverity convention; MAJOR also blocks.
BLOCKING_SEVERITIES = (FailureSeverity.CRITICAL, FailureSeverity.MAJOR)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


class BindingFinding(BaseModel):
    """One deterministic QA finding from the binding gate."""

    code: str
    severity: str  # FailureSeverity value
    check: str  # which binding check produced it (A..F)
    detail: str
    client_finding_id: str = ""
    refs: list[str] = Field(default_factory=list)  # evidence / finding ids involved


class BindingResult(BaseModel):
    """Outcome of the final binding gate over a whole record."""

    record_id: str = ""
    findings: list[BindingFinding] = Field(default_factory=list)
    releasable: bool = True
    blocker_count: int = 0
    major_count: int = 0

    def codes(self) -> list[str]:
        return [f.code for f in self.findings]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def compute_content_fingerprint(exact_claim_text: str, provenance_state: str) -> str:
    """Recomputable SHA-256 over the frozen claim text + its provenance state.

    Deterministic and offline; any consumer can recompute and compare to detect
    silent drift between a frozen snapshot and a later reconstruction.
    """
    payload = f"{provenance_state}\n{exact_claim_text}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _strength_rank(label: str) -> int | None:
    try:
        return SUMMARY_STRENGTH_ORDER.index(label)
    except ValueError:
        return None


def _coarse_direction(role: EvidenceRole) -> str:
    """Collapse EvidenceRole to a two-valued direction for symmetry accounting."""
    return (
        "supports_finding"
        if role == EvidenceRole.SUPPORTING
        else "opposes_or_qualifies_finding"
    )


def _unresolved_value_finding(eid: str, cf_id: str) -> BindingFinding:
    """Fail-closed finding: a client-visible value whose internal origin is unresolved."""
    return BindingFinding(
        code=QA_UNRESOLVED_VALUE_ORIGIN,
        severity=QA_CODE_SEVERITY[QA_UNRESOLVED_VALUE_ORIGIN].value,
        check="VF",
        client_finding_id=cf_id,
        refs=[eid],
        detail=(
            f"client-visible value {eid!r} has an unresolved internal value_origin; "
            f"a missing origin must not be treated as source-reported (fail closed)"
        ),
    )


def load_forensic_record(path: str | Path) -> ForensicRecord:
    """Load a pipeline-QA ForensicRecord fixture (JSON). Separate from task_loader.

    Rejects any record carrying private-identity / private-path leakage (reuses the
    forensic_report leakage vocabulary).
    """
    path = Path(path)
    with open(path) as f:
        data = json.load(f)
    leaks = leakage_findings(data)
    if leaks:
        raise ValueError(f"pipeline-QA fixture contains private identity/path: {leaks}")
    return ForensicRecord(**data)


# ---------------------------------------------------------------------------
# QA primitive: evidence symmetry
# ---------------------------------------------------------------------------


def check_evidence_symmetry(record: ForensicRecord) -> list[BindingFinding]:
    """First independent 7B QA primitive (deterministic).

    Question: has materially relevant source evidence in an opposing / qualifying
    direction been omitted from the client representation in a way that would make
    the conclusion stronger, weaker, or less qualified? Direction-neutral: it does
    not matter which side benefits.

    For each client finding with a resolvable parent, it compares the material
    evidence bound to the parent finding against the evidence the client finding
    references. If a whole direction present in the parent's material evidence is
    entirely dropped by the client, it flags ``asymmetric_evidence_selection``.
    """
    findings: list[BindingFinding] = []
    ev_by_id = {e.evidence_id: e for e in record.evidence}
    find_by_id = {f.finding_id: f for f in record.findings}

    for cf in record.client_findings:
        parent = find_by_id.get(cf.parent_finding_id)
        if parent is None:
            continue  # binding gate reports the missing parent separately (check A)

        # evidence_symmetry 1.1.0 (Package B, P7-F1): every item the parent finding itself binds
        # as supporting or contrary counts for direction accounting. The producer's material flag
        # is not an opt-out (docs/phase8_semantic_contract.md: applicability from actual objects).
        parent_ev_ids = set(parent.supporting_evidence_ids) | set(
            parent.contrary_evidence_ids
        )
        material_ids = {eid for eid in parent_ev_ids if eid in ev_by_id}
        if not material_ids:
            continue

        parent_dirs = {_coarse_direction(ev_by_id[eid].role) for eid in material_ids}
        kept_ids = material_ids & set(cf.referenced_evidence_ids)
        kept_dirs = {_coarse_direction(ev_by_id[eid].role) for eid in kept_ids}
        missing_dirs = parent_dirs - kept_dirs
        if missing_dirs:
            dropped = sorted(material_ids - kept_ids)
            findings.append(
                BindingFinding(
                    code=QA_ASYMMETRIC_EVIDENCE_SELECTION,
                    severity=QA_CODE_SEVERITY[QA_ASYMMETRIC_EVIDENCE_SELECTION].value,
                    check="E",
                    client_finding_id=cf.client_finding_id,
                    refs=dropped,
                    detail=(
                        "materially relevant evidence in direction(s) "
                        f"{sorted(missing_dirs)} was dropped from the client finding "
                        f"(omitted material ids: {dropped})"
                    ),
                )
            )
    return findings


# ---------------------------------------------------------------------------
# QA primitive: derived / source-reported value origin
# ---------------------------------------------------------------------------


def check_value_origin(record: ForensicRecord) -> list[BindingFinding]:
    """Deterministic value-origin QA primitive (Phase-7B slice 2).

    Enforces ``SYSTEM-DERIVED VALUE ≠ SOURCE-REPORTED VALUE`` on structured objects
    only (no NLP). FAIL-CLOSED: an unresolved internal origin never counts as
    source-reported. For each client finding it checks:

    - **fail-closed origin** — a client-visible value (an explicit value claim, or a
      referenced value carrying a ``reported_value``) whose parent ``value_origin`` is
      unresolved (``None`` / not a resolved origin) → ``unresolved_value_origin``;
    - **categorical origin compatibility** — value origin is categorical, not a ranking.
      A client may keep the same category or drop to ``unspecified``; it may never rewrite
      one category into the other. derived → source_reported →
      ``model_output_to_literature_fact``; source_reported → derived →
      ``source_reported_to_modelled_fact``;
    - **no invented lineage** — a client may not attribute a derived value to sources
      outside its derivation lineage → ``artifact_source_binding_drift``;
    - **value-origin resolves** — a client value claim must point to a real evidence
      item → ``artifact_source_binding_drift``;
    - **source-reported retains POSITIVE binding** — a referenced source-reported value
      must have a source id AND a locator/span (``exact_reference``) →
      ``artifact_source_binding_drift``;
    - **derived inputs resolve** — a referenced system-derived value's input evidence
      ids must all exist → ``artifact_source_binding_drift``.
    """
    findings: list[BindingFinding] = []
    ev_by_id = {e.evidence_id: e for e in record.evidence}

    def drift(check: str, detail: str, cf_id: str, refs: list[str]) -> None:
        findings.append(
            BindingFinding(
                code=QA_ARTIFACT_SOURCE_BINDING_DRIFT,
                severity=QA_CODE_SEVERITY[QA_ARTIFACT_SOURCE_BINDING_DRIFT].value,
                check=check,
                detail=detail,
                client_finding_id=cf_id,
                refs=refs,
            )
        )

    for cf in record.client_findings:
        flagged_unresolved: set[str] = set()  # dedupe per client finding

        # (a) explicit per-value origin claims: fail-closed, then categorical compatibility.
        for vc in cf.value_claims:
            ev = ev_by_id.get(vc.evidence_id)
            if ev is None:
                drift(
                    "VA",
                    f"client value claim references unknown evidence "
                    f"{vc.evidence_id!r}",
                    cf.client_finding_id,
                    [vc.evidence_id],
                )
                continue
            if ev.value_origin not in VALUE_ORIGINS:
                # FAIL-CLOSED: parent origin unresolved — cannot ship this client value.
                if vc.evidence_id not in flagged_unresolved:
                    flagged_unresolved.add(vc.evidence_id)
                    findings.append(
                        _unresolved_value_finding(vc.evidence_id, cf.client_finding_id)
                    )
                continue
            if vc.claimed_origin not in CLIENT_ORIGIN_CLAIMS:
                drift(
                    "VA",
                    f"client value claim on {vc.evidence_id!r} has unknown "
                    f"claimed_origin {vc.claimed_origin!r}",
                    cf.client_finding_id,
                    [vc.evidence_id],
                )
            elif vc.claimed_origin not in ALLOWED_CLIENT_ORIGINS[ev.value_origin]:
                # Categorical falsification (not a ranking): the client rewrote one
                # provenance category into the other. Both directions are release-blocking.
                if ev.value_origin == VALUE_ORIGIN_SYSTEM_DERIVED:
                    code = QA_MODEL_OUTPUT_TO_LITERATURE_FACT
                else:  # internal source_reported represented as derived
                    code = QA_SOURCE_REPORTED_TO_MODELLED_FACT
                findings.append(
                    BindingFinding(
                        code=code,
                        severity=QA_CODE_SEVERITY[code].value,
                        check="VB",
                        client_finding_id=cf.client_finding_id,
                        refs=[vc.evidence_id, ev.value_origin, vc.claimed_origin],
                        detail=(
                            f"client represents value {vc.evidence_id!r} as "
                            f"{vc.claimed_origin!r} but its internal origin is the distinct "
                            f"category {ev.value_origin!r} (provenance may be omitted, not "
                            f"rewritten into a different origin)"
                        ),
                    )
                )
            # invented lineage: attributed sources must lie within the derivation lineage.
            if ev.value_origin == VALUE_ORIGIN_SYSTEM_DERIVED and vc.claimed_source_ids:
                lineage = {
                    ev_by_id[iid].source_id
                    for iid in ev.input_evidence_ids
                    if iid in ev_by_id
                }
                invented = sorted(s for s in vc.claimed_source_ids if s not in lineage)
                if invented:
                    drift(
                        "VE",
                        f"client attributes derived value {vc.evidence_id!r} to "
                        f"source(s) {invented} absent from its derivation lineage "
                        f"{sorted(lineage)}",
                        cf.client_finding_id,
                        invented,
                    )

        # (b) structural integrity of referenced values by origin.
        for eid in cf.referenced_evidence_ids:
            ev = ev_by_id.get(eid)
            if ev is None:
                continue  # unknown-id drift is reported by the binding gate (check B)
            # FAIL-CLOSED: a client-visible quantitative value must have a resolved origin.
            if ev.reported_value is not None and ev.value_origin not in VALUE_ORIGINS:
                if eid not in flagged_unresolved:
                    flagged_unresolved.add(eid)
                    findings.append(
                        _unresolved_value_finding(eid, cf.client_finding_id)
                    )
                continue
            if ev.value_origin == VALUE_ORIGIN_SOURCE_REPORTED:
                # A positive provenance claim requires positive source binding.
                if not ev.source_id:
                    drift(
                        "VC",
                        f"source-reported value {eid!r} has no resolvable source "
                        f"binding (empty source_id)",
                        cf.client_finding_id,
                        [eid],
                    )
                elif not ev.exact_reference:
                    drift(
                        "VC",
                        f"source-reported value {eid!r} has no source locator/span "
                        f"(exact_reference); source-reported requires positive "
                        f"binding",
                        cf.client_finding_id,
                        [eid],
                    )
            if ev.value_origin == VALUE_ORIGIN_SYSTEM_DERIVED:
                missing = sorted(
                    iid for iid in ev.input_evidence_ids if iid not in ev_by_id
                )
                if missing:
                    drift(
                        "VD",
                        f"system-derived value {eid!r} references unknown input "
                        f"evidence {missing}",
                        cf.client_finding_id,
                        missing,
                    )
    return findings


# ---------------------------------------------------------------------------
# QA primitive: search-scope binding for negative evidence claims
# ---------------------------------------------------------------------------


def _scope_substantiated(scope) -> bool:
    """True iff a SearchScope carries positive machine-readable evidence of a search."""
    if scope.scope_type == SCOPE_REVIEWED_SET:
        return bool(scope.reviewed_source_ids)
    if scope.scope_type == SCOPE_DOCUMENTED_SEARCH:
        return bool(
            scope.reviewed_source_ids
            or scope.resources
            or scope.query_terms
            or scope.date_cutoff
        )
    return False


def _resolve_basis(assertion, scope_by_id, ev_ids) -> str | None:
    """Derive the actual documented BASIS breadth of a negative assertion, or None.

    Basis comes from real support, never from a self-declared label: a resolved and
    substantiated ``SearchScope`` (reviewed_set / documented_search), or resolvable
    ``source_local_evidence_ids`` (direct inspection). Otherwise unresolved → None.
    """
    if assertion.search_scope_id:
        scope = scope_by_id.get(assertion.search_scope_id)
        if scope is None or scope.scope_type not in SEARCH_SCOPE_TYPES:
            return None
        if not _scope_substantiated(scope):
            return None  # a claimed search with no record — fail closed
        return scope.scope_type
    if assertion.source_local_evidence_ids and all(
        eid in ev_ids for eid in assertion.source_local_evidence_ids
    ):
        return SCOPE_SOURCE_LOCAL
    return None


def _source_local_basis_resolves(assertion, ev_by_id) -> bool:
    """True iff a concrete source-local evidence basis resolves for this assertion.

    A source-local client claim ("the cited source does not contain X") makes a positive
    statement about a specific source; it requires direct-inspection evidence that each
    resolves to a real source (``source_local_evidence_ids`` → evidence item → non-empty
    ``source_id``). An empty or dangling basis fails closed — a narrower scope label must
    not invent a source basis.
    """
    ids = assertion.source_local_evidence_ids
    if not ids:
        return False
    return all(
        ev_by_id.get(eid) is not None and bool(ev_by_id[eid].source_id) for eid in ids
    )


def _reviewed_set_resolves(assertion, scope_by_id) -> bool:
    """True iff a concrete reviewed source set resolves for this assertion.

    A reviewed-set client claim ("X was not identified in the reviewed sources") asserts a
    specific, enumerated review basis. It requires the assertion's ``SearchScope`` to carry a
    non-empty ``reviewed_source_ids``. A ``documented_search`` scope does NOT by itself prove
    an explicit reviewed set exists (its search may be substantiated only by resources /
    query terms / date cutoff) — so the reviewed set must actually be represented.
    """
    if not assertion.search_scope_id:
        return False
    scope = scope_by_id.get(assertion.search_scope_id)
    if scope is None or scope.scope_type not in SEARCH_SCOPE_TYPES:
        return False
    return bool(scope.reviewed_source_ids)


def check_search_scope(record: ForensicRecord) -> list[BindingFinding]:
    """Deterministic search-scope QA primitive (Phase-7B slice 3).

    Enforces ``NOT FOUND ≠ DOES NOT EXIST`` on structured objects only (no NLP). A
    client negative assertion may keep or NARROW its basis scope, never broaden it; a
    global-nonexistence claim is supported by no basis by default. Curator hardening:
    scope containment is necessary but NOT sufficient — a narrower client scope is valid
    only if the narrower evidence basis it asserts actually resolves. A narrower scope
    label must never silently invent a narrower basis (NARROWER SCOPE WITHOUT NARROWER
    BASIS = INVENTED PROVENANCE). Checks:

    - **binding** — internal assertion resolves to a finding; a client negative assertion
      resolves to an internal assertion → ``artifact_source_binding_drift``;
    - **fail-closed scope** — a search-dependent client assertion whose internal basis is
      unresolved / unsubstantiated (no basis of any kind) → ``unresolved_search_scope``;
    - **no broadening** — a client scope broader than the documented basis supports (incl.
      any global-nonexistence claim) → ``search_scope_to_world_generalization``;
    - **narrower basis resolves** — a client that narrows to ``source_local`` without a
      concrete source-local evidence basis, or to ``reviewed_set`` without a represented
      reviewed source set, is fabricating the narrower provenance →
      ``artifact_source_binding_drift``.
    """
    findings: list[BindingFinding] = []
    scope_by_id = {s.search_scope_id: s for s in record.search_scopes}
    assertion_by_id = {a.assertion_id: a for a in record.negative_assertions}
    find_ids = {f.finding_id for f in record.findings}
    ev_by_id = {e.evidence_id: e for e in record.evidence}
    ev_ids = set(ev_by_id)

    def drift(check: str, detail: str, cf_id: str, refs: list[str]) -> None:
        findings.append(
            BindingFinding(
                code=QA_ARTIFACT_SOURCE_BINDING_DRIFT,
                severity=QA_CODE_SEVERITY[QA_ARTIFACT_SOURCE_BINDING_DRIFT].value,
                check=check,
                detail=detail,
                client_finding_id=cf_id,
                refs=refs,
            )
        )

    # Internal assertions must bind to a real finding.
    for a in record.negative_assertions:
        if a.finding_id not in find_ids:
            drift(
                "SA",
                f"negative assertion {a.assertion_id!r} binds to unknown finding "
                f"{a.finding_id!r}",
                "",
                [a.assertion_id, a.finding_id],
            )

    for cf in record.client_findings:
        for cna in cf.client_negative_assertions:
            a = assertion_by_id.get(cna.assertion_id)
            if a is None:
                drift(
                    "SA",
                    f"client negative assertion references unknown internal "
                    f"assertion {cna.assertion_id!r}",
                    cf.client_finding_id,
                    [cna.assertion_id],
                )
                continue
            if cna.client_scope not in ASSERTION_SCOPES:
                drift(
                    "SA",
                    f"client negative assertion on {cna.assertion_id!r} has unknown "
                    f"client_scope {cna.client_scope!r}",
                    cf.client_finding_id,
                    [cna.assertion_id],
                )
                continue
            basis = _resolve_basis(a, scope_by_id, ev_ids)
            if basis is None:
                # FAIL-CLOSED: no resolvable/substantiated search basis.
                findings.append(
                    BindingFinding(
                        code=QA_UNRESOLVED_SEARCH_SCOPE,
                        severity=QA_CODE_SEVERITY[QA_UNRESOLVED_SEARCH_SCOPE].value,
                        check="SB",
                        client_finding_id=cf.client_finding_id,
                        refs=[cna.assertion_id],
                        detail=(
                            f"client negative assertion {cna.assertion_id!r} claims scope "
                            f"{cna.client_scope!r} but no search basis resolves; missing "
                            f"search scope is not a global search (fail closed)"
                        ),
                    )
                )
                continue
            if cna.client_scope not in ALLOWED_CLIENT_SCOPES[basis]:
                findings.append(
                    BindingFinding(
                        code=QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION,
                        severity=QA_CODE_SEVERITY[
                            QA_SEARCH_SCOPE_TO_WORLD_GENERALIZATION
                        ].value,
                        check="SC",
                        client_finding_id=cf.client_finding_id,
                        refs=[cna.assertion_id, basis, cna.client_scope],
                        detail=(
                            f"client asserts scope {cna.client_scope!r} broader than the "
                            f"documented basis {basis!r} supports (a bounded search is not "
                            f"evidence of global (non-)existence)"
                        ),
                    )
                )
                continue
            # Curator hardening: containment holds, but a narrower scope is valid only if
            # the narrower evidence basis it asserts actually resolves. A narrower label
            # must not silently manufacture a source-local source or a reviewed set.
            if (
                cna.client_scope == SCOPE_SOURCE_LOCAL
                and not _source_local_basis_resolves(a, ev_by_id)
            ):
                drift(
                    "SD",
                    f"client narrows assertion {cna.assertion_id!r} to "
                    f"{SCOPE_SOURCE_LOCAL!r} but no concrete source-local evidence "
                    f"basis resolves (a narrower scope label may not invent a source "
                    f"basis)",
                    cf.client_finding_id,
                    [cna.assertion_id],
                )
            elif cna.client_scope == SCOPE_REVIEWED_SET and not _reviewed_set_resolves(
                a, scope_by_id
            ):
                drift(
                    "SD",
                    f"client narrows assertion {cna.assertion_id!r} to "
                    f"{SCOPE_REVIEWED_SET!r} but no reviewed source set is represented "
                    f"(a documented search does not by itself prove an explicit "
                    f"reviewed set)",
                    cf.client_finding_id,
                    [cna.assertion_id],
                )
    return findings


# ---------------------------------------------------------------------------
# QA primitive: finding / artifact binding + summary-strength monotonicity
# ---------------------------------------------------------------------------


def _binding_drift(
    check: str, detail: str, cf_id: str = "", refs: list[str] | None = None
) -> BindingFinding:
    return BindingFinding(
        code=QA_ARTIFACT_SOURCE_BINDING_DRIFT,
        severity=QA_CODE_SEVERITY[QA_ARTIFACT_SOURCE_BINDING_DRIFT].value,
        check=check,
        detail=detail,
        client_finding_id=cf_id,
        refs=refs or [],
    )


def check_finding_binding(record: ForensicRecord) -> list[BindingFinding]:
    """Deterministic structural-binding QA primitive.

    Checks per client finding: A the parent internal finding exists (NO CLIENT SUMMARY
    WITHOUT FINDING BINDING) · B referenced evidence ids exist · C referenced evidence
    belongs to the parent finding's context · F provenance resolves and matches the
    parent's frozen claim provenance. All failures reuse ``artifact_source_binding_drift``.
    A client finding whose parent cannot resolve (A) skips its own B/C/F — the missing
    parent is already reported, and the parent-dependent checks literally cannot run.
    """
    findings: list[BindingFinding] = []
    ev_by_id = {e.evidence_id: e for e in record.evidence}
    find_by_id = {f.finding_id: f for f in record.findings}
    prov_ids = {p.provenance_id for p in record.provenance}

    for cf in record.client_findings:
        # A — parent finding must exist.
        parent = find_by_id.get(cf.parent_finding_id)
        if parent is None:
            findings.append(
                _binding_drift(
                    "A",
                    f"client finding {cf.client_finding_id!r} binds to unknown parent "
                    f"finding {cf.parent_finding_id!r}",
                    cf.client_finding_id,
                    [cf.parent_finding_id],
                )
            )
            continue  # remaining parent-dependent checks cannot run

        parent_ev_ids = set(parent.supporting_evidence_ids) | set(
            parent.contrary_evidence_ids
        )

        # B — referenced evidence must exist.
        for eid in cf.referenced_evidence_ids:
            if eid not in ev_by_id:
                findings.append(
                    _binding_drift(
                        "B",
                        f"client finding {cf.client_finding_id!r} references unknown "
                        f"evidence id {eid!r}",
                        cf.client_finding_id,
                        [eid],
                    )
                )
        # C — referenced (existing) evidence must belong to the parent finding's context.
        for eid in cf.referenced_evidence_ids:
            if eid in ev_by_id and eid not in parent_ev_ids:
                findings.append(
                    _binding_drift(
                        "C",
                        f"client finding {cf.client_finding_id!r} references evidence "
                        f"{eid!r} that is not bound to parent finding "
                        f"{parent.finding_id!r} (evidence used out of context)",
                        cf.client_finding_id,
                        [eid],
                    )
                )

        # F — provenance reference must resolve and match the parent's frozen provenance.
        if cf.provenance_id not in prov_ids:
            findings.append(
                _binding_drift(
                    "F",
                    f"client finding {cf.client_finding_id!r} references unknown "
                    f"provenance {cf.provenance_id!r}",
                    cf.client_finding_id,
                    [cf.provenance_id],
                )
            )
        elif cf.provenance_id != parent.provenance_id:
            findings.append(
                _binding_drift(
                    "F",
                    f"client finding {cf.client_finding_id!r} resolves to provenance "
                    f"{cf.provenance_id!r} but its parent finding froze "
                    f"{parent.provenance_id!r} (provenance mismatch)",
                    cf.client_finding_id,
                    [cf.provenance_id, parent.provenance_id],
                )
            )
    if record.phase8 is not None:
        # Every existing binding entrypoint checks a present semantic payload;
        # clients cannot route an invalid Phase-8 record around the runner.
        from inspektorium.audit.forensics.semantics import evaluate_phase8

        assessment = evaluate_phase8(record)
        if assessment.technical_status != "completed":
            findings.append(
                _binding_drift(
                    "P8",
                    "Phase-8 output binding incomplete: "
                    + "; ".join(assessment.reasons),
                )
            )
    return findings


def check_summary_strength(record: ForensicRecord) -> list[BindingFinding]:
    """Deterministic summary-strength monotonicity QA primitive (minimal, no NLP).

    Freeze: CLIENT SUMMARY ≤ INTERNALLY VALIDATED FINDING. For each client finding with a
    resolvable parent, the client's declared ``client_strength`` may not exceed the
    parent's ``allowed_summary_strength`` on the ordered strength lattice
    (``summary_strength_escalation``); an unknown strength label on either side is a
    binding drift. A client finding whose parent cannot resolve is skipped here — the
    missing parent is reported by :func:`check_finding_binding`, and strength cannot be
    assessed without the parent ceiling.
    """
    findings: list[BindingFinding] = []
    find_by_id = {f.finding_id: f for f in record.findings}

    for cf in record.client_findings:
        parent = find_by_id.get(cf.parent_finding_id)
        if parent is None:
            continue  # unresolvable dependency — reported by check_finding_binding
        c_rank = _strength_rank(cf.client_strength)
        p_rank = _strength_rank(parent.allowed_summary_strength)
        if c_rank is None:
            findings.append(
                _binding_drift(
                    "D",
                    f"client finding {cf.client_finding_id!r} has unknown "
                    f"client_strength {cf.client_strength!r}",
                    cf.client_finding_id,
                )
            )
        elif p_rank is None:
            findings.append(
                _binding_drift(
                    "D",
                    f"parent finding {parent.finding_id!r} has unknown "
                    f"allowed_summary_strength {parent.allowed_summary_strength!r}",
                    cf.client_finding_id,
                )
            )
        elif c_rank > p_rank:
            findings.append(
                BindingFinding(
                    code=QA_SUMMARY_STRENGTH_ESCALATION,
                    severity=QA_CODE_SEVERITY[QA_SUMMARY_STRENGTH_ESCALATION].value,
                    check="D",
                    client_finding_id=cf.client_finding_id,
                    refs=[cf.client_strength, parent.allowed_summary_strength],
                    detail=(
                        f"client summary strength {cf.client_strength!r} exceeds the parent "
                        f"finding's allowed strength {parent.allowed_summary_strength!r}"
                    ),
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Consolidated Phase-7B gate evaluation (consumed by the official release boundary)
# ---------------------------------------------------------------------------
# Internal QA / release-control contract version. Compact; NOT a public API guarantee
# and NOT the frozen Forensic Report 6.3.0 (which is untouched). Bumped only when the
# serialized ReleaseReport contract or the mandatory-check set changes meaning.
PHASE7B_RELEASE_GATE_VERSION = "0.2.1"
PHASE7B_RELEASE_REPORT_SCHEMA_VERSION = "inspektorium.audit.phase7b_release_report/v2"
MANDATORY_PHASE7B_GATE_SET_ID = "inspektorium.audit.phase7b.mandatory"
MANDATORY_PHASE7B_GATE_SET_VERSION = "2.1.0"
PHASE7B_ASSURANCE_SCOPE = (
    "The deterministic gate stack verifies the represented structured inputs and their "
    "internal consistency under the tracked Phase-7B contract. It does not independently "
    "prove that producer-supplied scientific claims are true."
)


# The EXPLICIT, ordered, mandatory Phase-7B representation-QA control set. A future
# developer adding a release path invokes this registry — a control cannot be silently
# forgotten (see the coverage test). Each entry is (stable_name, deterministic_callable);
# every callable takes a ForensicRecord and returns list[BindingFinding], never raising
# for structural defects (it emits findings instead). Order is the canonical run order.
def _client_finding_population(record: ForensicRecord) -> int:
    return len(record.client_findings)


def _symmetry_population(record: ForensicRecord) -> int:
    """Client-finding contexts whose parent finding binds at least one existing evidence item.

    evidence_symmetry 1.1.0: the producer's ``material`` flag no longer removes a bound item.
    """
    evidence = {item.evidence_id: item for item in record.evidence}
    findings = {finding.finding_id: finding for finding in record.findings}
    eligible = 0
    for client in record.client_findings:
        parent = findings.get(client.parent_finding_id)
        if parent is None:
            continue
        parent_ids = set(parent.supporting_evidence_ids) | set(
            parent.contrary_evidence_ids
        )
        if any(eid in evidence for eid in parent_ids):
            eligible += 1
    return eligible


def _value_origin_population(record: ForensicRecord) -> int:
    """Distinct client-visible evidence values/references evaluated for origin binding."""
    evidence_ids = {item.evidence_id for item in record.evidence}
    visible: set[tuple[str, str]] = set()
    for client in record.client_findings:
        for evidence_id in client.referenced_evidence_ids:
            if evidence_id in evidence_ids:
                visible.add((client.client_finding_id, evidence_id))
        for claim in client.value_claims:
            if claim.evidence_id in evidence_ids:
                visible.add((client.client_finding_id, claim.evidence_id))
    return len(visible)


def _search_scope_population(record: ForensicRecord) -> int:
    return sum(
        len(client.client_negative_assertions) for client in record.client_findings
    )


@dataclass(frozen=True)
class MandatoryGateSpec:
    gate_id: str
    gate_version: str
    population: str
    check: Callable[[ForensicRecord], list[BindingFinding]]
    eligible_count: Callable[[ForensicRecord], int]


MANDATORY_PHASE7B_GATE_SPECS: tuple[MandatoryGateSpec, ...] = (
    MandatoryGateSpec(
        "finding_artifact_binding",
        "1.1.0",
        "client_findings",
        check_finding_binding,
        _client_finding_population,
    ),
    MandatoryGateSpec(
        "summary_strength_monotonicity",
        "1.0.0",
        "client_findings",
        check_summary_strength,
        _client_finding_population,
    ),
    MandatoryGateSpec(
        "evidence_symmetry",
        "1.1.0",
        "client_finding_material_evidence_contexts",
        check_evidence_symmetry,
        _symmetry_population,
    ),
    MandatoryGateSpec(
        "value_origin_provenance",
        "1.0.0",
        "client_visible_evidence_references",
        check_value_origin,
        _value_origin_population,
    ),
    MandatoryGateSpec(
        "search_scope_binding",
        "1.0.0",
        "client_negative_assertions",
        check_search_scope,
        _search_scope_population,
    ),
)

# Compatibility view for existing gate-level callers/tests. The authoritative specification is
# the richer immutable registry above; callers cannot provide or replace either registry.
MANDATORY_PHASE7B_CHECKS: tuple[tuple[str, object], ...] = tuple(
    (spec.gate_id, spec.check) for spec in MANDATORY_PHASE7B_GATE_SPECS
)


def mandatory_gate_set_fingerprint() -> str:
    """Fingerprint the tracked gate specification and implementation source."""
    payload = {
        "gate_set_id": MANDATORY_PHASE7B_GATE_SET_ID,
        "gate_set_version": MANDATORY_PHASE7B_GATE_SET_VERSION,
        "implementation_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "gates": [
            {
                "gate_id": spec.gate_id,
                "gate_version": spec.gate_version,
                "population": spec.population,
                "check": f"{spec.check.__module__}.{spec.check.__qualname__}",
                "eligibility": (
                    f"{spec.eligible_count.__module__}.{spec.eligible_count.__qualname__}"
                ),
            }
            for spec in MANDATORY_PHASE7B_GATE_SPECS
        ],
    }
    return hashlib.sha256(canonical_report_bytes(payload)).hexdigest()


# Deterministic severity roll-up order (worst → least). Reuses the existing
# FailureSeverity enum; no second severity taxonomy is introduced.
SEVERITY_ORDER = (
    FailureSeverity.CRITICAL,
    FailureSeverity.MAJOR,
    FailureSeverity.MODERATE,
    FailureSeverity.MINOR,
    FailureSeverity.STYLISTIC,
)
_SEVERITY_RANK = {s.value: i for i, s in enumerate(SEVERITY_ORDER)}


def record_fingerprint(record: ForensicRecord) -> str:
    """Recomputable SHA-256 over the canonical serialization of the evaluated record.

    Reuses the forensic_report canonical-bytes convention (sorted keys, fixed
    serialization) and the module's hashlib.sha256 convention, so any consumer can
    recompute it and verify that a given ReleaseReport was produced from exactly this
    structured record. No new hashing algorithm is introduced.
    """
    data = record.model_dump(mode="json")
    for extension in ("phase8", "phase8_taxonomy"):
        if getattr(record, extension) is None:
            data.pop(extension, None)  # Preserve legacy identity for absent extensions.
    return hashlib.sha256(canonical_report_bytes(data)).hexdigest()


def _finding_sort_key(f: BindingFinding) -> tuple:
    """Total, content-based order — stable under irrelevant input-collection reordering."""
    return (
        _SEVERITY_RANK.get(f.severity, len(SEVERITY_ORDER)),
        f.code,
        f.check,
        f.client_finding_id,
        tuple(f.refs),
        f.detail,
    )


class CheckRun(BaseModel):
    """Execution and coverage accounting for one mandatory control."""

    model_config = ConfigDict(extra="forbid")

    name: str
    gate_version: str = "1.0.0"
    status: str = "ran"
    population: str = ""
    eligible_count: int = Field(default=0, ge=0)
    evaluated_count: int = Field(default=0, ge=0)
    finding_count: int = Field(default=0, ge=0)
    unevaluated_count: int = Field(default=0, ge=0)
    coverage_state: str = "eligibility_unknown"
    status_reason: str = ""


class ReleaseReport(BaseModel):
    """Machine-readable Phase-7B structured-artifact release decision (internal QA).

    Answers exactly one question — RELEASABLE or NOT — from deterministic QA findings and
    frozen policy (no model call, no score). It identifies its input by fingerprint, lists
    every mandatory control that ran, lists all collected findings, counts severities, and
    states the decision with the blocking codes. It is NOT a public benchmark result, a
    client-facing scientific report, or a replacement for Forensic Report 6.3.0.
    """

    model_config = ConfigDict(extra="forbid")

    release_report_id: str
    release_report_schema_version: str = PHASE7B_RELEASE_REPORT_SCHEMA_VERSION
    forensic_record_id: str
    qa_contract_version: str = PHASE7B_RELEASE_GATE_VERSION
    record_fingerprint: str
    mandatory_gate_set_id: str = MANDATORY_PHASE7B_GATE_SET_ID
    mandatory_gate_set_version: str = MANDATORY_PHASE7B_GATE_SET_VERSION
    mandatory_gate_set_fingerprint: str
    checks_run: list[CheckRun] = Field(default_factory=list)
    findings: list[BindingFinding] = Field(default_factory=list)
    severity_counts: dict[str, int] = Field(default_factory=dict)
    releasable: bool = False
    decision_status: str = "gate_execution_error"
    blocking_codes: list[str] = Field(default_factory=list)
    decision_reason: str = "mandatory gate evidence has not been evaluated"
    assurance_scope: str = PHASE7B_ASSURANCE_SCOPE
    release_report_fingerprint: str = ""

    def codes(self) -> list[str]:
        return [f.code for f in self.findings]


def _severity_rollup(
    findings: list[BindingFinding],
) -> tuple[dict[str, int], bool, list[str]]:
    """Deterministic severity roll-up + frozen release policy (single source of truth).

    Counts findings across the full FailureSeverity range and derives releasability from
    the existing :data:`BLOCKING_SEVERITIES` convention (critical + major block; moderate /
    minor / stylistic do NOT). No aggregate quality/trust score is produced. Returns
    ``(severity_counts, releasable, blocking_codes)`` with ``blocking_codes`` sorted.
    """
    counts = {s.value: 0 for s in SEVERITY_ORDER}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    blocking_values = {s.value for s in BLOCKING_SEVERITIES}
    blocking_codes = sorted({f.code for f in findings if f.severity in blocking_values})
    return counts, (not blocking_codes), blocking_codes


def _run_mandatory_checks(
    record: ForensicRecord,
) -> tuple[list[CheckRun], list[BindingFinding]]:
    """Run every mandatory control in registry order, collecting ALL findings.

    No early exit: an independent failure in one control never suppresses another. Findings
    are returned in canonical (content-based) order so the result is stable for identical
    inputs and under irrelevant input-collection reordering.
    """
    checks_run: list[CheckRun] = []
    findings: list[BindingFinding] = []
    for spec in MANDATORY_PHASE7B_GATE_SPECS:
        try:
            eligible = spec.eligible_count(record)
            if (
                isinstance(eligible, bool)
                or not isinstance(eligible, int)
                or eligible < 0
            ):
                raise TypeError("eligibility count must be a non-negative integer")
        except (
            Exception
        ) as exc:  # pragma: no cover - exercised through adversarial monkeypatch
            checks_run.append(
                CheckRun(
                    name=spec.gate_id,
                    gate_version=spec.gate_version,
                    status="eligibility_unknown",
                    population=spec.population,
                    coverage_state="eligibility_unknown",
                    status_reason=f"{type(exc).__name__}: {exc}",
                )
            )
            continue
        try:
            produced = spec.check(record)
            if not isinstance(produced, list) or not all(
                isinstance(finding, BindingFinding) for finding in produced
            ):
                raise TypeError("gate result must be a list of BindingFinding objects")
        except Exception as exc:  # controlled fail-closed gate execution state
            checks_run.append(
                CheckRun(
                    name=spec.gate_id,
                    gate_version=spec.gate_version,
                    status="execution_error",
                    population=spec.population,
                    eligible_count=eligible,
                    evaluated_count=0,
                    unevaluated_count=eligible,
                    coverage_state="incomplete",
                    status_reason=f"{type(exc).__name__}: {exc}",
                )
            )
            continue
        coverage_state = (
            "evaluated_clean" if not produced else "evaluated_with_findings"
        )
        status_reason = ""
        if eligible == 0:
            coverage_state = "zero_eligibility"
            status_reason = "mandatory gate had zero eligible structured objects"
        checks_run.append(
            CheckRun(
                name=spec.gate_id,
                gate_version=spec.gate_version,
                status="ran",
                population=spec.population,
                eligible_count=eligible,
                evaluated_count=eligible,
                finding_count=len(produced),
                unevaluated_count=0,
                coverage_state=coverage_state,
                status_reason=status_reason,
            )
        )
        findings.extend(produced)
    findings.sort(key=_finding_sort_key)
    return checks_run, findings


def release_report_fingerprint(report: ReleaseReport | dict) -> str:
    payload = (
        report.model_dump(mode="json")
        if isinstance(report, ReleaseReport)
        else dict(report)
    )
    payload["release_report_fingerprint"] = ""
    return hashlib.sha256(canonical_report_bytes(payload)).hexdigest()


def validate_release_report_contract(report: ReleaseReport) -> list[str]:
    """Validate current gate identity, coverage accounting, decision, and integrity."""
    errors: list[str] = []
    expected_specs = MANDATORY_PHASE7B_GATE_SPECS
    if report.release_report_schema_version != PHASE7B_RELEASE_REPORT_SCHEMA_VERSION:
        errors.append("release report schema version mismatch")
    if report.qa_contract_version != PHASE7B_RELEASE_GATE_VERSION:
        errors.append("release report QA contract version mismatch")
    if report.mandatory_gate_set_id != MANDATORY_PHASE7B_GATE_SET_ID:
        errors.append("mandatory gate-set ID mismatch")
    if report.mandatory_gate_set_version != MANDATORY_PHASE7B_GATE_SET_VERSION:
        errors.append("mandatory gate-set version mismatch")
    if report.mandatory_gate_set_fingerprint != mandatory_gate_set_fingerprint():
        errors.append("mandatory gate-set fingerprint mismatch")
    if report.assurance_scope != PHASE7B_ASSURANCE_SCOPE:
        errors.append("release assurance scope mismatch")
    observed_identity = [
        (check.name, check.gate_version, check.population)
        for check in report.checks_run
    ]
    expected_identity = [
        (spec.gate_id, spec.gate_version, spec.population) for spec in expected_specs
    ]
    if observed_identity != expected_identity:
        errors.append(
            "mandatory gate identities, versions, populations, or order mismatch"
        )
    allowed_statuses = {"ran", "execution_error", "eligibility_unknown"}
    allowed_coverage = {
        "evaluated_clean",
        "evaluated_with_findings",
        "zero_eligibility",
        "incomplete",
        "eligibility_unknown",
    }
    for check in report.checks_run:
        if check.status not in allowed_statuses:
            errors.append(f"gate {check.name} has unknown execution status")
        if check.coverage_state not in allowed_coverage:
            errors.append(f"gate {check.name} has unknown coverage state")
        if check.evaluated_count > check.eligible_count:
            errors.append(f"gate {check.name} evaluated count exceeds eligibility")
        if check.unevaluated_count != check.eligible_count - check.evaluated_count:
            errors.append(f"gate {check.name} has inconsistent unevaluated count")
        if check.status == "ran":
            if (
                check.evaluated_count != check.eligible_count
                or check.unevaluated_count != 0
            ):
                errors.append(
                    f"gate {check.name} ran without complete population coverage"
                )
            expected_coverage = (
                "zero_eligibility"
                if check.eligible_count == 0
                else "evaluated_with_findings"
                if check.finding_count
                else "evaluated_clean"
            )
            if check.coverage_state != expected_coverage:
                errors.append(
                    f"gate {check.name} coverage state contradicts its counters"
                )
        elif check.status == "execution_error":
            if (
                check.evaluated_count != 0
                or check.unevaluated_count != check.eligible_count
            ):
                errors.append(
                    f"gate {check.name} execution error has inconsistent counters"
                )
            if check.finding_count != 0 or check.coverage_state != "incomplete":
                errors.append(
                    f"gate {check.name} execution error has inconsistent state"
                )
        elif check.status == "eligibility_unknown":
            if any(
                (
                    check.eligible_count,
                    check.evaluated_count,
                    check.finding_count,
                    check.unevaluated_count,
                )
            ):
                errors.append(
                    f"gate {check.name} unknown eligibility has non-zero counters"
                )
            if check.coverage_state != "eligibility_unknown":
                errors.append(
                    f"gate {check.name} unknown eligibility has inconsistent state"
                )
    if sum(check.finding_count for check in report.checks_run) != len(report.findings):
        errors.append("per-gate finding counts do not match release-report findings")
    (
        expected_counts,
        expected_releasable,
        expected_codes,
        expected_status,
        expected_reason,
    ) = _decision_from_evidence(report.checks_run, report.findings)
    if report.severity_counts != expected_counts:
        errors.append("release-report severity counts are inconsistent")
    if report.releasable != expected_releasable:
        errors.append("release-report releasable state is inconsistent")
    if report.blocking_codes != expected_codes:
        errors.append("release-report blocking codes are inconsistent")
    if (
        report.decision_status != expected_status
        or report.decision_reason != expected_reason
    ):
        errors.append("release-report consolidated decision is inconsistent")
    if report.release_report_fingerprint != release_report_fingerprint(report):
        errors.append("release report fingerprint mismatch")
    return errors


def _decision_from_evidence(
    checks_run: list[CheckRun], findings: list[BindingFinding]
) -> tuple[dict[str, int], bool, list[str], str, str]:
    counts, finding_releasable, blocking_codes = _severity_rollup(findings)
    if any(
        check.status in {"execution_error", "eligibility_unknown"}
        for check in checks_run
    ):
        return (
            counts,
            False,
            blocking_codes,
            "gate_execution_error",
            (
                "one or more mandatory gates could not establish and evaluate eligibility"
            ),
        )
    if any(check.eligible_count == 0 for check in checks_run):
        names = [check.name for check in checks_run if check.eligible_count == 0]
        return (
            counts,
            False,
            blocking_codes,
            "zero_eligibility",
            (
                "mandatory gate zero eligibility (not evaluated-and-clean): "
                + ", ".join(names)
            ),
        )
    if any(
        check.evaluated_count != check.eligible_count or check.unevaluated_count != 0
        for check in checks_run
    ):
        return (
            counts,
            False,
            blocking_codes,
            "incomplete_coverage",
            (
                "one or more mandatory gates did not evaluate the complete eligible population"
            ),
        )
    if not finding_releasable:
        n = sum(counts[severity.value] for severity in BLOCKING_SEVERITIES)
        return (
            counts,
            False,
            blocking_codes,
            "not_releasable",
            (f"blocked by {n} critical/major finding(s): {', '.join(blocking_codes)}"),
        )
    return (
        counts,
        True,
        blocking_codes,
        "releasable",
        (
            "all mandatory gates evaluated non-zero eligible populations with no blocking findings"
        ),
    )


def evaluate_artifact_release(record: ForensicRecord) -> ReleaseReport:
    """Consolidated Phase-7B structured-artifact gate evaluation (deterministic, offline).

    One entrypoint that runs every mandatory representation-QA control
    (:data:`MANDATORY_PHASE7B_CHECKS`) over the structured client representation, collects
    all findings without early exit, rolls severities up deterministically, and produces a
    single machine-readable release decision:

        releasable == complete_nonzero_coverage AND critical_count == 0 AND major_count == 0

    using the existing :class:`~inspektorium.audit.schemas.FailureSeverity` enum (no second
    severity taxonomy, no aggregate score). Callers using :func:`load_forensic_record`
    receive leakage validation; the official release boundary separately validates the
    canonical object before calling this function. This verifies the STRUCTURED artifact /
    pre-render client representation only — it does NOT parse or verify any rendered PDF/HTML. A PASS means
    the artifact satisfies the implemented Phase-7B QA contract; it does NOT certify
    scientific truth, source quality, literature exhaustiveness, or causal validity.
    """
    checks_run, findings = _run_mandatory_checks(record)
    severity_counts, releasable, blocking_codes, decision_status, decision_reason = (
        _decision_from_evidence(checks_run, findings)
    )

    fingerprint = record_fingerprint(record)
    report = ReleaseReport(
        release_report_id=f"RR-{record.record_id}-{fingerprint[:12]}",
        forensic_record_id=record.record_id,
        record_fingerprint=fingerprint,
        mandatory_gate_set_fingerprint=mandatory_gate_set_fingerprint(),
        checks_run=checks_run,
        findings=findings,
        severity_counts=severity_counts,
        releasable=releasable,
        decision_status=decision_status,
        blocking_codes=blocking_codes,
        decision_reason=decision_reason,
    )
    report.release_report_fingerprint = release_report_fingerprint(report)
    return report


def validate_release_report(
    report: ReleaseReport, record: ForensicRecord
) -> tuple[bool, list[str]]:
    """Re-execute the current tracked gate contract and compare the complete report."""
    expected = evaluate_artifact_release(record)
    errors = validate_release_report_contract(report)
    if report.model_dump(mode="json") != expected.model_dump(mode="json"):
        errors.append("release report differs from fresh mandatory-gate execution")
    return not errors, errors


def final_binding_check(record: ForensicRecord) -> BindingResult:
    """Backward-compatible binding-gate view over the consolidated mandatory check set.

    Retained for existing callers. Delegates to the SAME single execution path as
    :func:`evaluate_artifact_release` (:data:`MANDATORY_PHASE7B_CHECKS`) so the two can
    never diverge, and returns the legacy :class:`BindingResult`. Prefer
    :func:`evaluate_artifact_release` for the machine-readable release report.
    """
    _checks_run, findings = _run_mandatory_checks(record)
    if not record.findings or not record.client_findings or not record.provenance:
        findings.append(
            _binding_drift(
                "coverage",
                "Required claim/finding/client population is empty; no binding proof ran.",
            )
        )
    counts, releasable, _blocking = _severity_rollup(findings)
    releasable = releasable and all(check.status == "ran" for check in _checks_run)
    return BindingResult(
        record_id=record.record_id,
        findings=findings,
        releasable=releasable,
        blocker_count=counts[FailureSeverity.CRITICAL.value],
        major_count=counts[FailureSeverity.MAJOR.value],
    )
