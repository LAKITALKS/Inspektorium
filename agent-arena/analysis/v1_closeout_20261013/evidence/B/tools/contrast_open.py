"""Adds 'open_sentence_contrast' to summary.json: the REVIEW_REQUIRED (B2a) and READY (B1) candidate status
lines at 558e920, fd1ad7c and 5560e95, read from the bundles already produced by drive.py (no CLI call)."""
import html
import json
from pathlib import Path

SCRATCH = Path(__file__).resolve().parents[1]
summary = json.loads((SCRATCH / "summary.json").read_text())


def lines(path):
    if not path:
        return None
    raw = (Path(path.replace("<scratch>", str(SCRATCH))) / "report.md").read_bytes().decode("utf-8")
    return [html.unescape(l) for l in raw.splitlines()
            if l.startswith(("Automatic processing has ended", "| open cause |", "| automatic processing |",
                             "| local release |"))]


out = {}
for case in ("B1_bounded_optional_conflict", "B2a_material_premise"):
    out[case] = {"5560e95": lines(summary["cases"][case]["commands"]["run"].get("path"))}
    for old in ("558e920", "fd1ad7c"):
        out[case][old] = lines(summary["before_after"][old][case]["commands"]["run"].get("path"))
summary["open_sentence_contrast_candidate_report_md"] = out
(SCRATCH / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
print(json.dumps(out, indent=1, ensure_ascii=False))
