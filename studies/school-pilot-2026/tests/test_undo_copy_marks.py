"""Undoing the copy marks, tested on invented answers only."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
import undo_copy_marks as undo

ANSWER = {
    "grade": 3,
    "comments": [
        {
            "text": 'Erfunden: "Größe", _Strich_, *Stern* und C:\\Pfad.\nNeue Zeile.',
            "quotes": [{"sid": "S2", "quote": "Ein <erfundener> Satz & mehr."}],
        }
    ],
    "errors": [],
}
PLAIN = json.dumps(ANSWER, ensure_ascii=False, indent=2)


def chat_copy(text: str) -> str:
    """Imitate the copy path: escapes, leading spaces and line ends."""

    lines = []
    for line in text.split("\n"):
        escaped = re.sub(r"([\\_*])", r"\\\1", line)
        if escaped.startswith(" "):
            escaped = "&#x20;" + escaped[1:]
        lines.append(escaped)
    return "\\\n".join(lines)


def write(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


@pytest.fixture
def runs(tmp_path: Path) -> Path:
    folder = tmp_path / "runs"
    marked = chat_copy(PLAIN).encode("utf-8")
    write(folder / "bot-a/toy/original/1.json", marked)
    write(folder / "bot-a/toy/original/1.meta.json", b'{"time": "10:00&#x20;"}\\\n')
    write(folder / "bot-b/toy/original/1.json", PLAIN.encode("utf-8"))
    write(folder / "banks/toy.json", b'{"text": "&#x20;"}\\\n')
    write(folder / "prompts/toy.original.md", b"Zeile&#x20;\\\nZeile\n")
    write(folder / "notes.md", b"&#39;\\\n")
    return folder


def snapshot(folder: Path) -> dict[str, bytes]:
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for path in folder.rglob("*")
        if path.is_file()
    }


def test_the_rule_is_the_one_fixed_in_the_dated_entry() -> None:
    assert undo.EOL.pattern == r"\\(?=\r?\n)|\\\Z"
    assert undo.ESC.pattern == (r"\\([!-/:-@\[-`{-~])|&#x([0-9A-Fa-f]+);|&#([0-9]+);")
    assert undo.REFERENCE.pattern == r"&#x?[0-9A-Fa-f]+;"


@pytest.mark.parametrize(
    "content",
    [
        PLAIN.encode("utf-8"),
        PLAIN.replace("\n", "\r\n").encode("utf-8"),
        b"\xef\xbb\xbf" + PLAIN.encode("utf-8"),
        b'{"text": "a \\_ b \\* c &amp; d"}\n',
        b"",
    ],
)
def test_a_file_without_marks_stays_byte_identical(content: bytes) -> None:
    assert undo.undo_bytes(content) == (content, 0)


def test_an_answer_that_is_not_utf_8_stays_byte_identical() -> None:
    content = b"\xff\xfe \\\n"
    assert undo.undo_bytes(content) == (content, 0)


def test_an_escaped_quote_in_a_clean_file_stays() -> None:
    content = b'{"text": "Er sagt \\"nein\\"."}\n'
    assert undo.undo_bytes(content) == (content, 0)


def test_the_copied_answer_is_restored_exactly() -> None:
    copied = chat_copy(PLAIN)
    with pytest.raises(json.JSONDecodeError):
        json.loads(copied)
    restored, marks = undo.undo_bytes(copied.encode("utf-8"))
    assert restored == PLAIN.encode("utf-8")
    assert json.loads(restored) == ANSWER
    assert marks > copied.count("&#x20;") + PLAIN.count("\n")


def test_windows_line_ends_are_kept() -> None:
    copied = chat_copy(PLAIN).replace("\n", "\r\n")
    restored, _ = undo.undo_bytes(copied.encode("utf-8"))
    assert restored == PLAIN.replace("\n", "\r\n").encode("utf-8")


@pytest.mark.parametrize(
    ("marked", "restored", "marks"),
    [
        ("a\\\nb", "a\nb", 1),
        ("a\\\r\nb", "a\r\nb", 1),
        ("a\\", "a", 1),
        ("&#x20;a&#32;b", " a b", 2),
        ("&#xE4;\\_", "ä_", 2),
        # One pass: a decoded character never starts another mark.
        ("&#x26;#x20;", "&#x20;", 1),
        ("\\\\_&#x20;", "\\_ ", 2),
        ("\\&#x20;", "&#x20;", 1),
        # A backslash before a letter or digit is no mark.
        ("&#x20;\\n\\1", " \\n\\1", 1),
    ],
)
def test_each_mark_is_undone_once(marked: str, restored: str, marks: int) -> None:
    assert undo.undo_bytes(marked.encode("utf-8")) == (
        restored.encode("utf-8"),
        marks,
    )


def test_an_escape_alone_is_no_mark() -> None:
    assert not undo.has_marks('"a \\_ b \\" c"')
    assert undo.has_marks("a\\\nb")
    assert undo.has_marks("&#32;")


def test_the_folder_is_copied_and_only_marked_answers_change(
    runs: Path, tmp_path: Path
) -> None:
    before = snapshot(runs)
    dst = tmp_path / "reversed"
    undo.undo_folder(runs, dst)
    after = snapshot(dst)
    del after[undo.LOG_NAME]
    assert set(after) == set(before)
    changed = [name for name in before if after[name] != before[name]]
    assert changed == ["bot-a/toy/original/1.json"]
    assert after[changed[0]] == PLAIN.encode("utf-8")


def test_the_source_stays_unchanged(runs: Path, tmp_path: Path) -> None:
    before = snapshot(runs)
    undo.undo_folder(runs, tmp_path / "reversed")
    assert snapshot(runs) == before


def test_the_log_names_every_answer_with_both_hashes(
    runs: Path, tmp_path: Path
) -> None:
    dst = tmp_path / "reversed"
    returned = undo.undo_folder(runs, dst)
    log = json.loads((dst / undo.LOG_NAME).read_text(encoding="utf-8"))
    assert log == returned
    marked, clean = log
    copied = chat_copy(PLAIN).encode("utf-8")
    assert marked["file"] == "bot-a/toy/original/1.json"
    assert marked["marks"] == undo.undo_bytes(copied)[1] > 0
    assert marked["sha256_before"] == hashlib.sha256(copied).hexdigest()
    assert marked["sha256_after"] == hashlib.sha256(PLAIN.encode()).hexdigest()
    assert clean["file"] == "bot-b/toy/original/1.json"
    assert clean["marks"] == 0
    assert clean["sha256_before"] == clean["sha256_after"]
    assert set(marked) == {"file", "marks", "sha256_before", "sha256_after"}


def test_an_existing_target_is_not_replaced(runs: Path, tmp_path: Path) -> None:
    dst = tmp_path / "reversed"
    dst.mkdir()
    with pytest.raises(undo.UndoError, match="already exists"):
        undo.undo_folder(runs, dst)
    assert snapshot(dst) == {}


def test_a_target_inside_the_source_is_refused(runs: Path) -> None:
    before = snapshot(runs)
    with pytest.raises(undo.UndoError, match="inside the source"):
        undo.undo_folder(runs, runs / "reversed")
    assert snapshot(runs) == before


def test_a_missing_source_is_refused(tmp_path: Path) -> None:
    with pytest.raises(undo.UndoError, match="not a folder"):
        undo.undo_folder(tmp_path / "missing", tmp_path / "reversed")
    assert not (tmp_path / "reversed").exists()


def test_the_marks_are_not_undone_twice(runs: Path, tmp_path: Path) -> None:
    undo.undo_folder(runs, tmp_path / "reversed")
    with pytest.raises(undo.UndoError, match="already undone"):
        undo.undo_folder(tmp_path / "reversed", tmp_path / "again")
    assert not (tmp_path / "again").exists()


def test_an_impossible_reference_stops_before_writing(
    runs: Path, tmp_path: Path
) -> None:
    write(runs / "bot-a/toy/original/2.json", b"&#x110000;")
    with pytest.raises(ValueError):
        undo.undo_folder(runs, tmp_path / "reversed")
    assert not (tmp_path / "reversed").exists()


def test_the_command_prints_counts_and_no_answer_text(
    runs: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dst = tmp_path / "reversed"
    assert undo.main(["--src", str(runs), "--dst", str(dst)]) == 0
    marks = undo.undo_bytes(chat_copy(PLAIN).encode("utf-8"))[1]
    assert capsys.readouterr().out == (
        f"2 answer files, 1 with copy marks, {marks} marks undone\n"
    )
    assert "Erfunden" not in (dst / undo.LOG_NAME).read_text(encoding="utf-8")
