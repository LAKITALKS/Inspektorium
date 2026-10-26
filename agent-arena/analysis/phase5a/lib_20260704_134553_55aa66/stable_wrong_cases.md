# Stable-Wrong Cases (Phase 5A)

Cases where all 3 runs agreed on the SAME label that is not the gold primary label.

| case | gold | detected x3 | consistency | score(mean/range) | conf(mean) | case_type |
|---|---|---|---|---|---|---|
| study-forensics-042 | overclaim | solid/solid/solid | 1.0 | 38.5/2.5 | 0.88 | borderline |
| study-forensics-054 | overclaim | mechanism_vs_evidence/mechanism_vs_evidence/mechanism_vs_evidence | 1.0 | 40.0/0.0 | 0.92 | borderline |

Both are documented `borderline` cases landing on their documented alternative reading (see stable_alternative_cases.md). Not defects; flagged for review, not auto-changed.
