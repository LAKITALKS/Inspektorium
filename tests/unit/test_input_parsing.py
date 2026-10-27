"""Strict JSON helpers and the strict InspectionInput parser.

These tests target helpers introduced in v0.1.1 (``load_strict_json`` and
``parse_inspection_input_json``). The CLI-level counterproofs that also run on
v0.1.0 live in ``test_cli_input_rejection.py``.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError, field_validator

from inspektorium.core.fingerprints import canonical_bundle_json, fingerprint_input
from inspektorium.core.models import InspectionInput
from inspektorium.core.strict_json import (
    MAX_NESTING_DEPTH,
    StrictJSONError,
    display_key,
    load_strict_json,
)
from inspektorium.providers.parsing import (
    InputParseError,
    _schema_error_summary,
    parse_inspection_input_json,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples" / "inspect"
EXAMPLE_NAMES = (
    "01_supported",
    "02_contradicted",
    "03_not_established",
    "04_attribution_mismatch",
    "05_mixed_and_fabricated_quote",
)
BOM = chr(0xFEFF)

CLEAN = '{"answer": {"text": "A"}, "sources": [{"source_id": "s", "text": "T"}]}'


def _doc(answer: str = '"text": "A"', sources: str = "", top: str = "") -> str:
    source_list = sources or '{"source_id": "s", "text": "T"}'
    return f'{{{top}"answer": {{{answer}}}, "sources": [{source_list}]}}'


@pytest.fixture
def default_int_digit_limit() -> Iterator[None]:
    previous = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(4300)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(previous)


# --- load_strict_json -------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        CLEAN,
        '{"a": [1, 2.5, -0, true, false, null, "x"], "b": {"c": {}}}',
        "  [ ]  \n\t\r",
        '"\\ud83d\\ude00 pair, \\u00e9, \\/ and \\u0000"',
        "1e400",
    ],
)
def test_strict_loader_matches_the_standard_decoder_on_clean_json(raw: str) -> None:
    assert load_strict_json(raw) == json.loads(raw)


@pytest.mark.parametrize(
    ("raw", "key"),
    [
        ('{"a": 1, "a": 1}', "a"),
        ('{"outer": {"a": 1, "a": 2}}', "a"),
        ('[{"ok": 1}, {"list": [{"deep": {"x": 1, "x": 2}}]}]', "x"),
        ('{"text": "A", "\\u0074ext": "B"}', "text"),
        ('{"a/b": 1, "a\\/b": 2}', "a/b"),
        ('{"\\u00e9": 1, "\u00e9": 2}', "\u00e9"),
    ],
)
def test_duplicate_keys_are_rejected_at_every_level_after_decoding(
    raw: str, key: str
) -> None:
    with pytest.raises(StrictJSONError) as exc_info:
        load_strict_json(raw)

    assert type(exc_info.value) is StrictJSONError
    assert str(exc_info.value) == f"duplicate object key {ascii(key)}"


def test_keys_that_differ_only_by_unicode_normalization_are_distinct() -> None:
    # JSON compares decoded code points; no Unicode normalization is applied.
    assert load_strict_json('{"\\u00e9": 1, "e\\u0301": 2}') == {
        "\u00e9": 1,
        "e\u0301": 2,
    }


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_non_standard_constants_are_rejected(constant: str) -> None:
    with pytest.raises(StrictJSONError) as exc_info:
        load_strict_json(f'{{"value": [{constant}]}}')

    assert str(exc_info.value) == f"non-standard JSON constant {constant}"


@pytest.mark.parametrize(
    "raw",
    [
        '"\\ud800"',
        '"\\udfff"',
        '"tail \\ud83d"',
        '"\\ude00\\ud83d"',
        '{"\\ud800": 1}',
        '{"a": [[{"b": "x\\udc00"}]]}',
        '"' + chr(0xD800) + '"',
    ],
)
def test_unpaired_surrogates_are_rejected_in_values_and_keys(raw: str) -> None:
    with pytest.raises(StrictJSONError, match="unpaired UTF-16 surrogate"):
        load_strict_json(raw)


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        ("", "Expecting value (line 1, column 1)"),
        ("   ", "Expecting value (line 1, column 4)"),
        ('{"a": 1} {"b": 2}', "Extra data (line 1, column 10)"),
        ('{"a": 1}\n]', "Extra data (line 2, column 1)"),
        ("{'a': 1}", "Expecting property name enclosed in double quotes"),
        # Python 3.13 reports trailing commas with a more specific reason.
        ('{"a": 1,}', ("Expecting property name", "Illegal trailing comma")),
        ("[1, 2,]", ("Expecting value", "Illegal trailing comma")),
        ('{"a": 1 /* c */}', "Expecting ',' delimiter"),
        ('"tab\tinside"', "Invalid control character"),
        ('"\\x41"', "Invalid \\escape"),
        ('"\\u12"', "Invalid \\uXXXX escape"),
        ('"open', "Unterminated string starting"),
        ("01", "Extra data"),
        ("+1", "Expecting value"),
        (".5", "Expecting value"),
        ("\f{}", "Expecting value"),
        ("{}\u00a0", "Extra data"),
    ],
)
def test_invalid_json_is_rejected_with_a_bounded_reason(
    raw: str, reason: str | tuple[str, ...]
) -> None:
    with pytest.raises(StrictJSONError) as exc_info:
        load_strict_json(raw)

    assert type(exc_info.value) is StrictJSONError
    assert str(exc_info.value).startswith(reason)


def test_byte_order_mark_is_rejected_for_text_and_bytes() -> None:
    for raw in (BOM + CLEAN, (BOM + CLEAN).encode("utf-8")):
        with pytest.raises(StrictJSONError, match="byte order mark"):
            load_strict_json(raw)


def test_utf8_bytes_are_accepted_and_other_encodings_are_not() -> None:
    assert load_strict_json(CLEAN.encode("utf-8")) == json.loads(CLEAN)
    assert load_strict_json(bytearray(b'{"a": "\\u00e9"}')) == {"a": "\u00e9"}

    for raw in (
        CLEAN.encode("utf-16"),
        CLEAN.encode("utf-32"),
        b'{"a": "\xff"}',
        b'{"a": "\xed\xa0\x80"}',
    ):
        with pytest.raises(StrictJSONError, match="not valid UTF-8"):
            load_strict_json(raw)


def test_non_text_input_is_rejected() -> None:
    with pytest.raises(StrictJSONError, match="must be str or UTF-8 bytes"):
        load_strict_json(None)  # type: ignore[arg-type]


def test_nesting_up_to_the_limit_is_accepted() -> None:
    raw = "[" * MAX_NESTING_DEPTH + "]" * MAX_NESTING_DEPTH
    nested = load_strict_json(raw)
    for _ in range(MAX_NESTING_DEPTH - 1):
        assert isinstance(nested, list)
        nested = nested[0]
    assert nested == []


@pytest.mark.parametrize(
    "raw",
    [
        "[" * (MAX_NESTING_DEPTH + 1) + "]" * (MAX_NESTING_DEPTH + 1),
        '{"a": ' * (MAX_NESTING_DEPTH + 1) + "1" + "}" * (MAX_NESTING_DEPTH + 1),
        "[" * 100_000 + "]" * 100_000,
        '{"a": ' * 100_000,
    ],
)
def test_excessive_nesting_fails_cleanly_without_recursion_error(raw: str) -> None:
    with pytest.raises(StrictJSONError) as exc_info:
        load_strict_json(raw)

    assert str(exc_info.value) == (
        f"nesting is deeper than {MAX_NESTING_DEPTH} arrays or objects"
    )


def test_overlong_integer_literal_is_rejected(default_int_digit_limit: None) -> None:
    with pytest.raises(StrictJSONError, match="integer literal is too long"):
        load_strict_json("9" * 5_000)


def test_display_key_is_bounded_and_ascii() -> None:
    key = "\x1b[2J\u202e" + "k" * 10_000

    shown = display_key(key)

    assert shown.isascii()
    assert "\x1b" not in shown
    assert shown.endswith("...")
    assert len(shown) < 80
    assert display_key("text") == "'text'"


def test_duplicate_key_message_is_bounded() -> None:
    key = "x" * 100_000
    with pytest.raises(StrictJSONError) as exc_info:
        load_strict_json(json.dumps({key: 1})[:-1] + f', "{key}": 2}}')

    assert len(str(exc_info.value)) < 100


# --- parse_inspection_input_json: clean inputs are unchanged ---------------


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_examples_parse_to_the_same_model_and_fingerprints(example_name: str) -> None:
    directory = EXAMPLES / example_name
    raw = (directory / "input.json").read_text(encoding="utf-8")
    expected_report = json.loads(
        (directory / "expected_report.json").read_text(encoding="utf-8")
    )

    previous = InspectionInput.model_validate_json(raw)
    strict = parse_inspection_input_json(raw)

    assert strict == previous
    assert strict.model_dump() == previous.model_dump()
    assert strict.model_fields_set == previous.model_fields_set
    assert canonical_bundle_json(strict) == canonical_bundle_json(previous)
    assert fingerprint_input(strict) == fingerprint_input(previous)
    assert (
        fingerprint_input(strict).model_dump(mode="json")
        == expected_report["fingerprints"]
    )


def test_fixture_input_round_trips_through_the_strict_parser(
    inspection_input: InspectionInput,
) -> None:
    raw = json.dumps(inspection_input.model_dump(mode="json"), ensure_ascii=False)

    assert parse_inspection_input_json(raw) == inspection_input
    assert parse_inspection_input_json(raw) == InspectionInput.model_validate_json(raw)


def test_raw_bytes_are_not_hashed_only_canonical_text_is() -> None:
    compact = (
        '{"answer":{"text":"Caf\\u00e9\\r\\nopen."},'
        '"sources":[{"source_id":"s","text":"Cafe\\u0301\\ropen."}]}'
    )
    spaced = (
        '{\r\n  "schema_version": "0.1",\r\n'
        '  "sources": [ {"text": "Caf\u00e9\\nopen.",'
        ' "title": "Ignored by fingerprints", "source_id": "s"} ],\r\n'
        '  "answer": {"answer_id": "answer", "text": "Cafe\u0301\\nopen."}\r\n}'
    )

    first = parse_inspection_input_json(compact)
    second = parse_inspection_input_json(spaced)

    assert compact.encode("utf-8") != spaced.encode("utf-8")
    assert first.answer.text == second.answer.text == "Caf\u00e9\nopen."
    assert fingerprint_input(first) == fingerprint_input(second)
    assert fingerprint_input(first) == fingerprint_input(
        InspectionInput.model_validate_json(spaced)
    )


# --- parse_inspection_input_json: never more permissive than v0.1.0 ---------

_S = '{"source_id": "s", "text": "T"}'

DIFFERENTIAL_CORPUS: dict[str, str] = {
    # Clean documents (accepted before and after, with equal models).
    "minimal": CLEAN,
    "explicit_defaults": _doc(
        '"answer_id": "answer", "text": "A"', top='"schema_version": "0.1", '
    ),
    "pretty_printed": json.dumps(json.loads(CLEAN), indent=4),
    "reordered_keys": (
        '{"sources": [{"text": "T", "source_id": "s"}], "answer": {"text": "A"}}'
    ),
    "escaped_letters": _doc('"\\u0074ext": "\\u0041"'),
    "escaped_solidus": _doc('"text": "a\\/b"'),
    "surrogate_pair": _doc('"text": "\\ud83d\\ude00"'),
    "raw_astral": _doc('"text": "\U0001f600"'),
    "nul_and_del": _doc('"text": "A\\u0000B\x7f"'),
    "crlf_escapes": _doc('"text": "A\\r\\nB\\rC"'),
    "nfd_text": _doc('"text": "e\\u0301"'),
    "rtl_and_greek": _doc(
        '"text": "\u05e9\u05dc\u05d5\u05dd \u0391\u03b8\u03ae\u03bd\u03b1"'
    ),
    "title_null": _doc(sources='{"source_id": "s", "title": null, "text": "T"}'),
    "title_set": _doc(sources='{"source_id": "s", "title": "Guide", "text": "T"}'),
    "two_sources": _doc(sources=f'{_S}, {{"source_id": "t-2", "text": "U"}}'),
    "identifier_forms": _doc(
        '"answer_id": "a1-b_2", "text": "A"',
        sources='{"source_id": "x9_y-z", "text": "T"}',
    ),
    "long_text": _doc('"text": "' + "word " * 5_000 + '"'),
    "trailing_whitespace": CLEAN + " \n\t\r ",
    "leading_whitespace_and_crlf": "\t\r\n " + CLEAN.replace(", ", ",\r\n"),
    "raw_line_separator": _doc('"text": "A' + chr(0x2028) + 'B"'),
    "raw_c1_control": _doc('"text": "A' + chr(0x85) + 'B"'),
    "raw_noncharacter": _doc('"text": "A' + chr(0xFFFE) + '"'),
    "raw_max_code_point": _doc('"text": "' + chr(0x10FFFF) + '"'),
    "bom_inside_string": _doc('"text": "' + BOM + 'A"'),
    # Documents rejected before and after.
    "empty": "",
    "whitespace_only": " \n",
    "top_level_array": "[]",
    "top_level_null": "null",
    "top_level_string": '"text"',
    "missing_answer": f'{{"sources": [{_S}]}}',
    "missing_sources": '{"answer": {"text": "A"}}',
    "missing_text": _doc('"answer_id": "answer"'),
    "empty_text": _doc('"text": ""'),
    "empty_sources": '{"answer": {"text": "A"}, "sources": []}',
    "text_int": _doc('"text": 1'),
    "text_float": _doc('"text": 1.0'),
    "text_bool": _doc('"text": true'),
    "text_null": _doc('"text": null'),
    "text_array": _doc('"text": ["A"]'),
    "answer_string": f'{{"answer": "A", "sources": [{_S}]}}',
    "answer_array": f'{{"answer": [["text", "A"]], "sources": [{_S}]}}',
    "sources_object": f'{{"answer": {{"text": "A"}}, "sources": {_S}}}',
    "sources_string": '{"answer": {"text": "A"}, "sources": "s"}',
    "sources_nested_list": f'{{"answer": {{"text": "A"}}, "sources": [[{_S}]]}}',
    "schema_number": _doc(top='"schema_version": 0.1, '),
    "schema_other": _doc(top='"schema_version": "0.2", '),
    "schema_padded": _doc(top='"schema_version": "0.1 ", '),
    "schema_null": _doc(top='"schema_version": null, '),
    "extra_top": _doc(top='"extra": 1, '),
    "extra_answer": _doc('"text": "A", "extra": 1'),
    "extra_source": _doc(sources='{"source_id": "s", "text": "T", "extra": 1}'),
    "extra_nested_duplicate": _doc(top='"extra": {"a": 1, "a": 2}, '),
    "uppercase_identifier": _doc(sources='{"source_id": "S", "text": "T"}'),
    "identifier_too_long": _doc(
        sources='{"source_id": "' + "a" * 81 + '", "text": "T"}'
    ),
    "duplicate_source_ids": _doc(sources=f"{_S}, {_S}"),
    "empty_title": _doc(sources='{"source_id": "s", "title": "", "text": "T"}'),
    "answer_id_number": _doc('"answer_id": 7, "text": "A"'),
    "answer_id_overflow_float": _doc('"answer_id": 1e400, "text": "A"'),
    "answer_id_negative_zero": _doc('"answer_id": -0, "text": "A"'),
    "nan_extra": _doc(top='"extra": NaN, '),
    "infinity_answer_id": _doc('"answer_id": Infinity, "text": "A"'),
    "negative_infinity_title": _doc(
        sources='{"source_id": "s", "title": -Infinity, "text": "T"}'
    ),
    "lone_high_surrogate": _doc('"text": "A\\ud800"'),
    "lone_low_surrogate": _doc('"text": "\\udc00"'),
    "reversed_pair": _doc('"text": "\\ude00\\ud83d"'),
    "lone_surrogate_key": _doc('"text": "A", "x\\ud800": 1'),
    "byte_order_mark": BOM + CLEAN,
    "trailing_data": CLEAN + " x",
    "trailing_object": CLEAN + "{}",
    "raw_tab_in_string": _doc('"text": "A\tB"'),
    "raw_newline_in_string": _doc('"text": "A\nB"'),
    "form_feed_whitespace": CLEAN.replace(", ", ",\f"),
    "vertical_tab_whitespace": CLEAN.replace(", ", ",\v"),
    "nbsp_whitespace": CLEAN.replace(", ", ",\u00a0"),
    "single_quotes": CLEAN.replace('"', "'"),
    "trailing_comma": _doc(sources=f"{_S},"),
    "comment": CLEAN.replace(", ", ", /* c */ ", 1),
    "invalid_escape": _doc('"text": "\\x41"'),
    "short_unicode_escape": _doc('"text": "\\u12"'),
    "leading_zero": _doc('"answer_id": 01, "text": "A"'),
    "plus_sign": _doc('"answer_id": +1, "text": "A"'),
    "overlong_integer": _doc('"answer_id": ' + "9" * 5_000 + ', "text": "A"'),
    "nested_200": _doc(top='"extra": ' + "[" * 200 + "]" * 200 + ", "),
    "nested_300": _doc(top='"extra": ' + "[" * 300 + "]" * 300 + ", "),
    "nested_900_text": _doc('"text": ' + "[" * 900 + "]" * 900),
    "nested_100k": "[" * 100_000 + "]" * 100_000,
}

# v0.1.0 accepted these ambiguous documents ("last value wins").
NEWLY_REJECTED: dict[str, str] = {
    "duplicate_text": _doc('"text": "A", "text": "B"'),
    "duplicate_text_identical": _doc('"text": "A", "text": "A"'),
    "duplicate_text_escaped": _doc('"text": "A", "\\u0074ext": "B"'),
    "duplicate_answer_id": _doc('"answer_id": "a", "answer_id": "b", "text": "A"'),
    "duplicate_answer": (
        f'{{"answer": {{"text": "A"}}, "answer": {{"text": "B"}}, "sources": [{_S}]}}'
    ),
    "duplicate_sources": (
        f'{{"answer": {{"text": "A"}}, "sources": [], "sources": [{_S}]}}'
    ),
    "duplicate_schema_version": _doc(
        top='"schema_version": "x", "schema_version": "0.1", '
    ),
    "duplicate_source_text": _doc(
        sources='{"source_id": "s", "text": "T", "text": "U"}'
    ),
    "duplicate_source_id_escaped": _doc(
        sources='{"source_id": "a", "source\\u005fid": "s", "text": "T"}'
    ),
    "duplicate_title_second_source": _doc(
        sources=f'{_S}, {{"source_id": "t", "title": "1", "title": "2", "text": "U"}}'
    ),
}


def _outcome(parse: Callable[[], InspectionInput], errors: Any) -> object:
    try:
        return parse()
    except errors:
        return "rejected"


@pytest.mark.parametrize("name", sorted(DIFFERENTIAL_CORPUS))
def test_strict_parser_matches_v010_acceptance_on_the_corpus(
    name: str, default_int_digit_limit: None
) -> None:
    raw = DIFFERENTIAL_CORPUS[name]

    previous = _outcome(
        lambda: InspectionInput.model_validate_json(raw), ValidationError
    )
    strict = _outcome(lambda: parse_inspection_input_json(raw), InputParseError)

    assert strict == previous
    if isinstance(strict, InspectionInput):
        assert isinstance(previous, InspectionInput)
        assert strict.model_fields_set == previous.model_fields_set
        assert fingerprint_input(strict) == fingerprint_input(previous)


@pytest.mark.parametrize("name", sorted(NEWLY_REJECTED))
def test_ambiguous_documents_accepted_by_v010_are_now_rejected(name: str) -> None:
    raw = NEWLY_REJECTED[name]

    assert isinstance(InspectionInput.model_validate_json(raw), InspectionInput)
    with pytest.raises(InputParseError, match="duplicate object key"):
        parse_inspection_input_json(raw)


def test_corpus_clean_cases_are_really_accepted() -> None:
    accepted = {
        name
        for name, raw in DIFFERENTIAL_CORPUS.items()
        if isinstance(
            _outcome(lambda raw=raw: parse_inspection_input_json(raw), InputParseError),
            InspectionInput,
        )
    }

    assert accepted == {
        "minimal",
        "explicit_defaults",
        "pretty_printed",
        "reordered_keys",
        "escaped_letters",
        "escaped_solidus",
        "surrogate_pair",
        "raw_astral",
        "nul_and_del",
        "crlf_escapes",
        "nfd_text",
        "rtl_and_greek",
        "title_null",
        "title_set",
        "two_sources",
        "identifier_forms",
        "long_text",
        "trailing_whitespace",
        "leading_whitespace_and_crlf",
        "raw_line_separator",
        "raw_c1_control",
        "raw_noncharacter",
        "raw_max_code_point",
        "bom_inside_string",
    }


# --- parse_inspection_input_json: messages ----------------------------------


def test_json_level_rejection_message() -> None:
    with pytest.raises(InputParseError) as exc_info:
        parse_inspection_input_json(_doc('"text": "A", "text": "B"'))

    assert str(exc_info.value) == (
        "Inspection input is not valid JSON: duplicate object key 'text'."
    )
    assert isinstance(exc_info.value.__cause__, StrictJSONError)


def test_schema_rejection_message_names_locations_not_values() -> None:
    raw = _doc(
        '"text": "", "secret-key": "UNTRUSTED-VALUE"',
        sources='{"source_id": "BAD", "text": "T"}',
        top='"schema_version": "9", ',
    )

    with pytest.raises(InputParseError) as exc_info:
        parse_inspection_input_json(raw)

    message = str(exc_info.value)
    assert message.startswith(
        "Inspection input does not conform to the strict public schema: "
        "schema_version: Input should be '0.1'; "
        "answer.text: String should have at least 1 character; "
        "answer.'secret-key': Extra inputs are not permitted (and 2 more)."
    )
    assert "UNTRUSTED-VALUE" not in message
    assert isinstance(exc_info.value.__cause__, ValidationError)


def test_schema_rejection_message_escapes_untrusted_extra_keys() -> None:
    raw = _doc(top='"\\u001b[2J\\u202e": 1, ')

    with pytest.raises(InputParseError) as exc_info:
        parse_inspection_input_json(raw)

    message = str(exc_info.value)
    assert message.isascii()
    assert "'\\x1b[2J\\u202e': Extra inputs are not permitted" in message


def test_model_level_rule_is_reported_without_location() -> None:
    with pytest.raises(InputParseError) as exc_info:
        parse_inspection_input_json(_doc(sources=f"{_S}, {_S}"))

    assert str(exc_info.value) == (
        "Inspection input does not conform to the strict public schema: "
        "Value error, source_id values must be unique."
    )


def test_schema_summary_escapes_non_printable_rule_messages() -> None:
    class Probe(BaseModel):
        value: int

        @field_validator("value")
        @classmethod
        def reject(cls, value: int) -> int:
            raise ValueError("bad \x1b[2J value \u00e9")

    with pytest.raises(ValidationError) as exc_info:
        Probe.model_validate({"value": 1})

    assert _schema_error_summary(exc_info.value) == (
        "value: Value error, bad \\x1b[2J value \\xe9"
    )
