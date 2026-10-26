# Study Forensics Taxonomy — v0.6.5 Consolidated

## Overview

This document defines the four gold-label categories used in the Study Forensics
evaluation domain of Agent Arena, based on empirical calibration across multiple
LLM validation sprints (v0.6.0 through v0.6.5).

---

## Categories

### 1. `solid`

**Definition:** The study summary accurately reports evidence with appropriate
scope and caveats. Claims match the strength of the evidence presented.

**Core signal:** Honest reporting. Evidence supports the claims made.

**Includes:**
- Well-designed studies with clear conclusions
- Studies with limitations that are honestly acknowledged
- Mixed results (e.g., biomarker success + clinical failure) reported without
  inflating the positive aspects
- Weak evidence honestly reported as weak

**Key discriminator:** The text does not overclaim, overcause, or overextend.
Limitations are real but the *reporting* is appropriate.

**Empirical strength:** Strong. All models perform well (100% Haiku/Sonnet on
clear cases).

---

### 2. `overclaim`

**Definition:** The conclusion exceeds the evidence. Claims are stronger than
what the data support.

**Core signal:** Rhetorical inflation. The text sells results as more than they are.

**Includes:**
- Conclusions that go beyond the data
- Surrogate endpoints framed as clinical outcomes (e.g., LDL reduction sold as
  "cardiovascular protection")
- Extrapolation to populations not studied
- Decorative uncertainty that does not constrain the claims
- Commercial framing of preliminary results as therapeutic breakthroughs

**Key discriminator:** The *framing* of the results is the problem, not the
results themselves.

**Empirical strength:** Strong on clear cases (80% all models). Borderline Case007
(vitamin D / long COVID) is unstable — all models classify as solid due to
honest caveating.

---

### 3. `correlation_vs_causation`

**Definition:** The text treats correlation as causation. Observational or
cross-sectional data are used to make or imply causal claims.

**Core signal:** Causal language or policy recommendations from non-causal designs.

**Includes:**
- Cross-sectional studies with causal language
- Observational data used for policy recommendations
- Missing confounders not addressed
- Ecological fallacy (group-level correlations applied to individuals)

**Key discriminator:** The study design cannot support causal claims, but the
text makes or implies them.

**Empirical strength:** Strong. 100% accuracy for all models on clear cases.
Note: only 2 cases in current pool — category is well-defined but thin.

---

### 4. `mechanism_vs_evidence`

**Definition:** A biological mechanism is described and used to imply human
clinical benefit, but the evidence for that benefit does not exist.

**Core signal:** Animal or preclinical mechanism presented as basis for human
therapeutic claims.

#### Empirically validated scope (Shapes that work)

**Shape A — Animal-to-human therapeutic leap:**
A study demonstrates a mechanism in mice/rodents/animals and suggests or implies
human therapeutic applications. The mechanism is convincing in the animal model
but has not been tested in humans.

*Examples: Case013 (gut microbes), Case024 (Klotho), Case028 (NAD+)*

**Shape C — Preclinical pathway to therapeutic promise:**
A molecular pathway is described with impressive preclinical results and framed
as a future therapy. Evidence is entirely preclinical.

*Examples: Case030 (APJ exercise mimetic)*

#### Shapes that do NOT belong in this category

**Shape B — Biomarker-to-clinical gap:**
Empirically, this shape splits into `solid` or `overclaim` depending on framing:
- If the biomarker-clinical gap is **honestly reported** → `solid` (Case029)
- If the biomarker success is **rhetorically sold as clinical benefit** → `overclaim` (Case032)

Models do not reliably produce `mechanism_vs_evidence` for this shape.

#### Borderline handling

**Shape D — Strong preclinical + cautious reporting:**
When strong preclinical evidence meets honest, cautious reporting with explicit
caveats, models may classify as `solid`. These cases should be marked as
`gold_case_type: borderline` with `gold_confidence: medium` and excluded from
standard accuracy metrics. They serve as divergence probes.

*Example: Case031 (rapamycin)*

**Key discriminator:** The gap between a *mechanistic demonstration* (in animals
or in vitro) and *clinical evidence* (in humans, for clinical outcomes) is the
central issue. If the central issue is instead *rhetorical inflation*, the case
is `overclaim`.

**Empirical strength:** Moderate. Sonnet achieves 80% on clear cases. Haiku and
Opus achieve 40%. The category is well-defined but harder for models than the
other three.

---

## Borderline Cases

Three cases are marked `gold_case_type: borderline`:

| Case | Gold label | Issue |
|------|-----------|-------|
| 007 (vitamin D) | overclaim | Honest caveating masks decorative optimism; all models say solid |
| 022 (four-day workweek) | solid | Self-selection bias could justify overclaim; all models say solid |
| 031 (rapamycin) | mechanism_vs_evidence | Cautious reporting of animal-human gap; Sonnet+Opus say solid |

**Policy:** Borderline cases are excluded from standard accuracy metrics.
They are retained for divergence analysis and calibration purposes only.

---

## Category Maturity Assessment

| Category | Cases (clear) | Empirical accuracy | Maturity |
|----------|:------------:|:-----------------:|----------|
| solid | 5 | 94% (avg across models) | Mature |
| overclaim | 4 | 80% (avg) | Mature |
| correlation_vs_causation | 2 | 100% | Mature but thin |
| mechanism_vs_evidence | 4 | 53% (avg) | Developing |

---

## Label precedence

When more than one category could apply to a case (e.g. a generic `overclaim`
reading vs a specific structural failure mode), the choice of a single primary
`gold_label` is governed by the **taxonomy precedence rule** in
[`taxonomy_precedence.md`](taxonomy_precedence.md). In short: a specific label
(`correlation_vs_causation`, `mechanism_vs_evidence`) outranks generic `overclaim`
**only when its definitional trigger is genuinely present**; it is never stretched
to match a model's preferred reading.

---

## Version History

- **v0.6.5** — Consolidated taxonomy. Case029 relabeled solid, Case032 relabeled
  overclaim. Shape B documented as not belonging in mechanism_vs_evidence.
- **v0.6.4** — Case029 relabeled from mechanism_vs_evidence to solid.
- **v0.6.3** — Analytical reference FP fix, label detection priority, criticism-direction heuristic.
- **v0.6.2** — Gold standard calibration fields added. Case007 marked borderline.
- **v0.6.1** — Negation-aware FP detection, flexible pattern families, hedge detection.
- **v0.6.0** — Initial study forensics implementation.
