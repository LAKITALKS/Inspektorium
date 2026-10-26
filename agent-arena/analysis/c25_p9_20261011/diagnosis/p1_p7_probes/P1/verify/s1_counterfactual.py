"""Verifier: does the F1 first-object selection change any published S1 number?

Recomputes the S1 condition summary with the frozen analysis code (read-only) for
(a) the records as stored, (b) the two self-corrected records excluded as ambiguous,
(c) the two records relabelled to the model's own final (corrected) object.
"""
import sys, json, copy
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src"]
import agent_arena
assert agent_arena.__file__.startswith(B), agent_arena.__file__
from agent_arena.full_replication_analysis import summarize_records

S = B + "/analysis/phase5b_sonnet_full_replication/run/sonnet/"
records = [json.loads(l) for l in open(S + "raw/sonnet_raw_records.jsonl")]
frozen = json.load(open(S + "sonnet_condition_analysis.json"))
rep = frozen["report"]
bindings = [{k: u[k] for k in ("unit_id", "unit_type", "family_id", "gold_label")} for u in rep["unit_results"]]
model = records[0]["model"]
cond = rep.get("condition")


def summ(recs):
    s = summarize_records(recs, ordered_unit_bindings=bindings, model_id=model,
                          repetitions=5, condition=cond)
    return {
        "unit_modal": (s["unit_level_modal_accuracy"]["numerator"], s["unit_level_modal_accuracy"]["value"]),
        "response": (s["response_level_accuracy"]["numerator"], s["response_level_accuracy"]["classification_valid_denominator"],
                     round(s["response_level_accuracy"]["value"], 4)),
        "brier": round(s["calibration"]["brier"]["value"], 5),
        "ece5": round(s["calibration"]["ece_5bin"]["value"], 5),
        "mean_conf": round(s["calibration"]["confidence_distribution"]["mean"], 4),
        "stability": s["stability"],
    }


print("FROZEN report stability:", rep["stability"], "unit_modal", rep["unit_level_modal_accuracy"]["numerator"],
      "brier", rep["calibration"]["brier"]["value"])
print("RECOMPUTED as stored:", summ(records))

targets = {("P7A-BND-018", 3): 0.85, ("P7A-PRT-08-P2", 4): 0.92}
excl = copy.deepcopy(records)
corr = copy.deepcopy(records)
for recs, mode in ((excl, "exclude"), (corr, "correct")):
    for r in recs:
        key = (r["case_id"], r["run_index"])
        if key in targets:
            if mode == "exclude":
                r["parse_ok"] = False  # treated as ambiguous/invalid
            else:
                r["label"] = "overclaim"; r["label_correct"] = True; r["confidence"] = targets[key]
print("EXCLUDE ambiguous:", summ(excl))
print("USE corrected obj:", summ(corr))
