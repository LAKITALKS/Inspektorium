"""Sentence banks: synthetic unit tests plus plausibility checks on the corpus."""

from __future__ import annotations

import json
import re
import statistics
import unicodedata
from pathlib import Path

import genius_loader as loader
import pytest

HEADER = (
    "#FORMAT=WebAnno TSV 3.3\n"
    "#T_SP=webanno.custom.Argument|Clarity|KriteriumPreisBetrieb|KriteriumWirkungsgrad\n"
    "#T_SP=webanno.custom.Struktur|Struktur\n\n\n"
)
BODY = (
    "#Text=Erster Satz.\n"
    "1-1\t0-6\tErster\t*[1]\tPreis/Betrieb[1]\t*[1]\tEinleitung[2]\t\n"
    "1-2\t7-12\tSatz.\t_\t_\t_\t_\t\n\n"
    "#Text=Zweiter &lt; Satz mit Trenner.\n"
    "2-1\t13-20\tZweiter\t_\t_\t_\t_\t\n"
)


def _write(path: Path, content: str) -> Path:
    path.write_bytes(content.encode("utf-8"))
    return path


def test_each_text_line_is_one_sentence_with_exact_offsets(tmp_path: Path) -> None:
    item = loader.load_annotation(_write(tmp_path / "7_Verk_T1.tsv", HEADER + BODY))
    bank = item.bank
    assert bank.text_id == "7_Verk_T1"
    assert [s.sid for s in bank.sentences] == ["S1", "S2"]
    assert bank.sentences[1].start == bank.sentences[0].end + 1
    for sentence in bank.sentences:
        assert bank.full_text[sentence.start : sentence.end] == sentence.text


def test_only_lf_ends_a_line(tmp_path: Path) -> None:
    item = loader.load_annotation(_write(tmp_path / "a.tsv", HEADER + BODY))
    assert " " in item.bank.sentences[1].text


def test_html_entities_are_unescaped_before_nfc() -> None:
    assert loader.convert_sentence("a &lt; b") == "a < b"
    assert loader.convert_sentence("&amp;lt;") == "&lt;"
    assert loader.convert_sentence("ä") == "ä"
    assert loader.convert_sentence("a&#776;") == "ä"


def test_word_count_splits_on_whitespace() -> None:
    bank = loader.build_bank("x", ["Ein  Satz", "CO2-frei, oder?"])
    assert bank.word_count == 4


def test_the_argument_layer_is_detected_with_a_clean_counterpart(
    tmp_path: Path,
) -> None:
    with_layer = loader.load_annotation(_write(tmp_path / "a.tsv", HEADER + BODY))
    without = loader.load_annotation(
        _write(tmp_path / "b.tsv", "#T_SP=webanno.custom.Struktur|Struktur\n" + BODY)
    )
    assert with_layer.has_argument_layer is True
    assert with_layer.criterion_labels == (
        "KriteriumPreisBetrieb",
        "KriteriumWirkungsgrad",
    )
    assert without.has_argument_layer is False
    assert without.criterion_labels == ()


def test_sentence_criteria_ignore_empty_cells_and_other_layers(tmp_path: Path) -> None:
    item = loader.load_annotation(_write(tmp_path / "a.tsv", HEADER + BODY))
    assert item.sentence_criteria == {"S1": ["K4"], "S2": []}


def test_a_changed_label_set_is_an_error(tmp_path: Path) -> None:
    item = loader.load_annotation(_write(tmp_path / "a.tsv", HEADER + BODY))
    with pytest.raises(loader.CorpusError, match="unexpected criterion labels"):
        loader.build_criteria([item])


def test_same_input_gives_the_same_bytes(tmp_path: Path) -> None:
    (tmp_path / "in").mkdir()
    _write(tmp_path / "in/a.tsv", HEADER + BODY)
    banks = loader.load_corpus(tmp_path / "in")
    first = loader.dump_json(banks[0].bank.as_dict())
    second = loader.dump_json(
        loader.load_corpus(tmp_path / "in")[0].bank.as_dict(),
    )
    assert first == second
    assert first.endswith(b"\n")
    assert b"\r" not in first


@pytest.fixture(scope="module")
def corpus(annotations_dir: Path) -> list[loader.Annotation]:
    return loader.load_corpus(annotations_dir)


# Reference values as of 2026-10-30, with words split on whitespace.
def test_plausibility_annotation_files(corpus: list[loader.Annotation]) -> None:
    assert len(corpus) == 262


def test_plausibility_texts_with_at_least_80_words(
    corpus: list[loader.Annotation],
) -> None:
    assert sum(item.bank.word_count >= 80 for item in corpus) == 165


def test_plausibility_median_sentences(corpus: list[loader.Annotation]) -> None:
    assert statistics.median(len(item.bank.sentences) for item in corpus) == 6


def test_plausibility_one_file_with_html_entities(annotations_dir: Path) -> None:
    entity = re.compile(r"&(?:[A-Za-z][A-Za-z0-9]*|#[0-9]+|#[xX][0-9A-Fa-f]+);")
    hits = [
        path.name
        for path in sorted(annotations_dir.glob("*.tsv"))
        if any(
            line.startswith(loader.TEXT_MARKER) and entity.search(line)
            for line in loader.read_lines(path)
        )
    ]
    assert len(hits) == 1


def test_corpus_offsets_are_exact(corpus: list[loader.Annotation]) -> None:
    for item in corpus:
        bank = item.bank
        for sentence in bank.sentences:
            assert bank.full_text[sentence.start : sentence.end] == sentence.text
        assert unicodedata.normalize("NFC", bank.full_text) == bank.full_text


def test_corpus_has_no_unconverted_entities(corpus: list[loader.Annotation]) -> None:
    assert not any("&lt;" in item.bank.full_text for item in corpus)


def test_corpus_criteria_are_the_seven_expected_ones(
    corpus: list[loader.Annotation],
) -> None:
    criteria = loader.build_criteria(corpus)
    assert criteria["criteria"] == [
        {"id": cid, "original_label": label, "name": name}
        for cid, label, name in loader.CRITERIA
    ]
    assert len(loader.CRITERIA) == 7


def test_token_sentence_numbers_match_the_text_lines(
    corpus: list[loader.Annotation],
) -> None:
    for item in corpus:
        assert sorted(item.sentence_criteria) == sorted(
            s.sid for s in item.bank.sentences
        )


def test_corpus_serialization_is_byte_stable(annotations_dir: Path) -> None:
    def digest() -> list[bytes]:
        return [
            loader.dump_json(item.bank.as_dict())
            for item in loader.load_corpus(annotations_dir)
        ]

    assert digest() == digest()


def test_committed_criteria_match_the_loader(study_root: Path) -> None:
    committed = json.loads((study_root / "data/criteria.json").read_text("utf-8"))
    assert [item["id"] for item in committed["criteria"]] == [
        f"K{number}" for number in range(1, 8)
    ]
    assert [item["original_label"] for item in committed["criteria"]] == [
        label for _, label, _ in loader.CRITERIA
    ]
