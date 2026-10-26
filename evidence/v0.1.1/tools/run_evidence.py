"""Offline evidence run for one installed product version.

Run with the harness venv's Python and ``EVIDENCE_NETGUARD_LOG`` pointing to
``<work>/<label>/netguard.jsonl`` (the guard records its own start there).
Steps: preflight (guards installed and armed, product import check), build
cases from the catalog, run the real CLI per case and format, render every
accepted Markdown report with each renderer, probe each page in Chromium,
evaluate criteria, write results, aggregate.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any

from aggregate import aggregate
from browser_check import probe_pages
from build_cases import build_all
from common import (
    CATALOG_PATH,
    RENDERERS,
    REPO_ROOT,
    VERSIONS_PATH,
    Sanitizer,
    read_json,
    read_text_exact,
    scrubbed_env,
    sha256_file,
    write_json,
    write_jsonl,
)
from evaluate import (
    INTACT,
    MANIPULATED,
    NOT_EXECUTED,
    REJECTED,
    check_preconditions,
    cli_summary,
    evaluate_rendering,
    probe_ambiguity,
)
from renderers import render_page, renderer_versions
from run_cli import run_all

GUARD_SOURCE = Path(__file__).resolve().parent / "netguard.py"
IMPORT_CHECK = (
    "import json, importlib.metadata as m, inspektorium, sys;"
    "print(json.dumps({'file': inspektorium.__file__,"
    "'version_attr': getattr(inspektorium, '__version__', None),"
    "'dist_version': m.version('inspektorium'),"
    "'python': sys.version.split()[0],"
    "'unidata_version': __import__('unicodedata').unidata_version,"
    "'guard_armed': __import__('evidence_netguard').is_armed()}))"
)


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def installed_guard_sha(venv: Path) -> str | None:
    matches = list(venv.glob("lib/python*/site-packages/evidence_netguard.py"))
    pth = list(venv.glob("lib/python*/site-packages/zz_evidence_netguard.pth"))
    if len(matches) != 1 or len(pth) != 1:
        return None
    return sha256_file(matches[0])


def preflight(
    product_venv: Path, guard_log: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    import evidence_netguard  # installed by setup_env.py into the harness venv

    source_sha = sha256_file(GUARD_SOURCE)
    harness_sha = sha256_file(Path(evidence_netguard.__file__))
    product_sha = installed_guard_sha(product_venv)
    if not evidence_netguard.is_armed():
        raise SystemExit("harness network guard is not armed")
    configured = os.environ.get("EVIDENCE_NETGUARD_LOG")
    if configured is None or Path(configured).resolve() != guard_log.resolve():
        raise SystemExit("EVIDENCE_NETGUARD_LOG must point to the run's netguard.jsonl")
    if harness_sha != source_sha or product_sha != source_sha:
        raise SystemExit("installed guard differs from tools/netguard.py")
    result = subprocess.run(
        [str(product_venv / "bin" / "python"), "-c", IMPORT_CHECK],
        capture_output=True,
        text=True,
        check=True,
        env=scrubbed_env({"EVIDENCE_NETGUARD_LOG": str(guard_log)}),
        cwd=guard_log.parent,
    )
    product = json.loads(result.stdout)
    site = str(product_venv.resolve())
    product["imported_from_venv"] = str(Path(product["file"]).resolve()).startswith(
        site
    )
    product["imported_from_source_tree"] = str(
        Path(product["file"]).resolve()
    ).startswith(str(REPO_ROOT))
    if not product["imported_from_venv"] or product["imported_from_source_tree"]:
        raise SystemExit(f"product not imported from its venv: {product['file']}")
    if not product["guard_armed"]:
        raise SystemExit("product venv guard is not armed")
    guards = {
        "guard_source_sha256": source_sha,
        "harness_guard_sha256": harness_sha,
        "product_guard_sha256": product_sha,
    }
    return product, guards


def sentinel_job(case: dict[str, Any]) -> tuple[list[str], list[dict[str, str]]]:
    tokens: list[str] = []
    fields = []
    for ref, (begin, end) in case.get("sentinels", {}).items():
        tokens.extend([begin, end])
        fields.append({"field": ref, "begin": begin, "end": end})
    tokens.extend(case.get("absent_tokens", []))
    return tokens, fields


def measure(
    catalog: dict[str, Any],
    cli_rows: list[dict[str, Any]],
    out_dir: Path,
    html_dir: Path,
    vmap: dict[str, Any],
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], dict[str, str], list[dict[str, Any]]
]:
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in cli_rows:
        by_case.setdefault(row["case"], []).append(row)
    jobs = []
    pages: dict[tuple[str, str], dict[str, Any]] = {}
    for case in catalog["cases"]:
        cli = cli_summary(by_case.get(case["id"], []))
        if cli != "ACCEPTED":
            continue
        markdown_text = read_text_exact(out_dir / case["id"] / "report.md")
        tokens, fields = sentinel_job(case)
        for renderer in RENDERERS:
            path = html_dir / renderer / f"{case['id']}.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            page = render_page(renderer, markdown_text, f"{case['id']} {renderer}")
            path.write_text(page, encoding="utf-8")
            pages[(case["id"], renderer)] = {"html_sha256": sha256_file(path)}
            jobs.append(
                {
                    "case": case["id"],
                    "renderer": renderer,
                    "path": str(path),
                    "tokens": tokens,
                    "fields": fields,
                }
            )
    facts_rows, network_rows, browser = probe_pages(jobs)
    facts_index = {(row["case"], row["renderer"]): row for row in facts_rows}
    measurements = evaluate_all(
        catalog, by_case, out_dir, facts_index, network_rows, vmap, pages
    )
    return measurements, network_rows, browser, facts_rows


def evaluate_all(
    catalog: dict[str, Any],
    by_case: dict[str, list[dict[str, Any]]],
    out_dir: Path,
    facts_index: dict[tuple[str, str], dict[str, Any]],
    network_rows: list[dict[str, Any]],
    vmap: dict[str, Any],
    pages: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for case in catalog["cases"]:
        cli = cli_summary(by_case.get(case["id"], []))
        report = None
        json_text = None
        markdown_text = None
        if cli == "ACCEPTED":
            json_text = read_text_exact(out_dir / case["id"] / "report.json")
            markdown_text = read_text_exact(out_dir / case["id"] / "report.md")
            report = json.loads(json_text)
        preconditions = check_preconditions(case, report) if report else []
        absent = case.get("absent_tokens", [])
        absent_hits = [
            token
            for token in absent
            if (json_text and token in json_text)
            or (markdown_text and token in markdown_text)
        ]
        same_as = case.get("same_report_as")
        same_ok = True
        if same_as and cli == "ACCEPTED":
            other = out_dir / same_as / "report.json"
            same_ok = (
                other.exists()
                and other.read_bytes()
                == (out_dir / case["id"] / "report.json").read_bytes()
            )
        ambiguity = probe_ambiguity(case, json_text)
        for renderer in RENDERERS:
            row: dict[str, Any] = {
                "case": case["id"],
                "renderer": renderer,
                "cli": cli,
                "ambiguity_used": ambiguity,
                "case_checks_ok": not absent_hits and same_ok,
                "case_checks": {
                    "K13_absent_tokens": {
                        "passed": not absent_hits,
                        "detail": str(absent_hits),
                    }
                    if absent
                    else None,
                    "K14_equivalent_input_same_json": {
                        "passed": same_ok,
                        "detail": same_as,
                    }
                    if same_as
                    else None,
                },
            }
            if cli == "REJECTED_CLEAN":
                row.update(
                    outcome=REJECTED, reason="CLI rejected input for both formats"
                )
            elif cli != "ACCEPTED":
                row.update(outcome=NOT_EXECUTED, reason=f"CLI outcome {cli}")
            elif preconditions:
                row.update(
                    outcome=NOT_EXECUTED,
                    reason="precondition not met: " + "; ".join(preconditions),
                )
            else:
                facts = facts_index.get((case["id"], renderer))
                row["html_sha256"] = pages.get((case["id"], renderer), {}).get(
                    "html_sha256"
                )
                if facts is None or facts["facts"] is None:
                    error = facts["error"] if facts else "no browser facts"
                    row.update(outcome=NOT_EXECUTED, reason=f"browser: {error}")
                else:
                    page_network = [
                        r
                        for r in network_rows
                        if r["case"] == case["id"] and r["renderer"] == renderer
                    ]
                    assert report is not None
                    results = evaluate_rendering(
                        case, report, facts["facts"], vmap, page_network
                    )
                    row["criteria"] = {
                        key: {"passed": value.passed, "detail": value.detail}
                        for key, value in results.items()
                    }
                    failed = [key for key, value in results.items() if not value.passed]
                    row["outcome"] = MANIPULATED if failed else INTACT
                    row["reason"] = (
                        "failed " + ", ".join(failed) if failed else "all criteria held"
                    )
            rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--label", required=True, help="run label, e.g. baseline-4bd0ba9"
    )
    parser.add_argument("--product-venv", required=True)
    parser.add_argument("--build-provenance", required=True)
    parser.add_argument(
        "--version-map", required=True, help="key in config/versions.json"
    )
    parser.add_argument("--work", required=True, help="scratch directory for this run")
    parser.add_argument("--results", required=True, help="results directory to write")
    parser.add_argument("--binding", choices=("yes", "no"), required=True)
    parser.add_argument("--note", default="")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    parser.add_argument("--versions", default=str(VERSIONS_PATH))
    args = parser.parse_args(argv)

    started = now()
    work = Path(args.work).resolve()
    results = Path(args.results).resolve()
    product_venv = Path(args.product_venv).resolve()
    guard_log = work / "netguard.jsonl"
    product, guards = preflight(product_venv, guard_log)

    catalog_path = Path(args.catalog).resolve()
    catalog = read_json(catalog_path)
    versions = read_json(Path(args.versions))
    vmap = versions["maps"][args.version_map]
    if (
        vmap.get("display", {}).get("mode") == "tokenize"
        and product["unidata_version"] != unicodedata.unidata_version
    ):
        # The expected display is derived with this process's Unicode
        # database; it must be the one the product marks with.
        raise SystemExit(
            f"Unicode database differs: product {product['unidata_version']}, "
            f"harness {unicodedata.unidata_version}"
        )
    for case in catalog["cases"]:
        if "expected_outcome" not in case:
            raise SystemExit(f"catalog case {case['id']} lacks expected_outcome")

    cases_dir = work / "cases"
    out_dir = work / "out"
    html_dir = work / "html"
    for directory in (cases_dir, out_dir, html_dir):
        if directory.exists():
            shutil.rmtree(directory)
    manifest_cases = build_all(catalog_path, cases_dir)
    cli_rows = run_all(product_venv, cases_dir, out_dir, guard_log)
    measurements, network_rows, browser, facts_rows = measure(
        catalog, cli_rows, out_dir, html_dir, vmap
    )
    finished = now()

    sanitizer = Sanitizer(
        {
            str(work): "<WORK>",
            str(product_venv): "<PRODUCT_VENV>",
            str(Path(sys.prefix)): "<TOOLS_VENV>",
            str(REPO_ROOT): "<REPO>",
            str(Path(args.build_provenance).resolve().parent): "<BUILD>",
        }
    )
    provenance = read_json(Path(args.build_provenance))
    outputs = []
    for row in cli_rows:
        name = "report.json" if row["format"] == "json" else "report.md"
        path = out_dir / row["case"] / name
        text = read_text_exact(path) if row["output_written"] else None
        outputs.append(
            {
                "case": row["case"],
                "format": row["format"],
                "sha256": row["output_sha256"],
                "text": text,
            }
        )
    run_manifest = {
        "run_label": args.label,
        "binding": args.binding == "yes",
        "note": args.note,
        "started": started,
        "finished": finished,
        "catalog": {
            "id": catalog["catalog_id"],
            "version": catalog["catalog_version"],
            "sha256": sha256_file(catalog_path),
            "cases": len(catalog["cases"]),
        },
        "version_map": {
            "key": args.version_map,
            "versions_json_sha256": sha256_file(Path(args.versions)),
        },
        "product": {
            **{k: v for k, v in provenance.items() if k != "created"},
            "import_check": {
                "file": product["file"],
                "version_attr": product["version_attr"],
                "dist_version": product["dist_version"],
                "python": product["python"],
                "unidata_version": product["unidata_version"],
                "imported_from_venv": product["imported_from_venv"],
                "imported_from_source_tree": product["imported_from_source_tree"],
            },
            "venv_freeze": read_json(product_venv / "evidence_venv.json")["freeze"],
        },
        "harness": {
            "pid": os.getpid(),
            "python": sys.version.split()[0],
            "unidata_version": unicodedata.unidata_version,
            "platform": platform.platform(),
            "tools_freeze": read_json(Path(sys.prefix) / "evidence_venv.json")[
                "freeze"
            ],
            "renderers": renderer_versions(),
            "browser": browser,
            "tool_sha256": {
                path.name: sha256_file(path)
                for path in sorted(Path(__file__).resolve().parent.iterdir())
                if path.suffix in (".py", ".js")
            },
        },
        "network_guard": {
            **guards,
            "scope": "Python socket-level hook in the harness process and in every "
            "CLI subprocess; browser requests blocked by Playwright routing and a "
            "host-resolver rule. Native code outside these paths is not covered.",
        },
        "command": sanitizer.obj(["python", *sys.argv]),
        "case_inputs": manifest_cases["cases"],
    }
    results.mkdir(parents=True, exist_ok=True)
    write_json(results / "run_manifest.json", sanitizer.obj(run_manifest))
    write_json(results / "cases_manifest.json", manifest_cases)
    write_jsonl(results / "cli_results.jsonl", sanitizer.obj(cli_rows))
    write_jsonl(results / "outputs.jsonl", outputs)
    write_jsonl(results / "measurements.jsonl", sanitizer.obj(measurements))
    write_jsonl(results / "browser_network.jsonl", sanitizer.obj(network_rows))
    write_jsonl(work / "dom_facts.jsonl", facts_rows)
    guard_rows = [
        json.loads(line)
        for line in guard_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    write_jsonl(results / "netguard.jsonl", sanitizer.obj(guard_rows))
    summary, verdicts = aggregate(results, catalog)
    write_json(results / "summary.json", summary)
    write_jsonl(results / "case_verdicts.jsonl", verdicts)
    print(json.dumps({k: summary[k] for k in ("overall", "cases")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
