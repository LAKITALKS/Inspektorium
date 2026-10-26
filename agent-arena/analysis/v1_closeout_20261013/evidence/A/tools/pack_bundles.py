"""Deterministic tar.gz of the three replay bundles (5 canonical files each) plus an index with member SHA-256."""
import gzip
import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path

S, OUT = Path(sys.argv[1]), Path(sys.argv[2])
members = sorted(p for p in (S / "replay").glob("*/*/*") if p.is_file() and p.parent.name != "replay-state"
                 and "replay-state" not in p.parts)
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
    for p in members:
        data = p.read_bytes()
        info = tarfile.TarInfo("replay_bundles/" + p.relative_to(S / "replay").as_posix())
        info.size, info.mtime, info.mode, info.uid, info.gid, info.uname, info.gname = len(data), 0, 0o644, 0, 0, "", ""
        tar.addfile(info, io.BytesIO(data))
gz = io.BytesIO()
with gzip.GzipFile(fileobj=gz, mode="wb", mtime=0, filename="") as f:
    f.write(buf.getvalue())
(OUT / "replay_bundles.tar.gz").write_bytes(gz.getvalue())
index = {"archive": "replay_bundles.tar.gz", "archive_sha256": hashlib.sha256(gz.getvalue()).hexdigest(),
         "description": "Offline replays (agent_arena 1.0.0, code commit 5560e95) of Sonnet LR-02, Sonnet LR-03 and Haiku LR-03 from a "
                        "scratch COPY of analysis/c25_p9_20261011/live_retest; no model call. Loose report.md would trip "
                        "git diff --check, so the bundles are stored only inside this archive.",
         "extract": "tar -xzf replay_bundles.tar.gz  (then: agent-arena audit inspect --bundle replay_bundles/<slot>/<revision>)",
         "members": [{"path": "replay_bundles/" + p.relative_to(S / "replay").as_posix(), "bytes": p.stat().st_size,
                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in members]}
(OUT / "replay_bundles.index.json").write_text(json.dumps(index, indent=1) + "\n")
print(len(members), index["archive_sha256"])
