# Phase 7A — Adversarial Candidate & Source-Intake Log (WP-2)

Auditable record of candidate selection and source acquisition for the 16 frozen Adversarial bases
(7A.3). **No evaluation model was run** (Haiku/Sonnet/Opus evaluation, prompt-only, run_library,
scoring): `evaluation-model calls = 0`. Search engines / primary-source fetches (WebSearch/WebFetch)
were used **only for source acquisition**. Every gold label was frozen **before any model output
existed** (`gold_status: frozen_pre_model`). No LLM was used as gold judge, case generator, second
opinion, or evaluator — Claude Opus is the repo authoring agent only.

**Selection discipline (frozen):** cases were selected from the **frozen adversarial family contract
(A1-A8)** + scientific suitability, **never** because a model might get them right/wrong (no model
has run), never for expected accuracy impact, never for aesthetic balance. Provenance is `curated`
(real, inspectable public claims + real scientific/regulatory evidence), never `real_world_intake` /
client-derived. **No LaVita / client material.** No Boundary case (active or retired) was recycled.

**Frozen family definitions used** (verbatim from
`analysis/phase7a_startup/phase7a_case_and_perturbation_contract.md` §4 /
`phase7a_robustness_design.md` §4):

| family | pre-declared forensic trigger | expected gold logic |
|---|---|---|
| A1 | decorative citation (citation present, does not support the claim) | `overclaim` (rhetorical inflation; citation is decoration) |
| A2 | citation supports **mechanism** but not **outcome** | per precedence: `mechanism_vs_evidence` if a biological mechanism is described and used to imply human benefit; else `overclaim` |
| A3 | causal verb grafted onto observational/correlational data | `correlation_vs_causation` (trigger present) |
| A4 | subgroup → general-population generalization | `overclaim` (extrapolation to unstudied population) |
| A5 | surrogate endpoint → clinical benefit ("Shape B") | **`overclaim`** — positive control that taxonomy Shape-B routing holds under mechanistic dressing |
| A6 | unsupported superiority / benchmark cherry-picking / missing comparator | `overclaim` |
| A7 | biologically plausible mechanism → implied human efficacy | `mechanism_vs_evidence` (trigger present) |
| A8 | numerically-correct value on wrong population / technically-true-but-misleading, hedges that do not repair the overclaim | `overclaim` |

**A2 routing decision (frozen):** both A2 cases instantiate the family's *primary* branch — a real,
specific, prestigious cited preclinical/animal study genuinely establishes the **mechanism/animal
outcome**, and the public claim wields that citation for a **human outcome** the study never tested →
`mechanism_vs_evidence`. A2's dominant surface pressure (a named prestige citation used for the wrong
step) is distinct from A7 (mechanistic-plausibility narrative without a decorative outcome-citation)
and from A5 (a human *surrogate endpoint* sold as clinical benefit → overclaim).

---

## 1. Accepted cases (16) — claim source, evidence source, provisional→frozen gold

| ID | Family | Real public claim source | Primary evidence source(s) | Gold (frozen) | Competing | Acquisition |
|---|---|---|---|---|---|---|
| P7A-ADV-001 | A1 | Airborne "clinically proven" cold-prevention marketing | FTC 2008 deceptive-advertising action (regulatory) | overclaim | solid | ACCEPT — non-probative "clinical study" citation |
| P7A-ADV-002 | A1 | POM Wonderful "$35M research" heart/prostate/ED ads | FTC 2013 Commission Opinion (regulatory) | overclaim | solid | ACCEPT — research-volume decoration, unsupported disease claims |
| P7A-ADV-003 | A2 | Longevity-clinic "metformin is an anti-aging drug" | Martin-Montalvo 2013 Nat Commun (mouse); TAME status | mechanism_vs_evidence | overclaim | ACCEPT — mouse-lifespan citation → human anti-aging |
| P7A-ADV-004 | A2 | Spermidine "autophagy protects heart / extends life" | Eisenberg 2016 Nat Med (mouse); human observational only | mechanism_vs_evidence | overclaim | ACCEPT — mouse cardioprotection/lifespan citation → human outcome |
| P7A-ADV-005 | A3 | "Skipping breakfast makes you gain weight" diet message | Sievert 2019 BMJ RCT meta-analysis (systematic review) | correlation_vs_causation | overclaim | ACCEPT — observational→causal; RCTs refute |
| P7A-ADV-006 | A3 | Post-shooting "violent video games cause violence" | APA 2020 resolution/statement (authoritative assessment) | correlation_vs_causation | overclaim | ACCEPT — correlational aggression→causal violence |
| P7A-ADV-007 | A4 | "Everyone should go gluten-free" wellness message | Review: no non-celiac benefit; celiac ~1% (review) | overclaim | solid | ACCEPT — celiac subgroup → general population |
| P7A-ADV-008 | A4 | "Low T" DTC testosterone campaigns | FDA 2015 restriction to classical hypogonadism (regulatory) | overclaim | solid | ACCEPT — hypogonadism subgroup → all aging men |
| P7A-ADV-009 | A5 | Biogen Aduhelm amyloid-clearance treatment claim | FDA 2021 accelerated approval on amyloid surrogate (regulatory) | overclaim | mechanism_vs_evidence | ACCEPT — Shape-B positive control (surrogate→clinical) |
| P7A-ADV-010 | A5 | Antibacterial soap "kills 99.9% of germs → protects from illness" | FDA 2016 final rule (regulatory) | overclaim | solid | ACCEPT — germ-kill surrogate → illness-prevention clinical |
| P7A-ADV-011 | A6 | Nexium "better purple pill" vs Prilosec | Kahrilas 2000 head-to-head RCT (esomeprazole 40 mg vs omeprazole 20 mg; 8-wk healing 93.7% vs 84.2%) (primary_research) + clinical reference | overclaim | solid | ACCEPT — rigged (40 vs 20 mg) comparator; primary trial bound at gold review |
| P7A-ADV-012 | A6 | Listerine "as effective as floss" campaign | McNeil-PPC v. Pfizer, 351 F.Supp.2d 226 (SDNY 2005) (court) | overclaim | solid | ACCEPT — comparator over-generalized; court enjoined |
| P7A-ADV-013 | A7 | Red-light-therapy "mitochondria → reverse aging/heal" | Photobiomodulation cytochrome c oxidase (preclinical/animal) | mechanism_vs_evidence | overclaim | ACCEPT — real mechanism, preclinical; broad human benefit unshown |
| P7A-ADV-017 | A7 | Nattokinase "dissolves clots → prevents heart attacks/strokes" | Sumi 1987 (in-vitro fibrinolysis) + systematic review of RCTs (surrogate risk factors only; no outcome trial) | mechanism_vs_evidence | overclaim | ACCEPT (gold-review replacement for retired 014) — mechanism→undemonstrated clinical outcome; no human outcome trial |
| P7A-ADV-015 | A8 | Lipitor "36% reduction in heart attacks" ad | ASCOT-LLA via FDA-approved label (1.9% vs 3.0%; 36% RRR) | overclaim | solid | ACCEPT — true relative risk hides ~1pp absolute |
| P7A-ADV-016 | A8 | Colgate "more than 80% of dentists recommend Colgate" poster | UK ASA 2007 UPHELD adjudication (multiple-response survey; rival recommended almost as much) (regulatory_assessment) | overclaim | solid | ACCEPT — technically-true survey framed to imply preference; ASA ruling bound at gold review |

(Retired at gold review: **P7A-ADV-014** psychobiotic "heal your gut to cure anxiety/depression",
formerly A7 / mechanism_vs_evidence — see §5. Its A7 slot is filled by P7A-ADV-017.)

Exact URLs/citations, study design, population, endpoint, and result are frozen in each case's
`robustness.provenance` block. Access date: 2026-08-16.

---

## 2. Rejected / re-scoped candidates (retained; outcome-independent reasons)

| Candidate | Proposed family | Provisional gold | Decision | Objective reason (outcome-independent) |
|---|---|---|---|---|
| Lion's Mane (NGF/erinacine) → prevents dementia | A2 (mechanism_vs_evidence) | mechanism_vs_evidence | REJECT | Human-RCT confound: a 49-week double-blind trial (erinacine-A mycelia) reports cognitive/MMSE improvement in early Alzheimer's, so load-bearing evidence is a human RCT and the genuine alternative is solid/overclaim — not a clean mechanism_vs_evidence (the retired-Boundary-008 failure mode). Replaced by spermidine (P7A-ADV-004), whose human evidence is cleanly observational-only. |
| "Lower your A1c is better / tight control saves lives" (ACCORD) | A5 (Shape B) | overclaim | REJECT (re-scoped) | Partial-truth complication: DCCT/UKPDS show lower A1c genuinely reduces microvascular complications, so "lower A1c → fewer complications" is largely true; only aggressive targets (ACCORD, <6%) harm. Gold becomes contestable (solid vs overclaim). Replaced by antibacterial soap (P7A-ADV-010), a clean Shape-B with no partial-truth. |
| Curcumin/turmeric preclinical → cancer/Alzheimer's | A2 or A7 | mechanism_vs_evidence | REJECT | Near-duplication of Class-A case043 (plant-derived compound → cancer, preclinical→human), which the Boundary repair already flagged as a duplicate risk. Independence not defensible. |
| Resveratrol/sirtuins → "activates longevity genes, extends life" | A7 | mechanism_vs_evidence | REJECT | Already considered and rejected in the Boundary repair (preclinical→implied-human, redundant architecture); avoided to preserve independence from the Boundary candidate bank. |
| Antioxidant vitamins (E/beta-carotene) neutralize free radicals → prevent cancer/aging | A7 | mechanism_vs_evidence | REJECT | Load-bearing evidence is large human RCTs (SELECT/ATBC), largely null/harmful → genuine alternative is overclaim, not mechanism (retired-Boundary-008 failure mode). Not a clean A7. |
| EGCG/green tea preclinical apoptosis → "fights cancer" | A2/A7 | mechanism_vs_evidence | REJECT | Same decisive-proposition class as Class-A case043 (plant compound → cancer, preclinical→human). Independence risk. |
| Skechers Shape-ups "tone your muscles more than regular sneakers" (FTC) | A6 | overclaim | REJECT (not needed) | Strong FTC case, but the dominant surface is a decorative "clinically proven" (A1-flavored) rather than a clean comparator manipulation; Nexium (rigged comparator) + Listerine (over-generalized comparator) are purer A6 instances. Retained here as a valid alternative. |

**No candidate was rejected for any prohibited reason** (never "model might get it right/wrong",
"too easy/hard for Haiku/Sonnet", expected accuracy impact, aesthetic balance) — no model has run.
All rejections are provenance / evidence-quality / independence / gold-defensibility based.

---

## 3. Source-acquisition method

- **Tools:** WebSearch / WebFetch for discovery and to read authoritative sources (journal pages,
  regulator/enforcement records, court opinions, professional-body statements). This is source
  acquisition, **not** model adjudication.
- **Claim provenance ≠ evidence provenance** (§11): every case separately records the **public claim
  source** (who made the real claim) and the **scientific/forensic evidence source(s)**, each with a
  declared controlled-vocabulary `source_role`. Regulators/courts/professional bodies (FTC, FDA, ASA,
  APA, US federal court) are labeled `regulatory_assessment`, **never** `primary_research`.
- **No invented science:** `invented scientific sources = 0`; `authored-archetype-only active claims
  = 0`. Every load-bearing number is taken from a real, inspectable source; unverified figures were
  described qualitatively or omitted rather than fabricated (e.g. ASCOT-LLA N/follow-up stated
  qualitatively; only the verified 1.9% vs 3.0% / 36% RRR frozen).
- **Stability:** sources are regulators, courts, journals, professional bodies, and durable
  references chosen so a curator can re-check them.
- **Curator-review flags (v1.0, not blocking):** P7A-ADV-011 (Nexium) evidence is a clinical
  reference summarising the head-to-head trials — a primary equal-dose healing trial may be attached
  at gold review; P7A-ADV-016 (Colgate) evidence documents the ASA 2007 adjudication via a reference
  — the primary ASA adjudication may be attached at gold review.
- `evaluation-model calls = 0`.

---

## 5. WP-2 gold-review repairs (appended 2026-08-16)

Appended after the human-curator blocker-only gold review
(`adversarial_human_curator_gold_review.md`). No evaluation model was run (0 calls); public
web/source verification only. The original WP-2 candidate decisions above are unchanged except as noted.

### 5.1 Retirement + replacement (scientific, gold blocker)

| retired | prior family/gold | objective reason | replacement |
|---|---|---|---|
| P7A-ADV-014 (psychobiotic) | A7 / mechanism_vs_evidence | Direct human RCT/meta-analytic evidence exists for probiotics in depression (Nikolova 2019/2021; Goh 2019): adjunct benefit (SMD ~0.83), NOT stand-alone (SMD ~ -0.02). The frozen claim ("cure … no medication needed") therefore exaggerates/over-generalizes real human OUTCOME evidence, so `overclaim` is at least equally defensible and `mechanism_vs_evidence` is not uniquely defensible (WP-2 §7). Not a clean A7. | P7A-ADV-017 |

| new ID | family | real public claim | evidence | gold | alternative | decision |
|---|---|---|---|---|---|---|
| P7A-ADV-017 | A7 | Nattokinase "natural clot buster → prevents heart attacks/strokes" | Sumi 1987 (Experientia, in-vitro fibrinolysis, PMID 3478223) + systematic review/meta-analysis of RCTs (Rev Cardiovasc Med 2023;24(8):234, PMID 39076715: surrogate risk factors only, NO outcome trial) | mechanism_vs_evidence | overclaim | ACCEPT — the claimed CLINICAL OUTCOME (MI/stroke prevention) has zero human outcome trials, so mechanism→undemonstrated-benefit is uniquely defensible (not the probiotics situation) |

### 5.2 Source bindings / clerical corrections (in place, no proposition change)

| case | change | verified fact |
|---|---|---|
| P7A-ADV-011 (Nexium) | Bound primary head-to-head trial (was secondary_discovery only) | Kahrilas 2000 (Aliment Pharmacol Ther): esomeprazole 40 mg vs omeprazole 20 mg (unequal doses), 8-wk healing 93.7% vs 84.2% (p<0.001). Superiority rests on the unequal-dose comparison → forensic proposition confirmed; gold overclaim unchanged. |
| P7A-ADV-016 (Colgate) | Corrected claim span to the real ASA-challenged wording + bound the authoritative ASA adjudication (regulatory_assessment) | Real claim: "More than 80% of dentists recommend Colgate"; UK ASA UPHELD complaints (Jan 2007) — survey allowed multiple recommendations, a rival was recommended almost as much → misleading. Gold overclaim unchanged. |
| P7A-ADV-006 (video games) | Clerical clarification: APA is an authoritative scientific body, not a government regulator; `regulatory_assessment` role used in its "authoritative assessment" sense (no schema change). | — |

### 5.3 Cases confirmed unchanged at gold review

P7A-ADV-015 (Lipitor): A8 misleadingness CONFIRMED — the ad headlines the relative 36% while the
~1.1pp absolute reduction (1.9% vs 3.0%) sits in fine print; the reader meaning materially exceeds the
absolute benefit (more than "ARR would also be useful"). Gold overclaim retained. All other cases
(001-010, 012-013) reviewed briefly: no blocker; PASS.

`evaluation-model calls = 0` (WP-2 gold review).
