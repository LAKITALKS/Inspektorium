# Phase 7A Robustness Pool — Class B (Boundary cases)

**Data class B — Phase-7A analytical-robustness evaluation cases. NOT the Case Library (class A).**

This directory holds the frozen Phase-7A **Boundary** robustness bases. After the post-audit repair
and the **final curator-resolution** re-freeze it contains **14 ACTIVE** cases + **4 RETIRED**
historical cases (`P7A-BND-001` … `P7A-BND-018`; retired: 003, 006, 007, 008 — kept for provenance,
excluded from active metrics via `status: retired` + `excluded_from_active_metrics: true`, linked to
replacements 017/018/015/016 via `supersedes`/`superseded_by`). Only the active set counts toward the
frozen 14 / 5-5-4 / 8-2-2-2 distributions. Every active case carries **real public-claim provenance**
(a real `claim_source_url` + bounded exact claim + declared source roles). It is **structurally
isolated** from the normal Case Library:

- `agent_arena.run_library.discover_cases` globs `tasks/study_forensics/*.yaml`
  (non-recursive) and filters on `task_type == study_forensics`. This sibling directory
  (`tasks/study_forensics_robustness/`) is **not** on that glob, so these cases do **not**
  change the active Case-Library count (verified: 48 active / 50 incl. retired, unchanged).
- These cases are **never** run in this work package. WP-1 contains **0 model calls**.
- A separate, explicit robustness discovery / run path is built in a later work package —
  the class-A discovery glob is **not** broadened.

See `analysis/phase7a_startup/phase7a_case_and_perturbation_contract.md` (§10) and
`analysis/phase7a_boundary/` for the candidate log, source-intake log, and curator review.

**Gold labels** use only the four frozen analytical labels (`solid`, `overclaim`,
`correlation_vs_causation`, `mechanism_vs_evidence`); `boundary_family` is metadata, never a
gold label. Every gold label here was frozen **before any model output existed**
(`gold_status: frozen_pre_model`).

## Adversarial pool (7A.3) — `P7A-ADV-*.yaml`

This directory also holds the frozen Phase-7A **Adversarial** robustness bases (7A.3): **16 ACTIVE**
cases + **1 RETIRED** historical case (`P7A-ADV-001` … `P7A-ADV-017`; retired: `P7A-ADV-014`, gold-review
blocker, superseded by `P7A-ADV-017`) = **8 frozen adversarial families (A1–A8) × 2 independent active
cases**. They share the class-B directory, the canonical SHA-256 fingerprint, and the
provenance/source-role vocabulary with the Boundary pool, but keep a **distinct ID namespace**
(`P7A-ADV-*` vs `P7A-BND-*`) and distinct verify helper
(`agent_arena.robustness_pool.verify_adversarial_pool`). They are **never** discovered by the class-A
glob (`tasks/study_forensics/*.yaml`) and contribute **0** to Case-Library / Development / Holdout /
Phase-7B counts. WP-2 contains **0 model calls**. Only the active set counts toward metrics; the retired
case is kept for provenance (`status: retired` + `excluded_from_active_metrics: true`).

- Families (frozen, `analysis/phase7a_startup/phase7a_case_and_perturbation_contract.md` §4): A1
  decorative citation · A2 citation-supports-mechanism-not-outcome · A3 causal-verb-on-observational
  · A4 subgroup→general · A5 surrogate→clinical (Shape B) · A6 unsupported superiority/comparator ·
  A7 mechanism→implied-efficacy · A8 technically-true-but-misleading.
- **Emergent** frozen gold distribution (not a cosmetic balance): `overclaim` 10 ·
  `mechanism_vs_evidence` 4 · `correlation_vs_causation` 2 · `solid` 0. Difficulty: D2 8 · D3 8.
- Each active case carries **real public-claim provenance**, separate evidence `source_role`s, an
  explicit `robustness.adversarial_mechanism` (what pressure the model must resist), a
  `steelman_challenge`, and a `case_fingerprint` frozen before any model output.
- Manifest: `adversarial_manifest.yaml`. Review surfaces: `analysis/phase7a_adversarial/`.

## Perturbation / metamorphic pool (7A.2) — `P7A-NEU-*.yaml` + `perturbation_variants.yaml`

This directory also holds the frozen Phase-7A **Perturbation** (metamorphic robustness) track (7A.2):
**4 neutral anchors** (`P7A-NEU-001…004`, one per frozen gold label — `solid`, `overclaim`,
`correlation_vs_causation`, `mechanism_vs_evidence`) plus **50 meaning-preserving variants**
(`perturbation_variants.yaml`, ids `P7A-PRT-<slot>-<family>`). The variants are **10 independent base
clusters × 5 frozen families (P1–P5) × 1 variant**. WP-3 contains **0 model calls**.

- **10 cluster roots (contract §6):** the 4 neutral anchors + 6 bases selected **deterministically,
  pre-result** from the frozen Boundary/Adversarial pools by ascending `case_fingerprint` (B1, B2, B3
  one each; 3 adversarial from distinct families A5/A1/A6). Reproduce with
  `python3 -m agent_arena.robustness_pool` (`select_perturbation_bases`).
- **Five frozen families (design §3 / contract §7):** P1 claim paraphrase · P2 hedging variation
  (neutral) · P3 order (claim/evidence) · P4 distractor context · P5 formatting — all invariance
  tests (gold must NOT change). No sixth family; citation-surface variation is deferred.
- **50 variants ≠ 50 independent cases.** Each variant inherits its base gold, nests under
  `base_case_id`, stores the verbatim base prompt (`original_claim`) + a controlled meaning-preserving
  transformation (`perturbed_claim`) — **not** an independently published public claim — and binds to
  its base via `base_case_fingerprint`. `variant_fingerprint` = sha256 over the canonical variant
  record (minus the stored fingerprint). Every variant is certified `meaning_preservation: PASS` and
  `gold == base gold`.
- Neutral anchors are **independent** (fingerprint-disjoint from every Boundary/Adversarial case) and
  carry full real public-claim provenance. They contribute **0** to Case-Library / Phase-7B counts and
  are **not** on the class-A glob.
- Manifests: `perturbation_manifest.yaml` (master: selection + families + 50-variant aggregate +
  clustering guard) and `perturbation_variants.yaml` (the 50 records). Review surfaces + candidate /
  authoring logs: `analysis/phase7a_perturbation/`.

**Do not** add model responses, run records, Brier/accuracy, or any result-derived field to
this directory.
