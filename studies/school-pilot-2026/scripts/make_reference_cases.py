"""Create reference cases with known answers for the component test.

This script only constructs cases. It must not check them: it imports neither
the Inspektorium kernel nor ``check_quotes``. Running either on these cases is
the measurement that follows the preregistration.

A case's expected values come from its type. So that a label cannot be wrong by
accident, every candidate must satisfy them under the plain substring rules in
``_strict_hit`` and ``_normalized_hit``. Those rules restate the README here on
purpose: sharing code with the tool under test would make the test circular.

All choices derive from the seed through SHA-256, not from a random generator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TypeVar

from genius_loader import (
    DEFAULT_BANKS,
    Sentence,
    SentenceBank,
    dump_json,
    read_bank,
)

T = TypeVar("T")
STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = STUDY_ROOT / "prereg" / "seed.txt"
DEFAULT_SELECTION = STUDY_ROOT / "prereg" / "selection.json"
DEFAULT_SELECTED = STUDY_ROOT / "data" / "selected"
DEFAULT_DEV = STUDY_ROOT / "data" / "reference_cases_dev.json"
DEFAULT_SEALED = STUDY_ROOT / "sealed" / "holdout_cases.json"
DEFAULT_HASH = STUDY_ROOT / "prereg" / "holdout_sha256.txt"
DEFAULT_SUMMARY = STUDY_ROOT / "prereg" / "reference_cases_summary.json"

CASES_PER_TYPE = 2
"""Per text and type, each from a different sentence where possible."""
DEVELOPMENT_SHARE_PERCENT = 70
FABRICATION_SOURCE_TEXTS = 8
"""Reserve texts opened for ``fabricated`` cases; the others stay unread."""
MIN_FRAGMENT_TOKENS = 4
MAX_FRAGMENT_TOKENS = 8
MIN_FABRICATED_TOKENS = 6
MAX_ATTEMPTS = 6

# Each case type maps to its expected (strict, normalized) validity.
EXPECTED: dict[str, tuple[bool, bool]] = {
    "valid_exact": (True, True),
    "wrong_location": (False, False),
    "altered_number": (False, False),
    "altered_word": (False, False),
    "fabricated": (False, False),
    "case_change": (False, False),
    "format_variant": (False, True),
    "punctuation_added": (False, True),
}

FINAL_MARKS = ".!?"
_DOUBLE_QUOTES = "„“”‟«»"
_SINGLE_QUOTES = "‚‘’‛‹›"
_VARIANT_SPACES = (" ", " ", " ")
_TYPOGRAPHIC_FOR = {'"': "“", "'": "’"}
_NUMBER = re.compile(r"(?<![\w.,])[0-9]+(?:[.,][0-9]+)?(?!\w)")
_TOKEN = re.compile(r"\S+")
_WORD = re.compile(r"[^\W\d_]{4,}")


class ReferenceCaseError(RuntimeError):
    """The inputs cannot produce the agreed reference cases."""


@dataclass(frozen=True)
class Case:
    case_id: str
    text_id: str
    claimed_sid: str
    quote: str
    type: str
    expected_strict: bool
    expected_normalized: bool


Candidate = tuple[str, str]
"""A claimed sentence id and a quote."""


def _rank(*parts: object) -> int:
    joined = ":".join(str(part) for part in parts)
    return int(hashlib.sha256(joined.encode()).hexdigest(), 16)


def _shuffled(
    items: Sequence[T], key: Callable[[T], object], *parts: object
) -> list[T]:
    return sorted(items, key=lambda item: _rank(*parts, key(item)))


def _loose(text: str) -> str:
    """Spaces and quotation marks as the normalized mode compares them."""

    characters = []
    for character in text:
        if character.isspace():
            characters.append(" ")
        elif character in _DOUBLE_QUOTES:
            characters.append('"')
        elif character in _SINGLE_QUOTES:
            characters.append("'")
        else:
            characters.append(character)
    return "".join(characters)


def _strict_hit(quote: str, sentence: str) -> bool:
    return quote in sentence


def _normalized_hit(quote: str, sentence: str) -> bool:
    loose_quote = _loose(quote)
    loose_sentence = _loose(sentence)
    if loose_quote in loose_sentence:
        return True
    return loose_quote[-1:] in FINAL_MARKS and loose_quote[:-1] in loose_sentence


def label_holds(case_type: str, quote: str, sentence: str) -> bool:
    """Whether the expected values of ``case_type`` are true for this quote."""

    strict, normalized = EXPECTED[case_type]
    return (
        unicodedata.normalize("NFC", quote) == quote
        and _strict_hit(quote, sentence) is strict
        and _normalized_hit(quote, sentence) is normalized
    )


def _tokens(text: str) -> list[re.Match[str]]:
    return list(_TOKEN.finditer(text))


def _fragment(text: str, *parts: object) -> str | None:
    """Pick a run of tokens; a seeded choice of length and position."""

    tokens = _tokens(text)
    if len(tokens) < MIN_FRAGMENT_TOKENS:
        return None
    longest = min(MAX_FRAGMENT_TOKENS, len(tokens))
    size = MIN_FRAGMENT_TOKENS + _rank(*parts, "size") % (
        longest - MIN_FRAGMENT_TOKENS + 1
    )
    first = _rank(*parts, "first") % (len(tokens) - size + 1)
    return text[tokens[first].start() : tokens[first + size - 1].end()]


def _make_valid_exact(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    fragment = context.fragment(sentence, "valid_exact", attempt)
    return None if fragment is None else (sentence.sid, fragment)


def _make_wrong_location(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    fragment = context.fragment(sentence, "wrong_location", attempt)
    if fragment is None:
        return None
    others = [item for item in context.bank.sentences if item.sid != sentence.sid]
    for other in context.shuffled(others, "wrong_location", sentence.sid, attempt):
        if label_holds("wrong_location", fragment, other.text):
            return other.sid, fragment
    return None


def _make_altered_number(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    numbers = list(_NUMBER.finditer(sentence.text))
    if not numbers:
        return None
    number = numbers[_rank(context.seed, sentence.sid, attempt) % len(numbers)]
    tokens = _tokens(sentence.text)
    index = next(
        position
        for position, token in enumerate(tokens)
        if token.start() <= number.start() < token.end()
    )
    first = tokens[max(0, index - 2)].start()
    last = tokens[min(len(tokens) - 1, index + 2)].end()
    digit = number.end() - 1
    changed = str((int(sentence.text[digit]) + 1) % 10)
    return (
        sentence.sid,
        sentence.text[first:digit] + changed + sentence.text[digit + 1 : last],
    )


def _make_altered_word(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    fragment = context.fragment(sentence, "altered_word", attempt)
    if fragment is None:
        return None
    words = list(_WORD.finditer(fragment))
    if not words:
        return None
    target = words[_rank(context.seed, sentence.sid, attempt, "word") % len(words)]
    vocabulary = sorted(
        {found.group() for found in _WORD.finditer(context.bank.full_text)}
    )
    choices = [
        word for word in vocabulary if word.casefold() != target.group().casefold()
    ]
    for word in context.shuffled(choices, "altered_word", sentence.sid, attempt):
        quote = fragment[: target.start()] + word + fragment[target.end() :]
        if label_holds("altered_word", quote, sentence.text):
            return sentence.sid, quote
    return None


def _make_fabricated(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    for candidate in context.shuffled(
        context.fabrication_pool, "fabricated", sentence.sid, attempt
    ):
        if not _normalized_hit(candidate, context.bank.full_text):
            return sentence.sid, candidate
    return None


def _make_case_change(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    fragment = context.fragment(sentence, "case_change", attempt)
    if fragment is None:
        return None
    tokens = [
        token
        for token in _tokens(fragment)
        if token.group()[0].isalpha()
        and len(token.group()[0].swapcase()) == 1
        and token.group()[0].swapcase() != token.group()[0]
    ]
    if not tokens:
        return None
    token = tokens[_rank(context.seed, sentence.sid, attempt, "case") % len(tokens)]
    first = token.start()
    return (
        sentence.sid,
        fragment[:first] + fragment[first].swapcase() + fragment[first + 1 :],
    )


def _make_format_variant(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    fragment = context.fragment(sentence, "format_variant", attempt)
    if fragment is None:
        return None
    straight = [mark for mark in _TYPOGRAPHIC_FOR if mark in fragment]
    if straight and attempt % 2 == 0:
        mark = straight[0]
        return sentence.sid, fragment.replace(mark, _TYPOGRAPHIC_FOR[mark], 1)
    spaces = [match.start() for match in re.finditer(" ", fragment)]
    if not spaces:
        return None
    position = spaces[_rank(context.seed, sentence.sid, attempt, "gap") % len(spaces)]
    space = _VARIANT_SPACES[
        _rank(context.seed, sentence.sid, attempt, "space") % len(_VARIANT_SPACES)
    ]
    return sentence.sid, fragment[:position] + space + fragment[position + 1 :]


def _make_punctuation_added(
    context: _Context, sentence: Sentence, attempt: int
) -> Candidate | None:
    """Add a final mark. The omitted variant cannot exist in this type.

    A quote that merely lacks the sentence's final mark is a literal part of
    the sentence, so strict mode accepts it. ``label_holds`` rejects it.
    """

    fragment = context.fragment(sentence, "punctuation_added", attempt)
    if fragment is None:
        return None
    trimmed = fragment.rstrip(".,;:!?)\"'´")
    marks = context.shuffled(
        list(FINAL_MARKS), "punctuation_added", sentence.sid, attempt
    )
    for mark in marks:
        if label_holds("punctuation_added", trimmed + mark, sentence.text):
            return sentence.sid, trimmed + mark
    return None


BUILDERS: dict[str, Callable[[_Context, Sentence, int], Candidate | None]] = {
    "valid_exact": _make_valid_exact,
    "wrong_location": _make_wrong_location,
    "altered_number": _make_altered_number,
    "altered_word": _make_altered_word,
    "fabricated": _make_fabricated,
    "case_change": _make_case_change,
    "format_variant": _make_format_variant,
    "punctuation_added": _make_punctuation_added,
}


@dataclass(frozen=True)
class _Context:
    bank: SentenceBank
    seed: int
    fabrication_pool: tuple[str, ...]

    def fragment(self, sentence: Sentence, *parts: object) -> str | None:
        return _fragment(
            sentence.text, self.seed, self.bank.text_id, sentence.sid, *parts
        )

    def shuffled(self, items: Sequence[T], *parts: object) -> list[T]:
        return _shuffled(items, str, self.seed, self.bank.text_id, *parts)


def cases_for_text(
    bank: SentenceBank, seed: int, fabrication_pool: tuple[str, ...]
) -> list[Case]:
    """Build up to ``CASES_PER_TYPE`` cases of each type for one text."""

    context = _Context(bank, seed, fabrication_pool)
    by_sid = {sentence.sid: sentence for sentence in bank.sentences}
    cases: list[Case] = []
    for case_type, build in BUILDERS.items():
        strict, normalized = EXPECTED[case_type]
        chosen: list[Candidate] = []
        used_sentences: set[str] = set()
        ordered = _shuffled(
            bank.sentences, lambda item: item.sid, seed, bank.text_id, case_type
        )
        for attempt in range(MAX_ATTEMPTS):
            for sentence in ordered:
                if len(chosen) == CASES_PER_TYPE:
                    break
                if sentence.sid in used_sentences:
                    continue
                candidate = build(context, sentence, attempt)
                if candidate is None or candidate in chosen:
                    continue
                claimed, quote = candidate
                if not label_holds(case_type, quote, by_sid[claimed].text):
                    continue
                chosen.append(candidate)
                used_sentences.add(sentence.sid)
        for number, (claimed, quote) in enumerate(chosen, start=1):
            cases.append(
                Case(
                    case_id=f"{bank.text_id}.{case_type}.{number}",
                    text_id=bank.text_id,
                    claimed_sid=claimed,
                    quote=quote,
                    type=case_type,
                    expected_strict=strict,
                    expected_normalized=normalized,
                )
            )
    return cases


def split_cases(cases: list[Case], seed: int) -> tuple[list[Case], list[Case]]:
    """Split each type 70/30 by a seeded ranking of the case ids."""

    development: list[Case] = []
    held_out: list[Case] = []
    for case_type in EXPECTED:
        group = [case for case in cases if case.type == case_type]
        ranked = sorted(group, key=lambda case: _rank(seed, "split", case.case_id))
        cut = (len(ranked) * DEVELOPMENT_SHARE_PERCENT + 50) // 100
        development.extend(ranked[:cut])
        held_out.extend(ranked[cut:])
    return (
        sorted(development, key=lambda case: case.case_id),
        sorted(held_out, key=lambda case: case.case_id),
    )


def fabrication_pool(
    reserve_ids: list[str], banks: Path, seed: int
) -> tuple[list[str], tuple[str, ...]]:
    """Open a few reserve texts and return their ids and usable sentences."""

    opened = _shuffled(reserve_ids, str, seed, "fabrication")[:FABRICATION_SOURCE_TEXTS]
    sentences = [
        sentence.text
        for text_id in opened
        for sentence in read_bank(banks / f"{text_id}.json").sentences
        if len(_tokens(sentence.text)) >= MIN_FABRICATED_TOKENS
    ]
    return opened, tuple(sentences)


def _as_json(cases: list[Case]) -> bytes:
    return dump_json([asdict(case) for case in cases])


def write_cases(
    development: list[Case],
    held_out: list[Case],
    dev_path: Path,
    sealed_path: Path,
    hash_path: Path,
) -> str:
    """Write both parts and return the SHA-256 of the sealed file.

    An existing sealed file is never replaced. The check only asks whether the
    path exists; it does not open the file.
    """

    if sealed_path.exists():
        raise ReferenceCaseError("an existing sealed file is never replaced")
    dev_path.parent.mkdir(parents=True, exist_ok=True)
    dev_path.write_bytes(_as_json(development))
    payload = _as_json(held_out)
    sealed_path.parent.mkdir(parents=True, exist_ok=True)
    sealed_path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    hash_path.write_text(f"{digest}  sealed/{sealed_path.name}\n", encoding="utf-8")
    return digest


def summarize(
    development: list[Case], held_out: list[Case], opened: list[str]
) -> dict[str, object]:
    """Counts only; nothing here reveals a held-out case."""

    dev_counts = Counter(case.type for case in development)
    held_counts = Counter(case.type for case in held_out)
    return {
        "development": len(development),
        "held_out": len(held_out),
        "by_type": {
            case_type: {
                "development": dev_counts[case_type],
                "held_out": held_counts[case_type],
            }
            for case_type in EXPECTED
        },
        "reserve_texts_opened_for_fabricated": sorted(opened),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-file", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--selected", type=Path, default=DEFAULT_SELECTED)
    parser.add_argument("--banks", type=Path, default=DEFAULT_BANKS)
    parser.add_argument("--dev", type=Path, default=DEFAULT_DEV)
    parser.add_argument("--sealed", type=Path, default=DEFAULT_SEALED)
    parser.add_argument("--hash", type=Path, default=DEFAULT_HASH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args(argv)

    seed = int(args.seed_file.read_text(encoding="utf-8").strip())
    groups = json.loads(args.selection.read_text(encoding="utf-8"))["groups"]
    opened, pool = fabrication_pool(groups["reserve"], args.banks, seed)
    if not pool:
        raise ReferenceCaseError("no reserve sentence is available")
    cases: list[Case] = []
    for text_id in groups["component"]:
        bank = read_bank(args.selected / f"{text_id}.json")
        cases.extend(cases_for_text(bank, seed, pool))
    development, held_out = split_cases(cases, seed)
    digest = write_cases(development, held_out, args.dev, args.sealed, args.hash)
    summary = summarize(development, held_out, opened)
    args.summary.write_bytes(dump_json(summary))
    print(f"development {len(development)}, held out {len(held_out)}, sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
