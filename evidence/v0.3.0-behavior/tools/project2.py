"""Decision projection of a golden recording, version 2.

project2.py RECORDING > projection.json

Version 2 adds two rules to version 1 (project.py), both applied to report
text before the line multiset is formed:
- MODULE_COUNT: the bound runtime's module count is part of the module-hash
  manifest and is masked in its exact table row.
- Position blocks: rows "positions / N / ..." follow the random order of
  position IDs. Blocks are sorted by their full content and renumbered, so
  each attribute stays paired with its own position.

Keeps every decision-relevant value (exit codes, statuses, control outcomes,
findings, review and release state, byte hashes of reference-checker output)
and masks only values that vary between two runs of the same release
(run/revision/position IDs, timestamps, run-derived fingerprints and paths)
or that name the package and its version (package name, version, module-hash
manifest). Masking rules are listed in MASKS and SKIP_KEYS.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MASKS = [
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"), "<uuid>"),
    (re.compile(r"\b[0-9a-f]{64}\b"), "<sha256>"),
    (re.compile(r"\b[0-9a-f]{24}\b"), "<hex24>"),
    (re.compile(r"\b[0-9a-f]{12,20}\b"), "<hex>"),
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}(?::|&#58;)\d{2}(?::|&#58;)\d{2}(?:\.\d+)?(?:\+00(?::|&#58;)00|Z)?"), "<timestamp>"),
    (re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?(?: UTC)?"), "<timestamp>"),
    (re.compile(r"Agent Arena|agent-arena|agent_arena", re.I), "<package>"),
    (re.compile(r"\binspektorium(?=[ \]:,.)\n]|$)"), "<package>"),
    (re.compile(r"\b(?:1\.0\.[12]|0\.2\.0|0\.3\.0)\b"), "<version>"),
]
# Keys whose values differ between two runs of the same release or that are
# package identities: run/revision identity, creation time, code manifest.
SKIP_KEYS = {"created_at", "timestamp", "run_id", "revision_id", "parent", "latency_ms",
             "module_hashes", "code_fingerprint", "verified_source_commit", "package_version",
             "analysis_fingerprint", "review_fingerprint", "fingerprint", "registry_fingerprint_note"}


UNORDERED_KEYS = {"conflicts", "triggers", "position_ids", "positions"}

MODULE_COUNT = [
    (re.compile(r"(\| code / module count \| )\d+( \|)"), r"\1<module-count>\2"),
    (re.compile(r"(<td>code / module count</td><td>)\d+(</td>)"), r"\1<module-count>\2"),
]
MD_POSITION = re.compile(r"^\| positions / (\d+) / (.*)$", re.M)
HTML_POSITION = re.compile(r"<tr><td>positions / (\d+) / (.*?)</td></tr>")


def canonical_positions(text: str, pattern: re.Pattern, template: str) -> str:
    blocks: dict[str, list[str]] = {}
    for match in pattern.finditer(text):
        blocks.setdefault(match.group(1), []).append(match.group(2))
    if len(blocks) < 2:
        return text
    order = sorted(blocks, key=lambda index: sorted(blocks[index]))
    renumber = {old: str(new) for new, old in enumerate(order, 1)}
    return pattern.sub(lambda m: template.format(renumber[m.group(1)], m.group(2)), text)


def normalize_report(text: str) -> str:
    for pattern, replacement in MODULE_COUNT:
        text = pattern.sub(replacement, text)
    text = canonical_positions(text, MD_POSITION, "| positions / {} / {}")
    return canonical_positions(text, HTML_POSITION, "<tr><td>positions / {} / {}</td></tr>")


def mask(value):
    if isinstance(value, str):
        for pattern, token in MASKS:
            value = pattern.sub(token, value)
        return value
    if isinstance(value, list):
        return [mask(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k in SKIP_KEYS:
                out[mask(k)] = "<skipped>"
            elif k in UNORDERED_KEYS and isinstance(v, list):
                # Their order follows random position IDs and varies between two runs.
                out[k] = sorted((mask(item) for item in v), key=lambda item: json.dumps(item, sort_keys=True))
            else:
                out[mask(k)] = mask(v)
        return out
    return value


def project_step(step: dict) -> dict:
    if "files" in step:
        files = {}
        for name, entry in sorted(step["files"].items()):
            if "json" in entry:
                files[name] = mask(entry["json"])
            else:
                # Mask first: position blocks contain random IDs and are sorted by masked content.
                text = normalize_report(mask(entry.get("text", "")))
                pieces = text.replace("><", ">\n<").splitlines() if name.endswith(".html") else text.splitlines()
                # Report sections list conflicts in random-ID order; compare line multisets.
                files[name] = sorted(pieces)
        return {"label": step["label"], "files": files}
    row = {"label": step["label"], "exit_code": step["exit_code"]}
    data = step.get("json")
    if isinstance(data, dict):
        row["json"] = mask({k: v for k, v in data.items() if k != "path"})
        row["has_path"] = bool(data.get("path"))
    else:
        lines = [line for line in step["stderr"].splitlines() if line.strip()]
        row["stderr_last"] = mask(lines[-1]) if lines else ""
    if step["label"].startswith("inspect "):
        row["stdout_sha256"] = step["stdout_sha256"]
        if "output_sha256" in step:
            row["output_sha256"] = step["output_sha256"]
    for key in ("source_bundle_unchanged",):
        if key in step:
            row[key] = step[key]
    return row


def main() -> int:
    steps = json.loads((Path(sys.argv[1]) / "steps.json").read_text())
    print(json.dumps([project_step(s) for s in steps], indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
