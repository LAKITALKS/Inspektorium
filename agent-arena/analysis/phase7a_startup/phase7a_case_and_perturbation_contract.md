# Phase 7A — Case, Gold, Perturbation & Adversarial Contract (pre-registration)

Frozen construction rules for the Phase-7A robustness pool (data **class B**). **No case is
created in this startup session.** These are the contracts the curator has approved for the
pre-result design freeze; every case's gold is frozen *before* any model output is seen.

---

## 1. Case-pool plan (FROZEN counts)

| track | independent base cases | variants | notes |
|---|---:|---:|---|
| 7A.1 Boundary | **14** | — | B1 (5) + B2 (5) + B3 (4); directional counts frozen in §3 |
| 7A.3 Adversarial | **16** | — | 8 families (A1–A8) × 2 independent cases each |
| 7A.2 Perturbation | **4 new** | **50** | 10 designated base clusters × 5 families (P1–P5) × 1 variant; 4 new **neutral anchors** (§5) + 6 deterministically selected from the frozen pool (§6) |
| **Totals** | **34 independent bases** | **50 clustered variants** | **84 evaluated units** |

**Frozen composition:** **34 independent bases = 14 Boundary + 16 Adversarial + 4 neutral
Perturbation Anchors.** These counts are fixed pre-result and are **not** rebalanced based on model
output.

---

## 2. Independence / pseudoreplication controls (frozen, §21/§34)

- Every evaluated unit carries: `base_case_id`, and (for variants) `perturbation_cluster_id` =
  `base_case_id` + `family`. Boundary/adversarial bases carry `boundary_family_id` /
  `adversarial_family_id`.
- **Reporting always distinguishes `N_independent_bases` (34) from `N_derived_variants` (50) from
  `N_total_model-evaluated_units` (84).** The headline scientific count is **34 independent bases**,
  never 84. **84 evaluated units ≠ 84 independent scientific cases.** Perturbation results are
  reported **cluster-aware**, never as 50 independent cases.

---

## 3. Boundary contract & FROZEN directional counts (7A.1)

The 5 + 5 + 4 design is frozen, with directions now explicit:

| family | boundary | cases | gold distribution (frozen) |
|---|---|---:|---|
| **B1** | `overclaim ↔ correlation_vs_causation` | 5 | **3 gold `overclaim`** + **2 gold `correlation_vs_causation`** |
| **B2** | `overclaim ↔ mechanism_vs_evidence` | 5 | **3 gold `overclaim`** + **2 gold `mechanism_vs_evidence`** |
| **B3** | `solid ↔ overclaim` | 4 | **2 gold `solid`** + **2 gold `overclaim`** |

**Total Boundary gold distribution (frozen):** `overclaim` **8** · `correlation_vs_causation` **2** ·
`mechanism_vs_evidence` **2** · `solid` **2**.

This asymmetry is **intentional and pre-frozen** because the Phase-6 diagnostic hypothesis concerns
**overclaim → over-specific** errors; the counter-directions (specific-that-looks-overclaim,
solid-that-looks-overclaim) remain represented so the 4×4 transition matrix can show the pattern
**and** its reverse. **Do not later rebalance based on model output.**

- **Inclusion rule:** > 1 failure mode initially plausible; precedence / evidence-tier / wording
  genuinely matters; the frozen primary is **defensible** under `docs/taxonomy_precedence.md`.
- **Exclusion rule:** primary not defensible under precedence; gold intentionally ambiguous; pure
  trick construction; the case only "works" if a specific label is stretched beyond its trigger.

---

## 4. Adversarial contract (7A.3)

- **8 families A1–A8** (robustness_design §4) × **2 independent cases** = **16 cases**.
- **Before authoring, each family must have a pre-declared intended forensic trigger and expected
  gold-label logic** (below). Gold-label counts are **not** forced equal for cosmetic balance, but
  the **final frozen gold distribution is documented before any model run.**

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

- **Anti-trick safeguard (§19):** difficulty is *surface pressure only*; every case has a frozen,
  **defensible** gold + precedence rationale + alternate reading. Cases are **never** relabeled to
  make a family pass.

---

## 5. Four neutral perturbation anchors (frozen, §16 of patch)

Four dedicated perturbation base cases provide **controlled surface tests outside** the deliberately
hard boundary/adversarial cases — **one neutral anchor per frozen label:**

| anchor | gold | requirements |
|---|---|---|
| NA-solid | `solid` | clear gold · low ambiguity · strong precedence rationale · **no adversarial trick structure** |
| NA-overclaim | `overclaim` | as above |
| NA-corr | `correlation_vs_causation` | as above |
| NA-mech | `mechanism_vs_evidence` | as above |

These are **independent base cases** (counted in the 34) and are **automatically included** as
perturbation base clusters.

---

## 6. Ten perturbation base clusters — deterministic pre-result selection (frozen, §17 of patch)

**10 base clusters × 5 families (P1–P5) × 1 variant = 50 variants.** The 10 clusters are chosen by a
**pre-result, deterministic, model-performance-free** rule:

1. **4 neutral anchors** (§5) are included automatically.
2. **6 additional bases** are selected from the frozen **eligible pool = 14 Boundary + 16
   Adversarial = 30 bases** using stratified, fingerprint-ordered selection with these **frozen
   strata quotas**:

   | stratum | eligible members | quota |
   |---|---|---:|
   | B1 (`overclaim↔correlation`) | 5 boundary bases | **1** |
   | B2 (`overclaim↔mechanism`) | 5 boundary bases | **1** |
   | B3 (`solid↔overclaim`) | 4 boundary bases | **1** |
   | Adversarial | 16 bases (A1–A8) | **3**, each from a **distinct** family |

3. **Selection within a stratum:** sort the stratum's eligible cases by **ascending
   `case_fingerprint`** (sha256 hex, lexicographic) and take the first. For the Adversarial stratum
   (quota 3, distinct families): iterate the fingerprint-sorted list and pick a case only if its
   `adversarial_family_id` is not already chosen, until 3 distinct-family cases are selected.

**Guarantees:** both priority boundaries (B1, B2) represented; B3 represented; adversarial
represented across 3 distinct families; all 4 labels covered via the neutral anchors; selection is
**fully deterministic from frozen fingerprints** and uses **no model output** — no post-authoring
cherry-picking. The rule is executed once, at authoring time, and its output cluster list is frozen
into the case/variant manifest.

---

## 7. Perturbation contract (7A.2)

- **Permitted families:** P1 paraphrase · P2 hedging variation (neutral) · P3 order (claim/evidence)
  · P4 distractor context · P5 formatting. **All five are invariance tests** (gold must not change).
- **Citation-surface variation: deferred** (feasible only for citation-carrying cases; revisit after
  bases are frozen — documented, not silent).
- **Variants per base:** 1 per family (5 per base cluster); 10 clusters → 50 variants, each with
  `perturbation_cluster_id`.
- **Equivalence-validation method:** deterministic / human-curated construction + curator review
  against the fixed equivalence checklist (proposition, population, comparator, endpoint, evidence
  tier, direction/strength unchanged). **No LLM-assumed equivalence.**
- **Invalid-perturbation rejection rule (§16):** any candidate that changes causality, population,
  comparator, endpoint, evidence tier, superiority, temporal, or mechanism-to-clinical implication
  is **rejected** (it would be a *new case*, requiring its own gold freeze).
- **Reporting:** per-family and overall **invariance rate** (modal label vs base behavior),
  **perturbation label-switch rate**, cluster-aware — and **correctness-vs-gold reported
  separately** (**INVARIANCE ≠ CORRECTNESS**; a stable-but-wrong case is not a success).

---

## 8. Gold-freeze contract (frozen, §13 & §36)

**No case enters a robustness run without a complete, curator-frozen record.** Frozen fields reuse
the existing Class-A case schema (template: `case040`), extended with the Phase-7A tags. Required,
frozen **before** any model output:

1. `prompt` — the **exact claim** (isolated, single claim under evaluation).
2. `context` / evidence basis — the **evidence** and its tier.
3. `gold_label` — the frozen primary (one of the four).
4. `gold_justification` — **rationale**.
5. `gold_alternative_reading` — the documented strongest alternate (**precedence rationale**).
6. `gold_confidence`, `gold_case_type` (`clear` / `borderline`).
7. Ambiguity notes.
8. Provenance — `origin` ∈ {`synthetic`, `curated`, `curated_showcase`} (**never**
   `real_world_intake` / client-derived for class B), `source_dataset` / `source_id` where relevant.
9. `case_fingerprint` — sha256 over the frozen case content (reuse `runtime_contract._sha256_hex`);
   this fingerprint is what the §6 deterministic selection orders on.
10. Phase-7A tags — `case_family`, `boundary_family_id` / `adversarial_family_id` /
    `perturbation_cluster_id` as applicable, `difficulty_tier` (D1/D2/D3).

**Intake gate:** every case must also pass `docs/case_intake_policy.md`. Demo-derived material is
**not** used for class B.

**Discipline:** gold frozen **before** model output; **no result-driven relabeling / retirement /
selection**; a second reviewer is *review*, **not** human IAA (model agreement is never relabeled as
inter-annotator agreement). **Error-driven case selection is prohibited (§14):** DEV-0011 / DEV-0013
/ DEV-0018 / DEV-0024 are diagnostic references that may inform *family design*, never selective
inclusion; class-B cases are newly authored/synthesized.

---

## 9. Exclusion / retirement policy (frozen, §24)

Reuses `docs/case_intake_policy.md` (retire, never delete). Distinct from model outcomes.

- **VALID exclusion (objective, outcome-independent):** malformed artifact; corrupt evidence
  reference; impossible-to-resolve source; duplicate discovered **independently** of any model
  outcome; implementation failure affecting **all** conditions; intake-checklist failure on
  retrospective audit.
- **INVALID exclusion (never permitted):** the model failed it; confidence "looked strange"; it
  lowered headline accuracy; it raises an uncomfortable taxonomy question; it is "too hard".
- **Mechanism:** `status: retired` + `excluded_from_active_metrics: true` + provenance `origin` +
  `suite_history` (date, trigger, rationale, `label_flip: false`); rewrites get a **new** `case_id`
  via `supersedes`/`superseded_by`. **Nothing is silently deleted.**

---

## 10. Class-B location & isolation (frozen, §18 of patch)

- Class-B cases live in a **structurally separate** location: **`tasks/study_forensics_robustness/`**
  (or the closest repository-consistent equivalent if that exact path later conflicts).
- **CRITICAL:** do **NOT** broaden the normal Case-Library discovery glob so that Phase-7A robustness
  cases become normal Case-Library cases. A **separate explicit robustness discovery / manifest path**
  is implemented later, in the relevant WP — **not** by widening `run_library.discover_cases`'s
  default `tasks/study_forensics/*.yaml` glob. Normal library discovery and counts remain
  **unchanged** in design.
- **Frozen:** **PHASE-7A ROBUSTNESS CASES ≠ CASE-LIBRARY COUNTS.**
- Class-C Phase-7B QA fixtures (R1–R8) and the release gate contribute **0** to any Phase-7A count.
  **No LaVita / client-derived case** is authored for class B.
