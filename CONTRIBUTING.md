# Contributing

Inspektorium is one instrument. Its official public workflow is
`inspektorium audit`, which runs the Inspektorium audit runtime (internal/former
name Agent Arena, retained in package, module and folder names for provenance:
the `agent-arena` distribution, `agent_arena` imports and the `agent-arena/` folder).
The root version is 0.2.0 and the audit runtime version is 1.0.2. The public
entry delegates to the existing runtime without changing its semantics; runtime
1.0.2 changes only license, metadata and the version string in
`agent_arena/__init__.py`. See [ONE_INSTRUMENT.md](docs/ONE_INSTRUMENT.md).

The smaller `inspektorium inspect` reference checker keeps its v0.1.1/schema 0.1
contract: evaluators propose semantic relationships, while deterministic code
validates exact claim and citation spans. The audit workflow does not invoke
that pipeline automatically. Keep the two enforcement boundaries clear in code,
schemas, reports, tests and prose.

[AGENTS.md](AGENTS.md) lists binding working rules for automated agents and
agent-assisted changes. Its rules on evidence, check status and untrusted text
apply to every contribution; this guide and AGENTS.md are meant to agree, and
neither replaces tests or review.

## Run the checks

```bash
python -m pip install -e '.[dev]' -e './agent-arena[dev,providers]'
ruff check .
mypy src
pytest --cov=inspektorium --cov-report=term-missing --cov-fail-under=80
```

These are the root-package checks, including public-entry regressions. The
retained audit runtime has its own full suite and frozen acceptance command
below. CI runs the suites on Python 3.11 and 3.12. Deterministic-kernel
changes must include tests for successful and failed paths; protective
controls need a deliberate violation that must be caught and a clean
counterpart that must still pass. Tests and examples must remain reproducible
without a provider API key.

## Propose a change

Keep pull requests focused, explain the observable behavior, and include tests.
Confirm first that the proposal fits [SCOPE.md](SCOPE.md). Features outside the
frozen reference-checker v0.1 boundary or existing audit semantics require
separate design review under
[ROADMAP.md](ROADMAP.md) and [RESEARCH_PLAN.md](RESEARCH_PLAN.md). A planned
phase or documentation change does not authorize its implementation, paid
execution or publication. Keep existing versions, schemas and release tags
unchanged for narrative-only changes.

## Claim and evidence discipline

Every meaningful new or revised capability/result claim must update
[CLAIMS.md](CLAIMS.md), retaining a stable claim ID and these fields:

- claim;
- status: implemented, experimentally tested, roadmap or hypothesis;
- implementation evidence;
- experimental/verification evidence;
- known limitation;
- scope/version;
- verification/access status.

Link the applicable public implementation and existing tests. Regression
success is not scientific efficacy. For material still excluded from the publication use
“owner-reported; code/raw package not public here”; do not invent links or
describe an internal result as independently reproduced by public v0.1.
Separate current checks from historical CI and dated historical test counts.
Preserve null results, counterexamples, denominators and failed/missing attempts.

Describe the exact rule, protected field/action and enforcement boundary.
Do not turn a reportable evaluator proposal into a semantically verified
relation, or CLI success into release authorization. Any reliability statement
must name its fixed operating conditions; robustness must name the tested
disturbances. Scientific forensics and review are audit-runtime research capabilities
(R08, R09), not capabilities of the smaller reference checker. The public
`inspektorium audit` entry exposes those existing capabilities; it does not
transfer reference-checker safeguards into the audit pipeline. Display escaping
of untrusted text is not semantic checking (P12). No global or weighted assurance
score, compliance claim or generic safety claim is justified by these software
checks.

An eventual internal evidence release requires a separately reviewed package,
version mapping and preserved originals/hashes. Negative results and old
evidence must not be rewritten to make the presentation cleaner. Preserve old
names, command strings and version fields in historical evidence.
Use Inspektorium as the public instrument name and call the runtime the
Inspektorium audit runtime in prose. Explain `agent-arena` as the retained
distribution/compatibility identity, never as a second product, brand or
release title.

From version 0.2.0, Inspektorium is licensed under the
[Apache License 2.0](LICENSE); see [NOTICE](NOTICE). Unless stated otherwise,
contributions are submitted under the same license (section 5 of the license).
Earlier releases remain under PolyForm Noncommercial 1.0.0, as published.

Contributions must be original or use compatible, documented dependencies. Do
not submit private datasets, proprietary prompts, credentials, copied project
history, or implementation material from unrelated systems.

## Joint installation, runtime checks and publication records

The canonical operational installation is one command from the repository root,
inside a fresh Python 3.11+ virtual environment:

```sh
python -m pip install . ./agent-arena
inspektorium audit --help
```

The editable command above is for development. The retained audit runtime's full
suite must run from `agent-arena/` in that development environment:

```sh
cd agent-arena
python -m pytest tests
python scripts/phase10_acceptance.py --output /new/path/gates
```

The output directory must be new. Tests and acceptance use synthetic or saved
offline inputs; installing provider SDK extras supports adapter tests and does
not authorize provider calls. The runtime's historical release lint boundary is
recorded in `agent-arena/PUBLICATION.md`; known legacy lint findings remain
disclosed. Root Ruff excludes that tree, and root test discovery remains
`tests/`. Do not claim a full-runtime lint or strict type-check pass based on the
root checks.

Public-entry verification is implemented in
[tests/test_audit_entry.py](tests/test_audit_entry.py) and
[scripts/verify_instrument.py](scripts/verify_instrument.py). Record actual
commands, source/version identities and results in a new dated record under
`publication/`. Until a check executes, its status is not executed or pending;
historical suite counts are not new results. Preserve runtime bytes and old
artifact metadata; a runtime version change needs its own changelog entry and
a review of the tests that bind module bytes. Package versions
and source commits identify different layers; neither proves a software release
has been published.

The original publication authorization and import mapping remain unchanged in
`publication/2026-10-26/`. The mapping describes publication commit
`94eb4fc8b26c22da6a2cebdd01e5a7799750104d`; current documentation can legitimately
have new hashes. The later name/entry clarification is recorded in
[AGENTS.md](AGENTS.md), without rewriting the earlier decision.
