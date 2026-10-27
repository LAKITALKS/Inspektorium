"""Tests for Phase 6.1 confidence-validity classification.

Central guarantee: a missing/invalid confidence is NEVER treated as a real 0.0.
"""

from __future__ import annotations

import math

import pytest

from inspektorium.audit.checks.confidence_validity import (
    INVALID,
    MISSING,
    VALID,
    audit_confidences,
    classify_confidence,
    filter_valid,
    is_calibration_eligible,
)


@pytest.mark.parametrize("raw", [0.0, 0.5, 0.85, 1.0, 0, 1])
def test_valid_numeric_in_range(raw):
    assert classify_confidence(raw) == VALID
    assert is_calibration_eligible(raw)


@pytest.mark.parametrize("raw", [None, "", "   ", "\t"])
def test_missing(raw):
    assert classify_confidence(raw) == MISSING
    assert not is_calibration_eligible(raw)


@pytest.mark.parametrize("raw", [
    True, False,                # booleans are not confidences
    1.5, -0.1, 2, -1,           # out of range
    "0.85", "high", "0,85",     # stringified / non-numeric (contract requires JSON number)
    float("nan"), float("inf"), float("-inf"),
    [], {}, object(),
])
def test_invalid(raw):
    assert classify_confidence(raw) == INVALID
    assert not is_calibration_eligible(raw)


def test_missing_is_not_zero():
    """The core R-2 guard: MISSING must be distinct from a genuine 0.0."""
    assert classify_confidence(None) == MISSING
    assert classify_confidence(0.0) == VALID
    assert classify_confidence(None) != classify_confidence(0.0)


def test_nan_not_silently_used():
    assert classify_confidence(math.nan) == INVALID


def test_audit_counts_and_no_imputation():
    raws = [0.9, 0.1, None, "high", 0.0, 1.5, 0.5, ""]
    a = audit_confidences(raws)
    assert a.n_total == 8
    assert a.n_valid == 4            # 0.9, 0.1, 0.0, 0.5
    assert a.n_missing == 2          # None, ""
    assert a.n_invalid == 2          # "high", 1.5
    assert a.n_excluded == 4
    # valid values preserved exactly, excluded values NOT imputed to 0.0
    assert sorted(a.valid_values) == [0.0, 0.1, 0.5, 0.9]


def test_filter_valid():
    assert filter_valid([0.2, None, "x", 1.0, 3.0]) == [0.2, 1.0]
