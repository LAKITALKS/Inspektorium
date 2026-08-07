"""Canonical text and offset-policy tests."""

from __future__ import annotations

import unicodedata

from inspektorium.core.models import InspectionInput
from inspektorium.core.normalization import normalize_text


def test_crlf_and_bare_cr_become_lf() -> None:
    assert normalize_text("one\r\ntwo\rthree\n") == "one\ntwo\nthree\n"


def test_composed_and_decomposed_unicode_share_nfc_form() -> None:
    decomposed = "Cafe\u0301"
    composed = "Café"

    assert decomposed != composed
    assert normalize_text(decomposed) == composed
    assert unicodedata.is_normalized("NFC", normalize_text(decomposed))


def test_german_umlauts_are_preserved() -> None:
    assert normalize_text("Grüße aus Köln") == "Grüße aus Köln"


def test_other_whitespace_is_preserved() -> None:
    text = "  first\tcolumn  \n\nlast  "

    assert normalize_text(text) == text


def test_input_model_exposes_only_canonical_text() -> None:
    inspection_input = InspectionInput.model_validate(
        {
            "answer": {"text": "Gru\u0308n\r\nbleibt  "},
            "sources": [{"source_id": "source", "text": "Café\rline"}],
        }
    )

    assert inspection_input.answer.text == "Grün\nbleibt  "
    assert inspection_input.sources[0].text == "Café\nline"
