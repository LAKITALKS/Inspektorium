# Phase 6.2 — Runtime Freeze Preparation Status (frozen; pending curator approval)

**Governance:** Level 2. Three per-model runtime contracts built, validated, and frozen
(THREE_MODEL_PER_MODEL_CALIBRATION), now aligned with the real implementation.
**Not committed** — pending curator approval. Baseline `327e7690…`; no model/network
calls; no private material accessed.

## Execution-alignment fixes applied (this revision)
1. **Configs pinned before results:** `agents/claude_sonnet.yaml` →
   `claude-sonnet-4-5-20250929`, `agents/claude_opus.yaml` → `claude-opus-4-5-20251101`
   (Haiku already `claude-haiku-4-5-20251001`). No moving alias in the runtime path; no
   implicit model override. Each contract's `exact_model_id` equals its config's `model`
   (validated; mismatch/moving-alias rejected).
2. **Provider enforces transport values:** `providers/anthropic.py` now builds
   `anthropic.Anthropic(timeout=120.0, max_retries=2)` explicitly — no SDK-default
   fallback (confirmed against installed anthropic 0.86.0: default read-timeout was 600s).
   Contract transport values are tied to the provider constants and cross-checked.
3. **Executable gate corrected:** a contract is `is_executable` only when config model
   matches, provider timeout/retry match, all hashes reproduce, no alias, no placeholder.

## Resolved dated model ids (authoritative catalog)
Haiku `claude-haiku-4-5-20251001` · Sonnet `claude-sonnet-4-5-20250929` · Opus
`claude-opus-4-5-20251101`. Same 4.5 family; no newer family substituted; official model
metadata, no Messages API call.

## IMPLEMENTED
- `agents/claude_sonnet.yaml`, `agents/claude_opus.yaml` — pinned model fields.
- `src/agent_arena/providers/anthropic.py` — explicit `timeout=120.0` / `max_retries=2`
  (+ constants); no semantic/quality retry added.
- `src/agent_arena/runtime_contract.py` — build + validation with config-model match,
  moving-alias rejection, provider-enforcement cross-check, executable gate.
- `analysis/phase6_2_runtime_freeze/phase6_2_runtime_contract_{haiku,sonnet,opus}.json` —
  regenerated; all `is_executable == True`.
- Docs: `runtime_selection_review.md`, `runtime_contract_explanation.md`,
  `runtime_freeze_acceptance_criteria.md`, `phase6_2_private_execution_handoff.md`, this.
- Tests: `tests/test_runtime_contract.py`, `tests/test_provider_runtime.py`.

## Frozen shared runtime values (identical across the three)
provider anthropic · Anthropic Messages API · temperature 0.0 · max_output_tokens 4096 ·
replication_count 1 · concurrency 1 · **request_timeout_seconds 120 (enforced)** ·
**max_transport_retries_after_initial_request 2 (enforced)** · top_p OMITTED_FROM_REQUEST ·
seed UNSUPPORTED · semantic/quality retries PROHIBITED · missing/invalid confidence never
coerced to 0.0 · system-prompt/task-construction/parser hashes · repository_commit `327e769`.

## Acceptance (all met)
RF-1…RF-16 pass (see `runtime_freeze_acceptance_criteria.md`), incl. RF-15
(config/contract model match) and RF-16 (provider transport enforcement).

## Residual limitation (explicit)
`temperature 0.0`, no `seed`, no `top_p` reduce but **do not guarantee** identical model
outputs — Anthropic generation may still be nondeterministic run-to-run. The contracts
pin the request/transport/model surface, not sampling determinism.

## PENDING SEPARATE AUTHORIZATION (not done here)
Private 27-case execution per model; live model calls; actual results/envelopes; result
interpretation. Gated by private dev-pool provisioning + explicit curator authorization.

## Not done (by rule)
No commit; no tag; no model/network call; no private access.
