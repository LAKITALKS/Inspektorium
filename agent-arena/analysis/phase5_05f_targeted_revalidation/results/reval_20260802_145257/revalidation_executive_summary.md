# Phase 5.05f — Targeted Revalidation Executive Summary (PROVISIONAL — CURATOR DECISION REQUIRED)

**run:** reval_20260802_145257 · **commit:** 902fea74bf00 · **tag:** v0.8.7-targeted-revalidation-prep
**study:** targeted_versioned_blind_model_revalidation · **acceptance criteria:** 5.05f/1.0 (frozen, unchanged)

This is a targeted three-family blind **model** revalidation of two revised packets — **not** human IAA.
Revalidators: X=Opus 5, Y=GLM 5.2, Z=Gemini 3.5 Flash (Extra Thinking). Two cases; simple descriptive
agreement only (kappa **not** computed for a two-case sample).

## RVAL-001 → BIAA-013_v2 (gold `correlation_vs_causation`) — **CURATOR_REVIEW_REQUIRED**
- **Primary labels:** X `correlation_vs_causation` · Y `correlation_vs_causation` · Z `correlation_vs_causation` → **3/3 = gold, unanimous**.
- **Packet quality:** source_voice_clear yes **2/3**, claim_isolated yes **2/3**, evidence_context_understandable yes **3/3**.
- **Material packet defect:** yes 0 · **uncertain 1** (X) · no 2.
- Numerical criteria 1–4 **pass**, but **Revalidator X (Opus 5)** flagged `claim_isolated = no`,
  `source_voice_clear = uncertain`, `material_packet_defect = uncertain`,
  `multiple_competing_claims_present = yes`, `recommended_human_review = yes` (confidence 0.6), noting
  that RVAL-001 — unlike RVAL-002 — carries **no explicit claim-isolation instruction**, making the target
  reading-dependent. Frozen criterion 5 requires this individual `uncertain` flag to be curator-resolved;
  an `uncertain` is **not** treated as `no`.
- **Disagreement:** absent on taxonomy label (soft 0, serious 0); the open item is packet-remediation quality.

## RVAL-002 → BIAA-016_v2 (gold `overclaim`) — **PASS_CANDIDATE**
- **Primary labels:** X `overclaim` · Y `overclaim` · Z `overclaim` → **3/3 = gold, unanimous**.
- **Packet quality:** source_voice_clear, claim_isolated, evidence_context_understandable all **3/3 yes**.
- **Material packet defect:** none (0 yes, 0 uncertain). No individual flag. No unresolved curator item.

## Provisional overall disposition
**B. TARGETED REVALIDATION PARTIALLY PASSED — CURATOR REVIEW REQUIRED.**
One packet (RVAL-002 / BIAA-016_v2) is a clean PASS_CANDIDATE; the other (RVAL-001 / BIAA-013_v2)
numerically passes but has an unresolved individual material-defect/claim-isolation flag requiring curator
judgment. The disposition considers taxonomy outcome (all agree on gold in both cases) **separately** from
packet-remediation quality (RVAL-001 still has a claim-isolation gap per one revalidator).

Passing Phase 5.05f only makes a case eligible for **later** holdout consideration; **no case is declared
holdout-eligible here, and no holdout is created or frozen.** Confidence values are uncalibrated self-reports.
No response was altered; no revalidator was excluded.
""")
