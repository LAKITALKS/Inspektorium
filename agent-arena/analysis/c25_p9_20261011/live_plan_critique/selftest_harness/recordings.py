"""Synthetic Phase-8 recordings bound to the real LR-01..03 texts (critic simulation only).

Built from the repository's offline example recordings by replacing the example claim with the LR claim
and the example source sentence with a verbatim sentence of the LR context; selected fields are then
changed to produce the wanted model judgment / host derivation. These are stand-ins for model output,
not predictions of what a real model will answer.
"""
import copy
import json
from pathlib import Path

REPO = Path("__LOCAL_HOME__/Documents/Projects/agent-arena")
EXAMPLES = REPO / "examples" / "phase10"
OLD_PROMPT = "intervention X reduces event Q in adults."
OLD_CONTEXT = ("A randomized comparison in adults (human) found that intervention X reduced event Q versus "
               "placebo at 12 weeks.")

LR = {
    "LR-01": {
        "prompt": ("In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based "
                   "balance training program had fewer falls over twelve months than those assigned to general "
                   "health advice."),
        "quote": ("Over twelve months, community-dwelling adults aged 70 and older assigned to the home-based balance "
                  "training program had 31 percent fewer falls than those assigned to general health advice, and "
                  "the difference was statistically significant."),
    },
    "LR-02": {
        "prompt": "Drinking green tea daily prevents memory decline in adults aged 65 and older.",
        "quote": ("People who reported drinking green tea daily scored slightly higher on that test than people "
                  "who rarely drank it; daily tea drinkers were also more physically active and more often had "
                  "completed higher education, and the comparison was not adjusted for these differences."),
    },
    "LR-03": {
        "prompt": ("At a logistics company, introducing a four-day working week reduced recorded sick days among "
                   "office staff."),
        "quote": ("In its annual report, the company stated that recorded sick days among office staff were 20 "
                  "percent lower that year than in the previous year."),
    },
}


def _walk(value, prompt, quote):
    if isinstance(value, dict):
        return {k: _walk(v, prompt, quote) for k, v in value.items()}
    if isinstance(value, list):
        return [_walk(v, prompt, quote) for v in value]
    if isinstance(value, str):
        if value == OLD_CONTEXT:
            return quote
        return value.replace(OLD_PROMPT, prompt)
    return value


def build(case, variant):
    """variant: supported | unsupported_agreed | conflict_unknown_host | review_unsupported"""
    base = json.loads((EXAMPLES / "positive-recording.json").read_text())
    spec = LR[case]
    data = _walk(base, spec["prompt"], spec["quote"])
    rec = data["forensic_record"]
    for prop in rec["phase8"]["propositions"]:
        prop["original_span"] = {"start": 0, "end": len(spec["prompt"]), "text": spec["prompt"]}
    desc = rec["phase8"]["evidence_descriptions"][0]
    prop = rec["phase8"]["propositions"][0]
    if variant == "supported":
        pass
    elif variant == "unsupported_agreed":
        # Observational evidence for a causal claim: host 'unsupported'; the model says unsupported too.
        desc["evidence_type"] = "observational"
        desc["randomized"] = False
        prop["reported_verdict"] = "unsupported"
        for t in rec["phase8"]["transformations"]:
            if t.get("asserted_state") is not None:
                t["asserted_state"] = "unsupported"
    elif variant in {"conflict_unknown_host", "review_unsupported"}:
        # Non-randomized-unknown intervention: host 'unknown' (identification not established, randomized
        # null); the model judges 'unsupported' -> material composite conflict (mandatory review).
        desc["randomized"] = None
        prop["reported_verdict"] = "unsupported"
        for t in rec["phase8"]["transformations"]:
            if t.get("asserted_state") is not None:
                t["asserted_state"] = "unsupported"
    elif variant in {"conflict2", "review2"}:
        # As conflict_unknown_host, plus a second evidence item (another verbatim LR sentence) bound to the
        # proposition, so the Phase-9 stability variant (evidence order reversed) is not a no-op.
        desc["randomized"] = None
        prop["reported_verdict"] = "unsupported"
        for t in rec["phase8"]["transformations"]:
            if t.get("asserted_state") is not None:
                t["asserted_state"] = "unsupported"
        second = SECOND[case]
        rec["evidence"].append(dict(rec["evidence"][0], evidence_id="e2", exact_reference=second, text=second))
        prop["evidence_bindings"].append(dict(prop["evidence_bindings"][0], binding_id="b2", evidence_id="e2"))
        rec["phase8"]["evidence_descriptions"].append(dict(desc, evidence_id="e2", study_id="synthetic-study-1"))
        for finding in rec["findings"]:
            finding["supporting_evidence_ids"].append("e2")
        for finding in rec["client_findings"]:
            finding["referenced_evidence_ids"].append("e2")
    elif variant in {"mismatch_agreed", "mismatch_conflict"}:
        # Attribute-string difference only: the evidence population string differs from the claim's, so the host
        # derives 'unsupported' (semantic mismatch: population). Model unsupported (agreed) or supported (conflict).
        desc["attributes"] = dict(desc["attributes"], population="adults in one company")
        verdict = "unsupported" if variant == "mismatch_agreed" else "supported"
        prop["reported_verdict"] = verdict
        for t in rec["phase8"]["transformations"]:
            if t.get("asserted_state") is not None:
                t["asserted_state"] = verdict
    elif variant == "mixed_conflict":
        # Two bindings: e1 carries a design limitation (unknown), e2 differs only in the population string
        # (unsupported). Host unknown (unknown dominates); the model says supported -> material conflict.
        second = SECOND[case]
        rec["evidence"].append(dict(rec["evidence"][0], evidence_id="e2", exact_reference=second, text=second))
        prop["evidence_bindings"].append(dict(prop["evidence_bindings"][0], binding_id="b2", evidence_id="e2"))
        e2 = copy.deepcopy(desc)
        e2.update(evidence_id="e2", study_id="synthetic-study-1")
        e2["attributes"]["population"] = "adults in one company"
        rec["phase8"]["evidence_descriptions"].append(e2)
        desc["design_limitations"] = ["outcome counted by self-report"]
        for finding in rec["findings"]:
            finding["supporting_evidence_ids"].append("e2")
        for finding in rec["client_findings"]:
            finding["referenced_evidence_ids"].append("e2")
    else:
        raise ValueError(variant)
    return json.dumps(data)


SECOND = {
    "LR-01": "The program consisted of three short sessions per week.",
    "LR-02": "A one-time survey of 2,000 adults aged 65 and older asked about tea habits and gave each person a single memory test.",
    "LR-03": "A logistics company introduced a four-day working week for all office staff in January.",
}


if __name__ == "__main__":
    for case in LR:
        for variant in ("supported", "unsupported_agreed", "conflict_unknown_host"):
            print(case, variant, len(build(case, variant)))
