"""Abstract supplied-source cases for offline Phase-8 pipeline tests, never efficacy data."""

from copy import deepcopy


def raw_record(*, endpoint="event Q", species="human", intervention="intervention X"):
    claim = f"{intervention} reduces {endpoint} in adults."
    source = (
        f"A randomized comparison in adults ({species}) found that {intervention} "
        f"reduced {endpoint} versus placebo at 12 weeks."
    )
    attrs = {
        "species": species, "population": "adults", "intervention": intervention,
        "comparator": "placebo", "endpoint": endpoint, "endpoint_type": "clinical_event",
        "relation": "causal", "follow_up": "12 weeks", "certainty": "asserted",
        "comparison": "between",
    }
    prop = {
        "proposition_id": "claim:p1", "parent_claim_id": "claim", "proposition_text": claim,
        "original_span": {"start": 0, "end": len(claim), "text": claim},
        "materiality": "required", "attributes": attrs,
        "material_dimensions": list(attrs), "evidence_bindings": [{
            "binding_id": "b1", "proposition_id": "claim:p1", "evidence_id": "e1",
            "directness": "direct", "observation": "support", "reason": "Matching trial",
        }],
        "reported_verdict": "supported", "reason": "Source reports the stated comparison",
        "provenance_id": "origin", "search_question": f"What evidence supports: {claim}",
        "search_scope_ids": ["review"],
    }
    transformations = []
    for stage, from_text, to_text, target in (
        ("extraction", claim, claim, "claim:p1"),
        ("search_question", claim, prop["search_question"], "claim:p1"),
        ("internal", claim, claim, "claim:p1"),
        ("summary", claim, claim, "client1"),
    ):
        transformations.append({
            "transformation_id": stage, "stage": stage, "target_id": target,
            "from_proposition_ids": ["claim:p1"], "from_text": from_text, "to_text": to_text,
            "from_attributes": deepcopy(attrs), "to_attributes": deepcopy(attrs),
            "asserted_state": "supported" if stage == "summary" else None,
            "asserts_whole_claim": stage == "summary", "reason": "Meaning retained",
        })
    record = {
        "record_id": "offline-input", "synthetic_fixture": True,
        "provenance": [{"provenance_id": "origin", "exact_claim_text": claim,
                        "source_id": "input"}],
        "evidence": [{"evidence_id": "e1", "source_id": "context", "role": "supporting",
                      "endpoint": endpoint, "text": source, "exact_reference": source,
                      "value_origin": "source_reported"}],
        "findings": [{"finding_id": "claim:p1", "provenance_id": "origin",
                      "proposition": claim, "supporting_evidence_ids": ["e1"],
                      "allowed_summary_strength": "not_assessed"}],
        "client_findings": [{"client_finding_id": "client1", "parent_finding_id": "claim:p1",
                             "display_claim": claim, "provenance_id": "origin",
                             "referenced_evidence_ids": ["e1"], "client_strength": "not_assessed"}],
        "search_scopes": [{"search_scope_id": "review", "scope_type": "reviewed_set",
                           "reviewed_source_ids": ["input", "context"]}],
        "phase8": {
            "claim_id": "claim", "provenance_id": "origin", "original_claim": claim,
            "required_proposition_ids": ["claim:p1"], "propositions": [prop],
            "logic": {"operator": "leaf", "proposition_id": "claim:p1"},
            "extraction_provenance": "offline extraction from supplied prompt and context",
            "evidence_descriptions": [{
                "evidence_id": "e1", "evidence_type": "controlled_intervention",
                "source_role": "primary_study", "attributes": deepcopy(attrs),
                "randomized": True, "study_id": "synthetic-study-1",
            }],
            "transformations": transformations,
        },
    }
    return claim, source, record
