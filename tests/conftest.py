"""Reusable synthetic fixtures for the public test suite."""

from __future__ import annotations

from typing import Any

import pytest

from inspektorium.core.models import InspectionInput


@pytest.fixture
def inspection_input() -> InspectionInput:
    return InspectionInput.model_validate(
        {
            "answer": {
                "answer_id": "answer",
                "text": "The blue door opens at noon. The blue door closes at six.",
            },
            "sources": [
                {
                    "source_id": "manual",
                    "title": "Door manual",
                    "text": (
                        "The blue door opens at noon. The blue door closes at five."
                    ),
                },
                {
                    "source_id": "notice",
                    "title": "Lobby notice",
                    "text": "Visitors should use the blue door.",
                },
            ],
        }
    )


@pytest.fixture
def supported_proposal_data() -> dict[str, Any]:
    return {
        "claim_id": "claim-1",
        "claim_text": "The blue door opens at noon.",
        "claim_start": 0,
        "claim_end": 28,
        "proposed_relation": "supported",
        "source_id": "manual",
        "evidence_quote": "The blue door opens at noon.",
        "evidence_start": 0,
        "evidence_end": 28,
        "rationale": "The manual states the same opening time.",
        "evidence_sufficiency": "sufficient",
        "evaluator_certainty": "high",
    }
