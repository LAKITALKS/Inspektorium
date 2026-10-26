"""Process-exit contract for the public Phase-7A preflight CLIs.

All preflight results and providers are controlled sentinels.  The one subprocess test invokes
the actual module entrypoint but makes no provider or model call.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from agent_arena import phase7a_execution as p7
from agent_arena import phase7a_real_run as rr
from agent_arena import preflight_integrity as pi


REPO_ROOT = Path(__file__).resolve().parents[1]


def _preflight(
    *,
    go: bool | None,
    qa_status: str,
    gate_passes: bool = True,
    gate_errors: list[str] | None = None,
) -> dict:
    return {
        "go": go,
        "production_authorizing": True,
        "gate_passes": gate_passes,
        "gate_errors": gate_errors or [],
        "qa_status": qa_status,
        "qa_errors": [],
        "qa": None,
        "qa_record_fingerprint": None,
        "source_binding": {},
        "post_qa_source": {},
    }


def test_preflight_cli_go_maps_to_exit_zero(monkeypatch, capsys):
    monkeypatch.setattr(
        p7, "real_run_preflight", lambda: _preflight(go=True, qa_status=pi.QA_PASSED)
    )

    assert p7.main(["--preflight"]) == 0
    assert "real-run preflight: GO" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("qa_status", "gate_passes", "gate_errors"),
    [
        (pi.QA_COULD_NOT_EXECUTE, True, []),
        (pi.QA_FAILED, True, []),
        (pi.QA_NOT_EXECUTED, False, ["required artifact missing"]),
        (pi.QA_NOT_EXECUTED, False, ["source binding mismatch"]),
    ],
)
def test_preflight_cli_controlled_no_go_is_nonzero_without_provider_construction(
    monkeypatch, capsys, qa_status, gate_passes, gate_errors
):
    provider_constructions = 0

    def forbidden_provider(*_args, **_kwargs):
        nonlocal provider_constructions
        provider_constructions += 1
        raise AssertionError("preflight NO-GO must not construct a provider")

    monkeypatch.setattr(p7, "FakeLibraryProvider", forbidden_provider)
    monkeypatch.setattr(
        p7,
        "real_run_preflight",
        lambda: _preflight(
            go=False,
            qa_status=qa_status,
            gate_passes=gate_passes,
            gate_errors=gate_errors,
        ),
    )

    assert p7.main(["--preflight"]) != 0
    assert "real-run preflight: NO-GO" in capsys.readouterr().out
    assert provider_constructions == 0


@pytest.mark.parametrize("go_value", [None, "yes", 1])
def test_preflight_cli_malformed_go_state_cannot_map_to_success(
    monkeypatch, capsys, go_value
):
    monkeypatch.setattr(
        p7,
        "real_run_preflight",
        lambda: _preflight(go=go_value, qa_status=pi.QA_PASSED),
    )

    assert p7.main(["--preflight"]) != 0
    assert "real-run preflight: NO-GO" in capsys.readouterr().out


def test_preflight_cli_missing_go_state_cannot_map_to_success(monkeypatch, capsys):
    result = _preflight(go=False, qa_status=pi.QA_PASSED)
    result.pop("go")
    monkeypatch.setattr(p7, "real_run_preflight", lambda: result)

    assert p7.main(["--preflight"]) != 0
    assert "real-run preflight: NO-GO" in capsys.readouterr().out


def test_preflight_no_go_is_not_overwritten_by_later_informational_action(
    monkeypatch, capsys
):
    monkeypatch.setattr(
        p7,
        "real_run_preflight",
        lambda: _preflight(go=False, qa_status=pi.QA_FAILED),
    )
    monkeypatch.setattr(
        p7,
        "verify_pre_run",
        lambda: {
            "passes": True,
            "n_evaluated_units": 84,
            "n_independent_bases": 34,
            "n_perturbation_variants": 50,
            "n_perturbation_clusters": 10,
            "planned_analytical_calls": 840,
            "errors": [],
        },
    )

    assert p7.main(["--preflight", "--verify"]) != 0
    output = capsys.readouterr().out
    assert "pre-run gate: PASS" in output
    assert "real-run preflight: NO-GO" in output


def test_real_run_credential_no_go_is_nonzero_without_provider_construction(
    monkeypatch, capsys
):
    provider_constructions = 0

    def forbidden_provider(_model_key):
        nonlocal provider_constructions
        provider_constructions += 1
        raise AssertionError("credential NO-GO must not construct a provider")

    monkeypatch.setattr(
        rr.p7,
        "real_run_preflight",
        lambda _root: _preflight(go=True, qa_status=pi.QA_PASSED),
    )
    monkeypatch.setattr(
        rr,
        "check_provider_availability",
        lambda *, probe=False: {
            "available": False,
            "reason": "credential_missing",
            "probe": probe,
        },
    )
    monkeypatch.setattr(rr, "provider_factory_for", forbidden_provider)

    assert rr.main(["--preflight"]) != 0
    assert "credential=credential_missing" in capsys.readouterr().out
    assert provider_constructions == 0


def test_actual_phase7a_execution_module_exit_matches_displayed_preflight_result():
    env = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS", "PYTEST_PLUGINS"):
        env.pop(name, None)
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", TERM="dumb")

    result = subprocess.run(
        [sys.executable, "-m", "agent_arena.phase7a_execution", "--preflight"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    if "real-run preflight: GO" in result.stdout:
        assert result.returncode == 0
    else:
        assert "real-run preflight: NO-GO" in result.stdout
        assert result.returncode != 0
