"""The committed draw is complete, separate and reproducible."""

from __future__ import annotations

import json
from pathlib import Path

import fetch_genius
import genius_loader
import pytest
import select_texts as select


@pytest.fixture(scope="module")
def selection(study_root: Path) -> dict[str, object]:
    loaded: dict[str, object] = json.loads(
        (study_root / "prereg/selection.json").read_text("utf-8")
    )
    return loaded


@pytest.fixture(scope="module")
def groups(selection: dict[str, object]) -> dict[str, list[str]]:
    drawn = selection["groups"]
    assert isinstance(drawn, dict)
    return drawn


def test_groups_have_the_agreed_sizes(groups: dict[str, list[str]]) -> None:
    assert len(groups["pilot"]) == 3
    assert len(groups["component"]) == 20
    assert len(groups["validation_holdout"]) == 20
    assert groups["reserve"]


def test_groups_do_not_overlap(
    selection: dict[str, object], groups: dict[str, list[str]]
) -> None:
    drawn = [text_id for ids in groups.values() for text_id in ids]
    assert len(drawn) == len(set(drawn)) == selection["eligible_texts"]


def test_only_the_working_groups_are_committed(
    study_root: Path, groups: dict[str, list[str]]
) -> None:
    committed = {
        path.stem
        for path in (study_root / "data/selected").glob("*.json")
        if path.name != "sentence_criteria.json"
    }
    assert committed == set(groups["pilot"]) | set(groups["component"])


def test_committed_banks_are_exact(
    study_root: Path, groups: dict[str, list[str]]
) -> None:
    for text_id in groups["pilot"] + groups["component"]:
        bank = json.loads(
            (study_root / f"data/selected/{text_id}.json").read_text("utf-8")
        )
        assert bank["text_id"] == text_id
        assert bank["word_count"] >= select.MIN_WORDS
        assert bank["word_count"] == len(bank["full_text"].split())
        for sentence in bank["sentences"]:
            start, end = sentence["start"], sentence["end"]
            assert bank["full_text"][start:end] == sentence["text"]


def test_the_draw_is_reproducible_from_the_corpus(
    annotations_dir: Path, selection: dict[str, object], study_root: Path
) -> None:
    corpus = genius_loader.load_corpus(annotations_dir)
    seed = select.read_seed(study_root / "prereg/seed.txt")
    assert select.build_selection(corpus, seed, fetch_genius.EXPECTED_SHA256) == (
        selection
    )
