"""Normalize tar/gzip ownership/time metadata without changing payloads or modes.

All outputs are exclusive new files. The input is never modified. A private byte
copy of the original is mandatory. No archive member is extracted or executed.
Use this after the final package build, then scan the resulting public archive.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_members(data: bytes) -> list[tuple[tarfile.TarInfo, bytes]]:
    result = []
    names = set()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for member in tf:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or member.name in names:
                raise ValueError("unsafe or duplicate archive member: " + member.name)
            if not (member.isfile() or member.isdir()):
                raise ValueError(
                    "nonregular archive member requires review: " + member.name
                )
            names.add(member.name)
            payload = tf.extractfile(member).read() if member.isfile() else b""
            result.append((member, payload))
    return result


def normalize(data: bytes) -> tuple[bytes, list[dict]]:
    members = read_members(data)
    out = io.BytesIO()
    with gzip.GzipFile(
        fileobj=out, mode="wb", filename="", mtime=0, compresslevel=9
    ) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tf:
            for old, payload in members:
                new = copy.copy(old)
                new.uid = new.gid = new.mtime = 0
                new.uname = new.gname = ""
                new.pax_headers = {
                    key: value
                    for key, value in old.pax_headers.items()
                    if key not in {"uid", "gid", "uname", "gname", "mtime"}
                }
                # Preserve the original member order, path, mode, type, size and body.
                tf.addfile(new, io.BytesIO(payload) if old.isfile() else None)
    public = out.getvalue()
    reread = read_members(public)
    if len(members) != len(reread):
        raise ValueError("member count changed")
    manifest = []
    for (old, original), (new, revised) in zip(members, reread, strict=True):
        equal = (
            old.name == new.name
            and old.type == new.type
            and old.mode == new.mode
            and old.size == new.size
            and original == revised
        )
        normalized = (
            new.uid == new.gid == new.mtime == 0 and not new.uname and not new.gname
        )
        if not equal or not normalized:
            raise ValueError(
                "payload/permission or metadata invariant failed: " + old.name
            )
        manifest.append(
            {
                "path": old.name,
                "type": "file" if old.isfile() else "directory",
                "mode": oct(old.mode),
                "bytes": old.size,
                "original_sha256": sha(original),
                "public_sha256": sha(revised),
                "payload_and_permissions_equal": equal,
                "ownership_and_mtime_normalized": normalized,
            }
        )
    return public, manifest


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--original-copy", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    a = p.parse_args()
    paths = [
        a.input.resolve(),
        a.output.resolve(),
        a.original_copy.resolve(),
        a.manifest.resolve(),
    ]
    if len(set(paths)) != len(paths):
        raise SystemExit("input, output, original-copy and manifest must be distinct")
    if a.input.is_symlink() or not a.input.is_file():
        raise SystemExit("input must be a regular file")
    for dst in (a.output, a.original_copy, a.manifest):
        if dst.exists() or dst.is_symlink():
            raise SystemExit("refusing to overwrite: " + str(dst))
        if not dst.parent.is_dir():
            raise SystemExit("output parent must already exist: " + str(dst.parent))
    original = a.input.read_bytes()
    public, members = normalize(original)
    again, _ = normalize(original)
    if public != again:
        raise SystemExit("determinism check failed")
    result = {
        "schema": "release-archive-metadata-derivation/v1",
        "date": "2026-10-26",
        "original_archive": a.input.name,
        "public_archive": a.output.name,
        "original_sha256": sha(original),
        "public_sha256": sha(public),
        "original_bytes": len(original),
        "public_bytes": len(public),
        "changed_fields": [
            "tar uid",
            "tar gid",
            "tar uname",
            "tar gname",
            "tar mtime",
            "matching PAX ownership/mtime overrides",
            "gzip mtime",
            "gzip filename",
        ],
        "member_count": len(members),
        "all_member_payloads_and_permissions_equal": True,
        "deterministic_repeat_equal": True,
        "members": members,
    }
    if a.input.read_bytes() != original:
        raise SystemExit("input changed during processing")
    # Private preservation precedes creation of the normalized public artifact.
    with a.original_copy.open("xb") as f:
        f.write(original)
    with a.output.open("xb") as f:
        f.write(public)
    with a.manifest.open("x") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if sha(a.original_copy.read_bytes()) != result["original_sha256"]:
        raise SystemExit("private original-copy verification failed")
    if sha(a.output.read_bytes()) != result["public_sha256"]:
        raise SystemExit("public archive verification failed")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "members"}, indent=2
        )
    )


if __name__ == "__main__":
    main()
