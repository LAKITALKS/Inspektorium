"""Post-run check of the real retest outputs (not part of the frozen scripts; offline, read-only on bundles).

Checks every live bundle and every released revision of the retest: bundle integrity (inspect_bundle),
Markdown and HTML report present and showing the independent states, the local decision (decision.json
status, release intent, failing controls), and that no bundle with an open mandatory review or an open
material model/host conflict was released. Writes evidence/postrun_render_release_check.json.
Usage from the repository root:
  .venv/bin/python analysis/c25_p9_20261011/live_retest/postrun/check_render_release.py
"""
import hashlib
import json
from pathlib import Path

from agent_arena.phase10_bundle import inspect_bundle

RETEST = Path("analysis/c25_p9_20261011/live_retest")
STATE_ROWS = ("model judgment (composite)", "host evidence derivation (composite)", "model/host conflicts",
              "review route", "local release", "mandatory review")
TEST_REVIEWER = "TEST ONLY - not a scientific release"


def check(path):
    record = json.loads((path / "record.json").read_text())
    decision = json.loads((path / "decision.json").read_text())
    markdown = (path / "report.md").read_text()
    html = (path / "report.html").read_text()
    phase9 = record["run_record"]["metadata"].get("phase9") or {}
    intent = decision.get("release_intent") or {}
    return {
        "path": str(path.relative_to(RETEST)), "task": record["run_record"]["task"]["id"],
        "bundle_valid": inspect_bundle(path).valid, "status": decision["status"],
        "report_hashes_match": all(hashlib.sha256((path / name).read_bytes()).hexdigest() == digest
                                   for name, digest in decision["report_hashes"].items()),
        "markdown_state_rows": {row: row in markdown for row in STATE_ROWS},
        "html_state_rows": {row: row.replace("/", "&#47;") in html or row in html for row in STATE_ROWS},
        "markdown_status_line": next((line for line in markdown.splitlines() if "local artifact status" in line), None),
        "release_intent": intent or None,
        "test_marked": (intent.get("reviewer") == TEST_REVIEWER and TEST_REVIEWER in markdown
                        and TEST_REVIEWER in html) if intent else None,
        "failing_controls": [c["control_id"] for c in decision["controls"] if c["outcome"] == "fail"],
        "p9_route": phase9.get("route"), "p9_mandatory": phase9.get("mandatory"),
        "open_material_model_host_conflict": any(t.get("code") == "model_host_conflict" for t in phase9.get("triggers", [])),
    }


def main():
    bundles = [check(p.parent) for p in sorted(RETEST.glob("bundles/*/*/record.json"))]
    released = [check(p.parent) for p in sorted(RETEST.glob("released/*/*/*/record.json"))]
    violations = [r["path"] for r in released if r["status"] == "RELEASED"
                  and (r["p9_mandatory"] or r["open_material_model_host_conflict"])]
    out = {"bundles": bundles, "released": released,
           "released_with_open_mandatory_review_or_material_conflict": violations,
           "all_valid": all(r["bundle_valid"] and r["report_hashes_match"] for r in bundles + released),
           "all_reports_show_states": all(all(r["markdown_state_rows"].values()) and all(r["html_state_rows"].values())
                                          for r in bundles + released),
           "all_releases_test_marked": all(r["test_marked"] for r in released)}
    target = RETEST / "evidence" / "postrun_render_release_check.json"
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("bundles", "released")}, indent=1))
    for r in bundles + released:
        print(r["path"][:60], r["status"], r["bundle_valid"], r["report_hashes_match"], r["test_marked"],
              r["failing_controls"], r["p9_route"])


if __name__ == "__main__":
    main()
