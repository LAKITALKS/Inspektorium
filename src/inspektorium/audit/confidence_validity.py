"""Deterministic confidence-validity classification (Phase 6.1).

Enforces the frozen confidence semantics (`analysis/phase6_1_confidence_protocol/
confidence_semantics.md`): a raw model confidence is classified as VALID, MISSING,
or INVALID, and **missing/invalid confidence is never silently coerced to 0.0**
(risk R-2). Only VALID confidences enter calibration; MISSING/INVALID are counted
and reported as explicit exclusions.

Confidence is a real number on the closed interval [0.0, 1.0]. This module is
pool-independent and makes no model calls.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, field

VALID = "VALID"
MISSING = "MISSING"
INVALID = "INVALID"

CONFIDENCE_MIN = 0.0
CONFIDENCE_MAX = 1.0


def classify_confidence(raw: object) -> str:
    """Classify a raw confidence value into VALID / MISSING / INVALID.

    - MISSING: ``None`` or an empty/whitespace string (no value emitted).
    - VALID: a finite, non-boolean ``int``/``float`` within [0.0, 1.0].
    - INVALID: everything else — booleans, NaN/Inf, out-of-range numbers, and
      non-numeric or numeric-*string* values (the output contract requires a JSON
      number, so a stringified confidence is a contract violation, not a datum).

    A genuine ``0.0`` is VALID and must remain distinct from MISSING/INVALID — the
    whole point of this function is that a dropped/garbled confidence can never
    masquerade as a real minimal-confidence report.
    """
    if raw is None:
        return MISSING
    if isinstance(raw, str):
        return MISSING if raw.strip() == "" else INVALID
    if isinstance(raw, bool):
        return INVALID
    if isinstance(raw, (int, float)):
        v = float(raw)
        if not math.isfinite(v):
            return INVALID
        if CONFIDENCE_MIN <= v <= CONFIDENCE_MAX:
            return VALID
        return INVALID
    return INVALID


def is_calibration_eligible(raw: object) -> bool:
    """True iff the raw confidence is VALID (usable in calibration)."""
    return classify_confidence(raw) == VALID


def confidence_value_if_valid(raw: object, state: object) -> float | None:
    """Return a numeric confidence only when value *and* stored state agree.

    Stored analytical consumers must not reconstruct validity from the numeric
    field alone.  A malformed/unknown state, or a ``VALID`` state paired with an
    invalid value, therefore fails closed to ``None``.
    """
    if state != VALID or classify_confidence(raw) != VALID:
        return None
    return float(raw)


@dataclass
class ConfidenceAudit:
    n_total: int = 0
    n_valid: int = 0
    n_missing: int = 0
    n_invalid: int = 0
    valid_values: list[float] = field(default_factory=list)

    @property
    def n_excluded(self) -> int:
        return self.n_missing + self.n_invalid

    def as_dict(self) -> dict:
        return {
            "n_total": self.n_total,
            "n_valid": self.n_valid,
            "n_missing": self.n_missing,
            "n_invalid": self.n_invalid,
            "n_excluded": self.n_excluded,
        }


def audit_confidences(raw_values: Iterable[object]) -> ConfidenceAudit:
    """Classify a batch of raw confidences and tally valid/missing/invalid.

    Never imputes: excluded values are counted, valid values are collected as floats.
    """
    audit = ConfidenceAudit()
    for raw in raw_values:
        audit.n_total += 1
        state = classify_confidence(raw)
        if state == VALID:
            audit.n_valid += 1
            audit.valid_values.append(float(raw))
        elif state == MISSING:
            audit.n_missing += 1
        else:
            audit.n_invalid += 1
    return audit


def filter_valid(raw_values: Iterable[object]) -> list[float]:
    """Return only the VALID confidences, as floats (no imputation)."""
    return [float(v) for v in raw_values if is_calibration_eligible(v)]
