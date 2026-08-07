"""Deterministic SHA-256 provenance over canonical inspection text."""

from __future__ import annotations

import hashlib
import json

from inspektorium.core.models import (
    InputFingerprints,
    InspectionInput,
    SourceFingerprint,
)
from inspektorium.core.normalization import normalize_text


def fingerprint_text(text: str) -> str:
    """Hash canonical UTF-8 text with SHA-256."""

    canonical = normalize_text(text)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def canonical_bundle_json(inspection_input: InspectionInput) -> str:
    """Serialize the fingerprint bundle with stable source ordering."""

    payload = {
        "answer": inspection_input.answer.text,
        "sources": [
            {"source_id": source.source_id, "text": source.text}
            for source in sorted(
                inspection_input.sources,
                key=lambda item: item.source_id,
            )
        ],
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def fingerprint_input(inspection_input: InspectionInput) -> InputFingerprints:
    """Build all deterministic fingerprints for an inspection input."""

    sources = tuple(
        SourceFingerprint(
            source_id=source.source_id,
            sha256=fingerprint_text(source.text),
        )
        for source in sorted(
            inspection_input.sources,
            key=lambda item: item.source_id,
        )
    )
    bundle = canonical_bundle_json(inspection_input)
    return InputFingerprints(
        answer_sha256=fingerprint_text(inspection_input.answer.text),
        sources=sources,
        canonical_bundle_sha256=hashlib.sha256(bundle.encode("utf-8")).hexdigest(),
    )


__all__ = ["canonical_bundle_json", "fingerprint_input", "fingerprint_text"]
