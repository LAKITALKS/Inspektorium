"""Extra offline variants (OfflineReviewProvider only, no network).

R1: non-replicating trial e2 relabelled role=supporting (material=True), binding inconclusive,
    listed in supporting_evidence_ids, client drops it.
W6: W1 (e2 weakening, material=True) but the client keeps e2.
VX: e1 value_origin=source_reported with reported_value '97%' that does not occur in its
    exact_reference/text, plus a client value_claim claiming source_reported.
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
from agent_arena.phase10_bundle import run_audit  # noqa: E402
from agent_arena.phase8_pipeline import assess_forensic_payload  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.schemas import Task  # noqa: E402
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


def with_e2(role, material, in_supporting, client_keeps):
    claim, context, p = raw_record(endpoint="endpoint Delta", intervention="agent Gamma")
    context = context + " " + WEAK
    p["evidence"].append({"evidence_id": "e2", "source_id": "context", "role": role,
                          "endpoint": "endpoint Delta", "text": WEAK, "exact_reference": WEAK,
                          "value_origin": "source_reported", "material": material})
    prop = p["phase8"]["propositions"][0]
    prop["evidence_bindings"].append({"binding_id": "b2", "proposition_id": "claim:p1",
                                      "evidence_id": "e2", "directness": "direct",
                                      "observation": "inconclusive",
                                      "reason": "Second trial did not replicate"})
    d2 = deepcopy(p["phase8"]["evidence_descriptions"][0])
    d2.update(evidence_id="e2", study_id="synthetic-study-2")
    p["phase8"]["evidence_descriptions"].append(d2)
    if in_supporting:
        p["findings"][0]["supporting_evidence_ids"].append("e2")
    else:
        p["findings"][0]["contrary_evidence_ids"] = ["e2"]
    if client_keeps:
        p["client_findings"][0]["referenced_evidence_ids"].append("e2")
    taxonomy(p)
    return claim, context, p


def value_not_in_span():
    claim, context, p = raw_record(endpoint="endpoint Delta", intervention="agent Gamma")
    p["evidence"][0]["reported_value"] = "97%"
    p["client_findings"][0]["value_claims"] = [{"evidence_id": "e1", "claimed_origin": "source_reported"}]
    assert "97" not in p["evidence"][0]["exact_reference"] and "97" not in context
    taxonomy(p)
    return claim, context, p


def run(name, claim, context, p):
    a = assess_forensic_payload(p, original_input=claim, context=context, original_label="solid")
    task = Task(id="synthetic-input", title="Abstract comparison", domain="study_forensics",
                difficulty="medium", task_type="study_forensics", prompt=claim, context=context)
    raw = json.dumps({"final_answer": "solid", "confidence": .8, "forensic_record": p})
    root = OUT / name
    shutil.rmtree(root, ignore_errors=True)
    res = run_audit(task, OfflineReviewProvider(raw), output_root=root)
    gates = {}
    if res.path:
        d = json.loads((Path(res.path) / "decision.json").read_text())
        gates = {x["control_id"]: (x["outcome"], x["eligible"]) for x in d["controls"]
                 if x["control_id"] in {"evidence_symmetry", "value_origin_provenance"}}
    print(json.dumps({"case": name, "P8": [a["technical_status"], a.get("composite_state"),
                                           a.get("derived_label")],
                      "P8_reasons_tail": a.get("reasons", [])[-1:], "P10": res.status, "gates": gates}))


OUT.mkdir(exist_ok=True)
run("R1_role_supporting_inconclusive_dropped", *with_e2("supporting", True, True, False))
run("W6_weakening_material_client_keeps", *with_e2("weakening", True, False, True))
run("VX_source_reported_value_not_in_span", *value_not_in_span())
