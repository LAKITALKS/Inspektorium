import sys
from itertools import product
DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path.insert(0, DIAG + "/src")
import agent_arena; assert agent_arena.__file__.startswith(DIAG)
exec(open("enum_trees.py").read().split("pids = (")[0])
pids = ("a", "b", "c"); cases = mandatory_free = hidden = 0
for name, t in trees.items():
    for m in product(S, repeat=3):
        for h in product(S, repeat=3):
            model, host = dict(zip(pids, m)), dict(zip(pids, h))
            if model == host: continue
            cases += 1
            derived = {p: host[p] if host[p] == model[p] else "unknown" for p in pids}
            base = aggregate_claim(t, derived)
            infl = {p: any(aggregate_claim(t, {**derived, p: v}) != base for v in S) for p in pids}
            mandatory = aggregate_claim(t, model) != aggregate_claim(t, host) or any(
                infl[p] for p in pids if model[p] != host[p]) or any(infl[p] for p in pids if derived[p] == "unknown")
            if mandatory: continue
            mandatory_free += 1
            # any mixed adoption (each conflicting pid takes model or host side) yielding a different composite?
            conf = [p for p in pids if model[p] != host[p]]
            outs = {aggregate_claim(t, {**model, **{p: (host[p] if pick else model[p]) for p, pick in zip(conf, picks)}})
                    for picks in product((0, 1), repeat=len(conf))}
            if len(outs) > 1 or base == "unknown":
                hidden += 1; print("HIDDEN", name, m, h, outs, base)
print("conflict cases", cases, "| no mandatory trigger", mandatory_free, "| hidden at case level", hidden)
