# Phase 6.2 — Runtime Contract Explanation

**Mode:** THREE_MODEL_PER_MODEL_CALIBRATION. Three frozen contracts
(`phase6_2_runtime_contract_{haiku,sonnet,opus}.json`), one per model, generated and
validated deterministically by `src/agent_arena/runtime_contract.py`. Offline, no model
calls, no private material.

## What each contract pins

| field | meaning |
|-------|---------|
| `contract_id` / `contract_version` | `AA-RTC-6.2-<MODEL>-001` / `1.0` |
| `calibration_mode` | `THREE_MODEL_PER_MODEL_CALIBRATION` |
| `model_family` | `claude-{haiku,sonnet,opus}-4-5` |
| `exact_model_id` | **dated snapshot** — `…-20251001` / `…-20250929` / `…-20251101` |
| `model_revision` | the dated suffix |
| `agent_config_path` + `agent_config_model` + `agent_config_sha256` | the **pinned** config, its dated model string, and its byte hash |
| `repository_commit` | source-code baseline `327e7690…` (runner/providers/parser) |
| `protocol_version` | `6.1` |
| `system_prompt_sha256` | SHA-256 of `STUDY_FORENSICS_PROMPT` |
| `task_packet_construction_sha256` | SHA-256 of the construction descriptor (system + `task.prompt`; **no per-case content**) |
| `parser_contract_sha256` | SHA-256 of the output-contract core-field descriptor |
| runtime params | `temperature 0.0`, `max_output_tokens 4096`, `replication_count 1`, `concurrency 1`, `request_timeout_seconds 120`, `max_transport_retries_after_initial_request 2` |
| `top_p` | `OMITTED_FROM_REQUEST` (the runner transmits none) |
| `seed` | `UNSUPPORTED` (Anthropic Messages API exposes none) |
| retry policy | transport-only classes; `semantic_or_quality_retries: PROHIBITED` |
| handling | parser-failure → failed record (never re-run); missing/invalid confidence → classify, **never coerce to 0.0** |
| order / recovery | deterministic filename order; resume only not-yet-executed cases; no selective reruns |
| prohibitions | prompt/param changes during run; selective reruns; threshold/abstention tuning during execution |

## Dated model ids — configs pinned, no override

The Sonnet and Opus configs were **pinned to their dated snapshots before any result**
(`agents/claude_sonnet.yaml` → `claude-sonnet-4-5-20250929`, `agents/claude_opus.yaml`
→ `claude-opus-4-5-20251101`); Haiku was already dated. There is **no moving alias in
the runtime path and no implicit model override**: `validate_contract` requires
`exact_model_id == agent_config_model` and that the config's `model` is a dated snapshot
(`agent_config_model` is re-read from the file and reproduced). The future private
runner loads the same exact dated id the contract records.

## Provider enforces timeout and retry

`providers/anthropic.py` now constructs the client explicitly as
`anthropic.Anthropic(timeout=120.0, max_retries=2)` — no SDK-default fallback. The
contract's `request_timeout_seconds` and `max_transport_retries_after_initial_request`
are tied to those provider constants and cross-checked in validation, so a contract is
executable only when implementation and contract agree. Retries remain transport-only
(the SDK's transient HTTP/connection policy); Agent Arena adds **no** semantic/quality
retry — a parser failure, malformed output, or missing/invalid/low confidence never
triggers another request, and an exhausted failure is recorded as an explicit failed
record.

## Residual limitation — nondeterminism

`temperature = 0.0`, no `seed`, and no `top_p` reduce but **do not guarantee**
identical model outputs: Anthropic generation may still exhibit run-to-run
nondeterminism. The contracts pin the request/transport/model surface, not the model's
sampling determinism. Reproducibility claims are limited accordingly.

## Hashing & reproducibility

`system_prompt_sha256`, `task_packet_construction_sha256`, and `parser_contract_sha256`
are derived from the exact tracked source (`runner.STUDY_FORENSICS_PROMPT`, the
construction descriptor, `output_contract._CORE_FIELDS`); `agent_config_sha256` from the
config file bytes. `validate_contract()` recomputes all four and fails on any mismatch —
a one-character change to the prompt, the construction, or a config changes its hash and
invalidates the contract. Private case content is never hashed or referenced.

## Cross-contract invariant

`assert_non_model_values_identical()` proves all three contracts share every non-model
field. The only differences are `model_family`, `exact_model_id`, `model_revision`,
`agent_config_*`, and `contract_id`.

## Executable gate

`is_executable()` returns `True` only when `validate_contract()` is clean — which
requires no placeholder/ambiguous value anywhere. Explicit markers (`UNSUPPORTED`,
`OMITTED_FROM_REQUEST`, `PROHIBITED`) are valid values, not placeholders. All three
committed contracts are `is_executable == True`.
