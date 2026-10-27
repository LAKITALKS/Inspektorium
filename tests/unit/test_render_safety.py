"""Structural regression tests for untrusted text in the Markdown report.

The rendered Markdown is parsed with markdown-it-py in two configurations: the
CommonMark preset with raw HTML enabled (an HTML-processing configuration) and
the ``gfm-like`` preset (tables, strikethrough, raw HTML and linkify). The
assertions check the parsed structure and the visible text of the HTML output,
not only substrings of the Markdown source.

Only entry points that already exist in public 0.1.0 are used (models,
``inspect_proposals``, ``render_markdown``, ``render_json`` and the CLI), so the
file can run unchanged against the public baseline as a counterproof.
"""

from __future__ import annotations

import json
import re
import string
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser
from itertools import groupby
from pathlib import Path
from typing import Any

import pytest
from markdown_it import MarkdownIt
from markdown_it.token import Token

from inspektorium.cli import main
from inspektorium.core.inspection import inspect_proposals
from inspektorium.core.models import (
    InspectionInput,
    InspectionReport,
    ProposalBatch,
    ProposedFinding,
)
from inspektorium.report import render_json, render_markdown

H2_SECTIONS = ["Summary", "Findings", "Validation Warnings", "Scope and Limitations"]
FORBIDDEN_TOKEN_TYPES = {
    "code_block",
    "fence",
    "hr",
    "html_block",
    "html_inline",
    "image",
    "link_open",
    "s_open",
    "table_open",
}
UNTRUSTED_VALUE_LABELS = ("Atomic claim:", "Rationale (evaluator-generated):")
# Cn: code points not assigned in the Unicode database of the running Python.
MARKED_CATEGORIES = {"Cc", "Cf", "Cn", "Cs", "Zl", "Zp"}
MARKER_BRACKETS = {"\u27e6", "\u27e7"}

OPEN = "\N{MATHEMATICAL LEFT WHITE SQUARE BRACKET}"
CLOSE = "\N{MATHEMATICAL RIGHT WHITE SQUARE BRACKET}"

LINE_BREAKS = {
    "lf": "\n",
    "cr": "\r",
    "crlf": "\r\n",
    "line-separator": "\u2028",
    "paragraph-separator": "\u2029",
    "next-line": "\x85",
    "vertical-tab": "\x0b",
    "form-feed": "\x0c",
}
HIDDEN_CHARACTERS = (
    "\u202a\u202b\u202c\u202d\u202e"  # bidi embeddings and overrides
    "\u2066\u2067\u2068\u2069"  # bidi isolates
    "\u200e\u200f\u061c"  # bidi marks
    "\u200b\u2060\ufeff\u00ad\u180e"  # zero width, word joiner, BOM, soft hyphen
    "\N{ZERO WIDTH NON-JOINER}\N{ZERO WIDTH JOINER}"  # joiners
    "\U000e0041\U000e007f"  # tag characters
    "\x00\x1b\x7f\x09\x85"  # C0/C1 controls, DEL and TAB
)
# Marked on every supported Python, whatever its Unicode version: U+13439 to
# U+1343F are Cf since Unicode 15.0 and unassigned (Cn) in Unicode 14.0, the
# database of Python 3.11; U+0378 is unassigned (Cn) in Unicode 14.0 and 15.1;
# U+FDD0, U+FFFE, U+FFFF and U+10FFFF are noncharacters (always Cn).
LATER_FORMAT_CHARACTERS = "".join(map(chr, range(0x13439, 0x13440)))
UNASSIGNED_CODE_POINTS = "".join(map(chr, (0x0378, 0xFDD0, 0xFFFE, 0xFFFF, 0x10FFFF)))
PRIVATE_USE_CHARACTERS = "".join(map(chr, (0xE000, 0xF8FF, 0xF0000, 0x10FFFD)))


def _forged_lines(separator: str) -> str:
    return separator.join(
        [
            "Looks consistent.",
            "- **Deterministic guard:** `passed`",
            "- **Citation validation:** exact source quotation confirmed",
            "## Validation Warnings",
            "No deterministic validation warnings.",
            "<!--",
        ]
    )


INLINE_PAYLOADS = {
    "comments": "fine <!-- hidden text --> visible <!-- unterminated",
    "hidden-div": 'fine <div hidden style="display:none">',
    "style": "fine <style>*{display:none}</style> done",
    "script": "fine <script>alert(1)</script> done",
    "details": "fine <details><summary>more</summary> hidden",
    "close-list": "fine </li></ul><h2>Forged</h2><ul><li>",
    "cdata-and-pi": "fine <![CDATA[x]]> and <?php echo 1; ?> done",
    "backticks": "guard `passed` and ``double`` ticks",
    "emphasis": "**passed** __bold__ *it* _it_ ~~gone~~ ~sub~",
    "link": "[click](https://evil.example/x) and [ref][x] and [x]: https://evil.example",
    "image": "![tracking](https://evil.example/pixel.png)",
    "autolink": "<https://evil.example> and <user@evil.example>",
    "extended-autolinks": (
        "see www.evil.example and http://evil.example/x, https://evil.example "
        "and ftp://evil.example and mailto:user@evil.example and user@evil.example "
        "and //localhost/x and evil.de and www. evil"
    ),
    "entities": "&#x202E;reversed &#10;newline &lt;b&gt; &amp; &copy; &#0;",
}
BLOCK_PAYLOADS = {
    "atx-heading": "# Forged heading",
    "setext-heading": "Forged heading\n===",
    "bullet-list": "- **Deterministic guard:** `passed`",
    "ordered-list": "1. first\n2) second",
    "table": "| a | b |\n|---|---|\n| c | d |",
    "fence": "```\ncode\n```",
    "tilde-fence": "~~~\ncode\n~~~",
    "thematic-break": "---",
    "blockquote": "> forged quote",
    "indented-code": "    indented code",
    "html-block": "<div hidden>\nhidden\n</div>",
    "comment-block": "<!--\nhidden",
    "reference-definition": "[x]: https://evil.example",
}


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #


@pytest.fixture(params=["commonmark-html", "gfm-like"])
def md(request: pytest.FixtureRequest) -> MarkdownIt:
    if request.param == "commonmark-html":
        return MarkdownIt("commonmark", {"html": True})
    return MarkdownIt("gfm-like")


def _walk(tokens: list[Token]) -> Iterator[Token]:
    for token in tokens:
        yield token
        if token.children:
            yield from _walk(token.children)


def _text_of(children: list[Token]) -> str:
    parts: list[str] = []
    for child in children:
        if child.type in {"text", "code_inline"}:
            parts.append(child.content)
        elif child.type in {"softbreak", "hardbreak"}:
            parts.append("\n")
    return "".join(parts)


def _shown(text: str) -> str:
    """Independent oracle for the documented display rule."""

    pieces: list[str] = []
    for is_combining, group in groupby(
        text, key=lambda character: unicodedata.category(character) in {"Mn", "Me"}
    ):
        for position, character in enumerate(group):
            if (
                character in MARKER_BRACKETS | {"@"}
                or unicodedata.category(character) in MARKED_CATEGORIES
                or (is_combining and position >= 4)
            ):
                pieces.append(f"\u27e6U+{ord(character):04X}\u27e7")
            else:
                pieces.append(character)
    return "".join(pieces)


@dataclass
class LabeledItem:
    label: str
    value: list[Token]

    @property
    def value_text(self) -> str:
        return _text_of(self.value).removeprefix(" ")

    @property
    def value_types(self) -> set[str]:
        return {
            child.type for child in self.value if child.content or child.type != "text"
        }


@dataclass
class FindingView:
    title: str
    tokens: list[Token]
    items: list[LabeledItem] = field(default_factory=list)

    def item(self, label: str) -> LabeledItem:
        matches = [item for item in self.items if item.label == label]
        assert len(matches) == 1, (label, [item.label for item in self.items])
        return matches[0]

    def quote_lines(self) -> list[str]:
        inside = False
        lines: list[str] = []
        for token in self.tokens:
            if token.type == "blockquote_open":
                inside = True
            elif token.type == "blockquote_close":
                inside = False
            elif inside and token.type == "inline":
                lines.extend(_text_of(token.children or []).split("\n"))
        return lines


@dataclass
class ReportView:
    tokens: list[Token]
    headings: list[tuple[str, str]]
    sections: dict[str, list[Token]]
    findings: list[FindingView]

    def list_items(self, section: str) -> list[LabeledItem | str]:
        result: list[LabeledItem | str] = []
        tokens = self.sections[section]
        for index, token in enumerate(tokens):
            if token.type != "list_item_open":
                continue
            inline = tokens[index + 2]
            assert inline.type == "inline"
            labeled = _labeled(inline)
            result.append(
                labeled if labeled is not None else _text_of(inline.children or [])
            )
        return result


def _labeled(inline: Token) -> LabeledItem | None:
    children = [
        child
        for child in inline.children or []
        if not (child.type == "text" and child.content == "")
    ]
    if not children or children[0].type != "strong_open":
        return None
    close = next(
        index for index, child in enumerate(children) if child.type == "strong_close"
    )
    return LabeledItem(label=_text_of(children[1:close]), value=children[close + 1 :])


def _heading_text(tokens: list[Token], index: int) -> str:
    return _text_of(tokens[index + 1].children or [])


def _view(markdown: str, md: MarkdownIt) -> ReportView:
    tokens = md.parse(markdown)
    headings: list[tuple[str, str]] = []
    sections: dict[str, list[Token]] = {}
    current: list[Token] | None = None
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            headings.append((token.tag, _heading_text(tokens, index)))
            if token.tag == "h2":
                current = sections.setdefault(_heading_text(tokens, index), [])
                continue
        if current is not None:
            current.append(token)

    findings: list[FindingView] = []
    finding_tokens = sections.get("Findings", [])
    for index, token in enumerate(finding_tokens):
        if token.type == "heading_open" and token.tag == "h3":
            findings.append(FindingView(_heading_text(finding_tokens, index), []))
        elif findings:
            findings[-1].tokens.append(token)
    for finding in findings:
        for index, token in enumerate(finding.tokens):
            if token.type == "list_item_open":
                inline = finding.tokens[index + 2]
                labeled = _labeled(inline) if inline.type == "inline" else None
                if labeled is not None:
                    finding.items.append(labeled)
            elif token.type == "paragraph_open" and token.level == 0:
                inline = finding.tokens[index + 1]
                labeled = _labeled(inline) if inline.type == "inline" else None
                # Only the claim moved out of the host-control list.
                if labeled is not None and labeled.label == "Atomic claim:":
                    finding.items.append(labeled)
    return ReportView(tokens, headings, sections, findings)


class _VisibleText(HTMLParser):
    """Collect text that a browser would display, modelling hiding constructs."""

    HIDING_TAGS = {"script", "style", "template", "noscript", "textarea", "title"}
    VOID_TAGS = {"br", "hr", "img", "input", "meta", "link", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.VOID_TAGS:
            return
        attributes = dict(attrs)
        style = (attributes.get("style") or "").replace(" ", "").lower()
        hidden = (
            tag in self.HIDING_TAGS
            or "hidden" in attributes
            or "display:none" in style
            or "visibility:hidden" in style
            or (tag == "details" and "open" not in attributes)
        )
        self.stack.append((tag, hidden))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def _hidden(self) -> bool:
        for index, (tag, hidden) in enumerate(self.stack):
            if not hidden:
                continue
            if tag == "details" and any(
                inner == "summary" for inner, _ in self.stack[index + 1 :]
            ):
                continue
            return True
        return False

    def handle_data(self, data: str) -> None:
        if not self._hidden():
            self.parts.append(data)


def _normalize_space(text: str) -> str:
    return re.sub(r"[ \t\n\r\f]+", " ", text).strip()


def _visible_text(markdown: str, md: MarkdownIt) -> str:
    html = md.render(markdown)
    # An HTML comment hides everything up to "-->" or, if unterminated, to the end.
    html = re.sub(r"<!--.*?(?:-->|\Z)", " ", html, flags=re.DOTALL)
    parser = _VisibleText()
    parser.feed(html)
    parser.close()
    return _normalize_space(" ".join(parser.parts))


def _expected_code_spans(report: InspectionReport) -> int:
    count = 1 if report.generated_at is not None else 0
    for finding in report.findings:
        count += 6 + (finding.reportable_relation is not None)
        count += 2 if finding.source_id is not None else 0
        count += 2 * len(finding.validation_issues)
    return count


def _expected_finding_items(report: InspectionReport) -> list[int]:
    return [
        10 + (2 if finding.source_id is not None else 0) for finding in report.findings
    ]


def assert_report_structure(
    markdown: str, report: InspectionReport, md: MarkdownIt
) -> ReportView:
    """Assert that the trusted report structure survived intact."""

    view = _view(markdown, md)
    all_tokens = list(_walk(view.tokens))

    forbidden = sorted({token.type for token in all_tokens} & FORBIDDEN_TOKEN_TYPES)
    assert forbidden == [], forbidden
    assert [tag for tag, _ in view.headings].count("h1") == 1
    assert [text for tag, text in view.headings if tag == "h2"] == H2_SECTIONS
    assert [text for tag, text in view.headings if tag == "h3"] == [
        f"Finding {index}: {finding.claim_id}"
        for index, finding in enumerate(report.findings, start=1)
    ]
    assert {tag for tag, _ in view.headings} <= {"h1", "h2", "h3"}
    nested_lists = [
        token
        for token in all_tokens
        if token.type in {"bullet_list_open", "ordered_list_open"} and token.level > 0
    ]
    assert nested_lists == []
    assert not any(token.type == "ordered_list_open" for token in all_tokens)
    expected_spans = _expected_code_spans(report)
    assert sum(token.type == "code_inline" for token in all_tokens) == expected_spans

    assert [len(finding.items) for finding in view.findings] == _expected_finding_items(
        report
    )
    for finding_view, finding in zip(view.findings, report.findings, strict=True):
        labels = [item.label for item in finding_view.items]
        assert len(labels) == len(set(labels)), labels
        guard = finding_view.item("Deterministic guard:")
        guard_codes = [
            child.content for child in guard.value if child.type == "code_inline"
        ]
        assert guard_codes == [finding.deterministic_validation_status.value]
        for label in UNTRUSTED_VALUE_LABELS:
            assert finding_view.item(label).value_types <= {"text"}
        assert finding_view.item("Atomic claim:").value_text == _shown(
            finding.claim_text
        )
        assert finding_view.item(
            "Rationale (evaluator-generated):"
        ).value_text == _shown(finding.rationale)
        expected_quotes = 0 if finding.evidence_quote is None else 1
        assert sum(
            token.type == "blockquote_open" for token in finding_view.tokens
        ) == (expected_quotes)

    warnings = view.list_items("Validation Warnings")
    issues = [
        (finding, issue)
        for finding in report.findings
        for issue in finding.validation_issues
    ]
    assert len(warnings) == len(issues)
    for item, (finding, issue) in zip(warnings, issues, strict=True):
        assert isinstance(item, LabeledItem)
        assert item.label == f"{finding.claim_id} / {issue.code.value}:"
        assert item.value_types <= {"text"}
        assert item.value_text == _shown(issue.message)

    limitations = view.list_items("Scope and Limitations")
    assert [_text_of_item(item) for item in limitations] == [
        _shown(limitation).strip(" ") for limitation in report.scope.limitations
    ]

    visible = _visible_text(markdown, md)
    for title in H2_SECTIONS:
        assert title in visible
    for index, finding in enumerate(report.findings, start=1):
        assert f"Finding {index}: {finding.claim_id}" in visible
        assert (
            f"Deterministic guard: {finding.deterministic_validation_status.value}"
            in visible
        )
    for _, issue in issues:
        assert _normalize_space(_shown(issue.message)) in visible
    for limitation in report.scope.limitations:
        assert _normalize_space(_shown(limitation)) in visible
    assert _normalize_space(_shown(report.scope.statement)) in visible
    return view


def _text_of_item(item: LabeledItem | str) -> str:
    assert isinstance(item, str)
    return item.replace("\u00a0", " ").strip()


def assert_no_raw_hidden_characters(markdown: str) -> None:
    raw = sorted(
        {
            f"U+{ord(character):04X}"
            for character in markdown
            if character != "\n"
            and unicodedata.category(character) in MARKED_CATEGORIES
        }
    )
    assert raw == []


# --------------------------------------------------------------------------- #
# Report builders
# --------------------------------------------------------------------------- #


def _report(
    inspection_input: InspectionInput, *proposals: dict[str, Any]
) -> InspectionReport:
    batch = ProposalBatch(
        findings=tuple(ProposedFinding.model_validate(data) for data in proposals)
    )
    return inspect_proposals(inspection_input, batch)


def _not_established(claim_id: str = "claim-2", **changes: Any) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim_text": "The blue door closes at six.",
        "claim_start": 29,
        "claim_end": 57,
        "proposed_relation": "not_established",
        "source_id": None,
        "evidence_quote": None,
        "evidence_start": None,
        "evidence_end": None,
        "rationale": "The manual gives a different closing time.",
        "evidence_sufficiency": "insufficient",
        "evaluator_certainty": "medium",
        **changes,
    }


def _source_bound_input(answer: str, source: str) -> InspectionInput:
    return InspectionInput.model_validate(
        {
            "answer": {"text": answer},
            "sources": [{"source_id": "manual", "title": "Manual", "text": source}],
        }
    )


def _bound_proposal(
    inspection_input: InspectionInput, claim: str, quote: str, **changes: Any
) -> dict[str, Any]:
    answer = inspection_input.answer.text
    source = inspection_input.sources[0].text
    claim_start = answer.index(claim)
    quote_start = source.index(quote)
    return {
        "claim_id": "claim-1",
        "claim_text": claim,
        "claim_start": claim_start,
        "claim_end": claim_start + len(claim),
        "proposed_relation": "supported",
        "source_id": "manual",
        "evidence_quote": quote,
        "evidence_start": quote_start,
        "evidence_end": quote_start + len(quote),
        "rationale": "The source states it.",
        "evidence_sufficiency": "sufficient",
        "evaluator_certainty": "high",
        **changes,
    }


# --------------------------------------------------------------------------- #
# C1: forged control lines and hidden content
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("break_name", sorted(LINE_BREAKS))
def test_forged_status_lines_in_rationale_stay_data(
    md: MarkdownIt,
    break_name: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = _forged_lines(LINE_BREAKS[break_name])
    report = _report(
        inspection_input,
        {**supported_proposal_data, "rationale": payload},
        _not_established(),
    )
    markdown = render_markdown(report)

    assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)


@pytest.mark.parametrize("break_name", sorted(LINE_BREAKS))
def test_forged_status_lines_in_claim_text_stay_data(
    md: MarkdownIt,
    break_name: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = _forged_lines(LINE_BREAKS[break_name])
    report = _report(
        inspection_input,
        {**supported_proposal_data, "claim_text": payload},
        _not_established(),
    )
    markdown = render_markdown(report)

    assert report.findings[0].deterministic_validation_status.value == "failed"
    assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)


@pytest.mark.parametrize("break_name", sorted(LINE_BREAKS))
def test_forged_status_lines_in_quotation_stay_inside_the_quote(
    md: MarkdownIt,
    break_name: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = _forged_lines(LINE_BREAKS[break_name])
    report = _report(
        inspection_input,
        {
            **supported_proposal_data,
            "evidence_quote": payload,
            "evidence_end": len(payload),
        },
        _not_established(),
    )
    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)
    assert view.findings[0].quote_lines() == [
        _shown(line) for line in payload.split("\n")
    ]


def test_mixed_report_keeps_clean_findings_warnings_and_limitations_visible(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    attacked = {
        **supported_proposal_data,
        "claim_id": "claim-0",
        "claim_text": "The blue door opens at nine.",
        "rationale": _forged_lines("\n"),
        "evidence_quote": "The blue door opens at nine.",
    }
    report = _report(
        inspection_input,
        attacked,
        supported_proposal_data,
        _not_established(),
    )
    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    guards = [
        finding.item("Deterministic guard:").value[1].content
        for finding in view.findings
    ]
    assert guards == ["failed", "passed", "passed"]
    assert len(view.list_items("Validation Warnings")) == 2
    visible = _visible_text(markdown, md)
    assert "The manual states the same opening time." in visible
    assert "The manual gives a different closing time." in visible
    assert "Citation validation confirms exact text and offsets" in visible


@pytest.mark.parametrize("payload_name", sorted(INLINE_PAYLOADS))
def test_inline_markdown_and_html_payloads_are_shown_as_text(
    md: MarkdownIt,
    payload_name: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = INLINE_PAYLOADS[payload_name]
    report = _report(
        inspection_input,
        {
            **supported_proposal_data,
            "claim_text": payload,
            "rationale": payload,
            "evidence_quote": payload,
            "evidence_end": len(payload),
        },
        _not_established(),
    )
    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    assert view.findings[0].quote_lines() == [_shown(payload)]
    visible = _visible_text(markdown, md)
    assert visible.count(_normalize_space(_shown(payload))) == 3


@pytest.mark.parametrize("payload_name", sorted(BLOCK_PAYLOADS))
def test_block_breakouts_after_line_breaks_stay_data(
    md: MarkdownIt,
    payload_name: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = "Looks consistent.\n" + BLOCK_PAYLOADS[payload_name]
    report = _report(
        inspection_input,
        {
            **supported_proposal_data,
            "claim_text": payload,
            "rationale": payload,
            "evidence_quote": payload,
            "evidence_end": len(payload),
        },
        _not_established(),
    )
    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    quote = [
        line.replace("\u00a0", " ").strip() for line in view.findings[0].quote_lines()
    ]
    assert quote == [_shown(line).strip() for line in payload.split("\n")]


def test_quotation_line_starts_cannot_open_blocks(md: MarkdownIt) -> None:
    source_lines = [
        "Plain first line.",
        *(line for payload in BLOCK_PAYLOADS.values() for line in payload.split("\n")),
        "+ plus item",
        "* star item",
        "***",
        "___",
        "=== underline",
        "\tTabbed line",
        "",
        "    indented after a blank line",
        "",
        "# heading after a blank line",
        "Last line.",
    ]
    source = "\n".join(source_lines)
    inspection_input = _source_bound_input("Doors exist.", source)
    report = _report(
        inspection_input, _bound_proposal(inspection_input, "Doors exist.", source)
    )
    markdown = render_markdown(report)

    assert report.findings[0].evidence_span_verified is True
    view = assert_report_structure(markdown, report, md)
    shown = [
        line.replace("\u00a0", " ").strip() for line in view.findings[0].quote_lines()
    ]
    assert shown == [_shown(line).strip() for line in source_lines if line]
    quote_tokens = view.findings[0].tokens
    inside = False
    for token in quote_tokens:
        if token.type == "blockquote_open":
            inside = True
        elif token.type == "blockquote_close":
            inside = False
        elif inside:
            assert token.type in {"paragraph_open", "paragraph_close", "inline"}
            for child in token.children or []:
                assert child.type in {"text", "hardbreak", "softbreak"}


# --------------------------------------------------------------------------- #
# C5: control, bidirectional and invisible characters
# --------------------------------------------------------------------------- #


def test_hidden_characters_are_shown_as_markers(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = "x".join(HIDDEN_CHARACTERS) + "x\u2028x\u2029x\r"
    report = _report(
        inspection_input,
        {
            **supported_proposal_data,
            "claim_text": "admin\u202eexe.txt",
            "rationale": payload,
            "evidence_quote": payload,
            "evidence_end": len(payload),
        },
        _not_established(),
    )
    markdown = render_markdown(report)

    assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)
    assert "admin\u27e6U+202E\u27e7exe" in markdown
    for character in HIDDEN_CHARACTERS + "\u2028\u2029\r":
        marker = f"\u27e6U+{ord(character):04X}\u27e7"
        assert markdown.count(marker) >= 2, marker
    assert "\u27e6U+E0041\u27e7" in markdown


def test_hidden_characters_in_a_verified_claim_are_marked(md: MarkdownIt) -> None:
    claim = "Dose is 5\u202e01 mg\u2066."
    inspection_input = _source_bound_input(claim, "Dose is 5\u202e01 mg\u2066 daily.")
    report = _report(
        inspection_input,
        _bound_proposal(inspection_input, claim, "Dose is 5\u202e01 mg\u2066"),
    )
    markdown = render_markdown(report)

    assert report.findings[0].deterministic_validation_status.value == "passed"
    assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)
    assert "5\u27e6U+202E\u27e701 mg\u27e6U+2066\u27e7" in markdown


def test_exact_marker_brackets_in_text_are_shown_as_markers(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = "fake \u27e6U+202E\u27e7 marker"
    report = _report(
        inspection_input, {**supported_proposal_data, "rationale": payload}
    )
    markdown = render_markdown(report)

    assert_report_structure(markdown, report, md)
    assert "\u27e6U+202E\u27e7" not in markdown
    assert "fake \u27e6U+27E6\u27e7U+202E\u27e6U+27E7\u27e7 marker" in markdown


def _raw_and_marker_counts(markdown: str, characters: str) -> dict[str, int]:
    raw = {
        f"raw U+{ord(character):04X}": markdown.count(character)
        for character in characters
        if character in markdown
    }
    return raw | {
        f"\u27e6U+{ord(character):04X}\u27e7": markdown.count(
            f"\u27e6U+{ord(character):04X}\u27e7"
        )
        for character in characters
    }


def test_code_points_unknown_to_an_older_unicode_version_are_marked(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    characters = LATER_FORMAT_CHARACTERS + UNASSIGNED_CODE_POINTS
    payload = "Hiero" + "x".join(characters) + "end"
    report = _report(
        inspection_input,
        {
            **supported_proposal_data,
            "claim_text": payload,
            "rationale": payload,
            "evidence_quote": payload,
            "evidence_end": len(payload),
        },
        _not_established(),
    )
    markdown = render_markdown(report)

    # Claim, rationale and quotation each show every character once as a marker.
    assert _raw_and_marker_counts(markdown, characters) == {
        f"\u27e6U+{ord(character):04X}\u27e7": 3 for character in characters
    }
    assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)
    assert json.loads(render_json(report))["findings"][0]["rationale"] == payload


def test_later_format_characters_in_a_verified_claim_are_marked(
    md: MarkdownIt,
) -> None:
    claim = f"Hiero{LATER_FORMAT_CHARACTERS}end."
    inspection_input = _source_bound_input(claim, f"Source: {claim}")
    report = _report(
        inspection_input,
        _bound_proposal(inspection_input, claim, claim, rationale=claim),
    )
    markdown = render_markdown(report)

    assert report.findings[0].deterministic_validation_status.value == "passed"
    markers = "".join(
        f"\u27e6U+{code_point:X}\u27e7" for code_point in range(0x13439, 0x13440)
    )
    assert _raw_and_marker_counts(markdown, LATER_FORMAT_CHARACTERS) == {
        f"\u27e6U+{ord(character):04X}\u27e7": 3
        for character in LATER_FORMAT_CHARACTERS
    }
    assert markdown.count(f"Hiero{markers}end.") == 3
    assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)


def test_private_use_characters_are_not_marked(md: MarkdownIt) -> None:
    text = f"Door icon {PRIVATE_USE_CHARACTERS} opens."
    inspection_input = _source_bound_input(text, f"Source: {text}")
    report = _report(
        inspection_input,
        _bound_proposal(inspection_input, text, text, rationale=text),
    )
    markdown = render_markdown(report)

    assert report.findings[0].deterministic_validation_status.value == "passed"
    view = assert_report_structure(markdown, report, md)
    assert "\u27e6" not in markdown.split("## Findings", 1)[1]
    assert view.findings[0].item("Atomic claim:").value_text == text
    assert view.findings[0].quote_lines() == [text]


JOINED_TEXT = (
    "Door opens \N{WOMAN}\N{ZERO WIDTH JOINER}\N{PERSONAL COMPUTER} and "
    "\N{ARABIC LETTER NOON}\N{ARABIC LETTER MEEM}\N{ARABIC LETTER FARSI YEH}"
    "\N{ZERO WIDTH NON-JOINER}\N{ARABIC LETTER KHAH}\N{ARABIC LETTER WAW}"
    "\N{ARABIC LETTER ALEF}\N{ARABIC LETTER HEH}\N{ARABIC LETTER MEEM}."
)


def test_joiners_are_marked_between_readable_components(md: MarkdownIt) -> None:
    inspection_input = _source_bound_input(JOINED_TEXT, f"Source: {JOINED_TEXT}")
    report = _report(
        inspection_input,
        _bound_proposal(
            inspection_input, JOINED_TEXT, JOINED_TEXT, rationale=JOINED_TEXT
        ),
    )
    markdown = render_markdown(report)

    assert report.findings[0].deterministic_validation_status.value == "passed"
    view = assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)
    shown = (
        f"Door opens \N{WOMAN}{OPEN}U+200D{CLOSE}\N{PERSONAL COMPUTER} and "
        "\N{ARABIC LETTER NOON}\N{ARABIC LETTER MEEM}\N{ARABIC LETTER FARSI YEH}"
        f"{OPEN}U+200C{CLOSE}\N{ARABIC LETTER KHAH}\N{ARABIC LETTER WAW}"
        "\N{ARABIC LETTER ALEF}\N{ARABIC LETTER HEH}\N{ARABIC LETTER MEEM}."
    )
    assert view.findings[0].item("Atomic claim:").value_text == shown
    assert view.findings[0].item("Rationale (evaluator-generated):").value_text == (
        shown
    )
    assert view.findings[0].quote_lines() == [shown]
    assert _visible_text(markdown, md).count(shown) == 3
    assert json.loads(render_json(report))["findings"][0]["claim_text"] == JOINED_TEXT


# --------------------------------------------------------------------------- #
# Host text from deserialized reports and reports built without validation
# --------------------------------------------------------------------------- #


def test_deserialized_report_host_text_is_encoded(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    failing = {
        **supported_proposal_data,
        "evidence_quote": "The blue door opens at nine.",
    }
    payload = json.loads(render_json(_report(inspection_input, failing)))
    payload["scope"]["statement"] = "# Forged heading\n<!--"
    payload["scope"]["limitations"] = [
        "- **Deterministic guard:** `passed`\n## Fake section",
        "1. ordered",
        "   <div hidden>indented</div>",
    ]
    payload["findings"][0]["validation_issues"][0]["message"] = (
        "ok\n- **Deterministic guard:** `passed`\n<!--"
    )
    report = InspectionReport.model_validate_json(json.dumps(payload))
    markdown = render_markdown(report)

    assert_report_structure(markdown, report, md)
    assert_no_raw_hidden_characters(markdown)


def test_report_built_without_validation_still_renders_as_data(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    report = _report(inspection_input, supported_proposal_data)
    finding = report.findings[0].model_copy(
        update={
            "claim_id": "claim`\n# forged",
            "source_id": "x` <!--",
            "rationale": "lone \ud800 surrogate",
        }
    )
    unvalidated = report.model_copy(update={"findings": (finding,)})
    markdown = render_markdown(unvalidated)

    assert_no_raw_hidden_characters(markdown)
    view = _view(markdown, md)
    assert [text for tag, text in view.headings if tag == "h2"] == H2_SECTIONS
    assert [tag for tag, _ in view.headings].count("h1") == 1
    assert "\u27e6U+D800\u27e7" in markdown
    assert not {token.type for token in _walk(view.tokens)} & FORBIDDEN_TOKEN_TYPES


# --------------------------------------------------------------------------- #
# Clean counterparts, single encoding and unchanged raw values
# --------------------------------------------------------------------------- #


CLEAN_TEXTS = {
    "german": "Die Größe der Tür beträgt 2 m; Öffnung um 9 Uhr, Schließung später.",
    "greek": "Η πόρτα ανοίγει στις εννέα.",
    "hebrew": "הדלת נפתחת בתשע.",
    "arabic": "يفتح الباب في التاسعة.",
    "emoji": (
        "Door \N{DOOR} opens \N{WOMAN} \N{PERSONAL COMPUTER} "
        "\N{HEAVY BLACK HEART}\N{VARIATION SELECTOR-16} "
        "\N{REGIONAL INDICATOR SYMBOL LETTER D}"
        "\N{REGIONAL INDICATOR SYMBOL LETTER E} today."
    ),
    "markdown-punctuation": (
        "a*b_c [x](y) `code` # not a heading | pipe ~tilde~ <b>bold</b> &amp; "
        "1. 2) - + > = ! \\ end"
    ),
}


@pytest.mark.parametrize("name", sorted(CLEAN_TEXTS))
def test_clean_text_stays_readable(md: MarkdownIt, name: str) -> None:
    text = CLEAN_TEXTS[name]
    inspection_input = _source_bound_input(text, f"Source: {text}")
    report = _report(
        inspection_input,
        _bound_proposal(inspection_input, text, text, rationale=text),
    )
    markdown = render_markdown(report)

    assert report.findings[0].deterministic_validation_status.value == "passed"
    view = assert_report_structure(markdown, report, md)
    assert "\u27e6" not in markdown.split("## Findings", 1)[1]
    assert view.findings[0].item("Atomic claim:").value_text == text
    assert view.findings[0].item("Rationale (evaluator-generated):").value_text == text
    assert view.findings[0].quote_lines() == [text]
    assert _visible_text(markdown, md).count(_normalize_space(text)) == 3


def test_clean_multiline_quotation_keeps_its_lines(md: MarkdownIt) -> None:
    quote = "Opening hours:\nMonday to Friday, 9:00–17:00\n\nClosed on public holidays."
    inspection_input = _source_bound_input("The door opens on Monday.", quote)
    report = _report(
        inspection_input,
        _bound_proposal(inspection_input, "The door opens on Monday.", quote),
    )
    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    assert view.findings[0].quote_lines() == [
        line for line in quote.split("\n") if line
    ]
    paragraphs = [
        token for token in view.findings[0].tokens if token.type == "paragraph_open"
    ]
    assert len(paragraphs) >= 2
    line_breaks = [
        child.type
        for token in view.findings[0].tokens
        if token.type == "inline"
        for child in token.children or []
        if child.type in {"softbreak", "hardbreak"}
    ]
    assert line_breaks == ["hardbreak"]


def test_default_host_text_is_displayed_unchanged(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    no_citation = {
        "source_id": None,
        "evidence_quote": None,
        "evidence_start": None,
        "evidence_end": None,
    }
    report = _report(
        inspection_input,
        {**supported_proposal_data, "evidence_end": None},
        _not_established(),
        {**supported_proposal_data, "claim_id": "claim-3", **no_citation},
    )
    markdown = render_markdown(report)

    messages = [
        issue.message
        for finding in report.findings
        for issue in finding.validation_issues
    ]
    assert messages == [
        "Evidence reference fields must be either all present or all null.",
        "This proposed relation requires source_id, quote, start, and end.",
    ]
    assert_report_structure(markdown, report, md)
    assert _view(markdown, md).list_items("Scope and Limitations") == list(
        report.scope.limitations
    )


def test_markdown_characters_are_encoded_exactly_once(
    md: MarkdownIt,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = "a*b \\* c\\\\d `e` <f> &g; [h] www.i.example"
    report = _report(
        inspection_input, {**supported_proposal_data, "rationale": payload}
    )
    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    assert (
        view.findings[0].item("Rationale (evaluator-generated):").value_text == payload
    )
    assert render_markdown(report) == markdown


def _punctuation_samples(mark: str) -> list[str]:
    return [
        mark,
        mark * 3,
        f"{mark} x",
        f"x{mark}y",
        f"x{mark} y",
        f"{mark}x{mark}",
        f"x {mark}{mark} y{mark}",
    ]


@pytest.mark.parametrize("mark", list(string.punctuation))
def test_ascii_punctuation_follows_display_contract_in_every_context(
    md: MarkdownIt,
    mark: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    samples = _punctuation_samples(mark)
    inline = " ".join(samples)
    quotation = "\n".join(samples)
    built = _report(
        inspection_input,
        {
            **supported_proposal_data,
            "claim_text": inline,
            "rationale": inline,
            "evidence_quote": quotation,
            "evidence_end": len(quotation),
        },
    )
    payload = json.loads(render_json(built))
    payload["scope"]["statement"] = inline
    payload["scope"]["limitations"] = samples
    report = InspectionReport.model_validate_json(json.dumps(payload))
    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    assert view.findings[0].quote_lines() == [_shown(sample) for sample in samples]
    scope = view.sections["Scope and Limitations"]
    statement = next(
        scope[index + 1]
        for index, token in enumerate(scope)
        if token.type == "paragraph_open" and token.level == 0
    )
    assert _text_of(statement.children or []) == _shown(inline)
    # Claim, rationale, quotation lines, scope statement and limitation items.
    assert _visible_text(markdown, md).count(_shown(inline)) == 5


def test_attack_payloads_leave_json_and_stored_values_unchanged(
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = _forged_lines("\r\n") + "\u202e\u2028\x00\u27e6U+202E\u27e7"
    proposal = {
        **supported_proposal_data,
        "claim_text": payload,
        "rationale": payload,
        "evidence_quote": payload,
        "evidence_end": len(payload),
    }
    report = _report(inspection_input, proposal)
    dumped_before = report.model_dump(mode="json")
    json_before = render_json(report)

    render_markdown(report)

    assert report.model_dump(mode="json") == dumped_before
    assert render_json(report) == json_before
    finding = json.loads(json_before)["findings"][0]
    assert finding["claim_text"] == payload
    assert finding["rationale"] == payload
    assert finding["evidence_quote"] == payload
    assert finding["evidence_end"] == len(payload)
    assert report.findings[0].evidence_quote == payload


@pytest.mark.parametrize(
    "payload",
    [
        "X" + "\u030d" * 5,
        "X" + "\u030d\u20dd" * 256,
        "X" + "\u030d" * 5 + " Y" + "\u20dd" * 6,
        "Contact reader@example.org",
        "Contact mailto:reader@example.org",
        "Contact xmpp:reader@example.org",
    ],
    ids=["five-marks", "long-mixed-run", "two-runs", "email", "mailto", "xmpp"],
)
def test_display_limits_cover_all_report_contexts_without_changing_raw_values(
    md: MarkdownIt,
    payload: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    inspected = _report(
        inspection_input,
        {
            **supported_proposal_data,
            "claim_text": payload,
            "rationale": payload,
            "evidence_quote": payload,
            "evidence_end": len(payload),
        },
        _not_established(),
    )
    # These three host-composed fields can also carry data from deserialized
    # reports, and use line-start or inline encoders instead of quote encoding.
    serialized = inspected.model_dump(mode="json")
    serialized["scope"]["statement"] = payload
    serialized["scope"]["limitations"] = [payload]
    serialized["findings"][0]["validation_issues"][0]["message"] = payload
    report = InspectionReport.model_validate(serialized)
    before = render_json(report)

    markdown = render_markdown(report)

    view = assert_report_structure(markdown, report, md)
    assert view.findings[0].quote_lines() == [_shown(payload)]
    assert report.findings[0].deterministic_validation_status.value == "failed"
    assert report.findings[0].reportable_relation is None
    assert report.findings[1].deterministic_validation_status.value == "passed"
    visible = _visible_text(markdown, md)
    assert visible.count(_shown(payload)) == 6
    for is_combining, run in groupby(
        visible, key=lambda character: unicodedata.category(character) in {"Mn", "Me"}
    ):
        if is_combining:
            assert sum(1 for _ in run) <= 4
    assert render_json(report) == before
    assert report.model_dump(mode="json") == serialized


def test_cli_markdown_output_keeps_structure_for_attack_payload(
    tmp_path: Path,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    payload = _forged_lines("\n") + " \u202e <div hidden>"
    input_path = tmp_path / "input.json"
    proposals_path = tmp_path / "proposals.json"
    markdown_path = tmp_path / "report.md"
    json_path = tmp_path / "report.json"
    input_path.write_text(inspection_input.model_dump_json(), encoding="utf-8")
    proposals_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "findings": [
                    {**supported_proposal_data, "rationale": payload},
                    _not_established(),
                ],
            }
        ),
        encoding="utf-8",
    )
    common = ["inspect", "--input", str(input_path), "--proposals", str(proposals_path)]

    assert main([*common, "--format", "markdown", "--output", str(markdown_path)]) == 0
    assert main([*common, "--format", "json", "--output", str(json_path)]) == 0

    report = InspectionReport.model_validate_json(json_path.read_text(encoding="utf-8"))
    assert report.findings[0].rationale == payload
    markdown = markdown_path.read_text(encoding="utf-8")
    for parser in (MarkdownIt("commonmark", {"html": True}), MarkdownIt("gfm-like")):
        assert_report_structure(markdown, report, parser)
    assert_no_raw_hidden_characters(markdown)


@pytest.mark.parametrize(
    "claim",
    [*("X" + "\u0323" * n for n in (2, 3, 4, 48, 80)), "Cafe\u0301 Ελληνικά العربية"],
    ids=["two", "three", "four", "long-48", "long-80", "multilingual"],
)
def test_claim_paragraph_precedes_host_checks(
    md: MarkdownIt,
    claim: str,
    inspection_input: InspectionInput,
    supported_proposal_data: dict[str, Any],
) -> None:
    report = _report(inspection_input, {**supported_proposal_data, "claim_text": claim})
    before = render_json(report)
    view = assert_report_structure(render_markdown(report), report, md)
    tokens = view.findings[0].tokens
    claims = [
        index
        for index, token in enumerate(tokens)
        if token.type == "paragraph_open"
        and token.level == 0
        and (label := _labeled(tokens[index + 1])) is not None
        and label.label == "Atomic claim:"
    ]
    assert len(claims) == 1
    start = claims[0]
    assert tokens[start + 2].type == "paragraph_close"
    # The first host control is outside the claim paragraph, in a tight list.
    assert [token.type for token in tokens[start + 3 : start + 6]] == [
        "bullet_list_open",
        "list_item_open",
        "paragraph_open",
    ]
    answer_span = _labeled(tokens[start + 6])
    assert answer_span is not None and answer_span.label == "Answer span:"
    assert tokens[start + 5].hidden
    assert render_json(report) == before
