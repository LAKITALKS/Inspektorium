"""Start the frozen runner of SIM_ROOT detached, wait until a request is in flight, then kill.

Usage: kill_runner.py SIM_ROOT MODE   MODE = runner (SIGTERM to the runner only) | group (SIGTERM to its group)
Then try close_retest.py immediately (child may still hold the lease), wait for the child, try again.
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim_lib  # noqa: E402

root = sim_lib.guard(sys.argv[1])
mode = sys.argv[2]
PY = "__LOCAL_HOME__/Documents/Projects/agent-arena/.venv/bin/python"
env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
env.update(SIM_ROOT=str(root), PYTHONDONTWRITEBYTECODE="1")
runner_env = dict(env, ANTHROPIC_API_KEY="sim-placeholder-not-a-key")
log = open(root.parent / "run.out", "w")
runner = subprocess.Popen([PY, "analysis/c25_p9_20261011/live_retest/scripts/run_retest.py"], cwd=root, env=runner_env,
                          stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
marker = root / "inflight.marker"
deadline = time.time() + 60
while not marker.exists() and time.time() < deadline and runner.poll() is None:
    time.sleep(0.1)
info = json.loads(marker.read_text())
print("in flight:", info)
if mode == "runner":
    runner.send_signal(signal.SIGTERM)
else:
    os.killpg(runner.pid, signal.SIGTERM)
runner.wait(timeout=30)
print("runner exit code:", runner.returncode)
child_alive = True
try:
    os.kill(info["pid"], 0)
except ProcessLookupError:
    child_alive = False
print("CLI child alive after the kill:", child_alive)
wrap = str(sim_lib.HARNESS / "simwrap.py")
close = [PY, wrap, "analysis/c25_p9_20261011/live_retest/scripts/close_retest.py"]
first = subprocess.run(close, cwd=root, env=env, capture_output=True, text=True)
print("close #1 exit:", first.returncode, (first.stdout + first.stderr).strip().splitlines()[-1][:300])
while child_alive:
    try:
        os.kill(info["pid"], 0)
        time.sleep(0.2)
    except ProcessLookupError:
        child_alive = False
print("CLI child finished")
second = subprocess.run(close, cwd=root, env=env, capture_output=True, text=True)
print("close #2 exit:", second.returncode)
print(second.stdout[-1500:], second.stderr[-800:])
