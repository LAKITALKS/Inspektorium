"""Guarded canonical CLI: installs netguard, then runs agent_arena.cli:cli (the 'agent-arena' entry point)."""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netguard  # noqa: E402,F401
import agent_arena  # noqa: E402
sys.stderr.write(f"[aa_cli] agent_arena {agent_arena.__version__} from {os.path.dirname(agent_arena.__file__)}\n")
from agent_arena.cli import cli  # noqa: E402

sys.argv[0] = "agent-arena"
cli()
