# Phase 6.2 — Private Execution Handoff (do not begin without separate authorization)

**Mode:** THREE_MODEL_PER_MODEL_CALIBRATION. Execute the frozen 27-case development pool
**once per model** under the three frozen runtime contracts, producing **three
independent** anonymized envelopes (one per model). **Do not begin** until (a) the
private dev-pool manifest is provisioned (`development_pool_public_manifest.json`
commitment is not PENDING) and (b) the curator explicitly authorizes result generation.

## Pre-execution gates (per model)

1. HEAD/tag verified; tracked tree clean.
2. Load `phase6_2_runtime_contract_<model>.json`; `runtime_contract.is_executable()` →
   True; all hashes reproduce against the checked-out source.
3. Private dev-pool manifest verifies against the tracked public salted commitment
   (`dev_manifest.verify_public_against_private`); exactly 27 cases, gold 8/15/2/2.
4. The effective provider/model equals the contract's `exact_model_id` (dated snapshot),
   passed as an explicit override — **not** the config alias.

## Execution rules (per model, per contract)

- one primary execution for each of the 27 cases (`replication_count = 1`);
- deterministic filename order; `temperature 0.0`, `max_output_tokens 4096`,
  `top_p` omitted, no seed, `request_timeout_seconds 120`, concurrency 1;
- retries only for the frozen transport classes (connection / timeout / 429 / 5xx / 529),
  ≤ 2 after the initial request, SDK exponential backoff; **never** retry on parser
  failure, malformed/low confidence, wrong prediction, or output quality;
- record parser failures, exhausted transport failures, and MISSING/INVALID confidence
  **explicitly**; **never** coerce missing/invalid confidence to 0.0;
- no selective reruns; no prompt/parameter/threshold/abstention changes during the run;
- partial-run recovery: resume only not-yet-executed cases.

## Outputs (per model)

- a private transient DEV→canonical mapping (outside Git; never printed/committed);
- one anonymized result envelope conforming to
  `analysis/phase6_2_calibration/result_input_schema.json`, with `synthetic_fixture:
  false`, `manifest_id`/`public_commitment`/`protocol_version`/`run_id`/`model`/
  `provider`/`prompt_contract_version`/`generated_at`/`expected_record_count: 27`/
  `declared_gold_aggregate: 8/15/2/2`, and the model's exact dated id;
- validate each envelope with `calibration.validate_result_envelope(...)` before use.

## Isolation

Three separate runs, envelopes, and reports; **never pooled**. No canonical/BIAA/HLD ids,
salt, or private mapping in any envelope or log. The private execution session is
single-purpose and retired after the envelopes are produced and validated. This
preparation does **not** authorize execution.
