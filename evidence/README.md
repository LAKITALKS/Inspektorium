# Evidence packages

Each folder is a versioned, frozen evidence package. Its files stay unchanged after publication; later checks are added as new, dated addenda.

| Package | Version measured | What it holds |
| --- | --- | --- |
| [`v0.1.1/`](v0.1.1/README.md) | Reference checker 0.1.1, report schema 0.1 | Offline before/after measurement of the display and input-parsing fixes on a frozen synthetic catalog |
| [`v0.1.1/addendum-20261024/`](v0.1.1/addendum-20261024/README.md) | Same product | Display and setup follow-up (E1, E2, E3) |
| [`v0.1.1/addendum-20261024-e1-layout/`](v0.1.1/addendum-20261024-e1-layout/README.md) | Same product | Layout follow-up for E1, with product file hashes |
| [`v0.3.0-behavior/`](v0.3.0-behavior/README.md) | Releases 0.2.0 and 0.3.0 | Behavior comparison of `inspect` and `audit` across the 0.3.0 consolidation |
| [`judge-replay-2026-10-27/`](judge-replay-2026-10-27/README.md) | Release 0.3.0 | Preregistered replay of three LLM judges' quotations through `inspect`, with controls and a sensitivity analysis |

[Evidence](../docs/evaluation/evidence.md) explains what each package establishes and what it does not.
[Reproducibility](../docs/evaluation/reproducibility.md) explains how to recompute the results.

## Links inside frozen packages

The packages were written for the repository layout of their time.
One relative link no longer resolves and stays unchanged with its package:

| Package file | Link target | Where the content is now |
| --- | --- | --- |
| `v0.1.1/CLOSEOUT.md` | `../../RELEASE_CHECKLIST.md` | [Release process](../docs/development/release-process.md); the original is `historical-docs/RELEASE_CHECKLIST.md` in the [research record](https://github.com/LAKITALKS/inspektorium-research-record/tree/record-2026-10-27/historical-docs) |

The test files that the packages name, such as `tests/test_render_safety.py`, are now under `tests/unit/` and `tests/integration/`.
