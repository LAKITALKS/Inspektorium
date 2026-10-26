"""Provider-side evidence for the unit->request transition: per-unit input tokens.
H1/S1 actual input_tokens vs (a) the frozen pre-run count_tokens gate (system v2 + exact unit prompt)
and (b) the historical H0/S0 records (same user payload, different system prompt => constant delta)."""
import json, collections
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"


def jl(p):
    return [json.loads(l) for l in open(B + "/" + p) if l.strip()]


for key, ns, hist in (("haiku", "analysis/phase5b_haiku_full_replication", "analysis/phase7a_execution/haiku/raw/haiku_raw_records.jsonl"),
                      ("sonnet", "analysis/phase5b_sonnet_full_replication", "analysis/phase7a_execution/sonnet/raw/sonnet_raw_records.jsonl")):
    new = jl(f"{ns}/run/{key}/raw/{key}_raw_records.jsonl")
    old = jl(hist)
    gate = json.load(open(f"{B}/{ns}/pre_execution_cost_estimate.json"))
    counted = {r["unit_id"]: r["input_tokens"] for r in gate["input_tokens_first_attempt"]["per_unique_context"]}
    per_new = collections.defaultdict(set); per_old = collections.defaultdict(set)
    for r in new:
        per_new[r["unit_id"]].add((r.get("usage") or {}).get("input_tokens"))
    for r in old:
        per_old[r["unit_id"]].add((r.get("usage") or {}).get("input_tokens"))
    stable_new = all(len(v) == 1 for v in per_new.values())
    eq_gate = sum(1 for u, v in per_new.items() if v == {counted.get(u)})
    deltas = collections.Counter(next(iter(per_new[u])) - next(iter(per_old[u])) for u in per_new if len(per_old[u]) == 1)
    print(f"{key}: units {len(per_new)} | per-unit input tokens constant across 5 reps: {stable_new} | == count_tokens gate: {eq_gate}/84 | H1-H0 per-unit delta distribution: {dict(deltas)}")
