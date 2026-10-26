"""Phase-7A guarded REAL model-run driver (WP-5A / WP-5A.0).

This is a **thin real-provider driver** on top of the frozen WP-4 readiness harness
(:mod:`agent_arena.phase7a_execution`). It creates **no second harness** and changes **no**
scientific content. It adds only the smallest pieces genuinely required to run — and to freeze —
the real Haiku batch:

* a real Anthropic provider factory that reuses the frozen :class:`AnthropicProvider` (exact frozen
  transport contract: temperature ``0.0`` · request timeout ``120s`` · ``<=2`` transport retries),
  wrapped by a passive :class:`_CaptureProvider` that records the raw response text + provider-native
  token usage per call **without changing the request**;
* a fail-closed **credential / provider-availability gate** — static presence + non-placeholder;
  provider authentication is authoritative (a first-call ``auth_error`` / ``not_found_error`` aborts
  the batch instead of burning 420 auth failures). The secret value is never returned, printed,
  logged, or written to any artifact;
* replication-level **RAW persistence** (JSONL) with **resume + dedup** (reusing the frozen
  :func:`merge_records`), provider-error preservation, and raw-response capture;
* a **RAW RESULT FREEZE** manifest computed **before** any interpretive analysis;
* **usage aggregation** over provider-native token fields (no invented fields; no monetary-cost
  subsystem — cost is left to a later price-table application);
* a guarded CLI (``--preflight`` / ``--execute-haiku`` / ``--fake-e2e``) that refuses the real batch
  unless the frozen fingerprint gate **and** executable pytest QA **and** the credential gate pass.

Model: ``claude-haiku-4-5-20251001`` only. Execution type: ``independent_model_adjudication``.
Sonnet is excluded here. The real run enforces the mandatory ordering
EXECUTION -> RAW PERSISTENCE -> RAW FREEZE -> RESULT-SET FINGERPRINT -> DETERMINISTIC ANALYSIS.
There is no automatic mechanism that changes gold / prompt / cases / families / thresholds / N from
model outputs.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from agent_arena import phase7a_execution as p7
from agent_arena import preflight_integrity as pi
from agent_arena import resume_integrity as ri
from agent_arena import runtime_contract as rc
from agent_arena import condition_contract as cc
from agent_arena import condition_analysis as ca
from agent_arena import condition_retry as cr
from agent_arena.phase7a_execution import (
    EXEC_TYPE_ADJUDICATION,
    EXEC_TYPE_DRY_RUN,
    EXEC_TYPE_REPRODUCTION,
    N_REPLICATIONS,
    _enrich,
    build_call_plan,
    build_execution_manifest,
    is_calibration_valid,
    is_classification_valid,
    is_terminal_attempt,
    merge_records,
    replication_key,
    resolve_evaluated_units,
)
from agent_arena.providers import BaseProvider, classify_error_type
from agent_arena.providers.anthropic import (
    MAX_TRANSPORT_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
    AnthropicProvider,
)
from agent_arena.run_library import run_single
from agent_arena.schemas import Task

# --- Frozen Haiku-only real-run constants -----------------------------------
HAIKU_MODEL_KEY = "haiku"
HAIKU_MODEL_ID = rc.MODELS[HAIKU_MODEL_KEY]["exact_model_id"]  # claude-haiku-4-5-20251001
LIBRARY_RUN_ID = "phase7a_run_haiku"
DEFAULT_MAX_RESUME_PASSES = cr.PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION

# Known non-usable placeholders. This is a *convenience* reject-list, never the sole validity check:
# provider authentication is authoritative (see check_provider_availability / first-call abort).
KNOWN_PLACEHOLDERS = {
    "", "DEIN_KEY", "YOUR_KEY", "YOUR-KEY", "CHANGEME", "CHANGE_ME", "REPLACE_ME",
    "TODO", "TBD", "XXX", "SK-ANT-...", "SK-ANT-XXX",
}

# Provider-native usage fields we aggregate when the provider returns them (never invented).
USAGE_FIELDS = (
    "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
)

MONETARY_COST_SENTINEL = "MONETARY_COST_NOT_PROVIDER_REPORTED"

# Canonical, repository-relative artifact layout (no machine-specific absolute paths).
# The Haiku-named constants are retained for backward compatibility; each model gets its own
# sibling directory (analysis/phase7a_execution/<model_key>/) so Haiku and Sonnet never overwrite.
OUT_DIR = Path("analysis/phase7a_execution/haiku")
RAW_DIR = OUT_DIR / "raw"
RAW_RECORDS_FILE = RAW_DIR / "haiku_raw_records.jsonl"
FREEZE_FILE = OUT_DIR / "haiku_raw_result_freeze.json"
ANALYSIS_JSON = OUT_DIR / "haiku_deterministic_analysis.json"
ANALYSIS_MD = OUT_DIR / "haiku_deterministic_analysis.md"
USAGE_FILE = OUT_DIR / "haiku_usage_summary.json"

# --- Model registry (both primary Phase-7A conditions; each run is single-model, never pooled) ---
MODEL_KEYS = ("haiku", "sonnet")


def model_id_for(model_key: str) -> str:
    return rc.MODELS[model_key]["exact_model_id"]


def out_dir_for(model_key: str) -> Path:
    return Path(f"analysis/phase7a_execution/{model_key}")


def library_run_id_for(model_key: str) -> str:
    return f"phase7a_run_{model_key}"


# ---------------------------------------------------------------------------
# Credential / provider availability (fail-closed; secret never exposed)
# ---------------------------------------------------------------------------

def credential_status(env: dict | None = None) -> dict:
    """Non-exposing credential status. Returns booleans only — never the secret value/length."""
    env = os.environ if env is None else env
    val = env.get("ANTHROPIC_API_KEY")
    present = bool(val)
    is_placeholder = (val or "").strip() in KNOWN_PLACEHOLDERS
    return {
        "present": present,
        "is_placeholder": is_placeholder,
        "usable_static": present and not is_placeholder,
        "source": "environment",
    }


def check_provider_availability(*, probe: bool = False, client_factory=None,
                                env: dict | None = None) -> dict:
    """Fail-closed provider availability.

    Layer 1 (always): a usable credential must be present (non-empty, not a known placeholder) and the
    ``anthropic`` SDK must import + a client must be constructible.
    Layer 2 (``probe=True`` only): a **non-analytical** auth probe (``client.models.list``) — never a
    Haiku analytical call. Any exception classifies the failure and reports unavailable. Even with
    ``probe=False`` provider auth stays authoritative: the batch aborts on a first-call auth error.
    """
    cred = credential_status(env)
    if not cred["usable_static"]:
        reason = "credential_missing" if not cred["present"] else "credential_placeholder"
        return {"available": False, "reason": reason, "credential": cred,
                "probed": False, "error_type": None}
    try:
        import anthropic  # noqa: F401
    except Exception as e:  # pragma: no cover - SDK is a declared dependency
        return {"available": False, "reason": "sdk_import_failed", "credential": cred,
                "probed": False, "error_type": classify_error_type(e)}
    if not probe:
        return {"available": True, "reason": "static_ok_provider_authoritative_on_first_call",
                "credential": cred, "probed": False, "error_type": None}
    try:
        if client_factory is not None:
            client = client_factory()
        else:  # pragma: no cover - real network path, exercised only with a live credential
            import anthropic
            client = anthropic.Anthropic(timeout=REQUEST_TIMEOUT_SECONDS,
                                         max_retries=MAX_TRANSPORT_RETRIES)
        client.models.list(limit=1)  # authoritative auth check; NOT a Haiku analytical call
        return {"available": True, "reason": "probe_ok", "credential": cred,
                "probed": True, "error_type": None}
    except Exception as e:
        return {"available": False, "reason": "probe_failed", "credential": cred,
                "probed": True, "error_type": classify_error_type(e)}


def check_exact_model_availability(
    model_id: str,
    *,
    client_factory=None,
) -> dict:
    """Use one non-generative metadata lookup to verify the exact dated model ID."""
    if model_id != HAIKU_MODEL_ID:
        return {
            "available": False,
            "reason": "model_outside_phase5b_authorization",
            "requested_model_id": model_id,
            "returned_model_id": None,
            "metadata_operation": "models.retrieve",
            "metadata_http_attempts": 0,
            "model_generations": 0,
            "error_type": None,
        }
    http_client = None
    http_attempts = 0
    try:
        if client_factory is not None:
            client = client_factory()
        else:  # pragma: no cover - live metadata path used only by the authorized run
            import anthropic
            import httpx

            def count_http_attempt(_request) -> None:
                nonlocal http_attempts
                http_attempts += 1

            http_client = httpx.Client(event_hooks={"request": [count_http_attempt]})
            client = anthropic.Anthropic(
                timeout=REQUEST_TIMEOUT_SECONDS,
                max_retries=MAX_TRANSPORT_RETRIES,
                http_client=http_client,
            )
        info = client.models.retrieve(model_id)
        returned_model_id = getattr(info, "id", None)
        available = returned_model_id == model_id
        return {
            "available": available,
            "reason": "exact_model_metadata_match" if available else "model_metadata_mismatch",
            "requested_model_id": model_id,
            "returned_model_id": returned_model_id,
            "metadata_operation": "models.retrieve",
            "metadata_http_attempts": http_attempts,
            "model_generations": 0,
            "error_type": None,
        }
    except Exception as exc:
        return {
            "available": False,
            "reason": "model_metadata_lookup_failed",
            "requested_model_id": model_id,
            "returned_model_id": None,
            "metadata_operation": "models.retrieve",
            "metadata_http_attempts": http_attempts,
            "model_generations": 0,
            "error_type": classify_error_type(exc),
        }
    finally:
        if http_client is not None:
            http_client.close()


class ProviderUnavailable(RuntimeError):
    """Raised to fail closed when no usable credential/provider is available (infra blocker)."""


class CheckpointIntegrityError(ProviderUnavailable):
    """Raised before provider construction when a present checkpoint is not resumable."""

    def __init__(self, report: dict):
        self.report = report
        super().__init__(
            f"checkpoint {report.get('status')} is not resumable: {report.get('errors', [])}"
        )


class ConditionAuthorizationError(ProviderUnavailable):
    """A registered Phase-5A plan/condition was not authorized or did not reproduce."""


class BatchAborted(RuntimeError):
    """Raised on a non-transient provider error (auth/not-found) to abort before burning the batch."""


# ---------------------------------------------------------------------------
# Passive capture provider (delegates unchanged; records raw text + usage)
# ---------------------------------------------------------------------------

class _CaptureProvider(BaseProvider):
    """Wrap a real provider, delegating ``generate`` verbatim (the exact frozen request path) and
    recording, per call and in call order, the raw response text + provider-native usage. It adds
    nothing to the request and alters no parameter."""

    def __init__(self, inner: BaseProvider):
        self._inner = inner
        self.model = getattr(inner, "model", "")
        self.name = getattr(inner, "name", "anthropic")
        self.label = getattr(inner, "label", "") or self.model
        self.captures: list[dict] = []

    def generate(self, task: Task, system_prompt: str):
        resp = self._inner.generate(task, system_prompt)
        text = resp.text or ""
        self.captures.append({
            "task_id": task.id,
            "raw_response": text,
            "raw_response_sha256": rc._sha256_hex(text.encode("utf-8")),
            "usage": resp.usage,
            "finish_reason": resp.finish_reason,
            "error": resp.error,
            "error_type": resp.error_type,
        })
        return resp

    def send_prompt(self, task: Task, system_prompt: str) -> str:  # pragma: no cover - unused path
        return self._inner.send_prompt(task, system_prompt)


def provider_factory_for(model_key: str) -> _CaptureProvider:
    """Real provider for a model key: the frozen AnthropicProvider (exact transport contract) under
    capture. The request path is byte-identical across models — only the model id differs."""
    return _CaptureProvider(AnthropicProvider(model=model_id_for(model_key)))


def haiku_provider_factory() -> _CaptureProvider:
    """Real Haiku provider (frozen AnthropicProvider under capture)."""
    return provider_factory_for("haiku")


def sonnet_provider_factory() -> _CaptureProvider:
    """Real Sonnet 4.5 provider (frozen AnthropicProvider under capture)."""
    return provider_factory_for("sonnet")


# ---------------------------------------------------------------------------
# Raw persistence (JSONL) + resume/dedup helpers
# ---------------------------------------------------------------------------

def _write_jsonl_atomic(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def dedupe_records(records: list[dict]) -> list[dict]:
    """Collapse to one authoritative record per (model, unit_id, run_index) using the frozen
    merge precedence: a completed record wins; duplicate completed is rejected; an errored record is
    replaced by a later completed retry."""
    return merge_records([], records)["records"]


def _completed_keys(records: list[dict]) -> set[tuple]:
    """Legacy-named set of terminal-attempt keys used only for no-semantic-rerun resume."""
    return {replication_key(r) for r in records if is_terminal_attempt(r)}


# ---------------------------------------------------------------------------
# Fingerprints for the raw freeze
# ---------------------------------------------------------------------------

# Analytical content of one replication record (excludes wall-clock/latency/timestamp so the
# fingerprint is deterministic over the science, not the machine timing).
_RECORD_FP_FIELDS = (
    "model", "unit_id", "run_index", "unit_type", "base_case_id", "cluster_root_id", "family_id",
    "gold_label", "unit_fingerprint", "runtime_contract_fingerprint", "package_fingerprint",
    "execution_type", "label", "label_correct", "confidence", "confidence_state",
    "brier_contribution", "parse_ok", "finish_reason", "truncation_suspected", "error", "error_type",
    "raw_response_sha256",
)


def record_fingerprint(rec: dict) -> str:
    return p7._fp({k: rec.get(k) for k in _RECORD_FP_FIELDS})


def aggregate_usage(records: list[dict], *, model_id: str = HAIKU_MODEL_ID) -> dict:
    totals = {f: 0 for f in USAGE_FIELDS}
    present = {f: 0 for f in USAGE_FIELDS}
    n_with_usage = 0
    for r in records:
        u = r.get("usage") or {}
        if u:
            n_with_usage += 1
        for f in USAGE_FIELDS:
            v = u.get(f)
            if isinstance(v, int):
                totals[f] += v
                present[f] += 1
    return {
        "model": model_id,
        "n_records": len(records),
        "n_records_with_usage": n_with_usage,
        "token_totals": totals,
        "fields_present_counts": present,
        "monetary_cost": MONETARY_COST_SENTINEL,
        "note": (
            f"Cost requires applying the provider price table for {model_id} to "
            "input_tokens/output_tokens. cache_* fields are 0/absent: the frozen request sends no "
            "cache_control and the frozen AnthropicProvider surfaces input/output tokens. No dollar "
            "cost is invented here."
        ),
    }


def _git_head(repo_root: Path) -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_root),
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() if out.returncode == 0 else "UNKNOWN"
    except Exception:  # pragma: no cover
        return "UNKNOWN"


def build_raw_freeze(records: list[dict], *, repo_root: Path, dry_run: bool,
                     execution_type: str, model_key: str = "haiku") -> dict:
    """Immutable raw-result freeze binding model/execution/manifest/runtime/package fingerprints, N,
    call accounting, per-record + aggregate result-set fingerprints, usage totals, and provenance.
    Computed BEFORE any interpretive analysis. Single-model; never pooled across models."""
    model_id = model_id_for(model_key)
    units = resolve_evaluated_units(repo_root)
    expected = len(units) * N_REPLICATIONS
    manifest = build_execution_manifest(repo_root)
    plan = build_call_plan(repo_root)
    terminal = [r for r in records if is_terminal_attempt(r)]
    errored = [r for r in records if not is_terminal_attempt(r)]
    classification_valid = [r for r in records if is_classification_valid(r)]
    calibration_valid = [r for r in records if is_calibration_valid(r)]
    completed_keys = _completed_keys(records)
    missing = [
        {"model": model_id, "unit_id": u.unit_id, "run_index": i}
        for u in units for i in range(N_REPLICATIONS)
        if (model_id, u.unit_id, i) not in completed_keys
    ]
    rec_fps = sorted(record_fingerprint(r) for r in records)
    module_src = Path(__file__).read_bytes()
    return {
        "artifact": f"phase7a_{model_key}_raw_result_freeze",
        "freeze_stage": "raw_results_before_analysis",
        "model": model_id,
        "execution_type": execution_type,
        "synthetic_non_analytical": bool(dry_run),
        "n_replications": N_REPLICATIONS,
        "expected_analytical_calls": expected,
        # Historical compatibility only: this field and ``complete`` mean
        # terminal provider coverage, not analytical validity.
        "completed_analytical_calls": len(terminal),
        "provider_failures": len(errored),
        "missing_replication_keys": missing,
        "complete": len(terminal) == expected and not missing,
        "complete_semantics": "LEGACY_TERMINAL_ATTEMPT_COVERAGE_ONLY",
        "expected_calls": expected,
        "terminal_attempts": len(terminal),
        "terminal_attempt_complete": len(terminal) == expected and not missing,
        "classification_valid_calls": len(classification_valid),
        "classification_invalid_calls": len(terminal) - len(classification_valid),
        "classification_unavailable_calls": expected - len(classification_valid),
        "classification_complete": len(classification_valid) == expected,
        "calibration_valid_calls": len(calibration_valid),
        "calibration_invalid_calls": len(terminal) - len(calibration_valid),
        "calibration_unavailable_calls": expected - len(calibration_valid),
        "calibration_complete": len(calibration_valid) == expected,
        "analytical_complete": (
            len(classification_valid) == expected and len(calibration_valid) == expected
        ),
        "analysis_status": (
            "COMPLETE"
            if len(classification_valid) == expected and len(calibration_valid) == expected
            else "PARTIAL_INCOMPLETE"
        ),
        "transport_retries": (
            f"SDK_INTERNAL_NOT_INDIVIDUALLY_OBSERVABLE (<= {MAX_TRANSPORT_RETRIES} per call)"
        ),
        "scientific_manifest_fingerprint": manifest["scientific_manifest_fingerprint"],
        "execution_manifest_fingerprint": manifest["execution_manifest_fingerprint"],
        "call_plan_fingerprint": plan["call_plan_fingerprint"],
        "package_fingerprint": plan["package_fingerprint"],
        "runtime_contract_fingerprint": plan["runtime_contract_fingerprints"][model_id],
        "replication_record_count": len(records),
        "aggregate_result_set_fingerprint": p7._fp(rec_fps),
        "usage_totals": aggregate_usage(records, model_id=model_id),
        "freeze_timestamp": datetime.now(timezone.utc).isoformat(),
        "repository_commit": _git_head(repo_root),
        "harness": {
            "module": "agent_arena.phase7a_real_run",
            "execution_plan_version": p7.EXECUTION_PLAN_VERSION,
            "driver_source_sha256": rc._sha256_hex(module_src),
        },
    }


# ---------------------------------------------------------------------------
# Core replication loop (resume-aware; reuses frozen run_single + _enrich)
# ---------------------------------------------------------------------------

def execute_model_records(model_key, units, provider, *, repo_root: Path | None,
                          existing: list[dict] | None = None,
                          execution_type: str = EXEC_TYPE_ADJUDICATION,
                          dry_run: bool = False,
                          max_passes: int = DEFAULT_MAX_RESUME_PASSES,
                          on_checkpoint=None,
                          resume_contract: dict,
                          condition_arm: dict | None = None,
                          n_replications: int = N_REPLICATIONS) -> list[dict]:
    """Run exactly the missing/not-yet-completed (unit, run_index) slots for one model, N=5.

    Reuses the frozen per-call primitives ``run_single`` + ``_enrich`` (identical to
    :func:`phase7a_execution.execute`'s inner body), adds resume + raw capture. Completed replications
    are never re-run; errored slots are retried across bounded passes. A non-transient provider error
    (auth/not-found) aborts immediately (:class:`BatchAborted`)."""
    model_id = model_id_for(model_key)
    library_run_id = (
        resume_contract["library_run_id"] if condition_arm else library_run_id_for(model_key)
    )
    rt_fp = (
        condition_arm["runtime_contract_fingerprints"][model_id]
        if condition_arm else p7.runtime_contract_fingerprint(model_key, repo_root)
    )
    prompt_version = (
        condition_arm["prompt_version"]
        if condition_arm else cc.STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL
    )
    package_fp = condition_arm["package_fingerprint"] if condition_arm else None
    # ``existing`` has already passed whole-checkpoint validation before provider construction.
    # Recheck the record layer at this lower boundary as defense in depth; never collapse or repair
    # duplicates/ambiguity into apparent validity.
    existing_report = ri.validate_checkpoint_records(list(existing or []), resume_contract, units)
    if not existing_report["valid"]:
        raise ri.ResumeIntegrityError(
            "execute_model_records received invalid resume material: "
            + "; ".join(existing_report["errors"])
        )
    merged = existing_report["records"]
    any_success = any(is_terminal_attempt(r) for r in merged)

    for _pass in range(max_passes):
        done = _completed_keys(merged)
        todo = [(u, i) for u in units for i in range(n_replications)
                if (model_id, u.unit_id, i) not in done]
        if not todo:
            break
        for k, (u, i) in enumerate(todo):
            rec = run_single(
                provider,
                Path(f"{u.unit_id}.yaml"),
                u.task,
                i,
                library_run_id,
                prompt_version=prompt_version,
            )
            enr = _enrich(
                rec,
                u,
                model_id,
                rt_fp,
                dry_run,
                execution_type,
                package_fp=package_fp,
            )
            caps = getattr(provider, "captures", None)
            if caps:
                c = caps[-1]
                enr["raw_response"] = c.get("raw_response")
                enr["raw_response_sha256"] = c.get("raw_response_sha256")
                enr["raw_result_ref"] = "inline:raw_response"
            enr = ri.seal_new_record(enr, u, resume_contract)
            # Fail-closed on a non-transient error before we have any success (bad key / wrong model).
            if not any_success and enr.get("error") and enr.get("error_type") in (
                    "auth_error", "not_found_error"):
                merged = merge_records(merged, [enr])["records"]
                if on_checkpoint:
                    on_checkpoint(merged)
                raise BatchAborted(
                    f"non-transient provider error on first calls: {enr.get('error_type')}")
            merged = merge_records(merged, [enr])["records"]
            if is_terminal_attempt(enr):
                any_success = True
            if on_checkpoint and (k + 1) % 10 == 0:
                on_checkpoint(merged)
        if on_checkpoint:
            on_checkpoint(merged)
    return merged


def build_condition_raw_freeze(
    records: list[dict],
    *,
    document: dict,
    arm: dict,
    model_key: str,
    repo_root: Path,
    dry_run: bool,
    execution_type: str,
) -> dict:
    """Freeze one registered arm without pooling or mutating its immutable specification."""
    specification = document["specification"]
    units = cc.units_for_plan(document, repo_root)
    model_id = model_id_for(model_key)
    n_replications = specification["n_replications"]
    expected = len(units) * n_replications
    terminal = [record for record in records if is_terminal_attempt(record)]
    classification_valid = [record for record in records if is_classification_valid(record)]
    calibration_valid = [record for record in records if is_calibration_valid(record)]
    completed_keys = _completed_keys(records)
    missing = [
        {"model": model_id, "unit_id": unit.unit_id, "run_index": run_index}
        for unit in units
        for run_index in range(n_replications)
        if (model_id, unit.unit_id, run_index) not in completed_keys
    ]
    binding_fields = {
        "plan_id": specification["plan_id"],
        "specification_fingerprint": specification["specification_fingerprint"],
        "arm_id": arm["arm_id"],
        "arm_specification_fingerprint": arm["arm_specification_fingerprint"],
        "analytical_condition_id": arm["analytical_condition_id"],
        "prompt_condition_id": arm["prompt_condition_id"],
        "prompt_version": arm["prompt_version"],
        "system_prompt_sha256": arm["system_prompt_sha256"],
        "package_fingerprint": arm["package_fingerprint"],
        "runtime_contract_fingerprint": arm["runtime_contract_fingerprints"][model_id],
        "execution_manifest_fingerprint": arm["execution_manifest"][
            "execution_manifest_fingerprint"
        ],
        "call_plan_fingerprint": arm["call_plan"]["call_plan_fingerprint"],
    }
    for index, record in enumerate(records):
        for field, expected_value in binding_fields.items():
            if record.get(field) != expected_value:
                raise ri.ResumeIntegrityError(
                    f"condition freeze record {index} binding mismatch: {field}"
                )
    rec_fps = sorted(record_fingerprint(record) for record in records)
    return {
        "artifact_schema_version": "agent_arena.condition_raw_freeze/v1",
        "artifact_role": "diagnostic_validation_raw_freeze",
        **binding_fields,
        "model": model_id,
        "execution_type": execution_type,
        "synthetic_non_analytical": bool(dry_run),
        "n_independent_units": len(units),
        "n_replications": n_replications,
        "expected_calls": expected,
        "terminal_attempts": len(terminal),
        "missing_replication_keys": missing,
        "terminal_attempt_complete": len(terminal) == expected and not missing,
        "classification_valid_calls": len(classification_valid),
        "classification_complete": len(classification_valid) == expected,
        "calibration_valid_calls": len(calibration_valid),
        "calibration_complete": len(calibration_valid) == expected,
        "analytical_complete": (
            len(classification_valid) == expected and len(calibration_valid) == expected
        ),
        "analysis_status": (
            "COMPLETE"
            if len(classification_valid) == expected and len(calibration_valid) == expected
            else "PARTIAL_INCOMPLETE"
        ),
        "replication_record_count": len(records),
        "aggregate_result_set_fingerprint": p7._fp(rec_fps),
        "usage_totals": aggregate_usage(records, model_id=model_id),
        "repository_commit": _git_head(repo_root),
        "freeze_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def build_condition_analysis(
    records: list[dict],
    *,
    document: dict,
    arm: dict,
    model_key: str,
    dry_run: bool,
) -> dict:
    """Build the fixed three-vote single-arm analysis with explicit denominators."""
    specification = document["specification"]
    expected = {
        "plan_id": specification["plan_id"],
        "specification_fingerprint": specification["specification_fingerprint"],
        "arm_id": arm["arm_id"],
        "arm_specification_fingerprint": arm["arm_specification_fingerprint"],
        "analytical_condition_id": arm["analytical_condition_id"],
        "prompt_condition_id": arm["prompt_condition_id"],
    }
    for index, record in enumerate(records):
        for field, value in expected.items():
            if record.get(field) != value:
                raise ri.ResumeIntegrityError(
                    f"condition analysis record {index} binding mismatch: {field}"
                )
    report = ca.build_arm_model_analysis(
        records,
        ordered_unit_bindings=specification["ordered_unit_bindings"],
        unit_strata=specification["unit_strata"],
        analysis_contract=specification["analysis_contract"],
        model=model_id_for(model_key),
        arm_id=arm["arm_id"],
    )
    return {
        "analysis_schema_version": ca.ARM_ANALYSIS_SCHEMA_VERSION,
        "artifact_role": "diagnostic_validation_analysis",
        **expected,
        "model": model_id_for(model_key),
        "analysis_contract_fingerprint": specification["analysis_contract_fingerprint"],
        "classification_unit_denominators": {
            name: population["expected_units"]
            for name, population in report["populations"].items()
        },
        "response_level_denominators": {
            name: population["response_slot_accounting"]["expected_response_slots"]
            for name, population in report["populations"].items()
        },
        "analysis_status": (
            "CLASSIFICATION_COMPLETE"
            if report["classification_complete"]
            else "INCOMPLETE_CLASSIFICATION"
        ),
        "classification_complete": report["classification_complete"],
        "calibration_complete": report["calibration_complete"],
        "transport_missingness_complete": report["transport_missingness_complete"],
        "synthetic_non_analytical": bool(dry_run),
        "report": report,
    }


def build_condition_comparison(analyses: list[dict], *, document: dict) -> dict:
    """Build the paired four-batch verdict after rejecting provenance ambiguity."""
    specification = document["specification"]
    for index, analysis in enumerate(analyses):
        if analysis.get("specification_fingerprint") != specification["specification_fingerprint"]:
            raise ri.ResumeIntegrityError(
                f"condition comparison analysis {index} specification mismatch"
            )
        if analysis.get("analysis_contract_fingerprint") != specification[
            "analysis_contract_fingerprint"
        ]:
            raise ri.ResumeIntegrityError(
                f"condition comparison analysis {index} analysis-contract mismatch"
            )
    paired = ca.build_paired_analysis(
        [analysis["report"] for analysis in analyses],
        model_ids=specification["model_ids"],
        historical_arm_id=cc.HISTORICAL_ARM_ID,
        prospective_arm_id=cc.PROSPECTIVE_ARM_ID,
    )
    return {
        "analysis_schema_version": ca.PAIRED_ANALYSIS_SCHEMA_VERSION,
        "artifact_role": "diagnostic_validation_paired_analysis",
        "plan_id": specification["plan_id"],
        "specification_fingerprint": specification["specification_fingerprint"],
        "analysis_contract_fingerprint": specification["analysis_contract_fingerprint"],
        "paired": paired,
    }


def _run_registered_condition(
    plan_id: str,
    arm_id: str,
    model_key: str,
    *,
    repo_root: str | Path | None = None,
    _synthetic_test: bool = False,
    _plan_resolver=cc.resolve_registered_plan,
    _source_inspector=pi.inspect_source_state,
    _qa_executor=pi.execute_condition_contract_qa,
    _qa_validator=pi.validate_condition_contract_qa_record,
    _credential_checker=check_provider_availability,
    _provider_builder=provider_factory_for,
    _output_dir: str | Path | None = None,
) -> dict:
    """Internal condition-aware adapter around the existing guarded machinery.

    Production callers cannot inject any dependency: :func:`run_registered_condition`
    exposes identifiers only.  The private seams mirror the established Phase-2/3
    deterministic test pattern and are accepted solely with synthetic authorization.
    """
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]

    # 1. Trusted identifier lookup and immutable schema/specification validation.
    document = _plan_resolver(plan_id, root)
    arm = cc.resolve_arm(document, arm_id)
    if model_key not in document["specification"]["model_keys"]:
        raise ConditionAuthorizationError("model is outside the registered plan")
    target = Path(_output_dir).resolve() if _synthetic_test and _output_dir else (
        root / arm["artifact_namespace"] / model_key
    ).resolve()
    one_shot = bool(document["specification"].get("one_shot_execution"))
    if one_shot and (target / document["specification"]["execution_lease_filename"]).exists():
        raise ConditionAuthorizationError(
            "one-shot execution authorization already consumed; second invocation prohibited"
        )

    # 2. Authorization is separate from specification/progress. Caller booleans do not exist.
    if _synthetic_test:
        errors = cc.validate_plan_document(document, root, _allow_synthetic_test=True)
        authorization = document.get("authorization") or {}
        if authorization.get("status") != cc.AUTH_SYNTHETIC_TEST:
            errors.append("private synthetic execution lacks synthetic-only authorization")
        if authorization.get("authorization_source") != "private_test_seam":
            errors.append("private synthetic authorization source mismatch")
    else:
        errors = cc.production_authorization_errors(document, root)
    if errors:
        raise ConditionAuthorizationError("; ".join(errors))

    cost_gate = None
    if document["specification"].get("analysis_mode") == (
        "full_historical_reference_replication"
    ) and not _synthetic_test:
        from agent_arena import full_replication_contract as frc

        cost_gate = frc.validate_cost_gate(document, root)

    # 3. Authenticate source/environment before any QA, credential, or provider work.
    source_before = _source_inspector(root)
    if not source_before.get("valid"):
        raise ConditionAuthorizationError(
            "condition source state invalid: " + "; ".join(source_before.get("errors") or [])
        )

    # 4. The tracked plan artifact and every derived prompt/package/runtime/manifest binding.
    binding_errors = cc.verify_arm_bindings(
        document, arm, model_key, root, _allow_synthetic_test=_synthetic_test
    )
    if binding_errors:
        raise ConditionAuthorizationError("; ".join(binding_errors))

    # 5-6. Fresh internally selected, non-caller-selectable condition-contract QA.
    full_replication = document["specification"].get("analysis_mode") == (
        "full_historical_reference_replication"
    )
    if full_replication and not _synthetic_test:
        qa = pi.execute_full_replication_qa(root, source_before)
        qa_status, qa_errors = pi.validate_full_replication_qa_record(qa, source_before)
    else:
        qa = _qa_executor(root, source_before)
        qa_status, qa_errors = _qa_validator(qa, source_before)
    if qa_status != pi.QA_PASSED or qa_errors:
        raise ConditionAuthorizationError(
            f"condition canonical QA did not authorize execution: {qa_status}: {qa_errors}"
        )

    # 7. Runtime identity and credentials; no provider construction yet.
    runtime = arm["runtime_contracts"][model_key]
    expected_runtime = cc.condition_runtime_contract(model_key, arm["prompt_version"], root)
    if runtime != expected_runtime:
        raise ConditionAuthorizationError("condition runtime contract does not reproduce")
    availability = _credential_checker()
    if not availability.get("available"):
        raise ConditionAuthorizationError(
            f"provider unavailable ({availability.get('reason')}): no provider constructed"
        )
    model_availability = None
    if full_replication and not _synthetic_test:
        model_availability = check_exact_model_availability(model_id_for(model_key))
        if not model_availability.get("available"):
            raise ConditionAuthorizationError(
                "exact Haiku model unavailable "
                f"({model_availability.get('reason')}): no generation provider constructed"
            )

    # 8-9. Authenticate the complete condition checkpoint and missing slot universe.
    units = cc.units_for_plan(document, root)
    raw_file = target / "raw" / f"{model_key}_raw_records.jsonl"
    checkpoint_file = target / "raw" / f"{model_key}_checkpoint_manifest.json"
    resume_contract = ri.build_condition_resume_contract(
        document,
        arm,
        model_key,
        units,
        root,
        execution_type=EXEC_TYPE_DRY_RUN if _synthetic_test else EXEC_TYPE_ADJUDICATION,
        dry_run=_synthetic_test,
        source_binding=source_before,
        checkpoint_root=target,
    )
    resume_validation = ri.validate_resume_checkpoint(
        raw_file, checkpoint_file, resume_contract, units
    )
    if not resume_validation["valid"]:
        raise CheckpointIntegrityError(resume_validation)
    existing = resume_validation["records"]

    # 10. Revalidate both tested source and the registered artifact/specification.
    source_after = _source_inspector(root)
    source_errors = pi.compare_source_binding(source_before, source_after)
    if source_errors:
        raise ConditionAuthorizationError("; ".join(source_errors))
    refreshed = _plan_resolver(plan_id, root)
    if refreshed["specification"] != document["specification"]:
        raise ConditionAuthorizationError("registered specification changed after QA")
    refreshed_arm = cc.resolve_arm(refreshed, arm_id)
    if refreshed_arm != arm:
        raise ConditionAuthorizationError("registered condition changed after QA")

    one_shot_lease = None
    if one_shot:
        from agent_arena import full_replication_contract as frc

        one_shot_lease = frc.claim_one_shot_lease(
            target,
            document,
            arm,
            model_key,
            source_after,
            synthetic=_synthetic_test,
        )
        target.mkdir(parents=True, exist_ok=True)
        preflight_evidence = {
            "preflight_evidence_schema_version": (
                "agent_arena.full_replication_preflight_evidence/v1"
            ),
            "plan_id": plan_id,
            "specification_fingerprint": document["specification"][
                "specification_fingerprint"
            ],
            "arm_id": arm_id,
            "model_key": model_key,
            "model_id": model_id_for(model_key),
            "source_before": source_before,
            "source_after": source_after,
            "canonical_qa": qa,
            "canonical_qa_status": qa_status,
            "canonical_qa_errors": qa_errors,
            "credential_state": availability,
            "exact_model_availability": model_availability,
            "cost_gate": cost_gate,
            "one_shot_lease": one_shot_lease["record"],
            "provider_constructed_at_record_time": False,
        }
        preflight_evidence["preflight_evidence_fingerprint"] = p7._fp(
            preflight_evidence
        )
        (target / "preflight_evidence.json").write_text(
            json.dumps(preflight_evidence, indent=2, ensure_ascii=False) + "\n"
        )

    def checkpoint(records: list[dict]) -> None:
        ri.write_resume_checkpoint(raw_file, checkpoint_file, records, resume_contract, units)

    # 11-12. First provider construction, then request construction from authenticated prompt.
    provider = _provider_builder(model_key)
    batch_abort = None
    try:
        records = execute_model_records(
            model_key,
            units,
            provider,
            repo_root=root,
            existing=existing,
            execution_type=EXEC_TYPE_DRY_RUN if _synthetic_test else EXEC_TYPE_ADJUDICATION,
            dry_run=_synthetic_test,
            on_checkpoint=checkpoint,
            resume_contract=resume_contract,
            condition_arm=arm,
            n_replications=document["specification"]["n_replications"],
            max_passes=document["specification"].get(
                "outer_provider_error_passes_per_guarded_invocation",
                DEFAULT_MAX_RESUME_PASSES,
            ),
        )
    except BatchAborted as exc:
        # The one-shot lease is already consumed. Preserve the authenticated
        # nonterminal record and continue only through deterministic freezing.
        batch_abort = str(exc)
        aborted_checkpoint = ri.validate_resume_checkpoint(
            raw_file,
            checkpoint_file,
            resume_contract,
            units,
        )
        if not aborted_checkpoint["valid"]:
            raise CheckpointIntegrityError(aborted_checkpoint) from exc
        records = aborted_checkpoint["records"]
    records = sorted(records, key=replication_key)
    checkpoint(records)

    freeze = build_condition_raw_freeze(
        records,
        document=document,
        arm=arm,
        model_key=model_key,
        repo_root=root,
        dry_run=_synthetic_test,
        execution_type=EXEC_TYPE_DRY_RUN if _synthetic_test else EXEC_TYPE_ADJUDICATION,
    )
    comparison = None
    usage_cost = None
    if document["specification"].get("analysis_mode") == (
        "full_historical_reference_replication"
    ):
        from agent_arena import full_replication_analysis as fra

        historical_path = root / document["specification"]["historical_reference"][
            "raw_records_path"
        ]
        historical_records = _load_jsonl(historical_path)
        comparison = fra.build_comparison(
            historical_records,
            records,
            document=document,
            historical_raw_path=historical_path,
            prospective_raw_path=raw_file,
        )
        analysis = {
            "analysis_schema_version": fra.ANALYSIS_SCHEMA_VERSION,
            "artifact_role": "diagnostic_full_replication_analysis",
            "plan_id": document["specification"]["plan_id"],
            "specification_fingerprint": document["specification"][
                "specification_fingerprint"
            ],
            "arm_id": arm["arm_id"],
            "model": model_id_for(model_key),
            "bound_raw_freeze_fingerprint": freeze[
                "aggregate_result_set_fingerprint"
            ],
            "report": comparison["prospective"],
        }
        analysis["analysis_artifact_fingerprint"] = p7._fp(analysis)
        pricing = document["specification"]["pricing_contract"]
        usage_cost = fra.build_usage_cost(
            records,
            input_price=pricing["input_usd_per_million_tokens"],
            output_price=pricing["output_usd_per_million_tokens"],
        )
    else:
        analysis = build_condition_analysis(
            records,
            document=document,
            arm=arm,
            model_key=model_key,
            dry_run=_synthetic_test,
        )
    target.mkdir(parents=True, exist_ok=True)
    (target / f"{model_key}_raw_result_freeze.json").write_text(
        json.dumps(freeze, indent=2, ensure_ascii=False) + "\n"
    )
    (target / f"{model_key}_condition_analysis.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False) + "\n"
    )
    if comparison is not None:
        from agent_arena import full_replication_analysis as fra

        (target / f"{model_key}_historical_comparison.json").write_text(
            json.dumps(comparison, indent=2, ensure_ascii=False) + "\n"
        )
        (target / f"{model_key}_historical_comparison.md").write_text(
            fra.render_comparison_markdown(comparison)
        )
        (target / f"{model_key}_usage_cost.json").write_text(
            json.dumps(usage_cost, indent=2, ensure_ascii=False) + "\n"
        )
        execution_evidence = {
            "execution_evidence_schema_version": (
                "agent_arena.full_replication_execution_evidence/v1"
            ),
            "plan_id": plan_id,
            "specification_fingerprint": document["specification"][
                "specification_fingerprint"
            ],
            "provider_construction_counts": {
                "haiku": 1 if model_key == "haiku" else 0,
                "sonnet": 1 if model_key == "sonnet" else 0,
                "unapproved_conditions": 0,
            },
            "one_shot_lease": one_shot_lease["record"] if one_shot_lease else None,
            "planned_slots": document["specification"]["expected_calls_total"],
            "observed_records": len(records),
            "terminal_attempts": freeze["terminal_attempts"],
            "classification_valid_calls": freeze["classification_valid_calls"],
            "calibration_valid_calls": freeze["calibration_valid_calls"],
            "analysis_status": freeze["analysis_status"],
            "usage_cost_fingerprint": usage_cost["usage_cost_fingerprint"],
            "comparison_fingerprint": comparison["comparison_fingerprint"],
            "official_release_writes": 0,
            "manual_restarts": 0,
            "batch_abort": batch_abort,
        }
        execution_evidence["execution_evidence_fingerprint"] = p7._fp(
            execution_evidence
        )
        (target / "execution_evidence.json").write_text(
            json.dumps(execution_evidence, indent=2, ensure_ascii=False) + "\n"
        )
    return {
        "go": True,
        "plan_id": plan_id,
        "specification_fingerprint": document["specification"]["specification_fingerprint"],
        "arm_id": arm_id,
        "analytical_condition_id": arm["analytical_condition_id"],
        "model": model_id_for(model_key),
        "qa": qa,
        "availability": availability,
        "records": records,
        "checkpoint_validation": resume_validation,
        "freeze": freeze,
        "analysis": analysis,
        "comparison": comparison,
        "usage_cost": usage_cost,
        "one_shot_lease": one_shot_lease,
        "batch_abort": batch_abort,
    }


def run_registered_condition(
    plan_id: str,
    arm_id: str,
    model_key: str,
    *,
    repo_root: str | Path | None = None,
) -> dict:
    """Production API: registered identifiers only; no caller-controlled execution material."""
    return _run_registered_condition(plan_id, arm_id, model_key, repo_root=repo_root)


# ---------------------------------------------------------------------------
# Guarded batch entrypoint (preflight gate -> execute -> raw freeze -> analysis)
# ---------------------------------------------------------------------------

def run_model_batch(model_key: str, *, repo_root: str | Path | None = None, provider_factory=None,
                    run_qa: bool = True, qa_record: dict | None = None,
                    out_dir: str | Path | None = None,
                    dry_run: bool = False, execution_type: str | None = None,
                    max_passes: int = DEFAULT_MAX_RESUME_PASSES) -> dict:
    """The one guarded real-run entrypoint, parameterized by ``model_key`` ('haiku' | 'sonnet').

    A real adjudication refuses caller-supplied QA, caller-selected QA scope, and caller-supplied
    provider factories. It constructs the real provider only after required artifacts, runtime
    contracts, fresh canonical QA, exact source binding, credentials, and post-QA source
    revalidation pass. Diagnostic dry runs retain an explicitly non-authorizing injection seam.

    Then it enforces EXECUTION -> RAW PERSISTENCE -> RAW FREEZE -> DETERMINISTIC ANALYSIS.
    Single-model: it runs only ``model_key`` and writes only that model's directory; the other model's
    frozen artifacts are never touched. Tests may inject ``provider_factory`` and diagnostic QA only
    for dry-run/non-adjudication execution with 0 real calls."""
    if model_key not in MODEL_KEYS:
        raise ValueError(f"model_key must be one of {MODEL_KEYS}")
    model_id = model_id_for(model_key)
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    if execution_type is None:
        execution_type = EXEC_TYPE_DRY_RUN if dry_run else EXEC_TYPE_ADJUDICATION
    if dry_run != (execution_type == EXEC_TYPE_DRY_RUN):
        raise ProviderUnavailable("dry_run and execution_type provenance are inconsistent")
    if execution_type == EXEC_TYPE_REPRODUCTION:
        raise ProviderUnavailable("deterministic reproduction cannot construct a model provider")
    real_adjudication = execution_type == EXEC_TYPE_ADJUDICATION and not dry_run
    if real_adjudication:
        if provider_factory is not None:
            raise ProviderUnavailable(
                "caller-supplied provider factory is prohibited for real adjudication"
            )
        if not run_qa or qa_record is not None:
            raise ProviderUnavailable(
                "real adjudication requires fresh internally selected canonical QA"
            )
        expected_origin = root / "src/agent_arena/phase7a_real_run.py"
        if Path(__file__).resolve() != expected_origin.resolve():
            raise ProviderUnavailable("real-run module import origin differs from repository root")
    target = Path(out_dir) if out_dir else (root / out_dir_for(model_key))
    raw_file = target / "raw" / f"{model_key}_raw_records.jsonl"
    checkpoint_file = target / "raw" / f"{model_key}_checkpoint_manifest.json"
    freeze_file = target / f"{model_key}_raw_result_freeze.json"
    analysis_json = target / f"{model_key}_deterministic_analysis.json"
    analysis_md = target / f"{model_key}_deterministic_analysis.md"
    usage_file = target / f"{model_key}_usage_summary.json"

    # --- Gate 1+2: authenticated source + frozen artifacts + fresh canonical QA ---
    if real_adjudication:
        pf = p7.real_run_preflight(root)
    else:
        pf = p7.diagnostic_preflight(root, run_qa=run_qa, qa_record=qa_record)
    if not pf["go"]:
        raise ProviderUnavailable(
            f"preflight NO-GO (gate_passes={pf['gate_passes']} qa_status={pf['qa_status']}): "
            f"{pf['gate_errors']} {pf.get('qa_errors', [])}")

    # --- Gate 3: exact model / N / universe (explicit, redundant with the gate) ---
    units = resolve_evaluated_units(root)
    expected_ids = {"haiku": "claude-haiku-4-5-20251001", "sonnet": "claude-sonnet-4-5-20250929"}
    if model_id != expected_ids[model_key]:
        raise ProviderUnavailable(f"unexpected {model_key} model id: {model_id}")
    if not rc.is_executable(rc.build_contract(model_key, root)):
        raise ProviderUnavailable(f"{model_key} runtime contract not executable")
    if N_REPLICATIONS != 5 or len(units) != 84:
        raise ProviderUnavailable(f"universe drift: N={N_REPLICATIONS} units={len(units)}")

    # --- Gate 4: authenticate the entire checkpoint before any provider construction ---
    source_binding = pf.get("source_binding")
    resume_contract = ri.build_resume_contract(
        model_key,
        units,
        root,
        execution_type=execution_type,
        dry_run=dry_run,
        source_binding=source_binding if isinstance(source_binding, dict) else None,
        checkpoint_root=target,
    )
    resume_validation = ri.validate_resume_checkpoint(
        raw_file, checkpoint_file, resume_contract, units
    )
    if not resume_validation["valid"]:
        raise CheckpointIntegrityError(resume_validation)
    existing = resume_validation["records"]
    provider_calls_required = resume_validation["accounting"]["provider_calls_required"]

    # --- Gate 5: credential/provider availability (real path only; no construction) ---
    availability = None
    if real_adjudication:
        availability = check_provider_availability()
        if not availability["available"]:
            raise ProviderUnavailable(
                f"provider unavailable ({availability['reason']}): no real {model_key} call made")
        pf["credential_state"] = availability

        # --- Gate 6: exact tested source still equals the source about to execute ---
        source_check = pi.verify_source_binding(pf["source_binding"])
        if not source_check["matches"]:
            raise ProviderUnavailable(
                f"tested source changed before provider construction: {source_check['errors']}"
            )
        if Path(__file__).resolve() != (root / "src/agent_arena/phase7a_real_run.py").resolve():
            raise ProviderUnavailable("real-run module origin changed before provider construction")
        provider_factory = lambda: provider_factory_for(model_key)  # noqa: E731
    elif provider_factory is None:
        raise ProviderUnavailable("non-production execution requires an explicit offline provider")

    # First provider construction occurs only after complete authorization and checkpoint
    # authentication. A fully reusable checkpoint needs no provider object at all.
    def checkpoint(recs: list[dict]) -> None:
        ri.write_resume_checkpoint(
            raw_file, checkpoint_file, recs, resume_contract, units
        )

    initial_terminal_keys = _completed_keys(existing)
    if provider_calls_required:
        provider = provider_factory()
        records = execute_model_records(
            model_key, units, provider, repo_root=root, existing=existing,
            execution_type=execution_type, dry_run=dry_run, max_passes=max_passes,
            on_checkpoint=checkpoint, resume_contract=resume_contract)
    else:
        records = list(existing)
    records = sorted(records, key=replication_key)
    checkpoint(records)

    final_terminal_keys = _completed_keys(records)
    final_classification = sum(1 for record in records if is_classification_valid(record))
    final_calibration = sum(1 for record in records if is_calibration_valid(record))
    resume_accounting = {
        "checkpoint_status": resume_validation["status"],
        "expected_slots": resume_contract["expected_slots"],
        "records_loaded": resume_validation["accounting"]["records_loaded"],
        "resume_eligible_terminal_records": resume_validation["accounting"][
            "resume_eligible_terminal_records"
        ],
        "authenticated_nonterminal_records": resume_validation["accounting"][
            "authenticated_nonterminal_records"
        ],
        "legitimately_missing_slots": resume_validation["accounting"][
            "legitimately_absent_slots"
        ],
        "invalid_records": resume_validation["invalid_records"],
        "duplicate_slots": resume_validation["duplicate_slots"],
        "conflicting_slots": resume_validation["conflicting_slots"],
        "unexpected_slots": resume_validation["unexpected_slots"],
        "provider_calls_required": provider_calls_required,
        "new_calls_completed": len(final_terminal_keys - initial_terminal_keys),
        "final_terminal_coverage": len(final_terminal_keys),
        "final_classification_valid_count": final_classification,
        "final_calibration_valid_count": final_calibration,
        "final_analytical_complete": (
            final_classification == final_calibration == resume_contract["expected_slots"]
        ),
    }

    # --- RAW FREEZE (before any analysis) ---
    freeze = build_raw_freeze(records, repo_root=root, dry_run=dry_run,
                              execution_type=execution_type, model_key=model_key)
    freeze["resume_checkpoint"] = {
        "checkpoint_schema_version": ri.CHECKPOINT_SCHEMA_VERSION,
        "checkpoint_id": resume_contract["checkpoint_id"],
        "checkpoint_contract_fingerprint": resume_contract[
            "checkpoint_contract_fingerprint"
        ],
        "checkpoint_file": str(checkpoint_file),
        "accounting": resume_accounting,
    }
    target.mkdir(parents=True, exist_ok=True)
    freeze_file.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n")

    # --- USAGE (persist alongside the freeze; no cost invented) ---
    usage = aggregate_usage(records, model_id=model_id)
    usage_file.write_text(json.dumps(usage, indent=2, ensure_ascii=False) + "\n")

    # --- DETERMINISTIC ANALYSIS (only after the raw freeze exists) ---
    analysis = None
    if freeze["terminal_attempt_complete"]:
        report = p7.build_phase7a_report(
            records, dry_run=dry_run, expected_units=len(units),
            expected_calls_per_model=freeze["expected_calls"],
        )
        analysis = {
            "phase": "7A",
            "model": model_id,
            "execution_type": execution_type,
            "synthetic_non_analytical": bool(dry_run),
            "bound_raw_freeze": {
                "aggregate_result_set_fingerprint": freeze["aggregate_result_set_fingerprint"],
                "completed_analytical_calls": freeze["completed_analytical_calls"],
                "terminal_attempt_complete": freeze["terminal_attempt_complete"],
                "classification_valid_calls": freeze["classification_valid_calls"],
                "calibration_valid_calls": freeze["calibration_valid_calls"],
                "analytical_complete": freeze["analytical_complete"],
            },
            "analysis_status": report["analysis_status"],
            "report": report,
        }
        analysis_json.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n")
        analysis_md.write_text(p7.render_report_md(report))

    return {
        "go": True,
        "model": model_id,
        "preflight": pf,
        "availability": availability,
        "records": records,
        "raw_file": str(raw_file),
        "checkpoint_file": str(checkpoint_file),
        "checkpoint_validation": resume_validation,
        "resume_accounting": resume_accounting,
        "freeze_file": str(freeze_file),
        "freeze": freeze,
        "usage_file": str(usage_file),
        "analysis_file": str(analysis_json) if analysis else None,
        "analysis": analysis,
        "complete": freeze["complete"],
        "terminal_attempt_complete": freeze["terminal_attempt_complete"],
        "classification_complete": freeze["classification_complete"],
        "calibration_complete": freeze["calibration_complete"],
        "analytical_complete": freeze["analytical_complete"],
    }


def run_haiku_batch(**kwargs) -> dict:
    """Guarded real Haiku batch (claude-haiku-4-5-20251001)."""
    return run_model_batch("haiku", **kwargs)


def run_sonnet_batch(**kwargs) -> dict:
    """Guarded real Sonnet 4.5 batch (claude-sonnet-4-5-20250929); never conditioned on Haiku."""
    return run_model_batch("sonnet", **kwargs)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_preflight(root: Path, *, probe: bool) -> int:
    pf = p7.real_run_preflight(root)
    avail = check_provider_availability(probe=probe)
    qa = pf["qa"] or {}
    go = bool(pf["go"] and avail["available"])
    print(f"real Haiku preflight: {'GO' if go else 'NO-GO'} | gate="
          f"{'PASS' if pf['gate_passes'] else 'FAIL'} | qa={pf['qa_status']} | "
          f"credential={'USABLE' if avail['available'] else avail['reason']}")
    if qa:
        print(f"  QA: exit={qa.get('exit_code')} collected={qa.get('tests_collected')} "
              f"passed={qa.get('tests_passed')} failed={qa.get('tests_failed')} "
              f"skipped={qa.get('tests_skipped')} fp={(pf.get('qa_record_fingerprint') or '')[:16]}")
    for e in pf["gate_errors"]:
        print(f"  - {e}")
    return 0 if go else 2


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="agent_arena.phase7a_real_run",
        description="Guarded Phase-7A REAL run driver (single-model: haiku | sonnet; never pooled).",
    )
    p.add_argument("--preflight", action="store_true",
                   help="Fingerprint gate + real pytest QA + credential/provider check. 0 model calls.")
    p.add_argument("--probe", action="store_true",
                   help="With --preflight, also run a non-analytical provider auth probe (models.list).")
    p.add_argument("--execute-haiku", action="store_true",
                   help="Run the guarded REAL 420-call Haiku batch, then raw-freeze -> analysis. "
                        "Makes REAL model calls.")
    p.add_argument("--execute-sonnet", action="store_true",
                   help="Run the guarded REAL 420-call Sonnet 4.5 batch, then raw-freeze -> analysis. "
                        "Makes REAL model calls. Never conditioned on Haiku.")
    p.add_argument("--fake-e2e", action="store_true",
                   help="Full SYNTHETIC 84x5=420 end-to-end (fake provider, no network) for --model "
                        "to an isolated --out-dir. Never mixed with real results.")
    p.add_argument("--model", choices=MODEL_KEYS, default="haiku",
                   help="Model key for --fake-e2e (default: haiku).")
    p.add_argument("--out-dir", default=None, help="Override output dir (fake-e2e uses a scratch dir).")
    args = p.parse_args(argv)
    root = Path(__file__).resolve().parents[2]

    if args.preflight:
        return _print_preflight(root, probe=args.probe)

    if args.fake_e2e:
        from agent_arena.run_library import FakeLibraryProvider
        mk = args.model
        out = args.out_dir or f"/tmp/phase7a_{mk}_fake_e2e"
        res = run_model_batch(mk, repo_root=root, provider_factory=lambda: _CaptureProvider(
            FakeLibraryProvider(model=model_id_for(mk))), run_qa=False, qa_record={
                "qa_kind": "pytest_execution", "exit_code": 0, "tests_collected": 1,
                "tests_passed": 1, "tests_failed": 0, "tests_errors": 0,
                "qa_record_fingerprint": "fake"}, out_dir=out,
            dry_run=True, execution_type=EXEC_TYPE_DRY_RUN)
        f = res["freeze"]
        print(f"FAKE E2E [{mk}] (SYNTHETIC / NON-ANALYTICAL): records={f['replication_record_count']} "
              f"completed={f['completed_analytical_calls']} expected={f['expected_analytical_calls']} "
              f"complete={f['complete']} out={out}")
        return 0

    if args.execute_haiku or args.execute_sonnet:
        mk = "sonnet" if args.execute_sonnet else "haiku"
        res = run_model_batch(mk, repo_root=root)  # real provider, real QA, real credential
        f = res["freeze"]
        print(f"REAL {mk.upper()} BATCH: completed={f['completed_analytical_calls']}/"
              f"{f['expected_analytical_calls']} provider_failures={f['provider_failures']} "
              f"complete={f['complete']}")
        print(f"  raw:      {res['raw_file']}")
        print(f"  freeze:   {res['freeze_file']}")
        print(f"  analysis: {res['analysis_file']}")
        return 0 if res["analytical_complete"] else 3

    p.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
