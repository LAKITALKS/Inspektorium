# Phase 6 — Risk Register

Risks that could distort calibration, leak the holdout, overfit, misrepresent
confidence/abstention, or produce unsupported claims. Each risk has a likelihood
(L), impact (I), and a mitigation with an owning subphase. Highest-priority first.

| id | risk | L | I | mitigation | owner |
|----|------|---|---|------------|-------|
| **R-1** | **Holdout leakage via the dev pool.** The sealed holdout ⊂ the 21 eligible cases; using any eligible case for calibration silently includes holdout cases. | med | **critical** | Define the dev pool as `{active} \ {eligible-21}` (holdout-safe by construction); freeze it in a Level-2 prep checkpoint; packet-integrity refuses sealed paths. | 6.1 |
| **R-2** | **Confidence semantics corruption.** Missing/non-numeric confidence silently becomes `0.0`, indistinguishable from real low confidence → biases every reliability curve. | **high** | high | 6.1 spec mandates non-silent handling: flag/exclude unusable confidence; never treat coerced 0.0 as a datum. Add a guard + test. | 6.1/6.2 |
| **R-3** | **Result-driven selection (overfitting to dev set).** Choosing metrics, thresholds, bins, or pool membership after seeing the numbers. | high | high | Pre-specify all criteria in 6.0/6.1 before results; separate prep vs result checkpoints; no re-tuning against observed numbers. | 6.1/6.2 |
| **R-4** | **Calibration overfits a tiny dev set.** The holdout-safe dev pool is small and label-imbalanced (esp. correlation/mechanism), so calibration parameters may not generalize. | high | med | Prefer low-parameter methods; report uncertainty; treat calibration as provisional; document per-label thinness; no broad claim. | 6.2 |
| **R-5** | **Abstention assumed beneficial.** Adopting an abstain rule without measuring the coverage cost. | med | high | Risk–coverage evaluation reporting both error reduction and coverage lost; adopt only against a pre-specified benefit criterion. | 6.2 |
| **R-6** | **Comparison pilot overreach.** A small prompt-only pilot is read as proof of superiority. | med | high | Pre-register protocol; report as underpowered with CIs + explicit no-universal-superiority disclaimer; keep isolated from tuning. | 6.4 |
| **R-7** | **Public/product claim from limited evidence.** Any external claim of accuracy/superiority before adequate, holdout-validated evidence. | low | **critical** | Public claims are Level 3, curator-approved, out of Phase 6 scope; 16-case holdout framed as integrity test only. | all |
| **R-8** | **Accidental holdout evaluation / private-path access.** Tooling or scripts reach `internal_only/` or the private holdout. | low | **critical** | Tools refuse sealed paths (tested); no live eval without separate authorization; startup verifies isolation. | all |
| **R-9** | **Concurrent research-expansion contamination.** Unfinished `research/…expansion_150/` candidates treated as canonical, or altered/staged. | med | high | Treat folder as out of scope; never stage; exclude from all Phase 6 calculations; stage only explicit Phase 6 paths. | all |
| **R-10** | **Reproducibility gap.** A calibration result not bound to its input pool + code commit + params → cannot be reproduced or audited. | med | med | Result manifest for every Level-2 numeric output; deterministic seeds/config. | 6.2+ |
| **R-11** | **Doc-vs-gold inconsistency (case 031).** Taxonomy borderline table lists 031 as mechanism_vs_evidence while retired YAML gold is solid. | low | low | Non-blocking (031 retired, excluded from metrics). Reconciliation is Level 3; log only, do not fix in Phase 6. | maintenance |
| **R-12** | **Confidence-label conflation.** Heuristic finding-confidence (`HIGH/MEDIUM/HEURISTIC`) mistaken for calibrated model confidence. | med | med | 6.1 spec keeps the two namespaces distinct; reports label their source. | 6.1/6.3 |
| **R-13** | **Ad-hoc root scripts drift.** Many untracked `run_*.py` at repo root are non-reproducible entry points. | med | low | Prefer versioned CLI/library entry points for Phase 6; do not depend on untracked scripts for checkpointed results. | 6.x |
| **R-14** | **Scope creep past 6.0.** Beginning 6.1+ before 6.0 is closed/approved. | med | med | Strict linear gating; 6.0 closeout requires curator approval before 6.1. | governance |

**Review cadence:** re-read this register at the start of each subphase; add any new
risk surfaced during that subphase before producing results.
