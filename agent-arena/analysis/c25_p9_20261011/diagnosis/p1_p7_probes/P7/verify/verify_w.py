"""Independent verifier probe for P7-F1 (offline only, OfflineReviewProvider, no network).

Builds each case from tests/phase8_case_factory.raw_record in the read-only checkout and
runs the canonical offline audit (run_audit -> runner -> Phase8 -> _phase7_controls ->
Phase9 -> Phase10 evaluate -> bundle). Bundles are written under ./out only.
"""
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

BASE = ("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/"
        "cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base")
sys.path[:0] = [BASE + "/src", BASE]
OUT = Path(__file__).resolve().parent / "out"

from agent_arena import artifact_binding as ab  # noqa: E402
from agent_arena.phase10_bundle import inspect_bundle, release_candidate, run_audit  # noqa: E402
from agent_arena.phase8_pipeline import assess_forensic_payload  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.schemas import ForensicRecord, Task  # noqa: E402
from tests.phase8_case_factory import raw_record  # noqa: E402

assert ab.__file__.startswith(BASE), ab.__file__

WEAK = ("A second randomized comparison in adults found that agent Gamma did not "
        "reduce endpoint Delta versus placebo at 12 weeks.")


def taxonomy(p):
    p["phase8_taxonomy"] = {
        "core_error": "none", "causal_claim": True, "noncausal_result_used": False,
        "described_biological_mechanism": False, "implies_human_benefit": True,
        "proposition_ids": ["claim:p1"], "evidence_ids": ["e1"],
        "trigger_proposition_id": "claim:p1", "trigger_evidence_id": "e1",
        "trigger_quote": p["evidence"][0]["text"], "reason": "verifier probe",
    }


def case(e2_material, e1_material=True, include_e2=True, observation="inconclusive", role="weakening"):
    claim, context, p = raw_record(endpoint="endpoint Delta", intervention="agent Gamma")
    context = context + " " + WEAK
    p["evidence"][0]["material"] = e1_material
    if include_e2:
        p["evidence"].append({"evidence_id": "e2", "source_id": "context", "role": role,
                              "endpoint": "endpoint Delta", "text": WEAK, "exact_reference": WEAK,
                              "value_origin": "source_reported", "material": e2_material})
        prop = p["phase8"]["propositions"][0]
        prop["evidence_bindings"].append({"binding_id": "b2", "proposition_id": "claim:p1",
                                          "evidence_id": "e2", "directness": "direct",
                                          "observation": observation,
                                          "reason": "Second trial did not replicate"})
        d2 = deepcopy(p["phase8"]["evidence_descriptions"][0])
        d2.update(evidence_id="e2", study_id="synthetic-study-2")
        p["phase8"]["evidence_descriptions"].append(d2)
        p["findings"][0]["contrary_evidence_ids"] = ["e2"]
    taxonomy(p)
    return claim, context, p


def run(name, claim, context, p, release=False):
    rec = ForensicRecord.model_validate(p)
    a = assess_forensic_payload(p, original_input=claim, context=context, original_label="solid")
    sym = next(c for c in a["phase7_controls"] if c["name"] == "evidence_symmetry")
    task = Task(id="synthetic-input", title="Abstract comparison", domain="study_forensics",
                difficulty="medium", task_type="study_forensics", prompt=claim, context=context)
    raw = json.dumps({"final_answer": "solid", "confidence": .8, "forensic_record": p})
    root = OUT / name
    shutil.rmtree(root, ignore_errors=True)
    res = run_audit(task, OfflineReviewProvider(raw), output_root=root)
    out = {"case": name, "P8_technical": a["technical_status"], "P8_composite": a.get("composite_state"),
           "P8_assessed_composite": a.get("assessed_composite_state"), "derived_label": a.get("derived_label"),
           "P8_symmetry": (sym["status"], sym.get("eligible_count"), [f["code"] for f in sym.get("findings", [])]),
           "7B_legacy": ab.evaluate_artifact_release(rec).decision_status,
           "P10_status": res.status}
    if res.path:
        d = json.loads((Path(res.path) / "decision.json").read_text())
        c = {x["control_id"]: x for x in d["controls"]}
        s = c["evidence_symmetry"]
        out["P10_symmetry"] = (s["outcome"], s["eligible"], s["reason"])
        out["P10_route"] = json.loads((Path(res.path) / "record.json").read_text()).get(
            "run_record", {}).get("metadata", {}).get("phase9", {}).get("route")
        md = (Path(res.path) / "report.md").read_text()
        out["report_md_contains_e2_quote"] = "did not reduce endpoint Delta" in md
        out["inspect_valid"] = inspect_bundle(Path(res.path)).valid
        if release and res.status == "READY_FOR_RELEASE":
            rel = release_candidate(Path(res.path), output_root=root, reviewer="verifier-probe",
                                    reason="offline verification of gate bypass")
            out["release_status"] = rel.status
            out["release_errors"] = rel.errors
    print(json.dumps(out))


OUT.mkdir(exist_ok=True)
run("W1_e2_material_true", *case(True))
run("W2_e2_material_false", *case(False), release=True)
run("W3_all_material_false", *case(False, e1_material=False), release=True)
run("W0_e2_not_extracted", *case(True, include_e2=False))
run("W4_e2_material_false_no_effect_observed", *case(False, observation="no_effect_observed"))
run("W5_e2_material_false_missing_expected", *case(False, role="missing_expected"))
