"""Loaded via PYTHONPATH for the literal console script: installs netguard before agent_arena runs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import netguard  # noqa: E402,F401
