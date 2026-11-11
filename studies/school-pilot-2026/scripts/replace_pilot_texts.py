"""Replace pilot texts without a conclusion zone by reserve texts that have one.

The rule is committed before its first run on the corpus. It leaves no choice:
the candidates are the texts of ``available_reserve`` that meet the rule, in the
stored order of the draw, and the first two are taken. Only the privacy check can
pass over a text, and only in that order.

The check is done by reading. A run without ``--cleared`` names the texts that are
next and writes nothing. A run with ``--cleared`` writes only if these are exactly
the texts the rule takes, after the ``--skip`` entries. The groups of the draw stay
as they are: the result is an added marking in ``prereg/selection.json``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fetch_genius
import genius_loader
from reserve import PILOT_REPLACEMENT, ReserveError, available_reserve
from select_texts import (
    MIN_WORDS,
    RESERVE,
    SelectionError,
    copy_selected,
    draw_order,
    is_eligible,
    read_seed,
)

STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = STUDY_ROOT / "prereg" / "seed.txt"
DEFAULT_SELECTION = STUDY_ROOT / "prereg" / "selection.json"
DEFAULT_SELECTED = STUDY_ROOT / "data" / "selected"

STRUCTURE_COLUMN = "webanno.custom.Struktur|Struktur"
CONCLUSION_LABEL = "Schluss"
# The agreed plausibility count. A different count stops the script.
EXPECTED_CONCLUSION_FILES = 33
REPLACED = ("327_Verk_T1", "975_Verk_T1-rev")
KEPT = "1081_Verk_T1-Rev"
GROUPS_WITHOUT_RESERVE = ("pilot", "component", "validation_holdout")
PRIVACY_REASONS = ("person", "school", "place")
_TEXT_ID = re.compile(r"(?P<number>[0-9]+)_(?P<task>[A-Za-z]+_T[0-9]+)(?:-[Rr]ev)?")


class ReplacementError(SelectionError):
    """The replacement cannot be made, or would not follow the rule."""


@dataclass(frozen=True)
class Profile:
    """What the rule needs to know about one text."""

    word_count: int
    sentences: int
    has_argument_layer: bool
    has_conclusion: bool


def has_conclusion_zone(lines: list[str]) -> bool:
    """Tell by the annotation label; the word in the essay does not count."""

    labels = genius_loader.column_values(lines, STRUCTURE_COLUMN)
    return CONCLUSION_LABEL in labels


def read_profiles(annotations: Path) -> dict[str, Profile]:
    profiles: dict[str, Profile] = {}
    for path in sorted(annotations.glob("*.tsv")):
        item = genius_loader.load_annotation(path)
        profiles[item.bank.text_id] = Profile(
            word_count=item.bank.word_count,
            sentences=len(item.bank.sentences),
            has_argument_layer=item.has_argument_layer,
            has_conclusion=has_conclusion_zone(genius_loader.read_lines(path)),
        )
    return profiles


def check_corpus(selection: Mapping[str, Any], profiles: Mapping[str, Profile]) -> None:
    """Stop on a corpus other than the drawn one or on a different count."""

    if len(profiles) != selection["annotation_files"]:
        raise ReplacementError(
            f"expected {selection['annotation_files']} annotation files, "
            f"found {len(profiles)}"
        )
    zones = sum(profile.has_conclusion for profile in profiles.values())
    if zones != EXPECTED_CONCLUSION_FILES:
        raise ReplacementError(
            f"expected {EXPECTED_CONCLUSION_FILES} files with a conclusion zone, "
            f"found {zones}"
        )


def check_stored_order(selection: Mapping[str, Any], seed: int) -> None:
    """The rule takes the stored order, so it must be the order of the draw."""

    if selection["seed"] != seed:
        raise ReplacementError("the seed file differs from the seed of the draw")
    stored: list[str] = selection["groups"][RESERVE]
    if draw_order(stored, seed) != stored:
        raise ReplacementError("the reserve is not stored in the order of the draw")


def split_text_id(text_id: str) -> tuple[str, str]:
    """Return the student's number and the task of a text."""

    match = _TEXT_ID.fullmatch(text_id)
    if match is None:
        raise ReplacementError(f"cannot read the text id {text_id!r}")
    return match["number"], match["task"]


def find_candidates(
    selection: Mapping[str, Any], profiles: Mapping[str, Profile], kept: str
) -> list[str]:
    """Return the available reserve texts that meet the rule, in stored order."""

    _, task = split_text_id(kept)
    groups = selection["groups"]
    taken_numbers = {
        split_text_id(text_id)[0]
        for name in GROUPS_WITHOUT_RESERVE
        for text_id in groups[name]
    }
    found: list[str] = []
    for text_id in available_reserve(selection):
        profile = profiles.get(text_id)
        if profile is None:
            raise ReplacementError(f"{text_id} has no annotation file")
        number, text_task = split_text_id(text_id)
        if (
            is_eligible(profile.word_count, profile.has_argument_layer)
            and profile.has_conclusion
            and text_task == task
            and number not in taken_numbers
        ):
            found.append(text_id)
    return found


def take_first(
    candidates: Sequence[str], count: int, skips: Sequence[str]
) -> list[str]:
    """Take the first candidates; a skip must lie before the last text taken.

    Two versions of one text never both enter the pilot.
    """

    taken: list[str] = []
    numbers: set[str] = set()
    reached: set[str] = set()
    for text_id in candidates:
        if len(taken) == count:
            break
        if text_id in skips:
            reached.add(text_id)
            continue
        number = split_text_id(text_id)[0]
        if number not in numbers:
            taken.append(text_id)
            numbers.add(number)
    if len(taken) < count:
        raise ReplacementError(f"need {count} texts, the rule leaves {len(taken)}")
    never_reached = set(skips) - reached
    if never_reached:
        raise ReplacementError(f"skips never reached: {sorted(never_reached)}")
    return taken


def read_skip(entry: str) -> tuple[str, str]:
    """Read ``<text_id>=<reason>``; the reason names a kind, never a name."""

    text_id, separator, reason = entry.partition("=")
    if not separator or reason not in PRIVACY_REASONS:
        raise ReplacementError(
            f"a skip needs the form <text_id>=<reason>, reason one of "
            f"{', '.join(PRIVACY_REASONS)}: {entry!r}"
        )
    return text_id, reason


def _rule(kept: str) -> dict[str, object]:
    return {
        "pool": "available_reserve",
        "order": "stored order of the draw",
        "min_words": MIN_WORDS,
        "required_layer": genius_loader.ARGUMENT_LAYER,
        "conclusion_column": STRUCTURE_COLUMN,
        "conclusion_label": CONCLUSION_LABEL,
        "same_task_as": kept,
        "no_version_of_a_text_in": list(GROUPS_WITHOUT_RESERVE),
        "privacy_reasons": list(PRIVACY_REASONS),
    }


def _check_pilot(
    selection: Mapping[str, Any],
    profiles: Mapping[str, Profile],
    replaced: Sequence[str],
    kept: str,
) -> None:
    if PILOT_REPLACEMENT in selection:
        raise ReplacementError("the selection already holds a replacement")
    if sorted([*replaced, kept]) != sorted(selection["groups"]["pilot"]):
        raise ReplacementError("the named texts are not the drawn pilot")
    for text_id in [*replaced, kept]:
        if text_id not in profiles:
            raise ReplacementError(f"{text_id} has no annotation file")
    if any(profiles[text_id].has_conclusion for text_id in replaced):
        raise ReplacementError("a text to be replaced has a conclusion zone")
    if not profiles[kept].has_conclusion:
        raise ReplacementError("the kept text has no conclusion zone")


def next_texts(
    selection: Mapping[str, Any],
    profiles: Mapping[str, Profile],
    replaced: Sequence[str],
    kept: str,
    skips: Mapping[str, str],
) -> list[str]:
    """Return the texts the rule takes, once the skips are passed over."""

    _check_pilot(selection, profiles, replaced, kept)
    candidates = find_candidates(selection, profiles, kept)
    return take_first(candidates, len(replaced), list(skips))


def build_marking(
    selection: Mapping[str, Any],
    profiles: Mapping[str, Profile],
    replaced: Sequence[str],
    kept: str,
    skips: Mapping[str, str],
    cleared: Sequence[str],
) -> dict[str, object]:
    """Build the marking; the cleared texts must be the ones the rule takes."""

    taken = next_texts(selection, profiles, replaced, kept, skips)
    if list(cleared) != taken:
        raise ReplacementError(f"the rule takes {taken}, not {list(cleared)}")
    stored: list[str] = selection["groups"][RESERVE]
    replacements = [
        {
            "text_id": text_id,
            "replaces": old,
            "reserve_place": stored.index(text_id) + 1,
            "word_count": profiles[text_id].word_count,
            "sentences": profiles[text_id].sentences,
        }
        for old, text_id in zip(replaced, taken, strict=True)
    ]
    return {
        "reason": "The replaced texts have no conclusion zone.",
        "rule": _rule(kept),
        "kept": [kept],
        "replacements": replacements,
        "privacy_skips": [
            {
                "text_id": text_id,
                "reason": reason,
                "reserve_place": stored.index(text_id) + 1,
            }
            for text_id, reason in skips.items()
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--annotations", type=Path, default=genius_loader.DEFAULT_ANNOTATIONS
    )
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--banks", type=Path, default=genius_loader.DEFAULT_BANKS)
    parser.add_argument(
        "--sentence-criteria",
        type=Path,
        default=genius_loader.DEFAULT_SENTENCE_CRITERIA,
    )
    parser.add_argument("--seed-file", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--selected", type=Path, default=DEFAULT_SELECTED)
    parser.add_argument("--skip", action="append", default=[], metavar="ID=REASON")
    parser.add_argument("--cleared", nargs="*", metavar="ID")
    args = parser.parse_args(argv)

    archive = args.archive or fetch_genius.DEFAULT_EXTERNAL / fetch_genius.ASSET
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    try:
        fetch_genius.verify_sha256(archive.read_bytes(), selection["corpus_sha256"])
        profiles = read_profiles(args.annotations)
        check_corpus(selection, profiles)
        check_stored_order(selection, read_seed(args.seed_file))
        skips = dict(read_skip(entry) for entry in args.skip)
        if args.cleared is None:
            taken = next_texts(selection, profiles, REPLACED, KEPT, skips)
            print(f"next texts, nothing written: {' '.join(taken)}")
            return 0
        marking = build_marking(
            selection, profiles, REPLACED, KEPT, skips, args.cleared
        )
    except (SelectionError, ReserveError, fetch_genius.FetchError) as error:
        print(f"REFUSED, nothing written: {error}", file=sys.stderr)
        return 1

    groups = selection["groups"]
    copied = {
        "pilot": [*groups["pilot"], *args.cleared],
        "component": groups["component"],
    }
    copy_selected(copied, args.banks, args.sentence_criteria, args.selected)
    updated = {**selection, PILOT_REPLACEMENT: marking}
    args.selection.write_bytes(genius_loader.dump_json(updated))
    print(f"replaced {' '.join(REPLACED)} by {' '.join(args.cleared)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
