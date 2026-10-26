"""W-cases: a weakening/qualifying evidence direction dropped from the client finding.
Only the model-supplied `material` flag differs between W1 and W2."""
import runpy, sys
from copy import deepcopy
ns = runpy.run_path(sys.argv[1], run_name="probe_lib")  # reuse helpers (re-runs earlier cases)
raw_record, taxonomy, summarize = ns["raw_record"], ns["taxonomy"], ns["summarize"]
WEAK = ("A second randomized comparison in adults found that agent Gamma did not "
        "reduce endpoint Delta versus placebo at 12 weeks.")

def weakening(material):
    claim, context, p = raw_record(endpoint="endpoint Delta", intervention="agent Gamma")
    context = context + " " + WEAK
    p["evidence"].append({"evidence_id": "e2", "source_id": "context", "role": "weakening",
                          "endpoint": "endpoint Delta", "text": WEAK, "exact_reference": WEAK,
                          "value_origin": "source_reported", "material": material})
    prop = p["phase8"]["propositions"][0]
    prop["evidence_bindings"].append({"binding_id": "b2", "proposition_id": "claim:p1",
        "evidence_id": "e2", "directness": "direct", "observation": "inconclusive",
        "reason": "Second trial did not replicate"})
    d2 = deepcopy(p["phase8"]["evidence_descriptions"][0]); d2.update(evidence_id="e2", study_id="synthetic-study-2")
    p["phase8"]["evidence_descriptions"].append(d2)
    p["findings"][0]["contrary_evidence_ids"] = ["e2"]
    taxonomy(p, core="none")
    return claim, context, p

print("\n######## W cases")
summarize("W1 weakening e2 material=True, client drops e2", *weakening(True))
summarize("W2 weakening e2 material=False, client drops e2", *weakening(False))
