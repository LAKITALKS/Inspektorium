"""Deterministic, offline runtime-contract tooling (Phase 6.2 runtime freeze).

Builds and validates the three per-model Phase 6.2 runtime contracts
(Haiku / Sonnet / Opus) for the frozen 27-case development execution. Every hash and
the model id are derived from the exact tracked artifacts the runner uses; nothing here
makes a model call or reads private material.

Alignment (curator-required): the exact dated snapshot in each contract must equal the
`model` field of its referenced agent config (the configs are pinned to dated
snapshots — **no moving alias, no implicit override**), and the frozen transport values
(`request_timeout_seconds`, `max_transport_retries_after_initial_request`) must equal
what the real Anthropic provider enforces. A contract is executable only when
implementation and contract agree.

Frozen decision: THREE_MODEL_PER_MODEL_CALIBRATION — one independent contract, run,
envelope, and report per model; the three models are never pooled.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

from agent_arena.output_contract import _CORE_FIELDS
from agent_arena.providers.anthropic import MAX_TRANSPORT_RETRIES, REQUEST_TIMEOUT_SECONDS
from agent_arena.runner import STUDY_FORENSICS_PROMPT

CALIBRATION_MODE = "THREE_MODEL_PER_MODEL_CALIBRATION"
CONTRACT_VERSION = "1.0"
PROTOCOL_VERSION = "6.1"
# Source-code baseline these contracts are frozen against (runner / providers / parser
# / pinned configs). The freeze changeset is committed atop it by the curator.
REPOSITORY_COMMIT_BASELINE = "327e7690ad53d3de793c074d5aa9137764575fe7"

# Explicit non-numeric markers that are VALID values, never placeholders.
_EXPLICIT_MARKERS = {"UNSUPPORTED", "OMITTED_FROM_REQUEST", "NOT_APPLICABLE", "PROHIBITED"}
_PLACEHOLDER_TOKENS = {"", "TODO", "TBD", "PLACEHOLDER", "FIXME", "XXX", "PENDING",
                       "UNKNOWN", "???", "CHANGEME"}

_DATED_MODEL_RE = re.compile(r"^claude-[a-z]+-\d+-\d+-\d{8}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

# Frozen shared runtime values — identical across all three contracts. The transport
# values are tied to the provider constants so contract and implementation cannot drift.
SHARED_RUNTIME = {
    "provider": "anthropic",
    "endpoint": "Anthropic Messages API (anthropic.Anthropic().messages.create)",
    "protocol_version": PROTOCOL_VERSION,
    "replication_count": 1,
    "concurrency": 1,
    "temperature": 0.0,
    "top_p": "OMITTED_FROM_REQUEST",
    "seed": "UNSUPPORTED",
    "max_output_tokens": 4096,
    "request_timeout_seconds": int(REQUEST_TIMEOUT_SECONDS),
    "max_transport_retries_after_initial_request": MAX_TRANSPORT_RETRIES,
    "retry_backoff": "exponential_backoff_anthropic_sdk_default",
    "retryable_error_classes": [
        "connection_error", "request_timeout", "rate_limit_429",
        "transient_server_error_5xx", "overloaded_529",
    ],
    "semantic_or_quality_retries": "PROHIBITED",
    "parser_failure_handling": "record as failed record (parse_ok=false); never re-run",
    "missing_confidence_handling": "classify MISSING; never coerce to 0.0",
    "invalid_confidence_handling": "classify INVALID; never coerce to 0.0",
    "execution_order_rule": "deterministic filename order (discover_cases); one primary execution per case",
    "partial_run_recovery_rule": "resume only not-yet-executed cases; never re-run completed or failed cases",
    "prohibit_prompt_or_parameter_changes_during_run": True,
    "prohibit_selective_reruns": True,
    "prohibit_threshold_or_abstention_tuning_during_execution": True,
}

# Per-model identity (dated snapshots resolved from the authoritative model catalog and
# pinned into the agent configs).
MODELS = {
    "haiku": {
        "contract_id": "AA-RTC-6.2-HAIKU-001",
        "model_family": "claude-haiku-4-5",
        "exact_model_id": "claude-haiku-4-5-20251001",
        "model_revision": "20251001",
        "agent_config_path": "agents/claude_haiku.yaml",
    },
    "sonnet": {
        "contract_id": "AA-RTC-6.2-SONNET-001",
        "model_family": "claude-sonnet-4-5",
        "exact_model_id": "claude-sonnet-4-5-20250929",
        "model_revision": "20250929",
        "agent_config_path": "agents/claude_sonnet.yaml",
    },
    "opus": {
        "contract_id": "AA-RTC-6.2-OPUS-001",
        "model_family": "claude-opus-4-5",
        "exact_model_id": "claude-opus-4-5-20251101",
        "model_revision": "20251101",
        "agent_config_path": "agents/claude_opus.yaml",
    },
}
# Non-model fields whose values must be byte-identical across all three contracts.
NON_MODEL_FIELDS = tuple(SHARED_RUNTIME.keys()) + (
    "calibration_mode", "contract_version", "system_prompt_sha256",
    "task_packet_construction_sha256", "parser_contract_sha256", "repository_commit",
)


# ---------------------------------------------------------------------------
# Hashes / values derived from the exact tracked artifacts
# ---------------------------------------------------------------------------

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def system_prompt_sha256() -> str:
    return _sha256_hex(STUDY_FORENSICS_PROMPT.encode("utf-8"))


def task_packet_construction_descriptor() -> str:
    return ("study_forensics/v1|system=STUDY_FORENSICS_PROMPT|"
            "user=task.prompt(verbatim)|messages=[{role:user,content:user}]")


def task_packet_construction_sha256() -> str:
    return _sha256_hex(task_packet_construction_descriptor().encode("utf-8"))


def parser_contract_descriptor() -> str:
    return ("study_forensics_output_contract/v1|core_fields=" + ",".join(_CORE_FIELDS)
            + "|confidence=float|missing_or_invalid_confidence=flag_not_coerce")


def parser_contract_sha256() -> str:
    return _sha256_hex(parser_contract_descriptor().encode("utf-8"))


def _repo_root(repo_root: str | Path | None) -> Path:
    return Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]


def agent_config_sha256(config_path: str | Path, repo_root: str | Path | None = None) -> str:
    return _sha256_hex((_repo_root(repo_root) / config_path).read_bytes())


def agent_config_model(config_path: str | Path, repo_root: str | Path | None = None) -> str:
    data = yaml.safe_load((_repo_root(repo_root) / config_path).read_text())
    return str((data or {}).get("model", ""))


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_contract(model_key: str, repo_root: str | Path | None = None) -> dict:
    """Assemble the canonical per-model runtime contract (deterministic)."""
    m = MODELS[model_key]
    contract = {
        "contract_id": m["contract_id"],
        "contract_version": CONTRACT_VERSION,
        "calibration_mode": CALIBRATION_MODE,
        "model_family": m["model_family"],
        "exact_model_id": m["exact_model_id"],
        "model_revision": m["model_revision"],
        "agent_config_path": m["agent_config_path"],
        "agent_config_model": agent_config_model(m["agent_config_path"], repo_root),
        "agent_config_sha256": agent_config_sha256(m["agent_config_path"], repo_root),
        "repository_commit": REPOSITORY_COMMIT_BASELINE,
        "system_prompt_sha256": system_prompt_sha256(),
        "task_packet_construction_sha256": task_packet_construction_sha256(),
        "parser_contract_sha256": parser_contract_sha256(),
    }
    contract.update(SHARED_RUNTIME)
    return contract


def build_all_contracts(repo_root: str | Path | None = None) -> dict[str, dict]:
    return {k: build_contract(k, repo_root) for k in MODELS}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = (
    "contract_id", "contract_version", "calibration_mode", "model_family",
    "exact_model_id", "model_revision", "agent_config_path", "agent_config_model",
    "agent_config_sha256", "repository_commit", "system_prompt_sha256",
    "task_packet_construction_sha256", "parser_contract_sha256",
) + tuple(SHARED_RUNTIME.keys())


def _find_placeholders(obj: object) -> bool:
    if isinstance(obj, dict):
        return any(_find_placeholders(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return any(_find_placeholders(v) for v in obj)
    if isinstance(obj, str):
        s = obj.strip()
        return s in _PLACEHOLDER_TOKENS and s not in _EXPLICIT_MARKERS
    return False


def validate_contract(contract: dict, repo_root: str | Path | None = None) -> list[str]:
    """Validate one contract against the frozen requirements. [] == valid."""
    errors: list[str] = []
    for f in REQUIRED_FIELDS:
        if f not in contract:
            errors.append(f"missing required field: {f}")
    if _find_placeholders(contract):
        errors.append("contract contains a placeholder/ambiguous value")

    if contract.get("calibration_mode") != CALIBRATION_MODE:
        errors.append(f"calibration_mode must be {CALIBRATION_MODE}")

    mid = str(contract.get("exact_model_id", ""))
    acm = str(contract.get("agent_config_model", ""))
    if not _DATED_MODEL_RE.match(mid):
        errors.append("exact_model_id must be a dated snapshot (no alias)")
    if not _DATED_MODEL_RE.match(acm):
        errors.append("agent_config model is a moving alias, not a dated snapshot")
    if mid != acm:
        errors.append("exact_model_id does not match agent_config model (contract/config mismatch)")

    # explicit unsupported/omitted markers required (not blanks)
    if contract.get("top_p") != "OMITTED_FROM_REQUEST":
        errors.append("top_p must be explicitly OMITTED_FROM_REQUEST")
    if contract.get("seed") != "UNSUPPORTED":
        errors.append("seed must be explicitly UNSUPPORTED")
    if contract.get("semantic_or_quality_retries") != "PROHIBITED":
        errors.append("semantic_or_quality_retries must be PROHIBITED")
    if contract.get("replication_count") != 1:
        errors.append("replication_count must be exactly 1")
    if not _COMMIT_RE.match(str(contract.get("repository_commit", ""))):
        errors.append("repository_commit must be a 40-hex commit")

    # transport values must equal what the real provider enforces (no drift, no
    # hidden fallback to SDK defaults)
    if contract.get("request_timeout_seconds") != int(REQUEST_TIMEOUT_SECONDS):
        errors.append("request_timeout_seconds does not match provider enforcement")
    if contract.get("max_transport_retries_after_initial_request") != MAX_TRANSPORT_RETRIES:
        errors.append("max_transport_retries_after_initial_request does not match provider enforcement")

    # hashes / config model reproduce from the exact tracked artifacts
    if contract.get("system_prompt_sha256") != system_prompt_sha256():
        errors.append("system_prompt_sha256 does not reproduce")
    if contract.get("task_packet_construction_sha256") != task_packet_construction_sha256():
        errors.append("task_packet_construction_sha256 does not reproduce")
    if contract.get("parser_contract_sha256") != parser_contract_sha256():
        errors.append("parser_contract_sha256 does not reproduce")
    cfg = contract.get("agent_config_path")
    if cfg:
        try:
            if contract.get("agent_config_sha256") != agent_config_sha256(cfg, repo_root):
                errors.append("agent_config_sha256 does not reproduce")
            if acm != agent_config_model(cfg, repo_root):
                errors.append("agent_config_model does not reproduce from the config file")
        except OSError:
            errors.append("agent_config_path is not readable")
    return errors


def assert_non_model_values_identical(contracts: list[dict]) -> list[str]:
    """All three contracts must share every non-model field value. [] == ok."""
    errors: list[str] = []
    if not contracts:
        return ["no contracts supplied"]
    ref = contracts[0]
    for c in contracts[1:]:
        for f in NON_MODEL_FIELDS:
            if c.get(f) != ref.get(f):
                errors.append(f"non-model field {f!r} differs across contracts")
    return errors


def is_executable(contract: dict, repo_root: str | Path | None = None) -> bool:
    """Executable only when the contract fully validates — which now requires the
    referenced agent config to carry the same exact dated model id and the provider to
    enforce the frozen timeout/retry values."""
    return not validate_contract(contract, repo_root)
