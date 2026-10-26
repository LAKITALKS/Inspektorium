"""Unit tests for the Markdown display encoders added in 0.1.1.

These tests import ``inspektorium.report.display``, which does not exist in
public 0.1.0; on that baseline this module fails at import time by design. The
version-independent structural regression tests are in ``test_render_safety``.
"""

from __future__ import annotations

import re
import string
import sys
import unicodedata
from html.parser import HTMLParser

import pytest
from markdown_it import MarkdownIt

from inspektorium.report.display import (
    ALWAYS_ESCAPED,
    ENTITY_ESCAPED,
    LINK_PUNCTUATION,
    MARKED_CATEGORIES,
    MARKER_CLOSE,
    MARKER_OPEN,
    PORTABLE_BACKSLASH_ESCAPES,
    QUOTE_LINE_BREAK,
    display_marker,
    encode_identifier,
    encode_inline,
    encode_line,
    encode_quote,
    escape_punctuation,
    is_marked,
)

OPEN = "\N{MATHEMATICAL LEFT WHITE SQUARE BRACKET}"
CLOSE = "\N{MATHEMATICAL RIGHT WHITE SQUARE BRACKET}"
NBSP = "\N{NO-BREAK SPACE}"
ZWJ = "\N{ZERO WIDTH JOINER}"
ZWNJ = "\N{ZERO WIDTH NON-JOINER}"
RLO = "\N{RIGHT-TO-LEFT OVERRIDE}"
LINE_SEPARATOR = "\N{LINE SEPARATOR}"
VARIATION_SELECTOR_16 = "\N{VARIATION SELECTOR-16}"
PARSERS = {
    "commonmark-html": MarkdownIt("commonmark", {"html": True}),
    "gfm-like": MarkdownIt("gfm-like"),
}
# The characters that Python-Markdown 3.x accepts after a backslash by default
# (``markdown.Markdown().ESCAPED_CHARS``), written out independently of the
# product constant. CommonMark accepts every ASCII punctuation character.
PYTHON_MARKDOWN_ESCAPABLE = frozenset("\\`*_{}[]()>#+-.!")


def marker(character: str) -> str:
    return f"{OPEN}U+{ord(character):04X}{CLOSE}"


def shown(text: str) -> str:
    return "".join(
        marker(character)
        if character in (OPEN, CLOSE, "@")
        or unicodedata.category(character) in {"Cc", "Cf", "Cn", "Cs", "Zl", "Zp"}
        else character
        for character in text
    )


def test_marker_brackets_and_categories_are_the_documented_ones() -> None:
    assert (ord(MARKER_OPEN), ord(MARKER_CLOSE)) == (0x27E6, 0x27E7)
    assert MARKED_CATEGORIES == {"Cc", "Cf", "Cn", "Cs", "Zl", "Zp"}


@pytest.mark.parametrize(
    ("code_point", "label"),
    [
        (0x0000, "U+0000"),
        (0x0009, "U+0009"),
        (0x00AD, "U+00AD"),
        (0x200C, "U+200C"),
        (0x200D, "U+200D"),
        (0x202E, "U+202E"),
        (0xD800, "U+D800"),
        (0x27E6, "U+27E6"),
        (0xE0041, "U+E0041"),
        (0x10FFFD, "U+10FFFD"),
    ],
)
def test_marker_uses_uppercase_hex_with_at_least_four_digits(
    code_point: int, label: str
) -> None:
    assert display_marker(chr(code_point)) == f"{OPEN}{label}{CLOSE}"


def test_marked_characters_are_exactly_the_documented_classes() -> None:
    mismatches = [
        f"U+{code_point:04X}"
        for code_point in range(sys.maxunicode + 1)
        if is_marked(chr(code_point))
        != (
            chr(code_point) in (OPEN, CLOSE, "@")
            or unicodedata.category(chr(code_point)) in MARKED_CATEGORIES
        )
    ]

    assert mismatches == []


@pytest.mark.parametrize(
    "text",
    [
        "\N{RAINBOW}\N{SPARKLING HEART} \N{PERSONAL COMPUTER}",
        f"\N{HEAVY BLACK HEART}{VARIATION_SELECTOR_16}",
        "\N{REGIONAL INDICATOR SYMBOL LETTER D}\N{REGIONAL INDICATOR SYMBOL LETTER E}",
        "Größe Übermaß ß",
        "\N{GREEK CAPITAL LETTER ETA} \N{GREEK SMALL LETTER PI}",
        "\N{HEBREW LETTER SHIN}\N{HEBREW LETTER LAMED}\N{HEBREW LETTER FINAL MEM}",
        "\N{ARABIC LETTER NOON}\N{ARABIC LETTER MEEM}\N{ARABIC LETTER FARSI YEH}",
    ],
)
def test_readable_text_without_joiners_is_not_marked(text: str) -> None:
    assert encode_inline(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            f"\N{WOMAN}{ZWJ}\N{PERSONAL COMPUTER}",
            f"\N{WOMAN}{OPEN}U+200D{CLOSE}\N{PERSONAL COMPUTER}",
        ),
        (
            f"\N{ARABIC LETTER NOON}\N{ARABIC LETTER MEEM}\N{ARABIC LETTER FARSI YEH}"
            f"{ZWNJ}\N{ARABIC LETTER KHAH}",
            f"\N{ARABIC LETTER NOON}\N{ARABIC LETTER MEEM}\N{ARABIC LETTER FARSI YEH}"
            f"{OPEN}U+200C{CLOSE}\N{ARABIC LETTER KHAH}",
        ),
        (f"pa{ZWJ}ss{ZWNJ}ed", f"pa{OPEN}U+200D{CLOSE}ss{OPEN}U+200C{CLOSE}ed"),
    ],
)
def test_joiners_are_marked_between_the_visible_components(
    text: str, expected: str
) -> None:
    assert encode_inline(text) == expected
    assert ZWJ not in encode_inline(text)
    assert ZWNJ not in encode_inline(text)


def test_control_bidi_and_separator_characters_are_marked() -> None:
    text = f"a\tb\rc\nd\x85e{LINE_SEPARATOR}f{RLO}g\x00h{chr(0xD800)}i{ZWJ}j"

    assert encode_inline(text) == (
        f"a{marker(chr(9))}b{marker(chr(13))}c{marker(chr(10))}d{marker(chr(0x85))}"
        f"e{marker(LINE_SEPARATOR)}f{marker(RLO)}g{marker(chr(0))}h"
        f"{marker(chr(0xD800))}i{marker(ZWJ)}j"
    )


def test_literal_markers_cannot_collide_with_host_markers() -> None:
    assert encode_inline(f"{OPEN}U+202E{CLOSE}") == (
        f"{marker(OPEN)}U+202E{marker(CLOSE)}"
    )
    # Documented limit: look-alike brackets are ordinary characters.
    look_alike = "\N{LEFT WHITE SQUARE BRACKET}U+202E\N{RIGHT WHITE SQUARE BRACKET}"
    assert (ord(look_alike[0]), ord(look_alike[-1])) == (0x301A, 0x301B)
    assert encode_inline(look_alike) == look_alike


def test_escape_sets() -> None:
    assert ALWAYS_ESCAPED == set("<&\\`*_[]~|$")
    assert LINK_PUNCTUATION == set(".:/")
    assert ENTITY_ESCAPED == {"<": "&lt;", "&": "&amp;"}
    assert QUOTE_LINE_BREAK == "  "
    assert PORTABLE_BACKSLASH_ESCAPES == PYTHON_MARKDOWN_ESCAPABLE
    assert PORTABLE_BACKSLASH_ESCAPES <= set(string.punctuation)


@pytest.mark.parametrize("character", list(string.punctuation))
def test_each_punctuation_character_has_one_portable_escape(character: str) -> None:
    escaped = escape_punctuation(character)

    if character in ENTITY_ESCAPED:
        assert escaped == ENTITY_ESCAPED[character]
    elif character in PYTHON_MARKDOWN_ESCAPABLE:
        assert escaped == "\\" + character
    else:
        assert escaped == f"&#{ord(character)};"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a*b_c", "a\\*b\\_c"),
        ("`code`", "\\`code\\`"),
        ("[x](y)", "\\[x\\](y)"),
        ("<!--", "&lt;!--"),
        ("&#x202E;", "&amp;#x202E;"),
        ("<b>&amp;</b>", "&lt;b>&amp;amp;&lt;&#47;b>"),
        ("a|b ~c~ $d$", "a&#124;b &#126;c&#126; &#36;d&#36;"),
        ("back\\slash", "back\\\\slash"),
        ("user@example", f"user{marker('@')}example"),
        ("Saturdays.", "Saturdays."),
        ("10 a.m. to 2", "10 a\\.m. to 2"),
        ("Note: done", "Note: done"),
        ("9:00", "9&#58;00"),
        ("http://x", "http&#58;&#47;&#47;x"),
        ("and/or", "and&#47;or"),
        ("a / b", "a / b"),
        ("www.x.org", "www\\.x\\.org"),
        ("see www. x", "see www\\. x"),
        ("see WWW.", "see WWW\\."),
        ("# - + = > ! ( ) ' \" , ; ? % ^ { }", "# - + = > ! ( ) ' \" , ; ? % ^ { }"),
    ],
)
def test_inline_escaping(text: str, expected: str) -> None:
    assert encode_inline(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("plain", "plain"),
        ("", ""),
        ("# heading", "\\# heading"),
        ("===", "&#61;=="),
        ("- item", "\\- item"),
        ("+ item", "\\+ item"),
        ("* item", "\\* item"),
        ("> quote", "\\> quote"),
        ("1. one", "1\\. one"),
        ("12) twelve", "12\\) twelve"),
        ("1.5 kg", "1\\.5 kg"),
        ("```", "\\`\\`\\`"),
        ("~~~", "&#126;&#126;&#126;"),
        ("|a|", "&#124;a&#124;"),
        ("<div>", "&lt;div>"),
        ("&nbsp;", "&amp;nbsp;"),
        ("[x]: y", "\\[x\\]: y"),
        (". x", "\\. x"),
        (": x", "&#58; x"),
        ('"quoted"', '&#34;quoted"'),
        ("% x", "&#37; x"),
        ("\\x", "\\\\x"),
        ("    code", f"{NBSP * 4}code"),
        ("  # heading", f"{NBSP * 2}\\# heading"),
        ("\tcode", f"{marker(chr(9))}code"),
        (f"{RLO}# x", f"{marker(RLO)}# x"),
    ],
)
def test_line_start_protection(text: str, expected: str) -> None:
    assert encode_line(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("one line", "> one line"),
        ("a\nb", "> a  \n> b"),
        ("a\n\nb", "> a\n>\n> b"),
        ("a\n", "> a\n>"),
        ("\nb", ">\n> b"),
        ("a\rb", f"> a{marker(chr(13))}b"),
        ("a\r\nb", f"> a{marker(chr(13))}  \n> b"),
        (f"a{LINE_SEPARATOR}b", f"> a{marker(LINE_SEPARATOR)}b"),
        (
            "a\x0bb\x0cc\x85d",
            f"> a{marker(chr(11))}b{marker(chr(12))}c{marker(chr(0x85))}d",
        ),
        ("end\\\nnext", "> end\\\\  \n> next"),
        ("# a\n- b", "> \\# a  \n> \\- b"),
        ("x:\n~y", "> x:  \n> &#126;y"),
    ],
)
def test_quote_encoding_splits_only_on_lf(text: str, expected: str) -> None:
    assert encode_quote(text) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("claim-1", "`claim-1`"),
        ("a_b-c", "`a_b-c`"),
        ("claim`\n# x", f"claim\\`{marker(chr(10))}# x"),
        ("Claim", "Claim"),
        ("a" * 81, "a" * 81),
    ],
)
def test_identifiers_are_code_only_when_they_match_the_schema(
    value: str, expected: str
) -> None:
    assert encode_identifier(value) == expected


def _punctuation_samples(mark: str) -> tuple[str, ...]:
    return (
        mark,
        mark * 3,
        f"{mark} x",
        f"x{mark}y",
        f"x{mark} y",
        f"{mark}x{mark}",
        f"x {mark}{mark} y{mark}",
    )


PUNCTUATION_SAMPLES = [
    sample for mark in string.punctuation for sample in _punctuation_samples(mark)
]


def _backslash_escaped(markdown: str) -> list[str]:
    return re.findall(r"\\(.)", markdown, flags=re.DOTALL)


def test_backslash_escapes_are_portable_to_python_markdown() -> None:
    texts = [
        *PUNCTUATION_SAMPLES,
        *(
            first + second
            for first in string.punctuation
            for second in string.punctuation
        ),
        "http://example.org/a?b=1&c=2 user@example.org ~~x~~ a|b $x$ 9:00 ==",
    ]
    escaped: set[str] = set()
    for text in texts:
        for encoded in (
            encode_inline(text),
            encode_line(text),
            encode_quote(f"{text}\n{text}\n\n{text}"),
        ):
            escaped.update(_backslash_escaped(encoded))
            for line in encoded.split("\n"):
                trailing = len(line) - len(line.rstrip("\\"))
                assert trailing % 2 == 0, (text, encoded)

    assert escaped <= PYTHON_MARKDOWN_ESCAPABLE


class _VisibleHtml(HTMLParser):
    """Collect element names and decoded text of markdown-it-py HTML output."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.attributes: list[tuple[str, str | None]] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        self.attributes.extend(attrs)
        if tag == "br":
            self.parts.append("\n")

    def handle_comment(self, data: str) -> None:
        self.tags.append("!--")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _visible_html(html: str) -> _VisibleHtml:
    page = _VisibleHtml()
    page.feed(html)
    page.close()
    assert page.attributes == []
    return page


def _render_context(parser: MarkdownIt, context: str, text: str) -> tuple[str, str]:
    if context == "inline":
        page = _visible_html(parser.render(f"- **Label:** {encode_inline(text)}\n"))
        assert page.tags == ["ul", "li", "strong"], (text, page.tags)
        return "".join(page.parts).strip("\n"), f"Label: {shown(text)}"
    if context == "line-start":
        page = _visible_html(parser.render(encode_line(text) + "\n"))
        assert page.tags == ["p"], (text, page.tags)
        return "".join(page.parts).strip("\n"), shown(text)
    quotation = f"{text}\n{text}\n\nlast {text}"
    page = _visible_html(parser.render(encode_quote(quotation) + "\n"))
    assert page.tags == ["blockquote", "p", "br", "p"], (text, page.tags)
    lines = [line for line in "".join(page.parts).split("\n") if line]
    return "\n".join(lines), "\n".join(
        [shown(text), shown(text), f"last {shown(text)}"]
    )


@pytest.mark.parametrize("context", ["inline", "line-start", "quote"])
@pytest.mark.parametrize("mark", list(string.punctuation))
@pytest.mark.parametrize("parser_name", sorted(PARSERS))
def test_punctuation_round_trips_to_the_display_text(
    parser_name: str, mark: str, context: str
) -> None:
    parser = PARSERS[parser_name]
    for text in _punctuation_samples(mark):
        visible, intended = _render_context(parser, context, text)
        assert visible == intended, (text, encode_inline(text))


ROUND_TRIP_TEXTS = [
    *string.printable.strip(),
    *(first + second for first in string.punctuation for second in string.punctuation),
    *(f"a{mark}b" for mark in string.punctuation),
    *(f"a{mark} b" for mark in string.punctuation),
    "www.example.org and http://example.org/x?y=1&z=2 and user@example.org",
    "//localhost:8080/x and mailto:user@example.org and ftp://example.org",
    "<b>bold</b> <!-- c --> <![CDATA[x]]> <?pi?> &amp; &#10; &#x202E;",
    "**strong** __strong__ *em* _em_ ~~strike~~ `code` ``co`de``",
    "[link](https://example.org) ![image](x.png) [ref][r] [^1]",
    "a | b | c",
    "$\\color{green}\\text{passed}$ and $$x$$",
    f"bidi {RLO}override{chr(0x202C)} and tag {chr(0xE0041)} and {chr(0x200B)}",
    f"joined \N{WOMAN}{ZWJ}\N{PERSONAL COMPUTER} and non{ZWNJ}joined",
    f"{OPEN}U+202E{CLOSE}",
]


@pytest.mark.parametrize("parser_name", sorted(PARSERS))
def test_inline_encoding_round_trips_to_the_display_text(parser_name: str) -> None:
    parser = PARSERS[parser_name]
    failures = []
    for text in ROUND_TRIP_TEXTS:
        tokens = parser.parse(f"- **Label:** {encode_inline(text)}\n")
        inline = next(token for token in tokens if token.type == "inline")
        children = [
            child
            for child in inline.children or []
            if not (child.type == "text" and child.content == "")
        ]
        types = [child.type for child in children]
        value = "".join(child.content for child in children[3:])
        if types != ["strong_open", "text", "strong_close", "text"] or value != (
            f" {shown(text)}"
        ):
            failures.append((text, types, value))

    assert failures == []


LINE_START_TEXTS = [
    *(f"{mark} x" for mark in string.punctuation),
    *(mark * 3 for mark in string.punctuation),
    *(
        f"{digits}{delimiter} x"
        for digits in ("1", "12", "123456789")
        for delimiter in ".)"
    ),
    "    indented code",
    "  - indented item",
    "\tTabbed",
    "<div hidden>",
    "[x]: https://example.org",
    "| a | b |",
    "|---|---|",
]


@pytest.mark.parametrize("parser_name", sorted(PARSERS))
def test_line_encoding_never_opens_a_block(parser_name: str) -> None:
    parser = PARSERS[parser_name]
    failures = []
    for text in LINE_START_TEXTS:
        tokens = parser.parse(encode_line(text) + "\n")
        types = [token.type for token in tokens]
        inline = tokens[1] if len(tokens) == 3 else None
        children = [] if inline is None else inline.children or []
        value = "".join(child.content for child in children)
        if (
            types != ["paragraph_open", "inline", "paragraph_close"]
            or {child.type for child in children} != {"text"}
            or value.replace(NBSP, " ").strip() != shown(text).strip()
        ):
            failures.append((text, types, value))

    assert failures == []


@pytest.mark.parametrize("parser_name", sorted(PARSERS))
def test_quote_encoding_stays_one_block_quote(parser_name: str) -> None:
    parser = PARSERS[parser_name]
    text = "\n".join([*LINE_START_TEXTS, "", "after blank", "", "    code after blank"])
    tokens = parser.parse(encode_quote(text) + "\n")

    assert tokens[0].type == "blockquote_open"
    assert tokens[-1].type == "blockquote_close"
    inner = tokens[1:-1]
    assert {token.type for token in inner} == {
        "paragraph_open",
        "inline",
        "paragraph_close",
    }
    assert sum(token.type == "paragraph_open" for token in inner) == 3
    lines: list[str] = []
    for token in inner:
        if token.type != "inline":
            continue
        child_types = {child.type for child in token.children or []}
        assert child_types <= {"text", "hardbreak"}
        current = ""
        for child in token.children or []:
            if child.type == "hardbreak":
                lines.append(current)
                current = ""
            else:
                current += child.content
        lines.append(current)
    assert [line.replace(NBSP, " ").strip() for line in lines] == [
        shown(line).strip() for line in text.split("\n") if line
    ]
