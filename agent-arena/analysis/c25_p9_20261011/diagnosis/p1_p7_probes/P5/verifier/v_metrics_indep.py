"""Independent (no agent_arena import) recomputation of unit-modal accuracy, Brier and ECE-5 from frozen raw records."""
import json, collections, sys
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base/"
LABELS = {"solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"}
for name, p in (("H0", "analysis/phase7a_execution/haiku/raw/haiku_raw_records.jsonl"),
                ("H1", "analysis/phase5b_haiku_full_replication/run/haiku/raw/haiku_raw_records.jsonl"),
                ("S0", "analysis/phase7a_execution/sonnet/raw/sonnet_raw_records.jsonl"),
                ("S1", "analysis/phase5b_sonnet_full_replication/run/sonnet/raw/sonnet_raw_records.jsonl")):
    rs = [json.loads(l) for l in open(B + p) if l.strip()]
    by = collections.defaultdict(list)
    for r in rs:
        by[r["unit_id"]].append(r)
    correct = 0
    for u, lst in by.items():
        c = collections.Counter(r["label"] for r in lst if r.get("label") in LABELS)
        top = c.most_common()
        if top and (len(top) == 1 or top[0][1] > top[1][1]) and top[0][0] == lst[0]["gold_label"]:
            correct += 1
    cal = [(float(r["confidence"]), r["label"] == r["gold_label"]) for r in rs
           if r.get("label") in LABELS and isinstance(r.get("confidence"), (int, float)) and 0 <= r["confidence"] <= 1]
    brier = sum((c - ok) ** 2 for c, ok in cal) / len(cal)
    bins = collections.defaultdict(list)
    for c, ok in cal:
        bins[min(int(c * 5), 4)].append((c, ok))
    ece = sum(len(v) / len(cal) * abs(sum(c for c, _ in v) / len(v) - sum(ok for _, ok in v) / len(v)) for v in bins.values())
    print(f"{name}: units {len(by)} modal-correct {correct}/84 = {correct/84:.4f} | brier {brier:.6f} | ece5 {ece:.6f} | n_cal {len(cal)}")
