"""Download the pinned GENIUS annotations archive, verify it and unpack it.

This is the only network access of the study tooling. The commit and the
SHA-256 are fixed; a mismatch stops the script before anything is unpacked.
"""

from __future__ import annotations

import argparse
import hashlib
import ssl
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

REPOSITORY = "darius-ipn/genius_keylogs"
COMMIT = "34300c815c70a6ea52398d7a64305296c44663d7"
ASSET = "annotations.zip"
EXPECTED_SHA256 = "2545e604a469f99a90d20dcd6ccae4784b092b79b251261ecdfab0b1cdae7f81"
URL = f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/{ASSET}"
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXTERNAL = STUDY_ROOT / "data" / "external"


class FetchError(RuntimeError):
    """The archive could not be accepted; nothing was unpacked."""


def verify_sha256(payload: bytes, expected: str = EXPECTED_SHA256) -> str:
    """Return the digest of ``payload`` or fail if it differs from ``expected``."""

    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected:
        raise FetchError(f"SHA-256 mismatch: expected {expected}, got {actual}")
    return actual


def _safe_member_path(name: str, target: Path) -> Path:
    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts or "\\" in name:
        raise FetchError(f"unsafe path in archive: {name!r}")
    return target.joinpath(*member.parts)


def safe_extract(archive: Path, target: Path) -> int:
    """Unpack ``archive`` below ``target`` and return the number of files.

    Every member is checked before the first file is written, so a hostile
    archive leaves ``target`` untouched.
    """

    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        destinations = [_safe_member_path(item.filename, target) for item in members]
        for item in members:
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise FetchError(f"symbolic link in archive: {item.filename!r}")
        written = 0
        for item, destination in zip(members, destinations, strict=True):
            if item.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(bundle.read(item))
            written += 1
    return written


def _tls_context() -> ssl.SSLContext:
    """Return a verifying context, with certifi's roots where it is installed.

    The python.org macOS builds ship without system roots. Verification stays
    on in every case.
    """

    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def download(url: str = URL) -> bytes:
    """Fetch the archive, bounded in size."""

    try:
        with urllib.request.urlopen(  # noqa: S310
            url, timeout=120, context=_tls_context()
        ) as response:
            payload: bytes = response.read(MAX_ARCHIVE_BYTES + 1)
    except urllib.error.URLError as error:
        raise FetchError(f"download failed: {error}") from error
    if len(payload) > MAX_ARCHIVE_BYTES:
        raise FetchError("archive exceeds the size limit")
    return payload


def fetch(external: Path = DEFAULT_EXTERNAL) -> tuple[str, int]:
    """Download, verify and unpack; return the digest and the file count."""

    payload = download()
    digest = verify_sha256(payload)
    external.mkdir(parents=True, exist_ok=True)
    archive = external / ASSET
    archive.write_bytes(payload)
    return digest, safe_extract(archive, external / "genius")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", type=Path, default=DEFAULT_EXTERNAL)
    args = parser.parse_args(argv)
    try:
        digest, count = fetch(args.external)
    except FetchError as error:
        print(f"STOPPED: {error}", file=sys.stderr)
        return 1
    print(f"verified {digest}; unpacked {count} files from commit {COMMIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
