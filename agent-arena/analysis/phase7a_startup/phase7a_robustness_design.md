# Phase 7A — Robustness Design (subtracks, model condition, replication freeze)

Pre-result design for the **analytical-judgment robustness** track. Phase 7A asks whether the
analytical system reaches **stable and taxonomically defensible judgments under difficult,
perturbed, adversarial, and repeated conditions** — *not* whether the client report preserves
provenance (that is Phase 7B, already accepted). This document freezes the experimental
architecture; case authoring, gold freeze, and per-track contracts are in
`phase7a_case_and_perturbation_contract.md`; metrics/acceptance in
`phase7a_metrics_and_acceptance.md`.

**Design principles (frozen):** design before results · thresholds before results · freeze gold
before model output · difficulty before performance · replication count before variance · selection
before performance · exclusions before errors · perturbation equivalence before evaluation · test
the hypothesis *and* search for counterevidence · model stability ≠ calibrated probability · variants
≠ independent cases · 7A robustness ≠ 7B artifact QA · **no holdout access**.

**Root acceptance principle (frozen, curator patch):** an *isolated* analytical error is a
**finding** (INVESTIGATE / LIMITATION), **not** an automatic phase failure — but a **reproducible,
systematic analytical robustness failure CAN BLOCK Phase-7A closeout.** Robustness testing must be
capable of failing for lack of robustness. The pre-frozen BLOCK decision rules per subtrack live in
`phase7a_metrics_and_acceptance.md` §2 and are referenced from each subtrack below. This does not
alter the final, unconditional Phase-6 GO.

---

## 1. Smallest clean experimental architecture

Phase 7A is **one experiment with five reporting subtracks over one frozen pool**, not five
separate commits. Recommended run architecture:

```
ONE frozen robustness pool (class B)
  ├── independent BASE cases      → carry boundary-family / adversarial-family tags + difficulty tier
  │      ├── BOUNDARY family      (7A.1)
  │      └── ADVERSARIAL family   (7A.3)
  └── PERTURBATION variants       (7A.2) — clustered under a designated subset of frozen bases
ONE replication config (N frozen) over ONE frozen Agent-Arena package + model condition   (7A.4)
Difficulty tiers assigned to every case BEFORE any run                                     (7A.5)
→ deterministic metrics + stability + cluster-aware + transition-matrix diagnostics
```

This reuses `run_library.py` (batch + replication + stability) and `calibration.py` (Brier/ECE)
directly, adds only thin reporting layers, and keeps a single frozen manifest — matching the
Phase-7 "governance efficiency" goal (one machine report, one human report, one audit manifest,
one deterministic generator).

---

## 2. 7A.1 — Boundary robustness (design)

**Objective:** test difficult, *defensible* boundaries among the four frozen labels, where more
than one failure mode initially appears plausible, precedence matters, evidence tier matters,
wording matters, and the correct gold remains defensible. **Not** to maximize error rate.

**Priority boundaries (must be represented):**
- `overclaim` ↔ `correlation_vs_causation`
- `overclaim` ↔ `mechanism_vs_evidence`

**Secondary boundary (only where repo evidence justifies, no forced symmetry):**
- `solid` ↔ `overclaim` (e.g. honest-caveat cases such as case007-type material where decorative
  optimism hides under honest hedging).

**Bidirectional by design (to avoid a confirmation-only pool):** each priority boundary carries
cases in *both* directions — some gold `overclaim` whose surface *looks* correlational/mechanistic
(the overclaim → over-specific attractor), **and** some gold `correlation_vs_causation` /
`mechanism_vs_evidence` whose surface *looks* like generic rhetorical inflation (the reverse). The
reverse direction is the counterevidence arm for the §7 hypothesis.

**Primary-label prioritization test:** for every boundary case the frozen record pins the single
most-specific-yet-correct primary per the precedence rule, plus the documented
`gold_alternative_reading`. A model choosing the alternative is scored as a boundary confusion, and
the precedence rationale explains why the primary is defensible.

**Explicitly excluded:** artificially ambiguous gold, trick questions, or cases whose primary is
not defensible under the frozen precedence (see §4 anti-trick and the case contract).

**Boundary BLOCK rule (pre-frozen, metrics §2.1) — applied independently to each primary condition
(Haiku, Sonnet):** after ruling out {malformed case · invalid gold · evidence corruption ·
taxonomy-document contradiction}, the **same directional confusion** on **≥ 2 independent cases
within the same priority boundary** in **that condition** (wrong label modal in ≥ 3/5 replications
each) is a **systematic robustness failure → BLOCK**. A qualifying pattern in **Haiku alone** blocks;
in **Sonnet alone** blocks. Cross-model recurrence is **stronger corroboration, not a prerequisite**.
Classify as robustness failure first, not a taxonomy defect. Directional counts are frozen in the
case contract §3.

---

## 3. 7A.2 — Perturbation robustness (design)

**Objective:** measure label **stability** under transformations that **must not** change the gold
label (invariance tests).

**Permitted families (feasible with the existing harness, which evaluates `task.prompt` text):**

| id | family | invariance? | rationale |
|---|---|---|---|
| P1 | **Claim paraphrase** | yes | same scientific proposition, different wording |
| P2 | **Hedging variation (neutral)** | yes | stronger/weaker *superficial* hedge that does not change the substantive proposition |
| P3 | **Order (claim/evidence context)** | yes | reorder sentences / evidence items where semantic content is preserved (merges "sentence order" + "evidence order") |
| P4 | **Distractor context** | yes | add irrelevant-but-plausible material that does not bear on the claim |
| P5 | **Formatting** | yes | bullets ↔ prose, section ordering, metadata placement |

**Deferred (not in the first freeze):** *citation-surface variation* — feasible only for cases that
carry an explicit citation surface; revisit once the boundary/adversarial cases are frozen and it
is known which carry citations. Deferring it is documented, not silent.

**Invariance boundary (frozen, §16):** a perturbation is an invariance test **only if the gold
judgment should remain the same.** If a change alters causality, population, comparator, endpoint,
evidence tier, superiority claim, temporal claim, or a mechanism-to-clinical implication, it is
**not** a perturbation — it is a **new case** with its own gold freeze. Any candidate that crosses
this line is rejected from the perturbation set.

**Equivalence validation (frozen, §17):** perturbations are **deterministic / human-curated**.
Meaning-preservation is asserted by construction + curator review against a fixed equivalence
checklist (proposition, population, comparator, endpoint, evidence tier, direction/strength all
unchanged). **No LLM-generated-then-assumed-equivalent perturbation enters evaluation.** If LLM
assistance is ever used to *draft* candidates later, a separate deterministic/human freeze must
occur before evaluation. **No perturbations are generated in this startup session.**

**Invariance ≠ correctness (frozen):** perturbation invariance and correctness-vs-gold are reported
**separately**; a **stable-but-wrong** case is **not** counted as successful analytical performance
merely because it is invariant. **Perturbation BLOCK rule (pre-frozen, metrics §2.3) — applied
independently to each primary condition (Haiku, Sonnet):** **either** the **same** perturbation
family causing majority flips in **≥ 2 independent base clusters**, **or** **one** base cluster
flipping under **≥ 2 distinct** meaning-preserving families, in **that condition**, is a **systematic
perturbation failure → BLOCK** (Haiku alone or Sonnet alone suffices; both = stronger corroboration,
not a prerequisite). The 10 base clusters are selected by the deterministic pre-result rule in the
case contract §6.

---

## 4. 7A.3 — Adversarial robustness (design)

**Objective:** does the classifier hold the correct label when the *surface* pushes toward a wrong
one? This is **scientific claim-forensics adversarial testing**, mapped to known Agent-Arena
forensic failure modes — **not** generic AI red-teaming, jailbreaks, or prompt attacks (none are in
scope unless the repo explicitly defines them, which it does not).

**Candidate families (each mapped to the label it attacks / the failure mode it probes):**

| id | adversarial family | attacks toward | gold anchor |
|---|---|---|---|
| A1 | decorative citation (citation present, does not support the claim) | *specific* | usually `overclaim` |
| A2 | citation supports **mechanism** but not **outcome** | `mechanism_vs_evidence` surface | per precedence |
| A3 | association language dressed as causality (causal verb on observational data) | `correlation_vs_causation` | per trigger |
| A4 | subgroup → general-population generalization | `overclaim` | `overclaim` |
| A5 | surrogate endpoint → clinical benefit ("Shape B") | *looks* mechanistic | **`overclaim`** (routed by taxonomy) |
| A6 | unsupported superiority / benchmark cherry-picking / missing comparator | `overclaim` | `overclaim` |
| A7 | biologically plausible mechanism → implied human efficacy | `mechanism_vs_evidence` | per trigger |
| A8 | numerically-correct value attached to wrong population / technically-true-but-misleading, with hedges that do **not** repair the overclaim | `overclaim` | `overclaim` |

**Anti-trick rule (frozen, §19):** every adversarial case must have a frozen rationale, an evidence
basis, a **defensible** gold, and a precedence explanation. Difficulty comes from *surface
pressure*, never from epistemic sloppiness or a genuinely ambiguous gold. A5 in particular is a
*positive* control that the taxonomy's Shape-B routing (surrogate → `overclaim`) holds under
adversarial mechanistic dressing.

**Adversarial BLOCK rule (pre-frozen, metrics §2.2) — applied independently to each primary
condition (Haiku, Sonnet):** per family (2 cases) — **0/2** majority failures = PASS; **1/2** =
INVESTIGATE; **2/2** majority failures in **either** condition = **systematic adversarial-family
failure → BLOCK** (a "majority failure" = wrong modal label in ≥ 3/5 valid replications). Haiku alone
or Sonnet alone suffices; both = stronger corroboration, not a prerequisite. Each family's forensic
trigger and expected gold logic is pre-declared in the case contract §4; cases are never relabeled to
make a family pass.

---

## 5. 7A.4 — Replication / stability (design + FROZEN count)

**Frozen replication count: `N = 5`.**

**Justification (chosen before any variance is seen):**
- Runtime is **temperature 0.0** with `top_p` omitted and seed UNSUPPORTED (frozen Phase-6.2
  runtime), so residual provider nondeterminism is low; the value of replication is to *catch rare
  flips*, which is exactly the stability question. 5 keeps this affordable.
- **Odd** count → a well-defined majority; for a 4-way label there is no forced modal tie in the
  common near-deterministic case.
- 5 gives interpretable stability tiers: **unanimous (5/5) · stable-majority (4/5) · fragile (3/5)
  · unstable (plurality ≤ 2 or ≥ 2 distinct majority-less labels)** — richer than N=3, where a
  single flip drops to 2/3 (67 %) and overstates instability.
- 5 is the top of the pre-registered 3–5 range and maximizes interpretability without runaway cost
  at the proposed pool size.

**Execution configuration (frozen):**
- **Same** Agent-Arena package (prompt + response contract + parser) across all replications.
- Run on **both** frozen **primary** conditions — `claude-haiku-4-5-20251001` and
  `claude-sonnet-4-5-20250929` — under the frozen runtime contract (temp 0.0, top_p omitted,
  timeout 120 s); stability is evaluated **independently per condition**.
- **Independent** calls (fresh context per replication; `run_index` 0..4).
- **Retry handling:** ≤ 2 transport retries per call (existing contract). Retry *success* → normal
  record. Retry *exhaustion* / provider error / malformed / refusal / empty → **execution failure**,
  recorded with `error_type`, **excluded from label-accuracy/Brier for that replication**, and
  surfaced in the execution-integrity flags — **never scored as a wrong label** (see run-failure
  policy in metrics doc).
- **Aggregation (deterministic):** modal label; unanimous vs non-unanimous; label-switch count;
  confidence mean + spread; per-replication Brier where confidence is VALID; per-case instability
  flag. Reuses `CaseStability` (already computes modal fraction + variance/error flags) plus the
  thin additive fields listed in reconstruction §E.

**Frozen epistemic separation (§21):** run frequency ≠ model confidence ≠ calibrated probability.
`4/5` identical labels does **not** mean "80 % probability the label is correct." Replication
measures **behavioral stability under the frozen execution condition** only, and is reported
separately from calibration.

**Stability BLOCK criteria are pre-frozen** in `phase7a_metrics_and_acceptance.md` §2.4 (tiers 5/5
unanimous · 4/5 stable-majority · 3/5 fragile · ≤ 2 support = unstable; BLOCK when ≥ 2 independent
same-family cases are fragile-or-worse, or a no-majority case reproduces in another same-family
case, after excluding infrastructure failures).

---

## 6. 7A.5 — Difficulty / ceiling management (design)

**Objective:** raise diagnostic difficulty relative to the Phase-6 ceiling (Haiku/Opus 27/27)
**without** result-driven case changes.

**Frozen prohibitions:** do **not** remove cases because a model gets them right; do **not** retire
easy cases because they lower the error rate; do **not** select only failures.

**Difficulty tags — defined BEFORE results, on case *properties* only (§49):**

| tier | definition (case-intrinsic) |
|---|---|
| **D1** | single clear failure mode; one plausible label; low evidence-tier conflict |
| **D2** | one primary + one genuinely plausible alternate reading; precedence decides the primary |
| **D3** | ≥ 2 plausible failure modes, **or** evidence-tier conflict present, **or** large claim↔evidence distance |

Tag inputs (all pre-result, no model performance): `boundary_complexity`,
`n_plausible_failure_modes`, `evidence_tier_conflict` (bool), `claim_evidence_distance`. Reporting
is **stratified** by tier. **`hard` is never defined as "the model got it wrong."**

---

## 7. Robustness-failure-type vocabulary (reporting only — NOT the gold taxonomy)

The four gold labels are for *claims*. Robustness analysis needs a **separate** category set for
*failures*, which must never pollute the frozen taxonomy:

| robustness-failure type | meaning |
|---|---|
| `label_instability` | label changes across replications of the *same* input |
| `boundary_confusion` | wrong primary on a frozen boundary case (which alternate was chosen) |
| `perturbation_sensitivity` | label changes across an invariance-preserving perturbation |
| `adversarial_miss` | surface pressure flips the label away from the defensible gold |
| `confidence_instability` | large confidence spread across replications (VALID confidences) |
| `execution_failure` | timeout / provider error / malformed / refusal / parser failure (infra, **not** an analytical error) |

These are analysis-layer descriptors emitted by the reporting extension. They are kept in a
distinct namespace from `solid / overclaim / correlation_vs_causation / mechanism_vs_evidence`.

---

## 8. Model condition (FROZEN — curator decision)

**Frozen: Agent-Arena package only, with TWO PRIMARY Anthropic model conditions** (same package:
prompt + response contract + parser held identical across both). **Both conditions are primary** —
each systematic-failure BLOCK rule (metrics §2) applies **independently** to each; a systematic
failure in *either* blocks Phase-7A closeout. Model identifiers are read from the committed Phase-6.2
runtime contracts (`analysis/phase6_2_runtime_freeze/phase6_2_runtime_contract_{haiku,sonnet}.json`),
**not** guessed:

| primary condition | exact model id | agent config | descriptive role |
|---|---|---|---|
| **Haiku (primary)** | **`claude-haiku-4-5-20251001`** | `agents/claude_haiku.yaml` | *historically* the Phase-6 ceiling condition + low-cost package reference (also the Phase-6.4 Agent-Arena package Haiku condition) — ceiling status is descriptive, **not** exclusive block authority |
| **Sonnet (primary)** | **`claude-sonnet-4-5-20250929`** | `agents/claude_sonnet.yaml` | Phase-6.2 condition that produced the overclaim → over-specific error pattern; **primary**, not merely diagnostic |

- **This is NOT a cross-provider benchmark.** Both conditions run the same Agent-Arena package on
  two Anthropic snapshots; robustness is package-intrinsic.
- **Opus is excluded from the primary Phase-7A run.** `claude-opus-4-5-20251101` may serve as a
  *later optional* replication condition **only under separate curator authorization**.
- **No prompt-only baseline replication** is required (curator-approved).
- Frozen runtime for both conditions (from the Phase-6.2 contracts): `temperature = 0.0`,
  `top_p = OMITTED_FROM_REQUEST`, `seed = UNSUPPORTED`, `request_timeout = 120 s`, ≤ 2 transport
  retries, semantic/quality retries PROHIBITED.
- **No model is run in this session.**

Expected primary execution volume: **84 evaluated units × 5 replications × 2 conditions = 840
planned model calls** (a call count, **not** an independent sample size; see
`phase7a_metrics_and_acceptance.md` §4). BLOCK rules (metrics §2) apply **independently to each
primary condition**; "Phase-6 ceiling condition" is used only as a historical descriptor of Haiku,
never as exclusive block authority. Results are reported **separately per condition** (metrics §1),
never pooled into one headline.
