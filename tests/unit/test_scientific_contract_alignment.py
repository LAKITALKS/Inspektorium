"""Deterministic Phase-5A scientific-contract alignment tests (no model calls)."""

from __future__ import annotations

import hashlib

import pytest

from inspektorium.audit.runner import (
    STUDY_FORENSICS_CONDITION_HISTORICAL,
    STUDY_FORENSICS_CONDITION_PROSPECTIVE,
    STUDY_FORENSICS_PROMPT,
    STUDY_FORENSICS_PROMPT_PROSPECTIVE,
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
    STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
    resolve_study_forensics_prompt,
    study_forensics_prompt_identity,
)


HISTORICAL_SHA256 = "f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5"


def test_A_historical_prompt_bytes_and_hash_are_immutable():
    raw = STUDY_FORENSICS_PROMPT.encode("utf-8")
    assert len(raw) == 4_644
    assert hashlib.sha256(raw).hexdigest() == HISTORICAL_SHA256
    assert resolve_study_forensics_prompt(
        STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL
    ) == STUDY_FORENSICS_PROMPT


def test_B_prompt_versions_and_condition_identities_are_distinct():
    assert STUDY_FORENSICS_PROMPT_PROSPECTIVE != STUDY_FORENSICS_PROMPT
    assert resolve_study_forensics_prompt(
        STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE
    ) == STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert study_forensics_prompt_identity(STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL) == {
        "prompt_version": STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
        "prompt_condition_id": STUDY_FORENSICS_CONDITION_HISTORICAL,
    }
    assert study_forensics_prompt_identity(STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE) == {
        "prompt_version": STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE,
        "prompt_condition_id": STUDY_FORENSICS_CONDITION_PROSPECTIVE,
    }


def test_C_unknown_prompt_version_fails_closed():
    with pytest.raises(ValueError, match="unknown Study Forensics prompt version"):
        resolve_study_forensics_prompt("study_forensics_prompt/unregistered")


def test_D_only_the_two_approved_scientific_passages_change():
    historical_prefix, historical_schema = STUDY_FORENSICS_PROMPT.split(
        "You MUST respond with valid JSON", 1
    )
    prospective_prefix, prospective_schema = STUDY_FORENSICS_PROMPT_PROSPECTIVE.split(
        "You MUST respond with valid JSON", 1
    )
    assert historical_schema == prospective_schema
    assert historical_prefix != prospective_prefix
    # Unrelated task framing/evidence tiers remain exactly represented.
    assert historical_prefix.split("KEY RULE:", 1)[0] == prospective_prefix.split("KEY RULE:", 1)[0]


def test_E_prospective_rule_has_genuine_ME_trigger_and_no_broad_early_stage_shortcut():
    prompt = STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert "described biological mechanism in animal or preclinical evidence" in prompt
    assert "Broad \"early-stage research\" language" in prompt
    assert "early-stage research but the text implies human benefit" not in prompt


def test_F_shape_B_routes_by_honest_reporting_versus_inflation():
    prompt = STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert "Do NOT use mechanism_vs_evidence for the biomarker/surrogate-to-clinical gap" in prompt
    assert "honestly reported" in prompt and "classify as solid" in prompt
    assert "rhetorically sold as established clinical benefit" in prompt
    assert "classify as overclaim" in prompt


def test_G_genuine_overlap_uses_trigger_and_core_error_not_promotional_tone_alone():
    prompt = STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert "only when that trigger is present AND the specific failure captures the core error" in prompt
    assert "Promotional tone alone must not automatically override a genuine specific label" in prompt
    assert "actively sells" not in prompt


def test_H_cautious_reporting_distinguishes_real_constraint_from_decorative_hedging():
    prompt = STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert "A hedge is decorative when the surrounding text still implies unsupported benefit" in prompt
    assert "actually constrains the conclusion" in prompt
    assert "regardless of hedging quality" not in prompt


def test_I_CvC_specific_precedence_is_expressed_consistently():
    prompt = STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert "correlation_vs_causation or mechanism_vs_evidence" in prompt
    assert "causal claim from a non-causal, uncontrolled, or confounded design" in prompt


@pytest.mark.parametrize(
    ("case_name", "required_fragments", "forbidden_fragment"),
    [
        (
            "pure_me",
            ("described biological mechanism", "unproven human clinical benefit"),
            None,
        ),
        (
            "pure_overclaim",
            ("Otherwise use overclaim for rhetorical inflation beyond the evidence",),
            None,
        ),
        (
            "genuine_me_overclaim_overlap",
            ("specific label takes precedence", "captures the core error"),
            "Promotional tone automatically",
        ),
        (
            "shape_b_inflated",
            ("Shape B surrogate/biomarker inflation remains overclaim",),
            None,
        ),
        (
            "shape_b_honest",
            ("honestly reported", "classify as solid"),
            None,
        ),
        (
            "cautious_reporting",
            ("actually constrains the conclusion", "solid"),
            None,
        ),
        (
            "cvc_overlap",
            ("Use correlation_vs_causation", "specific label takes precedence"),
            None,
        ),
    ],
)
def test_J_synthetic_contract_cases_are_expressible_without_contradiction(
    case_name, required_fragments, forbidden_fragment
):
    # These assertions establish textual contract coverage, not LLM compliance or accuracy.
    prompt = STUDY_FORENSICS_PROMPT_PROSPECTIVE
    assert case_name
    assert all(fragment in prompt for fragment in required_fragments)
    if forbidden_fragment:
        assert forbidden_fragment not in prompt
