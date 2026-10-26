"""Scan every newly reachable blob after an already scanned frozen history.

This supplements a successful full baseline..frozen scan; it never substitutes
for it. No network, repository code execution, or checkout modification occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--baseline", required=True)
    p.add_argument("--frozen", required=True)
    p.add_argument("--final", required=True)
    p.add_argument("--frozen-scan", type=Path, required=True)
    p.add_argument("--auditor", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    spec = importlib.util.spec_from_file_location("publication_auditor", a.auditor)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=a.repo)

    baseline, frozen, final = (
        git("rev-parse", x + "^{commit}").decode().strip()
        for x in (a.baseline, a.frozen, a.final)
    )
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline, frozen], cwd=a.repo, check=True
    )
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", frozen, final], cwd=a.repo, check=True
    )
    old_scan_bytes = a.frozen_scan.read_bytes()
    old_scan = json.loads(old_scan_bytes)
    if old_scan.get("status") != "PASSED_FOCUSED_SCAN" or old_scan.get("findings"):
        raise SystemExit("a successful frozen full-history scan is required")
    prior_commits = (
        git("rev-list", "--reverse", baseline + ".." + frozen).decode().splitlines()
    )
    new_commits = (
        git("rev-list", "--reverse", frozen + ".." + final).decode().splitlines()
    )

    def entries(commit):
        for row in git("ls-tree", "-rz", commit).split(b"\0"):
            if row:
                meta, path = row.split(b"\t", 1)
                mode, kind, oid = meta.decode().split()
                yield mode, kind, oid, path.decode()

    covered = {
        oid
        for c in prior_commits
        for mode, kind, oid, path in entries(c)
        if kind == "blob"
    }
    if old_scan["counts"].get("new_commits") != len(prior_commits):
        raise SystemExit("frozen scan commit count does not match actual range")
    if old_scan["counts"].get("unique_newly_examined_blobs") != len(covered):
        raise SystemExit("frozen scan blob count does not match actual range")
    scanned, new_metadata, new_paths = set(), [], set()
    for c in new_commits:
        commit_bytes = git("cat-file", "commit", c)
        identity = (
            git("show", "-s", "--format=%an%n%ae%n%cn%n%ce", c).decode().splitlines()
        )
        exact_identity = (
            identity == ["Lazaros Varvatis", "varvatislazaros@gmail.com"] * 2
        )
        if not exact_identity:
            audit.report(c, "unexpected_publication_identity")
        if audit.SECRET.search(commit_bytes) or audit.PRIVATE.search(commit_bytes):
            audit.report(c, "sensitive_commit_metadata")
        if re.search(rb"(?im)^Co-authored-by:", commit_bytes):
            audit.report(c, "coauthorship_trailer")
        new_metadata.append(
            {
                "commit": c,
                "commit_object_sha256": hashlib.sha256(commit_bytes).hexdigest(),
                "expected_author_and_committer": exact_identity,
            }
        )
        for mode, kind, oid, path in entries(c):
            label = c[:12] + ":" + path
            if kind != "blob" or mode == "120000":
                audit.report(label, "nonregular_git_entry")
                continue
            if any(
                x in PurePosixPath(path).parts
                for x in [".DS_Store", ".env", ".venv", "__pycache__", ".agent_arena"]
            ):
                audit.report(label, "excluded_filename_even_if_blob_previously_scanned")
            if oid in covered or oid in scanned:
                continue
            audit.scan(git("cat-file", "blob", oid), label)
            scanned.add(oid)
            new_paths.add(path)
    changed_paths = git("diff", "--name-only", frozen, final).decode().splitlines()
    product_changed = [
        x
        for x in changed_paths
        if x.startswith(
            (
                "src/",
                "tests/",
                "agent-arena/src/",
                "agent-arena/tests/",
                "agent-arena/scripts/",
            )
        )
        or x in {"pyproject.toml", "agent-arena/pyproject.toml"}
    ]
    result = {
        "status": "PASSED_FROZEN_HISTORY_PLUS_DELTA"
        if not audit.findings
        else "FAILED",
        "baseline": baseline,
        "frozen": frozen,
        "final": final,
        "frozen_full_scan_sha256": hashlib.sha256(old_scan_bytes).hexdigest(),
        "frozen_commits": prior_commits,
        "frozen_unique_blobs": len(covered),
        "frozen_blob_set_sha256": hashlib.sha256(
            ("\n".join(sorted(covered)) + "\n").encode()
        ).hexdigest(),
        "new_commits": new_metadata,
        "new_unique_blobs_scanned": len(scanned),
        "new_blob_ids": sorted(scanned),
        "new_blob_paths": sorted(new_paths),
        "final_changed_paths": changed_paths,
        "product_paths_changed_after_frozen": product_changed,
        "scan_counts": dict(audit.counts),
        "findings": audit.findings,
        "coverage": (
            "All blobs in all newly reachable commits, not merely final "
            "working-tree diff. Previously scanned byte-identical blob IDs "
            "reused; every new commit metadata and path checked."
        ),
    }
    a.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in {"new_blob_ids", "new_blob_paths", "final_changed_paths"}
            },
            indent=2,
        )
    )
    raise SystemExit(bool(audit.findings))


if __name__ == "__main__":
    main()
