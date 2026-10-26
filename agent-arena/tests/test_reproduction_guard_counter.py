"""Counter verification rejects missing or fabricated zero-count logs."""

import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "reproduction", Path(__file__).resolve().parents[1] / "scripts/phase10_clean_reproduce.py"
)
REPRO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPRO)


def _check():
    return {
        "armed": True,
        "loopback_positive_control": "connected",
        **{str(i): "refused_by_guard" for i in range(5)},
    }


def test_exact_refusal_counters_and_loopback_pass():
    records = [{"event": "armed"}] + [{"event": "refused"}] * 5
    assert REPRO.guard_countercheck_valid(_check(), records)


def test_missing_zero_or_extra_counters_fail():
    for records in (
        [],
        [{"event": "armed"}],
        [{"event": "refused"}] * 5,
        [{"event": "armed"}] + [{"event": "refused"}] * 6,
    ):
        assert not REPRO.guard_countercheck_valid(_check(), records)
    bad = _check()
    bad["loopback_positive_control"] = "failed"
    assert not REPRO.guard_countercheck_valid(
        bad, [{"event": "armed"}] + [{"event": "refused"}] * 5
    )
