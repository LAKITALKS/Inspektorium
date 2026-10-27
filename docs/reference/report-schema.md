# Report schema

This page describes the files Inspektorium reads and writes.
It covers the `inspect` input, proposals and report (schema 0.1) and the five files of an audit bundle.
Field definitions come from the Pydantic models named in each section.

- [Inspection input](#inspection-input)
- [Proposal batch](#proposal-batch)
- [Inspect report (schema 0.1)](#inspect-report-schema-01)
- [Audit bundle files](#audit-bundle-files)
- [Operation output](#operation-output)

## Conventions for `inspect`

All `inspect` models reject unknown fields and are immutable ([models](../../src/inspektorium/core/models.py)).

| Type | Rule |
| --- | --- |
| Identifier | String matching `^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$`, 1–80 characters |
| Non-empty text | String with at least one character |
| Offset | Integer ≥ 0; a Python character index into canonical text |
| SHA-256 | 64 lowercase hexadecimal characters |

Canonical text uses LF newlines and Unicode NFC; all other whitespace is kept ([normalization](../../src/inspektorium/core/normalization.py)).
Answer and source texts are canonicalized when the input is parsed.
Spans are half-open intervals `[start, end)`.

## Inspection input

Model `InspectionInput`. Read by `inspect --input`.

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `schema_version` | `"0.1"` | no | Default `"0.1"` |
| `answer.answer_id` | Identifier | no | Default `"answer"` |
| `answer.text` | Non-empty text | yes | Canonicalized |
| `sources` | list of source objects | yes | At least one; `source_id` values unique |
| `sources[].source_id` | Identifier | yes | |
| `sources[].title` | Non-empty text or `null` | no | Display only; not hashed |
| `sources[].text` | Non-empty text | yes | Canonicalized |

Use `parse_inspection_input_json` for untrusted files; it applies the strict decoder ([Python API](python-api.md#parsing)).

## Proposal batch

Model `ProposalBatch`. Read by `inspect --proposals`, or returned by the provider.

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | `"0.1"` | Optional; default `"0.1"` |
| `findings` | list of `ProposedFinding` | May be empty; `claim_id` values unique |

Each `ProposedFinding` has these keys. All keys are required; the four evidence keys may be `null`.

| Field | Type | Meaning |
| --- | --- | --- |
| `claim_id` | Identifier | Finding identifier |
| `claim_text` | Non-empty text | Proposed atomic claim |
| `claim_start`, `claim_end` | Offset | Proposed claim span in the answer |
| `proposed_relation` | `supported`, `contradicted`, `not_established`, `attribution_mismatch` | Evaluator-proposed relation |
| `source_id` | Identifier or `null` | Cited source |
| `evidence_quote` | Non-empty text or `null` | Proposed quotation |
| `evidence_start`, `evidence_end` | Offset or `null` | Proposed quotation span in the source |
| `rationale` | Non-empty text | Evaluator rationale |
| `evidence_sufficiency` | `sufficient`, `partial`, `insufficient` | Evaluator judgment |
| `evaluator_certainty` | `high`, `medium`, `low` | Evaluator judgment |

Every relation except `not_established` requires all four evidence fields ([relations](../../src/inspektorium/core/relations.py)).

## Inspect report (schema 0.1)

Model `InspectionReport`, produced by `inspect_proposals` ([inspection](../../src/inspektorium/core/inspection.py)).

### JSON serialization

`render_json` writes the model dump with sorted keys, two-space indentation, unescaped Unicode and one final newline ([JSON renderer](../../src/inspektorium/report/json_report.py)).
Fixed inputs, proposals and timestamp settings give identical bytes.

### Top-level fields

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | `"0.1"` | Report schema version |
| `generated_at` | ISO 8601 string or `null` | Explicit `--generated-at` value; timezone required; `null` by default |
| `fingerprints` | object | SHA-256 of the canonical inputs |
| `summary` | object | Mechanical counts |
| `findings` | list of validated findings | One per proposal, in proposal order |
| `scope` | object | Fixed scope statement and limitations |

### `fingerprints`

| Field | Meaning |
| --- | --- |
| `algorithm` | Always `"sha256"` |
| `answer_sha256` | SHA-256 of the canonical answer text, UTF-8 encoded |
| `sources[]` | `{source_id, sha256}` per source, sorted by `source_id` |
| `canonical_bundle_sha256` | SHA-256 of `{"answer":…,"sources":[{"source_id":…,"text":…}]}` with sorted keys, no spaces and sources sorted by ID |

Titles and `generated_at` are not hashed ([fingerprints](../../src/inspektorium/core/fingerprints.py)).

### `summary`

| Field | Count of findings where |
| --- | --- |
| `claims_inspected` | every finding |
| `reportable_findings` | `reportable_relation` is not `null` |
| `citation_spans_verified` | `evidence_span_verified` is `true` |
| `validation_failures` | `deterministic_validation_status` is `failed` |

The model rejects a report whose counts do not match its findings.

### `findings[]`

Each validated finding contains every `ProposedFinding` field unchanged, plus:

| Field | Type | Meaning |
| --- | --- | --- |
| `claim_span_verified` | boolean | `answer[claim_start:claim_end] == claim_text` |
| `evidence_span_verified` | boolean or `null` | Quotation equals the source span; `null` when no citation was proposed and none is required |
| `deterministic_validation_status` | `passed` or `failed` | All mandatory checks passed |
| `reportable_relation` | relation or `null` | Equals `proposed_relation` if passed; `null` if failed |
| `validation_issues` | list of `{code, message}` | Empty if passed; at least one entry if failed |

Model invariants ([models](../../src/inspektorium/core/models.py)):

- `evidence_span_verified: true` requires all four evidence fields.
- A passed finding exposes the unchanged proposed relation and has no issues.
- A failed finding has `reportable_relation: null` and at least one issue.
- A reportable citation must name a fingerprinted source.

Issue codes: `claim_span_mismatch`, `unknown_source`, `invalid_evidence_offsets`, `evidence_span_mismatch`, `incomplete_evidence_reference`.
The vocabulary also contains `malformed_proposal`, used for proposal parsing errors.

### `scope`

| Field | Value |
| --- | --- |
| `basis` | Always `"user_supplied_sources_only"` |
| `statement` | Fixed sentence describing the comparison |
| `limitations` | Fixed list of statements |

The fixed texts are defined as `SCOPE_NOTICE` in [inspection](../../src/inspektorium/core/inspection.py).

### Markdown report

`render_markdown` builds the Markdown report from the same model ([Markdown renderer](../../src/inspektorium/report/markdown_report.py)).
Its sections are fixed: title, optional timestamp line, Summary with a display note, Findings, Validation Warnings, and Scope and Limitations.
Untrusted text is encoded as described in [methodology](../concepts/methodology.md#display-convention-for-untrusted-text).
The JSON report keeps the exact characters.

## Audit bundle files

An audit revision is a directory with exactly the files in `FILES` ([workflow models](../../src/inspektorium/audit/workflow/models.py)).
The directory name is the revision ID.

| File | Model | Written as |
| --- | --- | --- |
| `record.json` | `AuditRecord` | Canonical JSON |
| `decision.json` | `Decision` | Canonical JSON |
| `manifest.json` | `Manifest` | Canonical JSON |
| `report.md` | — | Deterministic Markdown from a projection of the record |
| `report.html` | — | Escaped HTML with the same content |

Canonical JSON means sorted keys, separators without spaces, unescaped Unicode, no `NaN` and one final newline ([pipeline](../../src/inspektorium/audit/workflow/pipeline.py), function `canonical`).
Every digest is SHA-256 over canonical JSON or over the raw file bytes.
All three JSON models reject unknown fields and use strict types. `inspect` also rejects duplicate keys.

### `record.json`

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | `"1.0"` | Bundle schema version |
| `contract_version` | `"AA-P10/1.0"` | Operational contract version |
| `revision_id` | string | Random UUID; equals the directory name |
| `parent` | object or `null` | `{revision_id, manifest_fingerprint}` of the previous revision; `null` for a first run |
| `created_at` | string | UTC creation time, ISO 8601 |
| `execution_mode` | `recorded_offline`, `live_generation`, `offline_replay_of_live` | Derived from the execution carriers, never from a caller flag |
| `status` | status name | Operational status of this revision |
| `release_intent` | object or `null` | `{reviewer, reason, scope}` for a released revision |
| `run_record` | object | The evaluated run: `run_id`, `task`, `results`, `timestamp`, `metadata` |
| `selected_position_id` | string or `null` | The review-history position the reports are built from |
| `provenance` | object | Bound provenance core; identical to `manifest.json` `provenance` |

`run_record.results[].agent_result.raw_output` holds the exact raw response.
`run_record.metadata.phase9` holds the review history: positions, conflicts, route and review state.

### `decision.json`

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | `"1.0"` | |
| `status` | status name | Equals the record status |
| `subject` | SHA-256 | Digest of `record.json` |
| `registry_fingerprint` | SHA-256 | Digest of the control registry and the mandatory gate set |
| `controls` | list of `Control` | One entry per registered control |
| `report_hashes` | object | SHA-256 of `report.md` and `report.html` |
| `release_intent` | object or `null` | Present only for `RELEASED` |

Each `Control`:

| Field | Type | Meaning |
| --- | --- | --- |
| `control_id` | string | Registered control name |
| `version` | string | Registered control version |
| `subject` | SHA-256 | Digest of the record the control evaluated |
| `execution` | `executed`, `error`, `not_executed` | Whether the control ran |
| `outcome` | `pass`, `fail`, `not_applicable` | Result |
| `eligible`, `evaluated` | integer ≥ 0 | Population size and evaluated count |
| `findings` | list of objects | Findings of the control |
| `reason` | non-empty string | Explanation |

The control registry of a recorded offline run, as captured from a released bundle:

| `control_id` | `version` |
| --- | --- |
| `input_preflight` | `1.1` |
| `analysis_source` | `1.1` |
| `finding_artifact_binding` | `1.1.0` |
| `summary_strength_monotonicity` | `1.0.0` |
| `evidence_symmetry` | `1.1.0` |
| `value_origin_provenance` | `1.0.0` |
| `search_scope_binding` | `1.0.0` |
| `phase8_semantics_taxonomy` | `1.3` |
| `phase9_history_review` | `1.3` |
| `provenance` | `1.0` |
| `markdown_qa` | `1.1` |
| `html_qa` | `1.1` |

Live and replayed bundles use the same registry with `provenance` at version `live-1.0`.
The registries are `REGISTRY` and `LIVE_REGISTRY` in [pipeline](../../src/inspektorium/audit/workflow/pipeline.py).

### `manifest.json`

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | `"1.0"` | |
| `contract_version` | `"AA-P10/1.0"` | |
| `revision_id`, `status`, `created_at`, `execution_mode`, `release_intent`, `provenance` | | Must equal the values in `record.json` |
| `files` | object | SHA-256 of the raw bytes of `record.json`, `decision.json`, `report.md` and `report.html` |
| `fingerprint` | SHA-256 | Digest of the manifest without its `fingerprint` field |

### `provenance`

Keys of the provenance core of a recorded offline bundle:

| Key | Content |
| --- | --- |
| `contract`, `config` | `AA-P10/1.0` and `offline-recording-v1` |
| `package_version` | Installed `inspektorium` version, for example `0.3.0` |
| `code` | `code_fingerprint`, `module_hashes`, `verified_source_commit`, `source_binding` |
| `case_id`, `run_id` | Case and run identity |
| `input_fingerprint`, `analysis_fingerprint`, `evidence_fingerprint`, `ledger_fingerprint`, `review_fingerprint` | Digests of task, run record, evidence, semantic ledger and review history |
| `phase8_summary`, `phase9_summary`, `review_counts` | Summaries of the semantic analysis and review state |
| `selected_position_id` | Same as in the record |
| `providers` | Provider, model and usage per result |
| `recording_notice` | `RECORDED OFFLINE / SYNTHETIC; no live model execution` |

`code.module_hashes` lists the SHA-256 of every installed `inspektorium.audit` module file.
`verified_source_commit` is set only when those bytes match a Git commit; otherwise it is `null`.
Live and replayed bundles add `contract_addendum`, `execution_mode`, `execution_mode_errors` and `execution_evidence`.

### Fingerprint chain

| Link | Rule |
| --- | --- |
| `decision.subject` | Equals the SHA-256 of `record.json` |
| `decision.report_hashes` | Equal the SHA-256 of both report files |
| `manifest.files` | Equal the SHA-256 of the four other files |
| `manifest.fingerprint` | Equals the digest of the manifest without `fingerprint` |
| `record.parent.manifest_fingerprint` | Equals the `fingerprint` of the parent's manifest when the revision is written |
| `decision` as a whole | Equals a fresh recomputation of all controls |

`audit inspect` checks every rule except the parent link ([limitations](../evaluation/limitations.md#audit-workflow-inspektorium-audit)).
`review` and `release` set the parent link from the parent's manifest after inspecting the parent.

The record fingerprint is also printed in both reports, in the table "Revision identity".

### `report.md` and `report.html`

Both reports are rendered from one deterministic projection of the record ([render](../../src/inspektorium/audit/workflow/render.py), [projection](../../src/inspektorium/audit/workflow/projection.py)).
The top-level sections of a released bundle's `report.md` are:

```text
# Canonical local audit
## Execution and release
## Original claim
## Scientific judgments
## Original label and taxonomy
## Propositions and inference limits
## Evidence and source quotations
## Search scope
## Finding and client traces
## UNKNOWN, conflicts and review history
## Mandatory controls
## Limitations
## Provenance
```

`report.html` has the same `h2` sections. Its template contains no `script` element.
Model and source text is escaped. Control and invisible format characters are shown as `⟦U+XXXX⟧`; `record.json` keeps the exact characters.
Canonical PDF output is not supported.

## Operation output

`audit run`, `review` and `release` print an `OperationResult`:

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | status name | Outcome of the operation |
| `path` | string or `null` | Absolute path of the new revision; `null` when none was written |
| `errors` | list of strings | Failed control reasons or the refusal cause |

`audit inspect` prints a `Verification`:

| Field | Type | Meaning |
| --- | --- | --- |
| `valid` | boolean | Files, hashes and recomputed controls match |
| `status` | status name | Recorded status if valid; `RELEASE_BLOCKED` if not |
| `errors` | list of strings | Verification failure, if any |

`audit validate` prints `{"input_valid": …, "errors": […], "release_authorized": false}`.
If the task file cannot be loaded, it prints `{"status": "PREFLIGHT_BLOCKED", "errors": […]}`.

The status names are `PREFLIGHT_BLOCKED`, `RUN_FAILED`, `ANALYSIS_INCOMPLETE`, `REVIEW_REQUIRED`, `RELEASE_BLOCKED`, `READY_FOR_RELEASE` and `RELEASED`.
Their meanings are in the [audit workflow guide](../guides/audit-workflow.md#status-reference).
