# Phase 5.1 — Holdout Freeze Policy

- The holdout is **frozen prospectively** from this checkpoint. It is **not** historically untouched:
  several selected cases participated in earlier Phase 5 curation/model revalidation and are
  protected only from this freeze onward.

## Development access (Phase 6–10)
Development must **not** inspect: the private HLD→source mapping, the private per-HLD gold, the
selected packet contents, or any holdout result. Development may use **only** the non-holdout pool.

Holdout cases may **not** be used for: prompt engineering; taxonomy revision; scoring-rule tuning;
calibration fitting; threshold tuning; or outcome-based report-template optimization.

## Evaluation discipline
- **No holdout evaluation** may occur until its evaluation protocol is committed.
- Predictions must be **frozen before gold access**.
- One model/configuration run must **not** be silently replaced.
- Discovered errors require a **versioned retirement-and-replacement** protocol; no selected case
  may be silently edited; **no result-driven case exclusion** is permitted.

## Reporting discipline
- Holdout performance must be reported **with sample-size limitations**.
- A 16-case holdout has a raw accuracy resolution of **6.25 percentage points**.
- **In the correlation_vs_causation and mechanism_vs_evidence strata, all four eligible cases are
  selected, so source membership may be inferable to maintainers** who know the approved pool; the
  HLD ordering, HLD→source and HLD→gold mappings, and evaluator packets nonetheless remain sealed.
- Passing the holdout will **not** establish universal superiority over all LLMs or prompting
  strategies.
