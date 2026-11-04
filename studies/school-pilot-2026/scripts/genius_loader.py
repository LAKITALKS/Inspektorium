"""Turn GENIUS WebAnno TSV files into sentence banks and the criteria list.

Every line that starts with ``#Text=`` is one sentence. Each sentence is
HTML-unescaped, then normalized to Unicode NFC. Sentences are joined with one
ASCII space to form ``full_text``; ``start`` and ``end`` are Python character
offsets into ``full_text``.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANNOTATIONS = STUDY_ROOT / "data" / "external" / "genius" / "annotations"
DEFAULT_BANKS = STUDY_ROOT / "data" / "external" / "banks"
DEFAULT_SENTENCE_CRITERIA = STUDY_ROOT / "data" / "external" / "sentence_criteria.json"
DEFAULT_CRITERIA = STUDY_ROOT / "data" / "criteria.json"

TEXT_MARKER = "#Text="
LAYER_MARKER = "#T_SP="
ARGUMENT_LAYER = "webanno.custom.Argument"
CRITERION_PREFIX = "Kriterium"
SENTENCE_SEPARATOR = " "
_TOKEN_ID = re.compile(r"^(\d+)-\d+")
_EMPTY_CELLS = frozenset({"_", "*"})

# The order is the study's K1 to K7. The header labels keep the corpus spelling,
# which lost its umlauts; the readable names are a separate field.
CRITERIA: tuple[tuple[str, str, str], ...] = (
    ("K1", "KriteriumJahresertragEnergiedichte", "Jahresertrag/Energiedichte"),
    ("K2", "KriteriumLebensdauerVerfgbarkeit", "Lebensdauer/Verfügbarkeit"),
    (
        "K3",
        "KriteriumLokaleEmissionenGeruschemissionen",
        "Lokale Emissionen/Geräuschemissionen",
    ),
    ("K4", "KriteriumPreisBetrieb", "Preis/Betrieb"),
    ("K5", "KriteriumTreibhausgasemissionen", "Treibhausgasemissionen"),
    ("K6", "KriteriumWirkungsgrad", "Wirkungsgrad"),
    ("K7", "KriteriumSonstiges", "Sonstiges"),
)
_CRITERION_ID_BY_LABEL = {label: cid for cid, label, _ in CRITERIA}


class CorpusError(ValueError):
    """The corpus does not have the structure this study relies on."""


@dataclass(frozen=True)
class Sentence:
    sid: str
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class SentenceBank:
    text_id: str
    word_count: int
    sentences: tuple[Sentence, ...]
    full_text: str

    def as_dict(self) -> dict[str, object]:
        return {
            "text_id": self.text_id,
            "word_count": self.word_count,
            "sentences": [
                {"sid": s.sid, "text": s.text, "start": s.start, "end": s.end}
                for s in self.sentences
            ],
            "full_text": self.full_text,
        }


@dataclass(frozen=True)
class Annotation:
    """One annotation file: its bank and what the eligibility rule needs."""

    bank: SentenceBank
    has_argument_layer: bool
    criterion_labels: tuple[str, ...]
    sentence_criteria: dict[str, list[str]]


def bank_from_dict(data: dict[str, Any]) -> SentenceBank:
    """Rebuild a bank from its JSON form."""

    return SentenceBank(
        text_id=data["text_id"],
        word_count=data["word_count"],
        sentences=tuple(
            Sentence(item["sid"], item["text"], item["start"], item["end"])
            for item in data["sentences"]
        ),
        full_text=data["full_text"],
    )


def read_bank(path: Path) -> SentenceBank:
    """Read one sentence bank file."""

    return bank_from_dict(json.loads(path.read_text(encoding="utf-8")))


def convert_sentence(raw: str) -> str:
    """Apply the study's two text conversions, in this order."""

    return unicodedata.normalize("NFC", html.unescape(raw))


def build_bank(text_id: str, raw_sentences: list[str]) -> SentenceBank:
    """Build a bank; offsets refer to the single-space-joined ``full_text``."""

    sentences: list[Sentence] = []
    cursor = 0
    for number, raw in enumerate(raw_sentences, start=1):
        text = convert_sentence(raw)
        end = cursor + len(text)
        sentences.append(Sentence(f"S{number}", text, cursor, end))
        cursor = end + len(SENTENCE_SEPARATOR)
    full_text = SENTENCE_SEPARATOR.join(s.text for s in sentences)
    return SentenceBank(text_id, len(full_text.split()), tuple(sentences), full_text)


def read_lines(path: Path) -> list[str]:
    """Read a file split on LF only.

    ``str.splitlines`` would also split on U+2028, U+0085 and similar characters
    inside a sentence.
    """

    return path.read_bytes().decode("utf-8").split("\n")


def argument_fields(lines: list[str]) -> tuple[str, ...] | None:
    """Return the feature names of the Argument layer, or None if it is absent."""

    prefix = f"{LAYER_MARKER}{ARGUMENT_LAYER}|"
    for line in lines:
        if line.startswith(prefix):
            return tuple(line.removeprefix(prefix).split("|"))
    return None


def _column_names(lines: list[str]) -> list[str]:
    names: list[str] = []
    for line in lines:
        if line.startswith(LAYER_MARKER):
            layer, *features = line.removeprefix(LAYER_MARKER).split("|")
            names.extend(f"{layer}|{feature}" for feature in features)
    return names


def sentence_criteria(lines: list[str]) -> dict[str, list[str]]:
    """Map each sentence id to the criteria the corpus annotators marked in it."""

    columns = _column_names(lines)
    found: dict[str, set[str]] = {}
    for line in lines:
        match = _TOKEN_ID.match(line)
        if match is None:
            continue
        sid = f"S{match.group(1)}"
        marked = found.setdefault(sid, set())
        cells = line.split("\t")[3:]
        for column, cell in zip(columns, cells, strict=False):
            layer, _, feature = column.partition("|")
            if layer != ARGUMENT_LAYER or feature not in _CRITERION_ID_BY_LABEL:
                continue
            values = {re.sub(r"\[\d+\]$", "", part) for part in cell.split("|")}
            if values - _EMPTY_CELLS:
                marked.add(_CRITERION_ID_BY_LABEL[feature])
    return {sid: sorted(marked) for sid, marked in found.items()}


def load_annotation(path: Path) -> Annotation:
    """Read one WebAnno TSV file."""

    lines = read_lines(path)
    raw_sentences = [
        line.removeprefix(TEXT_MARKER) for line in lines if line.startswith(TEXT_MARKER)
    ]
    fields = argument_fields(lines)
    return Annotation(
        bank=build_bank(path.stem, raw_sentences),
        has_argument_layer=fields is not None,
        criterion_labels=tuple(
            field for field in fields or () if field.startswith(CRITERION_PREFIX)
        ),
        sentence_criteria=sentence_criteria(lines),
    )


def load_corpus(annotations: Path) -> list[Annotation]:
    """Read all annotation files in a stable order."""

    return [load_annotation(path) for path in sorted(annotations.glob("*.tsv"))]


def build_criteria(corpus: list[Annotation]) -> dict[str, object]:
    """Build ``criteria.json`` from the headers; any other label set is an error."""

    expected = {label for _, label, _ in CRITERIA}
    seen = {label for item in corpus for label in item.criterion_labels}
    if seen != expected:
        raise CorpusError(f"unexpected criterion labels: {sorted(seen ^ expected)}")
    return {
        "layer": ARGUMENT_LAYER,
        "criteria": [
            {"id": cid, "original_label": label, "name": name}
            for cid, label, name in CRITERIA
        ],
    }


def dump_json(value: object) -> bytes:
    """Serialize deterministically: same value, same bytes."""

    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    return text.encode("utf-8")


def write_outputs(
    corpus: list[Annotation],
    banks: Path,
    criteria: Path,
    by_sentence: Path,
) -> None:
    banks.mkdir(parents=True, exist_ok=True)
    for item in corpus:
        target = banks / f"{item.bank.text_id}.json"
        target.write_bytes(dump_json(item.bank.as_dict()))
    criteria.parent.mkdir(parents=True, exist_ok=True)
    criteria.write_bytes(dump_json(build_criteria(corpus)))
    by_sentence.parent.mkdir(parents=True, exist_ok=True)
    by_sentence.write_bytes(
        dump_json({item.bank.text_id: item.sentence_criteria for item in corpus})
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--banks", type=Path, default=DEFAULT_BANKS)
    parser.add_argument("--criteria", type=Path, default=DEFAULT_CRITERIA)
    parser.add_argument(
        "--sentence-criteria", type=Path, default=DEFAULT_SENTENCE_CRITERIA
    )
    args = parser.parse_args(argv)
    corpus = load_corpus(args.annotations)
    write_outputs(corpus, args.banks, args.criteria, args.sentence_criteria)
    print(f"wrote {len(corpus)} sentence banks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
