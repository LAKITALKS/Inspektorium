"""Immutable local audit revisions. Inspection replays controls without provider calls."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from inspektorium.audit.workflow import render as rendering
from inspektorium.audit.execution.evaluator import evaluate_run
from inspektorium.audit.workflow.models import (
    FILES,
    AuditRecord,
    Decision,
    Manifest,
    OperationResult,
    Parent,
    ReleaseIntent,
    Verification,
)
from inspektorium.audit.workflow.pipeline import (
    bundle_mode,
    canonical,
    control,
    digest,
    evaluate,
    preflight,
    provenance,
    reconstruct,
    registry_for,
    registry_fingerprint,
)
from inspektorium.audit.review.runtime import OfflineReviewProvider, submit_human_review
from inspektorium.audit.execution.runner import run_agent
from inspektorium.audit.schemas import RunRecord, Task


def _load(directory: Path):
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Bundle must be a real directory")
    if {p.name for p in directory.iterdir()} != set(FILES):
        raise ValueError("Bundle must contain exactly the five canonical files")
    for name in FILES:
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Bundle members must be ordinary files")

    # Duplicate JSON keys must not hide a second history/decision layer.
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON field: {key}")
            result[key] = value
        return result

    def read(name, model):
        return model.model_validate(
            json.loads((directory / name).read_bytes(), object_pairs_hook=unique)
        )

    return (
        read("record.json", AuditRecord),
        read("decision.json", Decision),
        read("manifest.json", Manifest),
    )


def _decision(audit, intent, directory):
    if intent != audit.release_intent:
        raise ValueError(
            "Release intent differs from the immutable revision core; create a new revision"
        )
    run = RunRecord.model_validate(audit.run_record)
    subject = digest(audit.model_dump(mode="json"))
    status, controls, review, selected, assessment, forensic = evaluate(
        run, subject, audit.provenance
    )
    mode, _ = bundle_mode(run, review)
    if mode != audit.execution_mode:
        raise ValueError(
            "Recorded execution mode differs from the mode derived from its carriers"
        )
    if intent is not None:
        if (
            status != "READY_FOR_RELEASE"
            or not intent.reviewer.strip()
            or not intent.reason.strip()
        ):
            raise ValueError(
                "Host intent cannot waive a blocked control; resolve the cause first"
            )
        status = "RELEASED"
    if status != audit.status:
        raise ValueError(
            f"Stale operational status: expected {status}, recorded {audit.status}"
        )
    if audit.selected_position_id != (selected["position_id"] if selected else None):
        raise ValueError(
            "Selected analysis is stale or does not cover current review history"
        )
    projected = rendering.projection(
        audit, controls, review, selected, assessment, forensic
    )
    hashes = rendering.validate_files(directory, projected, mode=audit.execution_mode)
    registry = registry_for(audit.execution_mode)
    controls += [
        control(
            name,
            subject,
            True,
            f"Actual UTF-8 file and complete ordered projection checked: {hashes[file]}",
            registry=registry,
        )
        for name, file in (("markdown_qa", "report.md"), ("html_qa", "report.html"))
    ]
    if (
        len(controls) != len(registry)
        or {c.control_id: c.version for c in controls} != registry
    ):
        raise ValueError("Mandatory control registry coverage invalid")
    return Decision(
        status=status,
        subject=subject,
        registry_fingerprint=registry_fingerprint(audit.execution_mode),
        controls=controls,
        report_hashes=hashes,
        release_intent=intent,
    )


def inspect_bundle(path: Path) -> Verification:
    """valid means intact/current, not necessarily releasable; status is independent."""
    try:
        directory = Path(path)
        audit, decision, manifest = _load(directory)
        values = manifest.model_dump(mode="json")
        fingerprint = values.pop("fingerprint")
        if digest(values) != fingerprint:
            raise ValueError("Manifest fingerprint mismatch")
        if set(manifest.files) != set(FILES) - {"manifest.json"}:
            raise ValueError("Manifest artifact set mismatch")
        if any(
            digest((directory / name).read_bytes()) != value
            for name, value in manifest.files.items()
        ):
            raise ValueError("Artifact bytes do not match manifest")
        if (
            manifest.revision_id != audit.revision_id
            or manifest.status != audit.status
            or manifest.created_at != audit.created_at
            or manifest.provenance != audit.provenance
            or manifest.release_intent != audit.release_intent
            or manifest.execution_mode != audit.execution_mode
        ):
            raise ValueError("Manifest and canonical record disagree")
        if (decision.release_intent is not None) != (audit.status == "RELEASED"):
            raise ValueError("Release status and explicit host intent disagree")
        expected = _decision(audit, decision.release_intent, directory)
        if canonical(expected.model_dump()) != canonical(decision.model_dump()):
            raise ValueError(
                "Stored decision/controls differ from current raw-bound recomputation"
            )
        return Verification(valid=True, status=audit.status)
    except Exception as exc:
        return Verification(
            valid=False,
            errors=[
                f"Verification failed: {exc}. Rebuild from original inputs; do not release."
            ],
        )


def _write_revision(record, *, output_root, parent=None, intent=None):
    staging = None
    try:
        review, selected, assessment, forensic = reconstruct(record)
        mode, mode_errors = bundle_mode(record, review)
        if mode is None:
            # Nothing is relabelled: a carrier that is neither a built-in offline recording nor
            # bound AA-P10-LIVE/1.0 evidence blocks the bundle.
            return OperationResult(
                status="PREFLIGHT_BLOCKED",
                errors=[
                    "Execution provenance is mixed, unknown or unbound; only built-in offline recordings or "
                    "complete AA-P10-LIVE/1.0 evidence are accepted: "
                    + "; ".join(mode_errors)
                ],
            )
        bound = provenance(record, review, selected, forensic, assessment)
        status, _, _, _, _, _ = evaluate(record, "pending", bound)
        if intent:
            if status != "READY_FOR_RELEASE":
                return OperationResult(
                    status=status,
                    errors=[
                        "Controls block release; resolve the reported analysis/review cause."
                    ],
                )
            status = "RELEASED"
        audit = AuditRecord(
            revision_id=str(uuid4()),
            parent=parent,
            created_at=datetime.now(timezone.utc).isoformat(),
            status=status,
            release_intent=intent,
            execution_mode=mode,
            run_record=record.model_dump(mode="json"),
            selected_position_id=selected["position_id"] if selected else None,
            provenance=bound,
        )
        subject = digest(audit.model_dump(mode="json"))
        _, controls, review, selected, assessment, forensic = evaluate(
            record, subject, bound
        )
        projected = rendering.projection(
            audit, controls, review, selected, assessment, forensic
        )
        root = Path(output_root)
        root.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".audit-staging-", dir=root))
        (staging / "record.json").write_bytes(canonical(audit.model_dump(mode="json")))
        (staging / "report.md").write_bytes(rendering.markdown(projected))
        (staging / "report.html").write_bytes(rendering.html_report(projected))
        decision = _decision(audit, intent, staging)
        (staging / "decision.json").write_bytes(
            canonical(decision.model_dump(mode="json"))
        )
        values = dict(
            revision_id=audit.revision_id,
            status=audit.status,
            created_at=audit.created_at,
            release_intent=audit.release_intent,
            execution_mode=audit.execution_mode,
            provenance=bound,
            files={
                n: digest((staging / n).read_bytes())
                for n in FILES
                if n != "manifest.json"
            },
            fingerprint="",
        )
        manifest = Manifest(**values)
        fields = manifest.model_dump(mode="json")
        fields.pop("fingerprint")
        manifest.fingerprint = digest(fields)
        (staging / "manifest.json").write_bytes(
            canonical(manifest.model_dump(mode="json"))
        )
        verification = inspect_bundle(staging)
        if not verification.valid:
            raise ValueError("; ".join(verification.errors))
        for name in FILES:
            with (staging / name).open("rb") as file:
                os.fsync(file.fileno())
        destination = root / audit.revision_id
        if destination.exists():
            raise ValueError("Immutable revision already exists")
        staging.rename(destination)
        staging = None
        descriptor = os.open(root, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return OperationResult(
            status=status,
            path=str(destination.resolve()),
            errors=[
                f"{c.control_id}: {c.reason}" for c in controls if c.outcome == "fail"
            ],
        )
    except Exception as exc:
        return OperationResult(
            status="RELEASE_BLOCKED",
            errors=[
                f"Bundle blocked: {exc}. Correct inputs or controls and create a new revision."
            ],
        )
    finally:
        if staging is not None:
            shutil.rmtree(staging)


def create_candidate(
    record: RunRecord, *, output_root: Path, parent: Parent | None = None
) -> OperationResult:
    return _write_revision(record, output_root=output_root, parent=parent)


def run_audit(
    task: Task, provider, *, output_root: Path, review_state: Path | None = None
) -> OperationResult:
    errors = preflight(task)
    if errors:
        return OperationResult(status="PREFLIGHT_BLOCKED", errors=errors)
    from inspektorium.audit.workflow.live import LiveAuditProvider, ReplayProvider

    if type(provider) in (LiveAuditProvider, ReplayProvider):
        return _run_live(
            task, provider, output_root=output_root, review_state=review_state
        )
    if (
        type(provider) is not OfflineReviewProvider
        or set(vars(provider)) != {"raw_output", "error", "requests"}
        or type(provider.raw_output) is not str
        or (provider.error is not None and type(provider.error) is not str)
        or type(provider.requests) is not list
    ):
        return OperationResult(
            status="PREFLIGHT_BLOCKED",
            errors=[
                "Offline mode requires the exact built-in recorded provider; no fallback is allowed."
            ],
        )
    record = evaluate_run(task, str(uuid4()), [run_agent(provider, task)])
    return create_candidate(record, output_root=output_root)


def _run_live(
    task: Task, provider, *, output_root: Path, review_state: Path | None
) -> OperationResult:
    """Live or replayed-live primary run plus Phase9 review only on its documented triggers."""
    from inspektorium.audit.review.pipeline import refresh_run_phase9
    from inspektorium.audit.review.runtime import execute_review

    # The profile revision binds both prompt versions: the primary Phase8 prompt and its Phase9 review.
    primary_version, review_version = provider.profile.prompt_versions
    if provider.kind != "primary" or provider.prompt_version != primary_version:
        return OperationResult(
            status="PREFLIGHT_BLOCKED",
            errors=["Live audit requires the primary Phase8 slot provider."],
        )
    if review_state is None:
        return OperationResult(
            status="PREFLIGHT_BLOCKED",
            errors=["Live audit requires a Phase9 review state directory."],
        )
    if provider.task_id != task.id:
        return OperationResult(
            status="PREFLIGHT_BLOCKED",
            errors=["Provider slot belongs to another case."],
        )
    refusal = provider.preflight(task) if hasattr(provider, "preflight") else None
    if refusal:
        return OperationResult(status="PREFLIGHT_BLOCKED", errors=[refusal])
    from inspektorium.audit.review.routing import case_key

    # A case state written under another authorization would reject this run's original analysis
    # only after the paid primary request; refuse before it instead.
    if (
        Path(review_state)
        / provider.profile.profile_id
        / "phase9"
        / f"{case_key(task)}.json"
    ).exists() and provider.slot not in provider.session.ledger.data["terminal_keys"]:
        return OperationResult(
            status="PREFLIGHT_BLOCKED",
            errors=[
                "Review state already holds this case from another run; use a fresh review state per authorization."
            ],
        )
    record = evaluate_run(
        task, str(uuid4()), [run_agent(provider, task, prompt_version=primary_version)]
    )
    route = refresh_run_phase9(record).metadata.get("phase9", {}).get("route")
    if route == "REVIEW_RECOMMENDED":
        from inspektorium.audit.workflow.live import review_allowance

        state = Path(review_state) / provider.profile.profile_id
        reviewer = type(provider)(
            provider.session,
            provider.profile.profile_id,
            task.id,
            "counterreview",
            review_version,
        )
        # A per-model review cap of a successor authorization records a denial; the case stays open.
        # The live decision is written to the ledger first, so replay reproduces it exactly.
        denied = review_allowance(provider.session, reviewer.slot, claim=True)
        record = execute_review(
            record,
            reviewer,
            base_dir=state,
            authorized=denied is None,
            budget_calls=0 if denied else 2,
            kind="counterreview",
            denial_reason=denied,
        )
        data = record.metadata.get("phase9", {})
        counter = [
            a for a in data.get("attempts", []) if a.get("kind") == "counterreview"
        ]
        if (
            counter
            and counter[-1].get("status") == "completed"
            and data.get("mandatory") is True
            and data.get("technical_status") == "completed"
        ):
            stability = type(provider)(
                provider.session,
                provider.profile.profile_id,
                task.id,
                "stability",
                review_version,
            )
            denied = review_allowance(provider.session, stability.slot, claim=True)
            record = execute_review(
                record,
                stability,
                base_dir=state,
                authorized=denied is None,
                budget_calls=0 if denied else 2,
                kind="stability",
                denial_reason=denied,
            )
    return create_candidate(record, output_root=output_root)


def _parent(path):
    verification = inspect_bundle(path)
    if not verification.valid:
        raise ValueError("; ".join(verification.errors))
    audit, _, manifest = _load(Path(path))
    return audit, Parent(
        revision_id=audit.revision_id, manifest_fingerprint=manifest.fingerprint
    )


def release_candidate(
    path: Path, *, output_root: Path, reviewer: str, reason: str
) -> OperationResult:
    try:
        audit, parent = _parent(path)
        if audit.status != "READY_FOR_RELEASE":
            return OperationResult(
                status="RELEASE_BLOCKED",
                errors=[
                    f"Candidate is {audit.status}; a current READY_FOR_RELEASE candidate is required."
                ],
            )
        intent = ReleaseIntent(reviewer=reviewer, reason=reason)
        return _write_revision(
            RunRecord.model_validate(audit.run_record),
            output_root=output_root,
            parent=parent,
            intent=intent,
        )
    except Exception as exc:
        return OperationResult(status="RELEASE_BLOCKED", errors=[str(exc)])


def review_candidate(
    path: Path,
    *,
    output_root: Path,
    state_dir: Path,
    selected_position_id: str,
    reviewer: str,
    reason: str,
    corrected_raw_output: str | None = None,
) -> OperationResult:
    try:
        audit, parent = _parent(path)
        record = submit_human_review(
            RunRecord.model_validate(audit.run_record),
            base_dir=state_dir,
            selected_position_id=selected_position_id,
            reviewer_provenance=reviewer,
            reason=reason,
            corrected_raw_output=corrected_raw_output,
        )
        return create_candidate(record, output_root=output_root, parent=parent)
    except Exception as exc:
        return OperationResult(
            status="REVIEW_REQUIRED",
            errors=[
                f"Review rejected: {exc}. Supply valid bound selection/correction; historical controls cannot be waived."
            ],
        )
