"""The fetch script stops on a wrong hash and on hostile archives. No network."""

from __future__ import annotations

import stat
import zipfile
from pathlib import Path

import fetch_genius
import pytest


def _archive(path: Path, members: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as bundle:
        for name, content in members.items():
            bundle.writestr(name, content)
    return path


def test_the_pinned_source_is_exactly_the_agreed_commit_and_hash() -> None:
    assert fetch_genius.COMMIT == "34300c815c70a6ea52398d7a64305296c44663d7"
    assert fetch_genius.EXPECTED_SHA256 == (
        "2545e604a469f99a90d20dcd6ccae4784b092b79b251261ecdfab0b1cdae7f81"
    )
    assert fetch_genius.COMMIT in fetch_genius.URL


def test_a_matching_digest_is_accepted() -> None:
    digest = "b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b878ae4944c"
    assert fetch_genius.verify_sha256(b"foo\n", digest) == digest


def test_a_wrong_digest_is_rejected() -> None:
    with pytest.raises(fetch_genius.FetchError, match="SHA-256 mismatch"):
        fetch_genius.verify_sha256(b"tampered")


def test_a_wrong_digest_stops_before_anything_is_written(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(fetch_genius, "download", lambda: b"tampered")
    assert fetch_genius.main(["--external", str(tmp_path / "external")]) == 1
    assert not (tmp_path / "external").exists()


def test_a_clean_archive_is_unpacked(tmp_path: Path) -> None:
    archive = _archive(tmp_path / "ok.zip", {"annotations/a.tsv": "#Text=Hallo\n"})
    assert fetch_genius.safe_extract(archive, tmp_path / "out") == 1
    assert (tmp_path / "out/annotations/a.tsv").read_text() == "#Text=Hallo\n"


@pytest.mark.parametrize("name", ["../evil.tsv", "/abs/evil.tsv", "a\\..\\evil.tsv"])
def test_a_hostile_path_leaves_the_target_untouched(tmp_path: Path, name: str) -> None:
    archive = _archive(tmp_path / "bad.zip", {"ok.tsv": "x", name: "y"})
    with pytest.raises(fetch_genius.FetchError, match="unsafe path"):
        fetch_genius.safe_extract(archive, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_a_symbolic_link_is_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "link.zip"
    info = zipfile.ZipInfo("link.tsv")
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr(info, "/etc/passwd")
    with pytest.raises(fetch_genius.FetchError, match="symbolic link"):
        fetch_genius.safe_extract(archive, tmp_path / "out")
    assert not (tmp_path / "out").exists()
