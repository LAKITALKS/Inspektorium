"""Display encoding for untrusted text embedded in the Markdown report.

The Markdown report combines host-generated structure (headings, labels and
status lines) with text that the host does not control: the evaluator's claim
text, rationale and quotation, and, when a report is deserialized from JSON,
any message or scope text. That text is encoded exactly once, where it is
embedded, by the encoder for its context:

``encode_inline``
    Text that follows a host label on the same line.
``encode_line``
    Text that starts a line or a list item.
``encode_quote``
    A quotation rendered as a Markdown block quote.

Encoding changes only the Markdown display. Report objects, the JSON report,
offsets, raw proposals and fingerprints keep the exact original characters, and
no Unicode normalization is applied.

Display rule:

* Every character in the Unicode general categories Cc, Cf, Cs, Zl and Zp, and
  every code point that is not assigned (category Cn) in the Unicode database
  of the running Python, is shown as a visible marker such as ``⟦U+202E⟧``
  (uppercase hexadecimal, at least four digits). This covers control characters
  including TAB, CR and NEL, bidirectional controls, zero-width characters
  including U+200C ZERO WIDTH NON-JOINER and U+200D ZERO WIDTH JOINER, the line
  and paragraph separators, and noncharacters such as U+FFFE. The only
  exception is LF inside a quotation, which is shown as a line break;
  everywhere else LF is a marker as well. Emoji joined with U+200D and words
  written with U+200C are therefore shown as their parts with markers between
  them. In each consecutive run of nonspacing or enclosing marks (Mn, Me),
  only the first four characters remain raw; the fifth and every later
  character become markers. This also applies to variation selectors (Mn).
  Other invisible characters outside these categories and private-use
  characters (Co) are not marked. The run limit is a text property, not a
  guarantee of visual integrity for every font or viewer.
* Categories come from the ``unicodedata`` module of the running Python, whose
  Unicode version depends on the Python version (Unicode 14.0 in Python 3.11,
  15.1 in Python 3.13). A character assigned in a later Unicode version is
  unassigned (Cn) there and is therefore marked. This keeps format characters
  assigned later, such as U+13439 to U+1343F (Cf since Unicode 15.0), from
  appearing raw on an older Python. In exchange, any other character assigned
  after that version, such as a newer emoji, is also shown as a marker there.
* The marker brackets U+27E6 and U+27E7 are themselves always shown as markers,
  so embedded text cannot write a marker with these exact brackets. Look-alike
  brackets such as U+301A and U+301B are not marked and can make text look like
  a marker; they add no structure.
* ``@`` is shown as ``⟦U+0040⟧``. Unlike an escaped or entity-encoded ``@``,
  this prevents the cmark-gfm autolink extension from creating e-mail links,
  including addresses with a ``mailto:`` or ``xmpp:`` prefix.
* ``<`` and ``&`` become the entity references ``&lt;`` and ``&amp;``, the
  ASCII characters in ``ALWAYS_ESCAPED`` are escaped wherever they occur, and
  ``.``, ``:`` and ``/`` are escaped unless a space or the end of the text
  follows them (``.`` is also escaped after ``www``). This blocks raw HTML,
  entity references, emphasis, code, links, tables, strikethrough and URL,
  ``www.`` and domain autolinks while leaving ordinary sentence punctuation
  unchanged.
* At the start of a line, leading spaces become U+00A0 NO-BREAK SPACE, a
  leading ASCII punctuation character is escaped, and the ``.`` or ``)`` of an
  ordered-list marker is escaped, so no heading, list, quote, fence, table,
  thematic break, HTML block or indented code block can begin.
* A character is escaped with a backslash only if it is in
  ``PORTABLE_BACKSLASH_ESCAPES``, the ASCII punctuation that both CommonMark
  and Python-Markdown accept after a backslash. Every other ASCII punctuation
  character is written as a decimal numeric character reference such as
  ``&#58;``, which renderers decode as literal text after the Markdown
  structure has been parsed. Python-Markdown, which keeps a backslash before
  other characters as literal text, therefore never shows a stray backslash.
* Lines of a quotation that are followed by another non-empty line end with
  two spaces, the hard line break that CommonMark, GitHub Flavored Markdown and
  Python-Markdown all render as a line break without raw HTML. An empty line
  ends the paragraph; several consecutive empty lines are shown as one
  paragraph break. A tool that strips trailing spaces from the Markdown file
  joins such lines into one displayed line; the text and structure stay intact.
"""

from __future__ import annotations

import re
import string
import unicodedata

MARKER_OPEN = "\N{MATHEMATICAL LEFT WHITE SQUARE BRACKET}"
MARKER_CLOSE = "\N{MATHEMATICAL RIGHT WHITE SQUARE BRACKET}"

MARKED_CATEGORIES = frozenset({"Cc", "Cf", "Cn", "Cs", "Zl", "Zp"})
_COMBINING_CATEGORIES = frozenset({"Mn", "Me"})
_MAX_RAW_COMBINING_RUN = 4
ENTITY_ESCAPED = {"<": "&lt;", "&": "&amp;"}
PORTABLE_BACKSLASH_ESCAPES = frozenset("\\`*_{}[]()>#+-.!")
ALWAYS_ESCAPED = frozenset("<&\\`*_[]~|$")
LINK_PUNCTUATION = frozenset(".:/")
QUOTE_LINE_BREAK = "  "

_ASCII_PUNCTUATION = frozenset(string.punctuation)
_NO_BREAK_SPACE = "\N{NO-BREAK SPACE}"
_ORDERED_LIST_MARKER = re.compile(r"[0-9]+[.)]")
_IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*")
_IDENTIFIER_MAX_LENGTH = 80


def display_marker(character: str) -> str:
    """Return the visible marker for one character, such as ``⟦U+202E⟧``."""

    return f"{MARKER_OPEN}U+{ord(character):04X}{MARKER_CLOSE}"


def is_marked(character: str) -> bool:
    """Whether a character is always marked, independently of its context."""

    if character in (MARKER_OPEN, MARKER_CLOSE, "@"):
        return True
    return unicodedata.category(character) in MARKED_CATEGORIES


def escape_punctuation(character: str) -> str:
    """Escape one ASCII punctuation character so it is shown literally."""

    if character in ENTITY_ESCAPED:
        return ENTITY_ESCAPED[character]
    if character in PORTABLE_BACKSLASH_ESCAPES:
        return "\\" + character
    return f"&#{ord(character)};"


def _escapes_link_punctuation(text: str, index: int) -> bool:
    following = text[index + 1] if index + 1 < len(text) else " "
    if following != " ":
        return True
    return text[index] == "." and text[max(0, index - 3) : index].lower() == "www"


def _encode_character(text: str, index: int) -> str:
    character = text[index]
    if is_marked(character):
        return display_marker(character)
    if (
        unicodedata.category(character) in _COMBINING_CATEGORIES
        and index >= _MAX_RAW_COMBINING_RUN
        and all(
            unicodedata.category(previous) in _COMBINING_CATEGORIES
            for previous in text[index - _MAX_RAW_COMBINING_RUN : index]
        )
    ):
        # Inspect at most four preceding characters, even for very long runs.
        return display_marker(character)
    if character in ALWAYS_ESCAPED or (
        character in LINK_PUNCTUATION and _escapes_link_punctuation(text, index)
    ):
        return escape_punctuation(character)
    return character


def encode_inline(text: str) -> str:
    """Encode text that follows a host label on the same line."""

    return "".join(_encode_character(text, index) for index in range(len(text)))


def encode_line(text: str) -> str:
    """Encode text that starts a line or a list item."""

    content = text.lstrip(" ")
    pieces = [_encode_character(content, index) for index in range(len(content))]
    protected = 0
    marker = _ORDERED_LIST_MARKER.match(content)
    if marker is not None:
        protected = marker.end() - 1
    if pieces and content[protected] in _ASCII_PUNCTUATION:
        if pieces[protected] == content[protected]:
            pieces[protected] = escape_punctuation(content[protected])
    indent = _NO_BREAK_SPACE * (len(text) - len(content))
    return indent + "".join(pieces)


def encode_quote(text: str) -> str:
    """Encode a quotation as a block quote that keeps its LF-separated lines.

    Only LF separates lines. Each line is encoded with ``encode_line``; a line
    followed by a non-empty line ends with ``QUOTE_LINE_BREAK`` (two spaces, a
    hard line break) so that the lines stay visibly separate, and an empty line
    becomes ``>``.
    """

    lines = [encode_line(line) for line in text.split("\n")]
    rendered: list[str] = []
    for index, line in enumerate(lines):
        if not line:
            rendered.append(">")
        elif index + 1 < len(lines) and lines[index + 1]:
            rendered.append(f"> {line}{QUOTE_LINE_BREAK}")
        else:
            rendered.append(f"> {line}")
    return "\n".join(rendered)


def encode_identifier(value: str) -> str:
    """Show a schema identifier as code, or as encoded text if it is not one."""

    if len(value) <= _IDENTIFIER_MAX_LENGTH and _IDENTIFIER.fullmatch(value):
        return f"`{value}`"
    return encode_inline(value)


__all__ = [
    "ALWAYS_ESCAPED",
    "ENTITY_ESCAPED",
    "LINK_PUNCTUATION",
    "MARKED_CATEGORIES",
    "MARKER_CLOSE",
    "MARKER_OPEN",
    "PORTABLE_BACKSLASH_ESCAPES",
    "QUOTE_LINE_BREAK",
    "display_marker",
    "encode_identifier",
    "encode_inline",
    "encode_line",
    "encode_quote",
    "escape_punctuation",
    "is_marked",
]
