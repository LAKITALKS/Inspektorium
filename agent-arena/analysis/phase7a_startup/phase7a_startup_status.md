# Phase 7A — Startup Status & Attestation (design-freeze)

Consolidated status for the Phase-7A robustness **design freeze**, after the curator design-freeze
hardening patch. Detailed content lives in the sibling documents; this file is the reviewable
attestation for the pre-result design-freeze commit.

**Status: DESIGN FROZEN — READY FOR BOUNDARY-POOL AUTHORING (WP-1).**

## Startup package (frozen)
| doc | contents |
|---|---|
| `phase7a_reconstruction.md` | repo-state verification · Phase-6 findings · frozen taxonomy/precedence + doc↔code audit · infrastructure inventory (with exact model ids) · data-class & 7B separation · security attestation |
| `phase7a_robustness_design.md` | experimental architecture · 7A.1–7A.5 subtracks with BLOCK-rule pointers · robustness-failure vocabulary · **frozen 2-model condition** · replication freeze N=5 |
| `phase7a_case_and_perturbation_contract.md` | frozen pool · pseudoreplication controls · **boundary directional counts** · adversarial forensic triggers · **4 neutral anchors** · **deterministic 10-cluster selection** · gold-freeze · exclusion/retirement · **class-B isolation** |
| `phase7a_metrics_and_acceptance.md` | metric families · **three-disposition acceptance matrix (systematic failure CAN block)** · run-failure policy · **expected volume 840** · reproducibility |
| `phase7a_execution_plan.md` | frozen decisions · execution order · pilot policy · budget/stop discipline · work packages |
| `phase7a_startup_status.md` | this file |

## Repository state
- branch `feat/case-library-run-harness`; HEAD `aa71c4a2…debe05`; parent `596f5301…29c18a`.
- Phase-6 tag `v0.9.0-phase6-closeout` → `ec57472…`; ancestor of HEAD ✅. Phase 6 GO is **final,
  unconditional** (unchanged by this phase).
- All seven Phase-7B commits verified as the exact `ec57472..HEAD` chain.
- Working tree before commit: **no tracked modifications**; only the untracked
  `analysis/phase7a_startup/` docs + pre-existing untracked files (untouched).
- Baseline suite: **1414 tests collected** (imports clean; **not executed** — docs-only session).

## Corrected acceptance semantics (root patch)
- **Removed** any claim that "analytical errors can never block Phase 7A."
- **Frozen:** an *isolated* analytical error = **INVESTIGATE / LIMITATION**; a **reproducible,
  systematic analytical robustness failure = BLOCK**. Three dispositions: PASS · INVESTIGATE/
  LIMITATION · BLOCK/FAIL. Robustness testing must be **capable of failing for lack of robustness**.
- **Both model conditions are PRIMARY**; every BLOCK rule applies **independently to each** (Haiku
  or Sonnet alone can block). Cross-model recurrence = **stronger corroboration, not a prerequisite**.
  Pre-frozen BLOCK rules (metrics §2): Boundary (≥2 same-direction independent cases in a primary
  condition, ≥3/5 modal each, after ruling out case/gold/evidence/taxonomy-doc issues); Adversarial
  (2/2 family majority failures in a primary condition); Perturbation (same family flips ≥2 clusters,
  or one cluster flips under ≥2 families, in a primary condition); Replication (≥2 same-family
  fragile-or-worse, or a no-majority case reproducing in-family, in a primary condition).
- **INVARIANCE ≠ CORRECTNESS** (stable-but-wrong ≠ success). Systematic error **may reveal** a
  taxonomy problem but does **not by itself prove** one → Level-3 curator escalation, not a 7A fix.

## Frozen design headline
- **Taxonomy frozen** (4 labels; `mechanism_vs_evidence` biologically scoped). Precedence is a
  governance/gold-freeze rule, **not executable code**; **no doc↔code contradiction**.
- **Overclaim → over-specific = HYPOTHESIS**, tested bidirectionally with a 4×4 transition matrix
  (searches for counterevidence). Not assumed; not a taxonomy defect.
- **Model conditions (frozen, exact, from committed Phase-6.2 contracts):** Agent-Arena package
  only — **two PRIMARY conditions** `claude-haiku-4-5-20251001` + `claude-sonnet-4-5-20250929`
  (Haiku's "ceiling" status is historical/descriptive only). **Opus `claude-opus-4-5-20251101`
  excluded** from primary. Not a cross-provider benchmark. Results reported **separately per
  condition**, never pooled.
- **Replication N = 5** (frozen; not changed after variance).
- **Pool:** 34 independent bases (14 Boundary + 16 Adversarial + 4 neutral anchors) + 50 clustered
  variants = 84 evaluated units. **Boundary gold:** overclaim 8 · correlation 2 · mechanism 2 ·
  solid 2 (intentional, pre-frozen). Reported bases-vs-variants-vs-units separately.
- **Perturbation clusters (10):** 4 neutral anchors + 6 via deterministic fingerprint-ordered
  stratified selection (contract §6).
- **Expected volume:** 84 × 5 × 2 = **840 planned model calls** (not a sample size; retries ≠
  replications).
- **Brier primary; ECE secondary/diagnostic; no universal robustness score.**
- **Gold frozen before output;** no result-driven relabel/retire/selection; error-driven selection
  prohibited; DEV-0011/0013/0018/0024 diagnostic references only.
- **Harness reused** (`run_library` replication + `calibration` Brier/ECE + `runtime_contract`
  fingerprints); only thin additive reporting to build.

## Data-class / class-B isolation / Phase-7B separation
- Class A (library) / Class B (7A robustness) / Class C (7B fixtures) kept **distinct**.
- **Class-B location:** separate `tasks/study_forensics_robustness/`; a **separate robustness
  discovery/manifest path** is built later — the normal library glob is **not** widened; normal
  library discovery and counts remain unchanged. **Robustness cases ≠ case-library counts.**
- **Class-C 7B fixtures contribute 0** to every Phase-7A count/statistic; the 7B release gate is a
  separate pipeline-control namespace. **No LaVita/client material** becomes a class-B case.

## Post-render PDF/HTML QA
- Classified **BELONGS LATER (report-engineering)**; not a 7A blocker; not implemented.

## Security / holdout attestation
- Holdout touched: **NO** · Holdout gold touched: **NO** · Private mappings touched: **NO** ·
  Salts/envelopes touched: **NO** · Client material touched: **NO** · External model calls: **0**.
- Only tracked docs/code and committed Phase-6 manifests were read (incl. the Phase-6.2 runtime
  contracts for the exact model ids). No broad traversal of private/untracked directories.

## Git (this design-freeze session)
- Startup docs under `analysis/phase7a_startup/` are committed as the **pre-result design-freeze
  checkpoint** (one commit `docs: freeze phase 7A robustness design`). **No case files, no source
  code** in the commit. **No amend, no tag, no push.**

## Recommendation
```
PHASE 7A ROBUSTNESS DESIGN FROZEN — READY FOR BOUNDARY-POOL AUTHORING
```
Next package: **WP-1 — Boundary pool authoring + gold freeze** (not started; awaiting curator
authorization).
