"""Run the frozen quote checker on the reference cases and count the outcome.

This is the component test. Each case is checked in both modes against the
sentence bank of its text, and ``location_valid`` is compared with the expected
value of the case. The checker and the kernel are used unchanged. Two kinds of
deviation are counted apart:

- a *false accept*: the case is constructed as invalid, the checker accepts it;
- a *false reject*: the case is constructed as valid, the checker rejects it.

The result is counts, as the README agrees: ``0 von n`` and no error rate. A
deviating case is named by its id and the checker's reason, never by its text.

The runner stops before it reads a case if the frozen tools differ from the
README, if the kernel does not come from ``src/`` of this checkout, or if the
SHA-256 of the case file is not the given one. The held-out part needs that
SHA-256. An existing result is never replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import check_quotes
from genius_loader import SentenceBank, dump_json, read_bank
from make_reference_cases import EXPECTED

import inspektorium

STUDY_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = STUDY_ROOT.parents[1]
DEFAULT_BANKS = STUDY_ROOT / "data" / "selected"
DEFAULT_SUMMARY = STUDY_ROOT / "prereg" / "reference_cases_summary.json"

FROZEN_SRC_TREE = "0afbc0115f904d6408b1b8196af4e019678d3c56"
FROZEN_CHECKER_BLOB = "2a3368683da37db01ae6487dc75cf552c6bfa9e0"
DEVELOPMENT = "development"
HELD_OUT = "held_out"
PARTS = (DEVELOPMENT, HELD_OUT)
FALSE_ACCEPT = "false_accept"
FALSE_REJECT = "false_reject"
_EXPECTED_FIELD: dict[check_quotes.Mode, str] = {
    "strict": "expected_strict",
    "normalized": "expected_normalized",
}


class RunError(RuntimeError):
    """The component test cannot run as agreed; no result is written."""


def git(*arguments: str) -> str:
    process = subprocess.run(
        ["git", *arguments], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if process.returncode != 0:
        raise RunError("the frozen state needs a Git checkout")
    return process.stdout.strip()


def frozen_state() -> dict[str, str]:
    """Return the ids of the frozen tools, or stop if one is not as agreed.

    ``git hash-object`` and the clean state of ``src/`` describe the files on
    disk, so an uncommitted change cannot pass.
    """

    checker = Path(check_quotes.__file__).resolve()
    if checker != STUDY_ROOT / "scripts" / "check_quotes.py":
        raise RunError("the quote checker is not the one of this study")
    kernel = Path(inspektorium.__file__).resolve()
    if not kernel.is_relative_to(REPO_ROOT / "src"):
        raise RunError("the kernel does not come from src/ of this checkout")
    blob = git("hash-object", str(checker))
    tree = git("rev-parse", "HEAD:src")
    if blob != FROZEN_CHECKER_BLOB or tree != FROZEN_SRC_TREE:
        raise RunError("a frozen tool differs from the agreed state")
    if git("status", "--porcelain", "--", "src"):
        raise RunError("src/ has uncommitted changes")
    return {
        "commit": git("rev-parse", "HEAD"),
        "src_tree": tree,
        "check_quotes_blob": blob,
    }


def read_cases(
    raw: bytes, expected_counts: Mapping[str, int]
) -> list[Mapping[str, Any]]:
    """Return the cases if ids, labels and counts are as documented."""

    cases: list[Mapping[str, Any]] = json.loads(raw)
    ids = [case["case_id"] for case in cases]
    if len(set(ids)) != len(ids):
        raise RunError("a case id appears twice")
    for case in cases:
        label = (case["expected_strict"], case["expected_normalized"])
        if EXPECTED.get(case["type"]) != label:
            raise RunError(f"{case['case_id']}: label and type do not fit")
    counts = {
        case_type: sum(case["type"] == case_type for case in cases)
        for case_type in EXPECTED
    }
    if counts != dict(expected_counts):
        raise RunError("the number of cases differs from the summary")
    return cases


def evaluate(
    cases: Sequence[Mapping[str, Any]], banks: Mapping[str, SentenceBank]
) -> dict[str, Any]:
    """Check every case in both modes and count the deviations."""

    by_type: dict[str, dict[str, dict[str, int]]] = {}
    total = {
        mode: {"cases": 0, FALSE_ACCEPT: 0, FALSE_REJECT: 0}
        for mode in check_quotes.MODES
    }
    deviations: list[dict[str, str]] = []
    for case in cases:
        for mode in check_quotes.MODES:
            expected = case[_EXPECTED_FIELD[mode]]
            result = check_quotes.check_quote(
                banks[case["text_id"]], case["claimed_sid"], case["quote"], mode
            )
            cell = by_type.setdefault(case["type"], {}).setdefault(
                mode, {"cases": 0, FALSE_ACCEPT: 0, FALSE_REJECT: 0}
            )
            cell["cases"] += 1
            total[mode]["cases"] += 1
            if result.location_valid == expected:
                continue
            kind = FALSE_REJECT if expected else FALSE_ACCEPT
            cell[kind] += 1
            total[mode][kind] += 1
            deviations.append(
                {
                    "case_id": case["case_id"],
                    "mode": mode,
                    "kind": kind,
                    "reason": result.reason,
                }
            )
    return {"total": total, "by_type": by_type, "deviations": deviations}


def run(
    part: str, cases_path: Path, sha256: str | None, banks: Path, summary: Path
) -> dict[str, Any]:
    """Check the preconditions, then evaluate one part."""

    state = frozen_state()
    if part == HELD_OUT and sha256 is None:
        raise RunError("the held-out part needs its SHA-256")
    raw = cases_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if sha256 is not None and digest != sha256:
        raise RunError("the SHA-256 of the case file is not the given one")
    by_type = json.loads(summary.read_text(encoding="utf-8"))["by_type"]
    cases = read_cases(raw, {name: by_type[name][part] for name in by_type})
    loaded = {
        text_id: read_bank(banks / f"{text_id}.json")
        for text_id in sorted({case["text_id"] for case in cases})
    }
    return {
        "part": part,
        "cases_sha256": digest,
        "frozen": state,
        "python": platform.python_version(),
        **evaluate(cases, loaded),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", choices=PARTS, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--sha256")
    parser.add_argument("--banks", type=Path, default=DEFAULT_BANKS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        raise RunError(f"{args.out.name} already exists and is not replaced")
    result = run(args.part, args.cases, args.sha256, args.banks, args.summary)
    args.out.write_bytes(dump_json(result))
    print(f"{args.part}, cases {result['cases_sha256']}")
    for mode, cell in result["total"].items():
        invalid = sum(
            counts[mode]["cases"]
            for case_type, counts in result["by_type"].items()
            if not EXPECTED[case_type][check_quotes.MODES.index(mode)]
        )
        print(
            f"{mode}: false accepts {cell[FALSE_ACCEPT]} of {invalid}, "
            f"false rejects {cell[FALSE_REJECT]} of {cell['cases'] - invalid}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
