r"""Undo the marks of a copy path in a copy of the answers.

The copy button of one chat interface returns Markdown-escaped text: a backslash
before each line break, ``&#x20;`` for a leading space, and a backslash before
some punctuation. ``prereg/deviations_2026-11-25.md`` fixed this rule before any
result was viewed:

1. A backslash directly before a line break or at the end of the file is removed.
2. In one pass, a backslash followed by ASCII punctuation is replaced by the
   punctuation, and numeric character references are decoded.

The rule applies only to answer files with a mark of step 1 or a numeric
character reference. Every other file is copied byte for byte, so a ``\"`` in an
answer without marks stays. An answer that is not UTF-8 is copied unchanged.

The source folder is never changed. The log lists every answer file with the
number of undone marks and the SHA-256 before and after. It holds no answer text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

EOL = re.compile(r"\\(?=\r?\n)|\\\Z")
ESC = re.compile(r"\\([!-/:-@\[-`{-~])|&#x([0-9A-Fa-f]+);|&#([0-9]+);")
REFERENCE = re.compile(r"&#x?[0-9A-Fa-f]+;")
META_SUFFIX = ".meta.json"
LOG_NAME = "undo_copy_marks_log.json"


class UndoError(RuntimeError):
    """The copy cannot be made as agreed; nothing was written."""


def has_marks(text: str) -> bool:
    return bool(EOL.search(text) or REFERENCE.search(text))


def _decoded(match: re.Match[str]) -> str:
    punctuation, hexadecimal, decimal = match.groups()
    if punctuation is not None:
        return str(punctuation)
    if hexadecimal is not None:
        return chr(int(hexadecimal, 16))
    return chr(int(decimal))


def undo_marks(text: str) -> tuple[str, int]:
    """Return the text without the marks, and how many there were."""

    text, line_ends = EOL.subn("", text)
    text, escapes = ESC.subn(_decoded, text)
    return text, line_ends + escapes


def undo_bytes(raw: bytes) -> tuple[bytes, int]:
    """Apply the rule to one answer; without marks, return the same bytes."""

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw, 0
    if not has_marks(text):
        return raw, 0
    restored, marks = undo_marks(text)
    return restored.encode("utf-8"), marks


def answer_files(runs: Path) -> list[Path]:
    """List the answers in the layout of ``import_runs.py``, without metadata."""

    return sorted(
        path
        for path in runs.glob("*/*/*/*.json")
        if not path.name.endswith(META_SUFFIX)
    )


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def undo_folder(src: Path, dst: Path) -> list[dict[str, Any]]:
    """Copy ``src`` to the new folder ``dst`` and undo the marks there."""

    if not src.is_dir():
        raise UndoError("the source is not a folder")
    if dst.exists():
        raise UndoError("the target already exists and is not replaced")
    if dst.resolve().is_relative_to(src.resolve()):
        raise UndoError("the target is inside the source")
    if (src / LOG_NAME).exists():
        raise UndoError("the marks in the source are already undone")
    log: list[dict[str, Any]] = []
    restored: dict[Path, bytes] = {}
    for path in answer_files(src):
        relative = path.relative_to(src)
        before = path.read_bytes()
        after, marks = undo_bytes(before)
        if after != before:
            restored[relative] = after
        log.append(
            {
                "file": relative.as_posix(),
                "marks": marks,
                "sha256_before": _sha256(before),
                "sha256_after": _sha256(after),
            }
        )
    shutil.copytree(src, dst)
    for relative, content in restored.items():
        (dst / relative).write_bytes(content)
    (dst / LOG_NAME).write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    return log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--dst", type=Path, required=True)
    args = parser.parse_args(argv)
    log = undo_folder(args.src, args.dst)
    marked = sum(entry["marks"] > 0 for entry in log)
    marks = sum(entry["marks"] for entry in log)
    print(f"{len(log)} answer files, {marked} with copy marks, {marks} marks undone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
