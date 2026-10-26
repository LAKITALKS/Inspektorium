import json, subprocess, sys
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
for path, commits in (("analysis/phase5b_haiku_full_replication/execution_plan.json", sys.argv[1].split(",")),
                      ("analysis/phase5b_sonnet_full_replication/execution_plan.json", sys.argv[2].split(","))):
    for c in commits:
        out = subprocess.run(["git", "-C", B, "show", f"{c}:{path}"], capture_output=True)
        if out.returncode:
            print(c, path.split("/")[1], "ABSENT"); continue
        d = json.loads(out.stdout); a = d["authorization"]
        print(c, path.split("/")[1], a["status"], a.get("authorized_budget_calls"), "authfp", a["specification_fingerprint"][:8],
              "consumed", (a.get("consumed_invocation_specification_fingerprint") or "")[:8], a.get("authorization_mode"), d["progress"]["status"], d["progress"].get("stop_stage"))
