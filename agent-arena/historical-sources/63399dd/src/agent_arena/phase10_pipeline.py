"""Current controls reconstructed from raw responses and every Phase9 carrier."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from importlib.metadata import version
from pathlib import Path

from agent_arena import artifact_binding as gates
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase10_models import CONTRACT_VERSION, Control
from agent_arena.phase8_pipeline import assess_agent_result
from agent_arena.phase9_pipeline import refresh_run_phase9
from agent_arena.phase9_review import case_key
from agent_arena.providers.anthropic_live import benchmark_fields
from agent_arena.schemas import AgentResult, ForensicRecord, RunRecord, Task, TaskType

# Independent versioned inventory: an accidentally omitted registry entry fails closed.
GATE_VERSIONS = {"finding_artifact_binding": "1.1.0", "summary_strength_monotonicity": "1.0.0",
                 "evidence_symmetry": "1.1.0", "value_origin_provenance": "1.0.0",
                 "search_scope_binding": "1.0.0"}
# input_preflight 1.1 (Package B): curated benchmark cases are refused as audit inputs.
REGISTRY = {"input_preflight": "1.1", "analysis_source": "1.0", **GATE_VERSIONS,
            # 1.1 = AA-P8/1.1 + AA-P9/1.1 (separate model/host states, mandatory conflict review);
            # 1.2 = AA-P8/1.2 + AA-P9/1.2 (Package B: C15 for every proposition, label-sensitive materiality).
            "phase8_semantics_taxonomy": "1.2", "phase9_history_review": "1.2",
            "provenance": "1.0", "markdown_qa": "1.0", "html_qa": "1.0"}
# AA-P10-LIVE/1.0: live and replayed-live bundles bind a separately versioned provenance rule.
# Apart from that rule the live registry equals the offline registry above; both moved to the 1.1
# P8/P9 entries together, so their fingerprints changed with AA-P8/1.1 + AA-P9/1.1.
LIVE_REGISTRY = {**REGISTRY, "provenance": "live-1.0"}
LIVE_CONFIG = {"live_generation": "live-anthropic-v1", "offline_replay_of_live": "live-replay-v1"}
LIVE_NOTICES = {
    "live_generation": "LIVE MODEL GENERATION (AA-P10-LIVE/1.0); see execution evidence for model, request IDs and cost",
    "offline_replay_of_live": ("OFFLINE REPLAY of an earlier live model generation (AA-P10-LIVE/1.0); "
                               "no new model call in this execution"),
}


def registry_for(mode: str) -> dict:
    return REGISTRY if mode == "recorded_offline" else LIVE_REGISTRY


def bundle_mode(record: RunRecord, review: dict) -> tuple[str | None, list[str]]:
    """Single execution mode derived from every result and Phase9 carrier; never caller-supplied."""
    from agent_arena.phase10_live import execution_mode
    return execution_mode(record, review)


def canonical(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def digest(value) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def _git_source_matches(directory: Path, contents: dict[str, bytes], commit: str) -> bool:
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        return False
    try:
        root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                           cwd=directory, stderr=subprocess.DEVNULL).decode().strip())
        prefix = directory.relative_to(root).as_posix() + "/"
        tree = subprocess.check_output(["git", "ls-tree", "-rz", commit, "--", prefix],
                                       cwd=root, stderr=subprocess.DEVNULL)
        tracked = {}
        for entry in tree.split(b"\0"):
            if not entry:
                continue
            info, name = entry.decode().split("\t", 1)
            mode, kind, oid = info.split()
            if name.endswith(".py"):
                if kind != "blob" or mode not in {"100644", "100755"}:
                    return False
                tracked[name.removeprefix(prefix)] = oid
        if set(tracked) != set(contents):
            return False
        for name, raw in contents.items():
            oid = tracked[name]
            algorithm = hashlib.sha1 if len(oid) == 40 else hashlib.sha256
            if algorithm(f"blob {len(raw)}\0".encode() + raw).hexdigest() != oid:
                return False
        return True
    except (OSError, subprocess.CalledProcessError, ValueError):
        return False


def code_identity() -> dict:
    """Installed bytes are authoritative; a Git claim is made only if every file matches."""
    directory = Path(__file__).resolve().parent
    contents = {p.relative_to(directory).as_posix(): p.read_bytes()
                for p in sorted(directory.rglob("*.py"))}
    files = {name: digest(raw) for name, raw in contents.items()}
    source_commit = None
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=directory,
                                         stderr=subprocess.DEVNULL).decode().strip()
        if _git_source_matches(directory, contents, commit):
            source_commit = commit
    except (OSError, subprocess.CalledProcessError):
        pass
    return {"code_fingerprint": digest(files), "module_hashes": files,
            "verified_source_commit": source_commit,
            "source_binding": "verified Git source bytes" if source_commit else
            "installed bytes only; no verified tracked-source claim"}


def source_claim_valid(bound: dict) -> bool:
    claim = bound.get("verified_source_commit")
    if claim is None:
        return bound.get("source_binding") == "installed bytes only; no verified tracked-source claim"
    directory = Path(__file__).resolve().parent
    return (isinstance(claim, str) and bound.get("source_binding") == "verified Git source bytes" and
            _git_source_matches(directory, {p.relative_to(directory).as_posix(): p.read_bytes()
                                            for p in directory.rglob("*.py")}, claim))


def preflight(task: Task) -> list[str]:
    errors = []
    if task.task_type != TaskType.STUDY_FORENSICS:
        errors.append("Use a study_forensics task for the canonical audit.")
    if not task.id.strip() or not task.prompt.strip():
        errors.append("Supply a nonempty task ID and exact original claim.")
    curated = benchmark_fields(task)
    if curated:
        # input_preflight 1.1 (Package B): a curated library case is not an audit input; its
        # context may be curator commentary naming the expected label.
        errors.append("Curated benchmark case fields present (" + ", ".join(curated) + "); supply only the claim, "
                      "its source context and identity fields.")
    return errors


def reconstruct(record: RunRecord) -> tuple[dict, dict | None, dict, ForensicRecord | None]:
    refreshed = refresh_run_phase9(record)
    review = refreshed.metadata.get("phase9", {})
    positions = review.get("positions", [])
    final_id = review.get("final_position_id")
    selected = next((p for p in positions if p["position_id"] == final_id), None) if final_id else next(
        iter(sorted((p for p in positions if p["origin"] == "original"),
                    key=lambda p: p["position_id"])), None)
    assessment, forensic = {}, None
    if selected:
        result = AgentResult.model_validate(selected["agent_result"])
        assessment = assess_agent_result(record.task, result)
        parsed, diagnostics = parse_structured_output(result.raw_output, result.finish_reason)
        if parsed and diagnostics.ok and not diagnostics.repaired and not diagnostics.truncation_suspected \
                and not diagnostics.multiple_objects:
            try:
                forensic = ForensicRecord.model_validate(parsed.forensic_record)
            except (ValueError, TypeError):
                pass
    return review, selected, assessment, forensic


def provenance(record: RunRecord, review: dict, selected: dict | None,
               forensic: ForensicRecord | None, assessment: dict) -> dict:
    payload = forensic.model_dump(mode="json") if forensic else {}
    mode, mode_errors = bundle_mode(record, review)
    bound = {"contract": CONTRACT_VERSION, "config": "offline-recording-v1",
            "package_version": version("agent-arena"), "code": code_identity(), "case_id": case_key(record.task), "run_id": record.run_id,
            "input_fingerprint": digest(record.task.model_dump(mode="json")),
            "analysis_fingerprint": digest(record.model_dump(mode="json")),
            "evidence_fingerprint": digest(payload.get("evidence", [])),
            "ledger_fingerprint": digest(payload.get("phase8")),
            "review_fingerprint": digest(review),
            "phase8_summary": {"technical_status": assessment.get("technical_status", "not_executed"),
                               "composite_state": assessment.get("composite_state", "unknown"),
                               "original_model_label": assessment.get("original_model_label"),
                               "derived_label": assessment.get("derived_label"),
                               "taxonomy_status": assessment.get("taxonomy", {}).get("technical_status", "not_executed")},
            "phase9_summary": {key: review.get(key) for key in
                               ("technical_status", "route", "review_state", "execution_status",
                                "mandatory", "history_validation", "final_position_id")},
            "review_counts": {"positions": len(review.get("positions", [])),
                              "conflicts": len(review.get("conflicts", [])),
                              "attempts": len(review.get("attempts", [])),
                              "adjudications": len(review.get("adjudications", []))},
            "selected_position_id": selected["position_id"] if selected else None,
            "providers": [{"provider": r.agent_result.provider, "model": r.agent_result.model,
                           "usage": r.agent_result.usage} for r in record.results],
            "recording_notice": "RECORDED OFFLINE / SYNTHETIC; no live model execution"}
    if mode == "recorded_offline":
        return bound  # historical offline provenance, byte-identical
    from agent_arena.phase10_live import ADDENDUM
    bound["config"] = LIVE_CONFIG.get(mode, "invalid-unbound-execution")
    bound["recording_notice"] = LIVE_NOTICES.get(mode, "EXECUTION PROVENANCE INVALID; release blocked")
    bound["contract_addendum"] = ADDENDUM
    bound["execution_mode"] = mode or "invalid"
    bound["execution_mode_errors"] = mode_errors
    carriers = [("primary", r.agent_result.model_dump(mode="json")) for r in record.results]
    carriers += [(p.get("origin"), p.get("agent_result") or {}) for p in review.get("positions", [])
                 if p.get("origin") in {"model_review", "stability", "human_correction"}]
    keys = ("current_execution", "origin", "slot_key", "profile_id", "requested_model", "returned_model",
            "request_id", "message_id", "stop_reason", "completion_state", "attempt_ids", "usage",
            "reserved_microusd", "confirmed_cost_microusd", "billing", "capture_sha256", "authorization_id",
            "latency_ms", "denial_reason", "retry_denied", "replay_capture_verified", "replay_request_identical")
    bound["execution_evidence"] = [
        {"role": role, "provider": c.get("provider"), "model": c.get("model"),
         **{k: (c.get("execution_evidence") or {}).get(k) for k in keys}} for role, c in carriers]
    return bound


def registry_fingerprint(mode: str = "recorded_offline") -> str:
    return digest({"controls": registry_for(mode), "phase7": gates.mandatory_gate_set_fingerprint()})


def control(control_id, subject, ok, reason, *, eligible=1, findings=None,
            execution="executed", not_applicable=False, registry=None):
    return Control(control_id=control_id, version=(registry or REGISTRY)[control_id], subject=subject,
                   execution=execution, outcome=("not_applicable" if not_applicable and ok else
                                                "pass" if ok else "fail"),
                   eligible=eligible, evaluated=eligible if execution == "executed" else 0,
                   findings=findings or [], reason=reason)


def evaluate(record: RunRecord, subject: str, bound_provenance: dict):
    review, selected, assessment, forensic = reconstruct(record)
    errors = preflight(record.task)
    controls = [control("input_preflight", subject, not errors and bool(record.results),
                        "; ".join(errors) or "Input and nonempty execution population checked")]
    populated = forensic is not None and all((forensic.provenance, forensic.evidence,
                                             forensic.findings, forensic.client_findings))
    controls.append(control("analysis_source", subject,
                            bool(populated and assessment.get("technical_status") == "completed"),
                            "Reparsed raw, supplied source spans and nonempty claim/evidence/output traces checked"))
    actual_registry = {s.gate_id: s.gate_version for s in gates.MANDATORY_PHASE7B_GATE_SPECS}
    registry_ok = actual_registry == GATE_VERSIONS and len(gates.MANDATORY_PHASE7B_GATE_SPECS) == 5
    for gate_id in GATE_VERSIONS:
        spec = next((s for s in gates.MANDATORY_PHASE7B_GATE_SPECS if s.gate_id == gate_id), None)
        try:
            if not registry_ok or not forensic or spec is None:
                raise ValueError("Required gate registry or forensic input unavailable")
            count = spec.eligible_count(forensic)
            if type(count) is not int or count < 0:
                raise ValueError("Invalid gate population")
            findings = spec.check(forensic)
            if type(findings) is not list or not all(isinstance(f, gates.BindingFinding) for f in findings):
                raise ValueError("Gate did not return findings")
            required = spec.population == "client_findings"
            ok = bool(populated) and (count > 0 or not required) and not any(
                f.severity in {"critical", "major"} for f in findings)
            controls.append(control(gate_id, subject, ok, f"Evaluated {spec.population}" if count else
                                    f"Host-derived N/A: no {spec.population}; check executed successfully",
                                    eligible=count, findings=[f.model_dump(mode="json") for f in findings],
                                    not_applicable=count == 0 and not required))
        except Exception as exc:
            controls.append(control(gate_id, subject, False, str(exc), eligible=0, execution="error"))
    controls.append(control("phase8_semantics_taxonomy", subject,
                            assessment.get("technical_status") == "completed" and
                            assessment.get("taxonomy", {}).get("technical_status") == "completed",
                            "Current semantic and separate taxonomy analysis required"))
    review_ok = (bool(selected) and review.get("history_validation") != "invalid" and
                 review.get("route") == "AUTO_RESOLVABLE" and review.get("mandatory") is False and
                 (review.get("technical_status") == "completed" or bool(review.get("final_position_id"))))
    controls.append(control("phase9_history_review", subject, review_ok,
                            "All original/review/adjudication carriers and mandatory review revalidated"))
    current = provenance(record, review, selected, forensic, assessment)
    # A doc-only commit does not alter executable bytes. Keep the historical source claim,
    # while requiring the complete installed-code manifest and all material bindings now.
    current["code"]["verified_source_commit"] = bound_provenance.get("code", {}).get("verified_source_commit")
    current["code"]["source_binding"] = bound_provenance.get("code", {}).get("source_binding")
    offline = bool(record.results) and all(
        r.agent_result.model == "offline-recording-no-live-model" and
        r.agent_result.provider == "offline-recording-no-live-model" for r in record.results
    ) and all(p.get("origin") == "human_correction" or
              (p.get("model") == "offline-recording-no-live-model" and
               p.get("provider") == "offline-recording-no-live-model")
              for p in review.get("positions", []))
    mode, mode_errors = bundle_mode(record, review)
    if mode == "recorded_offline":
        controls.append(control("provenance", subject, current == bound_provenance and offline and
                                source_claim_valid(bound_provenance.get("code", {})),
                                "Current code bytes, task/raw/history/selected evidence and offline configuration bound"))
    else:
        # A live or replayed-live bundle passes only with complete bound evidence for every
        # carrier; mixed, relabelled or unbound carriers fail and are listed.
        live_ok = (mode in LIVE_CONFIG and not mode_errors and current == bound_provenance and
                   source_claim_valid(bound_provenance.get("code", {})))
        controls.append(control("provenance", subject, live_ok,
                                "Current code bytes, task/raw/history/selected evidence and live execution evidence bound "
                                "(AA-P10-LIVE/1.0)" if live_ok else
                                "Live execution provenance invalid or stale: " +
                                ("; ".join(mode_errors) or "bound provenance differs from recomputation"),
                                registry=LIVE_REGISTRY,
                                findings=[{"code": "live_provenance", "detail": e} for e in mode_errors]))
    by_id = {c.control_id: c for c in controls}
    if by_id["input_preflight"].outcome == "fail":
        status = "PREFLIGHT_BLOCKED"
    elif all(r.agent_result.error for r in record.results) and not review.get("final_position_id"):
        status = "RUN_FAILED"
    elif any(by_id[n].outcome == "fail" for n in ("analysis_source", "phase8_semantics_taxonomy")):
        status = "ANALYSIS_INCOMPLETE"
    elif not review_ok:
        status = "REVIEW_REQUIRED"
    elif any(c.outcome == "fail" for c in controls):
        status = "RELEASE_BLOCKED"
    else:
        status = "READY_FOR_RELEASE"
    return status, controls, review, selected, assessment, forensic
