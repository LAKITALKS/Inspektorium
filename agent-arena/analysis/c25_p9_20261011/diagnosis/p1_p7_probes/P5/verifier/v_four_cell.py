"""Recompute the generator-less S1 four-cell artifact from the four frozen raw record sets."""
import sys, json, collections
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B + "/src")
from pathlib import Path
import agent_arena
from agent_arena import condition_contract as cc, full_replication_contract as frc, full_replication_analysis as fra
assert agent_arena.__file__.startswith(B)
root = Path(B)
jl = lambda p: [json.loads(l) for l in (root / p).read_text().splitlines() if l.strip()]
fc = json.loads((root / "analysis/phase5b_sonnet_full_replication/run/sonnet/h1_s1_and_four_cell_analysis.json").read_text())
cells = {}
for prof, hist_key, new_key in ((frc.HAIKU, "H0", "H1"), (frc.SONNET, "S0", "S1")):
    doc = cc.resolve_registered_plan(prof.plan_id, root); spec = doc["specification"]
    b = spec["ordered_unit_bindings"]
    for key, path in ((hist_key, spec["historical_reference"]["raw_records_path"]),
                      (new_key, f"{prof.artifact_namespace}/{prof.model_key}/raw/{prof.model_key}_raw_records.jsonl")):
        s = fra.summarize_records(jl(path), ordered_unit_bindings=b, model_id=prof.model_id, repetitions=5, condition=key)
        cells[key] = (s, {x["unit_id"]: x for x in b})
mism = []
for key, (s, bind) in cells.items():
    exp = fc["four_cell"][key]
    ur = {u["unit_id"]: u for u in s["unit_results"]}
    correct = sum(1 for u in ur.values() if u.get("modal_correct"))
    got = {"unit_modal_n": correct, "brier": s["calibration"]["brier"]["value"], "ece_5bin": s["calibration"]["ece_5bin"]["value"],
           "unanimous": s["stability"]["unanimous_units"]}
    want = {"unit_modal_n": exp["unit_modal"][0], "brier": exp["brier"], "ece_5bin": exp["ece_5bin"], "unanimous": exp["unanimous"]}
    for g in ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"):
        got[g] = [sum(1 for u, x in ur.items() if bind[u]["gold_label"] == g and x.get("modal_correct")), sum(1 for u in ur if bind[u]["gold_label"] == g)]
        want[g] = exp[g]
    for k in want:
        ok = abs(got[k] - want[k]) < 1e-9 if isinstance(want[k], float) else got[k] == want[k]
        if not ok:
            mism.append((key, k, got[k], want[k]))
    print(key, {k: got[k] for k in ("unit_modal_n", "unanimous")}, "brier", round(got["brier"], 6), "ece5", round(got["ece_5bin"], 6))
h1 = {u["unit_id"]: u for u in cells["H1"][0]["unit_results"]}; s1 = {u["unit_id"]: u for u in cells["S1"][0]["unit_results"]}
dis = sorted(u for u in h1 if h1[u].get("modal_label") != s1[u].get("modal_label"))
print("H1/S1 modal disagreements recomputed:", len(dis), "| artifact:", fc["h1_s1_disagreement_count"], "| same unit set:", dis == sorted(x["unit_id"] for x in fc["h1_s1_modal_disagreements"]))
print("mismatches:", mism)
