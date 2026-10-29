"""Input normalization outside the product, for the sensitivity analysis.

This is not Inspektorium behavior. It maps U+2009 THIN SPACE, U+202F NARROW
NO-BREAK SPACE and U+00A0 NO-BREAK SPACE to U+0020 in the judges' answers,
the source and the pieces, and writes the results to a new input folder.

sensitivity.py --inputs DIR --out DIR
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

SPACES = {" ": " ", " ": " ", " ": " "}


def normalize_spaces(text: str) -> str:
    return text.translate(str.maketrans(SPACES))


def write_normalized_inputs(inputs: Path, out: Path) -> dict[str, int]:
    """Write a space-normalized copy of the inputs; return replaced counts."""

    if out.exists():
        raise SystemExit(f"output folder exists: {out}")
    replaced: dict[str, int] = {}
    for relative in ("judges", "source"):
        for path in sorted((inputs / relative).glob("*.txt")):
            text = path.read_text(encoding="utf-8")
            target = out / relative / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(normalize_spaces(text), encoding="utf-8")
            replaced[f"{relative}/{path.name}"] = sum(text.count(c) for c in SPACES)
    pieces = json.loads((inputs / "extraction/pieces.json").read_text(encoding="utf-8"))
    count = 0
    for piece in pieces:
        count += sum(piece["quote"].count(c) for c in SPACES)
        piece["quote"] = normalize_spaces(piece["quote"])
    target = out / "extraction/pieces.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(pieces, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    replaced["extraction/pieces.json"] = count
    shutil.copy2(inputs / "PREREGISTRATION.md", out / "PREREGISTRATION.md")
    return replaced


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_normalized_inputs(args.inputs, args.out), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
