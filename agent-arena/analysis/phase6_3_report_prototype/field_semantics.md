# Phase 6.3 — Field Semantics

Field-by-field meaning of the claim-forensics report (schema
`forensic_report_schema.json`, version `6.3.0`). Frozen vocabularies are **reused** from
the existing engine where they already exist; see the source of truth column.

## A. Report identity and status

| field | meaning | source of truth |
|---|---|---|
| `report_schema_version` | `6.3.0` (const) | this phase |
| `report_id` | opaque id; passthrough or `FR-<input_digest[:12]>` | derived |
| `generated_at` | ISO-8601 passthrough from input, or `null`; **no build-time clock** | input |
| `analysis_status` | `complete · parser_failure · insufficient_input` | derived |
| `synthetic_fixture` | bool; **defaults to `true`** if absent (prototype-safe) + warning | input/default |
| `development_or_production_status` | `development · production` (default `development`) | input |
| `status_banner` | human banner lines incl. the synthetic marker | derived |

## B. Claim under review (`claim`)

`claim_text` (required, non-empty) · `claim_context` · `claim_source_reference` ·
`claim_scope` · `intended_reader_or_audience`. Absent optional fields render as
`_not supplied_`; a missing source is **never invented**.

## C. Forensic verdict (`verdict`)

- `predicted_label` — frozen taxonomy `solid · overclaim · correlation_vs_causation ·
  mechanism_vs_evidence`, or `null` for `parser_failure` / `insufficient_input`.
  (`study_forensics_checker.py` is the label source of truth.)
- `verdict_title` — fixed plain-language title per label (`VERDICT_TITLES`); validated to
  stay consistent with `predicted_label`.
- `verdict_summary` — neutral, evidence-relationship summary; never asserts factual falsity.
- `confidence_status` — `VALID · MISSING · INVALID` from
  `confidence_validity.classify_confidence` (Phase 6.1).
- `confidence_value` — a number in `[0,1]` **only** when `VALID`; otherwise `null`.
  Booleans and out-of-range values are `INVALID` → `null`. **Never coerced to 0.0.**
- `confidence_interpretation` — fixed text for the status.
- `classification_note` — the "not proof of factual falsity" statement.

## D. Evidence assessment (`evidence`)

- `evidence_items[]` — `{text, source_reference|null, tier, role, why_it_matters|null}`.
  - `tier` — **reused evidence-tier vocabulary** from `runner.py`:
    `cell · animal · biomarker · limited_human · clinical_human` (weakest→strongest),
    plus `unknown` and `not_applicable`.
    (weakest) cell → in-vitro; animal → mouse/rat models; biomarker → surrogate endpoints;
    limited_human → small/pilot/failed-primary human; clinical_human → large RCT / positive
    primary (strongest).
  - `role` — `supporting · weakening · contradictory · missing_expected`
    (`schemas.EvidenceRole`).
- `supporting[]`, `contradicting_or_limiting[]` — free-text summaries.
- `missing_comparison_group`, `missing_causal_chain`, `missing_human_evidence` —
  `true · false · null`; `null` renders as "unknown / not assessed" (never silently `false`).
- `evidence_sufficiency` — `sufficient · insufficient · unknown` (default `unknown`).

## E. Failure-mode analysis (`failure_modes`)

`detected[]` of `{mode, rationale, evidence_refs[]}`; `none_detected` bool. A mode is
**echoed from the analysis, never inferred by the builder**, and each requires a
non-empty `rationale`. Frozen `mode` vocabulary:

| mode | meaning | maps to |
|---|---|---|
| `correlation_vs_causation_conflation` | causal claim from association | `correlation_as_causation` |
| `inappropriate_generalization` | conclusion generalized beyond sample/scope | `unsupported_generalization` |
| `evidence_tier_mismatch` | evidence tier < conclusion tier | evidence-tier check |
| `unsupported_superiority_claim` | "better than / beats all" without support | overclaim family |
| `benchmark_exaggeration` | one benchmark generalized to real-world superiority | overclaim family |
| `decorative_or_weak_hedging` | hedge present but does not constrain the claim | `decorative_uncertainty` |
| `mechanism_to_human_benefit_leap` | biological/preclinical → implied human benefit | `mechanism_not_demonstrated` |
| `conclusion_exceeds_results` | conclusion beyond what results establish | `conclusion_exceeds_results` |
| `missing_comparison_group` | no control/comparison to support the claim | evidence gap |
| `missing_causal_chain` | no mechanism/design linking cause to effect | evidence gap |
| `missing_human_evidence` | human clinical tier absent | evidence gap |

**`mechanism_vs_evidence` scope is preserved:** it applies only when biological mechanism
or preclinical evidence is used to imply **human clinical benefit** — not a general
mechanism/evidence category. `mechanism_to_human_benefit_leap` / `evidence_tier_mismatch` /
`missing_human_evidence` are its supporting failure modes.

## F. Reader-impact risk (`reader_impact`)

`risk_level` (see `risk_vocabulary.md`) · `risk_rationale` ·
`likely_reader_misunderstanding` · `affected_decision_type` · `risk_uncertainty` ·
`not_a_harm_probability_note` (fixed). Absent risk → `unknown` + warning.

## G. Uncertainty (`uncertainty`)

`unresolved_questions[]` · `missing_evidence[]` · `ambiguity|null` ·
`alternative_plausible_label` (frozen label or `null`) · `alternative_label_rationale|null` ·
`scope_limitations[]` · `confidence_caveat` (fixed by status) · `development_caveat`
(present in development mode). Empty lists stay visible.

## H. Recommended revision (`recommended_revision`)

`defensible_rewrite|null` (copied verbatim from input, **never synthesized**) ·
`rewrite_available` bool · `rewrite_verification` · `rewrite_verification_note` ·
`rewrite_rationale|null` · `claims_to_remove_or_narrow[]` · `evidence_qualifiers_to_add[]` ·
`claims_that_remain_supportable[]` · `rewrite_guard{checked, unsupported_new_facts[], status}`.
`status ∈ {clean, blocked, no_rewrite}`; **blocked** drops the rewrite to `null`.

`rewrite_verification ∈ {unverified_proposal, blocked_unsupported_new_facts,
no_rewrite_supplied}`. **A present rewrite is always `unverified_proposal`:** passing the
numeric-containment guard means only that no unsupported *number* was introduced — it is
**not** factual or semantic verification. `rewrite_verification_note` states this, and both
the full report and the executive summary render the rewrite as an *unverified proposal
that still requires human review*. Where support is absent or the guard blocks the rewrite,
the report states that **no safe rewrite is available**.

## I. Provenance and audit (`provenance`)

`model|null` · `provider|null` · `prompt_contract_version|null` · `repository_commit|null` ·
`analysis_source|null` · `input_digest_sha256` · `report_generation_digest_sha256`
(recomputable by blanking itself) · `parser_status (ok · failed · unknown)` ·
`warnings[]` · `audit_trail[]`.
