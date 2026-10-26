"""Verifier: does `agent-arena packet-integrity` PASS (exit 0) on an empty population?"""
import sys, os
B = sys.argv[1]; sys.path.insert(0, B + "/src")
from click.testing import CliRunner
from agent_arena.cli import cli
r = CliRunner()
def run(label, args, cwd):
    old = os.getcwd(); os.chdir(cwd)
    try:
        res = r.invoke(cli, ["packet-integrity"] + args)
    finally:
        os.chdir(old)
    head = [l for l in res.output.splitlines() if l.startswith(("cases:", "overall:", "task_dir:"))]
    print(f"{label:58s} exit={res.exit_code} {head}")
run("A) from repo root, defaults", [], B)
run("B) from a non-repo CWD, defaults", [], sys.argv[2])
run("C) repo root, --case-id typo", ["--case-id", "study-forensics-0004"], B)
run("D) repo root, --task-dir = AA-P10 live smoke tasks (JSON)", ["--task-dir", "analysis/live_smoke_20261011/live_run/tasks"], B)
run("E) repo root, --task-dir = examples/phase10 (JSON)", ["--task-dir", "examples/phase10"], B)
