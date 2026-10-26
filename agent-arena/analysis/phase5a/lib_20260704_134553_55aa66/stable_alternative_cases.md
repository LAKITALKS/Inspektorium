# Stable-Alternative Cases (Phase 5A)

Stable-wrong cases that are marked `borderline` with a documented `gold_alternative_reading`, and land on that alternative.

| case | gold | detected x3 | consistency | score(mean/range) | conf(mean) | case_type |
|---|---|---|---|---|---|---|
| study-forensics-042 | overclaim | solid/solid/solid | 1.0 | 38.5/2.5 | 0.88 | borderline |
| study-forensics-054 | overclaim | mechanism_vs_evidence/mechanism_vs_evidence/mechanism_vs_evidence | 1.0 | 40.0/0.0 | 0.92 | borderline |

- **case042** (gold overclaim, detected solid): the surrounding text is a careful analytical paper; `solid` is the documented alternative. boundary_candidate + review_required.
- **case054** (gold overclaim, detected mechanism_vs_evidence): the in-vitro→clinical tier gap makes `mechanism_vs_evidence` the documented alternative. boundary_candidate + review_required.

Per instruction: labels NOT auto-flipped; cases NOT removed/quarantined.
