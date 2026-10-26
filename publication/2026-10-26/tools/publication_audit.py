"""Sanitized final publication scan: trees, new Git blobs and release archives.

No network access and no repository imports/execution. Findings contain paths/types
only. Run with the bundled Python that supplies pypdf. This is a focused mechanical
check, not a claim of exhaustive secret discovery or legal clearance.
"""

from __future__ import annotations

import argparse
import collections
import io
import json
import re
import struct
import subprocess
import tarfile
import zipfile
import zlib
from pathlib import Path, PurePosixPath

from pypdf import PdfReader

SECRET = re.compile(
    rb"\bsk-(?:ant-|proj-|or-v1-)?[A-Za-z0-9_-]{20,}|"
    rb"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{25,}|"
    rb"github_pat_[A-Za-z0-9_]{25,}|"
    rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|"
    rb"\bAKIA[A-Z0-9]{16}\b|\bxox[baprs]-[A-Za-z0-9-]{20,}"
)
PRIVATE = re.compile(
    rb"/"
    rb"Users/[^/\s\"'<>]{1,100}/|/"
    rb"home/[^/\s\"'<>]{1,100}/|~(?=/Documents/)|-"
    rb"Users-[^-\s/]+|/private/tmp/claude-\d+|/var/folders/[^/\s]+/[^/\s]+/[TC]"
)
SESSION = re.compile(rb'"type"\s*:\s*"(?:session_meta|response_item|event_msg)"')
ACCOUNT_KEYS = {
    "organization_header_hashes",
    "organization_identifier_sha256",
    "account_billing_url",
    "billing_ui_available_credits_usd_at_check",
    "auto_reload_enabled",
    "account_route_matches_api_credential",
}
findings = []
counts = collections.Counter()


def report(path, kind):
    findings.append({"path": path, "type": kind})


def structure(obj, path):
    if isinstance(obj, dict):
        for key in ACCOUNT_KEYS.intersection(obj):
            report(path, "private_account_field:" + key)
        if obj.get("status") == "ACTIVE" and {
            "authorization_id",
            "canonical_directory",
            "allowed_profiles",
        }.issubset(obj):
            report(path, "active_authorization_object")
        for v in obj.values():
            structure(v, path)
    elif isinstance(obj, list):
        for v in obj:
            structure(v, path)


def safe(name):
    return (
        not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts
    )


def scan(data, path):
    counts["objects"] += 1
    if SECRET.search(data):
        report(path, "credential_shaped_value")
    if PRIVATE.search(data):
        report(path, "private_local_path")
    if SESSION.search(data):
        report(path, "agent_session_signature")
    name = path.split("!")[-1]
    if any(
        x in PurePosixPath(name).parts
        for x in [".DS_Store", ".env", ".venv", "__pycache__", ".agent_arena"]
    ):
        report(path, "excluded_local_state_filename")
    if name.endswith((".tar.gz", ".tgz")):
        counts["tar_archives"] += 1
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            for m in tf:
                if not safe(m.name) or not (m.isfile() or m.isdir()):
                    report(path + "!" + m.name, "unsafe_archive_member")
                    continue
                if m.uname or m.gname:
                    report(path + "!" + m.name, "tar_owner_metadata")
                if m.isfile():
                    scan(tf.extractfile(m).read(), path + "!" + m.name)
        return
    if name.endswith((".zip", ".whl")):
        counts["zip_archives"] += 1
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for m in z.infolist():
                if not safe(m.filename):
                    report(path + "!" + m.filename, "unsafe_archive_member")
                elif not m.is_dir():
                    scan(z.read(m), path + "!" + m.filename)
        return
    if name.endswith(".pdf"):
        counts["pdfs"] += 1
        q = PdfReader(io.BytesIO(data))
        txt = "\n".join(p.extract_text() or "" for p in q.pages).encode()
        if SECRET.search(txt):
            report(path, "pdf_body_credential")
        if PRIVATE.search(txt):
            report(path, "pdf_body_private_local_path")
        meta = json.dumps(dict(q.metadata or {}), default=str).encode()
        if PRIVATE.search(meta):
            report(path, "pdf_metadata_private_local_path")
        if "ChatGPT" in str((q.metadata or {}).get("/Author", "")):
            report(path, "ai_named_as_document_author")
        return
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        counts["pngs"] += 1
        pos = 8
        while pos + 12 <= len(data):
            size = struct.unpack(">I", data[pos : pos + 4])[0]
            typ, body = data[pos + 4 : pos + 8], data[pos + 8 : pos + 8 + size]
            if typ == b"zTXt":
                body = zlib.decompress(body.split(b"\0", 1)[1][1:])
            if typ in {b"tEXt", b"zTXt", b"iTXt"}:
                if PRIVATE.search(body) or SECRET.search(body):
                    report(path, "png_text_metadata")
            pos += size + 12
        return
    try:
        txt = data.decode("utf-8")
    except UnicodeDecodeError:
        return
    try:
        obj = json.loads(txt)
    except (ValueError, RecursionError):
        return
    structure(obj, path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("paths", type=Path, nargs="*")
    p.add_argument("--repo", type=Path)
    p.add_argument("--range", dest="revisions")
    p.add_argument("--report", type=Path)
    a = p.parse_args()
    for root in a.paths:
        files = (
            [root]
            if root.is_file()
            else sorted(
                x
                for x in root.rglob("*")
                if x.is_file() and ".git" not in x.relative_to(root).parts
            )
        )
        for fp in files:
            label = fp.name if root.is_file() else str(fp.relative_to(root))
            if fp.is_symlink():
                report(label, "symlink_requires_review")
            else:
                scan(fp.read_bytes(), label)
    if a.revisions:
        if not a.repo:
            raise SystemExit("--range requires --repo")
        commits = (
            subprocess.check_output(["git", "rev-list", a.revisions], cwd=a.repo)
            .decode()
            .splitlines()
        )
        seen = set()
        counts["new_commits"] = len(commits)
        for commit in commits:
            entries = subprocess.check_output(
                ["git", "ls-tree", "-rz", commit], cwd=a.repo
            ).split(b"\0")
            for e in entries:
                if not e:
                    continue
                meta, path = e.split(b"\t", 1)
                mode, kind, oid = meta.decode().split()
                label = commit[:12] + ":" + path.decode()
                if kind != "blob" or mode == "120000":
                    report(label, "nonregular_git_entry")
                    continue
                if oid in seen:
                    continue
                seen.add(oid)
                scan(
                    subprocess.check_output(
                        ["git", "cat-file", "blob", oid], cwd=a.repo
                    ),
                    label,
                )
            msg = subprocess.check_output(
                ["git", "cat-file", "commit", commit], cwd=a.repo
            )
            if SECRET.search(msg) or PRIVATE.search(msg):
                report(commit, "commit_metadata_sensitive_pattern")
            if re.search(rb"(?im)^Co-authored-by:", msg):
                report(commit, "coauthorship_trailer_requires_review")
        counts["unique_newly_examined_blobs"] = len(seen)
    result = {
        "status": "FAILED" if findings else "PASSED_FOCUSED_SCAN",
        "counts": dict(counts),
        "findings": findings,
        "scope": (
            "Pattern scan, JSON account/authorization structure, all archive "
            "members, extracted PDF text/metadata and PNG textual metadata. "
            "Not OCR or exhaustive rights/secret detection."
        ),
    }
    if a.report:
        a.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(findings))


if __name__ == "__main__":
    main()
