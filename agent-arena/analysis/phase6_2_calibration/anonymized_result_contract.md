# Phase 6.2 — Anonymized Result Contract (envelope binding)

**Governance:** Level 2. Boundary between the (later, separately authorized) trusted
private run and this session's public, offline analyzer.

## Principle

The analyzer consumes only an **anonymized result envelope** (schema:
`result_input_schema.json`). It never sees canonical case identities, the private
manifest, the salt, eligible ids, or any BIAA↔canonical mapping. The envelope
**binds** the records to the exact curator-certified pool without revealing identities.

## Binding fields (envelope metadata — all validated)

| field | binding role |
|-------|--------------|
| `envelope_version` = `6.2.0` | envelope format |
| `protocol_version` = `6.1` | the frozen protocol the run followed |
| `manifest_id` = `AA-DEVPOOL-6100` | must equal the tracked manifest id |
| `public_commitment` (64-hex) | must equal the tracked **public salted commitment** (salt never present) |
| `run_id` | opaque private-run id |
| `model`, `provider` | model/provider identifier |
| `prompt_contract_version` | system/prompt contract version or hash |
| `generated_at` | ISO result-generation timestamp |
| `expected_record_count` = `27` | pool size |
| `declared_gold_aggregate` = 8/15/2/2/27 | GOLD-label composition |
| `records` | 27 anonymized records |

## Two-sided verification

- **Trusted private runner (later, authorized):** verifies the private manifest
  against the public commitment (`dev_manifest.verify_public_against_private`, salt in
  hand) **before** emitting the envelope; stamps the envelope with `manifest_id` +
  `public_commitment` (public values only).
- **Offline analyzer (this session's tooling):** `validate_result_envelope(...)`
  checks `manifest_id` and `public_commitment` equal the tracked
  `development_pool_public_manifest.json` values (string equality — no salt needed),
  the protocol/count/aggregate bindings, and rejects any canonical/BIAA/HLD id or salt
  anywhere, **before** accepting records.

## Record fields (opaque)

`dev_id` (opaque `DEV-####`) · `model` · `predicted_label` · `gold_label` (class, not
identity) · `stratum` · `confidence` (number in `[0,1]` or `null` = MISSING) · optional
`gold_case_type`, `correct`.

## Prohibited anywhere in the envelope

canonical ids / `study-forensics-*`, `BIAA-*` / `HLD-*`, the salt, private-manifest
contents, a confidence coerced to `0.0` from missing/invalid.

## Invariants enforced

opaque unique `(model, dev_id)`; labels/strata vocabularies; **gold** aggregate
8/15/2/2 = 27 (predicted labels never constrained); confidence validity with no
coercion; every output keyed by `dev_id`/class only.
