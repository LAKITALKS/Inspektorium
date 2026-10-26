"""Check every simulated -004 ledger against the order limits."""
import collections
import glob
import json
from pathlib import Path

for path in sorted(glob.glob("*/root/analysis/c25_p9_20261011/live_retest/ledger.json")):
    d = json.loads(Path(path).read_text())
    auth = json.loads((Path(path).parent / "authorization.json").read_text())
    total, attempts = auth["total_budget_microusd"], d["attempts"]
    retries = sum(1 for a in attempts if a.get("retry_of"))
    per_slot = collections.Counter(a["slot_key"] for a in attempts)
    over_call_reserved = [a["attempt_id"] for a in attempts if a["reserved_microusd"] > 300_000]
    over_call_confirmed = [a["attempt_id"] for a in attempts if (a.get("confirmed_token_cost_microusd") or 0) > 300_000]
    cum_violation = []
    running = 0
    for a in attempts:
        if running + a["reserved_microusd"] > total:
            cum_violation.append(a["attempt_id"])
        running += a["bound_microusd"]
    caps = {k: sum(1 for c in d.get("review_cap_claims", []) if c.split("|")[1:] == k.split("|"))
            for k in ("claude-haiku-5-5@3|counterreview", "claude-haiku-5-5@3|stability",
                      "claude-sonnet-5-5@3|counterreview", "claude-sonnet-5-5@3|stability")}
    print(f"{path.split('/')[0]:26s} attempts {len(attempts):2d}/12 retries {retries}/2 max/slot {max(per_slot.values()) if per_slot else 0}/2 "
          f"reserved>300k {over_call_reserved or '-'} confirmed>300k {over_call_confirmed or '-'} "
          f"reservation beyond total {cum_violation or '-'} final {d['reserved_microusd']}/{total} state {d['state']} "
          f"caps {'ok' if all(v <= 1 for v in caps.values()) else caps}")
