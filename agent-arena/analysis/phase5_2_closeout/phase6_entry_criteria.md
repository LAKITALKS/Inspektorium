# Phase 6 — Entry Criteria

**Phase 6 may begin only from the final Phase 5 closeout tag (`v0.8.13-phase5-closeout`).**

## Phase 6 scope
Calibration; confidence reliability; expected calibration error (or documented alternatives);
reliability diagrams; selective prediction / abstention; risk-coverage analysis; threshold policy —
using **non-holdout development and validation data only**.

## Phase 6 prohibitions
Do **not**: inspect the private holdout mapping; inspect private holdout gold; inspect sealed holdout
packet contents; evaluate the holdout; use holdout results for calibration; tune prompts or
thresholds against holdout cases; alter the taxonomy silently; rewrite historical Phase 5 results.

## Required before Phase 6 implementation
1. fresh session · 2. verify the Phase 5 closeout commit and tag · 3. clean tracked working tree ·
4. a written Phase 6 plan before any code change · 5. inventory of existing calibration code and
tests · 6. explicit identification of the non-holdout development pool · 7. pre-specified calibration
metrics and acceptance criteria · 8. no live model call unless separately authorized · 9. no holdout
access.
