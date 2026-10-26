"""Evidence-derived proposition state before the C29 reported-verdict override (offline, read-only)."""
import glob
import json
import sys

from agent_arena.output_contract import parse_structured_output
from agent_arena.phase8_models import PropositionLedger
from agent_arena.phase8_semantics import _assess_proposition, aggregate_claim
from agent_arena.schemas import AgentResult, ForensicRecord

for path in sorted(glob.glob(f"{sys.argv[1]}/*/*/record.json")):
    rr = json.load(open(path))["run_record"]
    res = AgentResult.model_validate(rr["results"][0]["agent_result"])
    parsed, _ = parse_structured_output(res.raw_output, res.finish_reason)
    record = ForensicRecord.model_validate(parsed.forensic_record)
    ledger = PropositionLedger.model_validate(record.phase8)
    host, evid = {}, {}
    for prop in ledger.propositions:
        host[prop.proposition_id] = _assess_proposition(prop, ledger, record).derived_state
        neutral = prop.model_copy(update={"reported_verdict": "supported"})
        evid[prop.proposition_id] = _assess_proposition(neutral, ledger, record).derived_state
    print(path.split("/")[-3][:13], rr["task"]["id"][-5:],
          "reported=", {p.proposition_id: p.reported_verdict for p in ledger.propositions},
          "evidence_only=", evid, "host=", host,
          "composite_evidence_only=", aggregate_claim(ledger.logic, evid),
          "composite_host=", aggregate_claim(ledger.logic, host))
