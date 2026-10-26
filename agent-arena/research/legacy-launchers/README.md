# Historical research launchers

These thirteen `run_*.py` scripts are historical launchers from the earlier
research phases of the Inspektorium audit runtime. They are kept unchanged as
a record of how earlier research runs were started. They are **not** part of
the supported workflow and are **not** authorized by any Inspektorium release.

- Twelve of them call model providers through `agent_arena.providers` and
  expect provider credentials in the environment. Running them can start
  paid live model calls. `run_study_forensics_pilot.py` uses built-in
  synthetic responses instead.
- They were written to run from the `agent-arena/` folder with
  `PYTHONPATH=src` and write to relative paths such as `runs/` and `reports/`.
  Their usage notes still name the old location; the file contents were not
  edited when they were moved here.
- They predate the current execution authorization, budget and release
  controls. Do not use them as offline examples or as a substitute for
  `inspektorium audit`.

The supported offline workflow is `inspektorium audit`; see the
[root README](../../../README.md). The moves are listed in the
[research folder index](../README.md).
