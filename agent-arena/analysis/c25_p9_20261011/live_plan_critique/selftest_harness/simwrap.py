"""Run one frozen retest script unchanged inside a critic_live2 simulation root.

Usage (cwd = SIM_ROOT):  PY simwrap.py SCRIPT [ARGS...]
Applies only: real network blocked, KNOWN_CLOSED_AUTHORIZATIONS pinned to the throwaway predecessors,
every LiveSession restricted to SIM_ROOT (no transport or key is injected: these scripts never send).
"""
import os
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim_lib  # noqa: E402

SIM_ROOT = sim_lib.guard(os.environ["SIM_ROOT"])
assert Path.cwd().resolve() == SIM_ROOT, "run from the simulation root"
assert "ANTHROPIC_API_KEY" not in os.environ
sim_lib.block_real_network()
sim_lib.pin(SIM_ROOT)
sim_lib.guard_sessions(SIM_ROOT, inject_live=False)
if os.environ.get("SIM_FAKE_NOW"):
    import datetime as _dt
    from agent_arena import phase10_live as _live
    _fake = _dt.datetime.fromisoformat(os.environ["SIM_FAKE_NOW"])

    class _Future(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return _fake
    _live.datetime = _Future  # simulated clock for authorization expiry only
if os.environ.get("SIM_CRASH_EXPOSURE"):
    from agent_arena.providers import anthropic_live as _al

    def _crash(*_a, **_k):
        raise RuntimeError("simulated crash inside prepare after the authorization was written")
    _al.max_exposure_microusd = _crash
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
