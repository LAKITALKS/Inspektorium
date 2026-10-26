# Human Curator Review Dossier — `mechanism_vs_evidence` ↔ `overclaim`

*WP-7C. The single shared difficult boundary surfaced by the two-model failure topology. This dossier
is **evidence for a human decision** — it does **not** change gold, does not declare the model right or
wrong on the taxonomy, and is **not** resolved by any model. Derived from the frozen raw records and
cases only; **no model calls**. Confidences are the mean over 5 replications; every unit below is
unanimous (5/5) unless a support count says otherwise.*

## The frozen boundary (from `docs/study_forensics_taxonomy.md` + `docs/taxonomy_precedence.md`)

- **`mechanism_vs_evidence` (specific):** a **described biological mechanism** (animal / preclinical
  pathway) is used to imply **human clinical benefit that has not been demonstrated**. Trigger:
  animal-or-preclinical mechanism → human therapeutic claim.
- **`overclaim` (generic / residual):** rhetorical inflation — framing exceeds evidence. The taxonomy
  **explicitly routes the surrogate-endpoint-framed-as-clinical-outcome case ("Shape B") to
  `overclaim`, and excludes it from `mechanism_vs_evidence`.**
- **Precedence:** the specific label outranks generic `overclaim` **only if its documented trigger is
  genuinely present and captures the core error**; it is "never stretched to match a model's preferred
  reading." Silently widening the category to match model output is benchmark overfitting.

The dossier set is every unit where **either** model's modal disagrees with gold across this boundary,
plus the full B2 family. **27 units** = **12 independent bases** + **15 derived perturbation variants**
(nested in 3 clusters — never counted as independent cases). They fall into three clean groups.

| group | n | pattern | who errs |
|---|--:|---|---|
| **G1 shared collapse** | 9 | gold `mechanism_vs_evidence`, modal `overclaim` | **both** models |
| **G2 Sonnet over-extension** | 9 | gold `overclaim`, modal `mechanism_vs_evidence` | **Sonnet only** (Haiku correct) |
| **G3 Haiku collapse** | 8 | gold `mechanism_vs_evidence`, modal `overclaim` | **Haiku only** (Sonnet correct) |
| both correct (B2 ref) | 1 | gold `overclaim` (BND-015) | neither |

---

## G1 — SHARED COLLAPSE (gold `mechanism_vs_evidence` → both say `overclaim`)

*Independent bases. Both models agree with each other and disagree with gold, at high confidence.*

| case | fam | claim (mechanism → implied human benefit) | evidence tier | Haiku | Sonnet |
|---|---|---|---|---|---|
| **P7A-ADV-003** | A2 | metformin "activates AMPK … slows your aging, adds years" | **mouse** lifespan (Martin-Montalvo 2013); TAME not yet reported | overclaim 5/5 (0.93) | overclaim 5/5 (0.95) |
| **P7A-ADV-004** | A2 | spermidine "switches on autophagy … renews cells, live longer" | **mouse** cardioprotection/lifespan (Eisenberg 2016); human = observational | overclaim 5/5 (0.94) | overclaim 5/5 (0.95) |
| **P7A-ADV-013** | A7 | red light "absorbed by cytochrome c oxidase … reverses aging" | in-vitro/**animal** photobiomodulation; human evidence narrow | overclaim 5/5 (0.92) | overclaim 5/5 (0.95) |
| **P7A-BND-009** | B2 | senolytics clear "zombie cells … reverse aging, add healthy years" | **mouse** (Xu 2018); human = Phase 1/2 biomarker pilots | overclaim 5/5 (0.92) | overclaim **4/5** (0.94) |
| **P7A-BND-010** | B2 | fasting "regrows insulin-producing cells … cures diabetes" | **mouse** + donor **cell cultures** (Cheng 2017); "warrants FDA trial" | overclaim 5/5 (0.96) | overclaim 5/5 (0.95) |

Also in G1 (derived variants, nested): `PRT-06-P1/P2/P4` (cluster root BND-009), `PRT-04-P3` (root
NEU-004) — same collapse.

**Boundary at issue:** all five bases carry a **textbook `mechanism_vs_evidence` signature** — an
explicitly *described* preclinical/animal mechanism (AMPK, autophagy, cytochrome-c-oxidase, senescent-
cell clearance, Ngn3 β-cell regeneration) offered as the basis for an unproven human therapeutic claim.
Both models detect the inflation but assign the **generic** `overclaim` rather than the **specific**
mechanism label.

**Curator question (G1):** For each case, is the described-mechanism trigger genuinely present and the
*core* error (→ gold `mechanism_vs_evidence` stands), or does rhetorical inflation so dominate that
`overclaim` is the primary and `mechanism_vs_evidence` only a secondary reading? On the frozen
definition these look like defensible `mechanism_vs_evidence` golds and a genuine **model limitation**,
not a gold error — please confirm.

---

## G2 — SONNET OVER-EXTENSION (gold `overclaim` → Sonnet says `mechanism_vs_evidence`; Haiku correct)

*This is the sharpest curator question: these are the taxonomy's **"Shape B" surrogate-endpoint cases**,
which the frozen taxonomy **deliberately routes to `overclaim`.** Sonnet reads the biological rationale
as a "mechanism" and picks the specific label; Haiku correctly stays `overclaim`.*

| case | fam | claim | why gold = `overclaim` (frozen) | Haiku | Sonnet |
|---|---|---|---|---|---|
| **P7A-ADV-009** | A5 | aducanumab "clears amyloid plaques … treats Alzheimer's" | **surrogate** (plaque imaging); phase-3 futility, withdrawn | overclaim 5/5 (0.97) | **mech 5/5 (0.96)** |
| **P7A-ADV-010** | A5 | antibacterial soap "kills 99.9% of germs … healthier home" | lab germ-kill **surrogate**; FDA: no better than plain soap (gold competing = `solid`, **not** mech) | overclaim 5/5 (0.98) | **mech 5/5 (0.95)** |
| **P7A-BND-016** | B2 | ginkgo "boosts cerebral blood flow … protects against dementia" | **surrogate** (blood flow); GEM RCT: no dementia reduction | overclaim 5/5 (0.95) | **mech 5/5 (0.95)** |
| **P7A-BND-018** | B2 | calcium+D "build blocks of bone … prevent fractures" | **surrogate** (BMD); JAMA meta-analysis: no fracture reduction | overclaim 5/5 (0.94) | **mech 5/5 (0.93)** |

Also in G2 (derived variants, nested): `PRT-08-P1…P5` (cluster root ADV-010) — Sonnet says
`mechanism_vs_evidence` on all five rewrites; Haiku `overclaim` on all five.

**Boundary at issue:** the frozen taxonomy separates a **described causal mechanism**
(`mechanism_vs_evidence`) from a **surrogate endpoint framed as a clinical outcome** (`overclaim`,
Shape B). Sonnet appears to treat "there is a plausible biological story" as sufficient for the specific
label, extending it into surrogate territory the taxonomy excludes — notably ADV-010, whose gold
competing label is `solid` (no mechanism reading intended at all).

**Curator question (G2):** Is the surrogate-vs-mechanism distinction operationally clear for these
cases, so gold `overclaim` is correct and Sonnet is **over-applying** the specific label (governance:
"do not stretch a specific label to match model output")? Or is any case genuinely dual — a described
mechanism *and* a surrogate gap — warranting a `borderline` mark? Default per frozen governance: gold
stands; **please confirm none should be relabeled or marked borderline.**

---

## G3 — HAIKU COLLAPSE (gold `mechanism_vs_evidence` → Haiku says `overclaim`; Sonnet correct)

| case | fam | claim | Haiku | Sonnet |
|---|---|---|---|---|
| **P7A-ADV-017** | A7 | nattokinase "breaks down fibrin … prevents heart attacks/strokes" | overclaim 5/5 (0.92) | **mech 5/5 (0.94)** ✓ |
| **P7A-NEU-004** | neutral anchor | cryotherapy "triggers anti-inflammatory response … speeds recovery" | overclaim 5/5 (0.92) | **mech 5/5 (0.93)** ✓ |

Also in G3 (derived variants, nested): `PRT-04-P1/P2/P4/P5` (root NEU-004), `PRT-06-P3/P5` (root
BND-009) — Sonnet recovers the mechanism label where Haiku collapses.

**Boundary at issue / curator question (G3):** Sonnet's correct answers corroborate that the gold
`mechanism_vs_evidence` is reachable on the frozen definition; Haiku's uniform collapse is a
**model-capacity limitation**, not evidence against the gold. Confirm gold stands.

---

## Central unresolved question for the curator

> **Is the frozen seam between a *described biological/preclinical mechanism → unproven human benefit*
> (`mechanism_vs_evidence`) and a *surrogate endpoint framed as a clinical outcome* (`overclaim`,
> Shape B) operationally clear and correctly applied to all 12 dossier bases — such that every gold
> stands and the failures are model limitations — or are any specific cases genuinely ambiguous / dual
> and better marked `borderline` (excluded from standard accuracy, retained for divergence)?**

Supporting facts for the decision (all frozen, no interpretation added):

- Both models are near-deterministic (5/5) and **highly confident** (≈0.92–0.98) on their errors — the
  boundary is not a sampling-noise artifact.
- The two models fail the seam in **opposite** directions (Haiku → generic `overclaim`; Sonnet →
  specific `mechanism_vs_evidence`), which is the signature of a genuinely **hard boundary**, consistent
  with the taxonomy's own prior "developing / not reliably produced" rating for `mechanism_vs_evidence`.
- The gold labels are **internally consistent with the frozen taxonomy** as written (G1/G3 = described
  mechanism; G2 = surrogate → Shape B → `overclaim`). No gold change is proposed here.

**Governance boundary (per WP §11 / §3):** no gold is changed, no case retired, no taxonomy edited, no
model declared correct/incorrect on the taxonomy. The human curator decides after reading this dossier;
if a Level-3 taxonomy clarification is warranted, it is a **separate, post-Phase-7** curation action and
must not retroactively alter the frozen Haiku/Sonnet result sets.
