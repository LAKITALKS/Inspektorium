# Phase 7A — Metrics, Acceptance Matrix, Run-Failure & Reproducibility (pre-registration)

All metrics, thresholds, and decision rules are frozen **before** any result, per Level-2
discipline. Metric families are kept **separate** — there is **no single "robustness score"** and
no weighted universal number.

**Root principle (frozen, curator design-freeze patch):** an *isolated* analytical error is a
**finding**, not a phase failure. A **reproducible, systematic analytical robustness failure CAN
BLOCK Phase-7A closeout.** Phase 7A must be *capable of failing for lack of robustness* — otherwise
the phase could fail its scientific tests while remaining formally PASS. Robustness testing must be
able to fail. This does **not** alter the final, unconditional Phase-6 GO.

---

## 1. Metric families (separated; primary vs secondary vs diagnostic)

### 1.1 Label performance
| metric | tier | notes |
|---|---|---|
| primary-label accuracy (overall) | **primary** | on frozen bases; stratified by difficulty tier |
| per-label accuracy | secondary | reported only where **n ≥ 5** (reuses `calibration.py` rule); `correlation`/`mechanism` may be descriptive-only at small n |
| confusion matrix (4×4) | primary (diagnostic) | full matrix, all four labels visible |
| error counts | primary | raw counts, not rates alone, given small n |

### 1.2 Calibration (reuse `calibration.py`, frozen engine)
| metric | tier | notes |
|---|---|---|
| **Brier** (top-label correctness) | **primary** | VALID-confidence records only |
| confidence distributions | secondary | VALID/MISSING/INVALID, never coerced to 0.0 |
| ECE (5 fixed bins) | **secondary / diagnostic only** | high-variance at small n / sparse bins; interpreted only if bin occupancy supports it; never used to assert calibration quality on its own (Phase-6 lesson: Sonnet had lowest ECE while being the only model with errors) |

### 1.3 Robustness
| metric | tier | notes |
|---|---|---|
| perturbation invariance rate (per family + overall) | **primary (7A.2)** | fraction of variants whose modal label = base modal behavior; cluster-aware |
| perturbation correctness-vs-gold | **primary (7A.2)** | reported **separately** from invariance — **INVARIANCE ≠ CORRECTNESS** |
| perturbation label-switch rate | primary (7A.2) | |
| adversarial failure rate (per family) | **primary (7A.3)** | per A1–A8; "majority failure" = wrong modal label in ≥3/5 valid replications |
| boundary confusion pattern | **primary (7A.1)** | 4×4 transition matrix, both directions (overclaim→over-specific **and** reverse) |

### 1.4 Stability (replication, reuse `run_library` + thin extension)
| metric | tier | notes |
|---|---|---|
| modal label; unanimous vs non-unanimous | **primary (7A.4)** | |
| label-switch count across N=5 | primary | |
| confidence mean + spread | secondary | spread ≠ calibrated probability |
| per-replication Brier | secondary | where VALID |
| per-case instability flag | primary | `unstable_label` etc. |

### 1.5 Difficulty
Stratified reporting by pre-result tier **D1/D2/D3**. Difficulty is descriptive context for every
other family, never a metric of model quality by itself.

**Frozen separations (§20):** label performance · calibration (Brier primary, ECE secondary) ·
robustness (invariance kept separate from correctness) · stability (kept separate from confidence) ·
difficulty strata (kept separate from observed accuracy). Replication frequency ≠ calibrated
probability (§21). No family is merged into one number; no universal robustness score.

**Model-condition-specific reporting (frozen, §9 of patch):** every metric family is reported
**separately for each primary condition** — Haiku and Sonnet — at minimum: accuracy · confusion
matrix · boundary patterns · adversarial-family outcomes · perturbation invariance · stability ·
Brier. **The two models are never collapsed into one pooled headline metric.** Cross-model summaries
are **supplementary**, never a substitute for the per-condition results.

---

## 2. Pre-result acceptance matrix — three dispositions

Three pre-result dispositions, applied per objective:

- **PASS**
- **INVESTIGATE / LIMITATION** — a finding that may remain a *documented limitation* if it does not
  meet a pre-frozen BLOCK rule.
- **BLOCK / FAIL** — blocks Phase-7A closeout.

The governing distinction is **isolated error vs repeatable pattern vs systematic failure**. Not
every incorrect case blocks the phase; a *systematic, reproducible* robustness failure does. All
counts below are frozen *before* results and are **not** moved afterward. A "majority failure" /
"majority flip" for a case means the **wrong modal label in ≥ 3 of 5 valid replications** (execution
failures excluded from the denominator, never scored as a wrong label).

**Both model conditions are PRIMARY (frozen):** `claude-haiku-4-5-20251001` **and**
`claude-sonnet-4-5-20250929`. **Every systematic-failure BLOCK rule below applies INDEPENDENTLY to
each primary condition** — a systematic failure meeting a frozen criterion in *either* condition
blocks Phase-7A closeout pending curator review. **Cross-model recurrence (the same failure in both
conditions) is STRONGER CORROBORATION, not a prerequisite for BLOCK.** Haiku was the *Phase-6
ceiling condition* — a useful **historical / descriptive** fact — but Phase-6 ceiling status confers
**no exclusive Phase-7A block authority**; Sonnet is not merely diagnostic. Result reporting stays
model-condition-specific (§ metric families / §9 of the patch); models are never collapsed into one
pooled headline.

### 2.1 — 7A.1 Boundary (per priority boundary: `overclaim↔correlation_vs_causation`, `overclaim↔mechanism_vs_evidence`)
| disposition | condition |
|---|---|
| **PASS** | no pre-frozen systematic boundary-confusion rule is met |
| **INVESTIGATE / LIMITATION** | an isolated wrong **majority** outcome on **one** independent case within a priority boundary |
| **BLOCK / FAIL** | applied **independently to each primary condition** (Haiku, Sonnet): after ruling out {malformed case · invalid gold · evidence corruption · taxonomy-document contradiction}, the **same directional confusion** (e.g. gold `overclaim` → modal `correlation_vs_causation`) occurs on **≥ 2 independent cases within the same priority boundary** in **that condition**, with the wrong label modal in **≥ 3/5 replications for each affected case**. A qualifying pattern in **Haiku alone** blocks; a qualifying pattern in **Sonnet alone** blocks (even if the other condition passes those cases). The same pattern across **both** conditions is **stronger corroboration, not a prerequisite**. |

Classify a met criterion first as a **ROBUSTNESS FAILURE**, *not* a taxonomy defect — a taxonomy
contradiction requires separate evidence (§2.7).

### 2.2 — 7A.3 Adversarial (per family, 2 independent cases each)
| disposition | condition |
|---|---|
| **PASS** (for that family) | **0/2** majority failures |
| **INVESTIGATE / LIMITATION** | **1/2** majority failures |
| **BLOCK / FAIL** | applied **independently to each primary condition**: **2/2** majority failures in **either** Haiku **or** Sonnet → systematic adversarial-family failure → BLOCK (even if the other condition passes). The same 2/2 across **both** conditions is stronger corroboration, **not** a prerequisite. |

Cases are **never** relabeled to make a family pass (governance breach, §2.8).

### 2.3 — 7A.2 Perturbation (meaning-preserving; cluster-aware)
A **variant-induced flip** = an equivalence-certified variant changes the **modal label relative to
the frozen base behavior**. Correctness-vs-gold is always reported **separately**; a
**stable-but-wrong** case does **not** count as successful analytical performance merely because it
is invariant (**INVARIANCE ≠ CORRECTNESS**).
| disposition | condition |
|---|---|
| **PASS** | no pre-frozen systematic perturbation rule is met |
| **INVESTIGATE / LIMITATION** | a single isolated variant-induced majority flip |
| **BLOCK / FAIL** | applied **independently to each primary condition** (Haiku, Sonnet): **either** (A) the **same** perturbation family causes majority label flips in **≥ 2 independent base clusters**, **or** (B) **one** base cluster experiences majority flips under **≥ 2 distinct** meaning-preserving families — in **that** condition. A qualifying pattern in Haiku alone, or Sonnet alone, blocks; both conditions = stronger corroboration, not a prerequisite. |

### 2.4 — 7A.4 Replication / stability (N = 5; per case/condition)
Modal-consistency tiers: **5/5 unanimous · 4/5 stable-majority · 3/5 fragile · no majority or modal
support ≤ 2 = unstable.** Evaluated **independently for each primary condition** (Haiku, Sonnet).
| disposition | condition |
|---|---|
| **PASS** | no pre-frozen systematic instability rule is met |
| **INVESTIGATE / LIMITATION** | one **3/5 fragile** case |
| **SERIOUS INVESTIGATION** | any **no-majority / ≤ 2 modal-support** case in a frozen analytical condition |
| **BLOCK / FAIL** | in **either** primary condition, after excluding infrastructure/provider failures: **≥ 2 independent cases within the same family are fragile or worse**, **or** one case has **no majority** and the instability **reproduces** in another independent case from the same family. A systematic stability failure in Sonnet is **not** downgraded because Haiku is stable, and vice versa; both conditions = stronger corroboration, not a prerequisite. |

Replication frequency is **never** translated into a calibrated correctness probability (§21).

### 2.5 — 7A.5 Difficulty / ceiling
| disposition | condition |
|---|---|
| **PASS** | the frozen pool demonstrably raises difficulty vs the Phase-6 ceiling (non-trivial D2/D3 representation), achieved **without** any result-driven case change |
| **INVESTIGATE / LIMITATION** | ceiling persists on the chosen model(s) → nominate additional harder cases **separately** (outcome-independent); do not retire easy cases |
| **BLOCK / FAIL** | evidence of **result-driven** case removal/relabel/selection (a governance breach, §2.8) |

### 2.6 — Overall Phase-7A disposition (§11)
- **Phase 7A cannot PASS while a valid systematic BLOCK condition remains open in EITHER primary
  model condition** (Haiku or Sonnet). This does **not** mean one ordinary model error fails the
  phase — the isolated-error → INVESTIGATE/LIMITATION vs systematic-pattern → BLOCK distinction holds.
- **PHASE 7A PASS** requires: no unresolved BLOCK condition in either primary condition; no unresolved
  governance/integrity violation; no unresolved Level-3 taxonomy contradiction; **all mandated result
  families reported**; **counterevidence reported**; **limitations reported**.
- **INVESTIGATE / LIMITATION** findings may remain as documented limitations if they do not meet a
  pre-frozen BLOCK rule.
- **PHASE 7A FAIL / BLOCK** if any pre-frozen systematic robustness criterion above is met and
  remains valid after an objective case/infrastructure audit. **Thresholds are not moved after
  results.**

### 2.7 — Level-3 taxonomy-contradiction escalation (§9)
If a repeated failure pattern appears to result from a **genuine contradiction inside the frozen
taxonomy / precedence rules**, it is **not** fixed inside Phase 7A. Disposition: **BLOCK CLOSEOUT
PENDING CURATOR LEVEL-3 REVIEW.** Frozen: a systematic error pattern **may reveal** a taxonomy
problem, but a systematic error pattern **does not by itself prove** a taxonomy problem — the
default classification is *robustness failure*, and a taxonomy contradiction requires separate,
explicit evidence.

### 2.8 — Execution / governance — unconditional blockers (§10)
These block Phase-7A closeout regardless of analytical results:
- holdout leakage;
- result-driven gold changes; result-driven exclusions; result-driven retirement;
- changing replication **N after observing variance**; changing **acceptance thresholds after
  results**;
- corrupted experiment manifest; unresolvable run configuration;
- systemic parsing/runtime failure that invalidates the experiment;
- inability to reproduce frozen case/config fingerprints.

---

## 3. Run-failure policy (frozen, §52 / patch §22)

**Separate MODEL ANALYTICAL ERROR from EXECUTION / INFRASTRUCTURE ERROR.** Infrastructure failures
are **never** scored as scientific label errors, and a **transport retry caused by infrastructure
failure is NOT an additional analytical replication.**

| event | class | handling |
|---|---|---|
| API timeout | execution | ≤ 2 transport retries; on exhaustion → `error_type` recorded, excluded from label/Brier for that replication, surfaced in integrity flags |
| provider error | execution | as above |
| malformed structured response | execution | strict-parse failure recorded; excluded from that replication's label/Brier; `parse_fragile` flag |
| parser failure | execution | as above; parser completion reported **separately** from accuracy |
| refusal | execution | `error_type=refusal`; excluded from label/Brier; not a wrong label |
| empty output | execution | recorded; excluded; not a wrong label |
| retry **success** | normal | counts as an ordinary record (not an extra replication) |
| retry **exhaustion** | execution | replication marked failed; base's stability read uses the successful replications; if too few succeed, the base is flagged `execution_incomplete`, not mislabeled |

Most of this is already implemented in `run_library` (error / error_type separation,
`parse_failures`, `provider_error_seen`, `truncation_risk`, `parse_fragile` flags). A model that
*answers with the wrong label* is an analytical error and **is** scored.

---

## 4. Expected execution volume (frozen, §22)

```
84 evaluated units  ×  5 planned replications  ×  2 model conditions  =  840 planned model calls
```

- **840 is a planned model-call count, NOT an independent sample size.** The independent scientific
  unit count is **34 bases** (§5, pseudoreplication).
- **Planned analytical replications** (N = 5 per unit per condition) are distinct from **transport
  retries** (≤ 2 per call, infrastructure-only). A retry does **not** add an analytical replication.
- If, **before any model run**, the execution budget proves insufficient for the full 840 planned
  calls at N = 5, the correct action is **STOP for curator rescoping** — do **not** partially run
  and then change N (that would be "changing N after variance", a §2.8 blocker).

---

## 5. Reproducibility (frozen, §53)

Every Phase-7A result preserves, without exposing any private response publicly:
- **case fingerprints** — per-case content sha256 (`case_fingerprint`);
- **configuration fingerprints** — `system_prompt_sha256`, `task_packet_construction_sha256`,
  `parser_contract_sha256`, `agent_config_sha256`, `repository_commit` (`runtime_contract.py`);
- **model IDs** — the exact frozen snapshots `claude-haiku-4-5-20251001` and
  `claude-sonnet-4-5-20250929`;
- **prompt / package version**; **run IDs** (`library_run_id` + `run_index`); **replication IDs**
  (`run_index` 0..4); **timestamps** per record;
- **raw response integrity** — retained in the private/anonymized journal envelope
  (`DEV-####`-style opaque ids), **never** published; **parsed output**; **deterministic metrics**.

Public artifacts follow the Phase-6 leakage posture: no private identity / mapping / salt /
envelope / raw response / holdout content in any tracked file.
