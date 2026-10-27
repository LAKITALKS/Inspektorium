"""Extract a complete primary response for a new recorded-offline analysis.

This does not verify or recreate a historical live authorization, ledger, review
history, or bundle. Output provenance records the actual supplied capture bytes.
Run with the installed agent-arena package; no provider or network is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from inspektorium.audit.phase10_live import task_sha256
from inspektorium.audit.providers.anthropic_live import interpret_message
from inspektorium.audit.task_loader import load_task


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def extract(capture_path: Path, task_path: Path, output: Path) -> dict:
    raw = capture_path.read_bytes()
    capture = json.loads(raw)
    task = load_task(task_path)
    if capture.get("schema") != "aa-p10-live-capture/1.0":
        raise ValueError("Unsupported capture schema")
    expected_slot = f"{task.id}|{capture.get('profile_id')}|primary"
    if capture.get("slot_key") != expected_slot:
        raise ValueError("A matching primary capture is required; review captures are not primary inputs")
    if capture.get("task_id") != task.id or capture.get("task_sha256") != task_sha256(task):
        raise ValueError("Task identity or canonical task hash does not match the capture")
    call = capture.get("call") or {}
    body = call.get("response_body")
    if call.get("http_status") != 200 or not isinstance(body, dict):
        raise ValueError("A successful recorded response body is required")
    info = interpret_message(body)
    if info["completion_state"] != "complete":
        raise ValueError("Only a complete final response can become this offline example")
    if info.get("final_text") != (capture.get("interpretation") or {}).get("final_text"):
        raise ValueError("Stored interpretation differs from the response text blocks")
    recording = info["final_text"].encode("utf-8")
    task_bytes = task_path.read_bytes()
    manifest = {
        "schema": "agent-arena-offline-capture-derivation/1.0",
        "method": "UTF-8 encoding of concatenated recorded response text blocks, unchanged",
        "scope": "New recorded_offline analysis; not native live replay or original bundle verification",
        "unverified": ["historical authorization", "ledger binding", "historical review history",
                       "provider authenticity", "unredacted original capture identity"],
        "capture_filename": capture_path.name,
        "supplied_capture_sha256": sha256(raw),
        "capture_authorization_id": capture.get("authorization_id"),
        "attempt_id": capture.get("attempt_id"),
        "profile_id": capture.get("profile_id"),
        "task_id": task.id,
        "canonical_task_sha256": task_sha256(task),
        "recording_sha256": sha256(recording),
        "task_file_sha256": sha256(task_bytes),
    }
    # Reject every existing target, including an empty directory or symlink.
    output.mkdir(parents=True, exist_ok=False)
    (output / "recording.json").write_bytes(recording)
    (output / "task.json").write_bytes(task_bytes)
    (output / "derivation.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(extract(args.capture, args.task, args.output), indent=2))


if __name__ == "__main__":
    main()
