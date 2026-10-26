# Phase 6.2 — Runtime Freeze Acceptance Criteria

All criteria are enforced by `runtime_contract.py` + `tests/test_runtime_contract.py`
(offline, deterministic). Freeze is accepted only when all hold.

## Freeze acceptance (this step)

| id | criterion | check |
|----|-----------|-------|
| RF-1 | mode recorded | every contract `calibration_mode == THREE_MODEL_PER_MODEL_CALIBRATION`; review records it |
| RF-2 | no model alias remains | every `exact_model_id` is an exact dated snapshot (`^claude-…-\d{8}$`) |
| RF-3 | three exact dated ids | `{haiku-…20251001, sonnet-…20250929, opus-…20251101}` |
| RF-4 | contracts complete | all required fields present in each contract |
| RF-5 | no placeholder | no placeholder/ambiguous value (explicit `UNSUPPORTED`/`OMITTED_FROM_REQUEST`/`PROHIBITED` allowed) |
| RF-6 | non-model values identical | all three contracts share every non-model field |
| RF-7 | hashes reproduce | config/prompt/task-construction/parser hashes recompute from source and match |
| RF-8 | one-char change invalidates | a one-character prompt or config change changes the hash; a tampered hash fails validation |
| RF-9 | unsupported params explicit | `top_p == OMITTED_FROM_REQUEST`, `seed == UNSUPPORTED` |
| RF-10 | timeout & retry explicit | `request_timeout_seconds` and `max_transport_retries_after_initial_request` are explicit integers |
| RF-11 | replication frozen | `replication_count == 1` |
| RF-12 | semantic retries impossible | `semantic_or_quality_retries == PROHIBITED`; contract rejects any other value |
| RF-13 | executable gate | `is_executable == True` only when validation is clean; placeholders block it |
| RF-14 | no private material | tooling reads only public tracked files; no private path/identity required |
| RF-15 | config/contract model match | each `exact_model_id` equals its **pinned** config `model`, both dated snapshots; a contract/config mismatch or a moving alias is rejected |
| RF-16 | provider transport enforcement | `request_timeout_seconds`/`max_transport_retries…` equal the provider constants (`anthropic.Anthropic(timeout=120.0, max_retries=2)`); a mismatch is rejected; mock tests prove the client receives them, `top_p`/`seed` absent, and parser failures cause no re-request |

## Stop conditions (freeze step)

Stop and report if: a dated snapshot cannot be resolved authoritatively; any hash fails
to reproduce; any contract carries a placeholder; the three contracts disagree on a
non-model value; any model/network call or private access would be required.

## Execution acceptance (LATER — separately authorized; NOT this step)

E-1 the private runner loads each contract's referenced **pinned** config (whose `model`
== `exact_model_id`, a dated snapshot) — no implicit override; the effective model equals
it · E-2 one primary execution per case, filename
order, no selective reruns, transport-only retries · E-3 parser/missing/invalid results
recorded explicitly, confidence never coerced to 0.0 · E-4 one anonymized envelope +
one calibration report per model; the three never pooled · E-5 no prompt/param/threshold
changes during the run.

**Remaining gate:** execution is **PENDING SEPARATE CURATOR AUTHORIZATION** (and remains
gated by `phase6_2_execution_contract.md §5` + the private dev-pool provisioning).
