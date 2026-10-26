"""5A diagnostics internal consistency: per-case detected runs -> per-run accuracy, majority, confusion matrix."""
import csv, collections, json
D = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base/analysis/phase5a/lib_20260704_134553_55aa66/"
rows = list(csv.DictReader(open(D + "case_diagnostics.csv")))
runs = [(r["gold"], d) for r in rows for d in r["detected_runs"].split("|")]
correct = sum(g == d for g, d in runs)
maj = sum(r["majority_correct"] == "True" for r in rows)
cm = collections.Counter(runs)
fcm = {r["gold\\detected"]: {k: int(v) for k, v in r.items() if k not in ("gold\\detected", "row_total")} for r in csv.DictReader(open(D + "confusion_matrix.csv"))}
mism = [(g, d, cm[(g, d)], fcm[g][d]) for g in fcm for d in fcm[g] if cm[(g, d)] != fcm[g][d]]
s = json.load(open(D + "phase5a_summary.json"))
print("cases", len(rows), "runs", len(runs), "per-run correct", correct, "majority correct", maj, "| confusion mismatches", mism)
print("summary keys:", sorted(s)[:12])
