# Contributing

Inspektorium is intentionally small: evaluators propose semantic relationships,
while deterministic code validates exact claim and citation spans. Changes
should keep that distinction obvious in code, schemas, reports, and prose.

## Run the checks

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest --cov=inspektorium --cov-report=term-missing
```

Deterministic-kernel changes must include tests for successful and failed paths.
Tests and examples must remain reproducible without a provider API key.

## Propose a change

Keep pull requests focused, explain the observable behavior, and include tests.
Confirm first that the proposal fits [SCOPE.md](SCOPE.md). Features outside the
frozen v0.1 boundary should be discussed before implementation and parked in
[ROADMAP.md](ROADMAP.md) rather than smuggled into the kernel.

Contributions must be original or use compatible, documented dependencies. Do
not submit private datasets, proprietary prompts, credentials, copied project
history, or implementation material from unrelated systems.
