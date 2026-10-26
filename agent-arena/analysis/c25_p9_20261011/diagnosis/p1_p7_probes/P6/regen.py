import sys, runpy
B=sys.argv[1]; script=sys.argv[2]; out=sys.argv[3]
sys.path.insert(0, B+"/src")
import agent_arena; print("agent_arena from", agent_arena.__file__)
sys.argv=[script, "--out-dir", out]
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    print("exit", e.code)
