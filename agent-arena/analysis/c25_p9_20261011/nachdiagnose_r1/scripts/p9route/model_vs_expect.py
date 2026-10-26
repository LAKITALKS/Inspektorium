import glob, json, sys
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase8_models import PropositionLedger
from agent_arena.phase8_semantics import aggregate_claim
from agent_arena.schemas import AgentResult
exp = json.load(open(sys.argv[2]))["cases"]
summ = {(s["profile"][:13], s["case"]): s for s in json.load(open(sys.argv[3]))["slots"]}
for path in sorted(glob.glob(f"{sys.argv[1]}/*/*/record.json")):
    a = json.load(open(path)); rr = a["run_record"]; case = rr["task"]["id"][-5:]
    res = AgentResult.model_validate(rr["results"][0]["agent_result"])
    parsed, _ = parse_structured_output(res.raw_output, res.finish_reason)
    led = PropositionLedger.model_validate(parsed.forensic_record["phase8"])
    model = aggregate_claim(led.logic, {p.proposition_id: p.reported_verdict for p in led.propositions})
    host = rr["results"][0]["agent_result"]["phase8"].get("assessed_composite_state")
    e = exp[case]; s = summ[(path.split("/")[-3][:13], case)]
    f = lambda v: "hit" if v in e["expected_composite"] else ("NOT_ACCEPTABLE" if v in e["not_acceptable"] else "neither")
    print(path.split("/")[-3][:13], case, "model_composite=", model, f(model), "| host_assessed=", host, f(host),
          "| summary expected_composite_hit=", s.get("expected_composite_hit"), "composite=", s["semantics"]["composite"])
