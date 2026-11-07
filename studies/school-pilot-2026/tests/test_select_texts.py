"""The draw procedure, tested on invented ids only.

These tests never read the corpus. The real draw runs once, after the procedure
is committed.
"""

from __future__ import annotations

import json
from pathlib import Path

import fetch_genius
import genius_loader
import pytest
import select_texts as select

IDS = [f"{number}_Spiel" for number in range(50)]


def test_the_seed_is_the_agreed_one(study_root: Path) -> None:
    assert select.read_seed(study_root / "prereg/seed.txt") == 20261113


@pytest.mark.parametrize("content", ["", "abc", "12 34", "-5", "٣"])
def test_a_malformed_seed_is_rejected(tmp_path: Path, content: str) -> None:
    path = tmp_path / "seed.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(select.SelectionError):
        select.read_seed(path)


@pytest.mark.parametrize(
    ("words", "layer", "expected"),
    [(80, True, True), (79, True, False), (80, False, False), (500, False, False)],
)
def test_the_participation_rule(words: int, layer: bool, expected: bool) -> None:
    assert select.is_eligible(words, layer) is expected


def test_groups_have_the_agreed_sizes_in_the_agreed_order() -> None:
    groups = select.assign_groups(IDS, 1)
    assert list(groups) == ["pilot", "component", "validation_holdout", "reserve"]
    assert [len(ids) for ids in groups.values()] == [3, 20, 20, 7]


def test_groups_do_not_overlap_and_lose_nothing() -> None:
    groups = select.assign_groups(IDS, 1)
    drawn = [text_id for ids in groups.values() for text_id in ids]
    assert sorted(drawn) == sorted(IDS)


def test_the_draw_ignores_the_input_order() -> None:
    assert select.assign_groups(IDS, 7) == select.assign_groups(IDS[::-1], 7)


def test_the_seed_changes_the_draw() -> None:
    assert select.assign_groups(IDS, 7) != select.assign_groups(IDS, 8)


def test_too_few_texts_stop_the_draw() -> None:
    with pytest.raises(select.SelectionError, match="need 43"):
        select.assign_groups(IDS[:42], 1)


def test_exactly_enough_texts_leave_an_empty_reserve() -> None:
    assert select.assign_groups(IDS[:43], 1)["reserve"] == []


def test_duplicate_ids_stop_the_draw() -> None:
    with pytest.raises(select.SelectionError, match="unique"):
        select.draw_order(["a", "a"], 1)


def test_an_earlier_draw_is_not_replaced(tmp_path: Path) -> None:
    target = tmp_path / "selection.json"
    select.write_once(b"first", target)
    with pytest.raises(select.SelectionError, match="different draw"):
        select.write_once(b"second", target)
    assert target.read_bytes() == b"first"


def test_repeating_the_same_draw_is_allowed(tmp_path: Path) -> None:
    target = tmp_path / "selection.json"
    select.write_once(b"first", target)
    select.write_once(b"first", target)
    assert target.read_bytes() == b"first"


def _toy_corpus(root: Path) -> Path:
    """Forty-six invented annotation files; three of them are not eligible."""

    annotations = root / "annotations"
    annotations.mkdir()
    layer = "#T_SP=webanno.custom.Argument|Clarity|KriteriumPreisBetrieb\n"
    long_text = "#Text=" + "wort " * 79 + "ende.\n1-1\t0-4\twort\t_\t_\n"
    for number in range(46):
        header = "" if number == 0 else layer
        body = "#Text=zu kurz\n" if number == 1 else long_text
        path = annotations / f"{number}_Spiel_T1.tsv"
        path.write_text(header + body, encoding="utf-8")
    return annotations


def _run(root: Path, archive: Path, seed: str = "5") -> int:
    annotations = root / "annotations"
    corpus = genius_loader.load_corpus(annotations)
    banks = root / "banks"
    banks.mkdir(exist_ok=True)
    for item in corpus:
        target = banks / f"{item.bank.text_id}.json"
        target.write_bytes(genius_loader.dump_json(item.bank.as_dict()))
    (root / "sentence_criteria.json").write_bytes(
        genius_loader.dump_json(
            {item.bank.text_id: item.sentence_criteria for item in corpus}
        )
    )
    (root / "seed.txt").write_text(seed, encoding="utf-8")
    return select.main(
        [
            "--annotations",
            str(annotations),
            "--archive",
            str(archive),
            "--banks",
            str(banks),
            "--sentence-criteria",
            str(root / "sentence_criteria.json"),
            "--seed-file",
            str(root / "seed.txt"),
            "--selection",
            str(root / "selection.json"),
            "--selected",
            str(root / "selected"),
        ]
    )


def test_the_whole_script_on_an_invented_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _toy_corpus(tmp_path)
    archive = tmp_path / "toy.zip"
    archive.write_bytes(b"toy")
    monkeypatch.setattr(fetch_genius, "verify_sha256", lambda payload: "toy-digest")

    assert _run(tmp_path, archive) == 0

    selection = json.loads((tmp_path / "selection.json").read_text("utf-8"))
    assert selection["annotation_files"] == 46
    assert selection["eligible_texts"] == 44
    assert selection["corpus_sha256"] == "toy-digest"
    drawn = [text_id for ids in selection["groups"].values() for text_id in ids]
    assert "0_Spiel_T1" not in drawn
    assert "1_Spiel_T1" not in drawn
    copied = selection["groups"]["pilot"] + selection["groups"]["component"]
    names = sorted(path.stem for path in (tmp_path / "selected").glob("*_T1.json"))
    assert names == sorted(copied)
    for text_id in copied:
        assert (tmp_path / "selected" / f"{text_id}.json").read_bytes() == (
            tmp_path / "banks" / f"{text_id}.json"
        ).read_bytes()
    subset = json.loads((tmp_path / "selected/sentence_criteria.json").read_text())
    assert sorted(subset) == sorted(copied)


def test_a_second_seed_cannot_replace_the_draw(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _toy_corpus(tmp_path)
    archive = tmp_path / "toy.zip"
    archive.write_bytes(b"toy")
    monkeypatch.setattr(fetch_genius, "verify_sha256", lambda payload: "toy-digest")
    assert _run(tmp_path, archive, seed="5") == 0
    with pytest.raises(select.SelectionError, match="different draw"):
        _run(tmp_path, archive, seed="6")


def test_an_unpinned_archive_stops_the_draw(tmp_path: Path) -> None:
    _toy_corpus(tmp_path)
    archive = tmp_path / "toy.zip"
    archive.write_bytes(b"not the pinned archive")
    with pytest.raises(fetch_genius.FetchError, match="SHA-256 mismatch"):
        _run(tmp_path, archive)
    assert not (tmp_path / "selection.json").exists()
