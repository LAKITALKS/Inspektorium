# Phase-5B Sonnet 4.5 Full Replication (S1) — Final Report

Post-repair Sonnet full replication under the exact repaired contract used by H1
Haiku. Fourth cell of the controlled H0/H1/S0/S1 design.

## 1. Execution verdict

**POST-REPAIR SONNET 4.5 FULL REPLICATION COMPLETE.** All 420 analytical slots
(84 units × N=5) executed terminally under `claude-sonnet-4-5-20250929` with the
repaired v2 prompt; raw data frozen; deterministic S1 analysis, S0→S1 paired
comparison, H1↔S1 controlled comparison and the four-cell table produced;
authorization consumed (budget 0); delivered-state full suite green. No push.

## 2. Starting / baseline state

- Repository: `__LOCAL_HOME__/Documents/Projects/agent-arena`
- Branch: `repair/pre-phase8-integrity`
- Registered baseline HEAD (S1 execution path): `c8f2ddf9171fc6b45b312acb0937b9a6df5f3017`
- Tracked source/tests unchanged from that baseline throughout execution.

## 3. S0 historical reconstruction (frozen, verified)

- Model `claude-sonnet-4-5-20250929`, historical v1 prompt.
- Aggregate result-set fingerprint `e1741121c55e522130a0522bb42ed14f7a6a5c0733b333456c1185c067f32fe8`.
- Unit-modal 65/84 = 0.7738; Brier 0.20126; ECE-5bin 0.16831; mean confidence 0.9445.
- Per-gold: solid 13/13, overclaim 35/44, CvC 9/10, ME 8/17.

## 4. H1 frozen verification (immutable comparison cell)

- Aggregate fingerprint `79ddfa509d302dfcaf5464060e3df4f8a25f7e76ecdf7a68a9a409281aca01ec`; spec `d5de4599…`.
- Unit-modal 78/84 = 0.9286; Brier 0.06816; ECE-5bin 0.00695; mean confidence 0.9355.
- Per-gold: solid 13/13, overclaim 39/44, CvC 9/10, ME 17/17.

## 5. Scientific-universe equivalence & the single intended difference

S1 and H1 resolve byte-identical scientific inputs — the same 84 ordered units,
gold, v2 prompt bytes (`system_prompt_sha256 37d91b81…`), packaging, N=5, the
420-slot schedule, and the frozen shared runtime (temperature 0.0, top_p
omitted, seed unsupported, max_tokens 4096, timeout 120s, ≤2 transport retries,
semantic retries prohibited). The **only** generatively relevant H1↔S1
difference is the foundation-model snapshot (haiku vs sonnet). S1 binds the
frozen S0 historical reference (never H0). Verified by
`tests/test_h1_s1_controlled_comparison.py`.

## 6–8. Preregistration, authorization, cost

- Plan `AA-P5B-SONNET-FULL-REPLICATION-001`, spec fingerprint
  `feb0d4c7d39ee126ec8c8adf5a315314ce3ddd1d43b28d85d074209ef5d14b53`.
- Pre-execution cost gate (non-generative `messages.count_tokens`, model_generations=0):
  599,105 scheduled input tokens, first-attempt estimate **$8.155785** ≤ operational budget $18.
- Authorization activated AUTH_REAL (sonnet only, exactly 420 slots, Haiku=0, other=0), then consumed.
- Authorized-state canonical QA: **369 collected / 369 passed / 0 failed / 0 errors**.

## 9. Execution accounting

| | |
|---|---|
| Planned slots | 420 |
| New slots executed | 420 |
| Authenticated reused slots | 0 |
| First attempts | 420 |
| Transport retries | 0 |
| Total HTTP attempts | 420 |
| Terminal attempts | 420 |
| Classification-valid | 420 |
| Calibration-valid | 420 |
| Provider failures | 0 |
| Parser failures | 0 |
| Semantic retries | 0 (prohibited) |
| Provider constructions | sonnet=1, haiku=0 |

## 10. S1 raw freeze

- `run/sonnet/sonnet_raw_result_freeze.json` — aggregate result-set fingerprint
  `0c61370bc3cadf36e58f5b9b6f63a856b45a575fbdc38bf1abd179b4dac56e70`; complete, 0 missing keys.
- Raw records `run/sonnet/raw/sonnet_raw_records.jsonl` (420); checkpoint manifest;
  one-shot lease; preflight & execution evidence; usage/cost.

## 11. S1 results

- Unit-modal accuracy **70/84 = 0.8333**; replication-level 350/420 = 0.8333.
- Base 25/34; variant 40/50; boundary 12/14; adversarial 15/16; perturbation 40/50; neutral 3/4.
- Brier **0.14902**; ECE-5bin **0.10243**; ECE-10bin **0.10243**; mean confidence **0.9358**.
- Per-gold: solid 13/13, overclaim 30/44, CvC 10/10, **ME 17/17**.
- Replication stability: 84/84 unanimous (5/5); 0 fragile.

## 12–13. S0 → S1

Deltas (S1 − S0): unit-modal **+0.0595**, response +0.0548, Brier **−0.0522**,
ECE-5bin **−0.0659**, ECE-10bin −0.0725, targeted-19 +0.263, remaining-65 0.0,
unanimous +2. Transition categories over 84 units: CORRECT→CORRECT 59,
**WRONG→CORRECT 11**, WRONG→SAME-WRONG 8, **CORRECT→WRONG 6** (net +5 → 65→70).
17 modal-changed units. Full matrix + per-unit rows in
`run/sonnet/sonnet_historical_comparison.json`.

> S0→S1 is a whole-system historical-versus-repaired comparison and does not
> identify the causal contribution of one repair.

## 14–15. H1 ↔ S1 controlled comparison

| Metric | H1 Haiku | S1 Sonnet | Δ (S1−H1) |
|---|---|---|---|
| Unit-modal | 78/84=0.9286 | 70/84=0.8333 | −0.0952 |
| Replication acc | 0.9286 | 0.8333 | −0.0952 |
| Brier | 0.06816 | 0.14902 | +0.0809 |
| ECE-5bin | 0.00695 | 0.10243 | +0.0955 |
| ECE-10bin | 0.01624 | 0.10243 | +0.0862 |
| Mean confidence | 0.9355 | 0.9358 | +0.0002 |
| Solid | 13/13 | 13/13 | 0 |
| Overclaim | 39/44 | 30/44 | −9 |
| CvC | 9/10 | 10/10 | +1 |
| ME | 17/17 | 17/17 | 0 |
| Boundary | 13/14 | 12/14 | −1 |
| Adversarial | 16/16 | 15/16 | −1 |
| Perturbation | 46/50 | 40/50 | −6 |

**Every H1↔S1 modal disagreement (10 units):**

| Unit | Type | Gold | H1 modal | S1 modal | H1 | S1 | Δconf(S1−H1) |
|---|---|---|---|---|---|---|---|
| P7A-BND-004 | boundary | correlation_vs_causation | overclaim | correlation_vs_causation | ✗ | ✓ | +0.000 |
| P7A-ADV-010 | adversarial | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | +0.000 |
| P7A-BND-016 | boundary | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | +0.016 |
| P7A-BND-018 | boundary | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | −0.060 |
| P7A-PRT-02-P5 | perturbation | overclaim | overclaim | correlation_vs_causation | ✓ | ✗ | +0.000 |
| P7A-PRT-08-P1 | perturbation | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | −0.012 |
| P7A-PRT-08-P2 | perturbation | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | −0.140 |
| P7A-PRT-08-P3 | perturbation | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | −0.036 |
| P7A-PRT-08-P4 | perturbation | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | +0.000 |
| P7A-PRT-08-P5 | perturbation | overclaim | overclaim | mechanism_vs_evidence | ✓ | ✗ | −0.006 |

Nine of ten disagreements are overclaim-gold units H1 keeps correct but S1
over-splits into ME/CvC; one (BND-004) is a CvC-gold unit S1 fixes and H1
misses. This disagreement set identifies the model-sensitive propositions under
the fixed repaired harness.

> H1↔S1 is the cleaner comparison because both models are evaluated under the
> same repaired harness; observed differences therefore measure model
> sensitivity under that contract, subject to normal provider/time confounds.

## 16–17. Four-cell H0/H1/S0/S1 and repair direction

| Metric | H0 | H1 | S0 | S1 | ΔHaiku (H1−H0) | ΔSonnet (S1−S0) |
|---|---|---|---|---|---|---|
| Unit-modal | 0.7262 | 0.9286 | 0.7738 | 0.8333 | +0.2024 | +0.0595 |
| Brier | 0.24007 | 0.06816 | 0.20126 | 0.14902 | −0.1719 | −0.0522 |
| ECE-5bin | 0.21374 | 0.00695 | 0.16831 | 0.10243 | −0.2068 | −0.0659 |
| ECE-10bin | 0.21717 | 0.01624 | 0.17488 | 0.10243 | −0.2009 | −0.0725 |
| Mean conf | 0.9399 | 0.9355 | 0.9445 | 0.9358 | −0.004 | −0.009 |
| ME | 0/17 | 17/17 | 8/17 | 17/17 | +17 | +9 |
| CvC | 4/10 | 9/10 | 9/10 | 10/10 | +5 | +1 |
| Overclaim | 44/44 | 39/44 | 35/44 | 30/44 | −5 | −5 |
| Solid | 13/13 | 13/13 | 13/13 | 13/13 | 0 | 0 |
| Boundary | 10/14 | 13/14 | 10/14 | 12/14 | +3 | +2 |
| Adversarial | 11/16 | 16/16 | 11/16 | 15/16 | +5 | +4 |
| Perturbation | 37/50 | 46/50 | 40/50 | 40/50 | +9 | 0 |

**Cross-model directional consistency under the repaired contract** for accuracy,
Brier, ECE, ME, CvC, boundary and adversarial (both models improve in the same
direction). **Model × contract interactions**: overclaim degrades in both (−5)
but from different baselines; perturbation improves for Haiku (+9) but is flat
for Sonnet (0). This is not causal proof of any single prompt rule.

## 18. ME ↔ overclaim topology

The repaired contract resolves the historical ME weakness for **both** models:
S0 8/17 → **S1 17/17**; H0 0/17 → H1 17/17. For Sonnet the ME↔OV confusion
reverses direction: S0 under-split (ME→overclaim), S1 over-splits
(overclaim→ME, 9 of the 14 overclaim misses land on ME). Overclaim is S1's
weakest gold (30/44).

## 19. CvC over-generalization test (prespecified: NEU-002 + PRT-02 P1–P4)

All five units are overclaim-gold; H0 and S0 classify them correctly (overclaim);
**both H1 and S1 shift them to correlation_vs_causation.** The regression cluster
introduced by the repaired contract in H1 reproduces identically in S1 —
cross-model directional consistency for this specific over-generalization
(analysis only; no labels/prompt changed).

## 20. Calibration comparison

S1 raises accuracy (0.774→0.833) toward its already-high confidence without the
confidence collapsing (mean 0.9445→0.9358) and improves calibration
(ECE-5bin 0.168→0.102; ECE-10bin 0.175→0.102) — the same qualitative pattern as
H1 (H0→H1 accuracy 0.726→0.929, confidence ~flat, ECE 0.214→0.007). Stated in
calibration terms; not a claim that historical confidence was intrinsically
correct.

## 21. Error ecology

- **Fixed by S1 vs S0:** ME fully resolved (8/17→17/17); 11 units WRONG→CORRECT; CvC 9/10→10/10.
- **New in S1:** overclaim over-splitting into ME/CvC (overclaim 35/44→30/44); 6 units CORRECT→WRONG.
- **Persistent:** solid perfect throughout; boundary/adversarial improved but not to H1's ceiling.
- **Model-sensitive (H1 vs S1 under the same harness):** the overclaim→ME/CvC
  over-split is markedly larger for Sonnet; perturbation gains are Haiku-only.
- **Cross-model shared regression:** the NEU-002 + PRT-02 P1–P4 overclaim→CvC cluster.

## 22. Interpretation limits

- S0→S1 is a whole-system historical-versus-repaired comparison and does not identify the causal contribution of one repair.
- H1↔S1 is the cleaner comparison because both models are evaluated under the same repaired harness; observed differences therefore measure model sensitivity under that contract, subject to normal provider/time confounds.

## 23–24. Historical and H1 immutability

H0 `b994672…`, S0 `e1741121…`, H1 `79ddfa50…` aggregate fingerprints unchanged;
gold, taxonomy, historical prompts, the H1 repaired prompt and Phase-7 closeout
untouched. Tracked source and tests unchanged from baseline `c8f2ddf` except the
minimal post-run governance-test fix (below).

## 25. Delivered-state full QA

**1905 passed, 0 failed, 0 errors, 0 skipped.** Two Sonnet governance tests were
authored during registration to assert the resting state `== NOT_AUTHORIZED`;
after the legitimate one-shot run the plan rests at `CONSUMED`. Under explicit
human authorization, the minimal post-run fix made those two assertions accept
the fail-closed non-executable set `{NOT_AUTHORIZED, CONSUMED}` (and the matching
resting progress states). No production code, prompt, gold, taxonomy, cases,
runtime, authorization semantics, or scientific analysis were modified.

## 26–28. Authorization final state, tokens, cost

- Authorization: **CONSUMED**, `authorized_budget_calls` 0, `authorized_model_keys` []
  — non-executable. Haiku authorization: none. The fixed consumed-state
  audit-anchor strings do not describe this run (which succeeded); run provenance
  lives in `run/sonnet/` and git history.
- Tokens: input 599,105; output 444,765. **Cost $8.46879** (Sonnet $3/$15).
- Additional Sonnet generations by the post-run fix task: 0; Haiku generations: 0.

## 29. Final git state

- Branch `repair/pre-phase8-integrity`; not pushed; no amend/rebase.
- Commits since baseline `c8f2ddf`: `56aba48` (authorize + cost estimate),
  `620398f` (results + revoke), plus the test-fix + this report.

---

**POST-REPAIR SONNET 4.5 FULL REPLICATION COMPLETE — DELIVERED-STATE QA GREEN —
FOUR-CELL H0/H1/S0/S1 COMPARISON READY FOR HUMAN REVIEW — NO HAIKU RERUN**
