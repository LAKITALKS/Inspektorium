# Phase 5.05h — Contamination Audit (annotator-facing material)

Scanned: `README_FOR_FINAL_REVALIDATOR.md`, `FXR-731.md`,
`AgentArena_Final_Revalidation_Bundle.md`, and the response sheets.

Scan terms: BIAA-013, RVAL-001, source case identifiers (study-forensics-*, case_public_001,
case037), gold_label, gold justification, `correlation_vs_causation` as an expected verdict,
previous response, previous vote, Opus, GLM, Gemini, Anthropic, agreement, majority, kappa,
curator decision, remediation result, holdout eligibility, correct answer, expected label.

## Result: **NONE — clean.**
No annotator-facing file contains any BIAA/RVAL identifier, real case ID, gold label, prior
response/vote, model name, agreement/majority/kappa value, curator decision, remediation
result, holdout reference, or expected/correct answer.

### Legitimate taxonomy definitions (not leakage)
- The bundle's taxonomy-reference section naturally contains all four label names (`solid`,
  `overclaim`, `correlation_vs_causation`, `mechanism_vs_evidence`) — these are the taxonomy the
  revalidator must apply, **not** an indication of which label applies to FXR-731.

### Legitimate ordinary-language evidence terms (not leakage)
- "Observational design — cannot prove causation" and the co-author's "associated with …" are
  verbatim evidence text from the source study — evidence caveats, not answer cues, and not the
  snake_case taxonomy token.

### Confirmation
- The **FXR-731 packet itself** contains **no** snake_case taxonomy token (`gold_label`,
  `correlation_vs_causation`, `overclaim`, `mechanism_vs_evidence`).
- **No annotator-facing text indicates which label applies to FXR-731.** The RVAL→BIAA mapping
  and the gold label appear only under `internal_only/`.
