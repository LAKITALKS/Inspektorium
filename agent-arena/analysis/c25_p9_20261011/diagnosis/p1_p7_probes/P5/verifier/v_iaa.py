"""Gap probe for 5.05c proxy IAA: input-sheet hash binding + recompute headline kappas from tracked data."""
import sys, csv, json, hashlib
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path.insert(0, B + "/src")
from pathlib import Path
import agent_arena
from agent_arena import iaa_analysis as ia
assert agent_arena.__file__.startswith(B)
run = Path(B) / "analysis/phase5_05c_iaa_results/iaa_20260801_162800"
man = json.loads((run / "input_manifest.json").read_text())
sheets = Path(B) / "analysis/phase5_05_blind_iaa_packets/annotator_facing/response_sheets"
for k, v in man["inputs"].items():
    p = sheets / v["filename"]
    print(f"sheet {k}: tracked={p.exists()} sha_matches_manifest={hashlib.sha256(p.read_bytes()).hexdigest() == v['sha256'] if p.exists() else None}")
rows = list(csv.DictReader(open(run / "four_rater_ABCD/case_vote_distribution.csv")))
summ = json.loads((run / "iaa_summary.json").read_text())
print("n cases:", len(rows), "| summary n_items:", summ["n_items"])
acd = [[r["A"], r["C"], r["D"]] for r in rows]
abcd = [[r["A"], r["B"], r["C"], r["D"]] for r in rows]
gold = [r["gold_label"] for r in rows]
print("Fleiss ACD recomputed:", ia.fleiss_kappa(acd, ia.LABEL_ORDER), "| summary:", summ["primary_ACD"]["fleiss_kappa"])
print("raw all-three ACD:", ia.all_agree_rate([[r[0] for r in acd], [r[1] for r in acd], [r[2] for r in acd]]), "| summary:", summ["primary_ACD"]["raw_all_three"])
print("Cohen A_vs_C:", ia.cohen_kappa([r[0] for r in acd], [r[1] for r in acd], ia.LABEL_ORDER), "| summary:", summ["primary_ACD"]["pairwise_kappa"]["A_vs_C"])
print("Cohen C_vs_gold:", ia.cohen_kappa([r[1] for r in acd], gold, ia.LABEL_ORDER), "| summary:", summ["primary_ACD"]["pairwise_kappa"]["C_vs_gold"])
fr = summ.get("four_rater_ABCD", {})
print("Fleiss ABCD recomputed:", ia.fleiss_kappa(abcd, ia.LABEL_ORDER), "| summary:", fr.get("fleiss_kappa"))
# tracked same-named sheets: how many rows carry a label?
for k in ("A", "B", "C"):
    parsed, errs = ia.parse_response_sheet(sheets / man["inputs"][k]["filename"])
    print(f"tracked sheet {k}: rows {len(parsed)} labelled {sum(1 for r in parsed if r.primary_label.strip())}")
