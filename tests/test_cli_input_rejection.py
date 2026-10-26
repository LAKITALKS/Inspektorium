"""Ambiguous or invalid JSON is rejected at the real CLI file entry.

These tests use only entry points that already existed in v0.1.0 (``main``
with argv and files in ``tmp_path``), so they can be run unchanged against the
public baseline as a counterproof. Every provider is a fake; no network.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

import inspektorium.cli as cli
import inspektorium.providers.anthropic as anthropic_module
from inspektorium.cli import main
from inspektorium.core.inspection import inspect_proposals
from inspektorium.core.models import InspectionInput, ProposalBatch
from inspektorium.report import render_json, render_markdown

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
EXAMPLE_NAMES = (
    "01_supported",
    "02_contradicted",
    "03_not_established",
    "04_attribution_mismatch",
    "05_mixed_and_fabricated_quote",
)
EXAMPLE = EXAMPLES / "05_mixed_and_fabricated_quote"
SENTINEL = "previous report that must survive a rejected run\n"

ANSWER = (
    "Northbridge Library is open on Saturdays. It closes at 8 p.m. on weekdays. "
    "It opened in 1998."
)
SOURCE = (
    "Northbridge Library is open on Saturdays from 10 a.m. to 2 p.m. On weekdays, "
    "the library closes at 6 p.m. The source does not state when the library "
    "opened."
)
ANSWER_JSON = json.dumps(ANSWER)
SOURCE_JSON = json.dumps(SOURCE)
TITLE_JSON = json.dumps("Northbridge Library visitor guide")


def _input_document(
    *,
    top: str = "",
    answer: str = "",
    source: str = "",
    second_source: str = "",
) -> str:
    """Assemble example 05's input with optional raw JSON members spliced in."""

    sources = (
        '{"source_id": "northbridge-guide", "title": '
        f'{TITLE_JSON}, {source}"text": {SOURCE_JSON}}}'
    )
    if second_source:
        sources += (
            ', {"source_id": "second-guide", '
            f'{second_source}"text": "Another supplied source."}}'
        )
    return (
        f'{{"schema_version": "0.1", {top}"answer": {{"answer_id": "answer", '
        f'{answer}"text": {ANSWER_JSON}}}, "sources": [{sources}]}}'
    )


# Each document is accepted by v0.1.0 ("last value wins") and must now fail.
DUPLICATE_KEY_INPUTS = {
    "top_level_schema_version": _input_document(top='"schema_version": "0.1", '),
    "top_level_answer": _input_document(
        top='"answer": {"text": "A shadowed answer."}, '
    ),
    "top_level_sources": _input_document(
        top='"sources": [{"source_id": "shadowed", "text": "Shadowed."}], '
    ),
    "answer_text": _input_document(answer='"text": "A shadowed answer.", '),
    "answer_text_identical_value": _input_document(answer=f'"text": {ANSWER_JSON}, '),
    "answer_answer_id": _input_document(answer='"answer_id": "shadowed", '),
    "answer_text_after_unicode_escape": _input_document(
        answer='"\\u0074ext": "A shadowed answer.", '
    ),
    "source_text": _input_document(source='"text": "Shadowed source text.", '),
    "source_title": _input_document(source='"title": "Shadowed title", '),
    "source_source_id_escaped": _input_document(
        source='"source\\u005fid": "shadowed", '
    ),
    "second_source_title": _input_document(
        second_source='"title": "One", "title": "Two", '
    ),
}

# Each document is rejected by v0.1.0 too; the outcome must stay a clean exit 2.
OTHER_INVALID_INPUTS = {
    "lone_high_surrogate_escape": _input_document().replace(
        TITLE_JSON, '"Visitor guide \\ud800"', 1
    ),
    "lone_surrogate_in_text": _input_document().replace(
        '"text": "Northbridge', '"text": "\\udc00Northbridge', 1
    ),
    "nan_constant": _input_document(top='"extra": NaN, '),
    "infinity_constant": _input_document(top='"extra": -Infinity, '),
    "byte_order_mark": "\ufeff" + _input_document(),
    "trailing_data": _input_document() + "\n{}",
    "truncated": _input_document()[:-1],
    "deeply_nested": "[" * 100_000 + "]" * 100_000,
    "not_json": "answer: text",
    "schema_violation": _input_document(top='"unexpected": true, '),
}


def _clean_input() -> str:
    return _input_document()


@pytest.fixture
def pipeline_calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Record (and still perform) analysis and rendering steps in the CLI."""

    calls: list[str] = []

    def record(name: str, function: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            calls.append(name)
            return function(*args, **kwargs)

        return wrapper

    monkeypatch.setattr(cli, "inspect_proposals", record("analysis", inspect_proposals))
    monkeypatch.setattr(cli, "render_json", record("render_json", render_json))
    monkeypatch.setattr(
        cli, "render_markdown", record("render_markdown", render_markdown)
    )
    return calls


class _RecordingProvider:
    constructed: list[str] = []
    calls: list[str] = []

    def __init__(self, *, model: str, client: object | None = None) -> None:
        type(self).constructed.append(model)

    def propose_findings(self, inspection_input: InspectionInput) -> ProposalBatch:
        type(self).calls.append(inspection_input.answer.text)
        return ProposalBatch(findings=())


@pytest.fixture
def fake_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[type[_RecordingProvider]]:
    _RecordingProvider.constructed = []
    _RecordingProvider.calls = []
    monkeypatch.setattr(anthropic_module, "AnthropicProvider", _RecordingProvider)
    yield _RecordingProvider


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _existing_output(tmp_path: Path, name: str = "report.md") -> Path:
    return _write(tmp_path / name, SENTINEL)


def _assert_rejected(
    status: int, captured: pytest.CaptureResult[str], output: Path
) -> str:
    """Exit 2, nothing on stdout, the existing report untouched, no traceback."""

    assert status == 2
    assert captured.out == ""
    assert output.read_text(encoding="utf-8") == SENTINEL
    error = captured.err
    assert error.startswith("inspektorium: error: ")
    assert "Traceback" not in error
    return error


def _assert_one_bounded_line(error: str) -> None:
    assert error.count("\n") == 1
    assert error.endswith("\n")
    assert len(error) < 400
    assert error.isascii()


@pytest.mark.parametrize("case", sorted(DUPLICATE_KEY_INPUTS))
@pytest.mark.parametrize("report_format", ["markdown", "json"])
def test_duplicate_input_keys_exit_2_before_analysis_and_output(
    case: str,
    report_format: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    pipeline_calls: list[str],
) -> None:
    input_path = _write(tmp_path / "input.json", DUPLICATE_KEY_INPUTS[case])
    output = _existing_output(tmp_path)

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
            "--format",
            report_format,
            "--output",
            str(output),
        ]
    )

    error = _assert_rejected(status, capsys.readouterr(), output)
    assert pipeline_calls == []
    assert "Inspection input is not valid JSON: duplicate object key" in error
    _assert_one_bounded_line(error)


@pytest.mark.parametrize("case", sorted(DUPLICATE_KEY_INPUTS))
def test_duplicate_input_keys_never_reach_stdout(
    case: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    pipeline_calls: list[str],
) -> None:
    input_path = _write(tmp_path / "input.json", DUPLICATE_KEY_INPUTS[case])

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
        ]
    )

    captured = capsys.readouterr()
    assert status == 2
    assert captured.out == ""
    assert pipeline_calls == []
    assert "duplicate object key" in captured.err


@pytest.mark.parametrize(
    "case", sorted(DUPLICATE_KEY_INPUTS) + sorted(OTHER_INVALID_INPUTS)
)
def test_rejected_input_never_constructs_or_calls_the_provider(
    case: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    fake_provider: type[_RecordingProvider],
    pipeline_calls: list[str],
) -> None:
    raw = {**DUPLICATE_KEY_INPUTS, **OTHER_INVALID_INPUTS}[case]
    input_path = _write(tmp_path / "input.json", raw)
    output = _existing_output(tmp_path)

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--provider",
            "anthropic",
            "--model",
            "test-model",
            "--output",
            str(output),
        ]
    )

    assert fake_provider.constructed == []
    assert fake_provider.calls == []
    assert pipeline_calls == []
    _assert_rejected(status, capsys.readouterr(), output)


def test_invalid_generated_at_is_rejected_before_the_provider_is_built(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    fake_provider: type[_RecordingProvider],
) -> None:
    input_path = _write(tmp_path / "input.json", _clean_input())
    output = _existing_output(tmp_path)

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--provider",
            "anthropic",
            "--model",
            "test-model",
            "--generated-at",
            "2026-10-13T12:00:00",
            "--output",
            str(output),
        ]
    )

    assert fake_provider.constructed == []
    error = _assert_rejected(status, capsys.readouterr(), output)
    assert "--generated-at must include a timezone offset" in error


def test_clean_input_still_reaches_the_fake_provider(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    fake_provider: type[_RecordingProvider],
) -> None:
    input_path = _write(tmp_path / "input.json", _clean_input())

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--provider",
            "anthropic",
            "--model",
            "test-model",
            "--format",
            "json",
        ]
    )

    assert status == 0
    assert fake_provider.constructed == ["test-model"]
    assert fake_provider.calls == [ANSWER]
    assert json.loads(capsys.readouterr().out)["summary"]["claims_inspected"] == 0


@pytest.mark.parametrize("case", sorted(OTHER_INVALID_INPUTS))
def test_other_invalid_input_exits_2_without_touching_output(
    case: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    pipeline_calls: list[str],
) -> None:
    input_path = _write(tmp_path / "input.json", OTHER_INVALID_INPUTS[case])
    output = _existing_output(tmp_path)

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
            "--output",
            str(output),
        ]
    )

    _assert_rejected(status, capsys.readouterr(), output)
    assert pipeline_calls == []


def _proposals_with(replacement: tuple[str, str]) -> str:
    raw = (EXAMPLE / "proposals.json").read_text(encoding="utf-8")
    old, new = replacement
    assert old in raw
    return raw.replace(old, new, 1)


INVALID_PROPOSALS = {
    "duplicate_rationale": ('"rationale": ', '"rationale": "shadowed", "rationale": '),
    "duplicate_offset_after_escape": (
        '"claim_start": ',
        '"claim\\u005fstart": 999, "claim_start": ',
    ),
    "lone_surrogate_rationale": ('"rationale": "', '"rationale": "\\ud800'),
    "nan_offset": ('"claim_start": 0', '"claim_start": NaN'),
    "deeply_nested": ('"findings": [', '"findings": [' + "[" * 100_000),
}


@pytest.mark.parametrize("case", sorted(INVALID_PROPOSALS))
def test_rejected_proposals_exit_2_without_touching_output(
    case: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    pipeline_calls: list[str],
) -> None:
    proposals = _write(
        tmp_path / "proposals.json", _proposals_with(INVALID_PROPOSALS[case])
    )
    output = _existing_output(tmp_path)

    status = main(
        [
            "inspect",
            "--input",
            str(EXAMPLE / "input.json"),
            "--proposals",
            str(proposals),
            "--output",
            str(output),
        ]
    )

    error = _assert_rejected(status, capsys.readouterr(), output)
    assert pipeline_calls == []
    assert "malformed_proposal" in error


@pytest.mark.parametrize("report_format", ["markdown", "json"])
def test_late_encoding_failure_leaves_existing_output_intact(
    report_format: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unencodable(report: object) -> str:
        return "report with an unpaired surrogate \ud800\n"

    monkeypatch.setattr(cli, "render_json", unencodable)
    monkeypatch.setattr(cli, "render_markdown", unencodable)
    output = _existing_output(tmp_path)

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

    error = _assert_rejected(status, capsys.readouterr(), output)
    assert "cannot be encoded as UTF-8" in error


def test_late_encoding_failure_writes_nothing_to_stdout(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "render_markdown", lambda report: "partial \udfff\n")

    status = main(
        [
            "inspect",
            "--input",
            str(EXAMPLE / "input.json"),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
        ]
    )

    captured = capsys.readouterr()
    assert status == 2
    assert captured.out == ""
    assert "cannot be encoded as UTF-8" in captured.err


def test_error_message_is_bounded_and_escapes_untrusted_keys(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    long_key = "\\u001b[31m\\u202e" + "k" * 20_000
    raw = _input_document(top=f'"{long_key}": 1, "{long_key}": 2, ')
    input_path = _write(tmp_path / "input.json", raw)
    output = _existing_output(tmp_path)

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
            "--output",
            str(output),
        ]
    )

    error = _assert_rejected(status, capsys.readouterr(), output)
    _assert_one_bounded_line(error)
    assert "\x1b" not in error
    assert "\\x1b[31m\\u202ekkk" in error


def test_schema_errors_do_not_echo_input_values(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    marker = "UNTRUSTED-VALUE-MARKER"
    raw = _input_document(top=f'"unexpected": "{marker}{"x" * 5_000}", ')
    input_path = _write(tmp_path / "input.json", raw)
    output = _existing_output(tmp_path)

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
            "--output",
            str(output),
        ]
    )

    error = _assert_rejected(status, capsys.readouterr(), output)
    _assert_one_bounded_line(error)
    assert marker not in error
    assert "unexpected: Extra inputs are not permitted" in error


@pytest.mark.parametrize(
    "case", sorted(DUPLICATE_KEY_INPUTS) + sorted(OTHER_INVALID_INPUTS)
)
def test_input_rejection_message_is_one_bounded_ascii_line(
    case: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    raw = {**DUPLICATE_KEY_INPUTS, **OTHER_INVALID_INPUTS}[case]
    input_path = _write(tmp_path / "input.json", raw)

    status = main(
        [
            "inspect",
            "--input",
            str(input_path),
            "--proposals",
            str(EXAMPLE / "proposals.json"),
        ]
    )

    captured = capsys.readouterr()
    assert status == 2
    assert captured.err.startswith("inspektorium: error: Inspection input ")
    _assert_one_bounded_line(captured.err)


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
@pytest.mark.parametrize("report_format", ["json", "markdown"])
def test_clean_examples_produce_unchanged_reports_through_the_cli(
    example_name: str,
    report_format: str,
    tmp_path: Path,
) -> None:
    directory = EXAMPLES / example_name
    raw_input = (directory / "input.json").read_text(encoding="utf-8")
    raw_proposals = (directory / "proposals.json").read_text(encoding="utf-8")
    output = _existing_output(tmp_path, f"report.{report_format}")

    status = main(
        [
            "inspect",
            "--input",
            str(directory / "input.json"),
            "--proposals",
            str(directory / "proposals.json"),
            "--format",
            report_format,
            "--output",
            str(output),
        ]
    )

    # Reference: the v0.1.0 loading path (pydantic JSON mode for the input,
    # plain json.loads plus schema validation for the proposals).
    reference = inspect_proposals(
        InspectionInput.model_validate_json(raw_input),
        ProposalBatch.model_validate(json.loads(raw_proposals)),
    )
    renderer = render_json if report_format == "json" else render_markdown
    expected = renderer(reference)
    assert status == 0
    assert output.read_bytes() == expected.encode("utf-8")
    if report_format == "json":
        assert output.read_bytes() == (directory / "expected_report.json").read_bytes()
