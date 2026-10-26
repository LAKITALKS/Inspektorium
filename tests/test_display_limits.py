"""Regressions for the bounded Mn/Me display rule and visible at-sign marker.

These are text and Markdown DOM checks. They do not infer pixel visibility in
other fonts or viewers; the versioned evidence addendum records those probes.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable
from itertools import groupby

import pytest
from markdown_it import MarkdownIt

from inspektorium.report.display import (
    encode_identifier,
    encode_inline,
    encode_line,
    encode_quote,
)

ENCODERS = [encode_inline, encode_line, encode_quote, encode_identifier]


def _marker(character: str) -> str:
    return f"\u27e6U+{ord(character):04X}\u27e7"


def _raw_mark_runs(text: str) -> list[int]:
    """Inspect actual output independently of the product's bounded lookup."""

    return [
        sum(1 for _ in group)
        for is_mark, group in groupby(
            text, key=lambda character: unicodedata.category(character) in {"Mn", "Me"}
        )
        if is_mark
    ]


def test_raw_run_oracle_rejects_five_and_accepts_four() -> None:
    assert max(_raw_mark_runs("X" + "\u030d" * 5)) > 4
    assert max(_raw_mark_runs("X" + "\u030d" * 4)) == 4
    assert max(_raw_mark_runs("X" + "\u030d" * 4 + "\u27e6U+030D\u27e7")) == 4


@pytest.mark.parametrize("encode", ENCODERS, ids=lambda encode: encode.__name__)
@pytest.mark.parametrize("count", [0, 1, 4, 5, 6, 32, 4096])
@pytest.mark.parametrize("marks", ["\u030d", "\u20dd", "\u030d\u20dd", "\ufe0f"])
def test_four_marks_stay_raw_and_every_later_mark_is_visible(
    encode: Callable[[str], str], count: int, marks: str
) -> None:
    run = marks * count
    text = "X" + run
    expected = "X" + run[:4] + "".join(_marker(mark) for mark in run[4:])
    if encode is encode_quote:
        expected = "> " + expected

    encoded = encode(text)

    assert encoded == expected
    assert max(_raw_mark_runs(encoded), default=0) <= 4
    assert text == "X" + run


@pytest.mark.parametrize("encode", ENCODERS, ids=lambda encode: encode.__name__)
@pytest.mark.parametrize("separator", ["a", " ", "\t", "\n", "\u0903", "\u200d", "@"])
def test_each_mn_me_run_has_its_own_limit(
    encode: Callable[[str], str], separator: str
) -> None:
    encoded = encode("X" + "\u030d" * 5 + separator + "\u20dd" * 6)

    assert _raw_mark_runs(encoded) == [4, 4]
    assert encoded.count("\u27e6U+030D\u27e7") == 1
    assert encoded.count("\u27e6U+20DD\u27e7") == 2


@pytest.mark.parametrize("encode", ENCODERS, ids=lambda encode: encode.__name__)
@pytest.mark.parametrize("length", [64, 1024])
def test_long_runs_do_not_require_quadratic_category_lookups(
    encode: Callable[[str], str], length: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = unicodedata.category
    calls = 0

    def count_category(character: str) -> str:
        nonlocal calls
        calls += 1
        return original(character)

    monkeypatch.setattr(unicodedata, "category", count_category)
    encode("X" + "\u030d" * length)

    # A linear counter or a short bounded lookup fits this bound. The reviewed
    # prototype's repeated scan of the whole preceding run does not.
    assert calls <= 8 * (length + 1)


@pytest.mark.parametrize("encode", ENCODERS, ids=lambda encode: encode.__name__)
@pytest.mark.parametrize(
    "text",
    [
        "Cafe\u0301 und Gro\u0308ße",
        "a\u0306\u0301",  # Vietnamese, deliberately decomposed
        "α\u0313\u0301",  # Greek breath mark and accent
        "שָׁלוֹם",  # Hebrew vowels and shin dot
        "مُحَمَّد",  # Arabic vowel marks and shadda
        "हिन्दी",  # Devanagari nonspacing and spacing marks
        "เก่ง",  # Thai tone mark
        "\u2764\ufe0f",  # Emoji variation selector
    ],
)
def test_legitimate_marks_remain_exact_without_normalization(
    encode: Callable[[str], str], text: str
) -> None:
    expected = "> " + text if encode is encode_quote else text
    assert encode(text) == expected


@pytest.mark.parametrize("encode", ENCODERS, ids=lambda encode: encode.__name__)
@pytest.mark.parametrize("prefix", ["", "mailto:", "xmpp:"])
def test_email_forms_have_a_visible_at_marker_and_no_markdown_link(
    encode: Callable[[str], str], prefix: str
) -> None:
    text = f"Contact {prefix}reader@example.org"
    encoded = encode(text)
    parser = MarkdownIt("gfm-like")
    tokens = parser.parse(encoded)
    children = [child for token in tokens for child in token.children or []]

    assert "@" not in encoded
    assert encoded.count("\u27e6U+0040\u27e7") == 1
    assert all(child.type not in {"link_open", "link_close"} for child in children)
    assert "".join(child.content for child in children) == text.replace(
        "@", "\u27e6U+0040\u27e7"
    )
