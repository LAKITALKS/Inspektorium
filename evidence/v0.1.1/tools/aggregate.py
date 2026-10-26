"""Aggregate one results directory into case verdicts and a run summary.

The aggregator only reads recorded rows (CLI rows, measurement rows, network
logs, guard log) and recomputes everything else. A missing row, file or log is
counted as incomplete, never as a pass. Stored derived fields are not trusted:

* the CLI class of every CLI row is recomputed from its raw fields (exit code,
  standard output/error, output file hash and size) with the classifier used
  at measurement time; a different stored ``cli_outcome`` makes the case
  ``NOT_EXECUTED``;
* the outcome of every rendered row is derived from its criteria (intact if
  and only if every applicable criterion passed); a missing or extra
  criterion, or a different stored outcome, makes the row ``NOT_EXECUTED``;
  the same holds for the case-level checks K13/K14;
* armed guard records are counted per distinct CLI process id in
  ``netguard.jsonl``; fewer CLI processes with an armed record than CLI rows is
  incomplete; refusals are counted from the log.

The overall result is:

* ``PASS`` - every case HOLDS, all rows and logs are present and consistent,
  the guard was armed in every CLI process and refused nothing, and the
  browser made no blocked request;
* ``FAIL`` - at least one case FAILS, the guard refused something, or the
  browser attempted a network request;
* ``INCOMPLETE`` - otherwise (missing, inconsistent, NOT_EXECUTED or
  NOT_DEMONSTRATED).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import (
    RENDERERS,
    read_json,
    read_jsonl,
    sha256_bytes,
    write_json,
    write_jsonl,
)
from evaluate import (
    FAILS,
    HOLDS,
    INTACT,
    MANIPULATED,
    NOT_EXECUTED,
    OUTCOMES,
    REJECTED,
    VERDICTS,
    applicable_criteria,
    case_verdict,
    cli_summary,
)
from run_cli import PRESEED, classify

REQUIRED_FILES = (
    "run_manifest.json",
    "cases_manifest.json",
    "cli_results.jsonl",
    "measurements.jsonl",
    "browser_network.jsonl",
    "netguard.jsonl",
)


def _load(results: Path) -> tuple[dict[str, Any], list[str]]:
    data: dict[str, Any] = {}
    missing = []
    for name in REQUIRED_FILES:
        path = results / name
        if not path.exists():
            missing.append(name)
            data[name] = None
        elif name.endswith(".jsonl"):
            data[name] = read_jsonl(path)
        else:
            data[name] = read_json(path)
    return data, missing


CASE_CHECK_KEYS = {
    "K13_absent_tokens": "absent_tokens",
    "K14_equivalent_input_same_json": "same_report_as",
}


def recompute_cli(row: dict[str, Any]) -> tuple[str, list[str]]:
    """CLI class recomputed from the raw fields of one CLI row, and every
    disagreement with the stored derived fields."""

    try:
        preseed = PRESEED.format(case=row["case"], fmt=row["format"]).encode("ascii")
        exists = row["output_exists"] is True
        preserved = (
            exists
            and row["output_sha256"] == sha256_bytes(preseed)
            and row["output_bytes"] == len(preseed)
        )
        written = exists and not preserved and row["output_bytes"] > 0
        facts = dict(row, output_preserved=preserved, output_written=written)
        recomputed = classify(facts)
    except (KeyError, TypeError, AttributeError) as error:
        return "UNREADABLE", [f"unreadable CLI row ({type(error).__name__}: {error})"]
    problems = []
    if row.get("output_preserved") is not preserved:
        problems.append(
            f"stored output_preserved {row.get('output_preserved')} != {preserved}"
        )
    if row.get("output_written") is not written:
        problems.append(
            f"stored output_written {row.get('output_written')} != {written}"
        )
    if row.get("cli_outcome") != recomputed:
        problems.append(
            f"stored cli_outcome {row.get('cli_outcome')} != recomputed {recomputed}"
        )
    return recomputed, problems


def row_problem(case: dict[str, Any], row: dict[str, Any], cli: str) -> str | None:
    """Why a stored measurement row disagrees with its own recorded facts."""

    outcome = row.get("outcome")
    if outcome not in OUTCOMES:
        return "unknown outcome class"
    if row.get("cli") != cli:
        return f"row records CLI outcome {row.get('cli')}, CLI rows give {cli}"
    criteria = row.get("criteria")
    if outcome in (INTACT, MANIPULATED) or criteria is not None:
        if cli != "ACCEPTED":
            return f"rendered row although the CLI outcome is {cli}"
        if not isinstance(criteria, dict):
            return f"stored outcome {outcome} without criteria"
        wanted = applicable_criteria(case)
        if set(criteria) != wanted:
            return f"criteria {sorted(criteria)} != applicable {sorted(wanted)}"
        passed = [
            item.get("passed") if isinstance(item, dict) else None
            for item in criteria.values()
        ]
        if not all(isinstance(value, bool) for value in passed):
            return "criterion without a boolean result"
        derived = INTACT if all(passed) else MANIPULATED
        if derived != outcome:
            return f"stored outcome {outcome} != {derived} derived from the criteria"
    elif outcome == REJECTED and cli != "REJECTED_CLEAN":
        return f"{REJECTED} row although the CLI outcome is {cli}"
    checks = row.get("case_checks")
    if not isinstance(checks, dict) or set(checks) != set(CASE_CHECK_KEYS):
        return "case-level checks missing or unknown"
    for key, catalog_field in CASE_CHECK_KEYS.items():
        item = checks[key]
        if (item is not None) != bool(case.get(catalog_field)):
            return f"case-level check {key} present/absent against the catalog"
        if item is not None and not isinstance(item.get("passed"), bool):
            return f"case-level check {key} without a boolean result"
    derived_ok = all(item["passed"] for item in checks.values() if item is not None)
    if row.get("case_checks_ok") is not derived_ok:
        return f"stored case_checks_ok {row.get('case_checks_ok')} != {derived_ok}"
    return None


def _is_cli_process(record: dict[str, Any]) -> bool:
    argv = record.get("argv")
    return isinstance(argv, list) and len(argv) > 1 and argv[1] == "inspektorium"


def aggregate(
    results: Path,
    catalog: dict[str, Any],
    case_filter: set[str] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data, missing_files = _load(results)
    cases = [
        case
        for case in catalog["cases"]
        if case_filter is None or case["id"] in case_filter
    ]
    cli_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data["cli_results.jsonl"] or []:
        cli_rows[row["case"]].append(row)
    measurement_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data["measurements.jsonl"] or []:
        measurement_rows[row["case"]].append(row)

    # CLI class per case, recomputed from the raw CLI fields.
    cli_by_case: dict[str, tuple[str, list[str]]] = {}
    for case in catalog["cases"]:
        recomputed: list[dict[str, Any]] = []
        problems: list[str] = []
        for row in cli_rows.get(case["id"], []):
            outcome, row_problems = recompute_cli(row)
            recomputed.append({"format": row.get("format"), "cli_outcome": outcome})
            problems.extend(f"{row.get('format')}: {p}" for p in row_problems)
        cli_by_case[case["id"]] = (cli_summary(recomputed), problems)

    def checked_row(case: dict[str, Any], renderer: str) -> tuple[dict[str, Any], str]:
        found = [
            r
            for r in measurement_rows.get(case["id"], [])
            if r.get("renderer") == renderer
        ]
        if len(found) != 1:
            row = {
                "renderer": renderer,
                "outcome": NOT_EXECUTED,
                "reason": "missing measurement row",
            }
            return row, f"{len(found)} measurement rows"
        row = dict(found[0])
        problem = row_problem(case, row, cli_by_case[case["id"]][0])
        if problem:
            row["outcome"] = NOT_EXECUTED
            row["reason"] = f"inconsistent row: {problem}"
            return row, problem
        return row, ""

    label_case = next(
        (c for c in catalog["cases"] if c.get("role") == "label_map_validation"),
        None,
    )
    label_map_valid = {}
    for renderer in RENDERERS:
        valid = False
        if label_case is not None and not cli_by_case[label_case["id"]][1]:
            row, problem = checked_row(label_case, renderer)
            valid = not problem and row["outcome"] == INTACT
        label_map_valid[renderer] = valid

    verdict_rows = []
    incomplete_reasons: list[str] = [f"missing file {name}" for name in missing_files]
    for case in cases:
        rows = []
        for renderer in RENDERERS:
            row, problem = checked_row(case, renderer)
            if problem:
                incomplete_reasons.append(f"{case['id']}/{renderer}: {problem}")
            if (
                row["outcome"] in (INTACT, MANIPULATED)
                and not label_map_valid[renderer]
            ):
                row["outcome"] = NOT_EXECUTED
                row["reason"] = "label map not validated for this renderer"
            rows.append(row)
        cli, cli_problems = cli_by_case[case["id"]]
        if cli == "MISSING":
            incomplete_reasons.append(f"{case['id']}: CLI rows missing")
        extra_ok = all(row.get("case_checks_ok", True) for row in rows)
        if cli_problems:
            incomplete_reasons.extend(f"{case['id']}/{p}" for p in cli_problems)
            verdict, reason = (
                NOT_EXECUTED,
                "inconsistent CLI row: " + "; ".join(cli_problems),
            )
        else:
            verdict, reason = case_verdict(case, cli, rows, extra_ok)
        verdict_rows.append(
            {
                "case": case["id"],
                "family": case["family"],
                "kind": case["kind"],
                "expected_outcome": case["expected_outcome"],
                "cli": cli,
                "outcomes": {row["renderer"]: row["outcome"] for row in rows},
                "verdict": verdict,
                "reason": reason,
                "ambiguity_used": next(
                    (r.get("ambiguity_used") for r in rows if r.get("ambiguity_used")),
                    None,
                ),
            }
        )

    # Network / guard measurement, computed from the logs only.
    case_ids = {case["id"] for case in cases}
    cli_all = data["cli_results.jsonl"] or []
    cli_selected = [row for row in cli_all if row["case"] in case_ids]
    guard_log = data["netguard.jsonl"]
    network_log = data["browser_network.jsonl"]
    manifest = data["run_manifest.json"] or {}
    harness_pid = manifest.get("harness", {}).get("pid")
    cli_armed_pids = (
        None
        if guard_log is None
        else len(
            {
                r.get("pid")
                for r in guard_log
                if r.get("event") == "armed"
                and _is_cli_process(r)
                and r.get("pid") != harness_pid
            }
        )
    )
    network = {
        "cli_invocations": len(cli_selected),
        "cli_rows_in_run": len(cli_all),
        "cli_processes_with_armed_record_in_log": cli_armed_pids,
        "cli_guard_armed_records": sum(
            r.get("guard_armed_records", 0) for r in cli_selected
        ),
        "cli_invocations_without_armed_guard": sum(
            not r.get("guard_armed_records", 0) >= 1 for r in cli_selected
        ),
        "cli_rows_reporting_refusals": sum(
            bool(r.get("guard_refused_records")) for r in cli_all
        ),
        "guard_log_records": None if guard_log is None else len(guard_log),
        "guard_refused_total": None
        if guard_log is None
        else sum(r.get("event") == "refused" for r in guard_log),
        "guard_refused_by_cli_processes": None
        if guard_log is None
        else sum(r.get("event") == "refused" and _is_cli_process(r) for r in guard_log),
        "harness_guard_armed": None
        if guard_log is None
        else any(
            r.get("event") == "armed" and r.get("pid") == harness_pid for r in guard_log
        ),
        "browser_requests_total": None if network_log is None else len(network_log),
        "browser_requests_blocked": None
        if network_log is None
        else sum(not r["own_page"] for r in network_log if r["case"] in case_ids),
        "browser_network_requests_blocked": None
        if network_log is None
        else sum(
            (not r["own_page"]) and r["network"]
            for r in network_log
            if r["case"] in case_ids
        ),
    }
    fail_reasons = []
    if network["guard_refused_total"] or network["cli_rows_reporting_refusals"]:
        fail_reasons.append("network guard refused at least one connection attempt")
    if network["cli_invocations_without_armed_guard"]:
        incomplete_reasons.append("a CLI process ran without an armed guard record")
    if cli_armed_pids is not None and cli_armed_pids < len(cli_all):
        incomplete_reasons.append(
            f"{len(cli_all)} CLI rows but only {cli_armed_pids} CLI processes "
            "with an armed record in netguard.jsonl"
        )
    if network["harness_guard_armed"] is False:
        incomplete_reasons.append("harness process guard not armed")
    if network["browser_network_requests_blocked"]:
        fail_reasons.append("rendered pages attempted network requests (blocked)")
    if len(cli_selected) != 2 * len(cases):
        incomplete_reasons.append(
            f"{len(cli_selected)} CLI rows for {len(cases)} cases (expected 2 each)"
        )

    verdict_counts = Counter(row["verdict"] for row in verdict_rows)
    if verdict_counts[FAILS]:
        fail_reasons.append(f"{verdict_counts[FAILS]} case(s) FAILS")
    other = sum(n for v, n in verdict_counts.items() if v not in (HOLDS, FAILS))
    if other:
        incomplete_reasons.append(f"{other} case(s) not HOLDS/FAILS")
    if fail_reasons:
        overall = "FAIL"
    elif incomplete_reasons:
        overall = "INCOMPLETE"
    else:
        overall = "PASS"

    def table(key: str) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for row in verdict_rows:
            bucket = out.setdefault(
                row[key], {"cases": 0, **dict.fromkeys(VERDICTS, 0)}
            )
            bucket["cases"] += 1
            bucket[row["verdict"]] += 1
        return dict(sorted(out.items()))

    renderings: dict[str, dict[str, int]] = {}
    for row in verdict_rows:
        for renderer, outcome in row["outcomes"].items():
            bucket = renderings.setdefault(renderer, dict.fromkeys(OUTCOMES, 0))
            bucket[outcome] += 1
    by_class = Counter(o for row in verdict_rows for o in row["outcomes"].values())
    summary = {
        "run_label": manifest.get("run_label"),
        "binding": manifest.get("binding"),
        "scope": "results on the synthetic catalog "
        f"{catalog['catalog_id']} v{catalog['catalog_version']} only",
        "case_filter": sorted(case_filter) if case_filter else None,
        "overall": overall,
        "fail_reasons": fail_reasons,
        "incomplete_reasons": incomplete_reasons[:50],
        "incomplete_reason_count": len(incomplete_reasons),
        "cases": {
            "total": len(verdict_rows),
            **{v: verdict_counts[v] for v in VERDICTS},
        },
        "renderings": {
            "note": "renderings of one case are not independent observations",
            "total": sum(by_class.values()),
            **{o: by_class[o] for o in OUTCOMES},
            "by_renderer": renderings,
        },
        "by_family": table("family"),
        "by_kind": table("kind"),
        "label_map_valid": label_map_valid,
        "network": network,
    }
    return summary, verdict_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--results", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--cases", nargs="*", help="optional case filter")
    parser.add_argument("--write", action="store_true", help="write summary files")
    args = parser.parse_args(argv)
    results = Path(args.results)
    catalog = read_json(Path(args.catalog))
    summary, verdicts = aggregate(
        results, catalog, set(args.cases) if args.cases else None
    )
    if args.write:
        write_json(results / "summary.json", summary)
        write_jsonl(results / "case_verdicts.jsonl", verdicts)
    print(
        json.dumps(
            {k: summary[k] for k in ("overall", "cases", "fail_reasons")}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
