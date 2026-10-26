# Human Review Queue (Phase 5A)

Cases flagged for a human curator decision. **No automatic label flips, removals, or quarantines were performed.**

| case | gold | detected x3 | consistency | score(mean/range) | conf(mean) | case_type |
|---|---|---|---|---|---|---|
| study-forensics-042 | overclaim | solid/solid/solid | 1.0 | 38.5/2.5 | 0.88 | borderline |
| study-forensics-054 | overclaim | mechanism_vs_evidence/mechanism_vs_evidence/mechanism_vs_evidence | 1.0 | 40.0/0.0 | 0.92 | borderline |

## Notes per case
- **case042** — stable_alternative (overclaim→solid). Decision options: keep as boundary discriminator; or replace later if it remains a stable miss. Do not flip automatically.
- **case054** — stable_alternative (overclaim→mechanism_vs_evidence). Productive decorative-hedge boundary; keep as documented borderline unless a panel probe says otherwise.

No other cases require review: 48/50 are stable-correct.
