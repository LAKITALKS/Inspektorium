"""Compare two result directories (e.g. baseline and candidate) case by case.

* JSON reports: for every case accepted by both versions, the JSON report bytes
  (SHA-256 of the output file) must be identical; raw values and guard results
  therefore cannot differ.
* CLI outcomes and case verdicts side by side (before/after table).
Only recorded rows are used; a case missing on either side is listed as such.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from common import read_json, read_jsonl, write_json


def compare(before: Path, after: Path, catalog: dict[str, Any]) -> dict[str, Any]:
    cli_before = {
        (r["case"], r["format"]): r for r in read_jsonl(before / "cli_results.jsonl")
    }
    cli_after = {
        (r["case"], r["format"]): r for r in read_jsonl(after / "cli_results.jsonl")
    }
    verdict_before = {r["case"]: r for r in read_jsonl(before / "case_verdicts.jsonl")}
    verdict_after = {r["case"]: r for r in read_jsonl(after / "case_verdicts.jsonl")}
    json_same: list[str] = []
    json_diff: list[str] = []
    not_both: list[str] = []
    missing: list[str] = []
    markdown_changed = 0
    table = []
    for case in catalog["cases"]:
        cid = case["id"]
        b = cli_before.get((cid, "json"))
        a = cli_after.get((cid, "json"))
        if b is None or a is None:
            missing.append(cid)
        elif b["cli_outcome"] == "ACCEPTED" and a["cli_outcome"] == "ACCEPTED":
            (
                json_same if b["output_sha256"] == a["output_sha256"] else json_diff
            ).append(cid)
        else:
            not_both.append(cid)
        mb = cli_before.get((cid, "markdown"))
        ma = cli_after.get((cid, "markdown"))
        if mb and ma and mb["output_sha256"] != ma["output_sha256"]:
            markdown_changed += 1
        vb = verdict_before.get(cid, {})
        va = verdict_after.get(cid, {})
        table.append(
            {
                "case": cid,
                "family": case["family"],
                "kind": case["kind"],
                "before_cli": vb.get("cli"),
                "after_cli": va.get("cli"),
                "before_verdict": vb.get("verdict"),
                "after_verdict": va.get("verdict"),
                "before_outcomes": vb.get("outcomes"),
                "after_outcomes": va.get("outcomes"),
            }
        )
    transitions = Counter(
        f"{row['before_verdict']} -> {row['after_verdict']}" for row in table
    )
    return {
        "before": read_json(before / "run_manifest.json")["run_label"],
        "after": read_json(after / "run_manifest.json")["run_label"],
        "json_reports": {
            "accepted_by_both": len(json_same) + len(json_diff),
            "byte_identical": len(json_same),
            "different": json_diff,
            "not_accepted_by_both": not_both,
            "missing_rows": missing,
        },
        "markdown_reports_changed": markdown_changed,
        "verdict_transitions": dict(sorted(transitions.items())),
        "cases": table,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    result = compare(Path(args.before), Path(args.after), read_json(Path(args.catalog)))
    write_json(Path(args.out), result)
    print(
        json.dumps(
            {k: result[k] for k in ("json_reports", "verdict_transitions")}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
