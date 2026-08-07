"""Tests for canonical SHA-256 provenance."""

from __future__ import annotations

from inspektorium.core.fingerprints import (
    canonical_bundle_json,
    fingerprint_input,
    fingerprint_text,
)
from inspektorium.core.models import InspectionInput


def _input(
    *, answer: str = "Café", source_order: tuple[str, ...] = ("b", "a")
) -> InspectionInput:
    return InspectionInput.model_validate(
        {
            "answer": {"text": answer},
            "sources": [
                {"source_id": source_id, "text": f"Text {source_id}."}
                for source_id in source_order
            ],
        }
    )


def test_same_canonical_text_has_same_digest() -> None:
    assert fingerprint_text("Cafe\u0301\r\n") == fingerprint_text("Café\n")


def test_one_character_change_changes_digest() -> None:
    assert fingerprint_text("alpha") != fingerprint_text("alphb")


def test_source_order_does_not_change_bundle_digest() -> None:
    first = fingerprint_input(_input(source_order=("b", "a")))
    second = fingerprint_input(_input(source_order=("a", "b")))

    assert first == second
    assert [source.source_id for source in first.sources] == ["a", "b"]


def test_bundle_serialization_is_stable_and_compact() -> None:
    bundle = canonical_bundle_json(_input())

    assert "\n" not in bundle
    assert '": "' not in bundle
    assert bundle.index('"source_id":"a"') < bundle.index('"source_id":"b"')
