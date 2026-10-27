"""Compare the kernel's verdicts with the preregistered predictions.

evaluate.py --runs DIR --out DIR

Reads the reports written by run_replay.py and writes pieces_results.json
and summary.json. For every piece whose quote has no exact occurrence in the
source, it lists the code points where the quote differs from the window the
locator chose.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PACKAGE = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from inspektorium.core.normalization import normalize_text  # noqa: E402

JUDGES = ("grok", "astra", "gemini")
PREDICTION = {"strict": "predicted_strict", "normalized": "predicted_space_normalized"}
CONTROL_EXPECTED = {
    "control-pos-1": "PASSED",
    "control-pos-2": "PASSED",
    "control-neg-1": "FAILED",
    "control-neg-2": "FAILED",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def differences(quote: str, window: str) -> list[dict]:
    """Positions where a same-length quote and source window differ."""

    return [
        {"offset_in_quote": i, "quote": f"U+{ord(a):04X}", "source": f"U+{ord(b):04X}"}
        for i, (a, b) in enumerate(zip(quote, window, strict=True))
        if a != b
    ]


def case_rows(runs: Path, variant: str, case: str, pieces: dict) -> list[dict]:
    folder = runs / variant / case
    report = load(folder / "report.json")
    locators = load(folder / "locator.json")
    source = normalize_text(load(folder / "input.json")["sources"][0]["text"])
    rows = []
    for finding in report["findings"]:
        core_id = finding["claim_id"]
        locator = locators[core_id]
        piece_id = locator["piece_id"]
        status = finding["deterministic_validation_status"].upper()
        if case == "controls":
            expected = CONTROL_EXPECTED[core_id]
        else:
            expected = pieces[piece_id][PREDICTION[variant]]
        quote = finding["evidence_quote"]
        window = source[locator["evidence_start"] : locator["evidence_end"]]
        rows.append(
            {
                "piece_id": piece_id,
                "core_id": core_id,
                "judge": case if case != "controls" else None,
                "variant": variant,
                "locator": locator["method"],
                "claim_start": finding["claim_start"],
                "claim_end": finding["claim_end"],
                "evidence_start": locator["evidence_start"],
                "evidence_end": locator["evidence_end"],
                "l2_ratio": locator["l2_ratio"],
                "exact_occurrences_in_canonical_source": locator[
                    "exact_occurrences_in_canonical_source"
                ],
                "status": status,
                "issue_codes": [
                    issue["code"] for issue in finding["validation_issues"]
                ],
                "expected": expected,
                "hit": status == expected,
                "differing_code_points": []
                if quote == window
                else differences(quote, window),
            }
        )
    return rows


def counts(rows: list[dict]) -> dict:
    return {
        "PASSED": sum(r["status"] == "PASSED" for r in rows),
        "FAILED": sum(r["status"] == "FAILED" for r in rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    meta = load(args.runs / "run_meta.json")
    raw = load(PACKAGE / "inputs/judge-replay/extraction/pieces.json")
    pieces = {p["id"]: p for p in raw}
    results = {}
    for variant in ("strict", "normalized"):
        judge_rows = [
            row
            for judge in JUDGES
            for row in case_rows(args.runs, variant, judge, pieces)
        ]
        results[variant] = {
            "pieces": judge_rows,
            "controls": case_rows(args.runs, variant, "controls", pieces),
        }
    strict = results["strict"]["pieces"]
    by_id = {row["piece_id"]: row for row in strict}
    typography = ("grok-3A", "astra-4A", "gemini-3A")
    controls_ok = all(row["hit"] for row in results["strict"]["controls"])
    summary = {
        "environment": meta["environment"],
        "network": meta["network"],
        "guard": meta["guard"],
        "exit_codes": meta["exit_codes"],
        "relation": "supported",
        "strict": {
            "predicted": {"PASSED": 39, "FAILED": 4},
            "result": counts(strict),
            "hits": sum(row["hit"] for row in strict),
            "pieces": len(strict),
        },
        "true_positive_grok_4B": {
            "predicted": "FAILED",
            "status": by_id["grok-4B"]["status"],
            "issue_codes": by_id["grok-4B"]["issue_codes"],
            "exact_occurrences_in_canonical_source": by_id["grok-4B"][
                "exact_occurrences_in_canonical_source"
            ],
        },
        "typography": {
            pid: {
                "predicted": "FAILED",
                "status": by_id[pid]["status"],
                "issue_codes": by_id[pid]["issue_codes"],
                "differing_code_points": by_id[pid]["differing_code_points"],
            }
            for pid in typography
        },
        "normalized": {
            "predicted": {"PASSED": 42, "FAILED": 1},
            "result": counts(results["normalized"]["pieces"]),
            "hits": sum(row["hit"] for row in results["normalized"]["pieces"]),
            "pieces": len(results["normalized"]["pieces"]),
        },
        "controls": {
            "expected": "2 PASSED, 2 FAILED",
            "strict": {
                r["core_id"]: r["status"] for r in results["strict"]["controls"]
            },
            "normalized": {
                r["core_id"]: r["status"] for r in results["normalized"]["controls"]
            },
            "valid": controls_ok,
        },
        "deviations": [
            {
                "variant": variant,
                "piece_id": row["piece_id"],
                "expected": row["expected"],
                "status": row["status"],
                "issue_codes": row["issue_codes"],
            }
            for variant in ("strict", "normalized")
            for row in results[variant]["pieces"] + results[variant]["controls"]
            if not row["hit"]
        ],
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "pieces_results.json").write_text(
        json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {k: summary[k] for k in ("strict", "normalized", "controls")}, indent=1
        )
    )
    return 0 if controls_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
