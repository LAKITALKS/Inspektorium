"""Inspektorium entry point: full audit workflow and reference inspection."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import datetime
from importlib import import_module
from pathlib import Path

from pydantic import ValidationError

from inspektorium.core.inspection import inspect_proposals
from inspektorium.core.models import (
    AnswerInput,
    InspectionInput,
    ProposalBatch,
    SourceDocument,
)
from inspektorium.providers.base import ProviderError
from inspektorium.providers.parsing import (
    InputParseError,
    ProposalParseError,
    parse_inspection_input_json,
    parse_proposal_json,
)
from inspektorium.report import render_json, render_markdown


def run_audit(arguments: Sequence[str]) -> int:
    """Run the audit command group and preserve its exit status.

    The audit runtime is imported lazily, so ``inspektorium --help`` and
    ``inspektorium inspect`` do not load it. A missing runtime is reported with
    exit status 2; there is no fallback to the reference checker.
    """

    try:
        backend = import_module("inspektorium.audit.cli")
    except ModuleNotFoundError as exc:
        if exc.name != "inspektorium.audit" and not (exc.name or "").startswith(
            "inspektorium.audit."
        ):
            raise
        print(
            "inspektorium audit: the audit runtime is missing from this "
            "installation; reinstall the inspektorium package.",
            file=sys.stderr,
        )
        return 2

    click = import_module("click")
    try:
        result: object = backend.audit.main(
            args=list(arguments), prog_name="inspektorium audit", standalone_mode=False
        )
    except click.ClickException as exc:
        exc.show()
        return int(exc.exit_code)
    except click.Abort:
        print("Aborted!", file=sys.stderr)
        return 1
    if result is None:
        return 0
    if isinstance(result, int):
        return result
    raise TypeError("The audit runtime returned a non-integer exit status")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inspektorium",
        description="Inspektorium: audit instrument and evidence reference tool.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "audit",
        add_help=False,
        help="run the full audit workflow (use audit --help for its commands)",
    )
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="reference checker: validate proposals for one answer and render a report",
    )
    input_group = inspect_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", type=Path, help="InspectionInput JSON file")
    input_group.add_argument("--answer", type=Path, help="answer text file")
    inspect_parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="SOURCE_ID=PATH",
        help="source text file; repeat for multiple sources",
    )
    proposal_group = inspect_parser.add_mutually_exclusive_group(required=True)
    proposal_group.add_argument(
        "--proposals",
        type=Path,
        help="precomputed ProposalBatch JSON for offline inspection",
    )
    proposal_group.add_argument(
        "--provider",
        choices=("anthropic",),
        help="optional live evaluator provider",
    )
    inspect_parser.add_argument(
        "--model",
        help="Anthropic model identifier; required with --provider",
    )
    inspect_parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
    )
    inspect_parser.add_argument(
        "--output",
        type=Path,
        help="output file; omit to write to standard output",
    )
    inspect_parser.add_argument(
        "--generated-at",
        help="optional explicit ISO-8601 timestamp included in the report",
    )
    return parser


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_inspection_input(args: argparse.Namespace) -> InspectionInput:
    if args.input is not None:
        if args.source:
            raise ValueError("--source cannot be combined with --input")
        return parse_inspection_input_json(_read_text(args.input))

    if not args.source:
        raise ValueError("at least one --source SOURCE_ID=PATH is required")
    sources: list[SourceDocument] = []
    for specification in args.source:
        if "=" not in specification:
            raise ValueError("each --source must use SOURCE_ID=PATH")
        source_id, path_text = specification.split("=", 1)
        if not source_id or not path_text:
            raise ValueError("each --source must use non-empty SOURCE_ID=PATH")
        sources.append(
            SourceDocument(source_id=source_id, text=_read_text(Path(path_text)))
        )
    return InspectionInput(
        answer=AnswerInput(text=_read_text(args.answer)),
        sources=tuple(sources),
    )


def _load_proposals(
    args: argparse.Namespace, inspection_input: InspectionInput
) -> ProposalBatch:
    if args.proposals is not None:
        return parse_proposal_json(_read_text(args.proposals))
    if not args.model:
        raise ValueError("--model is required with --provider anthropic")
    from inspektorium.providers.anthropic import AnthropicProvider

    return AnthropicProvider(model=args.model).propose_findings(inspection_input)


def _parse_generated_at(value: str | None) -> datetime | None:
    if value is None:
        return None
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("--generated-at must include a timezone offset")
    return timestamp


def _write_report(rendered: str, output: Path | None) -> None:
    """Write only a fully rendered, UTF-8-encodable report.

    Encodability is checked before the output file is opened, so a late
    encoding failure cannot truncate or overwrite an existing report.
    """

    try:
        rendered.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(
            "the rendered report cannot be encoded as UTF-8; nothing was written"
        ) from exc
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.write_text(rendered, encoding="utf-8")


def _run_inspect(args: argparse.Namespace) -> int:
    # The input file and --generated-at are validated before proposals are
    # loaded or the optional provider is constructed. Nothing is rendered or
    # written until every earlier step has succeeded.
    inspection_input = _load_inspection_input(args)
    generated_at = _parse_generated_at(args.generated_at)
    proposals = _load_proposals(args, inspection_input)
    report = inspect_proposals(
        inspection_input,
        proposals,
        generated_at=generated_at,
    )
    rendered = render_json(report) if args.format == "json" else render_markdown(report)
    _write_report(rendered, args.output)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point returning a conventional process status."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments[:1] == ["audit"]:
        return run_audit(arguments[1:])
    parser = build_parser()
    args = parser.parse_args(arguments)
    try:
        if args.command == "inspect":
            return _run_inspect(args)
    except (
        FileNotFoundError,
        InputParseError,
        OSError,
        ProposalParseError,
        ProviderError,
        ValidationError,
        ValueError,
    ) as exc:
        print(f"inspektorium: error: {exc}", file=sys.stderr)
        return 2
    parser.error("unknown command")
    return 2


__all__ = ["build_parser", "main", "run_audit"]
