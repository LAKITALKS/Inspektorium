#!/usr/bin/env python3
"""Deterministic Phase 6.3 example generator (offline, no model calls).

Reads the SYNTHETIC input fixtures in ``fixtures/`` and renders the worked example
artifacts (``example_full_report.json`` / ``.md`` and ``example_executive_summary.md``)
from a single showcase fixture, using only the frozen ``agent_arena.forensic_report``
engine. It also re-validates every fixture end-to-end.

Determinism: no wall-clock timestamps are injected (``generated_at`` comes from each
fixture), so repeated runs are byte-for-byte identical.

Usage::

    PYTHONPATH=src .venv/bin/python analysis/phase6_3_report_prototype/build_examples.py \
        [--out-dir analysis/phase6_3_report_prototype]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_arena.forensic_report import (
    build_forensic_report,
    canonical_report_bytes,
    render_executive_summary,
    render_forensic_report_markdown,
    validate_forensic_report,
)

HERE = Path(__file__).resolve().parent
FIXTURES_DIR = HERE / "fixtures"
SHOWCASE = "04_mechanism_vs_evidence"   # biologically-scoped label — the hardest to get right


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", default=str(HERE), help="directory to write example artifacts into")
    ap.add_argument("--fixtures-dir", default=str(FIXTURES_DIR), help="directory of input fixtures")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    fixtures_dir = Path(args.fixtures_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Re-validate every fixture (build + output-contract check).
    n_ok = 0
    for fx in sorted(fixtures_dir.glob("*.json")):
        raw = json.loads(fx.read_text())
        report = build_forensic_report(raw)
        ok, errs = validate_forensic_report(report)
        if not ok:
            print(f"[FAIL] {fx.name}: {errs}")
            return 2
        n_ok += 1
    print(f"validated {n_ok} fixtures")

    # Render the showcase example from a single validated report object.
    raw = json.loads((fixtures_dir / f"{SHOWCASE}.json").read_text())
    report = build_forensic_report(raw)
    (out_dir / "example_full_report.json").write_bytes(canonical_report_bytes(report))
    (out_dir / "example_full_report.md").write_text(render_forensic_report_markdown(report))
    (out_dir / "example_executive_summary.md").write_text(render_executive_summary(report))
    print(f"wrote example artifacts for {SHOWCASE} "
          f"(status={report['analysis_status']} label={report['verdict']['predicted_label']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
