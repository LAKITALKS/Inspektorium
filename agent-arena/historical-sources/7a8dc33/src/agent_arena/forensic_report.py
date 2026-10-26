"""Deterministic claim-forensics report prototype (Phase 6.3).

Turns ONE Agent Arena claim-forensics analysis into a versioned, machine-readable
report object and a human-readable Markdown rendering. Pure and deterministic: **no
model calls, no network, no wall-clock timestamps** (``generated_at`` is a passthrough
from the input). A single validated report object produces both the full JSON report and
the Markdown (full + executive) renderings — there is never a second source of truth.

Frozen vocabularies are **reused** from the existing engine, not redefined:

- labels — ``solid``, ``overclaim``, ``correlation_vs_causation``, ``mechanism_vs_evidence``
  (`study_forensics_checker`); ``mechanism_vs_evidence`` keeps its biological scope:
  biological mechanism / preclinical evidence used to imply **human clinical benefit**;
- evidence tiers — ``cell · animal · biomarker · limited_human · clinical_human``
  (from the `runner` analysis contract);
- confidence VALID / MISSING / INVALID — via ``confidence_validity.classify_confidence``
  (Phase 6.1); a missing/invalid confidence is **never coerced to 0.0**;
- evidence roles — ``schemas.EvidenceRole``.

Safety properties: evidence is never invented; a recommended rewrite is guarded against
introducing unsupported new facts (numeric-token containment) and drops to "no safe
rewrite available" if it would; a parser failure yields a failure report that cannot
masquerade as a successful verdict; a classification is explicitly **not** presented as
proof of factual falsity; reader-impact risk is a qualitative category, never a computed
harm probability. No threshold optimization or model-selection logic lives here.

All example material produced with this module is SYNTHETIC and must never be presented
as real Agent Arena performance.
"""

from __future__ import annotations

import hashlib
import json
import re

from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence

# ---------------------------------------------------------------------------
# Frozen constants (reused vocabularies + prototype additions)
# ---------------------------------------------------------------------------

REPORT_SCHEMA_VERSION = "6.3.0"

FORENSIC_LABELS = ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence")

# Plain-language verdict titles (refined from reporting.CATEGORY_LABELS; underlying
# label meaning unchanged). mechanism_vs_evidence stays biologically scoped.
VERDICT_TITLES = {
    "solid": "Supported within the available evidence",
    "overclaim": "Claim goes beyond the available evidence",
    "correlation_vs_causation": "Association is presented as causation",
    "mechanism_vs_evidence":
        "Biological or preclinical evidence is presented as human clinical benefit",
}

# Neutral, evidence-relationship summaries (never assert factual falsity).
VERDICT_DEFAULT_SUMMARY = {
    "solid": "The claim stays within what the cited evidence can support.",
    "overclaim": "The claim asserts more than the cited evidence establishes.",
    "correlation_vs_causation":
        "A causal conclusion is drawn from evidence that shows association, not causation.",
    "mechanism_vs_evidence":
        "Preclinical or mechanistic evidence is used to imply a human clinical benefit "
        "the evidence tier does not reach.",
}

# Evidence tiers (weakest → strongest), from the runner analysis contract.
EVIDENCE_TIERS = ("cell", "animal", "biomarker", "limited_human", "clinical_human")
EVIDENCE_TIER_VALUES = (*EVIDENCE_TIERS, "unknown", "not_applicable")

# Evidence roles (schemas.EvidenceRole).
EVIDENCE_ROLES = ("supporting", "weakening", "contradictory", "missing_expected")

# Frozen failure-mode vocabulary (maps the existing checker findings + the Phase 6.3
# brief). A failure mode may appear in a report only if the input analysis supplies it
# WITH a rationale — the builder never infers one.
FAILURE_MODES = (
    "correlation_vs_causation_conflation",
    "inappropriate_generalization",
    "evidence_tier_mismatch",
    "unsupported_superiority_claim",
    "benchmark_exaggeration",
    "decorative_or_weak_hedging",
    "mechanism_to_human_benefit_leap",
    "conclusion_exceeds_results",
    "missing_comparison_group",
    "missing_causal_chain",
    "missing_human_evidence",
)

# Reader-impact risk: qualitative only. "unknown" is an explicit insufficient state.
RISK_LEVELS = ("low", "moderate", "high", "critical")
RISK_UNKNOWN = "unknown"
RISK_VALUES = (*RISK_LEVELS, RISK_UNKNOWN)

EVIDENCE_SUFFICIENCY = ("sufficient", "insufficient", "unknown")
ANALYSIS_STATUS = ("complete", "parser_failure", "insufficient_input")
DEV_OR_PROD = ("development", "production")
CONFIDENCE_STATUSES = (VALID, MISSING, INVALID)

CONFIDENCE_INTERPRETATION = {
    VALID: ("Model's self-assessed probability that its own primary classification is "
            "correct (Phase 6.1 semantics). Not a calibrated probability."),
    MISSING: ("No confidence value was provided. Recorded as MISSING and NOT treated as "
              "0.0; excluded from any confidence-dependent reading."),
    INVALID: ("The provided confidence was non-numeric, boolean, or outside [0.0, 1.0]. "
              "Recorded as INVALID and NOT coerced; excluded from any confidence reading."),
}

NOT_FALSITY_NOTE = (
    "A forensic classification describes the relationship between the claim and the "
    "cited evidence. It is not, by itself, proof that the claim is factually false."
)
NOT_HARM_PROBABILITY_NOTE = (
    "Reader-impact risk is a qualitative category describing how a non-specialist might "
    "misread the claim. It is NOT a computed medical, legal, or financial harm probability."
)
DEVELOPMENT_CAVEAT = (
    "Development prototype output on synthetic input — small-sample characterization, "
    "not a validated production judgement."
)
REWRITE_VERIFICATION_NOTE = (
    "This rewrite is an UNVERIFIED proposal copied from the analysis input. The "
    "numeric-containment guard only checks that it introduces no unsupported number; it "
    "does NOT verify factual or semantic accuracy. Its factual support still requires "
    "human review."
)
# recommended_revision.rewrite_verification vocabulary
REWRITE_VERIFICATIONS = ("unverified_proposal", "blocked_unsupported_new_facts", "no_rewrite_supplied")

# Allowed keys (schema additionalProperties:false mirror).
_INPUT_TOP_KEYS = {
    "meta", "parser", "claim", "verdict", "evidence", "failure_modes",
    "reader_impact", "uncertainty", "recommended_revision", "provenance",
}
_META_KEYS = {"report_id", "generated_at", "synthetic_fixture",
              "development_or_production_status", "analysis_status"}
_PARSER_KEYS = {"parse_ok", "strategy", "error", "finish_reason", "truncation_suspected"}
_CLAIM_KEYS = {"claim_text", "claim_context", "claim_source_reference",
               "claim_scope", "intended_reader_or_audience"}
_VERDICT_KEYS = {"predicted_label", "verdict_summary", "confidence"}
_EVIDENCE_KEYS = {"evidence_items", "supporting", "contradicting_or_limiting",
                  "missing_comparison_group", "missing_causal_chain",
                  "missing_human_evidence", "evidence_sufficiency",
                  "evidence_sufficiency_rationale"}
_EVIDENCE_ITEM_KEYS = {"text", "source_reference", "tier", "role", "why_it_matters"}
_FAILURE_KEYS = {"detected"}
_FAILURE_ITEM_KEYS = {"mode", "rationale", "evidence_refs"}
_READER_KEYS = {"risk_level", "risk_rationale", "likely_reader_misunderstanding",
                "affected_decision_type", "risk_uncertainty"}
_UNCERTAINTY_KEYS = {"unresolved_questions", "missing_evidence", "ambiguity",
                     "alternative_plausible_label", "alternative_label_rationale",
                     "scope_limitations"}
_REVISION_KEYS = {"defensible_rewrite", "rewrite_rationale", "claims_to_remove_or_narrow",
                  "evidence_qualifiers_to_add", "claims_that_remain_supportable"}
_PROVENANCE_KEYS = {"model", "provider", "prompt_contract_version",
                    "repository_commit", "analysis_source"}

# Leakage patterns — private identities / paths that must never appear in a report input.
_LEAK_PATTERNS = (
    (re.compile(r"study-forensics-[0-9]+", re.I), "canonical study-forensics id"),
    (re.compile(r"\bBIAA-[0-9]+", re.I), "BIAA id"),
    (re.compile(r"\bHLD-[0-9]+", re.I), "HLD id"),
    (re.compile(r"\bDEV-[0-9]{3,}\b"), "private DEV pool id"),
    (re.compile(r"AgentArena_IAA_Private"), "private path"),
    (re.compile(r"/Users/"), "absolute private path"),
    (re.compile(r"internal_only"), "internal_only path"),
    (re.compile(r"\bsalt_hex\b|\bprivate_manifest\b"), "private manifest/salt token"),
)

_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


class ForensicReportError(ValueError):
    """Raised when report input violates the frozen schema (not for missing-data states)."""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _iter_strings(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k)
            yield from _iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _iter_strings(v)
    elif isinstance(obj, str):
        yield obj


def leakage_findings(obj) -> list[str]:
    """Return distinct private-identity / private-path findings in a value tree."""
    found: list[str] = []
    for s in _iter_strings(obj):
        for pat, label in _LEAK_PATTERNS:
            if pat.search(s) and label not in found:
                found.append(label)
    return found


def _str_or_none(v):
    if v is None:
        return None
    if isinstance(v, str):
        return v if v.strip() else None
    return str(v)


def _list_of_str(v) -> list[str]:
    if not isinstance(v, list):
        return []
    return [x for x in v if isinstance(x, str)]


def _bool_or_none(v):
    return v if isinstance(v, bool) else None


def _numbers(text: str) -> set[str]:
    return set(_NUMBER_RE.findall(text or ""))


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def _check_keys(obj, allowed, path, errors):
    if not isinstance(obj, dict):
        errors.append(f"{path} must be an object")
        return False
    extra = sorted(set(obj) - allowed)
    if extra:
        errors.append(f"{path} has unexpected field(s): {extra}")
    return True


def _resolve_status(raw: dict) -> str:
    meta = raw.get("meta") or {}
    parser = raw.get("parser") or {}
    if parser.get("parse_ok") is False:
        return "parser_failure"          # safety: a parser failure always wins
    explicit = meta.get("analysis_status")
    if explicit in ANALYSIS_STATUS:
        return explicit
    verdict = raw.get("verdict") or {}
    if not verdict.get("predicted_label"):
        return "insufficient_input"
    return "complete"


def validate_forensic_report_input(raw: dict) -> tuple[bool, list[str]]:
    """Structurally validate a report input against the frozen schema.

    Returns ``(ok, errors)``. Missing-data *states* (absent confidence, empty evidence,
    parser failure, insufficient input) are **valid** and are not errors here; only
    schema/vocabulary violations and identity leakage are.
    """
    errors: list[str] = []
    if not isinstance(raw, dict):
        return False, ["input must be an object"]

    _check_keys(raw, _INPUT_TOP_KEYS, "input", errors)

    # leakage
    for label in leakage_findings(raw):
        errors.append(f"private identity/path in input: {label}")

    status = _resolve_status(raw)

    meta = raw.get("meta") or {}
    _check_keys(meta, _META_KEYS, "meta", errors)
    if "synthetic_fixture" in meta and not isinstance(meta["synthetic_fixture"], bool):
        errors.append("meta.synthetic_fixture must be a boolean")
    if meta.get("development_or_production_status") not in (None, *DEV_OR_PROD):
        errors.append(f"meta.development_or_production_status must be one of {DEV_OR_PROD}")
    if meta.get("analysis_status") not in (None, *ANALYSIS_STATUS):
        errors.append(f"meta.analysis_status must be one of {ANALYSIS_STATUS}")

    if "parser" in raw:
        parser = raw.get("parser") or {}
        _check_keys(parser, _PARSER_KEYS, "parser", errors)
        if "parse_ok" in parser and not isinstance(parser["parse_ok"], bool):
            errors.append("parser.parse_ok must be a boolean")

    claim = raw.get("claim")
    if not isinstance(claim, dict):
        errors.append("claim is required and must be an object")
    else:
        _check_keys(claim, _CLAIM_KEYS, "claim", errors)
        if not _str_or_none(claim.get("claim_text")):
            errors.append("claim.claim_text is required and must be a non-empty string")

    verdict = raw.get("verdict") or {}
    if verdict:
        _check_keys(verdict, _VERDICT_KEYS, "verdict", errors)
        label = verdict.get("predicted_label")
        if label is not None and label not in FORENSIC_LABELS:
            errors.append(f"verdict.predicted_label {label!r} is not a frozen label")
        if isinstance(verdict.get("confidence"), bool):
            # boolean confidence is INVALID per Phase 6.1 — never a numeric value
            pass  # not a hard error; represented as INVALID in the report
    if status == "complete" and not verdict.get("predicted_label"):
        errors.append("verdict.predicted_label is required for a complete analysis")

    ev = raw.get("evidence") or {}
    if ev:
        _check_keys(ev, _EVIDENCE_KEYS, "evidence", errors)
        items = ev.get("evidence_items", [])
        if not isinstance(items, list):
            errors.append("evidence.evidence_items must be a list")
        else:
            for i, it in enumerate(items):
                if not _check_keys(it, _EVIDENCE_ITEM_KEYS, f"evidence.evidence_items[{i}]", errors):
                    continue
                if not _str_or_none(it.get("text")):
                    errors.append(f"evidence.evidence_items[{i}].text is required")
                if it.get("tier") not in (None, *EVIDENCE_TIER_VALUES):
                    errors.append(f"evidence.evidence_items[{i}].tier is not a valid tier")
                if it.get("role") not in (None, *EVIDENCE_ROLES):
                    errors.append(f"evidence.evidence_items[{i}].role is not a valid role")
        if ev.get("evidence_sufficiency") not in (None, *EVIDENCE_SUFFICIENCY):
            errors.append(f"evidence.evidence_sufficiency must be one of {EVIDENCE_SUFFICIENCY}")
        for k in ("missing_comparison_group", "missing_causal_chain", "missing_human_evidence"):
            if k in ev and not isinstance(ev[k], bool) and ev[k] is not None:
                errors.append(f"evidence.{k} must be a boolean or null")

    fm = raw.get("failure_modes") or {}
    if fm:
        _check_keys(fm, _FAILURE_KEYS, "failure_modes", errors)
        detected = fm.get("detected", [])
        if not isinstance(detected, list):
            errors.append("failure_modes.detected must be a list")
        else:
            for i, d in enumerate(detected):
                if not _check_keys(d, _FAILURE_ITEM_KEYS, f"failure_modes.detected[{i}]", errors):
                    continue
                if d.get("mode") not in FAILURE_MODES:
                    errors.append(f"failure_modes.detected[{i}].mode {d.get('mode')!r} "
                                  "is not a frozen failure mode")
                if not _str_or_none(d.get("rationale")):
                    errors.append(f"failure_modes.detected[{i}] must carry a non-empty "
                                  "rationale (a failure mode is never asserted unsupported)")

    ri = raw.get("reader_impact") or {}
    if ri:
        _check_keys(ri, _READER_KEYS, "reader_impact", errors)
        if ri.get("risk_level") not in (None, *RISK_VALUES):
            errors.append(f"reader_impact.risk_level must be one of {RISK_VALUES}")

    unc = raw.get("uncertainty") or {}
    if unc:
        _check_keys(unc, _UNCERTAINTY_KEYS, "uncertainty", errors)
        alt = unc.get("alternative_plausible_label")
        if alt is not None and alt not in FORENSIC_LABELS:
            errors.append("uncertainty.alternative_plausible_label must be a frozen label or null")

    rev = raw.get("recommended_revision") or {}
    if rev:
        _check_keys(rev, _REVISION_KEYS, "recommended_revision", errors)

    prov = raw.get("provenance") or {}
    if prov:
        _check_keys(prov, _PROVENANCE_KEYS, "provenance", errors)

    return (not errors), errors


# ---------------------------------------------------------------------------
# Canonical serialization + digests
# ---------------------------------------------------------------------------

def _canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"


def canonical_input_bytes(raw: dict) -> bytes:
    """Deterministic canonical bytes for a report input (used for the input digest)."""
    return _canonical_bytes(raw)


def canonical_report_bytes(report: dict) -> bytes:
    """Deterministic canonical JSON bytes for a report (sorted keys, fixed serialization)."""
    return _canonical_bytes(report)


def report_digest(report: dict) -> str:
    """SHA-256 over the report with its own generation-digest field blanked.

    Recomputable by any consumer: blank ``provenance.report_generation_digest_sha256``
    then hash the canonical bytes.
    """
    clone = json.loads(json.dumps(report))
    clone.get("provenance", {})["report_generation_digest_sha256"] = ""
    return hashlib.sha256(canonical_report_bytes(clone)).hexdigest()


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _rewrite_guard(rewrite: str | None, corpus: str) -> tuple[str | None, bool, list[str]]:
    """Guard a proposed rewrite against introducing unsupported new numeric facts.

    Returns ``(accepted_rewrite_or_None, available, unsupported_new_facts)``. Every
    number in the rewrite must already appear in the input corpus; otherwise the rewrite
    is blocked (dropped to None) rather than shipped with a fabricated fact.
    """
    if not _str_or_none(rewrite):
        return None, False, []
    corpus_numbers = _numbers(corpus)
    unsupported = sorted(n for n in _numbers(rewrite) if n not in corpus_numbers)
    if unsupported:
        return None, False, unsupported
    return rewrite, True, []


def build_forensic_report(raw: dict) -> dict:
    """Build the validated, deterministic claim-forensics report object.

    Raises :class:`ForensicReportError` on schema/vocabulary violations or identity
    leakage. Missing-data states (absent confidence, empty evidence, parser failure,
    insufficient input) are represented explicitly, never fabricated.
    """
    ok, errors = validate_forensic_report_input(raw)
    if not ok:
        raise ForensicReportError("; ".join(errors))

    warnings: list[str] = []
    audit: list[str] = [f"input validated against forensic_report schema {REPORT_SCHEMA_VERSION}"]
    status = _resolve_status(raw)
    audit.append(f"analysis_status={status}")

    meta = raw.get("meta") or {}
    parser = raw.get("parser") or {}
    claim = raw.get("claim") or {}
    verdict_in = raw.get("verdict") or {}
    ev_in = raw.get("evidence") or {}
    fm_in = raw.get("failure_modes") or {}
    ri_in = raw.get("reader_impact") or {}
    unc_in = raw.get("uncertainty") or {}
    rev_in = raw.get("recommended_revision") or {}
    prov_in = raw.get("provenance") or {}

    input_digest = hashlib.sha256(canonical_input_bytes(raw)).hexdigest()

    if "synthetic_fixture" in meta:
        synthetic = bool(meta["synthetic_fixture"])
    else:
        synthetic = True
        warnings.append("synthetic_fixture not supplied; defaulted to true (prototype-safe)")
    dev_or_prod = meta.get("development_or_production_status") or "development"

    report_id = _str_or_none(meta.get("report_id")) or f"FR-{input_digest[:12]}"
    generated_at = _str_or_none(meta.get("generated_at"))
    if generated_at is None:
        warnings.append("generated_at not supplied; recorded as null (no wall-clock injected)")

    # --- confidence (raw → VALID/MISSING/INVALID; never coerced to 0.0) -------------
    has_conf_key = "confidence" in verdict_in
    raw_conf = verdict_in.get("confidence") if has_conf_key else None
    conf_status = classify_confidence(raw_conf) if has_conf_key else MISSING
    conf_value = float(raw_conf) if conf_status == VALID else None
    audit.append(f"confidence classified as {conf_status} (no coercion to 0.0)")
    if conf_status != VALID:
        warnings.append(f"confidence {conf_status}: excluded from any confidence-dependent reading")

    # --- verdict --------------------------------------------------------------------
    label = verdict_in.get("predicted_label")
    if status == "parser_failure":
        verdict = {
            "predicted_label": None,
            "verdict_title": "Analysis could not be completed (parser failure)",
            "verdict_summary": _str_or_none(parser.get("error"))
            or "The analysis output could not be parsed into a structured verdict.",
            "confidence_status": conf_status,
            "confidence_value": conf_value,
            "confidence_interpretation": CONFIDENCE_INTERPRETATION[conf_status],
            "classification_note": NOT_FALSITY_NOTE,
        }
        warnings.append("parser failure: no verdict was produced; this is a failure report")
    elif status == "insufficient_input":
        verdict = {
            "predicted_label": None,
            "verdict_title": "Insufficient input for a verdict",
            "verdict_summary": "No forensic classification was supplied; the analysis is "
                               "incomplete and no verdict is asserted.",
            "confidence_status": conf_status,
            "confidence_value": conf_value,
            "confidence_interpretation": CONFIDENCE_INTERPRETATION[conf_status],
            "classification_note": NOT_FALSITY_NOTE,
        }
        warnings.append("insufficient input: no predicted_label supplied; no verdict asserted")
    else:
        verdict = {
            "predicted_label": label,
            "verdict_title": VERDICT_TITLES[label],
            "verdict_summary": _str_or_none(verdict_in.get("verdict_summary"))
            or VERDICT_DEFAULT_SUMMARY[label],
            "confidence_status": conf_status,
            "confidence_value": conf_value,
            "confidence_interpretation": CONFIDENCE_INTERPRETATION[conf_status],
            "classification_note": NOT_FALSITY_NOTE,
        }

    # --- evidence -------------------------------------------------------------------
    evidence_items = []
    for it in ev_in.get("evidence_items", []) or []:
        evidence_items.append({
            "text": it.get("text", ""),
            "source_reference": _str_or_none(it.get("source_reference")),
            "tier": it.get("tier") or "unknown",
            "role": it.get("role") or "supporting",
            "why_it_matters": _str_or_none(it.get("why_it_matters")),
        })
    evidence = {
        "evidence_items": evidence_items,
        "supporting": _list_of_str(ev_in.get("supporting")),
        "contradicting_or_limiting": _list_of_str(ev_in.get("contradicting_or_limiting")),
        "missing_comparison_group": _bool_or_none(ev_in.get("missing_comparison_group")),
        "missing_causal_chain": _bool_or_none(ev_in.get("missing_causal_chain")),
        "missing_human_evidence": _bool_or_none(ev_in.get("missing_human_evidence")),
        "evidence_sufficiency": ev_in.get("evidence_sufficiency") or "unknown",
        "evidence_sufficiency_rationale": _str_or_none(ev_in.get("evidence_sufficiency_rationale")),
    }
    if not evidence_items:
        warnings.append("no evidence items supplied; evidence list is empty (shown, not hidden)")

    # --- failure modes (echoed from analysis, never inferred) -----------------------
    detected = []
    for d in fm_in.get("detected", []) or []:
        detected.append({
            "mode": d.get("mode"),
            "rationale": d.get("rationale", ""),
            "evidence_refs": _list_of_str(d.get("evidence_refs")),
        })
    failure_modes = {"detected": detected, "none_detected": len(detected) == 0}
    audit.append(f"{len(detected)} failure mode(s) echoed from analysis (not inferred)")

    # --- reader-impact risk (qualitative; unknown when absent) ----------------------
    risk_level = ri_in.get("risk_level") or RISK_UNKNOWN
    if risk_level == RISK_UNKNOWN and "risk_level" not in ri_in:
        warnings.append("reader-impact risk not supplied; recorded as 'unknown' (insufficient)")
    reader_impact = {
        "risk_level": risk_level,
        "risk_rationale": _str_or_none(ri_in.get("risk_rationale")),
        "likely_reader_misunderstanding": _str_or_none(ri_in.get("likely_reader_misunderstanding")),
        "affected_decision_type": _str_or_none(ri_in.get("affected_decision_type")),
        "risk_uncertainty": _str_or_none(ri_in.get("risk_uncertainty")),
        "not_a_harm_probability_note": NOT_HARM_PROBABILITY_NOTE,
    }

    # --- uncertainty ----------------------------------------------------------------
    uncertainty = {
        "unresolved_questions": _list_of_str(unc_in.get("unresolved_questions")),
        "missing_evidence": _list_of_str(unc_in.get("missing_evidence")),
        "ambiguity": _str_or_none(unc_in.get("ambiguity")),
        "alternative_plausible_label": unc_in.get("alternative_plausible_label"),
        "alternative_label_rationale": _str_or_none(unc_in.get("alternative_label_rationale")),
        "scope_limitations": _list_of_str(unc_in.get("scope_limitations")),
        "confidence_caveat": CONFIDENCE_INTERPRETATION[conf_status],
        "development_caveat": DEVELOPMENT_CAVEAT if dev_or_prod == "development" else None,
    }

    # --- recommended revision (guarded against unsupported new facts) ---------------
    corpus = " ".join([
        _str_or_none(claim.get("claim_text")) or "",
        _str_or_none(claim.get("claim_context")) or "",
        *[it["text"] for it in evidence_items],
        *[s for s in evidence["supporting"]],
        *[s for s in evidence["contradicting_or_limiting"]],
    ])
    rewrite_in = _str_or_none(rev_in.get("defensible_rewrite"))
    accepted_rewrite, rewrite_available, unsupported_facts = _rewrite_guard(rewrite_in, corpus)
    if unsupported_facts:
        verification = "blocked_unsupported_new_facts"
        warnings.append("recommended rewrite blocked: introduces unsupported new fact(s) "
                        f"{unsupported_facts}; dropped to 'no safe rewrite available'")
        audit.append("rewrite guard: blocked (unsupported new facts)")
    elif accepted_rewrite:
        verification = "unverified_proposal"
        warnings.append("recommended rewrite is an UNVERIFIED proposal; numeric guard passed "
                        "but factual/semantic support still requires human review")
        audit.append("rewrite guard: clean (numeric-only); rewrite marked unverified_proposal")
    else:
        verification = "no_rewrite_supplied"
        audit.append("rewrite guard: no rewrite supplied")
    recommended_revision = {
        "defensible_rewrite": accepted_rewrite,
        "rewrite_available": rewrite_available,
        "rewrite_verification": verification,
        "rewrite_verification_note": REWRITE_VERIFICATION_NOTE,
        "rewrite_rationale": _str_or_none(rev_in.get("rewrite_rationale")),
        "claims_to_remove_or_narrow": _list_of_str(rev_in.get("claims_to_remove_or_narrow")),
        "evidence_qualifiers_to_add": _list_of_str(rev_in.get("evidence_qualifiers_to_add")),
        "claims_that_remain_supportable": _list_of_str(rev_in.get("claims_that_remain_supportable")),
        "rewrite_guard": {
            "checked": True,
            "unsupported_new_facts": unsupported_facts,
            "status": "blocked" if unsupported_facts else ("clean" if accepted_rewrite else "no_rewrite"),
        },
    }

    # --- provenance -----------------------------------------------------------------
    parser_status = "failed" if status == "parser_failure" else (
        "ok" if parser.get("parse_ok") in (True, None) else "unknown")
    provenance = {
        "model": _str_or_none(prov_in.get("model")),
        "provider": _str_or_none(prov_in.get("provider")),
        "prompt_contract_version": _str_or_none(prov_in.get("prompt_contract_version")),
        "repository_commit": _str_or_none(prov_in.get("repository_commit")),
        "analysis_source": _str_or_none(prov_in.get("analysis_source")),
        "input_digest_sha256": input_digest,
        "report_generation_digest_sha256": "",   # filled after the report is assembled
        "parser_status": parser_status,
        "warnings": warnings,
        "audit_trail": audit,
    }

    banner = ["DEVELOPMENT PROTOTYPE — claim-forensics report (Phase 6.3)"]
    if synthetic:
        banner.append("SYNTHETIC EXAMPLE — not real Agent Arena performance")

    report = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "report_id": report_id,
        "generated_at": generated_at,
        "analysis_status": status,
        "synthetic_fixture": synthetic,
        "development_or_production_status": dev_or_prod,
        "status_banner": banner,
        "claim": {
            "claim_text": _str_or_none(claim.get("claim_text")),
            "claim_context": _str_or_none(claim.get("claim_context")),
            "claim_source_reference": _str_or_none(claim.get("claim_source_reference")),
            "claim_scope": _str_or_none(claim.get("claim_scope")),
            "intended_reader_or_audience": _str_or_none(claim.get("intended_reader_or_audience")),
        },
        "verdict": verdict,
        "evidence": evidence,
        "failure_modes": failure_modes,
        "reader_impact": reader_impact,
        "uncertainty": uncertainty,
        "recommended_revision": recommended_revision,
        "provenance": provenance,
    }
    report["provenance"]["report_generation_digest_sha256"] = report_digest(report)
    return report


# ---------------------------------------------------------------------------
# Report re-validation (structural, mirrors the JSON schema)
# ---------------------------------------------------------------------------

def validate_forensic_report(report: dict) -> tuple[bool, list[str]]:
    """Re-validate a *built* report against the frozen output contract."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return False, ["report must be an object"]
    if report.get("report_schema_version") != REPORT_SCHEMA_VERSION:
        errors.append(f"report_schema_version must be {REPORT_SCHEMA_VERSION!r}")
    if report.get("analysis_status") not in ANALYSIS_STATUS:
        errors.append("analysis_status invalid")
    if not isinstance(report.get("synthetic_fixture"), bool):
        errors.append("synthetic_fixture must be a boolean")

    v = report.get("verdict") or {}
    label = v.get("predicted_label")
    if label is not None and label not in FORENSIC_LABELS:
        errors.append("verdict.predicted_label invalid")
    if label is not None and v.get("verdict_title") != VERDICT_TITLES.get(label):
        errors.append("verdict_title inconsistent with predicted_label")
    if v.get("confidence_status") not in CONFIDENCE_STATUSES:
        errors.append("confidence_status invalid")
    cval = v.get("confidence_value")
    if isinstance(cval, bool):
        errors.append("confidence_value must never be a boolean")
    elif cval is not None and not (isinstance(cval, (int, float)) and 0.0 <= float(cval) <= 1.0):
        errors.append("confidence_value must be null or a number in [0,1]")
    if v.get("confidence_status") != VALID and cval is not None:
        errors.append("confidence_value must be null unless confidence_status is VALID")

    ri = report.get("reader_impact") or {}
    if ri.get("risk_level") not in RISK_VALUES:
        errors.append("reader_impact.risk_level invalid")

    for d in (report.get("failure_modes") or {}).get("detected", []):
        if d.get("mode") not in FAILURE_MODES:
            errors.append(f"failure mode {d.get('mode')!r} invalid")

    rev = report.get("recommended_revision") or {}
    if rev.get("rewrite_verification") not in REWRITE_VERIFICATIONS:
        errors.append("recommended_revision.rewrite_verification invalid")
    if rev.get("defensible_rewrite") is not None and rev.get("rewrite_verification") != "unverified_proposal":
        errors.append("a present rewrite must be marked 'unverified_proposal'")
    if rev.get("defensible_rewrite") is None and rev.get("rewrite_available"):
        errors.append("rewrite_available must be false when no rewrite is present")

    for label_str in leakage_findings(report):
        errors.append(f"private identity/path in report: {label_str}")

    return (not errors), errors


# ---------------------------------------------------------------------------
# Markdown rendering (full + executive) — one report object, two views
# ---------------------------------------------------------------------------

def _fmt_conf(v: dict) -> str:
    status = v.get("confidence_status")
    if status == VALID:
        return f"{status} ({v.get('confidence_value'):.2f})"
    return f"{status} (no numeric value; not treated as 0.0)"


def _bullets(items: list[str], empty: str) -> list[str]:
    if not items:
        return [f"- _{empty}_"]
    return [f"- {x}" for x in items]


def render_forensic_report_markdown(report: dict) -> str:
    """Full diagnostic rendering; this lower-level view is never an official release."""
    L: list[str] = [
        "> **DIAGNOSTIC / NON-RELEASE ARTIFACT — NOT OFFICIALLY RELEASE-AUTHORIZED**",
        "",
        "`artifact_role=diagnostic_non_release` · `official_release_authorized=false`",
        "",
    ]
    for b in report.get("status_banner", []):
        L.append(f"> **{b}**")
    L.append("")
    L.append(f"# Claim-forensics report — {report['report_id']}")
    L.append(f"schema `{report['report_schema_version']}` · status "
             f"`{report['analysis_status']}` · {report['development_or_production_status']} · "
             f"synthetic={report['synthetic_fixture']} · generated_at={report.get('generated_at')}")
    warnings = report.get("provenance", {}).get("warnings", [])
    if warnings:
        L.append("")
        L.append("**⚠ Warnings**")
        L += _bullets(warnings, "none")

    c = report["claim"]
    L += ["", "## Claim", f"> {c.get('claim_text')}"]
    for lbl, key in (("Context", "claim_context"), ("Source", "claim_source_reference"),
                     ("Scope", "claim_scope"), ("Audience", "intended_reader_or_audience")):
        L.append(f"- {lbl}: {c.get(key) if c.get(key) is not None else '_not supplied_'}")

    v = report["verdict"]
    L += ["", "## Verdict", f"**{v.get('verdict_title')}**"
          + (f"  (`{v.get('predicted_label')}`)" if v.get("predicted_label") else ""),
          "", v.get("verdict_summary", ""),
          "", f"- Confidence: **{_fmt_conf(v)}**",
          f"- _{v.get('confidence_interpretation')}_",
          f"- _{v.get('classification_note')}_"]

    fm = report["failure_modes"]
    L += ["", "## Why this verdict"]
    if fm.get("none_detected"):
        L.append("- _No specific claim-forensics failure mode was reported._")
    else:
        for d in fm["detected"]:
            refs = f"  (evidence: {', '.join(d['evidence_refs'])})" if d.get("evidence_refs") else ""
            L.append(f"- **{d['mode']}** — {d['rationale']}{refs}")

    ev = report["evidence"]
    L += ["", "## Evidence assessment",
          f"- Sufficiency: **{ev.get('evidence_sufficiency')}**"
          + (f" — {ev['evidence_sufficiency_rationale']}" if ev.get("evidence_sufficiency_rationale") else "")]
    if ev["evidence_items"]:
        for it in ev["evidence_items"]:
            src = f" [{it['source_reference']}]" if it.get("source_reference") else ""
            why = f" — {it['why_it_matters']}" if it.get("why_it_matters") else ""
            L.append(f"- ({it['tier']} · {it['role']}){src} {it['text']}{why}")
    else:
        L.append("- _No evidence items supplied._")
    if ev["supporting"]:
        L += ["", "Supporting:"] + _bullets(ev["supporting"], "none")
    if ev["contradicting_or_limiting"]:
        L += ["", "Contradicting / limiting:"] + _bullets(ev["contradicting_or_limiting"], "none")

    L += ["", "## What is missing"]
    for lbl, key in (("Comparison group missing", "missing_comparison_group"),
                     ("Causal chain missing", "missing_causal_chain"),
                     ("Human evidence missing", "missing_human_evidence")):
        val = ev.get(key)
        shown = "unknown / not assessed" if val is None else ("yes" if val else "no")
        L.append(f"- {lbl}: {shown}")
    L += _bullets(report["uncertainty"]["missing_evidence"], "no further missing evidence noted")

    ri = report["reader_impact"]
    L += ["", "## Reader-impact risk", f"- Risk level: **{ri.get('risk_level')}**"]
    for lbl, key in (("Rationale", "risk_rationale"),
                     ("Likely misunderstanding", "likely_reader_misunderstanding"),
                     ("Affected decision", "affected_decision_type"),
                     ("Risk uncertainty", "risk_uncertainty")):
        L.append(f"- {lbl}: {ri.get(key) if ri.get(key) is not None else '_not supplied_'}")
    L.append(f"- _{ri.get('not_a_harm_probability_note')}_")

    u = report["uncertainty"]
    L += ["", "## Uncertainty"]
    L += _bullets(u["unresolved_questions"], "no unresolved questions recorded")
    if u.get("ambiguity"):
        L.append(f"- Ambiguity: {u['ambiguity']}")
    if u.get("alternative_plausible_label"):
        L.append(f"- Alternative plausible label: `{u['alternative_plausible_label']}`"
                 + (f" — {u['alternative_label_rationale']}" if u.get("alternative_label_rationale") else ""))
    if u["scope_limitations"]:
        L += ["", "Scope limitations:"] + _bullets(u["scope_limitations"], "none")
    L.append(f"- _Confidence caveat: {u.get('confidence_caveat')}_")
    if u.get("development_caveat"):
        L.append(f"- _{u['development_caveat']}_")

    rev = report["recommended_revision"]
    L += ["", "## Safer rewrite"]
    if rev.get("rewrite_available") and rev.get("defensible_rewrite"):
        L.append("_Unverified proposal — needs review._")
        L.append(f"> {rev['defensible_rewrite']}")
        L.append(f"- _{rev.get('rewrite_verification_note')}_")
    else:
        reason = ("blocked: would introduce unsupported new facts "
                  f"{rev['rewrite_guard']['unsupported_new_facts']}"
                  if rev["rewrite_guard"]["status"] == "blocked" else "none provided")
        L.append(f"- _No safe rewrite available ({reason})._")
    if rev.get("rewrite_rationale"):
        L.append(f"- Rationale: {rev['rewrite_rationale']}")
    if rev["claims_to_remove_or_narrow"]:
        L += ["", "Remove / narrow:"] + _bullets(rev["claims_to_remove_or_narrow"], "none")
    if rev["evidence_qualifiers_to_add"]:
        L += ["", "Qualifiers to add:"] + _bullets(rev["evidence_qualifiers_to_add"], "none")
    if rev["claims_that_remain_supportable"]:
        L += ["", "Remains supportable:"] + _bullets(rev["claims_that_remain_supportable"], "none")

    p = report["provenance"]
    L += ["", "## Provenance & audit",
          f"- model / provider: {p.get('model') or '—'} / {p.get('provider') or '—'}",
          f"- prompt contract: {p.get('prompt_contract_version') or '—'}",
          f"- repository commit: {p.get('repository_commit') or '—'}",
          f"- analysis source: {p.get('analysis_source') or '—'}",
          f"- parser status: {p.get('parser_status')}",
          f"- input digest: `{p.get('input_digest_sha256')}`",
          f"- report digest: `{p.get('report_generation_digest_sha256')}`"]
    L += ["", "Audit trail:"] + _bullets(p.get("audit_trail", []), "none")
    if warnings:
        L += ["", "Warnings:"] + _bullets(warnings, "none")
    return "\n".join(L) + "\n"


def render_executive_summary(report: dict) -> str:
    """Short diagnostic view — same verdict/confidence/limitations, no omitted uncertainty."""
    v = report["verdict"]
    ri = report["reader_impact"]
    fm = report["failure_modes"]
    u = report["uncertainty"]
    rev = report["recommended_revision"]
    warnings = report.get("provenance", {}).get("warnings", [])

    L: list[str] = [
        "> **DIAGNOSTIC / NON-RELEASE ARTIFACT — NOT OFFICIALLY RELEASE-AUTHORIZED**",
        "",
        "`artifact_role=diagnostic_non_release` · `official_release_authorized=false`",
        "",
    ]
    for b in report.get("status_banner", []):
        L.append(f"> **{b}**")
    L += ["", f"# Executive summary — {report['report_id']}",
          f"_schema {report['report_schema_version']} · {report['development_or_production_status']} "
          f"· status {report['analysis_status']}_", ""]
    claim_text = report["claim"].get("claim_text") or ""
    short = claim_text if len(claim_text) <= 240 else claim_text[:237] + "…"
    L += [f"**Claim:** {short}", ""]
    L.append(f"**Verdict:** {v.get('verdict_title')}"
             + (f" (`{v.get('predicted_label')}`)" if v.get("predicted_label") else ""))
    L.append(f"**Confidence:** {_fmt_conf(v)}")
    L.append(f"**Reader-impact risk:** {ri.get('risk_level')}"
             + (f" — {ri['risk_rationale']}" if ri.get("risk_rationale") else ""))
    if not fm.get("none_detected"):
        modes = ", ".join(d["mode"] for d in fm["detected"])
        L.append(f"**Failure mode(s):** {modes}")
    else:
        L.append("**Failure mode(s):** none reported")

    # material uncertainty must NOT be omitted
    L += ["", "**Key uncertainty:**"]
    material = list(u["unresolved_questions"])
    if u.get("alternative_plausible_label"):
        material.append(f"alternative plausible label: {u['alternative_plausible_label']}")
    if v.get("confidence_status") != VALID:
        material.append(f"confidence is {v.get('confidence_status')} (not treated as 0.0)")
    L += _bullets(material, "no material uncertainty recorded")

    if rev.get("rewrite_available") and rev.get("defensible_rewrite"):
        L += ["", f"**Safer rewrite (unverified proposal — needs review):** {rev['defensible_rewrite']}",
              f"_{rev.get('rewrite_verification_note')}_"]
    else:
        L += ["", "**Safer rewrite:** none available (evidence does not support a stronger claim)"]

    L += ["", f"_{v.get('classification_note')}_"]
    if report.get("development_or_production_status") == "development":
        L.append(f"_{DEVELOPMENT_CAVEAT}_")
    if warnings:
        L += ["", "**⚠ Warnings:**"] + _bullets(warnings, "none")
    return "\n".join(L) + "\n"
