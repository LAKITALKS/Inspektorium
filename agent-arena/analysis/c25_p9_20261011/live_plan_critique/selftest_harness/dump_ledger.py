import json
import sys
from pathlib import Path

d = Path(sys.argv[1])
if not (d / "ledger.json").exists():
    print("no ledger")
    sys.exit(0)
data = json.loads((d / "ledger.json").read_text())
for a in data["attempts"]:
    print(a["attempt_id"], a["slot_key"].replace("aa-p10-live-retest-", ""), a["state"], a.get("billing"),
          "http", a.get("http_status"), "retry_of", a.get("retry_of"), "reserved", a["reserved_microusd"],
          "bound", a["bound_microusd"], "confirmed", a.get("confirmed_token_cost_microusd"),
          "overrun", a.get("overrun_microusd"), "capture", (d / "captures" / f"{a['attempt_id']}.json").exists())
print("state", data["state"], "reserved", data["reserved_microusd"], "remaining", data["executable_remaining_microusd"],
      "attempts", len(data["attempts"]), "retries", sum(1 for a in data["attempts"] if a.get("retry_of")),
      "terminal", len(data["terminal_keys"]))
print("claims", [k.replace("aa-p10-live-retest-", "") for k in data.get("review_cap_claims", [])])
print("reason", data.get("revocation_reason"))
