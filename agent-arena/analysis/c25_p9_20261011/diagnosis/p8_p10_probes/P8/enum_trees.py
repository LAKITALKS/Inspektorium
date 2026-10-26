"""Exhaustive check: can a proposition conflict P9 calls non-material (derived-state perturbation) still change
the model or host composite? Trees over 3 leaves, all 4^3 x 4^3 model/host assignments."""
import sys
from itertools import product
DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path.insert(0, DIAG + "/src")
import agent_arena; assert agent_arena.__file__.startswith(DIAG)
from agent_arena.phase8_models import ClaimLogic
from agent_arena.phase8_semantics import aggregate_claim
S = ("supported", "unsupported", "contradicted", "unknown")
L = lambda p: ClaimLogic(operator="leaf", proposition_id=p)
N = lambda op, *c: ClaimLogic(operator=op, children=list(c))
trees = {"and3": N("and", L("a"), L("b"), L("c")), "or3": N("or", L("a"), L("b"), L("c")),
         "and(or)": N("and", N("or", L("a"), L("b")), L("c")), "or(and)": N("or", N("and", L("a"), L("b")), L("c")),
         "and(or(and))": N("and", N("or", N("and", L("a"), L("b")), L("c"))),}
pids = ("a", "b", "c"); checked = hidden = 0
for name, t in trees.items():
    for m in product(S, repeat=3):
        for h in product(S, repeat=3):
            model, host = dict(zip(pids, m)), dict(zip(pids, h))
            derived = {p: host[p] if host[p] == model[p] else "unknown" for p in pids}
            mc, hc = aggregate_claim(t, model), aggregate_claim(t, host)
            base = aggregate_claim(t, derived)
            for p in pids:
                if model[p] == host[p]:
                    continue
                checked += 1
                material = any(aggregate_claim(t, {**derived, p: v}) != base for v in S)
                if material or mc != hc:
                    continue
                # non-material and no composite conflict: does adopting either side for p change any composite?
                for side in (model, host):
                    for v in (model[p], host[p]):
                        if aggregate_claim(t, {**side, p: v}) != aggregate_claim(t, side):
                            hidden += 1
                    break
print("conflicting (tree, assignment, pid) checked:", checked, "| hidden material conflicts:", hidden)
# also: derived composite decisive => equals model and host composite
bad = 0
for name, t in trees.items():
    for m in product(S, repeat=3):
        for h in product(S, repeat=3):
            model, host = dict(zip(pids, m)), dict(zip(pids, h))
            derived = {p: host[p] if host[p] == model[p] else "unknown" for p in pids}
            d = aggregate_claim(t, derived)
            if d != "unknown" and not (d == aggregate_claim(t, model) == aggregate_claim(t, host)):
                bad += 1
print("decisive effective composite differing from model or host composite:", bad)
shown = 0
for name, t in trees.items():
    for m in product(S, repeat=3):
        for h in product(S, repeat=3):
            model, host = dict(zip(pids, m)), dict(zip(pids, h))
            derived = {p: host[p] if host[p] == model[p] else "unknown" for p in pids}
            mc, hc = aggregate_claim(t, model), aggregate_claim(t, host)
            base = aggregate_claim(t, derived)
            for p in pids:
                if model[p] == host[p]: continue
                material = any(aggregate_claim(t, {**derived, p: v}) != base for v in S)
                if material or mc != hc: continue
                if aggregate_claim(t, {**model, p: host[p]}) != mc and shown < 4:
                    shown += 1
                    print(name, "pid", p, "model", m, "host", h, "derived", derived, "base", base, "mc=hc", mc,
                          "model-with-host-p", aggregate_claim(t, {**model, p: host[p]}))
