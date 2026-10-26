"""Recompute the cap-aware reserve rule for every slot of every simulated run from run_log + manifest."""
import glob
import json
import re
from pathlib import Path

for log_path in sorted(glob.glob("*/root/analysis/c25_p9_20261011/live_retest/evidence/run_log.jsonl")):
    retest = Path(log_path).parents[1]
    manifest = json.loads((retest / "manifest.json").read_text())
    total = json.loads((retest / "authorization.json").read_text())["total_budget_microusd"]
    b = manifest["budget"]
    reserved, claims, bad, checked, starts = 0, [], [], 0, 0
    for line in Path(log_path).read_text().splitlines():
        e = json.loads(line)
        if e.get("event") == "start":
            starts += 1
            if starts > 1:
                break  # only the first runner start is checked here
            continue
        if "profile" not in e:
            continue
        key = f"{e['profile']}|{e['case']}"
        review_open = not any(k.split("|")[1:] == [e["profile"], "counterreview"] for k in claims)
        needed = b["max_primary_exposure_microusd"][key] + (b["counterreview_reserve_microusd"][key] if review_open else 0)
        reason = e.get("reason") or ""
        if e.get("invoked"):
            checked += 1
            if total - reserved < needed:
                bad.append(f"{key} ran with remaining {total - reserved} < needed {needed}")
            la = e.get("ledger_after")
            if la:
                reserved, claims = la["reserved_or_confirmed_microusd"], la["review_cap_claims"]
                if reserved > total:
                    bad.append(f"reserved {reserved} > total {total} after {key}")
        elif reason.startswith("reserve rule"):
            checked += 1
            m = re.search(r"remaining (\d+) < required (\d+)", reason)
            if not m or int(m.group(1)) != total - reserved or int(m.group(2)) != needed or total - reserved >= needed:
                bad.append(f"{key} skip reason inconsistent: {reason} (recomputed remaining {total - reserved}, needed {needed})")
    print(f"{log_path.split('/')[0]:28s} slots checked {checked}  violations {bad if bad else 'none'}")
