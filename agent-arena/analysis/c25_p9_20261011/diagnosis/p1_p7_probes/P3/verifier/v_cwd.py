"""Does every discover_cases consumer fail closed on an empty discovery? (offline)"""
import sys, os, json
B, D = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
from click.testing import CliRunner
from agent_arena.cli import cli

os.chdir(B)
r = CliRunner().invoke(cli, ["packet-integrity", "--json", "--quiet"])
s = json.loads(r.output)["summary"]
print("checkout cwd:", "exit", r.exit_code, s)
r = CliRunner().invoke(cli, ["packet-integrity", "--json", "--quiet", "--case-id", "study-forensics-999"])
print("nonexistent case-id:", "exit", r.exit_code, json.loads(r.output)["summary"])
os.chdir("/")
r = CliRunner().invoke(cli, ["packet-integrity", "--json", "--quiet"])
print("wrong cwd '/':", "exit", r.exit_code, json.loads(r.output)["summary"])
