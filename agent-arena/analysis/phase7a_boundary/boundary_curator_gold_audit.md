# Phase 7A — Independent Curator Gold Audit of the 14 Boundary Cases

Independent, pre-model scientific re-adjudication of the frozen Phase-7A Boundary Pool
(`tasks/study_forensics_robustness/P7A-BND-001..014.yaml`, commit `c4fc06b`). The pool passed
structural validation in WP-1; this audit asks the **different** question of whether the 14 gold
labels and their boundary rationales are **scientifically defensible**, reconstructing each case
`public claim → provenance → evidence → taxonomy → precedence → gold` and challenging the frozen
classification.

**No case YAML, manifest, fingerprint, or source file was modified. No evaluation model was run
(0 analytical model calls). Findings are described, not implemented.**

---

## 0. Authorship provenance correction (governance)

The WP-1 report stated substantively that "no LLM decided gold." **That framing is inaccurate and is
corrected here.** The accurate statement:

- The gold labels were **authored by the Claude repo agent (an LLM), pre-model, and frozen before
  any Haiku/Sonnet evaluation run.**
- **No separate evaluation model or external LLM judge** was invoked to determine gold.
- **This curator audit is itself performed by an LLM repo agent in an independent audit role** — it
  is **not** human authorship, human validation, or human inter-annotator agreement. It surfaces
  issues for a **human curator** to decide.

The gold must not be described anywhere as `human-authored`, `human-validated`, `human IAA`, or
`independently human adjudicated` unless/until that actually happens.

---

## 1. Audit method

- **Checkpoint verified:** branch `feat/case-library-run-harness`, HEAD `c4fc06b` (parent
  `1c7c017`), clean tracked tree, 14 files present, fingerprints reproduce (read-only
  `robustness_pool.verify_pool`).
- **Independent source re-verification** (WebSearch, public sources only): load-bearing figures were
  re-checked against original research / systematic reviews / authoritative assessments rather than
  trusting the YAML. Spot re-verified in this session: Riggs 1990 (fracture outcome + BMD basis),
  the real existence of the "processed meat as dangerous as smoking" public claim, and the
  hazard-vs-risk framing; other figures were verified during authoring against the cited sources.
- **Two-axis judgment (kept separate, §21):** `GOLD VALIDITY` (is the frozen label defensible?) and
  `BOUNDARY DIAGNOSTIC QUALITY` (is the specific-label tension for this family genuinely present?).
- **Precedence discipline:** a *possible* specific reading is not enough; a specific label must
  capture the central failure; the frozen 5/5/4 and 8/2/2/2 distributions are design targets and do
  **not** override validity.

---

## 2. Per-case audit matrix

Legend — Gold: PASS/QUESTIONABLE/FAIL · Boundary: STRONG/ADEQUATE/WEAK/FAIL · Disposition:
PASS / PASS+CLERICAL / NEEDS SCIENTIFIC REVISION / REJECT-REPLACE.

### B1 — overclaim ↔ correlation_vs_causation

**P7A-BND-001 — processed meat "as dangerous as smoking"** · gold overclaim
- Claim source: real 2015 media misinterpretation of IARC Group 1 (documented across NPR/PBS/Fox/
  Cancer Council Australia). **Claim provenance verified: YES** (claim-type real; exact span is a
  representative synthesis, no single URL frozen).
- Evidence: IARC/WHO — **regulatory/authoritative assessment** (IARC monograph = systematic review
  of epidemiology+mechanism), *not* a primary study. 18% relative risk / 50 g/day; ~34k vs ~1M
  attributable deaths; "category = strength of evidence, not level of risk" (verified verbatim).
- §11 Q4 (remove causal language → still problematic?): **YES** → central failure is magnitude/
  hazard-vs-risk inflation, not causal inference (IARC judged causation *established*). Gold
  **PASS**. Boundary **ADEQUATE** (correlation is a real attractor but a weak *defensible*
  alternative since causation is established). Steelman ADEQUATE. Numerical PASS. Precedence PASS.
- **Disposition: PASS** (optionally attach one real headline as the claim source — clerical).

**P7A-BND-002 — "must walk 10,000 steps a day"** · gold overclaim
- Claim source: marketing archetype (representative). Claim-type real & documented (manpo-kei 1965
  origin). Evidence: Paluch 2022 — **systematic review / meta-analysis** (47,471 adults; plateau
  ~6–8k / ~8–10k). §11 Q4: claim also carries causal benefit language ("lower your risk of early
  death"), but the decisive checkable defect is the fabricated 10,000 threshold + all-or-nothing
  certainty → overclaim. Gold **PASS**. Boundary **ADEQUATE-STRONG** (genuine correlation attractor
  from observational data). Steelman ADEQUATE. Numerical PASS.
- **Disposition: PASS.**

**P7A-BND-003 — "grip test is the single best predictor of death"** · gold overclaim
- Claim source: media archetype (representative). Evidence: Leong 2015 PURE — **primary research**
  (prospective cohort ~139,691; HR ~1.16 per 5-kg decrease; grip out-predicted systolic BP in-cohort).
  §11 Q4: claim is **purely predictive** (no causal assertion), so removing causal language changes
  nothing → central failure is superiority/individual-prediction overreach → overclaim. Gold
  **PASS**. **Boundary WEAK-ADEQUATE**: because the claim makes no causal inference,
  `correlation_vs_causation` is only a *reflex* attractor, not a genuinely defensible alternative —
  the honest strongest alternative is "just overclaim." Steelman **WEAK** (the frozen alternative,
  correlation, does not fit a predictive claim well).
- **Disposition: PASS** (gold sound) **with BOUNDARY-QUALITY note** — weakest B1 tension.

**P7A-BND-004 — "a daily drink protects your heart"** · gold correlation_vs_causation
- Claim source: lifestyle/media archetype (real, widely published framing). Evidence: Zhao 2023 —
  **systematic review / meta-analysis** (107 cohort studies; >4.8M; no low-volume benefit after
  abstainer-bias correction). §11: claim is causal + prescriptive ("start drinking"); evidence is
  confounded observational with a corrupted reference group; mismatch is central; removing causal
  language would dissolve the claim → the causal boundary crossing *is* the failure. Gold **PASS**.
  Boundary **STRONG**. Steelman (overclaim secondary) ADEQUATE-STRONG. Numerical PASS.
- **Disposition: PASS** (strongest B1 case).

**P7A-BND-005 — "get a dog to live longer"** · gold correlation_vs_causation
- Claim source: news archetype. Evidence: Kramer 2019 — **systematic review / meta-analysis** (10
  observational studies; >3.8M; RR 0.76 all-cause / 0.69 CV) — with the authors' *own* caveat that
  non-randomized data cannot prove causation and confounders were unadjusted (verified). Causal +
  prescriptive claim from confounded design; central. Gold **PASS**. Boundary **STRONG**. Steelman
  ADEQUATE-STRONG.
- **Disposition: PASS.** (Shares a structural template with 004 — lifestyle exposure → mortality,
  observational, causal claim — but distinct exposure/bias/evidence → **independent**, not a
  duplicate.)

### B2 — overclaim ↔ mechanism_vs_evidence  (highest-risk family — see §4 table)

**P7A-BND-006 — "raises bone density 35%, so it prevents fractures"** · gold overclaim (Shape B)
- Claim source: marketing archetype. Evidence: Riggs 1990 — **primary research** (RCT, 202 women,
  4 yr). Re-verified this session: lumbar-spine BMD rose substantially, **new vertebral fractures
  NOT reduced (163 vs 136, NS)**, **nonvertebral fractures 3.2× higher (72 vs 24, P<0.01)**. Classic
  surrogate→clinical dissociation → Shape B → overclaim (taxonomy routes surrogate-to-clinical to
  overclaim; case054 precedent). Gold **PASS**. **Boundary ADEQUATE-STRONG** — a biological
  "denser = stronger" rationale genuinely tempts a mechanism reading, so the overclaim↔mechanism
  tension is real (unlike 007/008). Precedence PASS.
- **Numerical ISSUE (minor):** the case states "increases bone density by 35% **compared with
  controls**." ~35% is the widely-cited **within-group** lumbar-spine increase; the placebo-adjusted
  between-group difference was reported as smaller (~8% in one analysis). The comparison basis should
  be clarified. Does **not** affect gold.
- **Disposition: PASS WITH CLERICAL CORRECTION** (clarify the 35% comparison basis).

**P7A-BND-007 — "probiotics boost your immune system"** · gold overclaim
- Claim source: marketing archetype. Evidence: EFSA — **regulatory/authoritative assessment** (all
  probiotic immune claims rejected; for Nutrimune, no cause-effect and **no plausible mechanism**).
  Gold **PASS** (broad unsubstantiated benefit = overclaim).
- **Boundary WEAK.** The B2 family requires *mechanistic/preclinical evidence used to imply human
  benefit*. Here **no mechanistic/preclinical evidence is presented at all** — the case's own
  alternative reading concedes EFSA "found no plausible mechanism." Therefore `mechanism_vs_evidence`
  is **not a genuinely defensible competing gold**; it is only a lexical attractor ("immune =
  biology"). The genuine competing question is "unsubstantiated claim vs defensible" — an
  overclaim/solid axis, not overclaim/mechanism. Steelman **WEAK** (the frozen mechanism alternative
  is self-defeating). Independence PASS. Numerical N/A.
- **Disposition: NEEDS SCIENTIFIC REVISION** (weak B2 boundary — do **not** retain merely to hold
  the B2 3/2 count). Options: (a) reframe the claim to actually cite an animal/preclinical immune
  pathway used to imply human protection (making mechanism a genuine attractor), or (b) REJECT/
  REPLACE for B2 with such a case. Gold-as-overclaim is not in dispute.

**P7A-BND-008 — "vitamin C prevents colds"** · gold overclaim
- Claim source: marketing archetype. Evidence: Cochrane 2013 — **systematic review / meta-analysis
  of RCTs** (no effect on incidence in general population, 29 comparisons/11,306; duration −8%
  adults/−14% children). Gold **PASS** (prevention claim contradicted by human RCTs = overclaim).
- **Boundary WEAK-ADEQUATE.** The load-bearing evidence is **human RCT**, and *no preclinical/
  mechanistic evidence does rhetorical work*; the honest strongest alternative is **solid** (a scoped
  "may modestly shorten colds" is faithful), i.e. an overclaim↔**solid** tension, not
  overclaim↔mechanism. So `mechanism_vs_evidence` is a **weak** competing gold and the frozen
  steelman is mis-targeted. Steelman **WEAK/mis-targeted**. Numerical PASS.
- **Disposition: NEEDS SCIENTIFIC REVISION** (reconsider B2 membership / re-point the steelman to
  solid; borderline vs PASS+note). Gold-as-overclaim is sound.

**P7A-BND-009 — "clear zombie cells to reverse aging"** · gold mechanism_vs_evidence (positive control)
- Claim source: longevity-marketing archetype. Evidence: Xu 2018 *Nat Med* — **primary research
  (animal)**: senolytics improve physical function and extend lifespan in **aged mice**; human data
  limited to small phase-1/2 pilots in specific diseases (IPF, diabetic kidney disease), not anti-
  aging. Mechanistic/preclinical evidence present ✔; implied human clinical benefit ✔; direct human
  efficacy does not justify it ✔; preclinical→human leap central ✔ (Shape A/C). Gold **PASS**.
  Boundary **STRONG**. Steelman (overclaim secondary) STRONG.
- **Disposition: PASS.**

**P7A-BND-010 — "fasting regenerates your pancreas and reverses diabetes"** · gold mechanism_vs_evidence (positive control)
- Claim source: diet-program archetype. Evidence: Cheng 2017 *Cell* — **primary research (animal +
  in-vitro human cells)**: fasting-mimicking diet drives Ngn3 β-cell regeneration and reverses
  diabetes in **mice**; human evidence is **in-vitro donor cells only** (authors call for a trial).
  Correctly treats **human cells ≠ human clinical outcome** (§16). Shape A/C. Gold **PASS**.
  Boundary **STRONG** (the in-vitro-human distractor makes it a genuine, hard mechanism control).
  Steelman STRONG.
- **Disposition: PASS.**

### B3 — solid ↔ overclaim

**P7A-BND-011 — Shingrix 97.2% (faithful)** · gold solid
- Claim source: authored **faithful public-health summary** (representative; the fidelity is the
  point). Evidence: Lal 2015 ZOE-50 — **primary research** (phase-3 RCT, 15,411; 7,698/7,713; ≥50;
  97.2% over mean ~3.2 yr). Scope bounded (no lifelong/all-population extension). Gold **PASS**.
  Boundary **ADEQUATE** (dramatic-number "distrust" attractor). Steelman (overclaim) ADEQUATE.
  Numerical PASS.
- **Disposition: PASS** (claim is author-constructed by design; see §3 provenance note).

**P7A-BND-012 — SPRINT (benefits + harms, scoped)** · gold solid
- Claim source: authored **faithful clinical briefing** (representative). Evidence: SPRINT 2015 —
  **primary research** (RCT, 9,361 high-risk, non-diabetic, no prior stroke; ~25% fewer major CV
  events, ~27% lower mortality; more hypotension/syncope/electrolyte/AKI; stopped early). Harms +
  scope + generalizability limits reported → honest mixed reporting = solid. Gold **PASS**. Boundary
  **ADEQUATE-STRONG** (dramatic figures + a genuinely contested clinical topic make "is this
  overclaim?" a real tension; the discriminator vs 013 is clean). Numerical PASS.
- **Disposition: PASS.**

**P7A-BND-013 — "everyone over 60 should take daily aspirin"** · gold overclaim
- Claim source: health-column archetype. Evidence: ASPREE 2018 — **primary research** (primary-
  prevention RCT, ~19,114 healthy elderly; CV HR 0.95 [0.83–1.08] NS; major hemorrhage HR 1.38
  [1.18–1.62]) + USPSTF 2022 — **guideline/authoritative recommendation** (against initiation ≥60).
  Central failure = population over-generalization (secondary→primary) + harms omission + certainty,
  with no causal-inference or mechanism structure → overclaim. Gold **PASS**. Boundary **STRONG**
  (genuine partial-truth solid↔overclaim tension). Numerical PASS.
- **Disposition: PASS.**

**P7A-BND-014 — "brain games make you smarter / prevent dementia"** · gold overclaim
- Claim source: brain-training-app archetype; the **FTC 2016 action documents Lumosity's actual
  ad claims** (a real, identifiable claim source that the frozen span paraphrases). Evidence: FTC —
  **regulatory enforcement action** (not primary science) + the cognitive-training **far-transfer
  scientific consensus**. Central failure = far-transfer generalization + unsupported dementia
  prevention → overclaim. Gold **PASS**. Boundary **STRONG**. Numerical N/A ($2M settlement
  verified).
- **Disposition: PASS** (optionally quote the FTC-documented claim verbatim — clerical).

---

## 3. Claim-provenance finding (pool-wide, §7 — highest-priority check)

**Finding:** across the pool the frozen public claims are **curator-authored representative
formulations attributed to archetypal sources** ("a wellness brand", "a supplement label", "a
health column", "a diet program"), grounded in real, documented public-claim *types* and real,
verified evidence — but they are **not verbatim quotations from a single identifiable public-claim
source, and no case freezes a `claim_source_url`.** (This matches the existing Class-A library
convention of synthetic representative scenarios; it does **not** meet a strict verbatim-sourcing
standard.)

- **Claim-*type* genuinely documented (strong):** 001 (2015 headlines), 004/005 (media framings),
  007 (EFSA-rejected claim class), 013 (long-standing advice), 014 (FTC-documented Lumosity ads).
- **Archetypal marketing/advice, no single source:** 002, 006, 009, 010.
- **Authored faithful summaries by design (fidelity probes):** 011, 012.

**No claim is fabricated science** (all evidence is real and verified). The gap is **provenance
rigor**, not invented claims. **Curator decision required:** set the Class-B claim-provenance
standard. Under a strict verbatim standard, attach real quoted claims + URLs where feasible
(001, 007, 014, 004/005) and explicitly label 011/012 as "authored faithful summary (fidelity
probe)." This is a governance decision, not a gold error.

---

## 4. B2 special audit table (§29)

| Case | Gold | Mechanistic/preclinical evidence present? | Human clinical benefit claimed? | Direct human clinical efficacy evidence? | Mechanistic evidence materially used? | `mechanism_vs_evidence` a genuinely plausible alternative? | Final B2 quality |
|---|---|---|---|---|---|---|---|
| 006 | overclaim | No animal pathway; **human RCT surrogate endpoint (BMD)** | Yes (fracture prevention) | Yes (fractures measured — showed no benefit / harm) | Biological rationale invoked ("denser=stronger") | Superficially yes → routed to overclaim by Shape-B rule | **ADEQUATE-STRONG** (designed Shape-B control) |
| 007 | overclaim | **No** (EFSA: no plausible mechanism) | Yes (immune protection) | No | **No** | **No** — no mechanism to over-extrapolate | **WEAK** |
| 008 | overclaim | No preclinical pathway in packet | Yes (cold prevention) | **Yes (Cochrane RCTs, contradict claim)** | No (evidence is human RCT) | **No** — genuine secondary is *solid* | **WEAK-ADEQUATE** |
| 009 | mechanism_vs_evidence | **Yes (aged-mice interventional)** | Yes (reverse aging) | No (only small phase-1/2 disease pilots) | **Yes** | Gold *is* mechanism; overclaim secondary | **STRONG** |
| 010 | mechanism_vs_evidence | **Yes (mice + in-vitro human cells)** | Yes (reverse diabetes) | No (in-vitro only; no patient trial) | **Yes** | Gold *is* mechanism; overclaim secondary | **STRONG** |

**Required yes/no answers (§34 G):**
- Is **P7A-BND-007** genuinely diagnostic for `overclaim ↔ mechanism_vs_evidence`? **NO** (no
  mechanistic/preclinical evidence; mechanism is only a lexical attractor).
- Is **P7A-BND-008** genuinely diagnostic for `overclaim ↔ mechanism_vs_evidence`? **NO** (load-
  bearing evidence is human RCT; the real tension is overclaim ↔ solid).

---

## 5. Source-type correction matrix (§8/§28)

Corrects the WP-1 loose use of "primary sources" (Cochrane, EFSA, USPSTF, FTC, IARC are **not**
primary studies).

| Case | Public-claim source (role) | Load-bearing evidence type | Supporting synthesis/regulatory |
|---|---|---|---|
| 001 | Real media misinterpretation | Regulatory/authoritative assessment (IARC monograph) | — |
| 002 | Marketing archetype | Systematic review / meta-analysis (Paluch 2022) | Historical provenance (manpo-kei) |
| 003 | Media archetype | **Primary research** (PURE cohort) | — |
| 004 | Media/lifestyle archetype | Systematic review / meta-analysis (Zhao 2023) | — |
| 005 | Media archetype | Systematic review / meta-analysis (Kramer 2019) | — |
| 006 | Marketing archetype | **Primary research** (Riggs 1990 RCT) | — |
| 007 | Marketing archetype | Regulatory/authoritative assessment (EFSA) | Commentary (Katan 2012) |
| 008 | Marketing archetype | Systematic review / meta-analysis (Cochrane 2013) | — |
| 009 | Marketing archetype | **Primary research (animal)** (Xu 2018) | — |
| 010 | Marketing archetype | **Primary research (animal + in-vitro human)** (Cheng 2017) | — |
| 011 | Authored faithful summary | **Primary research** (Lal 2015 RCT) | — |
| 012 | Authored faithful summary | **Primary research** (SPRINT 2015 RCT) | — |
| 013 | Media archetype | **Primary research** (ASPREE 2018 RCT) | Guideline/authoritative (USPSTF 2022) |
| 014 | Marketing archetype (FTC-documented) | Regulatory enforcement action (FTC 2016) | Scientific consensus (transfer literature) |

---

## 6. Cross-cutting findings

- **Numerical fidelity (§10/J):** all load-bearing figures verified. **One issue:** 006 "35% vs
  controls" conflates the within-group BMD increase (~35%) with the placebo-adjusted difference
  (~8% in one analysis) — clarify comparison basis (does not change gold). No other numerical
  issues found.
- **Precedence (§6):** all 14 precedence rationales are sound. Specific labels are primary only
  where the trigger is genuinely present and central (004, 005, 009, 010); overclaim is correctly
  kept generic elsewhere; no case stretches a specific label to hold the count.
- **Steelman quality (§20):** WEAK / mis-targeted for **003** (correlation does not fit a predictive
  claim) and **008** (the real strongest alternative is solid, not mechanism); borderline for 001.
  All others adequate-to-strong.
- **Independence (§19):** all 14 are independent scientific propositions; **no duplicates or
  dependencies** among them or with tracked Class-A cases (Class-A overlaps deliberately avoided:
  fluoride/BMD instead of the LDL/hs-CRP biomarker cases; fasting/diabetes instead of a plant-
  compound-cancer case). Shared *structural templates* (004/005 lifestyle→mortality; 009/010 animal
  mechanism→human) are acceptable — distinct decisive propositions.
- **Boundary-diagnostic quality vs gold validity (§21):** **all 14 gold labels are defensible.**
  Boundary tension is genuinely strong for the specific-side controls (004,005,009,010), the Shape-B
  control (006), and the B3 pairs (011/012/013 and 014); it is **weak for 007** and **weak-adequate
  for 008** (B2 mechanism attractor is only lexical/cultural, not evidential) and **weak-adequate for
  003** (correlation attractor for a predictive claim).

---

## 7. Pool-level decision

```
REVISION REQUIRED
```

**Rationale:** every gold label is scientifically defensible (no gold FAIL → not BLOCKED), but the
pool is not "ACCEPT ALL 14" because of substantive boundary-quality and provenance concerns:

1. **P7A-BND-007** is a WEAK B2 boundary case (no mechanistic/preclinical evidence → not diagnostic
   for `overclaim ↔ mechanism_vs_evidence`). — substantive.
2. **P7A-BND-008** B2 membership/steelman is mis-targeted (real tension is overclaim ↔ solid). —
   substantive-borderline.
3. **Pool-wide claim-provenance** is representative/authored rather than verbatim-sourced (§3) — a
   curator standard decision.
4. **P7A-BND-006** 35% BMD comparison basis — clerical clarification.

The frozen 5/5/4 and 8/2/2/2 targets are **not** used to override these findings; if 007 (and/or
008) are revised or replaced, the resulting B2 count shortfall is reported for separate curator-
authorized replacement — **no case is silently relabeled to restore counts.**

---

## 8. Required changes (described only — NOT implemented)

1. **007 (B2 weak):** either (a) reframe the claim to cite a genuine animal/preclinical immune
   pathway used to imply human benefit (so `mechanism_vs_evidence` becomes a real attractor), or
   (b) REJECT/REPLACE for B2 with such a case; gold-as-overclaim is retained. Curator authorizes.
2. **008 (B2 borderline):** re-point the frozen `gold_alternative_reading`/steelman to **solid**
   (the genuine strongest alternative) and reconsider whether it belongs in B2 or B3; or replace.
3. **006 (clerical):** clarify "35% bone-density increase" as within-group vs placebo-adjusted.
4. **003 (steelman):** consider a stronger alternative reading (predictive claim ⇒ correlation is a
   weak alternative); gold retained.
5. **Claim provenance (pool):** curator sets the Class-B standard; if verbatim required, attach real
   quoted claims + URLs (001, 004, 005, 007, 014) and label 011/012 as authored fidelity probes.

All changes require curator authorization and a re-freeze (new fingerprints) — **out of scope for
this audit session.**

---

## 9. Security attestation (this session)

```
Holdout touched: NO
Holdout gold touched: NO
Private mappings touched: NO
Salts/envelopes touched: NO
Private raw responses touched: NO
Client material touched: NO
LaVita material touched: NO
Evaluation-model calls: 0
Case YAML / manifest / fingerprints modified: NO (byte-identical)
```
(Public web sources were re-checked as authorized; no private/client sources.)
