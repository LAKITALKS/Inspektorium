"""Positive and invalid controls for the offline-only capture derivation tool."""

import importlib.util
import json
from pathlib import Path

import pytest

from inspektorium.audit.workflow.live import task_sha256
from inspektorium.audit.execution.task_loader import load_task

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "extract_recorded_capture", ROOT / "scripts/extract_recorded_capture.py"
)
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


@pytest.fixture
def inputs(tmp_path):
    task = ROOT / "examples/audit/positive-task.json"
    loaded = load_task(task)
    text = (ROOT / "examples/audit/positive-recording.json").read_text()
    capture = {
        "schema": "aa-p10-live-capture/1.0",
        "task_id": loaded.id,
        "task_sha256": task_sha256(loaded),
        "profile_id": "synthetic-profile",
        "slot_key": f"{loaded.id}|synthetic-profile|primary",
        "call": {
            "http_status": 200,
            "response_body": {
                "content": [{"type": "text", "text": text}],
                "stop_reason": "end_turn",
            },
        },
        "interpretation": {"final_text": text},
    }
    return tmp_path / "capture.json", task, tmp_path / "derived", capture, text


def test_complete_primary_preserves_exact_recording(inputs):
    path, task, output, capture, text = inputs
    path.write_text(json.dumps(capture))
    manifest = extractor.extract(path, task, output)
    assert (output / "recording.json").read_bytes() == text.encode("utf-8")
    assert (output / "task.json").read_bytes() == task.read_bytes()
    assert manifest["supplied_capture_sha256"] == extractor.sha256(path.read_bytes())
    assert manifest["recording_sha256"] == extractor.sha256(text.encode("utf-8"))
    assert "not native live replay" in manifest["scope"]


@pytest.mark.parametrize(
    "damage",
    [
        "schema",
        "review",
        "task_id",
        "task_hash",
        "http",
        "body",
        "incomplete",
        "interpretation",
    ],
)
def test_invalid_capture_is_rejected_without_output(inputs, damage):
    path, task, output, capture, _ = inputs
    if damage == "schema":
        capture["schema"] = "unknown"
    elif damage == "review":
        capture["slot_key"] = capture["slot_key"].replace("|primary", "|counterreview")
    elif damage == "task_id":
        capture["task_id"] = "other"
    elif damage == "task_hash":
        capture["task_sha256"] = "0" * 64
    elif damage == "http":
        capture["call"]["http_status"] = 500
    elif damage == "body":
        capture["call"]["response_body"] = None
    elif damage == "incomplete":
        capture["call"]["response_body"]["stop_reason"] = "max_tokens"
    elif damage == "interpretation":
        capture["interpretation"]["final_text"] = "changed"
    path.write_text(json.dumps(capture))
    with pytest.raises(ValueError):
        extractor.extract(path, task, output)
    assert not output.exists()


@pytest.mark.parametrize("kind", ["directory", "file", "symlink", "dangling-symlink"])
def test_existing_output_is_never_overwritten(inputs, kind):
    path, task, output, capture, _ = inputs
    path.write_text(json.dumps(capture))
    if kind == "directory":
        output.mkdir()
    elif kind == "file":
        output.write_text("preserve")
    else:
        output.symlink_to(task if kind == "symlink" else output.parent / "absent")
    with pytest.raises(FileExistsError):
        extractor.extract(path, task, output)
    if kind == "file":
        assert output.read_text() == "preserve"
    if kind == "directory":
        assert list(output.iterdir()) == []
    if "symlink" in kind:
        assert output.is_symlink()
