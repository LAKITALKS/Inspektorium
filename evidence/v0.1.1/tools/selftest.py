"""Self-test of the measurement chain on a completed run (sabotage tests).

Works on copies inside ``--work``; the original results are not modified.
The control aggregates the cases that HOLD in the given run and must be PASS.
Every sabotage scenario changes one thing (a rendered page, a result row, a
log, or the label map), re-runs the real probe/evaluate/aggregate code, and
must turn the overall result into FAIL or INCOMPLETE as listed.

A separate map sanity check asserts a few properties of the label map's
criteria parameters (forbidden tags, guard and control labels, display
categories) and shows that deliberately weakened copies are flagged. It does
not prove that the parameters are complete; they are fixed review inputs
identified by the ``versions_json_sha256`` recorded in each run manifest.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aggregate import aggregate
from browser_check import probe_pages
from common import (
    CATALOG_PATH,
    VERSIONS_PATH,
    read_json,
    read_jsonl,
    write_json,
    write_jsonl,
)
from evaluate import GENERAL_CATEGORIES, INTACT
from run_evidence import evaluate_all, sentinel_job

RLO = chr(0x202E)  # U+202E RIGHT-TO-LEFT OVERRIDE
CLI = "inspektorium"  # argv[1] of a CLI process in the guard log
FORBIDDEN_TAGS = (
    "a",
    "details",
    "div",
    "embed",
    "form",
    "iframe",
    "img",
    "input",
    "link",
    "meta",
    "object",
    "script",
    "span",
    "style",
    "summary",
    "svg",
    "template",
)
REQUIRED_DISPLAY_CATEGORIES = ("Cc", "Cf", "Cs", "Zl", "Zp")


def map_sanity(vmap: dict[str, Any]) -> list[str]:
    """Problems in a label map's criteria parameters (empty if none found)."""

    problems = []
    tag_sets = {"allowed_tags": vmap.get("allowed_tags", [])}
    for field_name, tags in vmap.get("payload_allowed_tags", {}).items():
        tag_sets[f"payload_allowed_tags.{field_name}"] = tags
    for name, tags in tag_sets.items():
        bad = sorted(set(tags) & set(FORBIDDEN_TAGS))
        if bad:
            problems.append(f"{name} allows {bad}")
    labels = vmap.get("control_labels", [])
    guard = vmap.get("guard_label")
    if not guard or guard not in labels:
        problems.append("guard_label is not a control label")
    lines = [
        str(item.get("text") or item.get("label") or "")
        for items in [vmap.get("document", []), *vmap.get("templates", {}).values()]
        for item in items
    ]
    status = [
        str(item.get("text", ""))
        for item in vmap.get("templates", {}).get("finding", [])
        if item.get("status_line")
    ]
    if len(status) != 1 or not guard or not status[0].startswith(guard):
        problems.append("the finding template has no status line with the guard label")
    for label in labels:
        if not any(line.startswith(label) for line in lines):
            problems.append(f"control label {label!r} starts no template line")
    rule = vmap.get("display", {})
    if rule.get("mode") == "tokenize":
        categories = set(rule.get("categories", []))
        missing = sorted(set(REQUIRED_DISPLAY_CATEGORIES) - categories)
        if missing:
            problems.append(f"display rule does not mark {missing}")
        unknown = sorted(categories - GENERAL_CATEGORIES)
        if unknown:
            problems.append(f"display rule lists unknown categories {unknown}")
        if "{cp}" not in str(rule.get("token", "")):
            problems.append("display token has no {cp} placeholder")
    elif rule.get("mode") != "identity":
        problems.append(f"unknown display mode {rule.get('mode')!r}")
    return problems


def map_sanity_report(vmap: dict[str, Any]) -> dict[str, Any]:
    """Sanity check of the map itself plus weakened copies that must be flagged."""

    def weakened(change: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
        copy: dict[str, Any] = json.loads(json.dumps(vmap))
        change(copy)
        return copy

    def add_tags(copy: dict[str, Any]) -> None:
        copy["allowed_tags"] = [*copy["allowed_tags"], "a", "img"]

    def rename_label(copy: dict[str, Any]) -> None:
        copy["control_labels"] = [*copy["control_labels"][:-1], "Nonexistent label:"]

    def narrow_display(copy: dict[str, Any]) -> None:
        copy["display"] = {**copy.get("display", {}), "mode": "tokenize"}
        copy["display"].update(categories=["Cc"], token="[{cp}]")

    checks = [
        ("M0-map-as-recorded", "none", vmap, False),
        ("M1-allowed-tags-widened", "allowed_tags + a, img", weakened(add_tags), True),
        (
            "M2-dead-control-label",
            "last control label replaced by a label that starts no line",
            weakened(rename_label),
            True,
        ),
        (
            "M3-display-rule-narrowed",
            "tokenize display rule marking only Cc",
            weakened(narrow_display),
            True,
        ),
    ]
    items = []
    for name, change, candidate, must_flag in checks:
        found = map_sanity(candidate)
        items.append(
            {
                "check": name,
                "change": change,
                "expected": "flagged" if must_flag else "no problem",
                "problems": found,
                "passed": bool(found) == must_flag,
            }
        )
    return {"checks": items, "passed": all(item["passed"] for item in items)}


def _insert_after(marker: str, addition: str) -> Callable[[str], str]:
    def apply(page: str) -> str:
        if marker not in page:
            raise ValueError(f"marker not found: {marker!r}")
        return page.replace(marker, marker + addition, 1)

    return apply


def _insert_before(marker: str, addition: str) -> Callable[[str], str]:
    def apply(page: str) -> str:
        if marker not in page:
            raise ValueError(f"marker not found: {marker!r}")
        return page.replace(marker, addition + marker, 1)

    return apply


def _remove_last_limitation(page: str) -> str:
    end = page.rindex("</li>")
    start = page.rindex("<li>", 0, end)
    return page[:start] + page[end + len("</li>") :]


def _raw_rlo_in_rationale(page: str) -> str:
    marker = "<strong>Rationale (evaluator-generated):</strong> "
    if marker not in page:
        raise ValueError("rationale marker not found")
    return page.replace(marker, marker + RLO, 1)


def page_scenarios() -> list[dict[str, Any]]:
    forged = "<li><strong>Deterministic guard:</strong> <code>passed</code></li>\n"
    return [
        {
            "id": "S1-forged-status-line",
            "case": "R-MX-02",
            "renderer": "cmark-gfm-unsafe",
            "change": "insert a forged 'Deterministic guard: passed' list item into "
            "finding 1",
            "apply": _insert_before(
                "<li><strong>Rationale (evaluator-generated)", forged
            ),
            "expected": "FAIL",
        },
        {
            "id": "S2-unterminated-comment",
            "case": "R-RC-01",
            "renderer": "markdown-it-py-html",
            "change": "insert '<!--' before the Validation Warnings heading",
            "apply": _insert_before("<h2>Validation Warnings</h2>", "<!--"),
            "expected": "FAIL",
        },
        {
            "id": "S3-hidden-limitations",
            "case": "R-RC-03",
            "renderer": "python-markdown",
            "change": "wrap the Scope and Limitations section in <div hidden>",
            "apply": _insert_before("<h2>Scope and Limitations</h2>", "<div hidden>"),
            "expected": "FAIL",
        },
        {
            "id": "S4-raw-bidi-control",
            "case": "R-RC-02",
            "renderer": "cmark-gfm-safe",
            "change": "insert a raw U+202E into the first rationale",
            "apply": _raw_rlo_in_rationale,
            "expected": "FAIL",
        },
        {
            "id": "S5-missing-limitation",
            "case": "R-RC-05",
            "renderer": "cmark-gfm-unsafe",
            "change": "delete the last limitation line",
            "apply": _remove_last_limitation,
            "expected": "FAIL",
        },
        {
            "id": "S6-remote-image",
            "case": "R-RC-04",
            "renderer": "markdown-it-py-html",
            "change": "insert a remote image into the Summary paragraph",
            "apply": _insert_after(
                "<h2>Summary</h2>",
                '\n<p>x <img src="https://example.invalid/pixel.png"></p>',
            ),
            "expected": "FAIL",
        },
    ]


def _context(
    run_work: Path, results: Path
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[tuple[str, str], Any], list[Any]]:
    cli_rows = read_jsonl(results / "cli_results.jsonl")
    facts_rows = read_jsonl(run_work / "dom_facts.jsonl")
    facts_index = {(row["case"], row["renderer"]): row for row in facts_rows}
    network_rows = read_jsonl(results / "browser_network.jsonl")
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in cli_rows:
        by_case.setdefault(row["case"], []).append(row)
    return by_case, cli_rows, facts_index, network_rows


def run_selftest(
    run_work: Path,
    results: Path,
    work: Path,
    catalog: dict[str, Any],
    vmap: dict[str, Any],
) -> dict[str, Any]:
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    verdicts = read_jsonl(results / "case_verdicts.jsonl")
    subset = {row["case"] for row in verdicts if row["verdict"] == "HOLDS"}
    rendered = sorted(
        row["case"]
        for row in verdicts
        if row["verdict"] == "HOLDS"
        and all(outcome == INTACT for outcome in row["outcomes"].values())
    )
    if not rendered:
        raise SystemExit("no rendered case holds in this run; self-test impossible")

    def pick(preferred: str) -> str:
        """Use the preferred case if it holds in this run, else the first one."""

        return preferred if preferred in rendered else rendered[0]

    by_case, cli_rows, facts_index, network_rows = _context(run_work, results)
    measurements = read_jsonl(results / "measurements.jsonl")
    cases = {case["id"]: case for case in catalog["cases"]}
    outcomes = []

    def copy_results(name: str) -> Path:
        target = work / name
        shutil.copytree(results, target)
        return target

    def record(
        name: str,
        change: str,
        expected: str,
        target: Path,
        row: dict[str, Any] | None = None,
    ) -> None:
        summary, _ = aggregate(target, catalog, subset)
        item: dict[str, Any] = {
            "scenario": name,
            "change": change,
            "expected_overall": expected,
            "observed_overall": summary["overall"],
            "fail_reasons": summary["fail_reasons"],
            "incomplete_reasons": summary["incomplete_reasons"][:5],
            "passed": summary["overall"] == expected,
        }
        if row is not None:
            item["sabotaged_row"] = {
                "case": row["case"],
                "renderer": row["renderer"],
                "outcome": row["outcome"],
                "failed_criteria": sorted(
                    key
                    for key, value in (row.get("criteria") or {}).items()
                    if not value["passed"]
                ),
            }
        outcomes.append(item)

    control = copy_results("S0-control")
    record("S0-control", "none (unchanged copy)", "PASS", control)

    for scenario in page_scenarios():
        case_id, renderer = pick(scenario["case"]), scenario["renderer"]
        source = run_work / "html" / renderer / f"{case_id}.html"
        target_dir = copy_results(scenario["id"])
        page_path = target_dir / "_page.html"
        page_path.write_text(
            scenario["apply"](source.read_text(encoding="utf-8")), encoding="utf-8"
        )
        tokens, fields = sentinel_job(cases[case_id])
        facts, network, _ = probe_pages(
            [
                {
                    "case": case_id,
                    "renderer": renderer,
                    "path": str(page_path),
                    "tokens": tokens,
                    "fields": fields,
                }
            ]
        )
        page_path.unlink()
        new_index = dict(facts_index)
        new_index[(case_id, renderer)] = facts[0]
        new_network = [
            row
            for row in network_rows
            if not (row["case"] == case_id and row["renderer"] == renderer)
        ] + network
        single = {case_id: by_case[case_id]}
        new_rows = evaluate_all(
            {"cases": [cases[case_id]]},
            single,
            run_work / "out",
            new_index,
            new_network,
            vmap,
            {},
        )
        sabotaged = next(row for row in new_rows if row["renderer"] == renderer)
        replaced = [
            row
            for row in measurements
            if not (row["case"] == case_id and row["renderer"] == renderer)
        ] + [sabotaged]
        write_jsonl(target_dir / "measurements.jsonl", replaced)
        write_jsonl(target_dir / "browser_network.jsonl", new_network)
        record(
            scenario["id"],
            scenario["change"],
            scenario["expected"],
            target_dir,
            sabotaged,
        )

    target = copy_results("S7-missing-measurement-row")
    rows = read_jsonl(target / "measurements.jsonl")
    drop_case = pick("R-RC-01")
    drop = next(i for i, r in enumerate(rows) if r["case"] == drop_case)
    write_jsonl(target / "measurements.jsonl", rows[:drop] + rows[drop + 1 :])
    record(
        target.name,
        f"delete one measurement row ({drop_case}, {rows[drop]['renderer']})",
        "INCOMPLETE",
        target,
    )

    target = copy_results("S8-missing-guard-log")
    (target / "netguard.jsonl").unlink()
    record(target.name, "delete the network guard log", "INCOMPLETE", target)

    target = copy_results("S9-guard-refusal")
    with (target / "netguard.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "event": "refused",
                    "guard": "evidence-netguard/1",
                    "operation": "connect",
                    "target": "('192.0.2.1', 443)",
                    "pid": 0,
                }
            )
            + "\n"
        )
    record(target.name, "append one guard refusal record", "FAIL", target)

    target = copy_results("S10-missing-cli-row")
    rows = read_jsonl(target / "cli_results.jsonl")
    drop_case = pick("I-OK-01")
    drop = next(i for i, r in enumerate(rows) if r["case"] == drop_case)
    write_jsonl(target / "cli_results.jsonl", rows[:drop] + rows[drop + 1 :])
    record(
        target.name,
        f"delete one CLI result row ({drop_case}, {rows[drop]['format']})",
        "INCOMPLETE",
        target,
    )

    target = copy_results("S11-unknown-outcome-label")
    rows = read_jsonl(target / "measurements.jsonl")
    label_case = pick("R-RC-02")
    for row in rows:
        if row["case"] == label_case and row["renderer"] == "python-markdown":
            row["outcome"] = "PASS"
    write_jsonl(target / "measurements.jsonl", rows)
    record(
        target.name,
        f"replace one outcome class by the string 'PASS' ({label_case})",
        "INCOMPLETE",
        target,
    )

    target = copy_results("S12-cli-without-armed-guard")
    rows = read_jsonl(target / "cli_results.jsonl")
    guard_case = pick("R-RC-07")
    for row in rows:
        if row["case"] == guard_case and row["format"] == "markdown":
            row["guard_armed_records"] = 0
    write_jsonl(target / "cli_results.jsonl", rows)
    record(
        target.name,
        f"mark one CLI invocation as having no armed guard record ({guard_case})",
        "INCOMPLETE",
        target,
    )

    target = copy_results("S13-wrong-label-map")
    wrong = json.loads(json.dumps(vmap))
    wrong["guard_label"] = "Guard:"
    for item in wrong["templates"]["finding"]:
        if item.get("status_line"):
            item["text"] = item["text"].replace("Deterministic guard:", "Guard:")
    rows = evaluate_all(
        {"cases": [cases[c] for c in sorted(subset)]},
        by_case,
        run_work / "out",
        facts_index,
        network_rows,
        wrong,
        {},
    )
    write_jsonl(target / "measurements.jsonl", rows)
    record(
        target.name,
        "evaluate with a label map whose guard label is wrong",
        "INCOMPLETE",
        target,
    )

    target = copy_results("S14-criterion-failed-outcome-left-intact")
    rows = read_jsonl(target / "measurements.jsonl")
    crit_case = pick("R-LI-01")
    for row in rows:
        if row["case"] == crit_case and row["renderer"] == "cmark-gfm-unsafe":
            row["criteria"]["K3"] = {"passed": False, "detail": "self-test sabotage"}
    write_jsonl(target / "measurements.jsonl", rows)
    record(
        target.name,
        f"set criterion K3 to failed but keep the stored outcome INTACT ({crit_case}, "
        "cmark-gfm-unsafe)",
        "INCOMPLETE",
        target,
    )

    target = copy_results("S15-armed-record-removed-from-log")
    guard_rows = read_jsonl(target / "netguard.jsonl")
    drop = next(
        i
        for i, r in enumerate(guard_rows)
        if r.get("event") == "armed" and r.get("argv", [None, None])[1:2] == [CLI]
    )
    write_jsonl(target / "netguard.jsonl", guard_rows[:drop] + guard_rows[drop + 1 :])
    record(
        target.name,
        "delete one CLI process's armed record from the guard log (the CLI row "
        "still reports it)",
        "INCOMPLETE",
        target,
    )

    target = copy_results("S16-crashed-cli-row-stored-accepted")
    rows = read_jsonl(target / "cli_results.jsonl")
    crash_case = pick("I-OK-01")
    for row in rows:
        if row["case"] == crash_case and row["format"] == "json":
            row["exit_code"] = 1
            row["stderr"] += (
                "Traceback (most recent call last):\nRuntimeError: self-test sabotage\n"
            )
    write_jsonl(target / "cli_results.jsonl", rows)
    record(
        target.name,
        "set exit code 1 and a traceback in one CLI row but keep its stored "
        f"cli_outcome ACCEPTED ({crash_case}, json)",
        "INCOMPLETE",
        target,
    )

    sanity = map_sanity_report(vmap)
    return {
        "subset_cases": sorted(subset),
        "scenarios": outcomes,
        "map_sanity": sanity,
        "passed": all(item["passed"] for item in outcomes) and sanity["passed"],
        "_cli_rows": len(cli_rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-work", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--work", required=True)
    parser.add_argument("--version-map", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    args = parser.parse_args(argv)
    catalog = read_json(Path(args.catalog))
    vmap = read_json(VERSIONS_PATH)["maps"][args.version_map]
    report = run_selftest(
        Path(args.run_work), Path(args.results), Path(args.work), catalog, vmap
    )
    report.pop("_cli_rows")
    report["run_label"] = read_json(Path(args.results) / "run_manifest.json")[
        "run_label"
    ]
    write_json(Path(args.out), report)
    for item in report["scenarios"]:
        print(
            f"{item['scenario']:42} expected {item['expected_overall']:10} "
            f"observed {item['observed_overall']:10} "
            + ("ok" if item["passed"] else "MISMATCH")
        )
    for item in report["map_sanity"]["checks"]:
        print(
            f"{item['check']:42} expected {item['expected']:10} "
            f"found {len(item['problems'])} problem(s) "
            + ("ok" if item["passed"] else "MISMATCH")
        )
    print("self-test passed" if report["passed"] else "self-test FAILED")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
