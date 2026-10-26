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
from agent_arena import runtime_contract as rc
from agent_arena.phase7a_execution import (
    EXEC_TYPE_ADJUDICATION,
    EXEC_TYPE_DRY_RUN,
    N_REPLICATIONS,
    _enrich,
    build_call_plan,
    build_execution_manifest,
    is_completed,
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
DEFAULT_MAX_RESUME_PASSES = 3

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


class ProviderUnavailable(RuntimeError):
    """Raised to fail closed when no usable credential/provider is available (infra blocker)."""


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
    return {replication_key(r) for r in records if is_completed(r)}


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
    completed = [r for r in records if is_completed(r)]
    errored = [r for r in records if not is_completed(r)]
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
        "completed_analytical_calls": len(completed),
        "provider_failures": len(errored),
        "missing_replication_keys": missing,
        "complete": len(completed) == expected and not missing,
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
                          on_checkpoint=None) -> list[dict]:
    """Run exactly the missing/not-yet-completed (unit, run_index) slots for one model, N=5.

    Reuses the frozen per-call primitives ``run_single`` + ``_enrich`` (identical to
    :func:`phase7a_execution.execute`'s inner body), adds resume + raw capture. Completed replications
    are never re-run; errored slots are retried across bounded passes. A non-transient provider error
    (auth/not-found) aborts immediately (:class:`BatchAborted`)."""
    model_id = model_id_for(model_key)
    library_run_id = library_run_id_for(model_key)
    rt_fp = p7.runtime_contract_fingerprint(model_key, repo_root)
    merged = dedupe_records(list(existing or []))
    any_success = any(is_completed(r) for r in merged)

    for _pass in range(max_passes):
        done = _completed_keys(merged)
        todo = [(u, i) for u in units for i in range(N_REPLICATIONS)
                if (model_id, u.unit_id, i) not in done]
        if not todo:
            break
        for k, (u, i) in enumerate(todo):
            rec = run_single(provider, Path(f"{u.unit_id}.yaml"), u.task, i, library_run_id)
            enr = _enrich(rec, u, model_id, rt_fp, dry_run, execution_type)
            caps = getattr(provider, "captures", None)
            if caps:
                c = caps[-1]
                enr["raw_response"] = c.get("raw_response")
                enr["raw_response_sha256"] = c.get("raw_response_sha256")
                enr["raw_result_ref"] = "inline:raw_response"
            # Fail-closed on a non-transient error before we have any success (bad key / wrong model).
            if not any_success and enr.get("error") and enr.get("error_type") in (
                    "auth_error", "not_found_error"):
                merged = merge_records(merged, [enr])["records"]
                if on_checkpoint:
                    on_checkpoint(merged)
                raise BatchAborted(
                    f"non-transient provider error on first calls: {enr.get('error_type')}")
            merged = merge_records(merged, [enr])["records"]
            if is_completed(enr):
                any_success = True
            if on_checkpoint and (k + 1) % 10 == 0:
                on_checkpoint(merged)
        if on_checkpoint:
            on_checkpoint(merged)
    return merged


# ---------------------------------------------------------------------------
# Guarded batch entrypoint (preflight gate -> execute -> raw freeze -> analysis)
# ---------------------------------------------------------------------------

def run_model_batch(model_key: str, *, repo_root: str | Path | None = None, provider_factory=None,
                    run_qa: bool = True, qa_record: dict | None = None,
                    out_dir: str | Path | None = None,
                    dry_run: bool = False, execution_type: str | None = None,
                    max_passes: int = DEFAULT_MAX_RESUME_PASSES) -> dict:
    """The one guarded real-run entrypoint, parameterized by ``model_key`` ('haiku' | 'sonnet').

    Refuses unless the frozen fingerprint gate AND executable pytest QA pass (``real_run_preflight``),
    the exact model / N / 84-unit universe hold, and — for the real provider — a usable credential is
    available. Then it enforces EXECUTION -> RAW PERSISTENCE -> RAW FREEZE -> DETERMINISTIC ANALYSIS.
    Single-model: it runs only ``model_key`` and writes only that model's directory; the other model's
    frozen artifacts are never touched. Tests inject ``provider_factory`` (fake/mock), ``run_qa=False``
    + a ``qa_record`` to run offline with 0 real calls."""
    if model_key not in MODEL_KEYS:
        raise ValueError(f"model_key must be one of {MODEL_KEYS}")
    model_id = model_id_for(model_key)
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    if execution_type is None:
        execution_type = EXEC_TYPE_DRY_RUN if dry_run else EXEC_TYPE_ADJUDICATION
    target = Path(out_dir) if out_dir else (root / out_dir_for(model_key))
    raw_file = target / "raw" / f"{model_key}_raw_records.jsonl"
    freeze_file = target / f"{model_key}_raw_result_freeze.json"
    analysis_json = target / f"{model_key}_deterministic_analysis.json"
    analysis_md = target / f"{model_key}_deterministic_analysis.md"
    usage_file = target / f"{model_key}_usage_summary.json"

    # --- Gate 1+2: frozen fingerprint gate AND executable pytest QA ---
    pf = p7.real_run_preflight(root, run_qa=run_qa, qa_record=qa_record)
    if not pf["go"]:
        raise ProviderUnavailable(
            f"preflight NO-GO (gate_passes={pf['gate_passes']} qa_status={pf['qa_status']}): "
            f"{pf['gate_errors']}")

    # --- Gate 3: exact model / N / universe (explicit, redundant with the gate) ---
    units = resolve_evaluated_units(root)
    expected_ids = {"haiku": "claude-haiku-4-5-20251001", "sonnet": "claude-sonnet-4-5-20250929"}
    if model_id != expected_ids[model_key]:
        raise ProviderUnavailable(f"unexpected {model_key} model id: {model_id}")
    if not rc.is_executable(rc.build_contract(model_key, root)):
        raise ProviderUnavailable(f"{model_key} runtime contract not executable")
    if N_REPLICATIONS != 5 or len(units) != 84:
        raise ProviderUnavailable(f"universe drift: N={N_REPLICATIONS} units={len(units)}")

    # --- Gate 4: credential / provider availability (real path only) ---
    availability = None
    if provider_factory is None:
        availability = check_provider_availability()
        if not availability["available"]:
            raise ProviderUnavailable(
                f"provider unavailable ({availability['reason']}): no real {model_key} call made")
        provider_factory = lambda: provider_factory_for(model_key)  # noqa: E731
    provider = provider_factory()

    # --- EXECUTION -> RAW PERSISTENCE (crash-safe checkpoints) ---
    existing = dedupe_records(_load_jsonl(raw_file))

    def checkpoint(recs: list[dict]) -> None:
        _write_jsonl_atomic(raw_file, sorted(recs, key=replication_key))

    records = execute_model_records(
        model_key, units, provider, repo_root=root, existing=existing,
        execution_type=execution_type, dry_run=dry_run, max_passes=max_passes,
        on_checkpoint=checkpoint)
    records = sorted(dedupe_records(records), key=replication_key)
    checkpoint(records)

    # --- RAW FREEZE (before any analysis) ---
    freeze = build_raw_freeze(records, repo_root=root, dry_run=dry_run,
                              execution_type=execution_type, model_key=model_key)
    target.mkdir(parents=True, exist_ok=True)
    freeze_file.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n")

    # --- USAGE (persist alongside the freeze; no cost invented) ---
    usage = aggregate_usage(records, model_id=model_id)
    usage_file.write_text(json.dumps(usage, indent=2, ensure_ascii=False) + "\n")

    # --- DETERMINISTIC ANALYSIS (only after the raw freeze exists) ---
    analysis = None
    if freeze["complete"]:
        report = p7.build_phase7a_report(records, dry_run=dry_run)
        analysis = {
            "phase": "7A",
            "model": model_id,
            "execution_type": execution_type,
            "synthetic_non_analytical": bool(dry_run),
            "bound_raw_freeze": {
                "aggregate_result_set_fingerprint": freeze["aggregate_result_set_fingerprint"],
                "completed_analytical_calls": freeze["completed_analytical_calls"],
            },
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
        "freeze_file": str(freeze_file),
        "freeze": freeze,
        "usage_file": str(usage_file),
        "analysis_file": str(analysis_json) if analysis else None,
        "analysis": analysis,
        "complete": freeze["complete"],
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
    pf = p7.real_run_preflight(root, run_qa=True)
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
        return 0 if res["complete"] else 3

    p.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
