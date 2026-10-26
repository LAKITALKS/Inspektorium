"""Create one throwaway simulation root that mirrors the repository layout the frozen scripts expect.

SIM_ROOT/
  .git, src/marker.py         tiny git repo (prepare/run pre-checks use git rev-parse/diff/status)
  .venv/bin/agent-arena       stand-in CLI wrapper -> fake_cli.py (real venv python, MockTransport)
  analysis/live_smoke_20261011/{live_run,repair_r1}
                              throwaway predecessors: byte-level transforms of the real -002/-003
                              authorization+ledger (read-only source), re-bound to this directory
                              (same consumed amounts 487,679 + 749,257 microUSD, 12 + 12 attempts,
                              0 retries, REVOKED), so the UNCHANGED prepare_retest.py computes 763,064.
  pins.json                   KNOWN_CLOSED_AUTHORIZATIONS for this root only
  draft/                      byte-identical copy of live_retest_draft (prepare reads DRAFT from here)
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim_lib  # noqa: E402

REPO = Path("__LOCAL_HOME__/Documents/Projects/agent-arena")
SP = Path("__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/"
          "cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad")
PY = REPO / ".venv/bin/python"
root = sim_lib.guard(sys.argv[1])
assert not root.exists(), root
root.mkdir(parents=True)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
(root / "src").mkdir()
(root / "src" / "marker.py").write_text("# simulation stand-in for the tested src tree\n")
git = ["git", "-c", "user.name=critic-sim", "-c", "user.email=critic-sim@example.invalid",
       "-c", "commit.gpgsign=false"]
subprocess.run(git + ["init", "-q"], cwd=root, check=True, env=env)
subprocess.run(git + ["add", "src/marker.py"], cwd=root, check=True, env=env)
subprocess.run(git + ["commit", "-q", "-m", "sim tested code"], cwd=root, check=True, env=env)

(root / ".venv" / "bin").mkdir(parents=True)
wrapper = root / ".venv" / "bin" / "agent-arena"
wrapper.write_text(f"#!/bin/zsh\nexport SIM_ROOT={root}\nexport PYTHONDONTWRITEBYTECODE=1\n"
                   f"exec {PY} {sim_lib.HARNESS / 'fake_cli.py'} \"$@\"\n")
wrapper.chmod(0o755)

base = root / "analysis" / "live_smoke_20261011"
pins, prev_ledger_sha = {}, None
for name, aid in (("live_run", "AA-P10-LIVE-SMOKE-20261011-002"), ("repair_r1", "AA-P10-LIVE-SMOKE-20261011-003")):
    src = REPO / "analysis" / "live_smoke_20261011" / name
    auth = json.loads((src / "authorization.json").read_bytes())
    ledger = json.loads((src / "ledger.json").read_bytes())
    assert auth["authorization_id"] == aid and ledger["state"] == "REVOKED"
    target = base / name
    target.mkdir(parents=True)
    auth["canonical_directory"] = str(target)
    if prev_ledger_sha is not None:
        auth["supersedes"]["prior_ledger_sha256_after_closure"] = prev_ledger_sha
    auth_raw = (json.dumps(auth, indent=2, ensure_ascii=False) + "\n").encode()
    (target / "authorization.json").write_bytes(auth_raw)
    ledger["binding"]["authorization_fingerprint"] = sha(auth_raw)
    ledger_raw = (json.dumps(ledger, indent=2) + "\n").encode()
    (target / "ledger.json").write_bytes(ledger_raw)
    pins[aid] = {"ledger_sha256": sha(ledger_raw), "authorization_sha256": sha(auth_raw)}
    prev_ledger_sha = sha(ledger_raw)
(root / "pins.json").write_text(json.dumps(pins, indent=2) + "\n")

draft = root / "draft"
shutil.copytree(SP / "live_retest_draft", draft)
for f in sorted((SP / "live_retest_draft").iterdir()):
    assert (draft / f.name).read_bytes() == f.read_bytes()
print(json.dumps({"root": str(root), "pins": pins}, indent=1))
