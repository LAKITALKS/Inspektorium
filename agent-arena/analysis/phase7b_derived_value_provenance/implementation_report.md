# Phase 7B — Second Vertical Slice: Derived-Value Provenance (implementation report)

Second bounded Phase-7B slice. Deterministic, offline, no model call, no holdout access,
no LaVita identity in any executable artifact. Builds on the first artifact-binding slice.

## Problem

A value Agent Arena **derives** (computes / models / estimates / aggregates) must never later
appear as though a scientific source **reported** it. Freeze:

```
SYSTEM-DERIVED VALUE ≠ SOURCE-REPORTED VALUE
SOURCE-REPORTED INPUTS + AGENT ARENA DERIVATION = AGENT ARENA DERIVED OUTPUT   (not a source output)
```

## Semantic placement decision (recorded)

**Claim provenance and derived-value origin are DISTINCT dimensions.** They answer different
questions and live in different layers:

- `ClaimProvenance` (unchanged) — *where did the public claim come from?* (claim layer).
- `QAEvidenceItem.value_origin` (**new**) — *did the source report this value, or did Agent Arena
  derive it?* (evidence-value layer).

`ClaimProvenance` was **NOT** overloaded. Value origin was placed on `QAEvidenceItem` because a
value is a property of an evidence item, and a single record has one claim provenance but many
evidence values, each with its own origin. The two dimensions are kept independent from evidence
strength and (future) search scope as well (Phase-7B §13).

## Existing structures reused (no duplication)

- `schemas.EvidenceRole`, `schemas.FailureSeverity`, `forensic_report.leakage_findings`,
  the SHA-256 fingerprint helper, `run_library.discover_cases` — as in slice 1.
- Slice-1 chain models (`QAEvidenceItem`, `ClientFinding`, `ForensicRecord`) — **extended**, not
  duplicated. `final_binding_check` and `check_evidence_symmetry` — extended with a sibling
  primitive, not forked.
- Duplication self-audit (§21): searched `schemas.py` for pre-existing origin/derived/estimate
  concepts. `Task.origin` (case dataset marker) and `probability_estimate` (forecasting) are
  unrelated. `ClaimProvenance.provenance_state` (`modelled`/`published_literature`) is the
  **claim** layer; the new `value_origin` is the **evidence-value** layer — related but not a
  duplicate. No second origin enum was introduced.

## New value-origin contract (additive, minimal)

- `VALUE_ORIGINS = (source_reported, system_derived)` — the smallest stable distinction; these are
  the only *resolved* origins.
- `QAEvidenceItem` gains optional fields: `value_origin` (**fail-closed default `None` =
  unresolved** — see hardening patch below), `reported_value`, `derivation_method`,
  `input_evidence_ids`, `derivation_note`.
- `ClientValueClaim{ evidence_id, claimed_origin, claimed_source_ids }` — a client's explicit,
  structured origin assertion about one value (no NLP).
- `ClientFinding.value_claims: list[ClientValueClaim]` (default `[]`).
- Value origin is **categorical**, not ordered (see Hardening II): `ALLOWED_CLIENT_ORIGINS` maps
  each resolved internal origin to the client claims compatible with it (same category, or a drop
  to `unspecified`). Separate from `SUMMARY_STRENGTH_ORDER`.

## Binding rules added (`check_value_origin`, wired into `final_binding_check`)

- **Origin monotonicity** — `rank(claimed_origin) > rank(value_origin)` (e.g. derived →
  source_reported) → `model_output_to_literature_fact` (BLOCKER). Independent of strength.
- **No invented lineage** — a client may attribute a derived value only to sources within its
  derivation lineage (`input_evidence_ids` → their `source_id`s) → else
  `artifact_source_binding_drift`.
- **Value origin resolves** — a client value claim must point to a real evidence item.
- **Source-reported retains binding** — a referenced `source_reported` value needs a resolvable
  `source_id`.
- **Derived inputs resolve** — a referenced `system_derived` value's `input_evidence_ids` must all
  exist.

QA code `model_output_to_literature_fact` is a pipeline-QA code (namespace disjoint from the
frozen four-label claim taxonomy — asserted in tests). No claim label was modified.

## Regression fixture

`tests/fixtures/pipeline_qa/qa_modelled_value_origin.json` — fully synthetic, generic: two
source-reported inputs (E1, E2) feed one Agent Arena derived estimate (D1, `system_derived`,
inputs E1+E2, method M). No commercial/LaVita identity, no private analysis, no verbatim
literature. Structurally isolated (data class C) like the slice-1 fixture.

## Tests (1328 → 1342, +14)

`test_artifact_binding_value_origin.py`: 1 valid derived passes · 2 derived→literature blocked
(core regression) · 3 source-reported stays bound · 4 source-reported w/o binding blocked · 5
missing derived input blocked · 6 invented source attribution blocked · 7 origin axis independent
of strength · 8/8b cautious `unspecified` / omitted claim pass · 19 parametrized invariant
(system_derived may never be claimed source_reported) · QA-code-not-a-label.
`test_pipeline_qa_isolation.py`: slice-2 fixture contributes 0 cases (Test 9). First-slice
regressions (symmetry, binding, strength monotonicity, leakage) remain green (Test 10, full suite).

## Backward compatibility & versioning

- Forensic report **6.3.0: unchanged**.
- `FORENSIC_RECORD_SCHEMA_VERSION` kept at **0.1.0**: all new fields are optional with defaults,
  so existing 0.1.0 records (incl. the slice-1 fixture) remain valid unchanged; nothing consumes
  or version-gates the string, so a `0.2.0` bump would carry no meaning. The extension is
  backward-compatible within the internal Phase-7B contract.
- Ruff: clean on all created/modified files; pre-existing repo-wide debt untouched.

## Known limitations (out of this slice)

Search-scope gate / Level-D negative-existence logic; PDF/HTML post-render extraction; free-text
"sounds published" classification; broader origin categories (author_calculated, externally_
modelled, …); LLM critics. The origin check operates on structured objects only.

## Curator hardening patch — fail-closed value origin (post-review correction)

**Development history, recorded honestly.** The initial slice-2 implementation defaulted a missing
`QAEvidenceItem.value_origin` to `source_reported`. Curator review identified this as **unsafe**:
absence of provenance metadata must not silently become a positive source attribution — exactly
the failure this slice exists to prevent. The contract was hardened to **fail closed**:

- `value_origin` default changed `source_reported → None` (unresolved). `None` never counts as
  source-reported.
- New QA code `unresolved_value_origin` (separate namespace; not a claim label). A **client-visible
  value** — one with an explicit `ClientValueClaim`, or a referenced value carrying a
  `reported_value` — whose parent `value_origin` is unresolved → BLOCKER, `releasable = false`. No
  origin is *inferred* from derivation metadata; explicit provenance is required.
- Source-binding strengthened: a `source_reported` value now requires **positive** binding —
  both a `source_id` **and** a locator/span (`exact_reference`). (A deeper source-object /
  value-representation model is a documented later limitation; the current locator primitive is
  `exact_reference`.)
- `ORIGIN_STRENGTH_ORDER` renamed `VALUE_ORIGIN_ORDER` (value origin is not evidence strength).
- Backward compatibility preserved: slice-1 records (no `value_origin`, no `value_claims`, no
  `reported_value`) are **not** retroactively blocked — their evidence is not a client-visible
  value. Verified by test G and the full suite.

Freeze: `NO VALUE ORIGIN ≠ SOURCE-REPORTED`; client-visible quantitative provenance fails closed
when origin is unresolved. Hardening tests: default-is-unresolved, A (omitted→blocked), B
(derivation metadata does not infer origin), C/D/E (explicit origins unchanged), F (source_reported
without locator blocked), G (slice-1 backward-compatible). Tests 1342 → 1350 (+8).

## Curator hardening II — categorical provenance (not a total order)

**Second post-review correction.** The fail-closed patch introduced `VALUE_ORIGIN_ORDER`
(`unspecified < system_derived < source_reported`) and a `rank(client) ≤ rank(internal)`
monotonicity. Curator review found this **semantically too strong**: value origin is not an
evidential-strength axis, and a total order silently *allowed* `internal source_reported → client
system_derived` (rank 1 < 2) — a provenance falsification. `source_reported` and `system_derived`
are **distinct categories**; neither may be substituted for the other.

- Removed `VALUE_ORIGIN_ORDER` and `_origin_rank`. Replaced with `ALLOWED_CLIENT_ORIGINS` —
  explicit categorical compatibility: `{source_reported → {source_reported, unspecified},
  system_derived → {system_derived, unspecified}}`. `PROVENANCE MAY BE OMITTED, NOT REWRITTEN.`
- Both cross-category rewrites are release-blocking: `system_derived → source_reported` =
  `model_output_to_literature_fact` (preserved); `source_reported → system_derived` = the new,
  smallest precise code `source_reported_to_modelled_fact` (both falsify provenance).
- `unspecified` remains a client-only loss of attribution detail; it never alters the internal
  record. Fail-closed unresolved rule and source/derivation binding rules are preserved unchanged.

Value origin is now **categorical provenance** — not evidence strength, confidence, search
certainty, or claim provenance; no generalized certainty lattice exists. Tests 1350 → 1359 (+9):
a 6-cell compatibility matrix (A–F), an explicit "source_reported may not become derived", an
origin/strength-independence test (H), and a reverse-code-is-not-a-label check.

## Next recommended step (one)

**Search-Scope Gate** (Phase-7B): the last major un-started representation control; it introduces
the negative-evidence lattice (A–D, "NOT FOUND ≠ DOES NOT EXIST") and pairs naturally with the
provenance/derivation dimensions now in place. Justification in the final report §NEXT.
