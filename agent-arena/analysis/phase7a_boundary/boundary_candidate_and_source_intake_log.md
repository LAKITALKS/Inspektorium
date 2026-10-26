# Phase 7A — Boundary Candidate Log & Source-Intake Log (WP-1)

Auditable record of candidate selection (§12) and source acquisition (§36) for the 14 frozen
Boundary bases. **No model was used to invent claims, generate literature, classify candidates, or
decide gold.** Search engines / primary-source fetches were used only for **source acquisition**
(`analytical evaluation model calls = 0`). Every gold label was frozen **before any model output
existed**. Rejected candidates are retained here (not deleted) with outcome-independent reasons.

**Selection discipline (frozen):** a candidate is never selected because a model got it right/wrong
(no model has run). Error history (Phase-6 DEV-0011/0013/0018/0024) motivated *family design* only;
no DEV case was copied. Provenance is `curated` (real, inspectable science curated into isolated
analytical units), never `real_world_intake` / client-derived. No LaVita / client material used.

---

## 1. Accepted cases (14) — claim source, evidence source, provisional→frozen gold

| ID | Family | Claim source | Primary evidence source | Gold (frozen) | Acquisition |
|---|---|---|---|---|---|
| P7A-BND-001 | B1 | Public/media hazard-vs-risk misreading of IARC 2015 | WHO/IARC Q&A (processed meat, Group 1) | overclaim | ACCEPT — primary regulator source |
| P7A-BND-002 | B1 | Wellness "10,000 steps required" marketing | Paluch 2022 *Lancet Public Health* + manpo-kei origin | overclaim | ACCEPT — cohort meta-analysis + provenance |
| P7A-BND-003 | B1 | Health-media "grip predicts lifespan best" | Leong 2015 PURE *Lancet* | overclaim | ACCEPT — primary cohort |
| P7A-BND-004 | B1 | Lifestyle "a daily drink protects your heart" | Zhao 2023 *JAMA Network Open* (107 studies) | correlation_vs_causation | ACCEPT — meta-analysis + abstainer-bias correction |
| P7A-BND-005 | B1 | News "get a dog to live longer" | Kramer 2019 *Circ Cardiovasc Qual Outcomes* | correlation_vs_causation | ACCEPT — meta-analysis + authors' confounding caveat |
| P7A-BND-006 | B2 | Bone-health "raises density 35%, prevents fractures" | Riggs 1990 *NEJM* (fluoride) | overclaim | ACCEPT — RCT, surrogate vs clinical endpoint |
| P7A-BND-007 | B2 | Supplement "probiotics boost immunity" | EFSA probiotic health-claim rejections (Katan 2012) | overclaim | ACCEPT — regulator evidence assessment |
| P7A-BND-008 | B2 | Marketing "vitamin C prevents colds" | Cochrane (Hemilä & Chalker 2013) | overclaim | ACCEPT — Cochrane RCT review |
| P7A-BND-009 | B2 | Longevity brand "clear zombie cells, reverse aging" | Xu 2018 *Nature Medicine* (senolytics, mice) | mechanism_vs_evidence | ACCEPT — animal interventional |
| P7A-BND-010 | B2 | Diet program "fasting reverses diabetes" | Cheng 2017 *Cell* (fasting-mimicking diet, mice) | mechanism_vs_evidence | ACCEPT — animal + in-vitro human cells |
| P7A-BND-011 | B3 | Public-health summary of Shingrix efficacy | Lal 2015 *NEJM* ZOE-50 | solid | ACCEPT — phase 3 RCT |
| P7A-BND-012 | B3 | Cardiology briefing on intensive BP control | SPRINT Research Group 2015 *NEJM* | solid | ACCEPT — RCT with harms reported |
| P7A-BND-013 | B3 | Column "everyone over 60 should take daily aspirin" | ASPREE 2018 *NEJM* + USPSTF 2022 | overclaim | ACCEPT — primary-prevention RCT + guideline |
| P7A-BND-014 | B3 | App "brain games make you smarter, prevent dementia" | FTC 2016 Lumosity action + transfer consensus | overclaim | ACCEPT — regulator + consensus |

Exact URLs/citations, study design, population, N, endpoint, and result are frozen in each case's
`robustness.provenance` block. Access date: 2026-08-16.

---

## 2. Rejected candidates (retained; outcome-independent reasons)

| Candidate | Proposed family | Provisional gold | Decision | Objective reason (outcome-independent) |
|---|---|---|---|---|
| Torcetrapib / raising HDL → heart protection (ILLUMINATE 2007) | B2 (overclaim, Shape B) | overclaim | REJECT | Duplicate-proposition risk / weak independence: Class-A already carries two "cardiovascular biomarker → heart benefit = overclaim" cases (case032 LDL drug, case045 hs-CRP). Replaced by a non-cardiovascular Shape-B surrogate (P7A-BND-006, fluoride/BMD) to preserve independence and topic diversity (§9, §32). |
| Curcumin / turmeric preclinical → "cures cancer" | B2 (mechanism_vs_evidence) | mechanism_vs_evidence | REJECT | Near-duplication of Class-A case043 (plant-derived compound → cancer, preclinical→human) and the overclaim/mechanism boundary with it is fragile. Replaced by a clearly independent Shape-A animal case (P7A-BND-010, fasting-mimicking diet → diabetes reversal) in a different domain (§32). |
| Messerli chocolate ↔ Nobel laureates (NEJM 2012, r=0.791) | B1 (correlation_vs_causation) | correlation_vs_causation? | REJECT | Claim not frozen precisely enough: the source is semi-satirical and does not cleanly assert a causal public claim, so the correlation_vs_causation trigger is ambiguous (§25). Not used to fill a slot. |
| Loneliness "as deadly as smoking 15 cigarettes/day" (Holt-Lunstad 2010) | B1 (overclaim) | overclaim vs correlation | REJECT | Genuinely ambiguous gold: the loneliness→mortality relation itself carries a correlation-vs-causation problem, so overclaim vs correlation_vs_causation remain co-defensible as primary (§25). Rejected rather than force a distribution fit. |

**No candidate was rejected for any prohibited reason** (never "model might get it right/wrong",
"too easy/hard for Haiku/Sonnet") — no model has run. All rejections are source/quality/independence
based.

---

## 3. Source-acquisition method (§36, §38)

- **Tools:** WebSearch / WebFetch for discovery and to read primary sources (journal pages,
  regulator/institution pages, press releases). This is source acquisition, **not** model
  adjudication.
- **Primary-source preference:** original papers (NEJM, Lancet, Cell, Nature Medicine, JAMA Network
  Open, Cochrane) and official regulator/institution material (WHO/IARC, EFSA, USPSTF, FTC).
- **No invented science:** `invented scientific sources = 0`. Every figure frozen in a case is taken
  from a real, inspectable source; unverified figures (e.g. a CI not seen in a primary source) were
  omitted rather than fabricated (e.g. ZOE-50 page range dropped; exact processed-meat/alcohol point
  estimates retained from primary/regulator sources).
- **Stability:** sources are journals/regulators/registries chosen so a curator can re-check them;
  no reliance on ephemeral social posts.
- `analytical evaluation model calls = 0`.

---

## 4. Post-audit REPAIR / replacement candidate flow (appended 2026-08-16)

Appended after the role-separated curator audit (`boundary_curator_gold_audit.md`) and the
human-curator-authorized repair. The original WP-1 candidate decisions above are **unchanged**.
No evaluation model was run (0 calls); public web/source research only.

### 4.1 Retirements (audit-driven, outcome-independent)

| retired | prior family/gold | objective reason | replacement |
|---|---|---|---|
| P7A-BND-003 | B1 / overclaim | real public grip-strength claim is PREDICTIVE ("single best predictor"); correlation_vs_causation is only a reflex attractor → weak B1 | P7A-BND-017 |
| P7A-BND-007 | B2 / overclaim | EFSA found NO plausible mechanism → no mechanistic evidence to over-extrapolate → not diagnostic for overclaim↔mechanism | P7A-BND-015 |
| P7A-BND-008 | B2 / overclaim | load-bearing evidence is a human RCT (Cochrane); genuine alternative is `solid`, not mechanism → not diagnostic for overclaim↔mechanism | P7A-BND-016 |

### 4.2 Accepted replacement candidates

| new ID | target family | real public claim source | evidence source(s) | gold | alternative | decision |
|---|---|---|---|---|---|---|
| P7A-BND-015 | B2 | Genentech Avastin "tumor-starving therapy" promotion (breast cancer) | E2100 RCT (PFS); FDA 2011 breast-cancer withdrawal | overclaim | mechanism_vs_evidence | ACCEPT — real anti-angiogenesis mechanism + human SURROGATE (PFS) framed as benefit; Shape-B → overclaim; genuine B2 tension |
| P7A-BND-016 | B2 | Ginkgo memory-supplement marketing ("increases blood flow to the brain") | GEM (JAMA 2008) + GuidAge (Lancet Neurol 2012) RCTs | overclaim | mechanism_vs_evidence | ACCEPT — real cerebral-blood-flow mechanism is the explicit basis; surrogate/mechanism framed as clinical benefit, contradicted by RCTs; Shape-B → overclaim |
| P7A-BND-017 | B1 | Berkeley Earth "breathing Delhi air = smoking 44 cigarettes/day" (widely reported) | IARC air-pollution Group 1 (2013) + Berkeley Earth risk heuristic | overclaim | correlation_vs_causation | ACCEPT — causation established (IARC Group 1) so correlation loses; defect = risk-metric magnitude overreach; distinct proposition from 001 |

### 4.3 Rejected repair candidates (retained; outcome-independent reasons)

| candidate | target | provisional gold | decision | objective reason |
|---|---|---|---|---|
| Resveratrol / sirtuins → "activates longevity genes, extends life" | B2 | mechanism_vs_evidence (not overclaim) | REJECT | Architecture is preclinical→implied-human (like 009/010) → gold would be mechanism_vs_evidence, not the needed overclaim; would not restore the 3 overclaim B2 slots. |
| Antioxidant vitamin E / beta-carotene → "prevents cancer" | B2 | overclaim | REJECT | Same defect as retired 008: load-bearing evidence is human RCT (ATBC/CARET/SELECT), no preclinical pathway does decisive rhetorical work; genuine alternative is solid, not mechanism. |
| Niacin/homocysteine "raises good cholesterol / lowers a heart marker → prevents heart attacks" | B2 | overclaim | REJECT | Cardiovascular-biomarker Shape-B overlaps Class-A case032 (LDL) / case045 (hs-CRP) and the 006 non-CV design intent; weak independence. |
| Loneliness "as deadly as smoking 15 cigarettes/day" (Surgeon General 2023) | B1 | overclaim vs correlation | REJECT | Ambiguous gold: loneliness→mortality causation is not established, so the correlation trigger genuinely fires → gold would be correlation, not the needed overclaim. |
| Alcohol "no safe level" cancer overclaim (WHO 2023 / IARC Group 1) | B1 | overclaim | REJECT | Strong real claim and clean overclaim logic, but shares the SUBSTANCE (alcohol) with active P7A-BND-004 → independence risk stronger than the audit tolerated; air pollution (017) chosen instead. |
| Tanning beds → melanoma (IARC Group 1) "one session = guaranteed cancer" | B1 | overclaim | REJECT | Right architecture, but a clean verbatim OVERCLAIMING public source is hard to freeze (public-health campaigns are careful); air pollution (017) has a stronger real verbatim claim. |

**No repair candidate was rejected for any prohibited reason** (no model has run). All rejections are
source/quality/independence/gold-defensibility based. Exact URLs, design, N, endpoint, and result for
every accepted replacement are frozen in the case `robustness.provenance` blocks. Access date:
2026-08-16.

---

## 5. FINAL curator-resolution slice (appended 2026-08-16)

See `boundary_final_curator_resolution.md`. No evaluation model run (0 calls); public source
verification only.

- **P7A-BND-006 RETIRED → P7A-BND-018.** First-try search for a real PUBLIC-FACING fluoride/
  osteoporosis claim found only SCIENTIFIC assertions (Pak 1989 journal titles / patents), which fail
  the public-facing standard (§7B), and no verifiable bounded ad/news claim exists (fluoride was never
  FDA-approved for osteoporosis). Per §8, retired (not archetype-excepted) and replaced.

| new ID | family | real public claim source | evidence source(s) | gold | alternative | decision |
|---|---|---|---|---|---|---|
| P7A-BND-018 | B2 | Bone Health & Osteoporosis Foundation "Get the Facts on Calcium and Vitamin D" + calcium/D supplement marketing | Zhao 2017 JAMA meta-analysis (51,145; no fracture reduction); USPSTF 2018 (against) | overclaim | mechanism_vs_evidence | ACCEPT — real ubiquitous public claim; real textbook bone mechanism (genuine B2); surrogate/mechanism→fracture contradicted by RCTs → Shape-B overclaim; preserves 006's forensic object |

- **P7A-BND-001 KEPT** (B1 tension ADEQUATE): directly causal-attributive claim; correlation engages
  the contested causal certainty of a modest observational association (> reflex), defeated by IARC
  Group 1 with a surviving hazard-vs-magnitude defect.
- **P7A-BND-017 KEPT** (B1 tension ADEQUATE, borderline disclosed): the "44 cigarettes" equivalence
  rests on an observationally-derived, contested causal PM2.5-mortality function; defeated by IARC
  Group 1 (2013), with a surviving, clearly non-causal risk-metric-transfer defect.
