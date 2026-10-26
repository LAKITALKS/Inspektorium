import json, re, sys, copy
from agent_arena.schemas import ForensicRecord
from agent_arena.phase8_semantics import evaluate_phase8, _missing_attributes, _binding_state, _raw_match, _capability
from agent_arena.phase8_models import PropositionLedger

REPO = "__LOCAL_HOME__/Documents/Projects/agent-arena/"

def load(attempt):
    d = json.load(open(REPO + f"analysis/live_smoke_20261011/repair_r1/captures/attempt-{attempt:03d}.json"))
    t = d["interpretation"]["final_text"].strip()
    t = re.sub(r"^```(json)?\s*", "", t); t = re.sub(r"\s*```$", "", t)
    return json.loads(t)

def run(fr, label=""):
    rec = ForensicRecord.model_validate(fr)
    res = evaluate_phase8(rec)
    out = {p.proposition_id: p.derived_state for p in res.propositions}
    print(f"[{label}] status={res.technical_status} assessed_composite={res.assessed_composite_state} props={out}")
    return rec, res

def detail(fr):
    rec = ForensicRecord.model_validate(fr)
    ledger = PropositionLedger.model_validate(rec.phase8)
    descs = {d.evidence_id: d for d in ledger.evidence_descriptions}
    scopes = {s.search_scope_id: s for s in rec.search_scopes}
    ev = {e.evidence_id: e for e in rec.evidence}
    for p in ledger.propositions:
        print(" ", p.proposition_id, "reported", p.reported_verdict, "missing", _missing_attributes(p))
        for b in p.evidence_bindings:
            st, rs = _binding_state(p, b, ledger, descs, scopes, ev, rec.negative_assertions)
            mm, un = _raw_match(p, descs[b.evidence_id])
            cap = _capability(p, descs[b.evidence_id], descs, ev)
            print(f"    {b.binding_id} ev={b.evidence_id} role={ev[b.evidence_id].role.value} dir={b.directness} obs={b.observation} -> {st}; mismatch={mm} unresolved={un} capability={cap}; last_reason={rs[-1]}")

if __name__ == "__main__":
    a = int(sys.argv[1])
    fr = load(a)["forensic_record"]
    run(fr, f"attempt-{a:03d} as captured")
    detail(fr)
