# Phase 6.4 — Acceptance Review (results session)

### DEVELOPMENT PILOT — NOT HOLDOUT

Pre-specified acceptance for the **results** session: validate the two completed envelopes,
analyze each arm, compute the frozen paired comparison, and document it under the frozen
interpretation rules — without changing any frozen artifact, without pooling, and without
committing. Each criterion carries a disposition and its evidence.

## Input-integrity gates (all must pass before paired analysis)

| # | gate | disposition | evidence |
|---|------|-------------|----------|
| 1 | exact expected run IDs | **MET** | `AA-6.2-RUN-6a3b93a24af7431e` / `AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03` — `run_id_matches_expected` ✓ |
| 2 | exact contract IDs | **MET** | `AA-RTC-6.2-HAIKU-001` / `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001` — `contract_binding_satisfied` ✓ |
| 3 | exact shared model ID | **MET** | both `claude-haiku-4-5-20251001` — `model_is_shared_pilot_model` ✓ |
| 4 | exact manifest ID `AA-DEVPOOL-6100` | **MET** | `manifest_id_matches_tracked` ✓ |
| 5 | exact public commitment `679233…4332` | **MET** | `public_commitment_matches_tracked` ✓ |
| 6 | exactly 27 records per arm | **MET** | `record_count_27` ✓ (both) |
| 7 | unique opaque DEV identifiers | **MET** | `dev_ids_unique_opaque` ✓ (27 unique, `DEV-####`) |
| 8 | identical DEV-ID set across arms | **MET** | `dev_id_set_identical_across_arms` = YES (27 common) |
| 9 | identical gold label per paired DEV | **MET** | `gold_label_identical_per_paired_dev` = YES (0 mismatches) |
| 10 | identical stratum per paired DEV | **MET** | `stratum_identical_per_paired_dev` = YES (0 mismatches) |
| 11 | gold aggregate exactly 8/15/2/2 | **MET** | `gold_aggregate_8_15_2_2` ✓ (both) |
| 12 | parser-completion state preserved | **MET** | `parser_completion_state_preserved` ✓ — 27/27, 0 failures (both) |
| 13 | confidence VALID/MISSING/INVALID preserved | **MET** | `confidence_validity_preserved` ✓ — 27/0/0 (both) |
| 14 | no missing-to-zero coercion | **MET** | `no_zero_coercion_artifact` ✓ (no confidence == 0.0) |
| 15 | no canonical IDs | **MET** | `no_identity_leakage` ✓ (leakage scan) |
| 16 | no salt | **MET** | leakage scan clean; engine rejects salt keys |
| 17 | no mapping data | **MET** | envelope fields limited to the allowed set; `records_no_unexpected_fields` ✓ |
| 18 | no private paths | **MET** | leakage scan clean; artifacts embed no private path |
| 19 | no BIAA/HLD identifiers | **MET** | leakage scan clean (`_BIAA` / `_HLD`) |
| 20 | no unexpected result fields | **MET** | `envelope_no_unexpected_fields` / `records_no_unexpected_fields` ✓ |
| 21 | no synthetic fixture mislabeled as a real run | **MET** | `not_synthetic_fixture_mislabeled_as_real` ✓ (real run_id + generated_at; no synthetic flag) |
| 22 | leakage validation clean | **MET** | `no_identity_leakage` ✓ + final artifact leakage sweep |

**Overall input integrity: PASS.** No gate failed; paired analysis proceeded.

## Per-arm analysis requirements

| requirement | disposition | evidence |
|---|---|---|
| parser completion + failure count | **MET** | 27/27, 0 failures (both) — reported separately from accuracy |
| confidence VALID/MISSING/INVALID counts | **MET** | 27/0/0 (both) |
| accuracy over all eligible records | **MET** | AA 1.000 · PO 0.889 (denominator 27) |
| correct / incorrect counts | **MET** | AA 27/0 · PO 24/3 |
| predicted-label distribution | **MET** | AA 8/15/2/2 · PO 8/12/3/4 |
| mean reported confidence | **MET** | AA 0.910 · PO 0.896 |
| confidence-valid coverage | **MET** | 100% (both) |
| binary top-label Brier | **MET** | AA 0.0093 · PO 0.0814 |
| frozen five-bin reliability table | **MET** | engine `reliability_5bin`, empty bins retained |
| descriptive ECE | **MET** | AA 0.0896 · PO 0.0811 (secondary) |
| ten-bin sensitivity (secondary only) | **MET** | engine `reliability_10bin_sensitivity` |
| fixed-threshold selective accuracy/coverage | **MET** | engine `risk_coverage_clear`, frozen τ grid |
| frozen abstention-cost | **MET** | `coverage_lost_all = 1 − coverage_all`; benefit + cost both reported |
| results by gold label | **MET** | `by_gold_label_all27`; all four labels visible |
| results by stratum | **MET** | clear / development_only / borderline separate |
| high-confidence errors | **MET** | AA 0 · PO 1 (DEV-0013 @ 0.92) |
| low-confidence correct | **MET** | none in either arm (all conf ≥ 0.72) |
| exact denominators | **MET** | accuracy 27; Brier/ECE/reliability 27 (both) |
| empty bins / small-n warnings | **MET** | empty bins shown n=0; corr/mech flagged `small_n`/`descriptive_only` |

## Paired-comparison requirements

| requirement | disposition | evidence |
|---|---|---|
| accuracy difference (AA − PO) | **MET** | +0.111 |
| Brier difference (PO − AA) | **MET** | +0.0721 |
| ECE per arm (secondary) | **MET** | 0.0896 / 0.0811 |
| mean confidence + coverage per arm | **MET** | 0.910/0.896; 100%/100% |
| parser completion per arm | **MET** | 27/27 both |
| predicted-label disagreement count | **MET** | 3 (DEV-0011, DEV-0013, DEV-0018) |
| paired correctness table (4 quadrants) | **MET** | 24 / 3 / 0 / 0 |
| opaque DEV ids for disagreements + asymmetric correctness | **MET** | listed (opaque DEV only) |
| high-confidence-error difference | **MET** | PO − AA = +1 |
| fixed-threshold selective behavior | **MET** | per-arm τ grid; PO benefit at τ≥0.8 (development-selected) |
| abstention-cost difference | **MET** | AA no benefit; PO benefit 0.077 at cost 0.115 (τ=0.8), development-selected |
| results by gold label + stratum | **MET** | see paired report |
| exact denominators | **MET** | stated throughout |

## Prohibitions upheld

| prohibition | upheld | evidence |
|---|---|---|
| no 54-case pool | **YES** | paired-by-DEV only; `no_54_case_pool` |
| no pooled accuracy/Brier/ECE | **YES** | no pooled score computed anywhere |
| no statistical-proof claim | **YES** | descriptive language only |
| no universal winner declared | **YES** | paired development observation, this pool only |
| no case excluded/altered after results | **YES** | all 27 paired cases accounted for |
| no threshold optimized after results | **YES** | `select_operating_threshold` prohibited; τ grid frozen |
| no methodology changed after results | **YES** | frozen engine + frozen protocol reused unchanged |

## Interpretation-rule compliance

- The Agent-Arena-outperforms branch of `interpretation_rules.md` is applied: the paired
  development observation is reported **for this pool only**, with **no generalization** and
  **no attribution to the system prompt alone**.
- No forbidden phrasing ("proven superior", "universally outperforms", "statistically
  defeated", "validates production", "holdout confirms", "increases n to 54", "differ only in
  the system prompt", "isolates the effect of the system prompt") appears in any artifact.
- The banner **DEVELOPMENT PILOT — NOT HOLDOUT** and all required caveats appear on every
  report.

## Boundaries

No holdout access; no completed Sonnet/Opus result accessed; no private mapping/salt/path in
any tracked artifact; neither raw envelope copied into Git; neither completed envelope
modified; **Phase 6 closeout not begun**; **nothing committed** — stops for curator review.
