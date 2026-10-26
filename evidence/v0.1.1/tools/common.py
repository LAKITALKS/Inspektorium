"""Shared helpers for the v0.1.1 evidence tools (standard library only)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from collections.abc import Iterable
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = TOOLS_DIR.parent
REPO_ROOT = EVIDENCE_DIR.parent.parent
CATALOG_PATH = EVIDENCE_DIR / "catalog" / "catalog.json"
VERSIONS_PATH = EVIDENCE_DIR / "config" / "versions.json"
RENDERERS = (
    "cmark-gfm-unsafe",
    "cmark-gfm-safe",
    "markdown-it-py-html",
    "python-markdown",
)
SECRET_MARKERS = ("API_KEY", "ANTHROPIC", "OPENAI", "TOKEN", "SECRET")
_ASCII_WS = re.compile(r"[ \t\n\r\f]+")
# Any remaining absolute local path (macOS/Linux temp or home locations) is
# reduced to its last component before it can reach a published file.
_LOCAL_PATH = re.compile(
    r"(?:file://)?(/(?:private/)?(?:tmp|var|Users|home)/(?:[^\s\"'#]*/)?)"
    r"([^\s\"'/#]*)"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_text_exact(path: Path) -> str:
    """Read a file as strict UTF-8 without newline translation.

    ``Path.read_text`` uses universal newlines and would turn a raw CR into LF;
    every CLI output file is read with this function instead, so the stored,
    hashed and rendered text equals the file bytes."""

    return path.read_bytes().decode("utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(payload), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")


def read_jsonl(path: Path) -> list[Any]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def normalize_ws(text: str) -> str:
    """Collapse ASCII whitespace runs (only) and strip; keeps other code points."""

    return _ASCII_WS.sub(" ", text).strip()


def canonical_text(text: str) -> str:
    """Mirror of the product's documented canonicalization (LF newlines, NFC)."""

    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))


def scrubbed_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Environment without credentials; never printed or stored."""

    env = {
        key: value
        for key, value in os.environ.items()
        if not any(marker in key.upper() for marker in SECRET_MARKERS)
    }
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("EVIDENCE_NETGUARD_LOG", None)
    env.pop("PYTHONPATH", None)
    if extra:
        env.update(extra)
    return env


class Sanitizer:
    """Replace local absolute paths before anything is written to the package."""

    def __init__(self, replacements: dict[str, str]) -> None:
        items = []
        for path, label in replacements.items():
            if not path:
                continue
            resolved = str(Path(path).resolve())
            items.append((resolved, label))
            items.append((path, label))
            if resolved.startswith("/private/"):
                items.append((resolved[len("/private") :], label))
        home = str(Path.home())
        items.append((home, "<HOME>"))
        self._items = sorted(set(items), key=lambda item: -len(item[0]))

    def text(self, value: str) -> str:
        for path, label in self._items:
            value = value.replace(path, label)
        return _LOCAL_PATH.sub(lambda m: "<LOCAL>/" + m.group(2), value)

    def obj(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.text(value)
        if isinstance(value, list):
            return [self.obj(item) for item in value]
        if isinstance(value, dict):
            return {self.text(str(k)): self.obj(v) for k, v in value.items()}
        return value


def get_path(payload: Any, dotted: str) -> Any:
    """Resolve 'findings.0.validation_issues.0.code' style paths."""

    current = payload
    for part in dotted.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def control_codepoints(text: str) -> list[str]:
    """Raw code points that criterion K9 forbids (Cc except TAB/LF/CR, Cf, Zl,
    Zp, Cs)."""

    found = []
    for char in text:
        category = unicodedata.category(char)
        if char in "\t\n\r":
            continue
        if category in ("Cc", "Cf", "Zl", "Zp", "Cs"):
            found.append(f"U+{ord(char):04X}")
    return found
