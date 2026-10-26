import sys, runpy
W = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_p8_p10/P10/wheel"
sys.path.insert(0, W + "/site")
import agent_arena; assert agent_arena.__file__.startswith(W + "/site"), agent_arena.__file__
script = sys.argv[1]; sys.argv = sys.argv[1:]
if script == "-c":
    exec(sys.argv[1])
else:
    runpy.run_path(script, run_name="__main__")
