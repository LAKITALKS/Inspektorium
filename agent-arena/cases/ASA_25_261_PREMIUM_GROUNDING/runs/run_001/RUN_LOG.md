# RUN LOG — ASA 25/261 · RUN 001

Case `ASA_25_261_PREMIUM_GROUNDING` · run `run_001` · 2026-08-23

Deterministic stage log of the executed pipeline.

```
STAGE 0 — INPUT INTEGRITY
  input/01_FINAL_EVIDENCE_FREEZE_v1.md: 530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069 (119130 bytes)
  provenance/01_CLOSED_CASE_SCIENTIFIC_EVIDENCE_PACKAGE_v1.md: 193877cacc4a3f3393b86b639a965a9446a3ba467b00c8baa632c024720c97d4 (109112 bytes)
  provenance/02_TARGETED_EVIDENCE_CLOSURE_v1.md: 7ae78f2b84cdca24fe8c327173672706fcf9a0e6ed01c88f6291bb42a151474b (34052 bytes)
  provenance/03_PRE_FREEZE_TERMINOLOGY_ROBUSTNESS_CHECK_v1.md: 4d8df9fb9c145cba278e5a63ccf74074e3e5de3656faf56daff8b612ddc0fed2 (18068 bytes)
  CANONICAL FREEZE INTEGRITY: PASS
STAGE 1 — FROZEN CLAIM INGESTION: 26 active propositions
STAGE 2/3 — CLAIM-FORENSICS REPORTS + VALIDATION
  M-01a: report built + validated (label=solid, status=complete)
  M-01b: report built + validated (label=overclaim, status=complete)
  M-02: report built + validated (label=mechanism_vs_evidence, status=complete)
  M-03: report built + validated (label=mechanism_vs_evidence, status=complete)
  I-01: report built + validated (label=overclaim, status=complete)
  I-02: report built + validated (label=overclaim, status=complete)
  S-01: report built + validated (label=overclaim, status=complete)
  S-02: report built + validated (label=overclaim, status=complete)
  S-03: report built + validated (label=overclaim, status=complete)
  S-04: report built + validated (label=overclaim, status=complete)
  P-01: report built + validated (label=overclaim, status=complete)
  P-02: report built + validated (label=overclaim, status=complete)
  P-03: report built + validated (label=overclaim, status=complete)
  P-04: report built + validated (label=overclaim, status=complete)
  P-05: report built + validated (label=overclaim, status=complete)
  V-01: report built + validated (label=overclaim, status=complete)
  E-01: report built + validated (label=overclaim, status=complete)
  E-02: report built + validated (label=overclaim, status=complete)
  E-03: report built + validated (label=overclaim, status=complete)
  C-01: report built + validated (label=overclaim, status=complete)
  R-01: report built + validated (label=overclaim, status=complete)
  W-01: report built + validated (label=overclaim, status=complete)
  X-01: report built + validated (label=overclaim, status=complete)
  X-02: report built + validated (label=overclaim, status=complete)
  Q-01: report built + validated (label=None, status=insufficient_input)
  Q-02: report built + validated (label=None, status=insufficient_input)
  26/26 reports valid against schema 6.3.0
STAGE 4 — REPRESENTATION RECORD
  record fingerprint: 98bb2eec89f6247d9ad5fb6860654377c034d619e66177b8da778c91aa8a97e0
STAGE 5 — RELEASE GATE
  finding_artifact_binding: ran (0 findings)
  summary_strength_monotonicity: ran (0 findings)
  evidence_symmetry: ran (0 findings)
  value_origin_provenance: ran (0 findings)
  search_scope_binding: ran (0 findings)
  releasable=True — no blocking (critical/major) QA findings
STAGE 6 — CROSS-PROPOSITION CONSISTENCY
  [PASS] M-01a / M-01b separation preserved
  [PASS] Downstream mechanism does not assume M-01b
  [PASS] X-01 does not assume immune benefit
  [PASS] X-01 does not represent sleep as uniformly established
  [PASS] E-03 preserves GROUNDING COMPONENT NOT ISOLABLE
  [PASS] No exact-product verdict assumes study-product identity
  [PASS] Q-01 / Q-02 not adjudicated on biomedical absence
  [PASS] Bounded negative search routed only where documented
  [PASS] Overlapping cohorts not counted as independent replications
  [PASS] Within-group significance not converted to between-group effect
  [PASS] H31 exact p-value preserved
  [PASS] H30 actigraphy timepoint left unresolved
  [PASS] H10 2.70 not read as a health improvement
  [PASS] Verdicts not derived mechanically from preparation state
  [PASS] ASA outcome quarantined
STAGE 7 — OUTPUT FREEZE
  wrote RUN_CONFIG.md
  wrote INPUT_INTEGRITY_REPORT.md
  wrote AGENT_ARENA_ADJUDICATION.md
  wrote PROPOSITION_VERDICTS.md
  wrote ADVERSARIAL_REVIEW.md
  wrote STEELMAN_REVIEW.md
  wrote CONSISTENCY_CHECK.md
  wrote RUN_LOG.md
```
