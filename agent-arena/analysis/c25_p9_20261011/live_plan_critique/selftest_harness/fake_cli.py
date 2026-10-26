"""Stand-in for `.venv/bin/agent-arena` inside a critic_live2 simulation root (throwaway authorizations only).

Runs the unchanged canonical CLI (agent_arena.cli -> phase10_cli audit run --live -> run_audit) with three
differences: KNOWN_CLOSED_AUTHORIZATIONS is pinned to the throwaway predecessors of SIM_ROOT, every live session
gets a MockTransport and api_key='test-key', and the real HTTP transport raises if it is ever reached.
SIM_BREAK_RENDER_PROFILE (optional) makes the HTML renderer raise for that profile (bundle-write defect).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim_lib  # noqa: E402

SIM_ROOT = sim_lib.guard(os.environ["SIM_ROOT"])
assert Path.cwd().resolve() == SIM_ROOT, "the stand-in CLI runs only from its simulation root"
sim_lib.block_real_network()
sim_lib.pin(SIM_ROOT)
sim_lib.guard_sessions(SIM_ROOT, inject_live=True)
broken = os.environ.get("SIM_BREAK_RENDER_PROFILE")
if broken and "--profile" in sys.argv and sys.argv[sys.argv.index("--profile") + 1] == broken:
    from agent_arena import phase10_render

    def _boom(projection):
        raise RuntimeError("simulated renderer defect")
    phase10_render.html_report = _boom
from agent_arena.cli import cli  # noqa: E402

sys.argv[0] = "agent-arena"
sys.exit(cli())
