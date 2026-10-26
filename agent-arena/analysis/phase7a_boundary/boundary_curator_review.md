# Phase 7A — Boundary Pool Curator Review (WP-1)

Compact review surface for the 14 frozen Boundary bases (data class B). Lets the curator inspect
every case — exact claim, source, evidence basis, gold, alternative, precedence, difficulty,
fingerprint — without reading raw YAML. **Gold frozen pre-model; 0 model calls; holdout untouched.**
Full records: `tasks/study_forensics_robustness/P7A-BND-*.yaml`. This summary does not replace them.

---

## Per-case review
### P7A-BND-001 — B1 (overclaim <-> correlation_vs_causation) — gold: **overclaim** · D3

- **Exact claim:** "same category as cigarettes and asbestos ... as dangerous as smoking ... no safe amount"
- **Claim source:** Public/media misinterpretation of the 2015 IARC processed-meat classification (hazard-vs-risk) (news_media_summary)
- **Evidence basis:** IARC/WHO Q&A: Carcinogenicity of the consumption of red meat and processed meat (Oct 2015)
  - design: IARC Monographs Working Group evaluation (systematic review of epidemiological + mechanistic evidence); population: General population dietary epidemiology
  - result: Group 1 (carcinogenic to humans); ~18% higher relative risk of colorectal cancer per 50 g/day; ~34,000 attributable cancer deaths/yr worldwide vs ~1,000,000 (tobacco), 600,000 (alcohol)
  - tier: High-tier causal classification (IARC Group 1)
  - url: https://www.who.int/news-room/questions-and-answers/item/cancer-carcinogenicity-of-the-consumption-of-red-meat-and-processed-meat
- **Alternative reading:** correlation_vs_causation — Alternative: correlation_vs_causation. Plausible because the whole processed-meat/cancer question is epidemiological, and readers frequently attack diet–disease claims on causal-inference grounds. It loses under precedence because the causal relationship is no…
- **Precedence rationale:** overclaim is the generic/residual label (rhetorical inflation). correlation_vs_causation outranks it ONLY if a causal claim is drawn from a non-causal/confounded design. Here causation is the ESTABLISHED IARC judgment, not an inference from a confounded design, so the specific trigger is absent and the primary stays ov…
- **Difficulty (D3):** >=2 plausible labels (overclaim vs correlation_vs_causation); resolving it requires the non-obvious hazard-vs-risk distinction and knowing that IARC already established causation; evidence-tier nuance (high-tier causal classification misuse…
- **Fingerprint:** `22914e6a2c543f2e7c8869142606253d75856a99673b9c095068790bef784f38`

### P7A-BND-002 — B1 (overclaim <-> correlation_vs_causation) — gold: **overclaim** · D2

- **Exact claim:** "you must walk 10,000 steps every day to stay healthy ... Anything less and you are not doing enough"
- **Claim source:** Wellness marketing '10,000 steps a day' health mandate (marketing_claim)
- **Evidence basis:** Paluch AE et al. Daily steps and all-cause mortality: a meta-analysis of 15 international cohorts. Lancet Public Health 2022;7(3):e219-e228
  - design: Meta-analysis of prospective cohorts (observational); population: 47,471 adults (Asia, Australia, Europe, North America)
  - result: Inverse dose-response that plateaus at ~6,000-8,000 steps/day (older adults 60+) and ~8,000-10,000 (younger adults); no clear additional benefit beyond
  - tier: Observational cohort meta-analysis
  - url: https://pubmed.ncbi.nlm.nih.gov/35247352/
- **Alternative reading:** correlation_vs_causation — Alternative: correlation_vs_causation. Plausible because step-count/mortality data are observational and confounded (healthier people walk more). It loses under precedence because the claim's decisive defect is the fabricated specific threshold and all-or-noth…
- **Precedence rationale:** The specific correlation_vs_causation trigger (causal claim from a non-causal design) is not the decisive defect; even if walking helps, the claim's unsupported 10,000 threshold and all-or-nothing certainty are generic inflation. Under docs/taxonomy_precedence.md the primary stays overclaim; correlation_vs_causation is…
- **Difficulty (D2):** One primary (overclaim) plus one genuinely plausible alternate (correlation_vs_causation, invited by the observational data); precedence decides. Moderate claim-evidence distance; no deep evidence-tier conflict. Property-based tagging.
- **Fingerprint:** `7568019314d45315103487da19c99cd92bbf5a6b5557546bd78ea744dc2559ce`

### P7A-BND-003 — B1 (overclaim <-> correlation_vs_causation) — gold: **overclaim** · D3

- **Exact claim:** "the single best predictor of how long you will live ... read your own life expectancy"
- **Claim source:** Health-media 'grip strength predicts your lifespan' feature (news_media_summary)
- **Evidence basis:** Leong DP et al. Prognostic value of grip strength: findings from the PURE study. Lancet 2015;386(9990):266-273
  - design: Prospective cohort (observational, prognostic); population: ~139,691 adults, 17 countries; median follow-up ~4 years
  - result: Each 5-kg decrease in grip ~16% higher all-cause mortality (also ~17% CV/non-CV mortality, 7% MI, 9% stroke); grip a stronger predictor of mortality than systolic BP in this cohort
  - tier: Large observational cohort (prognostic association)
  - url: https://pubmed.ncbi.nlm.nih.gov/25982160/
- **Alternative reading:** correlation_vs_causation — Alternative: correlation_vs_causation. Plausible because grip strength is an observational marker and confounded by underlying illness/frailty. It loses under precedence because the claim asserts PREDICTION, not causation, and makes no interventional leap; the…
- **Precedence rationale:** correlation_vs_causation requires a causal claim from a non-causal design. The claim is predictive, not causal (no intervention, no "grip causes longevity"), so the specific trigger is absent. The defect is inflated superiority/magnitude/individual-forecast = generic overclaim, which remains primary under docs/taxonomy…
- **Difficulty (D3):** >=2 plausible labels and a subtle discriminator: prediction vs causation. The observational marker strongly invites correlation_vs_causation, and separating "best predictor" overreach from a causal error requires care; large claim-evidence …
- **Fingerprint:** `4bb53f1b718f66ae9d504539255a92e9eb35fff2124b4770fe70ce0e50c0e591`

### P7A-BND-004 — B1 (overclaim <-> correlation_vs_causation) — gold: **correlation_vs_causation** · D2

- **Exact claim:** "a daily glass of wine protects your heart and helps you live longer ... if you don't drink, consider starting"
- **Claim source:** Lifestyle 'a daily drink protects your heart' recommendation (J-curve) (news_media_summary)
- **Evidence basis:** Zhao J et al. Association Between Daily Alcohol Intake and Risk of All-Cause Mortality: A Systematic Review and Meta-analyses. JAMA Network Open 2023;6(3):e236185
  - design: Systematic review + meta-analysis of prospective cohort studies (observational); population: 107 cohort studies; >4.8 million participants
  - result: No statistically significant mortality reduction for low-volume drinkers vs lifetime nondrinkers after adjusting for study biases; risk rose above ~2 drinks/day (women) and ~3/day (men); apparent J-curve attributed to abstainer/sick-quitter bias
  - tier: Meta-analysis of observational cohorts (confounded; corrupted reference group in earlier studies)
  - url: https://pubmed.ncbi.nlm.nih.gov/37000449/
- **Alternative reading:** overclaim — Alternative: overclaim. Plausible because "protects your heart / live longer" is rhetorical inflation. It is the secondary reading; it loses as PRIMARY because the core, structural defect is the causal inference from a confounded observational design (abstaine…
- **Precedence rationale:** The correlation_vs_causation trigger (causal claim from a confounded, non-causal design with a biased comparator) is genuinely present and is the core error, so under docs/taxonomy_precedence.md rule 1 it outranks the generic overclaim reading, which is retained as secondary.
- **Difficulty (D2):** One primary (correlation_vs_causation) with a genuinely plausible alternate (overclaim); precedence decides. The causal/prescriptive framing and the well-known abstainer bias make the specific trigger clear, keeping this at D2 rather than D…
- **Fingerprint:** `460714ae923c226dbfcf5852f33574303f707d5d8c52ae7cb4f6c7abd2c3bf1b`

### P7A-BND-005 — B1 (overclaim <-> correlation_vs_causation) — gold: **correlation_vs_causation** · D2

- **Exact claim:** "Owning a dog reduces your risk of death by 24% - so if you want to live longer, get a dog"
- **Claim source:** News 'get a dog to live longer' summary of the dog-ownership survival meta-analysis (news_media_summary)
- **Evidence basis:** Kramer CK, Mehmood S, Suen RS. Dog Ownership and Survival: A Systematic Review and Meta-Analysis. Circ Cardiovasc Qual Outcomes 2019;12(10):e005554
  - design: Systematic review + meta-analysis of observational (non-randomized) studies; population: 10 studies; >3.8 million people; mean follow-up ~10 years
  - result: 24% lower relative risk of all-cause mortality; 31% lower CV mortality
  - tier: Meta-analysis of observational cohorts (confounded)
  - url: https://www.ahajournals.org/doi/10.1161/circoutcomes.119.005554
- **Alternative reading:** overclaim — Alternative: overclaim. Plausible because "the science proves" / "dogs make owners healthier" overstate certainty. It is secondary; it loses as PRIMARY because the central, structural defect is causal inference from a confounded, self-selected observational de…
- **Precedence rationale:** The correlation_vs_causation trigger (causal, prescriptive claim from a confounded, self-selected observational design) is genuinely present and central; under docs/taxonomy_precedence.md rule 1 it outranks the generic overclaim reading, which is retained as secondary.
- **Difficulty (D2):** One primary (correlation_vs_causation) with a plausible overclaim alternate; precedence decides. The authors' explicit no-causation caveat makes the specific trigger clear (D2, not D3). Property-based tagging.
- **Fingerprint:** `0be9954217636af499db747cd33e00da6dc062cb2d92ab00b6692da680b8981a`

### P7A-BND-006 — B2 (overclaim <-> mechanism_vs_evidence) — gold: **overclaim** · D3

- **Exact claim:** "increases your spinal bone mineral density by 35% - denser bones are stronger bones, so it protects you from the fractures"
- **Claim source:** Bone-health marketing: bone-density gain framed as fracture prevention (marketing_claim)
- **Evidence basis:** Riggs BL, Hodgson SF, O'Fallon WM, et al. Effect of fluoride treatment on the fracture rate in postmenopausal women with osteoporosis. N Engl J Med 1990;322(12):802-809 (PMID 2407957)
  - design: Randomized controlled trial (4 years); population: Postmenopausal women with osteoporosis
  - result: Spinal BMD +~35%, but no significant reduction in new vertebral fractures and an approximately three-fold increase in non-vertebral fractures; added bone structurally abnormal/fragile
  - tier: RCT with clinical fracture endpoint (surrogate BMD improved, clinical outcome did not)
  - url: https://www.nejm.org/doi/full/10.1056/NEJM199003223221203
- **Alternative reading:** mechanism_vs_evidence — Alternative: mechanism_vs_evidence. Plausible because a biological "denser = stronger" rationale is invoked. It loses under precedence because the evidence is a human trial with a surrogate ENDPOINT (BMD), not an animal/preclinical pathway; the taxonomy routes…
- **Precedence rationale:** mechanism_vs_evidence requires a described animal/preclinical pathway extrapolated to human benefit. Here the evidence is a human RCT with a surrogate endpoint (BMD); the taxonomy explicitly excludes the surrogate-to-clinical gap ("Shape B") and routes it to overclaim (docs/taxonomy_precedence.md; case054). Primary = o…
- **Difficulty (D3):** >=2 plausible labels and a subtle precedence call: a biological "denser = stronger" rationale invites mechanism_vs_evidence, but the frozen taxonomy routes surrogate-to-clinical to overclaim. Evidence-tier nuance (surrogate vs clinical endp…
- **Fingerprint:** `84a34b22ef11d9830caf650829d10780c1f250c1d775cfdc75ebdd8c10759944`

### P7A-BND-007 — B2 (overclaim <-> mechanism_vs_evidence) — gold: **overclaim** · D2

- **Exact claim:** "boosts your immune system and strengthens your body's natural defences"
- **Claim source:** Probiotic supplement 'boosts your immune system' label claim (marketing_claim)
- **Evidence basis:** EFSA NDA Panel scientific opinions rejecting probiotic immune-health claims (e.g. Nutrimune); summarized in Katan MB, 'Why the European Food Safety Authority was right to reject health claims for probiotics' (2012)
  - design: Regulatory evidence assessment (systematic appraisal of submitted human studies); population: General population; submitted human trials
  - result: All probiotic immune-health claims rejected; for Nutrimune, evidence insufficient for cause-and-effect, human study not replicated, and no plausible in-vivo mechanism provided
  - tier: Regulatory evidence assessment (high-tier appraisal finding evidence insufficient)
  - url: https://pubmed.ncbi.nlm.nih.gov/22683835/
- **Alternative reading:** mechanism_vs_evidence — Alternative: mechanism_vs_evidence. Plausible because probiotics carry a gut-immune mechanism narrative. It loses under precedence because no described animal/preclinical pathway is being extrapolated (EFSA found no plausible mechanism at all); the claim is ge…
- **Precedence rationale:** mechanism_vs_evidence requires a described animal/preclinical pathway extrapolated to human benefit. EFSA found no plausible mechanism at all, so there is nothing for the specific label to attach to; the claim is generic unsupported-breadth inflation, primary = overclaim (docs/taxonomy_precedence.md rule 2).
- **Difficulty (D2):** One primary (overclaim) plus one plausible alternate (mechanism_vs_evidence, invited by the gut-immune narrative); precedence decides. Low evidence-tier conflict (regulator clearly found the claim unsubstantiated). Property-based tagging.
- **Fingerprint:** `a9e63cc6eb0f4f0d76207d8cda0866bd4c23faf87d3172c8a4de993c9bad4050`

### P7A-BND-008 — B2 (overclaim <-> mechanism_vs_evidence) — gold: **overclaim** · D2

- **Exact claim:** "Take vitamin C every day to boost your immunity and prevent colds - it stops you getting sick"
- **Claim source:** Vitamin C supplement 'prevent colds / boost immunity' marketing claim (marketing_claim)
- **Evidence basis:** Hemila H, Chalker E. Vitamin C for preventing and treating the common cold. Cochrane Database Syst Rev 2013;(1):CD000980
  - design: Systematic review + meta-analysis of randomized controlled trials; population: General population (incl. a small extreme-physical-stress subgroup)
  - result: No effect on incidence in the general population (29 comparisons, 11,306 participants); modest duration reduction (~8% adults, ~14% children); incidence halved only in extreme-physical-stress subgroup (5 trials, 598 participants)
  - tier: Cochrane review of RCTs (highest human-evidence tier)
  - url: https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000980.pub4/full
- **Alternative reading:** mechanism_vs_evidence — Alternative: mechanism_vs_evidence. Plausible via the antioxidant/immune mechanism narrative. It loses under precedence because direct human RCT evidence exists and contradicts the prevention claim; there is no mechanism-to-human extrapolation gap to adjudicat…
- **Precedence rationale:** mechanism_vs_evidence is for a described animal/preclinical pathway implying an undemonstrated human benefit. Here human RCT evidence exists and contradicts the prevention claim, so there is no mechanism-to-human gap; the failure is inflation against human data = overclaim (docs/taxonomy_precedence.md rule 2).
- **Difficulty (D2):** One primary (overclaim) plus one plausible alternate (mechanism_vs_evidence, invited by the antioxidant/immune narrative); precedence decides. Low evidence-tier conflict — Cochrane RCT evidence is clear. Property-based tagging.
- **Fingerprint:** `06d0a17e9d51e0c470c35fbfb28c6728573cba5d228be1238f540588970d026a`

### P7A-BND-009 — B2 (overclaim <-> mechanism_vs_evidence) — gold: **mechanism_vs_evidence** · D2

- **Exact claim:** "Clear them out with senolytics and you can reverse aging, restore youthful function, and add healthy years to your life"
- **Claim source:** Longevity supplement 'clear zombie cells to reverse aging' senolytic claim (marketing_claim)
- **Evidence basis:** Xu M, Pirtskhalava T, Farr JN, et al. Senolytics improve physical function and increase lifespan in old age. Nat Med 2018;24(8):1246-1256
  - design: Preclinical interventional study (mice) + human senescent-cell explant work; population: Naturally aged mice; transplant models
  - result: Senolytics improved physical function and extended remaining lifespan in aged mice; senescent-cell transplant caused persistent dysfunction
  - tier: Animal (preclinical) interventional evidence
  - url: https://www.nature.com/articles/s41591-018-0092-9
- **Alternative reading:** overclaim — Alternative: overclaim. Plausible because the language is inflated marketing. It is the secondary reading; it loses as PRIMARY because the decisive, structural defect is the animal-mechanism-to- human-benefit leap (Shape A), which is the mechanism_vs_evidence …
- **Precedence rationale:** A described animal/preclinical mechanism (senescent-cell clearance in mice) used to imply an undemonstrated human clinical benefit is the mechanism_vs_evidence trigger (Shape A). It is genuinely present and central, so under docs/taxonomy_precedence.md rule 1 it outranks the generic overclaim reading, which is retained…
- **Difficulty (D2):** One primary (mechanism_vs_evidence) with a genuinely plausible alternate (overclaim, invited by the inflated marketing); precedence decides. The animal-to-human structure is clear (Shape A), keeping this at D2. Property-based tagging.
- **Fingerprint:** `6f308d750bc7ca66d0e9264f96332fc3717a14e057aed54b97a2edf0101d01b1`

### P7A-BND-010 — B2 (overclaim <-> mechanism_vs_evidence) — gold: **mechanism_vs_evidence** · D3

- **Exact claim:** "Fasting regenerates your pancreas and reverses diabetes ... regrow the insulin-producing cells you've lost and cure the disease at its root - no drugs required"
- **Claim source:** Fasting diet program 'regenerate your pancreas / reverse diabetes' claim (marketing_claim)
- **Evidence basis:** Cheng CW, Villani V, Buono R, et al. Fasting-Mimicking Diet Promotes Ngn3-Driven Beta-Cell Regeneration to Reverse Diabetes. Cell 2017;168(5):775-788
  - design: Preclinical interventional study (mice) + in-vitro human donor-cell experiments; population: Type 1 and type 2 diabetes mouse models; cultured human donor pancreatic cells
  - result: In mice, FMD drove Ngn3-based beta-cell regeneration and reversed diabetes; in human donor cells fasting-like conditions raised Ngn3/insulin expression
  - tier: Animal (preclinical) + in-vitro human cells; no patient clinical trial
  - url: https://www.cell.com/fulltext/S0092-8674(17)30130-7
- **Alternative reading:** overclaim — Alternative: overclaim. Plausible because "cure ... no drugs required" is inflated. It is secondary; it loses as PRIMARY because the decisive, structural defect is the animal/preclinical regeneration mechanism extrapolated to a human cure without patient evide…
- **Precedence rationale:** A described animal/preclinical pathway (Ngn3-driven beta-cell regeneration in mice, plus in-vitro human cells) used to imply an undemonstrated human clinical cure is the mechanism_vs_evidence trigger (Shape A/C). It is present and central, so under docs/taxonomy_precedence.md rule 1 it outranks generic overclaim, which…
- **Difficulty (D3):** >=2 plausible labels, plus an evidence-tier wrinkle: in-vitro human donor-cell data are present and could be mistaken for demonstrated human benefit (they are preclinical). Distinguishing the animal/preclinical mechanism-to-human leap from …
- **Fingerprint:** `90175bf991966aef06b7dfc5fb0c4326be183babeb31a758ba0ec7de51cdb0cc`

### P7A-BND-011 — B3 (solid <-> overclaim) — gold: **solid** · D2

- **Exact claim:** "reduced the incidence of shingles by 97.2% compared with placebo ... adults aged 50 and older"
- **Claim source:** Public-health summary of the ZOE-50 Shingrix efficacy result (public_health_summary)
- **Evidence basis:** Lal H, Cunningham AL, Godeaux O, et al. Efficacy of an Adjuvanted Herpes Zoster Subunit Vaccine in Older Adults (ZOE-50). N Engl J Med 2015;372(22) (doi:10.1056/NEJMoa1501184)
  - design: Phase 3 randomized, placebo-controlled trial (18 countries); population: 15,411 adults >=50 (7,698 vaccine / 7,713 placebo)
  - result: Vaccine efficacy 97.2% against herpes zoster in adults >=50 over a mean follow-up of ~3.2 years
  - tier: Large phase 3 RCT with clinical endpoint (highest tier)
  - url: https://www.nejm.org/doi/full/10.1056/NEJMoa1501184
- **Alternative reading:** overclaim — Alternative: overclaim. The strongest reason to consider it: a 97.2% efficacy claim is unusually high and superficially resembles marketing inflation. It loses because the figure and scope are faithful to the ZOE-50 RCT and are not extended beyond the trial; c…
- **Precedence rationale:** overclaim requires framing that exceeds the evidence. The claim's magnitude and scope match the RCT and are not extended, so the defining trigger for overclaim is absent and the primary is solid. (Precedence among labels only re-routes when a failure exists; here the honest-reporting definition of solid governs.)
- **Difficulty (D2):** One primary (solid) with a plausible alternate (overclaim, invited by the dramatic 97.2% figure); fidelity check decides. Low evidence-tier conflict (single high-tier RCT). Property-based tagging.
- **Fingerprint:** `d13dd68ab361c65541a4831dfbba17006227393b33b7bcbb7aeb60a5dd117d2b`

### P7A-BND-012 — B3 (solid <-> overclaim) — gold: **solid** · D3

- **Exact claim:** "reduced major cardiovascular events by about 25% and all-cause death by about 27% ... also increased the rates of hypotension, fainting, electrolyte abnormalities, and acute kidney injury"
- **Claim source:** Cardiology briefing summarizing the SPRINT intensive-vs-standard BP trial (clinical_summary)
- **Evidence basis:** The SPRINT Research Group. A Randomized Trial of Intensive versus Standard Blood-Pressure Control. N Engl J Med 2015;373(22):2103-2116
  - design: Randomized controlled trial (stopped early); population: 9,361 adults at increased CV risk WITHOUT diabetes or prior stroke
  - result: Primary composite reduced ~25% (HR ~0.75) and all-cause mortality ~27% (HR ~0.73); higher rates of hypotension, syncope, electrolyte abnormalities, and acute kidney injury in the intensive group
  - tier: Large RCT with clinical endpoints
  - url: https://pubmed.ncbi.nlm.nih.gov/26551272/
- **Alternative reading:** overclaim — Alternative: overclaim. Strongest reason to consider it: the ~25%/27% reductions are dramatic and intensive BP targeting is clinically debated, so one might suspect inflation or selective emphasis. It loses because the briefing explicitly reports the harms, th…
- **Precedence rationale:** overclaim requires framing that exceeds the evidence. Here harms, early stop, and generalizability limits are reported and the claim is bounded to the studied population, so no overclaim trigger exists; the honest-reporting definition of solid governs.
- **Difficulty (D3):** Two plausible labels and a subtle call: dramatic effect sizes plus a live clinical debate about BP targets pull toward overclaim, but the report is faithful and caveated. Distinguishing honest mixed reporting from inflation requires care. P…
- **Fingerprint:** `89149c815f2f17b66a212dedff3e0f41fc561edfc2558450ac5a4bd93a26dcb8`

### P7A-BND-013 — B3 (solid <-> overclaim) — gold: **overclaim** · D3

- **Exact claim:** "Everyone over 60 should take a low-dose aspirin every day ... There's no reason not to"
- **Claim source:** Health-column 'everyone over 60 should take daily aspirin' advice (news_media_summary)
- **Evidence basis:** McNeil JJ, Wolfe R, Woods RL, et al. (ASPREE). Effect of Aspirin on Cardiovascular Events and Bleeding in the Healthy Elderly. N Engl J Med 2018;379(16):1509-1518
  - design: Randomized, double-blind, placebo-controlled primary-prevention trial; population: ~19,114 community-dwelling healthy older adults (mostly 70+) without established CVD
  - result: No significant CV benefit (HR 0.95, 95% CI 0.83-1.08); significant increase in major hemorrhage (HR 1.38, 95% CI 1.18-1.62); higher all-cause mortality in the aspirin group
  - tier: Large primary-prevention RCT
  - url: https://www.nejm.org/doi/full/10.1056/NEJMoa1805819
- **Alternative reading:** solid — Alternative: solid. Strongest reason to consider it: aspirin does prevent cardiovascular events in secondary-prevention patients, so the claim is not baseless. It loses because the claim over-generalizes that benefit to all healthy adults over 60 (where RCTs s…
- **Precedence rationale:** No specific-label trigger is present (randomized evidence rules out correlation_vs_causation; no animal/mechanism pathway rules out mechanism_vs_evidence). The failure is generic: framing exceeds the evidence via population over-generalization + harms omission = overclaim vs the tempting solid.
- **Difficulty (D3):** Two plausible labels and a subtle discriminator: the claim contains a real kernel (secondary- prevention benefit), so distinguishing over-generalization (overclaim) from a defensible scoped claim (solid) requires the primary/secondary-preve…
- **Fingerprint:** `d1d305dee137bd324a99060af391f0853ca7bd309dfbeb1aec0dd247bab585c7`

### P7A-BND-014 — B3 (solid <-> overclaim) — gold: **overclaim** · D2

- **Exact claim:** "make you smarter, sharpen your memory and attention in everyday life, and protect you against age-related cognitive decline and dementia"
- **Claim source:** Brain-training app 'smarter + prevents dementia' marketing claim (marketing_claim)
- **Evidence basis:** US Federal Trade Commission. Lumosity to Pay $2 Million to Settle FTC Deceptive Advertising Charges for Its 'Brain Training' Program (Jan 5, 2016)
  - design: Regulatory enforcement action (FTC); population: Consumers of the Lumosity brain-training program
  - result: $2M settlement; FTC found the company 'simply did not have the science to back up its ads' for work/school performance and cognitive-decline/dementia claims
  - tier: Regulatory enforcement + scientific-consensus context
  - url: https://www.ftc.gov/news-events/news/press-releases/2016/01/lumosity-pay-2-million-settle-ftc-deceptive-advertising-charges-its-brain-training-program
- **Alternative reading:** solid — Alternative: solid. Strongest reason to consider it: brain-training genuinely improves performance on the trained tasks, so the claim is not baseless. It loses because the marketing generalizes to everyday intelligence and dementia prevention — far transfer an…
- **Precedence rationale:** No specific-label trigger applies (training studies are experimental -> not correlation_vs_causation; no animal/mechanism pathway -> not mechanism_vs_evidence). The failure is generic: a narrow true effect generalized to broad benefit and disease prevention = overclaim vs the tempting solid.
- **Difficulty (D2):** One primary (overclaim) with a plausible alternate (solid, invited by the real trained-task effect); the fidelity check (far transfer? disease prevention?) decides. Moderate claim-evidence distance; low evidence-tier conflict. Property-base…
- **Fingerprint:** `f6f14577507884bb35918a33a11edc800491df1fb208da056ff38564b99a9a41`

---

## Gold-distribution matrix (§33)

| Family | Case ID | Gold | Alternative | Difficulty |
|---|---|---|---|---|
| B1 | P7A-BND-001 | overclaim | correlation_vs_causation | D3 |
| B1 | P7A-BND-002 | overclaim | correlation_vs_causation | D2 |
| B1 | P7A-BND-003 | overclaim | correlation_vs_causation | D3 |
| B1 | P7A-BND-004 | correlation_vs_causation | overclaim | D2 |
| B1 | P7A-BND-005 | correlation_vs_causation | overclaim | D2 |
| B2 | P7A-BND-006 | overclaim | mechanism_vs_evidence | D3 |
| B2 | P7A-BND-007 | overclaim | mechanism_vs_evidence | D2 |
| B2 | P7A-BND-008 | overclaim | mechanism_vs_evidence | D2 |
| B2 | P7A-BND-009 | mechanism_vs_evidence | overclaim | D2 |
| B2 | P7A-BND-010 | mechanism_vs_evidence | overclaim | D3 |
| B3 | P7A-BND-011 | solid | overclaim | D2 |
| B3 | P7A-BND-012 | solid | overclaim | D3 |
| B3 | P7A-BND-013 | overclaim | solid | D3 |
| B3 | P7A-BND-014 | overclaim | solid | D2 |

## Aggregate counts

- **Family:** B1=5 · B2=5 · B3=4  (expected 5/5/4 — OK)
- **Gold:** overclaim=8 · correlation_vs_causation=2 · mechanism_vs_evidence=2 · solid=2  (expected 8/2/2/2 — OK)
- **Directional:** B1 = 3 overclaim / 2 correlation_vs_causation · B2 = 3 overclaim / 2 mechanism_vs_evidence · B3 = 2 solid / 2 overclaim
- **Difficulty:** D2=8 · D3=6 · D1=0 (boundary cases are intrinsically >= D2)
- **Fingerprints:** all 14 unique=true · reproduce=true · frozen_pre_model=true

## Pre-result hypothesis map (§35) — transitions the pool can reveal

| Case | Gold | Most plausible competing | Direction probed |
|---|---|---|---|
| P7A-BND-001 | overclaim | correlation_vs_causation | overclaim -> over-specific (correlation) attractor |
| P7A-BND-002 | overclaim | correlation_vs_causation | overclaim -> over-specific (correlation) attractor |
| P7A-BND-003 | overclaim | correlation_vs_causation | overclaim -> over-specific (correlation) attractor |
| P7A-BND-004 | correlation_vs_causation | overclaim | counter-direction: specific gold that also looks like generic overclaim |
| P7A-BND-005 | correlation_vs_causation | overclaim | counter-direction: specific gold that also looks like generic overclaim |
| P7A-BND-006 | overclaim | mechanism_vs_evidence | overclaim -> over-specific (mechanism) attractor; Shape-B routing positive control |
| P7A-BND-007 | overclaim | mechanism_vs_evidence | overclaim -> over-specific (mechanism) attractor |
| P7A-BND-008 | overclaim | mechanism_vs_evidence | overclaim -> over-specific (mechanism) attractor |
| P7A-BND-009 | mechanism_vs_evidence | overclaim | counter-direction: specific gold that also looks like generic overclaim |
| P7A-BND-010 | mechanism_vs_evidence | overclaim | counter-direction: specific gold that also looks like generic overclaim |
| P7A-BND-011 | solid | overclaim | counter-direction: faithful solid that looks like overclaim (dramatic effect size) |
| P7A-BND-012 | solid | overclaim | counter-direction: faithful caveated solid that looks like overclaim |
| P7A-BND-013 | overclaim | solid | solid <-> overclaim: partially-true claim over-generalized beyond its evidence |
| P7A-BND-014 | overclaim | solid | solid <-> overclaim: narrow-true effect generalized beyond its evidence |

The 6 gold-`overclaim` B1+B2 cases (001,002,003,006,007,008) test the Phase-6 `overclaim → over-specific`
attractor; the 4 specific-gold cases (004,005 correlation; 009,010 mechanism) are the counter-direction
arm, and B3 (011-014) tests the solid↔overclaim boundary in both directions. The pool can therefore
show `overclaim→specific`, `specific→overclaim`, `solid→overclaim`, and `overclaim→solid` — it can
weaken or falsify the hypothesis, not only confirm it.
