import json, sys
from pathlib import Path
s = json.loads((Path(sys.argv[1]) / "analysis/c25_p9_20261011/live_retest/evidence/retest_summary.json").read_text())
print("RUN", s["run"], "ledger", s["ledger_state"], "attempts", s["attempts_total"], "retries", s["technical_retries"], "cost", s["confirmed_or_reserved_microusd"], "overruns", s["work_order_limits"]["overruns"])
for r in s["slots"]:
    if not r.get("invoked"):
        print(" -", r["profile"][:12], r["case"], "NOT RUN:", (r.get("reason") or "")[:160]); continue
    print(" +", r["profile"][:12], r["case"], r.get("status"), "m/h/e", r.get("model_judgment"), r.get("host_state"), r.get("effective_state"),
          "route", r.get("host_route"), "checks", r.get("expectation_checks"), "within", r.get("within_expectations"),
          "artifact", r.get("host_deviation_likely_string_artifact"), r.get("host_within_representation_artifact"))
    print("     p9", r.get("p9_route"), r.get("p9_status"), {k: (v["outcome"], v["request_sent"], v["response_received"], v["response_processed"]) for k, v in (r.get("p9_reviews") or {}).items()})
    print("     release", (r.get("test_release") or {}).get("status"), (r.get("test_release") or {}).get("as_expected"), "outside_log", r.get("executed_outside_the_runner_log"), "stop", r.get("stop_reasons"), "cause", (r.get("not_evaluable_cause") or {}).get("reason"))
