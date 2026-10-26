"""Independent verifier recompute of the frozen 5B artifacts (read-only on the checkout)."""
import sys, json, copy
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B + "/src")
from pathlib import Path
import agent_arena
from agent_arena import condition_contract as cc, full_replication_contract as frc, full_replication_analysis as fra
from agent_arena import phase7a_real_run as rr, phase7a_execution as p7

print("agent_arena origin:", agent_arena.__file__)
root = Path(B)


def jl(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


for prof in (frc.HAIKU, frc.SONNET):
    doc = cc.resolve_registered_plan(prof.plan_id, root)
    spec = doc["specification"]
    arm = cc.resolve_arm(doc, prof.arm_id)
    ns = root / prof.artifact_namespace / prof.model_key
    rawp = ns / "raw" / f"{prof.model_key}_raw_records.jsonl"
    raw = jl(rawp)
    print(f"== {prof.model_key}: spec {spec['specification_fingerprint'][:8]} auth {doc['authorization']['status']} records {len(raw)}")
    print("   distinct record spec fps:", {r.get('specification_fingerprint', '')[:8] for r in raw})
    # self-consistency of each frozen artifact's own fingerprint
    for name, fpkey, fpfun in (
        (f"{prof.model_key}_historical_comparison.json", "comparison_fingerprint", cc._fp),
        (f"{prof.model_key}_usage_cost.json", "usage_cost_fingerprint", cc._fp),
        (f"{prof.model_key}_raw_result_freeze.json", None, None),
        (f"{prof.model_key}_condition_analysis.json", "analysis_artifact_fingerprint", p7._fp),
        ("execution_evidence.json", "execution_evidence_fingerprint", p7._fp),
        ("preflight_evidence.json", "preflight_evidence_fingerprint", p7._fp),
    ):
        v = json.loads((ns / name).read_text())
        if fpkey:
            body = {k: x for k, x in v.items() if k != fpkey}
            print(f"   self-fp {name}: stored==recomputed {fpfun(body) == v[fpkey]}")
    hist_p = root / spec["historical_reference"]["raw_records_path"]
    frozen = json.loads((ns / f"{prof.model_key}_historical_comparison.json").read_text())
    comp = fra.build_comparison(jl(hist_p), raw, document=doc, historical_raw_path=hist_p, prospective_raw_path=rawp)
    print("   comparison fp (checkout paths):", comp["comparison_fingerprint"][:8], "frozen:", frozen["comparison_fingerprint"][:8])
    c2 = copy.deepcopy(comp)
    c2["historical_raw"]["path"] = frozen["historical_raw"]["path"]
    c2["prospective_raw"]["path"] = frozen["prospective_raw"]["path"]
    body = {k: x for k, x in c2.items() if k != "comparison_fingerprint"}
    print("   comparison fp with frozen path strings == frozen:", cc._fp(json.loads(json.dumps(body))) == frozen["comparison_fingerprint"])
    h, p = comp["historical"], comp["prospective"]
    print("   unit-modal acc H/S0 -> 1:", round(h["unit_level_modal_accuracy"]["value"], 4), "->", round(p["unit_level_modal_accuracy"]["value"], 4),
          "| brier:", round(h["calibration"]["brier"]["value"], 4), "->", round(p["calibration"]["brier"]["value"], 4))
    fz = rr.build_condition_raw_freeze(raw, document=doc, arm=arm, model_key=prof.model_key, repo_root=root,
                                       dry_run=False, execution_type=rr.EXEC_TYPE_ADJUDICATION)
    ffz = json.loads((ns / f"{prof.model_key}_raw_result_freeze.json").read_text())
    print("   freeze agg fp recomputed/frozen:", fz["aggregate_result_set_fingerprint"][:8], ffz["aggregate_result_set_fingerprint"][:8],
          "terminal/cls/cal:", fz["terminal_attempts"], fz["classification_valid_calls"], fz["calibration_valid_calls"],
          "| full freeze dict equal:", json.loads(json.dumps(fz)) == ffz)
    if json.loads(json.dumps(fz)) != ffz:
        diff = [k for k in set(fz) | set(ffz) if json.loads(json.dumps(fz.get(k))) != ffz.get(k)]
        print("   freeze differing keys:", diff)
    pr = spec["pricing_contract"]
    uc = fra.build_usage_cost(raw, input_price=pr["input_usd_per_million_tokens"], output_price=pr["output_usd_per_million_tokens"])
    fuc = json.loads((ns / f"{prof.model_key}_usage_cost.json").read_text())
    print("   usage fp recomputed/frozen:", uc["usage_cost_fingerprint"][:8], fuc["usage_cost_fingerprint"][:8], "cost", uc["calculated_cost_usd"], "http", uc["http_attempts"], "retries", uc["transport_retries"])
    lease = frc.validate_one_shot_lease(ns / frc.LEASE_FILENAME, spec["specification_fingerprint"])
    print("   lease:", lease["lease_fingerprint"][:8], "consumed_at", lease["consumed_at"], "commit", lease["repository_commit"][:8], "synthetic", lease["synthetic_test_only"])
    ev = json.loads((ns / "execution_evidence.json").read_text())
    print("   evidence lease fp == lease:", ev["one_shot_lease"]["lease_fingerprint"] == lease["lease_fingerprint"], "batch_abort", ev["batch_abort"], "manual_restarts", ev["manual_restarts"])
    print("   plan authorization.lease_fingerprint:", doc["authorization"].get("lease_fingerprint"), "| consumed spec fp:", doc["authorization"]["consumed_invocation_specification_fingerprint"][:8],
          "| progress:", doc["progress"]["status"], doc["progress"].get("stop_stage"), doc["progress"].get("terminal_attempts"))
