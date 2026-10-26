# Phase 6.3 — Risk Register

Risks specific to shipping a product-facing claim-forensics report prototype, with the
mitigation encoded in `forensic_report.py` and its tests.

| id | risk | L | I | mitigation | status |
|----|------|---|---|-----------|--------|
| **P-1** | **Classification read as proof of falsity** — a label taken as "the claim is false" | med | high | every verdict carries `classification_note`; renderers print it; `test_classification_not_presented_as_falsity` | mitigated |
| **P-2** | **Confidence corruption** — missing/invalid confidence shown as 0.0 | med | high | reuse `classify_confidence`; VALID/MISSING/INVALID; `confidence_value` null unless VALID; no coercion; multiple tests | mitigated |
| **P-3** | **Invented facts in a rewrite** — a rewrite adds a statistic not in the input | med | high | numeric-containment guard blocks & drops the rewrite; warning recorded; `test_rewrite_with_new_number_is_blocked` | mitigated (numeric guard; not full NL entailment — documented) |
| **P-4** | **`mechanism_vs_evidence` scope creep** — broadened to a generic mechanism/evidence category | med | high | biological verdict title; scoped failure modes; `test_mechanism_vs_evidence_is_biologically_scoped`; `field_semantics.md` note | mitigated |
| **P-5** | **False harm quantification** — risk read as a computed harm probability | med | high | qualitative frozen vocabulary + `not_a_harm_probability_note`; no numeric risk formula | mitigated |
| **P-6** | **Parser failure masquerading as a verdict** | low | high | `parse_ok=false` forces `parser_failure`, `predicted_label=null`; overrides optimistic status; tested | mitigated |
| **P-7** | **Identity leakage** — canonical/BIAA/HLD/DEV id, salt, or private path in input/report | low | critical | leakage scan on input and report; build raises; `test_private_identifiers_and_paths_rejected` | mitigated |
| **P-8** | **Silent gap-filling** — a missing field defaulted to a confident value | med | med | missing → explicit MISSING/unknown/null + warning; empty lists stay visible; tested | mitigated |
| **P-9** | **Non-determinism** — build-time clock or unordered keys change the digest | low | med | no wall-clock injected; sorted-key canonical bytes; determinism tests across processes | mitigated |
| **P-10** | **Hidden thresholding / model selection** creeping into a "report" module | low | high | module is pure render/validate; `test_no_threshold_or_model_selection_logic` | mitigated |
| **P-11** | **Synthetic mistaken for real performance** | med | med | `synthetic_fixture` default true + warning; synthetic banner on every rendering; all examples labelled | mitigated |
| **P-12** | **Schema drift** — unexpected fields silently accepted | low | med | `additionalProperties:false` mirror; unexpected-field rejection tests; frozen vocabularies enumerated | mitigated |
| **P-13** | **Over-long/decorative prose** exceeding evidence | low | med | compact bullet renderers, no giant tables; prose bounded to supplied fields | mitigated |

**Documented residual:** P-3's guard is a conservative **numeric-containment** check, not
a natural-language entailment verifier; it blocks fabricated numbers but a reviewer
should still read rewrites for non-numeric overreach. This is stated in
`report_design_principles.md` §6 and `phase6_3_limitations` context.
