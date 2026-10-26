"""P8 probe A: a non-material model/host conflict that alone decides the derived taxonomy label.

Offline only: OfflineReviewProvider + run_audit into a scratch output root. No network.
"""
import json
import sys
from copy import deepcopy
from pathlib import Path

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P8/out_probeA")
sys.path.insert(0, DIAG + "/src")
sys.path.insert(0, DIAG)

import agent_arena
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__

from agent_arena.output_contract import parse_structured_output
from agent_arena.phase9_review import assess_case, position_from_result
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.phase10_bundle import inspect_bundle, release_candidate, run_audit
from agent_arena.schemas import AgentResult, Task

CLAIM = "intervention X reduces event Q in adults."
S1 = "A randomized comparison in adults (human) found that intervention X reduced event Q versus placebo at 12 weeks."
S2 = "In an observational cohort of adults, intervention X use was associated with lower event Q."
S3 = "Event Q rose in adults given intervention X."
CONTEXT = " ".join([S1, S2, S3])

ATTRS = {"species": "human", "population": "adults", "intervention": "intervention X",
         "comparator": "placebo", "endpoint": "event Q", "endpoint_type": "clinical_event",
         "relation": "causal", "follow_up": "12 weeks", "certainty": "asserted", "comparison": "between"}
DESC_ATTRS = dict(ATTRS, relation="description")


def build(p1_model="unsupported"):
    p1 = {
        "proposition_id": "claim:p1", "parent_claim_id": "claim", "proposition_text": CLAIM,
        "original_span": {"start": 0, "end": len(CLAIM), "text": CLAIM}, "materiality": "required",
        "attributes": deepcopy(ATTRS), "material_dimensions": list(ATTRS),
        "evidence_bindings": [
            {"binding_id": "b1", "proposition_id": "claim:p1", "evidence_id": "e1", "directness": "direct",
             "observation": "support", "reason": "trial"},
            {"binding_id": "b2", "proposition_id": "claim:p1", "evidence_id": "e2", "directness": "direct",
             "observation": "support", "reason": "cohort"}],
        "reported_verdict": p1_model, "reason": "model judgment", "provenance_id": "origin",
        "search_question": "q1", "search_scope_ids": ["review"],
    }
    p2_text = "event Q falls in adults given intervention X"
    p2 = {
        "proposition_id": "claim:p2", "parent_claim_id": "claim", "proposition_text": p2_text,
        "original_span": {"start": 0, "end": len(CLAIM), "text": CLAIM}, "materiality": "required",
        "attributes": deepcopy(DESC_ATTRS), "material_dimensions": list(DESC_ATTRS),
        "evidence_bindings": [
            {"binding_id": "b3", "proposition_id": "claim:p2", "evidence_id": "e3", "directness": "direct",
             "observation": "contradiction", "reason": "rose"}],
        "reported_verdict": "contradicted", "reason": "model judgment", "provenance_id": "origin",
        "search_question": "q2", "search_scope_ids": ["review"],
    }
    model_states = {"claim:p1": p1_model, "claim:p2": "contradicted"}
    composite = "contradicted"  # AND(x, contradicted)
    trans = []
    for p in (p1, p2):
        pid, a = p["proposition_id"], p["attributes"]
        for stage, ft, tt in (("extraction", CLAIM, p["proposition_text"]),
                              ("search_question", p["proposition_text"], p["search_question"]),
                              ("internal", p["proposition_text"], p["proposition_text"])):
            trans.append({"transformation_id": f"{stage}-{pid}", "stage": stage, "target_id": pid,
                          "from_proposition_ids": [pid], "from_text": ft, "to_text": tt,
                          "from_attributes": deepcopy(a), "to_attributes": deepcopy(a),
                          "asserted_state": None, "asserts_whole_claim": False, "reason": "same"})
    trans.append({"transformation_id": "summary", "stage": "summary", "target_id": "client1",
                  "from_proposition_ids": ["claim:p1"], "from_text": CLAIM, "to_text": CLAIM,
                  "from_attributes": deepcopy(ATTRS), "to_attributes": deepcopy(ATTRS),
                  "asserted_state": composite, "asserts_whole_claim": True, "reason": "whole claim"})
    ev = lambda eid, role, text: {"evidence_id": eid, "source_id": "context", "role": role, "endpoint": "event Q",
                                  "text": text, "exact_reference": text, "value_origin": "source_reported"}
    record = {
        "record_id": "probeA", "synthetic_fixture": True,
        "provenance": [{"provenance_id": "origin", "exact_claim_text": CLAIM, "source_id": "input"}],
        "evidence": [ev("e1", "supporting", S1), ev("e2", "supporting", S2), ev("e3", "contradictory", S3)],
        "findings": [
            {"finding_id": "claim:p1", "provenance_id": "origin", "proposition": CLAIM,
             "supporting_evidence_ids": ["e1", "e2"], "allowed_summary_strength": "not_assessed"},
            {"finding_id": "claim:p2", "provenance_id": "origin", "proposition": p2_text,
             "contrary_evidence_ids": ["e3"], "allowed_summary_strength": "not_assessed"}],
        "client_findings": [{"client_finding_id": "client1", "parent_finding_id": "claim:p1",
                             "display_claim": CLAIM, "provenance_id": "origin",
                             "referenced_evidence_ids": ["e1"], "client_strength": "not_assessed"}],
        "search_scopes": [{"search_scope_id": "review", "scope_type": "reviewed_set",
                           "reviewed_source_ids": ["input", "context"]}],
        "phase8": {
            "claim_id": "claim", "provenance_id": "origin", "original_claim": CLAIM,
            "required_proposition_ids": ["claim:p1", "claim:p2"], "propositions": [p1, p2],
            "logic": {"operator": "and", "children": [{"operator": "leaf", "proposition_id": "claim:p1"},
                                                      {"operator": "leaf", "proposition_id": "claim:p2"}]},
            "extraction_provenance": "probe",
            "evidence_descriptions": [
                {"evidence_id": "e1", "evidence_type": "controlled_intervention", "source_role": "primary_study",
                 "attributes": deepcopy(ATTRS), "randomized": True, "study_id": "s1"},
                {"evidence_id": "e2", "evidence_type": "observational", "source_role": "primary_study",
                 "attributes": dict(ATTRS, relation="association"), "study_id": "s2"},
                {"evidence_id": "e3", "evidence_type": "descriptive", "source_role": "primary_study",
                 "attributes": deepcopy(DESC_ATTRS), "study_id": "s3"}],
            "transformations": trans,
        },
        "phase8_taxonomy": {
            "core_error": "causal_inference", "causal_claim": True, "noncausal_result_used": True,
            "described_biological_mechanism": False, "implies_human_benefit": False,
            "proposition_ids": ["claim:p1"], "evidence_ids": ["e2"], "trigger_proposition_id": "claim:p1",
            "trigger_evidence_id": "e2", "trigger_quote": "associated with lower event Q", "reason": "cvc"},
    }
    return {"final_answer": "correlation_vs_causation", "confidence": 0.7, "steps": ["x"],
            "forensic_record": record}


TASK = Task(id="probe-a", title="Probe A", domain="study_forensics", difficulty="medium",
            task_type="study_forensics", prompt=CLAIM, context=CONTEXT)

for model in ("unsupported", "supported"):
    raw = json.dumps(build(model))
    parsed, diag = parse_structured_output(raw)
    res = AgentResult(provider="recorded-offline", model="offline-fixture", raw_output=raw, parsed=parsed,
                      parse_ok=diag.ok)
    pos = position_from_result(TASK, res, "run1")
    a = pos.phase8
    print(f"=== P1 model={model}")
    print(" technical_status:", a["technical_status"], "| composite:", a["composite_state"],
          "| model/host composite:", a["model_composite_state"], a["host_composite_state"])
    for p in a["propositions"]:
        print("  ", p["proposition_id"], "model", p["reported_verdict"], "host", p["host_state"],
              "derived", p["derived_state"], "conflict", p["model_host_conflict"])
    print(" conflicts:", [(c["scope"], c.get("proposition_id")) for c in a["model_host_conflicts"]])
    print(" derived_label:", a["derived_label"], "| taxonomy:", a["taxonomy"]["reasons"])
    routed = assess_case(TASK, [pos])
    print(" P9 route:", routed.route, "mandatory:", routed.mandatory)
    for t in routed.triggers:
        print("   trigger", t.code, "mandatory", t.mandatory, "|", t.reason[:110])
    out = OUT / model
    r = run_audit(TASK, OfflineReviewProvider(raw), output_root=out / "audit")
    print(" P10 run_audit status:", r.status, r.errors)
    b = Path(r.path)
    print(" bundle valid:", inspect_bundle(b).valid)
    rel = release_candidate(b, output_root=out / "released", reviewer="DIAG ONLY", reason="probe")
    print(" release:", rel.status)
    rep = (b / "report.md").read_text()
    for line in rep.splitlines():
        if "derived" in line.lower() and ("taxonom" in line.lower() or "classification" in line.lower()):
            print("  report:", line.strip()[:200])
