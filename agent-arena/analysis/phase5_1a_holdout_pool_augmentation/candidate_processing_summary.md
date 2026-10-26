# Phase 5.1a — Candidate Processing Summary (aggregate only)

No canonical source identities appear in this file.

| target label | initial candidates | processed (rank order) | suitability failures | approved |
|--------------|--------------------|------------------------|----------------------|----------|
| correlation_vs_causation | 3 | 1 | 0 | 1 |
| mechanism_vs_evidence | 4 | 2 | 0 | 2 |

- Deterministic ordering (holdout_pool_augment_v1, frozen seed) was followed; the first-ranked
  candidate for correlation_vs_causation and the first two for mechanism_vs_evidence passed packet
  suitability, so no lower-ranked candidate was needed.
- **No passing higher-ranked candidate was skipped.**
- **No manual swaps** occurred; no model-performance/correctness/confidence/difficulty field
  influenced ranking or selection.
- Suitability failures: **none** (0 by every reason).
