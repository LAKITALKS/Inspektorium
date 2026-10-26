"""P7 probe: evidence-direction drop and unresolved value origin through the current
offline audit path (run_agent -> Phase8 assess -> _phase7_controls -> Phase10 evaluate).
No network: OfflineReviewProvider only."""
import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [BASE + "/src", BASE]
OUT = Path(__file__).parent / "out"

from agent_arena import artifact_binding as ab  # noqa: E402
from agent_arena.phase10_bundle import run_audit  # noqa: E402
from agent_arena.phase8_pipeline import assess_forensic_payload  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.schemas import ForensicRecord  # noqa: E402
from tests.phase8_case_factory import raw_record  # noqa: E402
from tests.test_phase8_pipeline import task_for  # noqa: E402

assert ab.__file__.startswith(BASE), ab.__file__

CONTRA = ("A second randomized comparison in adults found that agent Gamma did not "
          "reduce endpoint Delta versus placebo at 12 weeks.")


def taxonomy(payload, core="unknown"):
    payload["phase8_taxonomy"] = {
        "core_error": core, "causal_claim": True, "noncausal_result_used": False,
        "described_biological_mechanism": False, "implies_human_benefit": True,
        "proposition_ids": ["claim:p1"], "evidence_ids": ["e1"],
        "trigger_proposition_id": "claim:p1", "trigger_evidence_id": "e1",
        "trigger_quote": payload["evidence"][0]["text"], "reason": "probe",
    }


def mixed(material_contra=True, client_keeps_contra=False, verdict="unknown"):
    claim, context, p = raw_record(endpoint="endpoint Delta", intervention="agent Gamma")
    context = context + " " + CONTRA
    e2 = {"evidence_id": "e2", "source_id": "context", "role": "contradictory",
          "endpoint": "endpoint Delta", "text": CONTRA, "exact_reference": CONTRA,
          "value_origin": "source_reported", "material": material_contra}
    p["evidence"].append(e2)
    prop = p["phase8"]["propositions"][0]
    prop["evidence_bindings"].append({
        "binding_id": "b2", "proposition_id": "claim:p1", "evidence_id": "e2",
        "directness": "direct", "observation": "contradiction", "reason": "Null trial"})
    d2 = deepcopy(p["phase8"]["evidence_descriptions"][0])
    d2.update(evidence_id="e2", study_id="synthetic-study-2")
    p["phase8"]["evidence_descriptions"].append(d2)
    p["findings"][0]["contrary_evidence_ids"] = ["e2"]
    if client_keeps_contra:
        p["client_findings"][0]["referenced_evidence_ids"].append("e2")
    prop["reported_verdict"] = verdict
    if verdict == "unknown":
        prop["uncertainty"] = ["Conflicting trials"]
    p["phase8"]["transformations"][-1]["asserted_state"] = verdict
    taxonomy(p)
    return claim, context, p


def origin_case(value_origin, reported_value):
    claim, context, p = raw_record(endpoint="endpoint Delta", intervention="agent Gamma")
    p["evidence"][0]["value_origin"] = value_origin
    if reported_value is not None:
        p["evidence"][0]["reported_value"] = reported_value
    taxonomy(p, core="none")
    return claim, context, p


def summarize(name, claim, context, p):
    rec = ForensicRecord.model_validate(p)
    rr = ab.evaluate_artifact_release(rec)
    a = assess_forensic_payload(p, original_input=claim, context=context, original_label="solid")
    ctrls = {c["name"]: (c["status"], c.get("eligible_count"), [f["code"] for f in c.get("findings", [])])
             for c in a["phase7_controls"]}
    task = task_for(claim, context)
    raw = json.dumps({"final_answer": "solid", "confidence": .8, "forensic_record": p})
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        res = run_audit(task, OfflineReviewProvider(raw), output_root=Path(tmp))
        status = res.status
        p10 = None
        if res.path:
            c = json.loads((Path(res.path) / "decision.json").read_text())
            p10 = {x["control_id"]: (x["outcome"], x["eligible"], [f.get("code") for f in x["findings"]])
                   for x in c["controls"]
                   if x["control_id"] in {s.gate_id for s in ab.MANDATORY_PHASE7B_GATE_SPECS}
                   or x["control_id"] in {"analysis_source", "phase8_semantics_taxonomy"}}
    print(f"== {name}")
    print("  7B release:", rr.decision_status, rr.blocking_codes)
    print("  P8 tech/composite:", a["technical_status"], a.get("composite_state"), "derived:", a.get("derived_label"))
    print("  P8 phase7_controls:", ctrls)
    print("  P8 reasons:", [r for r in a.get("reasons", [])][:4])
    print("  P10 status:", status, "| gate outcomes:", p10)


OUT.mkdir(exist_ok=True)
summarize("M1 mixed, contra material, client drops contra", *mixed(True, False))
summarize("M2 mixed, contra NOT material, client drops contra", *mixed(False, False))
summarize("M3 mixed, contra NOT material, client keeps contra", *mixed(False, True))
summarize("M4 mixed, contra material, client keeps contra", *mixed(True, True))
summarize("M5 mixed, contra NOT material, client drops contra, verdict supported, core none", *(lambda c: (taxonomy(c[2], "none"), c)[1])(mixed(False, False, "supported")))
summarize("M6 same as M5 but contra material", *(lambda c: (taxonomy(c[2], "none"), c)[1])(mixed(True, False, "supported")))
summarize("V1 origin None + reported_value", *origin_case(None, "0.42"))
summarize("V2 origin None, no reported_value", *origin_case(None, None))
summarize("V0 baseline source_reported", *origin_case("source_reported", None))
