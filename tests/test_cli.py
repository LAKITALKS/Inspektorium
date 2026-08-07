"""CLI behavior tests, including the offline demonstration path."""

from __future__ import annotations

from pathlib import Path

import pytest

from inspektorium.cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "05_mixed_and_fabricated_quote"


def test_help_works(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", "--help"])

    assert exc_info.value.code == 0
    assert "--proposals" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("report_format", "expected_name"),
    [("json", "expected_report.json"), ("markdown", "expected_report.md")],
)
def test_offline_cli_outputs_expected_report(
    report_format: str,
    expected_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    output = tmp_path / expected_name

    status = main(
        [
            "inspect",
            "--input",
            str(EXAMPLE / "input.json"),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
            "--format",
            report_format,
            "--output",
            str(output),
        ]
    )

    assert status == 0
    assert output.read_bytes() == (EXAMPLE / expected_name).read_bytes()


def test_invalid_proposal_input_returns_nonzero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text("not json", encoding="utf-8")

    status = main(
        [
            "inspect",
            "--input",
            str(EXAMPLE / "input.json"),
            "--proposals",
            str(malformed),
        ]
    )

    assert status == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_direct_answer_and_source_files_are_supported(tmp_path: Path) -> None:
    answer = tmp_path / "answer.txt"
    source = tmp_path / "source.txt"
    proposals = tmp_path / "proposals.json"
    output = tmp_path / "report.json"
    answer.write_text("A bell rings.", encoding="utf-8")
    source.write_text("A bell rings.", encoding="utf-8")
    proposals.write_text(
        """{
  "schema_version": "0.1",
  "findings": [{
    "claim_id": "claim-1",
    "claim_text": "A bell rings.",
    "claim_start": 0,
    "claim_end": 13,
    "proposed_relation": "supported",
    "source_id": "notice",
    "evidence_quote": "A bell rings.",
    "evidence_start": 0,
    "evidence_end": 13,
    "rationale": "The notice states the claim.",
    "evidence_sufficiency": "sufficient",
    "evaluator_certainty": "high"
  }]
} """,
        encoding="utf-8",
    )

    status = main(
        [
            "inspect",
            "--answer",
            str(answer),
            "--source",
            f"notice={source}",
            "--proposals",
            str(proposals),
            "--format",
            "json",
            "--output",
            str(output),
        ]
    )

    assert status == 0
    assert '"reportable_relation": "supported"' in output.read_text(encoding="utf-8")


def test_environment_secret_is_not_rendered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_secret = "unit-test-secret-value"
    monkeypatch.setenv("ANTHROPIC_API_KEY", fake_secret)
    output = tmp_path / "report.json"

    assert (
        main(
            [
                "inspect",
                "--input",
                str(EXAMPLE / "input.json"),
                "--proposals",
                str(EXAMPLE / "proposals.json"),
                "--format",
                "json",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert fake_secret not in output.read_text(encoding="utf-8")


def test_provider_requires_explicit_model(capsys: pytest.CaptureFixture[str]) -> None:
    status = main(
        [
            "inspect",
            "--input",
            str(EXAMPLE / "input.json"),
            "--provider",
            "anthropic",
        ]
    )

    assert status == 2
    assert "--model is required" in capsys.readouterr().err
