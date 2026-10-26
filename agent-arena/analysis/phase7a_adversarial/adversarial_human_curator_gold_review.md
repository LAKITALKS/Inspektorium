# Phase 7A — Adversarial Pool Human-Curator Gold Review (WP-2, blocker-only)

Narrow, blocker-only gold review of the 16-case Phase-7A Adversarial Pool, closing WP-2 for Agent
Arena v1.0. **No evaluation model run (Haiku / Sonnet / Opus evaluation / prompt-only = 0);** public
source verification only. Reviewed at checkpoint `4b055bb`. The question answered for each case is
**"is this case scientifically unsafe to freeze as gold?"**, not "can it be made better".

**Outcome:** 1 gold blocker found and repaired by retire+replace (ADV-014 → ADV-017); 2 load-bearing
source bindings verified and bound (ADV-011, ADV-016); 1 clerical source-role clarification
(ADV-006). All 16 active cases now pass. Family counts (A1-A8 = 2), gold distribution (overclaim 10,
mechanism_vs_evidence 4, correlation_vs_causation 2, solid 0), and difficulty (D2 8 / D3 8) unchanged.

## Disposition legend
PASS · PASS+BIND (source binding upgraded) · PASS+CLERICAL (clerical correction) ·
REPLACED (retired + new-ID replacement for a gold blocker).

---

## 1. 16-case verdict table

| ID | Family | Gold | Claim provenance | Evidence adequacy | Family quality | Gold validity | Disposition |
|---|---|---|---|---|---|---|---|
| 001 | A1 | overclaim | Real (Airborne / FTC 2008) | Adequate (FTC evidence assessment) | A1 trigger real (non-probative study) | Defensible; solid tempting | PASS |
| 002 | A1 | overclaim | Real (POM / FTC 2013) | Adequate (Commission Opinion) | A1 trigger real (research-volume decoration) | Defensible | PASS |
| 003 | A2 | mechanism_vs_evidence | Real (metformin longevity claim / TAME) | Adequate (Martín-Montalvo 2013 mouse) | A2 trigger real (citation supports mechanism, not outcome) | Uniquely defensible (no human anti-aging trial) | PASS |
| 004 | A2 | mechanism_vs_evidence | Real (spermidine marketing / Nat Med) | Adequate (Eisenberg 2016 mouse; human observational only) | A2 trigger real | Uniquely defensible (human data observational, not outcome) | PASS |
| 005 | A3 | correlation_vs_causation | Real (breakfast diet message / BMJ) | Adequate (Sievert 2019 RCT meta-analysis) | A3 trigger real (causal from observational) | Defensible (RCTs refute) | PASS |
| 006 | A3 | correlation_vs_causation | Real (post-shooting discourse / APA) | Adequate (APA 2020 assessment) | A3 trigger real | Defensible | PASS+CLERICAL (APA role note) |
| 007 | A4 | overclaim | Real (gluten-free wellness message) | Adequate (GFD review; celiac ~1%) | A4 trigger real (subgroup→general) | Defensible; solid tempting | PASS |
| 008 | A4 | overclaim | Real ("Low T" DTC / FDA 2015) | Adequate (FDA restriction) | A4 trigger real | Defensible | PASS |
| 009 | A5 | overclaim | Real (Biogen Aduhelm / FDA) | Adequate (FDA accelerated approval; futility trials) | A5 Shape-B positive control | Defensible under frozen Shape-B→overclaim routing | PASS |
| 010 | A5 | overclaim | Real (antibacterial soap / FDA 2016) | Adequate (FDA final rule) | A5 trigger real (germ-kill surrogate→illness) | Defensible; solid tempting | PASS |
| 011 | A6 | overclaim | Real (Nexium marketing) | **Bound primary trial (Kahrilas 2000, 40 vs 20 mg, 93.7% vs 84.2%)** | A6 trigger real (rigged comparator) | Defensible (unequal-dose superiority) | **PASS+BIND** |
| 012 | A6 | overclaim | Real (Pfizer Listerine) | Adequate (federal court injunction 2005) | A6 trigger real (comparator over-generalized) | Defensible | PASS |
| 013 | A7 | mechanism_vs_evidence | Real (red-light device marketing) | Adequate (photobiomodulation animal mechanism) | A7 trigger real (mechanism→efficacy) | Defensible (broad human benefit unshown) | PASS |
| ~~014~~ | ~~A7~~ | ~~mechanism_vs_evidence~~ | Real (psychobiotic marketing) | — | **Human RCTs on the claimed outcome exist** | **Not uniquely defensible → overclaim equally defensible** | **REPLACED → 017 (retired)** |
| 015 | A8 | overclaim | Real (Lipitor 36% ad) | Adequate (ASCOT-LLA via FDA label) | A8 trigger real (relative vs absolute) | Defensible; misleadingness confirmed | PASS |
| 016 | A8 | overclaim | **Corrected to real claim ("More than 80% of dentists recommend Colgate")** | **Bound ASA 2007 upheld adjudication** | A8 trigger real (multiple-response survey) | Defensible | **PASS+CLERICAL/BIND** |
| 017 | A7 | mechanism_vs_evidence | Real (nattokinase "clot buster" marketing) | Adequate (Sumi 1987 in-vitro; RCT review — surrogates only, no outcome trial) | A7 trigger real (mechanism→undemonstrated outcome) | **Uniquely defensible** (claimed outcome has no human trial) | PASS (replacement) |

Active gold pool = 001-013, 015, 016, 017 (16). Retired = 014 (1).

---

## 2. ADV-011 (Nexium) — priority comparator check

**Primary comparator evidence verified? YES.** The pivotal head-to-head healing trial is **Kahrilas
PJ et al., Aliment Pharmacol Ther 2000** (PMID 11012468):

- **Doses compared:** esomeprazole (Nexium) **40 mg** vs omeprazole (Prilosec) **20 mg** — **unequal**.
- **Endpoint:** healing of erosive/reflux oesophagitis at 8 weeks (+ symptom resolution).
- **Result:** 8-week healing **93.7% vs 84.2%** (p<0.001, life-table, ITT).
- **Dose-equivalent?** No. The superiority is real but was demonstrated at unequal doses; at equal doses
  it narrows substantially and, for typical GERD symptom control, the drugs are broadly comparable.

The public "better purple pill / switch" superiority claim **overstates** the fair-comparison
difference, resting on the unequal-dose comparator — the frozen A6 forensic proposition is **confirmed**.
Primary trial now bound as `primary_research` (the earlier secondary clinical reference is retained as
equal-dose/typical-patient context). **Disposition: PASS (primary comparator evidence bound).**

---

## 3. ADV-014 (psychobiotic) — priority gold re-adjudication (the key scientific check)

Re-adjudicated from scratch (WP-2 §7):

1. **Exact public clinical-benefit claim:** a probiotic "heals your gut" via the gut-brain axis and
   thereby **cures anxiety and lifts depression, "no medication needed"** (a stand-alone cure claim).
2. **Mechanistic evidence invoked:** the gut-brain axis (vagus, HPA axis, SCFAs, serotonin/GABA).
3. **Human clinical evidence that exists:** **direct human RCTs and meta-analyses** — Nikolova et al.
   2019/2021, Goh et al. 2019, and later reviews — measuring the **claimed outcome** (depressive
   symptoms). They show probiotics reduce depressive symptoms **as an adjunct to antidepressants**
   (SMD ≈ 0.83) but **not stand-alone** (SMD ≈ −0.02).
4. **Does that establish the claimed efficacy?** No — the modest adjunctive effect does not support a
   stand-alone **cure**, and "no medication needed" directly **contradicts** the adjunct-only finding.
5. **Is the central failure "mechanism → implied efficacy"?** Not cleanly: unlike a pure animal/
   preclinical claim, **direct human outcome trials exist**, so the defect is better read as
   **exaggeration/over-generalization of real (weak) human outcome evidence**.
6. **Stronger primary diagnosis:** **generic overclaim** is at least equally defensible (arguably more),
   because human evidence on the claimed outcome exists and is inflated/over-generalized.
7. **Is `mechanism_vs_evidence` still uniquely defensible?** **No.** This is an equal-primary ambiguity
   (the retired-Boundary-007/008 failure mode; WP-2 §7).

**Final gold: not uniquely `mechanism_vs_evidence`; `overclaim` equally defensible.** Because the A7
family requires `mechanism_vs_evidence` gold, the case no longer instantiates A7. **Disposition:
REPLACED** — retired (not deleted), superseded by **ADV-017 (nattokinase)**, a clean A7 whose claimed
clinical **outcome** (MI/stroke prevention) has **no human outcome trial** (only in-vitro fibrinolysis
+ human *surrogate* studies), so `mechanism_vs_evidence` is uniquely defensible there. The gold count
was **not** preserved by relabeling any other case; the replacement independently satisfies A7.

---

## 4. ADV-016 (Colgate) — priority ASA verification

**Primary/authoritative ASA evidence verified? YES.**

- **Claim actually made:** "**More than 80% of dentists recommend Colgate**" (poster; plus "Colgate —
  used and recommended by most dentists"). The originally-frozen span ("more dentists recommend Colgate
  than any other brand …") was a paraphrase; **corrected** to the real wording.
- **Respondents could recommend multiple brands? YES** — the survey asked dentists to name the brands
  they recommend and allowed more than one; a competitor was recommended **almost as much** as Colgate.
- **Did the design affect the reader meaning? YES** — the **UK Advertising Standards Authority upheld
  complaints (January 2007)** and ruled the claim misleading, because readers would take "80% recommend
  Colgate" to mean **over and above other brands**, which the multiple-response survey does not show.

Authoritative ASA adjudication bound (`regulatory_assessment`, documented via the advertising-law
record). Gold `overclaim` unchanged. **Disposition: PASS (ASA adjudication bound; claim span corrected).**

---

## 5. ADV-015 (Lipitor) — secondary watch

**A8 misleadingness: CONFIRMED.** The advertisement **headlines the relative** figure ("reduces the
risk of heart attack by **36%**") while the **absolute** reduction — event rates **1.9% vs 3.0%**
(ASCOT-LLA, per the FDA label), an absolute reduction of **~1.1 percentage points** — is relegated to a
footnote. The prominent relative framing creates a **materially stronger reader meaning** (a large
benefit) than the small absolute reduction warrants, and the fine-print hedge does not repair it. This
is **more than "ARR would also be useful"**: the headline suppresses the materially important absolute
context and inflates the reader's sense of benefit magnitude — a clean fit for frozen A8.
**Disposition: PASS (not reopened).**

---

## 6. Source-type clerical check (§9)

The controlled evidence-role vocabulary defines `regulatory_assessment` as
"regulatory / government / **authoritative assessment** or enforcement"
(`robustness_pool.EVIDENCE_SOURCE_ROLES`). The **APA** (ADV-006) is an **authoritative scientific/
professional body, not a government regulator**; it fits the "authoritative assessment" sense of that
role. This is a **terminology** matter, not a schema defect — **no schema redesign**. A clarifying note
was added to the ADV-006 evidence item. The court (ADV-012) and ASA (ADV-016) adjudications are
advertising/consumer-protection **regulatory/authoritative** records and are correctly
`regulatory_assessment`. **Disposition: PASS+CLERICAL.**

---

## 7. Acceptance (§14)

- No unresolved wrong gold — the one gold blocker (ADV-014) was retired + replaced.
- No unresolved wrong family — A1-A8 each have 2 active cases that instantiate their trigger.
- No unresolved real-claim provenance failure — all 16 active carry a real, bounded public claim + URL.
- No load-bearing scientific claim resting solely on unverified secondary assertion — the two flagged
  cases (011, 016) now cite the primary trial / authoritative adjudication.
- No duplicate/dependent proposition — 16 distinct claim spans/URLs; the nattokinase replacement is an
  independent proposition (fibrinolysis → CV events), distinct from red light (013) and all others.
- All 16 remain **pre-model frozen**; all fingerprints reproduce; all tests pass.

**ADVERSARIAL GOLD POOL READY FOR HUMAN CURATOR FINAL APPROVAL.**
