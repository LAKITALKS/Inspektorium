# Contributing

INSPEKTORIUM's public v0.1 kernel is intentionally small: evaluators propose
semantic relationships, while deterministic code validates exact claim and
citation spans. Changes should keep that distinction obvious in code, schemas,
reports and prose.

[AGENTS.md](AGENTS.md) lists binding working rules for automated agents and
agent-assisted changes. Its rules on evidence, check status and untrusted text
apply to every contribution; this guide and AGENTS.md are meant to agree, and
neither replaces tests or review.

## Run the checks

```bash
python -m pip install -e '.[dev]'
ruff check .
mypy src
pytest --cov=inspektorium --cov-report=term-missing --cov-fail-under=80
```

These are the checks CI runs on Python 3.11 and 3.12. Deterministic-kernel
changes must include tests for successful and failed paths; protective
controls need a deliberate violation that must be caught and a clean
counterpart that must still pass. Tests and examples must remain reproducible
without a provider API key.

## Propose a change

Keep pull requests focused, explain the observable behavior, and include tests.
Confirm first that the proposal fits [SCOPE.md](SCOPE.md). Features outside the
frozen v0.1 boundary require separate design review under
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
disturbances. Scientific forensics and review are separate Arena research capabilities
(R08, R09), not capabilities of the core package. Display escaping of untrusted text is not semantic checking
(P12). No global or
weighted assurance score, compliance claim or generic safety claim is justified
by these software checks.

An eventual internal evidence release requires a separately reviewed package,
version mapping and preserved originals/hashes. Negative results and old
evidence must not be rewritten to make the presentation cleaner. If an old
name is unavoidable, explain it in a provenance note rather than creating a
competing public brand.

Contributions must be original or use compatible, documented dependencies. Do
not submit private datasets, proprietary prompts, credentials, copied project
history, or implementation material from unrelated systems.

## Arena component and publication checks

Arena is installed separately with `python -m pip install -e './agent-arena[dev,providers]'`.
Run its full suite from `agent-arena/` with `python -m pytest tests` and the
frozen gate `python scripts/phase10_acceptance.py --output /new/path/gates`.
Its release lint boundary is recorded in `agent-arena/PUBLICATION.md`; known
legacy lint findings are disclosed, not described as a clean full lint run.
Core Ruff excludes the separate Arena tree. Root test discovery remains `tests/`;
CI runs both complete suites in separate jobs on Python 3.11 and 3.12.
The dated GitHub authorization is in `publication/2026-10-26/AUTHORIZATION.md`.
