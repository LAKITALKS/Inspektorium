# Phase 5 — Known Limitations and Maintenance

Each item is classified and marked for whether it blocks Phase 6. **When Phase 6 uses only the
non-holdout pool, no listed item blocks Phase 6.**

| # | item | class | blocks Phase 6? |
|---|------|-------|-----------------|
| 1 | Model revalidation is **not** human IAA | future validation requirement | no |
| 2 | Case library is finite; domain coverage not universal | non-blocking limitation | no |
| 3 | 16-case holdout has limited statistical precision (6.25 pp) | non-blocking limitation | no |
| 4 | Holdout is prospective, not historically untouched | governance constraint | no |
| 5 | In two strata, source membership may be inferable to maintainers | governance constraint | no |
| 6 | No holdout evaluation has yet occurred | future validation requirement | no |
| 7 | No direct comparison vs best-in-class optimized prompt-only workflows yet establishes an accuracy/error-reduction advantage | future validation requirement | no |
| 8 | Stale packet-local annotation-field-list inconsistency (found in Phase 5.05h) | maintenance item | no |
| 9 | Private holdout packet generation removed packet-local response schemas; one authoritative external response sheet is used | maintenance item (resolved for holdout) | no |
| 10 | Future general packet/bundle generators should enforce one authoritative response schema | maintenance item | no |
| 11 | Any future taxonomy change requires explicit versioning + comparability impact assessment | governance constraint | no |
| 12 | Any selected holdout-case defect requires the frozen retirement-and-deterministic-replacement procedure | governance constraint | no |

**No unresolved Phase 5 blocker materially blocks calibration/reliability work on the non-holdout
development pool.** These limitations are documented honestly and are **not** represented as resolved
scientific validation.
