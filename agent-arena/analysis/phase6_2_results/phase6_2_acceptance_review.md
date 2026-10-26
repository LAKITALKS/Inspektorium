# Phase 6.2 — Acceptance Review

**DEVELOPMENT CALIBRATION — NOT HOLDOUT.** This review checks the three-model results
and this analysis session against the pre-registered Phase 6.2 acceptance criteria
(`analysis/phase6_2_calibration/phase6_2_acceptance_criteria.md`) and risk register
(`…/phase6_2_risk_register.md`). Nothing frozen was changed after seeing results.

## Execution acceptance criteria (E-1 … E-4)

| id | criterion | disposition | evidence |
|---|---|---|---|
| **E-1** | Runs against the fingerprint-verified 27-case manifest; emits anonymized records only | **PASS (public side)** | Every envelope's `manifest_id` = `AA-DEVPOOL-6100` and `public_commitment` = `679233c6…6ae4332` equal the tracked public manifest; 27 records each; opaque `DEV-####` ids only; leakage scan clean. Private salted-fingerprint verification is runner-side; the public string binding is verified here. |
| **E-2** | Metrics computed exactly as pre-registered; bound to commitment + code commit + params + seed; reproducible | **PASS (with seed note)** | Metrics produced solely by frozen `src/agent_arena/calibration.py`; `report.params` embeds `five_bin_edges`, `ten_bin_edges`, `tau_grid`, `min_label_n`, `abstention_cost_model`; provenance embeds commitment, run_id, model, `prompt_contract_version`, `generated_at`; code commit `dd53226`. Reports regenerate **byte-for-byte** across independent processes. `seed = UNSUPPORTED` is documented (nondeterminism caveat). |
| **E-3** | Abstention reported as costed trade-off; adopted only vs the frozen conditional criterion, else "not demonstrated beneficial"; no threshold tuned then reported as unbiased | **PASS** | Full costed risk–coverage curve per model (benefit **and** cost = coverage lost + involuntary count). Conclusion: **abstention not demonstrated beneficial** on development data (Haiku/Opus baseline risk 0; Sonnet τ=0.9 benefit −0.010). No operating threshold selected; `select_operating_threshold()` remains a hard error. |
| **E-4** | No holdout; no universal-superiority claim; small-sample caveats present | **PASS** | Holdout sealed and untouched; no winner selected; `DEVELOPMENT — NOT HOLDOUT` + small-sample banners on every report; `n < 5` flagged; corr/mech (n=2) descriptive only. |

## Execution stop conditions — none triggered

| stop condition | triggered? | note |
|---|---|---|
| fingerprint / commitment mismatch | **No** | public commitment string-equal across all three envelopes |
| any holdout / `internal_only` need | **No** | analysis needed neither |
| result-driven re-tuning | **No** | no bin/threshold/cost/metric changed after results |
| any canonical id in an output | **No** | opaque `DEV`/class only; leakage scan clean |

## Risk register spot-check (post-results)

| risk | status |
|---|---|
| C-1 confidence coercion to 0.0 | **Mitigated** — 27 VALID / 0 MISSING / 0 INVALID per model; no `0.0` coercion artifact; classifier used throughout. |
| C-2 identity leakage | **Mitigated** — leakage scan of every proposed artifact is clean (no canonical/BIAA/HLD/salt). |
| C-3 threshold overfitting | **Mitigated** — fixed bins/τ grid; no threshold chosen; conclusion is "not beneficial". |
| C-4 small-sample over-interpretation | **Mitigated** — small-sample banners; per-bin/per-label n; corr/mech descriptive only; interpretation separates observed / interpretation / speculation. |
| C-5 hidden truncation | **Mitigated** — all 4 empty bins retained and shown `[empty]`. |
| C-6 aggregate drift | **Mitigated** — 8/15/2/2 verified on gold per model. |
| C-7 abstention assumed beneficial | **Mitigated** — costed both sides; benefit ≤ 0 reported honestly. |
| C-8 synthetic mistaken for real | **N/A/Mitigated** — real-run envelopes; `synthetic_fixture = false`; no synthetic labeling. |
| C-11 gold/prediction confusion | **Mitigated** — aggregate on gold only; predicted distribution reported descriptively. |
| C-12 unbound results | **Mitigated** — envelope binding verified before accepting records. |
| C-13 accuracy erased by confidence handling | **N/A** — no MISSING/INVALID present; denominators still reported separately. |

## Item for curator decision (not a blocker)

- **Opus `prompt_contract_version` carries only `system_prompt_sha256`**, not the literal
  `AA-RTC-6.2-OPUS-001` id (Haiku/Sonnet echo their id). Schema-permitted (version *or
  hash*); binding satisfied via exact model id + matching pinned sha. The curator may
  wish to have the runner re-stamp Opus's `prompt_contract_version` to echo the contract
  id for symmetry. **Not** an integrity failure and **not** a stop condition.

## Overall

All observable execution acceptance criteria **PASS**; no stop condition triggered; one
cosmetic provenance item flagged for curator decision. **Recommendation:** accept the
results for curator review as *development-set characterization*, subject to the
limitations in `phase6_2_limitations.md`. No production, ranking, or abstention-adoption
decision is authorized by these results.
