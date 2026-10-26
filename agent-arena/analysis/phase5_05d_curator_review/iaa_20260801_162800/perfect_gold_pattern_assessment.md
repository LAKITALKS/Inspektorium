# Phase 5.05d — Perfect-Gold Pattern Assessment

**Fact under review.** Three of the four raters reproduced **all 20** gold primary labels.
The fourth (Rater 3) diverged on exactly three cases (BIAA-003, 007, 016), each a *soft*
disagreement whose secondary label equals gold. (Model identities: see
`internal_rater_mapping.json`.)

This is neither proof of validity nor proof of leakage. Competing explanations, each with
evidence for/against and a distinguishing test:

### 1. Taxonomy and packets are genuinely clear
- **For:** 19/20 packets use a neutral, uniform template; the shortcut audit found no
  demonstrated leakage; nine cases are anchor/clear by design.
- **Against:** if it were *only* clarity, the independent-family rater would also reach
  20/20; instead it diverges on the borderline set.
- **Distinguishing test:** independent human expert labelling of the same 20; high
  human-gold agreement supports genuine clarity.

### 2. Sample is unusually easy / curated
- **For:** `sample_reason` shows deliberate inclusion of "anchor" cases; the sample is
  curated, not random.
- **Against:** the sample *also* deliberately includes hard/high-ambiguity cases
  (BIAA-007), which three raters still matched to gold; not uniformly easy.
- **Distinguishing test:** re-run on a fresh, non-curated, harder real-world sample and
  compare agreement.

### 3. Models and curator share general language-model priors
- **For:** all four raters are language models; three are different families yet converge —
  consistent with shared pretraining priors about "overclaim/causation" rhetoric.
- **Against:** shared priors would also tend to converge the fourth rater; its systematic
  primary↔secondary reordering suggests a real definitional degree of freedom remains.
- **Distinguishing test:** compare against a non-LM signal (human experts, or a rule-based
  classifier) on the same items.

### 4. Label definitions contain highly diagnostic cues
- **For:** the taxonomy's specific triggers (surrogate-as-outcome, uncontrolled
  before/after) are crisp and map cleanly onto most packets.
- **Against:** the same crispness did not resolve the mechanism-vs-overclaim and
  corr-vs-overclaim boundaries (the soft cases), so cues are diagnostic but not total.
- **Distinguishing test:** stress the boundary with paraphrase/robustness probes.

### 5. Packets contain unintended structural or lexical signals
- **For:** BIAA-013 embeds an instruction naming all four taxonomy terms and has a unique
  structure/length (see shortcut audit).
- **Against:** that signal names *all four* labels (non-unique); no real-case-id or
  verdict leakage anywhere; the independent rater still diverged on other cases.
- **Distinguishing test:** reword BIAA-013 to the neutral template and re-annotate; a
  strip-and-re-run robustness pass on all packets.

### 6. Model-assisted gold-curation co-evolution  ← **most material caution**
- **For:** the case fixtures carry curator provenance indicating model assistance — e.g.
  a gold `alternative_reading` that explicitly references a *live multi-run model probe*
  used to set the borderline call, and a "reworded fixture" note. If gold was tuned with
  model help, model–gold agreement is partly circular.
- **Against:** the divergent rater is a *different* family and still mostly agrees, and the
  agreement holds on clear cases that need no model tuning.
- **Distinguishing test:** compare gold against labels from annotators/experts **outside**
  the gold-curation loop; if agreement drops materially, co-evolution is implicated.

### 7. Exact agreement arose by chance
- **For:** none.
- **Against:** with four categories, 20/20 for three raters is astronomically unlikely by
  chance; models are not random.
- **Distinguishing test:** not needed — chance is excluded.

## Assessment
The 3-of-4 perfect-gold pattern is best explained by a **combination of (1) genuine
clarity on the clear/anchor cases and (4) diagnostic label definitions**, with a **real
and material caution from (6) model-assisted gold co-evolution and (3) shared LM priors**.
Explanations (5) and (7) are largely excluded (no demonstrated leakage; chance ruled out);
(2) is partly true by construction but insufficient alone.

**Bottom line for the curator:** the A/B/D perfect match must **not** be reported as
independent, human-grade validation of the gold labels. It is consistent with a clear
taxonomy *and* with partial circularity from model-assisted curation. An out-of-loop
human (or non-LM) check on the same 20 is the single most informative next test before any
validity claim or holdout freeze.
