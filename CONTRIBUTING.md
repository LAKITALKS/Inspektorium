# Contributing

Inspektorium is intentionally small. Contributions should preserve the frozen
v0.1 boundary in [SCOPE.md](SCOPE.md) and the separation between generative
proposals and deterministic validation.

All contributions must be original or drawn from dependencies with compatible,
documented licenses. Do not submit private datasets, private evaluation cases,
credentials, proprietary prompts, copied implementation material, or external
repository history.

Before proposing a change:

1. Confirm that it is in the v0.1 scope.
2. Add or update tests for observable behavior.
3. Keep tests deterministic and independent of live APIs.
4. Preserve strict schemas and visible failure behavior.
5. Avoid scores, aggregate labels, automatic quotation repair, and hidden
   inference rules.

Provider integrations, release licensing, and publication remain curator
decisions.

