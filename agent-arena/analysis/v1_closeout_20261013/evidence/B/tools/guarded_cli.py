"""Guarded canonical CLI: identical to the console script `agent-arena` (agent_arena.cli:cli) after netguard.

Optional env OLD_SRC puts an archived source tree first on sys.path (before/after contrast only).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import netguard  # noqa: E402,F401

if os.environ.get("OLD_SRC"):
    sys.path.insert(0, os.environ["OLD_SRC"])

import agent_arena  # noqa: E402
from agent_arena.cli import cli  # noqa: E402

sys.stderr.write(f"AGENT_ARENA {agent_arena.__version__} {agent_arena.__file__}\n")
sys.argv = ["agent-arena", *sys.argv[1:]]
cli()
