# Phase-5B Haiku 4.5 Full Replication — H0→H1 Final Report

**Verdict:** `POST-REPAIR HAIKU 4.5 FULL REPLICATION COMPLETE — 420-SLOT H0→H1 COMPARISON READY FOR HUMAN REVIEW — NO SONNET EXECUTED`

---

## 1. Execution verdict
All 420 authorized analytical slots executed against the exact snapshot
`claude-haiku-4-5-20251001` under the prospective taxonomy-aligned prompt. Raw
package frozen, deterministic analysis complete, delivered-state post-run QA
green (1855/1855), authorization revoked to a non-executable state. No Sonnet,
no other model, no extra replications, no semantic retries.

## 2. Starting git state
- branch: `repair/pre-phase8-integrity`
- start HEAD: `a6b3f8e9e431c13f0ba6bd1cf8873070654b4b55` (== expected baseline)
- tracked: clean; untracked: 40 pre-existing non-material files (`.DS_Store`, `Dataset*.pdf`, root `run_*.py`, `cases/`, `research/` …). None are material runtime overrides (`inspect_source_state.valid == True`).

## 3. Experiment identity
- **H0** = historical Phase-7 Haiku condition (frozen, reference-only, prompt `study_forensics_prompt/v1-historical-phase7`).
- **H1** = current repaired Agent Arena Haiku condition (prospective, prompt `study_forensics_prompt/v2-taxonomy-aligned-phase5a`).
- Both: exact model `claude-haiku-4-5-20251001`, same frozen 84-unit universe, N=5, 420 slots. H0 responses were **not** reused as H1 output.

## 4. Historical reference reconstruction (integrity anchors, independently recomputed)
| Anchor | Registered | Recomputed | Match |
|---|---|---|---|
| specification_fingerprint | d5de4599… | d5de4599… | ✓ |
| raw_records / freeze / analysis / manifest / call_plan sha256 | (5 hashes) | (5 hashes) | ✓ all |
| aggregate_result_set_fingerprint | b994672e… | b994672e… | ✓ |
| H0 unit-modal accuracy | 61/84 = 0.726190 | 61/84 = 0.726190 | ✓ |
| H0 Brier | 0.240072 | 0.240072 | ✓ |
| H0 ECE 5-bin / 10-bin | 0.213738 / 0.217167 | 0.213738 / 0.217167 | ✓ |
| H0 mean confidence | ~0.94 | 0.939929 | ✓ |
| H0 per-gold solid/overclaim/CvC/ME | 13/13, 44/44, 4/10, 0/17 | identical | ✓ |
| H0 unanimity | 84/84 | 84/84 | ✓ |

## 5. Scientific universe equivalence
Same 84 unit ids (ordered), 34 bases (14 boundary + 16 adversarial + 4 neutral),
50 variants in 10 clusters, identical gold (solid 13, overclaim 44,
correlation_vs_causation 10, mechanism_vs_evidence 17), N=5. Scientific manifest
fingerprint `55217a9d…`. H0 and H1 draw from one `resolve_evaluated_units`
resolution → identical universe and gold. **YES / YES / YES.**

## 6. H0→H1 preregistered contract differences
- Artifact: `analysis/phase5b_haiku_full_replication/h0_h1_contract_delta_preregistration.json`
- content fingerprint `53330eee…`; file sha256 `09cad8fd…`; companion `.md`.
- **32 material differences** registered; **6 can affect model output**, all
  facets of the single intended generation-time change (system prompt v1→v2:
  KEY RULE + PRIORITY RULE) plus the uncontrolled temporal/provider confound.
  The 84 unit user payloads are byte-identical; sampling parameters identical.

## 7. Runtime parameter comparison (H0 = H1)
temperature 0.0 · top_p OMITTED · seed UNSUPPORTED · max_tokens 4096 · timeout
120s · transport retries ≤2 · semantic retries PROHIBITED. Identical
(SHARED_RUNTIME 6.1). Runtime-contract fingerprints differ only because of the
prompt condition and representation evolution, not sampling.

## 8. Execution authorization (scope + lifecycle)
One-shot `AUTHORIZED_FOR_REAL_EXECUTION` (source `tracked_governance_approval`):
420 slots, model key `haiku` only, prompt condition
`study_forensics.taxonomy_aligned.v2`, 1 guarded batch, 0 manual restarts, USD
6.00 cap. Lifecycle: activated (commit `3834644`) → one-shot lease claimed
before provider construction → executed → revoked to `CONSUMED` baseline (commit
`13bf67a`). Final budget 0, model keys []. Sonnet/other budget: 0.

## 9. Cost guard (estimate vs actual)
- Estimate (frozen cost gate): input 599,105 tok, output 604,640 tok, **$3.622305**; cap $6.00.
- Actual: input 599,105 tok, output 617,314 tok, **$3.685675**. Within cap.

## 10. Fresh authorized-state canonical QA
Pinned Phase-5B QA profile v2, WITH authorization active: **369 collected, 369
passed, 0 failed, 0 errors, 0 skipped.** Confirms the repaired authorization
invariant (both authorized and unauthorized plan states pass canonical QA).

## 11. Execution accounting
- planned analytical slots: **420**
- authenticated reused H1 slots: **0** (fresh run)
- new scientific slots invoked: **420**  → 0 + 420 = 420 ✓
- provider method invocations: 420 · HTTP/provider attempts: **421** (exactly one SDK transport retry) · transport failures: 0
- terminal attempts: 420 · classification-valid: 420 · classification-invalid: 0 · calibration-valid: 420 · calibration-invalid: 0 · analytically complete: 420
- parser failures: 0 · missing records: 0 · duplicate keys: 0 · provider failures: 0
- semantic retries: 0 · manual restarts: 0 · provider constructions: haiku 1 / sonnet 0 / other 0

## 12. Raw freeze
- run namespace: `analysis/phase5b_haiku_full_replication/run/haiku/`
- raw records: `raw/haiku_raw_records.jsonl` (420) · freeze: `haiku_raw_result_freeze.json`
- aggregate_result_set_fingerprint (stored == recomputed): **`79ddfa509d302dfcaf5464060e3df4f8a25f7e76ecdf7a68a9a409281aca01ec`**
- comparison fingerprint: `e0182db1…` · analysis_status: COMPLETE · missing keys: 0

## 13. H1 results (numerator/denominator)
| Metric | Value |
|---|---|
| Unit-modal accuracy | 78/84 = 0.928571 |
| Replication-level accuracy | 390/420 = 0.928571 |
| Base accuracy | 32/34 = 0.941176 |
| Variant accuracy | 46/50 = 0.920000 |
| Brier (calibration-valid) | 0.068160 (den 420) |
| ECE 5-bin (primary) | 0.006952 (den 420) |
| ECE 10-bin (sensitivity) | 0.016238 (den 420) |
| Mean confidence | 0.935524 (den 420) |
| Per gold: solid | 13/13 |
| Per gold: overclaim | 39/44 |
| Per gold: correlation_vs_causation | 9/10 |
| Per gold: mechanism_vs_evidence | 17/17 |
| Boundary / Adversarial / Neutral bases | 13/14 · 16/16 · 3/4 |
| Perturbation variants | 46/50 |
| Perturbation clusters (label-consistent / all-correct) | 9/10 · 9/10 |
| Replication stability (unanimous 5/5) | 84/84 |

## 14. H0 vs H1 deltas
| Metric | H0 | H1 | Δ |
|---|---|---|---|
| Unit-modal accuracy | 0.726190 (61/84) | 0.928571 (78/84) | **+0.202381** |
| Replication accuracy | 0.726190 (305/420) | 0.928571 (390/420) | +0.202381 |
| Base accuracy | 0.705882 (24/34) | 0.941176 (32/34) | +0.235294 |
| Variant accuracy | 0.740000 (37/50) | 0.920000 (46/50) | +0.180000 |
| Brier | 0.240072 | 0.068160 | **−0.171912** |
| ECE 5-bin | 0.213738 | 0.006952 | **−0.206786** |
| ECE 10-bin | 0.217167 | 0.016238 | −0.200929 |
| Mean confidence | 0.939929 | 0.935524 | −0.004405 |
| solid | 13/13 | 13/13 | 0 |
| overclaim | 44/44 | 39/44 | −5 |
| correlation_vs_causation (CvC) | 4/10 | 9/10 | +5 |
| mechanism_vs_evidence (ME) | 0/17 | 17/17 | **+17** |
| unanimous units | 84/84 | 84/84 | 0 |
| boundary / adversarial | 10/14 · 11/16 | 13/14 · 16/16 | +3 · +5 |
| perturbation status | 37/50; 7/10 clusters all-correct | 46/50; 9/10 clusters all-correct | +9; +2 |

## 15. 84-unit paired transition analysis
- CORRECT→CORRECT: 56 · WRONG→CORRECT: 22 · CORRECT→WRONG: 5 · WRONG→SAME_WRONG: 1 · WRONG→DIFFERENT_WRONG: 0 (sum 84 ✓; H0 correct 61, H1 correct 78 ✓).
- Modal-label transition matrix: overclaim(H0) → {overclaim 40, mechanism_vs_evidence 17, correlation_vs_causation 10}; correlation_vs_causation(H0) → correlation_vs_causation 4; solid(H0) → solid 13.
- Topology: ME→overclaim confusion **17 → 0** (fully eliminated); overclaim→ME 0 in both. The dominant driver is the 17 ME units H0 uniformly mislabeled `overclaim` and H1 now labels ME correctly, plus 6 CvC gains.

## 16. Every modal-prediction change (27 units)
**WRONG→CORRECT (22):** BND-005 (→CvC), BND-009 (→ME), BND-010 (→ME),
ADV-003 (→ME), ADV-004 (→ME), ADV-006 (→CvC), ADV-013 (→ME), ADV-017 (→ME),
NEU-004 (→ME), PRT-03-P2/P3/P4 (→CvC), PRT-04-P1/P2/P3/P4/P5 (→ME),
PRT-06-P1/P2/P3/P4/P5 (→ME). *(all H0=overclaim)*
**CORRECT→WRONG (5):** NEU-002, PRT-02-P1, PRT-02-P2, PRT-02-P3, PRT-02-P4
(all gold=overclaim, H1=correlation_vs_causation).
All changed units are unanimous 5/5 in both conditions.

## 17. Error ecology
- **Resolved H0 errors (22):** the entire ME family (17/17) plus 5 CvC/boundary/adversarial cases H0 called `overclaim`.
- **New H1 errors (5):** overclaim gold over-attributed to `correlation_vs_causation` — NEU-002 and cluster PRT-02 (P1–P4). The v2 explicit CvC guidance over-applies here.
- **Persistent error (1):** `P7A-BND-004` (gold correlation_vs_causation) called `overclaim` in both H0 and H1.
- Perturbation clusters improving: PRT-03, PRT-04, PRT-06. Degrading: PRT-02 (4/5 variants flip overclaim→CvC; the one label-inconsistent cluster).

## 18. Calibration analysis
- Primary ECE (5-bin, edges 0/.2/.4/.6/.8/1): 0.213738 → 0.006952 (den 420 both).
- Sensitivity ECE (10-bin): 0.217167 → 0.016238.
- Brier: 0.240072 → 0.068160 (den 420 both).
- Mean confidence essentially unchanged (0.9399 → 0.9355); the calibration gain
  comes from accuracy rising to meet the high confidence, not from confidence moving.
- All 420 H1 records are calibration-valid; no missing/invalid confidence; no denominator shrinkage.

## 19. Interpretation limitation
> **H0→H1 is a whole repaired-system comparison. Multiple contract changes are
> confounded. The experiment does not identify the causal contribution of an
> individual repair. An improvement or degradation must not be attributed to a
> specific repair without a controlled ablation.**

The only intended generation-time difference is the system prompt (v1→v2: KEY
RULE + PRIORITY RULE); an uncontrolled temporal/provider confound (same snapshot,
different wall-clock) also exists. Sampling parameters, unit payloads, ordering,
and model are identical. Bounded to Haiku; S0→S1 and H1↔S1 are future tasks.

## 20. Historical immutability check
Before and after execution, all five historical Phase-7A artifacts reproduce
their registered sha256; `git diff v0.10.0-phase7-closeout HEAD -- analysis/phase7a_execution/`
is empty. No historical overwrite, cleanup, or relabeling.

## 21. Post-run QA
- Delivered (revoked) state: full suite **1855 passed, 0 failed, 0 errors, 0 skipped** (`post_run_qa_execution.json`).
- While-authorized snapshot (preserved as `post_run_qa_while_authorized.json`): 1852/1855, 3 transient failures, all in `tests/test_authorization_state_invariant.py`, each asserting the on-disk plan ≠ AUTHORIZED_FOR_REAL_EXECUTION — i.e. correctly detecting the temporarily active authorization. Resolved by revocation; no test or result changed.

## 22. Authorization final state
`CONSUMED_AFTER_SINGLE_GUARDED_INVOCATION`, budget 0, model keys [],
`production_authorization_errors` non-empty (non-executable). One-shot lease
present (blocks any re-invocation). Plan file byte-identical to the pre-authorization
verified baseline; the CONSUMED audit anchor legitimately preserves the original
pre-repair invocation record. Further Haiku execution requires new human authorization.

## 23. Git end state
- end HEAD: `3849de0`
- new commits: `3834644` (authorize + preregistration), `13bf67a` (results + revoke), `3849de0` (green post-run QA).
- tracked working tree: clean. Untracked: the 40 pre-existing non-material files + local scratchpad (outside repo). Push status: **not pushed** (no upstream).

## 24. Provider summary
Haiku scientific slots: 420. Transport retries: 1 (one HTTP re-attempt within one
scientific slot; 421 total attempts). Sonnet calls: **0**. Other model calls: **0**.
Non-generative preflight: 1 `models.retrieve` metadata lookup (0 generations).

## 25. Actual token usage and cost
- input tokens: 599,105 · output tokens: 617,314 · cache: none
- pricing: $1.00 / M input, $5.00 / M output
- **billed/estimated cost: $3.685675** (≤ $6.00 authorized cap)
