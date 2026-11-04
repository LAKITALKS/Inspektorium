"""Draw the study groups with the fixed seed.

The procedure is committed before its first run on the corpus. Eligibility and
order are computed from the text ids and the seed alone: each eligible id is
ranked by SHA-256 of ``"<seed>:<text_id>"``, and the groups take that ranking in
the fixed order pilot, component, validation_holdout, reserve. The ranking does
not depend on the file system, the Python version or a random generator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import fetch_genius
import genius_loader

STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = STUDY_ROOT / "prereg" / "seed.txt"
DEFAULT_SELECTION = STUDY_ROOT / "prereg" / "selection.json"
DEFAULT_SELECTED = STUDY_ROOT / "data" / "selected"

MIN_WORDS = 80
GROUPS: tuple[tuple[str, int], ...] = (
    ("pilot", 3),
    ("component", 20),
    ("validation_holdout", 20),
)
RESERVE = "reserve"
COPIED_GROUPS = ("pilot", "component")


class SelectionError(RuntimeError):
    """The draw cannot be made, or would replace an earlier draw."""


def read_seed(path: Path) -> int:
    text = path.read_text(encoding="utf-8").strip()
    if not text.isascii() or not text.isdigit():
        raise SelectionError("seed file must hold one decimal integer")
    return int(text)


def is_eligible(word_count: int, has_argument_layer: bool) -> bool:
    """The participation rule: at least 80 words and the Argument layer."""

    return word_count >= MIN_WORDS and has_argument_layer


def draw_order(text_ids: list[str], seed: int) -> list[str]:
    """Rank ids by a seeded hash; the input order has no influence."""

    if len(set(text_ids)) != len(text_ids):
        raise SelectionError("text ids must be unique")

    def rank(text_id: str) -> str:
        return hashlib.sha256(f"{seed}:{text_id}".encode()).hexdigest()

    return sorted(text_ids, key=rank)


def assign_groups(text_ids: list[str], seed: int) -> dict[str, list[str]]:
    """Fill the groups in order; everything left over is the reserve."""

    required = sum(size for _, size in GROUPS)
    if len(text_ids) < required:
        raise SelectionError(f"need {required} eligible texts, got {len(text_ids)}")
    ordered = draw_order(text_ids, seed)
    groups: dict[str, list[str]] = {}
    cursor = 0
    for name, size in GROUPS:
        groups[name] = ordered[cursor : cursor + size]
        cursor += size
    groups[RESERVE] = ordered[cursor:]
    return groups


def build_selection(
    corpus: list[genius_loader.Annotation], seed: int, corpus_sha256: str
) -> dict[str, object]:
    eligible = [
        item.bank.text_id
        for item in corpus
        if is_eligible(item.bank.word_count, item.has_argument_layer)
    ]
    return {
        "seed": seed,
        "corpus_sha256": corpus_sha256,
        "annotation_files": len(corpus),
        "eligible_texts": len(eligible),
        "rule": {
            "min_words": MIN_WORDS,
            "required_layer": genius_loader.ARGUMENT_LAYER,
        },
        "groups": assign_groups(eligible, seed),
    }


def write_once(payload: bytes, target: Path) -> None:
    """Write the draw; a different existing draw is never replaced."""

    if target.exists() and target.read_bytes() != payload:
        raise SelectionError(f"{target.name} already holds a different draw")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)


def copy_selected(
    groups: dict[str, list[str]],
    banks: Path,
    sentence_criteria: Path,
    selected: Path,
) -> int:
    """Copy the banks of the working groups byte for byte."""

    text_ids = [text_id for name in COPIED_GROUPS for text_id in groups[name]]
    selected.mkdir(parents=True, exist_ok=True)
    for text_id in text_ids:
        source = banks / f"{text_id}.json"
        (selected / source.name).write_bytes(source.read_bytes())
    annotated = json.loads(sentence_criteria.read_text("utf-8"))
    subset = {text_id: annotated[text_id] for text_id in sorted(text_ids)}
    (selected / "sentence_criteria.json").write_bytes(genius_loader.dump_json(subset))
    return len(text_ids)


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
    args = parser.parse_args(argv)

    archive = args.archive or fetch_genius.DEFAULT_EXTERNAL / fetch_genius.ASSET
    corpus_sha256 = fetch_genius.verify_sha256(archive.read_bytes())
    corpus = genius_loader.load_corpus(args.annotations)
    selection = build_selection(corpus, read_seed(args.seed_file), corpus_sha256)
    write_once(genius_loader.dump_json(selection), args.selection)
    groups = selection["groups"]
    assert isinstance(groups, dict)
    copied = copy_selected(groups, args.banks, args.sentence_criteria, args.selected)
    sizes = {name: len(ids) for name, ids in groups.items()}
    print(f"eligible {selection['eligible_texts']}; groups {sizes}; copied {copied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
