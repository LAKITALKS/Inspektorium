"""Verifier for P8-F1: can a bounded (non-material) model/host conflict alone decide the released
derived taxonomy label? Independent fixtures: CvC (both conflict directions) and ME. Offline only."""
import json
import sys
from copy import deepcopy
from pathlib import Path

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P8/verifier/out_f1")
sys.path.insert(0, DIAG + "/src")
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
from agent_arena.output_contract import parse_structured_output  # noqa: E402
from agent_arena.phase9_review import assess_case, position_from_result  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.phase10_bundle import inspect_bundle, release_candidate, run_audit  # noqa: E402
from agent_arena.schemas import AgentResult, Task  # noqa: E402

CLAIM = "intervention X reduces event Q in adults."
S1 = "A randomized comparison in adults (human) found that intervention X reduced event Q versus placebo at 12 weeks."
S2 = "In an observational cohort of adults, intervention X use was associated with lower event Q."
S2M = "In mice, intervention X activated pathway M that lowers event Q."
S3 = "Event Q rose in adults given intervention X."
ATTRS = {"species": "human", "population": "adults", "intervention": "intervention X",
         "comparator": "placebo", "endpoint": "event Q", "endpoint_type": "clinical_event",
         "relation": "causal", "follow_up": "12 weeks", "certainty": "asserted", "comparison": "between"}
DESC = dict(ATTRS, relation="description")


def ev(eid, role, text):
    return {"evidence_id": eid, "source_id": "context", "role": role, "endpoint": "event Q",
            "text": text, "exact_reference": text, "value_origin": "source_reported"}


def build(kind, p1_model, with_rct=True):
    """kind: 'cvc' (observational trigger e2) or 'me' (animal mechanism trigger e2)."""
    trig_text = S2 if kind == "cvc" else S2M
    bindings = []
    if with_rct:
        bindings.append({"binding_id": "b1", "proposition_id": "claim:p1", "evidence_id": "e1",
                         "directness": "direct", "observation": "support", "reason": "trial"})
    bindings.append({"binding_id": "b2", "proposition_id": "claim:p1", "evidence_id": "e2",
                     "directness": "direct", "observation": "support", "reason": "trigger"})
    p1 = {"proposition_id": "claim:p1", "parent_claim_id": "claim", "proposition_text": CLAIM,
          "original_span": {"start": 0, "end": len(CLAIM), "text": CLAIM}, "materiality": "required",
          "attributes": deepcopy(ATTRS), "material_dimensions": list(ATTRS), "evidence_bindings": bindings,
          "reported_verdict": p1_model, "reason": "model judgment", "provenance_id": "origin",
          "search_question": "q1", "search_scope_ids": ["review"]}
    p2_text = "event Q falls in adults given intervention X"
    p2 = {"proposition_id": "claim:p2", "parent_claim_id": "claim", "proposition_text": p2_text,
          "original_span": {"start": 0, "end": len(CLAIM), "text": CLAIM}, "materiality": "required",
          "attributes": deepcopy(DESC), "material_dimensions": list(DESC),
          "evidence_bindings": [{"binding_id": "b3", "proposition_id": "claim:p2", "evidence_id": "e3",
                                 "directness": "direct", "observation": "contradiction", "reason": "rose"}],
          "reported_verdict": "contradicted", "reason": "model judgment", "provenance_id": "origin",
          "search_question": "q2", "search_scope_ids": ["review"]}
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
                  "asserted_state": "contradicted", "asserts_whole_claim": True, "reason": "whole claim"})
    descs = [{"evidence_id": "e2", "source_role": "primary_study", "study_id": "s2",
              **({"evidence_type": "observational", "attributes": dict(ATTRS, relation="association")}
                 if kind == "cvc" else
                 {"evidence_type": "animal", "attributes": dict(ATTRS, relation="mechanism")})},
             {"evidence_id": "e3", "evidence_type": "descriptive", "source_role": "primary_study",
              "attributes": deepcopy(DESC), "study_id": "s3"}]
    evidence = [ev("e2", "supporting", trig_text), ev("e3", "contradictory", S3)]
    supp = ["e2"]
    if with_rct:
        descs.insert(0, {"evidence_id": "e1", "evidence_type": "controlled_intervention",
                         "source_role": "primary_study", "attributes": deepcopy(ATTRS), "randomized": True,
                         "study_id": "s1"})
        evidence.insert(0, ev("e1", "supporting", S1))
        supp = ["e1", "e2"]
    record = {
        "record_id": "vf1", "synthetic_fixture": True,
        "provenance": [{"provenance_id": "origin", "exact_claim_text": CLAIM, "source_id": "input"}],
        "evidence": evidence,
        "findings": [{"finding_id": "claim:p1", "provenance_id": "origin", "proposition": CLAIM,
                      "supporting_evidence_ids": supp, "allowed_summary_strength": "not_assessed"},
                     {"finding_id": "claim:p2", "provenance_id": "origin", "proposition": p2_text,
                      "contrary_evidence_ids": ["e3"], "allowed_summary_strength": "not_assessed"}],
        "client_findings": [{"client_finding_id": "client1", "parent_finding_id": "claim:p1",
                             "display_claim": CLAIM, "provenance_id": "origin",
                             "referenced_evidence_ids": [supp[0]], "client_strength": "not_assessed"}],
        "search_scopes": [{"search_scope_id": "review", "scope_type": "reviewed_set",
                           "reviewed_source_ids": ["input", "context"]}],
        "phase8": {"claim_id": "claim", "provenance_id": "origin", "original_claim": CLAIM,
                   "required_proposition_ids": ["claim:p1", "claim:p2"], "propositions": [p1, p2],
                   "logic": {"operator": "and", "children": [{"operator": "leaf", "proposition_id": "claim:p1"},
                                                             {"operator": "leaf", "proposition_id": "claim:p2"}]},
                   "extraction_provenance": "verifier", "evidence_descriptions": descs, "transformations": trans},
        "phase8_taxonomy": (
            {"core_error": "causal_inference", "causal_claim": True, "noncausal_result_used": True,
             "described_biological_mechanism": False, "implies_human_benefit": False,
             "proposition_ids": ["claim:p1"], "evidence_ids": ["e2"], "trigger_proposition_id": "claim:p1",
             "trigger_evidence_id": "e2", "trigger_quote": "associated with lower event Q", "reason": "cvc"}
            if kind == "cvc" else
            {"core_error": "mechanism_to_outcome", "causal_claim": True, "noncausal_result_used": False,
             "described_biological_mechanism": True, "implies_human_benefit": True,
             "proposition_ids": ["claim:p1"], "evidence_ids": ["e2"], "trigger_proposition_id": "claim:p1",
             "trigger_evidence_id": "e2", "trigger_quote": "activated pathway M", "reason": "me"}),
    }
    label = "correlation_vs_causation" if kind == "cvc" else "mechanism_vs_evidence"
    return {"final_answer": label, "confidence": 0.7, "steps": ["x"], "forensic_record": record}


CONTEXT = " ".join([S1, S2, S2M, S3])
TASK = Task(id="v-f1", title="V F1", domain="study_forensics", difficulty="medium",
            task_type="study_forensics", prompt=CLAIM, context=CONTEXT)

CASES = [("cvc", "unsupported", True), ("cvc", "supported", True),
         ("cvc_reverse", "supported", False), ("cvc_reverse", "unsupported", False),
         ("me", "unsupported", True), ("me", "supported", True)]
for name, model, rct in CASES:
    kind = "me" if name == "me" else "cvc"
    raw = json.dumps(build(kind, model, rct))
    parsed, d = parse_structured_output(raw)
    res = AgentResult(provider="recorded-offline", model="offline-fixture", raw_output=raw, parsed=parsed,
                      parse_ok=d.ok)
    pos = position_from_result(TASK, res, "run1")
    a = pos.phase8
    print(f"=== {name} model_p1={model}")
    print("  P8:", a["technical_status"], "| composite", a["composite_state"], "| model/host composite",
          a["model_composite_state"], a["host_composite_state"])
    for p in a["propositions"]:
        print("   ", p["proposition_id"], "model", p["reported_verdict"], "host", p["host_state"],
              "derived", p["derived_state"], "conflict", p["model_host_conflict"])
    print("  derived_label:", a["derived_label"], "|", a["taxonomy"]["reasons"])
    routed = assess_case(TASK, [pos])
    print("  P9:", routed.route, "mandatory", routed.mandatory,
          [(t.code, t.mandatory, t.reason[-62:]) for t in routed.triggers])
    out = OUT / f"{name}_{model}"
    r = run_audit(TASK, OfflineReviewProvider(raw), output_root=out / "audit")
    b = Path(r.path)
    rel = release_candidate(b, output_root=out / "rel", reviewer="DIAG ONLY", reason="verifier probe")
    print("  P10:", r.status, "valid", inspect_bundle(b).valid, "| release:", rel.status)
    rep = (b / "report.md").read_text()
    for line in rep.splitlines():
        low = line.lower()
        if ("derived taxonomy" in low or "model/host conflicts" in low) and len(line) < 300:
            print("    report:", line.strip())
