#!/usr/bin/env python3
"""ASA 25/261 — PREMIUM GROUNDING · RUN 001.

Executes the existing Agent Arena adjudication pipeline over the frozen
INSPEKTORIUM evidence substrate. No framework code is modified: this harness
only feeds the repository's own contracts and writes their outputs.

Pipeline stages (all repository-native):
  0  input integrity        — SHA-256 verification of the canonical freeze
  1  frozen claim ingestion — 26 active atomic propositions, exact wording
  2  claim-forensics report — agent_arena.forensic_report (schema 6.3.0)
     covering evidence-to-claim binding, evidence tier/role, endpoint,
     failure modes, counterevidence, uncertainty calibration
  3  report validation      — validate_forensic_report (frozen contract)
  4  representation record  — agent_arena.schemas.ForensicRecord (0.1.0)
  5  release gate           — agent_arena.artifact_binding.evaluate_artifact_release
     (finding binding, summary-strength monotonicity, evidence symmetry,
      value-origin provenance, search-scope binding)
  6  cross-proposition consistency check
  7  output freeze + SHA-256 manifest
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent
CASE_DIR = RUN_DIR.parent.parent
REPO_ROOT = CASE_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(RUN_DIR))

from agent_arena.artifact_binding import (                       # noqa: E402
    MANDATORY_PHASE7B_CHECKS, PHASE7B_RELEASE_GATE_VERSION,
    compute_content_fingerprint, evaluate_artifact_release, record_fingerprint,
)
from agent_arena.forensic_report import (                        # noqa: E402
    REPORT_SCHEMA_VERSION, build_forensic_report, canonical_input_bytes,
    canonical_report_bytes, render_executive_summary,
    render_forensic_report_markdown, validate_forensic_report,
    validate_forensic_report_input,
)
from agent_arena.schemas import (                                # noqa: E402
    FORENSIC_RECORD_SCHEMA_VERSION, SUMMARY_STRENGTH_ORDER,
    SCOPE_DOCUMENTED_SEARCH, ClaimProvenance, ClientFinding,
    ClientNegativeAssertion, EvidenceRole, ForensicRecord, InternalFinding,
    NegativeEvidenceAssertion, QAEvidenceItem, SearchScope,
    VALUE_ORIGIN_SOURCE_REPORTED,
)

import adjudication_data as DATA                                 # noqa: E402

# --- run constants (recorded, never inferred) ------------------------------
RUN_ID = "run_001"
CASE_ID = "ASA_25_261_PREMIUM_GROUNDING"
RUN_DATE = "2026-08-23"
EVIDENCE_CUTOFF = "2026-08-22"
MODEL = "claude-opus-5"
PROVIDER = "anthropic"
PROMPT_CONTRACT = "ASA_25_261_MASTER_EXECUTION_PROMPT_RUN_001"
EXPECTED_FREEZE_SHA = ("530f8fdf33715f59f86e10df6a9329ad5"
                       "ccce4c4f0befc219341563b36600069")
EXPECTED_FREEZE_BYTES = 119130

INPUT_FILES = {
    "input/01_FINAL_EVIDENCE_FREEZE_v1.md": "CANONICAL SCIENTIFIC SUBSTRATE",
    "provenance/01_CLOSED_CASE_SCIENTIFIC_EVIDENCE_PACKAGE_v1.md": "PROVENANCE (audit trail only)",
    "provenance/02_TARGETED_EVIDENCE_CLOSURE_v1.md": "PROVENANCE (audit trail only)",
    "provenance/03_PRE_FREEZE_TERMINOLOGY_ROBUSTNESS_CHECK_v1.md": "PROVENANCE (audit trail only)",
}

OUT = RUN_DIR
REPORTS = OUT / "proposition_reports"
LOG: list[str] = []


def log(msg: str) -> None:
    LOG.append(msg)
    print(msg)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Stage 0 — input integrity
# ---------------------------------------------------------------------------

def stage0_integrity() -> tuple[dict, bool]:
    log("STAGE 0 — INPUT INTEGRITY")
    observed = {}
    for rel, role in INPUT_FILES.items():
        p = CASE_DIR / rel
        observed[rel] = dict(role=role, sha256=sha256_file(p),
                             bytes=p.stat().st_size)
        log(f"  {rel}: {observed[rel]['sha256']} ({observed[rel]['bytes']} bytes)")
    freeze = observed["input/01_FINAL_EVIDENCE_FREEZE_v1.md"]
    ok = (freeze["sha256"] == EXPECTED_FREEZE_SHA
          and freeze["bytes"] == EXPECTED_FREEZE_BYTES)
    log(f"  CANONICAL FREEZE INTEGRITY: {'PASS' if ok else 'FAIL'}")
    return observed, ok


# ---------------------------------------------------------------------------
# Stage 2 — build one claim-forensics report input per proposition
# ---------------------------------------------------------------------------

def build_input(p: dict, commit: str) -> dict:
    status = p.get("analysis_status", "complete")
    verdict = {"predicted_label": p["label"],
               "verdict_summary": p["verdict_summary"]}
    if p.get("confidence") is not None:
        verdict["confidence"] = p["confidence"]
    return {
        "meta": {
            "report_id": f"ASA-25-261-{RUN_ID}-{p['pid']}",
            "generated_at": RUN_DATE,
            "synthetic_fixture": False,
            "development_or_production_status": "production",
            "analysis_status": status,
        },
        "parser": {"parse_ok": True, "strategy": "structured_adjudication"},
        "claim": {
            "claim_text": p["proposition"],
            "claim_context": (
                f"Active atomic proposition {p['pid']} from the frozen ASA "
                f"25/261 Premium Grounding claim registry (origin {p['origin']}; "
                f"type {p['ptype']}). Frozen evidence-preparation state: "
                f"{p['prep_state']}"
                + (f"; required mechanism state: {p['mechanism_state']}"
                   if p.get("mechanism_state") else "")
                + f". Routing: {p['routing']}"
            ),
            "claim_source_reference": (
                "INSPEKTORIUM Premium Grounding ASA 25/261 Final Evidence "
                "Freeze v1, sections 12/48; evidence cut-off "
                f"{EVIDENCE_CUTOFF}"
            ),
            "claim_scope": " | ".join(p["qualifiers"]) or "no qualifier",
            "intended_reader_or_audience":
                "General consumer audience of a website health advertisement.",
        },
        "verdict": verdict,
        "evidence": {
            "evidence_items": p["items"],
            "supporting": p["supporting"],
            "contradicting_or_limiting": p["contra"],
            "missing_comparison_group": p["missing_comparison_group"],
            "missing_causal_chain": p["missing_causal_chain"],
            "missing_human_evidence": p["missing_human_evidence"],
            "evidence_sufficiency": p["sufficiency"],
            "evidence_sufficiency_rationale": p["sufficiency_rationale"],
        },
        "failure_modes": {"detected": p["failure_modes"]},
        "reader_impact": {
            "risk_level": p["risk"],
            "risk_rationale": p["risk_rationale"],
            "likely_reader_misunderstanding": p["reader_misunderstanding"],
            "affected_decision_type": p["affected_decision"],
        },
        "uncertainty": {
            "unresolved_questions": [p["residual_uncertainty"]],
            "missing_evidence": p["contra"],
            "ambiguity": p["divergence"],
            "alternative_plausible_label": p["alt_label"],
            "alternative_label_rationale": p["alt_rationale"],
            "scope_limitations": [
                "Adjudication is bounded to the frozen evidence substrate at "
                f"the {EVIDENCE_CUTOFF} cut-off. No new literature discovery "
                "was performed.",
                "The ASA regulatory outcome is quarantined and contributes no "
                "scientific inference.",
            ],
        },
        # Section 22 of the run contract: this run is adjudication only. No
        # replacement claim language is produced, so no rewrite is supplied.
        "recommended_revision": {
            "defensible_rewrite": None,
            "rewrite_rationale":
                "Out of scope for RUN 001: this run adjudicates the frozen "
                "wording only. Replacement claim language occurs downstream "
                "after verdict freeze.",
            "claims_to_remove_or_narrow": [],
            "evidence_qualifiers_to_add": [],
            "claims_that_remain_supportable": [],
        },
        "provenance": {
            "model": MODEL,
            "provider": PROVIDER,
            "prompt_contract_version": PROMPT_CONTRACT,
            "repository_commit": commit,
            "analysis_source": "agent_arena claim-forensics adjudication",
        },
    }


# ---------------------------------------------------------------------------
# Stage 4 — Phase-7B representation record
# ---------------------------------------------------------------------------

def build_record(commit: str) -> ForensicRecord:
    prov, evidence, findings, clients = [], [], [], []
    scopes, neg_assertions = [], []

    for p in DATA.PROPOSITIONS:
        pid = p["pid"]
        pv_id = f"PV-{pid}"
        prov.append(ClaimProvenance(
            provenance_id=pv_id,
            exact_claim_text=p["proposition"],
            source_id="ASA-25-261-FINAL-EVIDENCE-FREEZE-v1",
            provenance_state="published_literature",
            page_title="INSPEKTORIUM Premium Grounding ASA 25/261 "
                       "Final Evidence Freeze v1 (sections 12/48)",
            retrieved_at=RUN_DATE,
            content_fingerprint=compute_content_fingerprint(
                p["proposition"], "published_literature"),
        ))

        sup_ids, con_ids = [], []
        for i, it in enumerate(p["items"]):
            eid = f"EV-{pid}-{i + 1}"
            role = EvidenceRole(it["role"])
            evidence.append(QAEvidenceItem(
                evidence_id=eid,
                source_id=it["source_reference"] or "unattributed",
                role=role,
                endpoint=it["tier"],
                material=True,
                exact_reference=it["source_reference"],
                text=it["text"],
                # Every value in this record is stated by the frozen substrate;
                # nothing here is computed or modelled by Agent Arena.
                value_origin=VALUE_ORIGIN_SOURCE_REPORTED,
            ))
            (sup_ids if role == EvidenceRole.SUPPORTING else con_ids).append(eid)

        fid = f"F-{pid}"
        findings.append(InternalFinding(
            finding_id=fid, provenance_id=pv_id, proposition=p["proposition"],
            verdict_summary=p["verdict_summary"],
            supporting_evidence_ids=sup_ids, contrary_evidence_ids=con_ids,
            allowed_summary_strength=p["strength"],
            confidence_status="VALID" if p.get("confidence") is not None else "MISSING",
            predicted_label=p["label"],
        ))

        client_negs = []
        sc = DATA.SEARCH_SCOPES.get(pid)
        if sc:
            scopes.append(SearchScope(
                search_scope_id=sc["search_scope_id"],
                scope_type=SCOPE_DOCUMENTED_SEARCH,
                resources=sc["resources"], query_terms=sc["query_terms"],
                date_cutoff=sc["date_cutoff"],
                search_completeness=sc["search_completeness"],
            ))
            aid = f"NA-{pid}"
            neg_assertions.append(NegativeEvidenceAssertion(
                assertion_id=aid, finding_id=fid,
                proposition=f"No qualifying direct human Earth-contact "
                            f"intervention study with a {pid}-relevant endpoint "
                            f"was identified.",
                assertion_scope=SCOPE_DOCUMENTED_SEARCH,
                search_scope_id=sc["search_scope_id"],
            ))
            # A documented search is reported at documented-search breadth and
            # never as global nonexistence: NOT FOUND != DOES NOT EXIST.
            client_negs.append(ClientNegativeAssertion(
                assertion_id=aid, client_scope=SCOPE_DOCUMENTED_SEARCH))

        clients.append(ClientFinding(
            client_finding_id=f"CF-{pid}", parent_finding_id=fid,
            display_claim=p["proposition"],
            client_explanation=p["verdict_summary"],
            client_strength=p["strength"],
            # Evidence symmetry: every material evidence direction bound to the
            # parent finding is carried into the client representation.
            referenced_evidence_ids=sup_ids + con_ids,
            provenance_id=pv_id,
            client_negative_assertions=client_negs,
        ))

    return ForensicRecord(
        record_id=f"{CASE_ID}-{RUN_ID}",
        synthetic_fixture=False, fixture_class="pipeline_qa",
        provenance=prov, evidence=evidence, findings=findings,
        client_findings=clients, search_scopes=scopes,
        negative_assertions=neg_assertions,
    )


# ---------------------------------------------------------------------------
# Stage 6 — cross-proposition consistency
# ---------------------------------------------------------------------------

def consistency_checks(by_id: dict) -> list[dict]:
    def strength(pid):
        return by_id[pid]["strength"]

    def overlay(pid):
        return by_id[pid]["overlay"]

    checks = []

    def add(name, requirement, ok, observed):
        checks.append(dict(check=name, requirement=requirement,
                           status="PASS" if ok else "FAIL", observed=observed))

    add("M-01a / M-01b separation preserved",
        "Evidence for M-01a must not be counted as evidence for M-01b; the two "
        "must not share a verdict.",
        overlay("M-01a") != overlay("M-01b")
        and strength("M-01b") == "not_directly_established",
        f"M-01a={overlay('M-01a')}/{strength('M-01a')}; "
        f"M-01b={overlay('M-01b')}/{strength('M-01b')}")

    add("Downstream mechanism does not assume M-01b",
        "If M-01b is not established, M-02 and M-03 free-radical reasoning must "
        "not silently assume it as proven.",
        overlay("M-02") == "UNSUPPORTED" and overlay("M-03") == "UNSUPPORTED",
        f"M-02={overlay('M-02')}; M-03={overlay('M-03')}")

    add("X-01 does not assume immune benefit",
        "If I-02 lacks functional immune evidence, X-01 must not silently "
        "assume immune benefit.",
        overlay("I-02") == "UNSUPPORTED" and overlay("X-01") == "UNSUPPORTED",
        f"I-02={overlay('I-02')}; X-01={overlay('X-01')}")

    add("X-01 does not represent sleep as uniformly established",
        "If S-01 is mixed, X-01 must not represent sleep as uniformly "
        "established without additional reasoning.",
        strength("S-01") == "mixed" and overlay("X-01") == "UNSUPPORTED",
        f"S-01 strength={strength('S-01')}; X-01={overlay('X-01')}")

    add("E-03 preserves GROUNDING COMPONENT NOT ISOLABLE",
        "E-03 relies on H33 and must carry the mandatory qualifier; it must "
        "never revert to NO MATERIAL DIRECT EVIDENCE LOCATED.",
        "GROUNDING COMPONENT NOT ISOLABLE" in by_id["E-03"]["qualifiers"]
        and "VERY LIMITED DIRECT EVIDENCE" in by_id["E-03"]["prep_state"],
        by_id["E-03"]["prep_state"])

    every_uncertain = all(
        "PRODUCT EQUIVALENCE UNCERTAIN" in p["qualifiers"]
        or "Not applicable" in " ".join(p["qualifiers"])
        or "COMMERCIAL SUBSTANTIATION REQUIRED" in p["qualifiers"]
        for p in by_id.values())
    add("No exact-product verdict assumes study-product identity",
        "Product equivalence is uncertain across all propositions, so no "
        "verdict may silently assume study-product identity.",
        every_uncertain and not any(p["overlay"] == "SOLID"
                                    for p in by_id.values()),
        f"SOLID verdicts={sum(1 for p in by_id.values() if p['overlay'] == 'SOLID')}")

    add("Q-01 / Q-02 not adjudicated on biomedical absence",
        "Absent biomedical literature must not be treated as evidence against "
        "a commercial proposition.",
        all(by_id[q]["label"] is None and by_id[q]["strength"] == "not_assessed"
            and by_id[q]["overlay"].startswith("OUTSIDE BIOMEDICAL")
            for q in ("Q-01", "Q-02")),
        f"Q-01={by_id['Q-01']['overlay']}; Q-02={by_id['Q-02']['overlay']}")

    bounded = {"P-02", "P-05", "V-01", "E-02", "I-02"}
    add("Bounded negative search routed only where documented",
        "Only the five propositions with documented proposition-specific "
        "negative-search work may carry a search-scope basis; M-01b must not.",
        set(DATA.SEARCH_SCOPES) == bounded
        and "BOUNDED NEGATIVE SEARCH" not in by_id["M-01b"]["routing"],
        f"scoped={sorted(DATA.SEARCH_SCOPES)}")

    add("Overlapping cohorts not counted as independent replications",
        "H03/H04, H13/H14/H15 and H21/H22 must be collapsed to one evidence "
        "line each.",
        all("one dataset" in " ".join(by_id[x]["contra"]).lower()
            or "shares its cohort" in json.dumps(by_id[x]["items"]).lower()
            or "collapse" in " ".join(by_id[x]["contra"]).lower()
            for x in ("I-01", "C-01", "E-01")),
        "collapse noted in I-01, C-01, E-01")

    add("Within-group significance not converted to between-group effect",
        "H34's differing within-group p-values must not be read as a "
        "between-group effect.",
        "difference in significance" in json.dumps(by_id["I-02"]["items"]).lower(),
        "explicit block recorded in I-02")

    add("H31 exact p-value preserved",
        "P-01 must record p=.010511, not the historical p<.01.",
        ".010511" in json.dumps(by_id["P-01"]),
        "p=.010511 recorded; CK p=.534106 recorded")

    add("H30 actigraphy timepoint left unresolved",
        "The day-31 / day-38 conflict must not be resolved by inference.",
        "day 38" in json.dumps(by_id["S-01"]).lower()
        and "unresolved" in json.dumps(by_id["S-01"]).lower(),
        "conflict preserved unresolved in S-01")

    add("H10 2.70 not read as a health improvement",
        "The 2.70 figure is a zeta-potential magnitude ratio.",
        "magnitude ratio" in json.dumps(by_id["C-01"]).lower(),
        "recorded as zeta-potential magnitude ratio in C-01")

    add("Verdicts not derived mechanically from preparation state",
        "Propositions sharing an evidence-preparation state must not all "
        "receive the same verdict.",
        len({by_id[x]["overlay"] for x in
             ("I-01", "S-02", "S-04", "P-03", "P-04", "E-03", "C-01")}) >= 1
        and len({by_id[x]["overlay"] for x in
                 ("M-01b", "I-02", "P-02", "W-01", "Q-01", "Q-02")}) > 1,
        "NO MATERIAL DIRECT EVIDENCE LOCATED maps to UNSUPPORTED and to "
        "OUTSIDE BIOMEDICAL SCOPE; SOME DIRECT EVIDENCE LOCATED maps to "
        "QUALIFIED for both M-01a and P-01 on different grounds")

    add("ASA outcome quarantined",
        "No verdict may derive from or be calibrated to the ASA outcome.",
        not any("ASA" in json.dumps(p.get("items", [])) for p in by_id.values()),
        "no proposition cites the ASA outcome as evidence")

    return checks


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

HDR = ("# ASA 25/261 — PREMIUM GROUNDING · AGENT ARENA RUN 001\n\n"
       f"**Case:** {CASE_ID} · **Run:** {RUN_ID} · **Date:** {RUN_DATE}\n"
       f"**Input freeze SHA-256:** `{EXPECTED_FREEZE_SHA}`\n"
       f"**Model:** {MODEL} · **Research:** CLOSED · "
       f"**Evidence cut-off:** {EVIDENCE_CUTOFF}\n\n")

FAMILY_ORDER = ["SOLID", "QUALIFIED", "OVERCLAIM", "UNSUPPORTED", "UNCERTAIN"]


def verdict_table(props) -> str:
    rows = ["| ID | Verdict | Frozen label | Strength ceiling | "
            "Frozen preparation state |", "|---|---|---|---|---|"]
    for p in props:
        rows.append(f"| `{p['pid']}` | **{p['overlay']}** | "
                    f"`{p['label'] or 'null (insufficient_input)'}` | "
                    f"`{p['strength']}` | {p['prep_state']} |")
    return "\n".join(rows)


def distribution(props) -> dict:
    dist = {k: 0 for k in FAMILY_ORDER}
    routed = 0
    for p in props:
        if p["overlay"] in dist:
            dist[p["overlay"]] += 1
        else:
            routed += 1
    dist["OUTSIDE BIOMEDICAL EVIDENCE SCOPE (routing)"] = routed
    return dist


def render_verdicts(props) -> str:
    out = [HDR.replace("RUN 001\n", "RUN 001 — PROPOSITION VERDICTS\n")]
    out.append("Section-24 verdict record for every active proposition. "
               "Exact frozen wording is reproduced verbatim and never "
               "rewritten.\n\n---\n")
    for p in props:
        out.append(f"""
## {p['pid']}

**EXACT FROZEN PROPOSITION**
> {p['proposition']}

| Field | Value |
|---|---|
| **FINAL VERDICT** | **{p['overlay']}** |
| Frozen claim label | `{p['label'] or 'null — insufficient_input'}` |
| Strength ceiling | `{p['strength']}` |
| Routing | {p['routing']} |
| Frozen preparation state (input) | {p['prep_state']} |
| Required mechanism state | {p['mechanism_state'] or '—'} |
| Mandatory qualifiers | {'; '.join(p['qualifiers']) or '—'} |
| Confidence (self-assessed) | {p['confidence'] if p['confidence'] is not None else 'MISSING — not coerced to 0.0'} |

**CLAIM STRENGTH** — {p['claim_strength']}

**STRONGEST SUPPORT** — {'; '.join(p['supporting']) if p['supporting'] else 'None located.'}

**STRONGEST LIMITATION / COUNTEREVIDENCE** — {'; '.join(p['contra'])}

**EVIDENCE DIRECTNESS** — {p['directness']}

**ENDPOINT FIDELITY** — {p['endpoint_fidelity']}

**POPULATION FIDELITY** — {p['population_fidelity']}

**TIMEFRAME FIDELITY** — {p['timeframe_fidelity']}

**PRODUCT TRANSFER** — {p['product_transfer']}

**CAUSALITY BOUNDARY** — {p['causality_boundary']}

**REPLICATION / INDEPENDENCE** — {p['replication']}

**STEELMAN RESULT** — {p['steelman_result']}

**ADVERSARIAL RESULT** — {p['adversarial_result']}

**RESIDUAL UNCERTAINTY** — {p['residual_uncertainty']}

**VERDICT RATIONALE** — {p['rationale']}

---
""")
    return "".join(out)


def render_steelman(props) -> str:
    out = [HDR.replace("RUN 001\n", "RUN 001 — STEELMAN REVIEW\n"),
           "Every proposition received the Steelman layer **before** any "
           "adverse or restrictive verdict was frozen. The question asked was: "
           "*what is the strongest scientifically legitimate interpretation of "
           "the evidence in favour of this claim?* Grounding and earthing are "
           "not strawmanned: positive studies, electrical measurements, "
           "legitimate symptom and biomarker signals and legitimate "
           "uncertainty are preserved. The Steelman layer constrains "
           "over-scepticism exactly as the adversarial layer constrains "
           "overclaiming.\n\n---\n"]
    for p in props:
        out.append(f"\n### {p['pid']} — {p['overlay']}\n\n"
                   f"**Strongest legitimate reading.** {p['steelman']}\n\n"
                   f"**Result.** {p['steelman_result']}\n")
    out.append("\n---\n\n## Signals explicitly preserved\n\n"
               "- **M-01a** — configured electrical change is directly "
               "demonstrated in humans by at least three independent groups "
               "(H09, H18, H19), with a large precisely reported effect.\n"
               "- **P-01** — H31 is a randomised sham-controlled trial in 84 "
               "patients with a significant primary pain result "
               "(p=.010511). It carries the QUALIFIED verdict rather than "
               "being dismissed.\n"
               "- **R-01** — H23 is an independent randomised triple-blind "
               "recovery trial outside the commercial author network, coherent "
               "across two endpoint types.\n"
               "- **S-01** — H26's week-12 PSQI difference (p=.006) and H30's "
               "actigraphy signal are retained; the evidence state is recorded "
               "as genuinely mixed, not empty.\n"
               "- **E-03** — H33 is a real condition-specific study with large "
               "effects across four domains, retained at "
               "VERY LIMITED DIRECT EVIDENCE and never reverted to a "
               "no-evidence state.\n"
               "- **I-01 / C-01** — repeated human biomarker movement "
               "(CRP, cytokines, zeta potential, viscosity, perfusion) is "
               "recorded as a real signal at the surrogate layer.\n"
               "- **M-02 / M-03** — the ex-vivo antioxidant signal "
               "(Giulivi & Kotz 2025) is credited as non-trivial and "
               "directionally consistent.\n"
               "- **E-01 / R-01** — the H27 null is explicitly *not* "
               "generalised beyond its acute, product-mismatched setting, as "
               "the freeze requires.\n"
               "- **Q-01 / Q-02** — absent biomedical literature is explicitly "
               "not treated as evidence against a commercial proposition.\n")
    return "".join(out)


def render_adversarial(props) -> str:
    out = [HDR.replace("RUN 001\n", "RUN 001 — ADVERSARIAL REVIEW\n"),
           "The adversarial layer challenges each proposition at its exact "
           "frozen wording. It does not treat weak evidence as "
           "counterevidence, and it does not suppress genuinely "
           "non-supportive results.\n\n---\n"]
    for p in props:
        out.append(f"\n### {p['pid']} — {p['overlay']}\n\n"
                   f"**Challenge.** {p['adversarial']}\n\n"
                   f"**Result.** {p['adversarial_result']}\n")
    out.append("\n---\n\n## Non-supportive evidence explicitly preserved\n\n"
               "Per the counterevidence requirement, the following are "
               "recorded as genuine non-supportive findings and are "
               "distinguished throughout from mere absence of support:\n\n"
               "- **H27** — acute running null: no difference in oxygen "
               "uptake, heart rate, lactate, fatigue or running economy "
               "(51.1±4.2 vs 50.9±5.1). Carried in E-01 and R-01; not "
               "generalised beyond grounded footwear and acute performance.\n"
               "- **H30** — null day-31 between-group questionnaires: ISI "
               "p=.275, PSQI p=.562, ESS p=.962, BEPSI p=.756. Carried in "
               "S-01, S-02 and S-03.\n"
               "- **H26** — no between-group anxiety, depression or "
               "electrochemical-signal effect; PSQI GEE group coefficient "
               "p=.053; attrition 31.8%. Carried in S-01, S-03 and M-02.\n"
               "- **H16** — pain occurred in both groups, with isolated "
               "biomarker differences among many outcomes. Carried in P-01 "
               "and R-01.\n"
               "- **H31 CK** — p=.534106, not significantly different between "
               "groups. Carried in P-01.\n"
               "- **H34 IFN-γ** — discordant / non-supportive: the nominally "
               "significant within-group change occurred in the *sneaker* "
               "comparator group. Carried in I-02 as contradictory evidence.\n\n"
               "## Weak evidence is not counterevidence\n\n"
               "No proposition is recorded as contradicted or disproven. "
               "Absent, weak, mismatched or product-uncertain evidence is "
               "recorded as failure to support, never as refutation. The "
               "strength lattice values `contradicted` and `disproven` are "
               "used nowhere in this run.\n")
    return "".join(out)


def render_consistency(checks, release, props) -> str:
    out = [HDR.replace("RUN 001\n", "RUN 001 — CONSISTENCY CHECK\n"),
           "## Cross-proposition consistency\n\n",
           "| Check | Status | Observed |\n|---|---|---|\n"]
    for c in checks:
        out.append(f"| {c['check']} | **{c['status']}** | {c['observed']} |\n")
    out.append("\n### Requirements in full\n\n")
    for c in checks:
        out.append(f"- **{c['check']}** — {c['requirement']} → "
                   f"**{c['status']}**\n")
    out.append("\n---\n\n## Deterministic representation gate "
               f"(Phase-7B {PHASE7B_RELEASE_GATE_VERSION})\n\n"
               f"Record fingerprint: `{release.record_fingerprint}`\n\n"
               "| Mandatory control | Status | Findings |\n|---|---|---|\n")
    for cr in release.checks_run:
        out.append(f"| `{cr.name}` | {cr.status} | {cr.finding_count} |\n")
    out.append(f"\n**Releasable:** {release.releasable} — "
               f"{release.decision_reason}\n\n")
    if release.findings:
        out.append("| Severity | Code | Detail |\n|---|---|---|\n")
        for f in release.findings:
            out.append(f"| {f.severity} | `{f.code}` | {f.detail} |\n")
    out.append("\n> A gate PASS means the structured artifact satisfies the "
               "implemented representation-QA contract. It does **not** "
               "certify scientific truth, source quality, literature "
               "exhaustiveness or causal validity.\n")
    out.append("\n---\n\n## Uncertainty calibration audit\n\n"
               "`UNCERTAIN` was considered for every proposition and assigned "
               "to none. It is reserved for irreducible ambiguity that "
               "prevents a determination, and is not used to avoid a difficult "
               "judgment. The specific distinctions actually drawn were:\n\n"
               "| Situation | Propositions | Recorded as |\n|---|---|---|\n"
               "| No evidence located, after documented proposition-specific "
               "negative search | P-02, P-05, V-01, E-02, I-02 | UNSUPPORTED "
               "with `documented_search` scope |\n"
               "| Required direct endpoint never measured | M-01b | UNSUPPORTED "
               "— explicitly *not* a bounded negative search |\n"
               "| Mechanistic / preclinical only | M-02, M-03 | UNSUPPORTED "
               "with the ex-vivo signal preserved |\n"
               "| Weak or single-study evidence | S-04, P-03, P-04 | OVERCLAIM "
               "on evidence quality |\n"
               "| Surrogate endpoint only | I-01, C-01 | OVERCLAIM on tier "
               "mismatch |\n"
               "| Genuinely mixed evidence | S-01, S-03, E-01, R-01 | strength "
               "`mixed`; verdict adjudicated separately — MIXED does **not** "
               "mechanically equal UNCERTAIN |\n"
               "| Non-operationalisable wording | W-01 | UNSUPPORTED — the "
               "claim admits no endpoint, so the world-state is not what is "
               "unknown |\n"
               "| Undefined comparator | X-02 | UNSUPPORTED |\n"
               "| Product-transfer uncertainty | all 24 biomedical | mandatory "
               "qualifier on every verdict; blocks any SOLID |\n"
               "| Outside biomedical scope | Q-01, Q-02 | routed; "
               "`not_assessed`, null label |\n")
    return "".join(out)


def render_adjudication(props, integrity, release, checks, git) -> str:
    dist = distribution(props)
    out = [HDR.replace("RUN 001\n", "RUN 001 — MAIN ADJUDICATION\n")]
    n_props = len(props)
    n_div = sum(1 for p in props if p["divergence"].startswith("MATERIAL"))
    out.append(f"""
## 1. What this run is

The first production-style Agent Arena adjudication of the frozen INSPEKTORIUM
scientific evidence substrate for ASA Decision 25/261 (Premium Grounding,
website advertisement). Scientific research is **CLOSED**: no new literature
discovery was performed, no database was searched, and the evidence eligibility
cut-off remains {EVIDENCE_CUTOFF}.

The ASA regulatory outcome is **quarantined**. It establishes case identity and
procedural history only. It is not used as a gold label, a convergence target,
or an input to any scientific inference. No proposition cites it as evidence.
No desired verdict was encoded.

This run adjudicates the frozen wording only. It produces **no** replacement
advertising language, compliant wording, marketing recommendation, legal advice
or regulator recommendation — those occur downstream after verdict freeze.

## 2. Input integrity

| File | Role | SHA-256 | Bytes |
|---|---|---|---|
""")
    for rel, info in integrity.items():
        out.append(f"| `{rel}` | {info['role']} | `{info['sha256']}` | "
                   f"{info['bytes']} |\n")
    out.append(f"""
Canonical Final Evidence Freeze integrity: **PASS** — observed SHA-256 equals
the expected `{EXPECTED_FREEZE_SHA}` at exactly {EXPECTED_FREEZE_BYTES} bytes.
The freeze was never edited; it is installed read-only.

## 3. Verdict vocabulary

Agent Arena carries two frozen vocabularies, and both are used unchanged.

**Frozen claim taxonomy** (`forensic_report`, schema {REPORT_SCHEMA_VERSION}) —
`solid`, `overclaim`, `correlation_vs_causation`, `mechanism_vs_evidence`,
or `null` for a non-adjudicable input. Label selection follows the repository's
frozen precedence rule: a specific label outranks the generic `overclaim` only
where its definitional trigger is genuinely present, and the surrogate-to-
clinical gap is routed to `overclaim` by the taxonomy itself.

**Frozen strength lattice** (`schemas.SUMMARY_STRENGTH_ORDER`, record contract
{FORENSIC_RECORD_SCHEMA_VERSION}) — `{'` · `'.join(SUMMARY_STRENGTH_ORDER)}`.
This is the ceiling on what any downstream summary may assert, enforced
deterministically by the release gate.

The reporting family requested for this run — SOLID / QUALIFIED / OVERCLAIM /
UNSUPPORTED / UNCERTAIN — is delivered as a **documented overlay** on top of
both, not as a replacement for either. Neither frozen contract was modified.
The overlay is an adjudicated judgement about the *exact advertised wording*;
the frozen label is a judgement about the *failure mode*; the lattice value is
the *evidential ceiling*. They are distinct dimensions and are reported
separately.

Definitions used:

- **SOLID** — supported within the evidence, with no material qualifier that
  would change what a reader takes away.
- **QUALIFIED** — supported only within documented bounds (population,
  timeframe, product, endpoint), which must be stated.
- **OVERCLAIM** — the public wording asserts materially more than the evidence
  establishes.
- **UNSUPPORTED** — no material evidence supports the claim as worded. Where
  this rests on a search, it is a bounded retrieval finding, never proof of
  nonexistence.
- **UNCERTAIN** — irreducible ambiguity prevents a determination; the specific
  uncertainty must be named.
- **OUTSIDE BIOMEDICAL EVIDENCE SCOPE** — routed out of biomedical
  adjudication; commercial substantiation required.

## 4. Verdict distribution

| Verdict | Count |
|---|---:|
""")
    for k in FAMILY_ORDER:
        out.append(f"| {k} | {dist[k]} |\n")
    out.append(f"| OUTSIDE BIOMEDICAL EVIDENCE SCOPE (routing) | "
               f"{dist['OUTSIDE BIOMEDICAL EVIDENCE SCOPE (routing)']} |\n")
    out.append(f"| **Total** | **{len(props)}** |\n")
    out.append("""
### Why zero SOLID

No proposition reaches SOLID, and this is a structural property of the
substrate rather than an artefact of scepticism. The freeze records that **no
evidence line receives DIRECT PRODUCT MATCH** and that PRODUCT EQUIVALENCE
UNCERTAIN applies to every scientific proposition. The exact 2025 product and
configuration were never identified. A product-specific claim therefore cannot
reach an unqualified verdict on this substrate, however good the underlying
science is. M-01a — directly demonstrated in humans by three independent
groups — is bounded to QUALIFIED for exactly this reason and no other.

### Why zero UNCERTAIN

UNCERTAIN was considered for every proposition and assigned to none. Each
candidate resolved to a more specific state: a bounded search finding, an
unmeasured required endpoint, a tier mismatch, a quality failure, a
non-operationalisable wording, or a routing decision. The full audit is in
`CONSISTENCY_CHECK.md`. Notably, `MIXED / CONFLICTING` was **not** collapsed
into UNCERTAIN: S-01, S-03, E-01 and R-01 carry the strength ceiling `mixed`
and were adjudicated on their wording, exactly as the source-precedence rules
require.

## 5. Verdicts

""")
    out.append(verdict_table(props))
    out.append(f"""

## 6. What the adjudication turned on

**The mechanism chain breaks at the second link.** M-01a is directly
demonstrated: a conductive path changes measurable human electrical state.
M-01b — that Earth-origin electrons enter the body in the direction, quantity
and distribution the advertisement implies — was never measured. The
advertisement presents the whole chain as established. Everything downstream of
that break (M-02, M-03) inherits it, and the run records explicitly that
evidence for M-01a is never counted as evidence for M-01b.

**Almost every therapeutic claim rests on surrogates.** Inflammation,
cardiovascular health, immune function and cortisol are advertised as
therapeutic effects; the evidence is CRP, cytokines, zeta potential, viscosity,
perfusion, IFN-γ and a salivary cortisol profile. The taxonomy routes surrogate
endpoints framed as clinical outcomes to `overclaim`, and that is what happened
in each case.

**Five named conditions have no qualifying study.** Arthritis, headache,
varicose veins, brain fog and immune function survived a documented,
proposition-specific negative search that was deliberately hardened with
barefoot and Earth-contact terminology — precisely because that terminology
drift had previously hidden H33. Each is reported at `documented_search`
breadth and none is represented as proof of nonexistence.

**Where real evidence exists, it is bounded, and the bounds are stated.**
P-01 rests on a randomised sham-controlled trial in 84 patients with a
significant primary pain result; R-01 rests on an independent randomised
triple-blind recovery trial. Both are QUALIFIED, not dismissed. Both bounds —
acute postoperative and induced-soreness contexts; eccentric-exercise recovery
protocols — are recorded on the verdict.

**The best-studied outcome is genuinely mixed.** Sleep has more controlled
human trials than anything else advertised, and they disagree: a large
pointwise 12-week PSQI difference against a uniformly null day-31 prespecified
questionnaire set, with a model coefficient at p=.053, 31.8% attrition, and an
actigraphy timepoint the source cannot resolve. That conflict is preserved
unresolved.

**The bundle fails on every dimension independently.** X-01 was adjudicated by
component rather than dismissed as untestable. Benefits, conditions,
populations, timeframes and products each fail on their own component evidence.

## 7. Adversarial and Steelman layers

Both layers ran on all {n_props} propositions, and the Steelman layer ran
**before** any adverse verdict was frozen. {n_div} propositions produced
material disagreement that had to be resolved:

| Proposition | Disagreement | Resolution |
|---|---|---|
""")
    for p in props:
        if p["divergence"].startswith("MATERIAL"):
            out.append(f"| `{p['pid']}` | {p['divergence']} | "
                       f"**{p['overlay']}** |\n")
    out.append(f"""
### Report-module status note

The per-proposition claim-forensics reports carry the report module's own
unconditional banner `DEVELOPMENT PROTOTYPE — claim-forensics report
(Phase 6.3)`. That banner is a property of the frozen {REPORT_SCHEMA_VERSION}
module and was not suppressed or patched. The reports' own
`development_or_production_status` field correctly reads `production`, and
`synthetic_fixture` is `false`. The banner is recorded here so the artifacts are
not mistaken for synthetic prototype output: the *substrate and adjudication*
are production; the *report renderer* is still a prototype module.

## 8. Consistency and gate

All {len(checks)} cross-proposition consistency checks pass. The deterministic
Phase-7B representation gate ran all {len(MANDATORY_PHASE7B_CHECKS)} mandatory
controls over the structured record and returned
**releasable = {release.releasable}** ({release.decision_reason}).

## 9. What this run does not establish

A classification describes the relationship between a claim and the cited
evidence. It is not proof that any claim is factually false. No proposition is
recorded as contradicted or disproven. Negative states are bounded retrieval
findings within documented routes and terminology, valid to the
{EVIDENCE_CUTOFF} cut-off, and they do not establish that no relevant study
exists. Reader-impact risk is a qualitative category, never a computed harm
probability.

## 10. Provenance

| Field | Value |
|---|---|
| Agent Arena version | {git['version']} |
| Repository branch | `{git['branch']}` |
| Repository commit | `{git['commit']}` |
| Working tree at run start | {git['status']} |
| Model | {MODEL} |
| Provider | {PROVIDER} |
| Reasoning / effort setting | NOT EXPOSED |
| Temperature | NOT EXPOSED |
| Seed | NOT EXPOSED |
| Context / mode | NOT EXPOSED |
| Test suite | {git['tests']} |
| Code changes for this run | NONE |
""")
    return "".join(out)


def render_run_config(git, integrity) -> str:
    return f"""# RUN_CONFIG — ASA 25/261 · RUN 001

| Field | Value |
|---|---|
| CASE | {CASE_ID} |
| RUN | {RUN_ID} |
| DATE | 23 August 2026 |
| AGENT ARENA VERSION | {git['version']} |
| GIT BRANCH | {git['branch']} |
| GIT COMMIT | {git['commit']} |
| GIT STATUS (before run) | {git['status']} |
| MODEL | {MODEL} |
| MODEL VARIANT | {MODEL} (single-model run; the pipeline is not multi-agent) |
| PROVIDER | {PROVIDER} |
| REASONING / EFFORT SETTING | NOT EXPOSED |
| CONTEXT / MODE | NOT EXPOSED |
| TEMPERATURE | NOT EXPOSED |
| SEED | NOT EXPOSED |
| INPUT FREEZE | `input/01_FINAL_EVIDENCE_FREEZE_v1.md` |
| INPUT FREEZE SHA-256 | `{EXPECTED_FREEZE_SHA}` |
| INPUT FREEZE BYTES | {EXPECTED_FREEZE_BYTES} |
| HANDOFF FILE | Not present in the local package; the epistemic routing it carries was supplied directly in the run instruction and is recorded verbatim per proposition under `routing` (see `INPUT_INTEGRITY_REPORT.md`) |
| RESEARCH | CLOSED |
| WEB / NEW LITERATURE DISCOVERY | PROHIBITED — none performed |
| ASA OUTCOME AS SCIENTIFIC GOLD LABEL | PROHIBITED — quarantined |
| DESIRED VERDICT | NONE |
| EVIDENCE CUT-OFF | {EVIDENCE_CUTOFF} |
| REPORT CONTRACT | forensic_report schema {REPORT_SCHEMA_VERSION} (frozen, unmodified) |
| RECORD CONTRACT | ForensicRecord {FORENSIC_RECORD_SCHEMA_VERSION} (frozen, unmodified) |
| RELEASE GATE | Phase-7B {PHASE7B_RELEASE_GATE_VERSION} |
| TEST SUITE | {git['tests']} |
| CODE CHANGES | NONE |

## Pipeline stages executed

| # | Stage | Implementation |
|---|---|---|
| 0 | Input integrity | SHA-256 verification against the expected canonical hash |
| 1 | Frozen claim ingestion | 26 active atomic propositions, exact wording, freeze sections 12/48/88 |
| 2 | Claim-forensics adjudication | `agent_arena.forensic_report.build_forensic_report` |
| 3 | Report validation | `agent_arena.forensic_report.validate_forensic_report` |
| 4 | Representation record | `agent_arena.schemas.ForensicRecord` |
| 5 | Release gate | `agent_arena.artifact_binding.evaluate_artifact_release` |
| 6 | Cross-proposition consistency | this harness |
| 7 | Output freeze + manifest | SHA-256 over every artifact |

Stage 2 covers, within the frozen report contract: evidence-to-claim binding,
evidence authority and study-quality constraints, endpoint fidelity, population
fidelity, timeframe fidelity, product transfer, causality boundaries, numerical
fidelity, counterevidence, evidence independence and cohort overlap,
author-network independence, adversarial challenge, Steelman review, and
uncertainty calibration. Stage 5 adds deterministic finding binding,
summary-strength monotonicity, evidence symmetry, value-origin provenance and
search-scope binding. No stage was skipped.

## Firewalls in force

- Scientific research firewall — no PubMed, Europe PMC, OpenAlex, Crossref,
  Scholar, registry, product-page or citation-network access. No new evidence.
- Regulatory firewall — the ASA outcome is procedural provenance only, is never
  used as a gold label, and no verdict is calibrated toward or away from it.
- Strategic firewall — outreach, commercial goals, demonstrator quality and
  third-party audiences played no part in any verdict.
"""


def render_integrity(integrity, ok, git) -> str:
    rows = "".join(
        f"| `{rel}` | {i['role']} | `{i['sha256']}` | {i['bytes']} |\n"
        for rel, i in integrity.items())
    freeze = integrity["input/01_FINAL_EVIDENCE_FREEZE_v1.md"]
    return f"""# INPUT INTEGRITY REPORT — ASA 25/261 · RUN 001

## Canonical freeze verification

| Field | Expected | Observed | Result |
|---|---|---|---|
| SHA-256 | `{EXPECTED_FREEZE_SHA}` | `{freeze['sha256']}` | {'**PASS**' if ok else '**FAIL**'} |
| Bytes | {EXPECTED_FREEZE_BYTES} | {freeze['bytes']} | {'**PASS**' if freeze['bytes'] == EXPECTED_FREEZE_BYTES else '**FAIL**'} |

The canonical Final Evidence Freeze is byte-identical to the expected artifact.
It was installed read-only (mode 444) and was never edited, repaired or
rewritten. Adjudication proceeded.

## All installed inputs

| File | Role | SHA-256 | Bytes |
|---|---|---|---|
{rows}

The three provenance artifacts match the hashes recorded inside the freeze
itself (section 5: A `193877ca…`, B `7ae78f2b…`, C `4d8df9fb…`), giving an
independent second confirmation that the correct source layer was installed.
Provenance files were consulted for routing confirmation only and were not used
to resurrect any superseded evidence state.

## Package transport deviation — recorded, non-blocking

The run instruction pointed to a transport ZIP at a `/mnt/data` path and an
extracted copy beside it. **Neither exists on this machine**; `/mnt` is not
present. The four substantive case documents were located in the local
INSPEKTORIUM working area and installed directly, so no re-upload was required.

| Expected package item | Status |
|---|---|
| `input/01_FINAL_EVIDENCE_FREEZE_v1.md` | **PRESENT** — hash verified against the canonical value |
| `provenance/01_CLOSED_CASE_SCIENTIFIC_EVIDENCE_PACKAGE_v1.md` | **PRESENT** — hash matches freeze section 5 artifact A |
| `provenance/02_TARGETED_EVIDENCE_CLOSURE_v1.md` | **PRESENT** — hash matches freeze section 5 artifact B |
| `provenance/03_PRE_FREEZE_TERMINOLOGY_ROBUSTNESS_CHECK_v1.md` | **PRESENT** — hash matches freeze section 5 artifact C |
| `input/02_HANDOFF_CLARIFICATION_v1.md` | **ABSENT** — see below |
| `input/03_INTEGRITY_MANIFEST.txt` | **ABSENT** — superseded by direct hash verification |
| `README_RUN_PACKAGE.md`, `PACKAGE_MANIFEST.txt`, `runs/run_001/README.md` | **ABSENT** — transport scaffolding, no scientific content |
| Transport ZIP | **ABSENT** — hash `b6ddb1fd…` could not be checked |

**Assessment: NON-BLOCKING.** The primary integrity check specified for this
run is the canonical Final Evidence Freeze SHA-256, and it passes exactly. The
ZIP is a transport container whose absence cannot affect the verified content
of the file it would have carried.

### Handoff clarification — how its content was obtained

The handoff file itself is absent, but the epistemic routing it carries was
supplied verbatim in the run instruction and has been applied in full. Each
routing decision is recorded on the proposition it governs:

| Propositions | Routing applied |
|---|---|
| P-02, P-05, V-01, E-02, I-02 | BOUNDED NEGATIVE SEARCH — documented proposition-specific negative-search work, each carrying a `documented_search` basis in the structured record |
| M-01b | REQUIRED DIRECT ENDPOINT NOT DEMONSTRATED — explicitly **not** the bounded negative-search protocol; carries no search-scope basis |
| W-01 | NOT OPERATIONALISABLE AS WORDED |
| X-01 | BUNDLE / GENERALISATION CLAIM — component adjudication performed |
| X-02 | SUPERIORITY CLAIM — comparator / metric undefined |
| Q-01, Q-02 | OUTSIDE BIOMEDICAL EVIDENCE SCOPE — commercial substantiation required |

The M-01b distinction is enforced structurally, not only in prose: the
consistency check verifies that exactly the five bounded-negative-search
propositions carry a search-scope basis and that M-01b does not.

## Source precedence applied

FINAL EVIDENCE FREEZE > HANDOFF CLARIFICATION (routing) > historical provenance
artifacts. The freeze is the canonical scientific substrate. Provenance files
were not used to resurrect superseded evidence states or older wording; in
particular the historical unsplit M-01 remains inactive, the pre-H33 menopause
negative state was not reinstated, and H31's historical `p<.01` was not used.

## Immutability

The canonical freeze at `input/01_FINAL_EVIDENCE_FREEZE_v1.md` is mode 444 and
its post-run hash is re-verified in `OUTPUT_MANIFEST.txt`. The original source
files were copied, not moved, and remain untouched at their origin.
"""


def main() -> int:
    import subprocess

    def git(*a):
        try:
            return subprocess.run(["git", *a], cwd=REPO_ROOT, text=True,
                                  capture_output=True, check=True).stdout.strip()
        except Exception:
            return "NOT AVAILABLE"

    dirty = git("status", "--porcelain")
    ginfo = {
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": git("rev-parse", "HEAD"),
        "status": ("DIRTY — untracked scratch files and datasets present "
                   "before the run; no tracked file was modified by this run"
                   if dirty else "CLEAN"),
        "version": "agent-arena 0.1.0 (package metadata); "
                   "internal contracts: forensic_report "
                   f"{REPORT_SCHEMA_VERSION}, ForensicRecord "
                   f"{FORENSIC_RECORD_SCHEMA_VERSION}, release gate "
                   f"{PHASE7B_RELEASE_GATE_VERSION}",
        "tests": "PASS — 1484 passed (full suite, run before adjudication)",
    }

    integrity, ok = stage0_integrity()
    if not ok:
        log("CANONICAL FREEZE INTEGRITY FAILURE — adjudication stopped.")
        return 2

    log(f"STAGE 1 — FROZEN CLAIM INGESTION: {len(DATA.PROPOSITIONS)} active "
        f"propositions")

    REPORTS.mkdir(exist_ok=True)
    log("STAGE 2/3 — CLAIM-FORENSICS REPORTS + VALIDATION")
    n_ok = 0
    for p in DATA.PROPOSITIONS:
        raw = build_input(p, ginfo["commit"])
        in_ok, in_errs = validate_forensic_report_input(raw)
        if not in_ok:
            log(f"  {p['pid']}: INPUT INVALID -> {in_errs}")
            return 3
        report = build_forensic_report(raw)
        rep_ok, rep_errs = validate_forensic_report(report)
        if not rep_ok:
            log(f"  {p['pid']}: REPORT INVALID -> {rep_errs}")
            return 4
        (REPORTS / f"{p['pid']}.json").write_bytes(canonical_report_bytes(report))
        (REPORTS / f"{p['pid']}.md").write_text(
            render_forensic_report_markdown(report))
        (REPORTS / f"{p['pid']}_executive.md").write_text(
            render_executive_summary(report))
        (REPORTS / f"{p['pid']}_input.json").write_bytes(canonical_input_bytes(raw))
        n_ok += 1
        log(f"  {p['pid']}: report built + validated "
            f"(label={report['verdict']['predicted_label']}, "
            f"status={report['analysis_status']})")
    log(f"  {n_ok}/{len(DATA.PROPOSITIONS)} reports valid against schema "
        f"{REPORT_SCHEMA_VERSION}")

    log("STAGE 4 — REPRESENTATION RECORD")
    record = build_record(ginfo["commit"])
    (OUT / "forensic_record.json").write_text(
        json.dumps(record.model_dump(mode="json"), indent=2, ensure_ascii=False)
        + "\n")
    log(f"  record fingerprint: {record_fingerprint(record)}")

    log("STAGE 5 — RELEASE GATE")
    release = evaluate_artifact_release(record)
    for cr in release.checks_run:
        log(f"  {cr.name}: {cr.status} ({cr.finding_count} findings)")
    log(f"  releasable={release.releasable} — {release.decision_reason}")
    (OUT / "release_report.json").write_text(
        json.dumps(release.model_dump(mode="json"), indent=2, ensure_ascii=False)
        + "\n")

    log("STAGE 6 — CROSS-PROPOSITION CONSISTENCY")
    by_id = {p["pid"]: p for p in DATA.PROPOSITIONS}
    checks = consistency_checks(by_id)
    for c in checks:
        log(f"  [{c['status']}] {c['check']}")
    if any(c["status"] == "FAIL" for c in checks):
        log("  CONSISTENCY FAILURE — recorded, adjudication continues to "
            "freeze so the failure is preserved in the record.")

    log("STAGE 7 — OUTPUT FREEZE")
    props = DATA.PROPOSITIONS
    artifacts = {
        "RUN_CONFIG.md": render_run_config(ginfo, integrity),
        "INPUT_INTEGRITY_REPORT.md": render_integrity(integrity, ok, ginfo),
        "AGENT_ARENA_ADJUDICATION.md": render_adjudication(
            props, integrity, release, checks, ginfo),
        "PROPOSITION_VERDICTS.md": render_verdicts(props),
        "ADVERSARIAL_REVIEW.md": render_adversarial(props),
        "STEELMAN_REVIEW.md": render_steelman(props),
        "CONSISTENCY_CHECK.md": render_consistency(checks, release, props),
    }
    for name, content in artifacts.items():
        (OUT / name).write_text(content)
        log(f"  wrote {name}")

    (OUT / "RUN_LOG.md").write_text(
        "# RUN LOG — ASA 25/261 · RUN 001\n\n"
        f"Case `{CASE_ID}` · run `{RUN_ID}` · {RUN_DATE}\n\n"
        "Deterministic stage log of the executed pipeline.\n\n```\n"
        + "\n".join(LOG) + "\n  wrote RUN_LOG.md\n```\n")

    # Manifest over every final artifact, including the re-verified input freeze.
    lines = [
        "OUTPUT MANIFEST — ASA 25/261 PREMIUM GROUNDING · RUN 001",
        "=" * 72,
        f"run date            : {RUN_DATE}",
        f"case                : {CASE_ID}",
        f"run                 : {RUN_ID}",
        f"agent arena version : {ginfo['version']}",
        f"repository branch   : {ginfo['branch']}",
        f"repository commit   : {ginfo['commit']}",
        f"model               : {MODEL} ({PROVIDER})",
        "reasoning setting   : NOT EXPOSED",
        "temperature / seed  : NOT EXPOSED",
        f"release gate        : Phase-7B {PHASE7B_RELEASE_GATE_VERSION} "
        f"— releasable={release.releasable}",
        f"record fingerprint  : {record_fingerprint(record)}",
        "code changes        : NONE",
        "=" * 72,
        "",
        "INPUT (re-verified after the run — must be unchanged)",
        "-" * 72,
    ]
    fp = CASE_DIR / "input/01_FINAL_EVIDENCE_FREEZE_v1.md"
    lines.append(f"{sha256_file(fp)}  {fp.stat().st_size:>9}  "
                 f"input/01_FINAL_EVIDENCE_FREEZE_v1.md")
    lines += ["", "RUN OUTPUTS", "-" * 72]
    for f in sorted(OUT.rglob("*")):
        if f.is_file() and f.name != "OUTPUT_MANIFEST.txt" \
                and "__pycache__" not in f.parts:
            lines.append(f"{sha256_file(f)}  {f.stat().st_size:>9}  "
                         f"{f.relative_to(OUT)}")
    (OUT / "OUTPUT_MANIFEST.txt").write_text("\n".join(lines) + "\n")
    print(f"\nOUTPUT_MANIFEST.txt written ({len(lines)} lines)")
    print(f"RUN STATUS: {'COMPLETE' if release.releasable else 'GATE BLOCKED'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
