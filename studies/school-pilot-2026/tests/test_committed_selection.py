"""The committed draw is complete, separate and reproducible, and so is its change."""

from __future__ import annotations

import json
from pathlib import Path

import fetch_genius
import genius_loader
import pytest
import replace_pilot_texts as rp
import select_texts as select
from reserve import PILOT_REPLACEMENT as REPLACEMENT_MARKER
from reserve import USED_FOR_FABRICATED as USED_MARKER
from reserve import current_pilot


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


def test_only_the_working_texts_are_committed(
    study_root: Path, selection: dict[str, object], groups: dict[str, list[str]]
) -> None:
    committed = {
        path.stem
        for path in (study_root / "data/selected").glob("*.json")
        if path.name != "sentence_criteria.json"
    }
    assert committed == (
        set(groups["pilot"]) | set(groups["component"]) | set(current_pilot(selection))
    )


def test_committed_banks_are_exact(
    study_root: Path, selection: dict[str, object], groups: dict[str, list[str]]
) -> None:
    for text_id in groups["pilot"] + groups["component"] + current_pilot(selection):
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
    added = {USED_MARKER, REPLACEMENT_MARKER}
    drawn = {key: value for key, value in selection.items() if key not in added}
    assert select.build_selection(corpus, seed, fetch_genius.EXPECTED_SHA256) == drawn


def test_the_selection_holds_only_the_draw_and_the_marking(
    selection: dict[str, object],
) -> None:
    assert set(selection) == {
        "seed",
        "corpus_sha256",
        "annotation_files",
        "eligible_texts",
        "rule",
        "groups",
        USED_MARKER,
        REPLACEMENT_MARKER,
    }


def test_the_pilot_uses_the_replacements(selection: dict[str, object]) -> None:
    assert current_pilot(selection) == [
        "298_Verk_T1",
        "950_Verk_T1-rev",
        "1081_Verk_T1-Rev",
    ]


def test_the_replaced_texts_stay_in_the_group_and_their_banks_stay(
    study_root: Path, groups: dict[str, list[str]]
) -> None:
    for text_id in rp.REPLACED:
        assert text_id in groups["pilot"]
        assert (study_root / f"data/selected/{text_id}.json").is_file()


def test_the_replacements_stay_in_the_reserve(
    groups: dict[str, list[str]], selection: dict[str, object]
) -> None:
    new = set(current_pilot(selection)) - set(groups["pilot"])
    assert len(new) == 2
    assert new <= set(groups["reserve"])


def test_the_replacement_is_what_the_rule_gives(
    annotations_dir: Path, selection: dict[str, object]
) -> None:
    profiles = rp.read_profiles(annotations_dir)
    marking = selection[REPLACEMENT_MARKER]
    assert isinstance(marking, dict)
    taken = [entry["text_id"] for entry in marking["replacements"]]
    before = {
        key: value for key, value in selection.items() if key != REPLACEMENT_MARKER
    }
    skips = {entry["text_id"]: entry["reason"] for entry in marking["privacy_skips"]}
    rebuilt = rp.build_marking(before, profiles, rp.REPLACED, rp.KEPT, skips, taken)
    assert rebuilt == marking


def test_the_committed_banks_of_the_replacements_match_the_corpus(
    annotations_dir: Path, selection: dict[str, object], study_root: Path
) -> None:
    for text_id in current_pilot(selection):
        item = genius_loader.load_annotation(annotations_dir / f"{text_id}.tsv")
        committed = (study_root / f"data/selected/{text_id}.json").read_bytes()
        assert committed == genius_loader.dump_json(item.bank.as_dict())


def test_the_sentence_criteria_cover_every_committed_bank(study_root: Path) -> None:
    selected = study_root / "data/selected"
    subset = json.loads((selected / "sentence_criteria.json").read_text("utf-8"))
    banks = {
        path.stem
        for path in selected.glob("*.json")
        if path.name != "sentence_criteria.json"
    }
    assert set(subset) == banks
