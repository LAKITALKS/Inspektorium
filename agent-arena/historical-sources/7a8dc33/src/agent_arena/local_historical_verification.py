"""Explicit read-only verification of the local historical ASA Phase-7B record.

The verifier implementation is tracked, but its hash-bound historical inputs are intentionally
ignored and are not part of the tracked-only test suite.  It executes deterministic representation
QA only; it does not establish independent scientific truth and never calls the official writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from agent_arena.artifact_binding import (
    PHASE7B_ASSURANCE_SCOPE,
    evaluate_artifact_release,
    load_forensic_record,
)
from agent_arena.release_boundary import OFFICIAL_RELEASE_NAMESPACE


VERIFICATION_TYPE = "LOCAL_HISTORICAL_VERIFICATION"
SUITE_SCOPE = "NOT_PART_OF_TRACKED_ONLY_FULL_SUITE"
ARTIFACT_ROLE = "NOT_AN_OFFICIAL_RELEASE"
CASE_ROOT = Path("cases/ASA_25_261_PREMIUM_GROUNDING/runs/run_001")
FORENSIC_RECORD_FILE = "forensic_record.json"
STORED_RELEASE_REPORT_FILE = "release_report.json"
EXPECTED_FORENSIC_RECORD_SHA256 = (
    "4c7dacd288a099ece36578bbc213892f75d57667ea41ce305f09f712e76cb465"
)
EXPECTED_STORED_REPORT_SHA256 = (
    "1c2ef23250e2cbe3a5e672ae7e74b3a6811582937caea4c875f8cbd353f8254b"
)
EXPECTED_GATES = (
    ("finding_artifact_binding", 26, 26, 0),
    ("summary_strength_monotonicity", 26, 26, 0),
    ("evidence_symmetry", 26, 26, 0),
    ("value_origin_provenance", 103, 103, 0),
    ("search_scope_binding", 5, 5, 0),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _namespace_snapshot(repo_root: Path) -> str:
    """Fingerprint the repository-local official namespace without changing it."""
    namespace = repo_root / OFFICIAL_RELEASE_NAMESPACE
    if not os.path.lexists(namespace):
        return "ABSENT"
    entries: list[dict[str, object]] = []
    if namespace.is_symlink():
        entries.append({"path": ".", "kind": "symlink", "target": os.readlink(namespace)})
    elif namespace.is_file():
        entries.append({"path": ".", "kind": "file", "sha256": _sha256(namespace)})
    else:
        for child in sorted(namespace.rglob("*")):
            relative = str(child.relative_to(namespace))
            if child.is_symlink():
                entries.append({"path": relative, "kind": "symlink", "target": os.readlink(child)})
            elif child.is_file():
                entries.append({"path": relative, "kind": "file", "sha256": _sha256(child)})
            elif child.is_dir():
                entries.append({"path": relative, "kind": "directory"})
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _result(status: str, *, success: bool, errors: list[str] | None = None) -> dict:
    return {
        "verification_type": VERIFICATION_TYPE,
        "suite_scope": SUITE_SCOPE,
        "artifact_role": ARTIFACT_ROLE,
        "status": status,
        "success": success,
        "errors": errors or [],
        "official_release_write_count": 0,
        "assurance_scope": PHASE7B_ASSURANCE_SCOPE,
        "independent_scientific_truth_verified": False,
    }


def verify_local_historical_asa(repo_root: str | Path) -> dict:
    """Verify the exact local historical bytes through the current deterministic five-gate path."""
    root = Path(repo_root).resolve()
    case_root = root / CASE_ROOT
    record_path = case_root / FORENSIC_RECORD_FILE
    stored_report_path = case_root / STORED_RELEASE_REPORT_FILE
    missing = [
        str(path.relative_to(root))
        for path in (record_path, stored_report_path)
        if not path.is_file()
    ]
    if missing:
        result = _result(
            "HISTORICAL_INPUT_UNAVAILABLE",
            success=False,
            errors=[f"required local historical input unavailable: {path}" for path in missing],
        )
        result["input_paths"] = {
            "forensic_record": str(record_path),
            "stored_release_report": str(stored_report_path),
        }
        return result

    try:
        hashes_before = {
            "forensic_record": _sha256(record_path),
            "stored_release_report": _sha256(stored_report_path),
        }
    except OSError as exc:
        return _result(
            "HISTORICAL_INPUT_UNAVAILABLE",
            success=False,
            errors=[f"historical input unreadable: {type(exc).__name__}: {exc}"],
        )
    expected_hashes = {
        "forensic_record": EXPECTED_FORENSIC_RECORD_SHA256,
        "stored_release_report": EXPECTED_STORED_REPORT_SHA256,
    }
    hash_errors = [
        f"{name} SHA-256 mismatch: expected {expected_hashes[name]}, observed {observed}"
        for name, observed in hashes_before.items()
        if observed != expected_hashes[name]
    ]
    if hash_errors:
        result = _result("HISTORICAL_INPUT_HASH_MISMATCH", success=False, errors=hash_errors)
        result["hashes_before"] = hashes_before
        return result

    namespace_before = _namespace_snapshot(root)
    errors: list[str] = []
    record = None
    fresh_report = None
    stored_report: object = None
    try:
        record = load_forensic_record(record_path)
        stored_report = json.loads(stored_report_path.read_text())
        fresh_report = evaluate_artifact_release(record)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"historical input/evaluation failure: {type(exc).__name__}: {exc}")

    gate_results: list[dict[str, object]] = []
    if fresh_report is not None:
        observed_gate_ids = tuple(check.name for check in fresh_report.checks_run)
        expected_gate_ids = tuple(gate[0] for gate in EXPECTED_GATES)
        if observed_gate_ids != expected_gate_ids:
            errors.append(
                f"mandatory gate identity mismatch: expected {expected_gate_ids}, "
                f"observed {observed_gate_ids}"
            )
        for index, expected in enumerate(EXPECTED_GATES):
            gate_id, eligible, evaluated, findings = expected
            if index >= len(fresh_report.checks_run):
                errors.append(f"mandatory gate result missing: {gate_id}")
                continue
            check = fresh_report.checks_run[index]
            gate_result = {
                "gate_id": check.name,
                "eligible_count": check.eligible_count,
                "evaluated_count": check.evaluated_count,
                "finding_count": check.finding_count,
                "unevaluated_count": check.unevaluated_count,
                "coverage_state": check.coverage_state,
                "status": check.status,
            }
            gate_results.append(gate_result)
            if (
                check.name,
                check.eligible_count,
                check.evaluated_count,
                check.finding_count,
            ) != expected:
                errors.append(
                    f"historical gate population mismatch for {gate_id}: "
                    f"expected {expected[1:]}, observed "
                    f"{(check.eligible_count, check.evaluated_count, check.finding_count)}"
                )
            if check.eligible_count <= 0:
                errors.append(f"historical gate has zero eligibility: {gate_id}")
            if (
                check.evaluated_count != check.eligible_count
                or check.unevaluated_count != 0
                or check.status != "ran"
                or check.coverage_state != "evaluated_clean"
            ):
                errors.append(f"historical gate coverage is not complete and clean: {gate_id}")
        if not fresh_report.releasable or fresh_report.decision_status != "releasable":
            errors.append(
                "fresh deterministic historical decision is not releasable: "
                f"{fresh_report.decision_status}"
            )

    if not isinstance(stored_report, dict):
        errors.append("stored historical release report is not a JSON object")
        stored_releasable = False
    else:
        stored_releasable = stored_report.get("releasable") is True
        if not stored_releasable:
            errors.append("stored historical release decision is not releasable")
        if record is not None and stored_report.get("forensic_record_id") != record.record_id:
            errors.append("stored historical release decision belongs to another record")

    try:
        hashes_after = {
            "forensic_record": _sha256(record_path),
            "stored_release_report": _sha256(stored_report_path),
        }
    except OSError as exc:
        hashes_after = {}
        errors.append(f"post-verification historical hash unavailable: {type(exc).__name__}: {exc}")
    if hashes_after != hashes_before:
        errors.append("historical input bytes changed during verification")
    namespace_after = _namespace_snapshot(root)
    if namespace_after != namespace_before:
        errors.append("repository-local official release namespace changed during verification")

    result = _result(
        "HISTORICAL_VERIFICATION_PASSED" if not errors else "HISTORICAL_VERIFICATION_FAILED",
        success=not errors,
        errors=errors,
    )
    result.update(
        {
            "input_paths": {
                "forensic_record": str(record_path),
                "stored_release_report": str(stored_report_path),
            },
            "hashes_before": hashes_before,
            "hashes_after": hashes_after,
            "historical_inputs_unchanged": hashes_after == hashes_before,
            "record_id": record.record_id if record is not None else None,
            "mandatory_gates": gate_results,
            "fresh_decision": (
                fresh_report.decision_status if fresh_report is not None else None
            ),
            "fresh_releasable": (
                fresh_report.releasable if fresh_report is not None else False
            ),
            "stored_releasable": stored_releasable,
            "official_namespace_unchanged": namespace_after == namespace_before,
        }
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent_arena.local_historical_verification",
        description=(
            "Explicit read-only local verification; not part of the tracked-only Full Suite."
        ),
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    verify = subcommands.add_parser(
        "verify-asa-phase7b", help="Verify the hash-bound local historical ASA Phase-7B record"
    )
    verify.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root containing the ignored local historical case",
    )
    args = parser.parse_args(argv)

    result = verify_local_historical_asa(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["success"]:
        return 0
    if result["status"] == "HISTORICAL_INPUT_UNAVAILABLE":
        return 2
    if result["status"] == "HISTORICAL_INPUT_HASH_MISMATCH":
        return 3
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
