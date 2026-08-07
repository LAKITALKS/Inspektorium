"""Canonical text normalization and offset policy."""

from __future__ import annotations

import unicodedata


def normalize_text(text: str) -> str:
    """Return the canonical text used for models, offsets, hashes, and reports.

    Canonical text uses LF newlines and Unicode NFC. All other whitespace is
    preserved. Offsets are Python string character indices into this result.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")
    lf_text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", lf_text)


__all__ = ["normalize_text"]
