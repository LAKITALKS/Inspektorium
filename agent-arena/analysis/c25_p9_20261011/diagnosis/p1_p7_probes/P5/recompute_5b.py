import sys, json
B="__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B+"/src")
from pathlib import Path
from agent_arena import condition_contract as cc, full_replication_contract as frc, full_replication_analysis as fra
from agent_arena import phase7a_real_run as rr
import agent_arena; print("origin", agent_arena.__file__)
root=Path(B)
def load(p): return [json.loads(l) for l in (root/p).read_text().splitlines() if l.strip()]
def strip(d, keys=("path",)):
    if isinstance(d, dict): return {k: strip(v) for k,v in d.items() if k not in ("path","comparison_fingerprint","freeze_timestamp","repository_commit")}
    if isinstance(d, list): return [strip(x) for x in d]
    return d
for prof in (frc.HAIKU, frc.SONNET):
    doc = cc.resolve_registered_plan(prof.plan_id, root)
    spec = doc["specification"]; arm = cc.resolve_arm(doc, prof.arm_id)
    ns = Path(prof.artifact_namespace)/prof.model_key
    raw = load(ns/"raw"/f"{prof.model_key}_raw_records.jsonl")
    print("==", prof.model_key, "records", len(raw), "spec", spec["specification_fingerprint"][:12],
          "records' spec fps", {r.get("specification_fingerprint","")[:12] for r in raw})
    hist_p = spec["historical_reference"]["raw_records_path"]
    hist = load(hist_p)
    comp = fra.build_comparison(hist, raw, document=doc, historical_raw_path=root/hist_p, prospective_raw_path=root/ns/"raw"/f"{prof.model_key}_raw_records.jsonl")
    frozen = json.loads((root/ns/f"{prof.model_key}_historical_comparison.json").read_text())
    print(" comparison fingerprint recomputed", comp["comparison_fingerprint"][:12], "frozen", frozen["comparison_fingerprint"][:12], "equal_excluding_paths", strip(comp)==strip(frozen))
    p=comp["prospective"]; h=comp["historical"]
    print(" H/P unit modal acc", h["unit_level_modal_accuracy"]["value"], p["unit_level_modal_accuracy"]["value"], "brier", h["calibration"]["brier"]["value"], p["calibration"]["brier"]["value"])
    freeze = rr.build_condition_raw_freeze(raw, document=doc, arm=arm, model_key=prof.model_key, repo_root=root, dry_run=False, execution_type=rr.EXEC_TYPE_ADJUDICATION)
    ffz = json.loads((root/ns/f"{prof.model_key}_raw_result_freeze.json").read_text())
    print(" freeze aggregate fp recomputed", freeze["aggregate_result_set_fingerprint"][:12], "frozen", ffz["aggregate_result_set_fingerprint"][:12],
          "terminal", freeze["terminal_attempts"], ffz["terminal_attempts"], "cls", freeze["classification_valid_calls"], "cal", freeze["calibration_valid_calls"])
    pr = spec["pricing_contract"]
    uc = fra.build_usage_cost(raw, input_price=pr["input_usd_per_million_tokens"], output_price=pr["output_usd_per_million_tokens"])
    fuc = json.loads((root/ns/f"{prof.model_key}_usage_cost.json").read_text())
    print(" usage fp", uc["usage_cost_fingerprint"][:12], fuc["usage_cost_fingerprint"][:12], "cost", uc.get("calculated_cost_usd"), fuc.get("calculated_cost_usd"), "http", uc.get("http_attempts"))
    ana = json.loads((root/ns/f"{prof.model_key}_condition_analysis.json").read_text())
    print(" analysis bound freeze fp == freeze", ana["bound_raw_freeze_fingerprint"]==ffz["aggregate_result_set_fingerprint"], "analysis.report == recomputed prospective (excl paths)", strip(ana["report"])==strip(p))
    ev = json.loads((root/ns/"execution_evidence.json").read_text())
    print(" evidence comparison fp == frozen", ev["comparison_fingerprint"]==frozen["comparison_fingerprint"], "evidence usage fp == frozen", ev["usage_cost_fingerprint"]==fuc["usage_cost_fingerprint"])
    lease = frc.validate_one_shot_lease(root/ns/frc.LEASE_FILENAME, spec["specification_fingerprint"])
    print(" lease valid; lease fp", lease["lease_fingerprint"][:12], "plan authorization.lease_fingerprint", doc["authorization"].get("lease_fingerprint"), "progress", doc["progress"]["status"], doc["progress"].get("completed_calls"))
