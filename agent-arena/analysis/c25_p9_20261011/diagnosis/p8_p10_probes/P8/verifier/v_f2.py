"""Verifier for P8-F2: role/observation consistency is skipped for optional propositions.
Independent rebuild on tests/phase8_case_factory.raw_record. Offline only."""
import json
import sys
from copy import deepcopy
from pathlib import Path

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
OUT = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P8/verifier/out_f2")
sys.path.insert(0, DIAG + "/src")
sys.path.insert(0, DIAG)
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
from agent_arena.output_contract import parse_structured_output  # noqa: E402
from agent_arena.phase8_pipeline import assess_forensic_payload  # noqa: E402
from agent_arena.phase9_review import assess_case, position_from_result  # noqa: E402
from agent_arena.phase9_runtime import OfflineReviewProvider  # noqa: E402
from agent_arena.phase10_bundle import release_candidate, run_audit  # noqa: E402
from agent_arena.schemas import AgentResult, Task  # noqa: E402
from tests.phase8_case_factory import raw_record  # noqa: E402

OPT_TEXT = "optional context statement"


def build(role, observation, materiality="optional", with_client=True, finding_side="contrary"):
    claim, context, rec = raw_record()
    s2 = "Event Q did not fall."
    context2 = context + " " + s2
    rec["evidence"].append({"evidence_id": "e2", "source_id": "context", "role": role, "endpoint": "event Q",
                            "text": s2, "exact_reference": s2, "value_origin": "source_reported"})
    attrs = deepcopy(rec["phase8"]["propositions"][0]["attributes"])
    opt = deepcopy(rec["phase8"]["propositions"][0])
    opt.update(proposition_id="claim:p2", materiality=materiality, proposition_text=OPT_TEXT,
               evidence_bindings=[{"binding_id": "bo", "proposition_id": "claim:p2", "evidence_id": "e2",
                                   "directness": "direct", "observation": observation, "reason": "r"}],
               reported_verdict="supported" if observation == "support" else "contradicted")
    rec["phase8"]["propositions"].append(opt)
    rec["phase8"]["evidence_descriptions"].append({"evidence_id": "e2", "evidence_type": "controlled_intervention",
                                                   "source_role": "primary_study", "attributes": deepcopy(attrs),
                                                   "randomized": True, "study_id": "s2"})
    finding = {"finding_id": "claim:p2", "provenance_id": "origin", "proposition": OPT_TEXT,
               "allowed_summary_strength": "not_assessed"}
    finding["contrary_evidence_ids" if finding_side == "contrary" else "supporting_evidence_ids"] = ["e2"]
    rec["findings"].append(finding)
    if with_client:
        rec["client_findings"].append({"client_finding_id": "client2", "parent_finding_id": "claim:p2",
                                       "display_claim": OPT_TEXT, "provenance_id": "origin",
                                       "referenced_evidence_ids": ["e2"], "client_strength": "not_assessed"})
        rec["phase8"]["transformations"].append({
            "transformation_id": "summary2", "stage": "summary", "target_id": "client2",
            "from_proposition_ids": ["claim:p2"], "from_text": OPT_TEXT, "to_text": OPT_TEXT,
            "from_attributes": deepcopy(attrs), "to_attributes": deepcopy(attrs),
            "asserted_state": opt["reported_verdict"], "asserts_whole_claim": False, "reason": "r"})
    if materiality == "required":
        rec["phase8"]["required_proposition_ids"].append("claim:p2")
        rec["phase8"]["logic"] = {"operator": "or", "children": [rec["phase8"]["logic"],
                                                                {"operator": "leaf", "proposition_id": "claim:p2"}]}
        for stage, ft, tt in (("extraction", claim, OPT_TEXT), ("search_question", OPT_TEXT, opt["search_question"]),
                              ("internal", OPT_TEXT, OPT_TEXT)):
            rec["phase8"]["transformations"].append({
                "transformation_id": stage + "2", "stage": stage, "target_id": "claim:p2",
                "from_proposition_ids": ["claim:p2"], "from_text": ft, "to_text": tt,
                "from_attributes": deepcopy(attrs), "to_attributes": deepcopy(attrs), "asserted_state": None,
                "asserts_whole_claim": False, "reason": "r"})
    rec["phase8_taxonomy"] = {"core_error": "none", "causal_claim": True, "noncausal_result_used": False,
                              "described_biological_mechanism": False, "implies_human_benefit": True,
                              "proposition_ids": ["claim:p1"], "evidence_ids": ["e1"],
                              "trigger_proposition_id": "claim:p1", "trigger_evidence_id": "e1",
                              "trigger_quote": "randomized comparison", "reason": "r"}
    return claim, context2, rec


def run(name, **kw):
    claim, context2, rec = build(**kw)
    a = assess_forensic_payload(rec, original_input=claim, context=context2, original_label="solid")
    print(f"=== {name} {kw}")
    print("  P8:", a["technical_status"], "| composite", a["composite_state"], "| label", a["derived_label"])
    if a["technical_status"] != "completed":
        print("  reasons:", [r for r in a["reasons"] if "role" in r or "Phase 7" in r][:3])
    for p in a.get("propositions", []):
        print("   ", p["proposition_id"], "required", p["required"], "model", p["reported_verdict"], "host",
              p["host_state"], "derived", p["derived_state"], "conflict", p["model_host_conflict"])
    print("  P7 major/critical:", [(c["name"], f["code"]) for c in a["phase7_controls"] for f in c.get("findings", [])
                                   if f.get("severity") in {"critical", "major"}])
    task = Task(id="v-f2-" + name, title="V F2", domain="study_forensics", difficulty="medium",
                task_type="study_forensics", prompt=claim, context=context2)
    raw = json.dumps({"final_answer": "solid", "confidence": 0.5, "forensic_record": rec})
    parsed, d = parse_structured_output(raw)
    pos = position_from_result(task, AgentResult(provider="recorded-offline", model="m", raw_output=raw,
                                                 parsed=parsed, parse_ok=d.ok), "run1")
    routed = assess_case(task, [pos])
    print("  P9:", routed.route, "mandatory", routed.mandatory, [(t.code, t.mandatory) for t in routed.triggers])
    r = run_audit(task, OfflineReviewProvider(raw), output_root=OUT / name / "audit")
    status = r.status
    rel = release_candidate(Path(r.path), output_root=OUT / name / "rel", reviewer="DIAG ONLY",
                            reason="verifier").status if r.path else None
    print("  P10:", status, "| release:", rel)
    if r.path:
        rep = (Path(r.path) / "report.md").read_text()
        idx = rep.find("summary2")
        print("  report mentions client2:", "client2" in rep, "| summary2 asserted_state shown:",
              '"asserted_state"' in rep[idx:idx + 4000] if idx >= 0 else None)


run("C_optional_support_on_contradictory", role="contradictory", observation="support")
run("C_required_same_binding", role="contradictory", observation="support", materiality="required")
run("C_optional_contradiction_on_supporting", role="supporting", observation="contradiction",
    finding_side="contrary")
run("C_required_support_listed_as_contrary", role="supporting", observation="support",
    materiality="required", finding_side="contrary")
