# Contributing

Thank you for helping. Inspektorium is a fail-closed integrity layer: a change must never let a check pass what it should block.

## Set up

Use Python 3.11 or newer and a fresh virtual environment:

```bash
git clone https://github.com/LAKITALKS/Inspektorium.git
cd Inspektorium
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev,providers]"
```

The `providers` extra installs the provider SDKs for adapter tests. No test calls a provider or needs an API key.

## Run the checks

```bash
ruff check .
ruff format --check .
mypy src/inspektorium/core src/inspektorium/report src/inspektorium/providers src/inspektorium/cli.py
python scripts/check_type_baseline.py
python -m pytest
python scripts/run_acceptance.py --output "$(mktemp -d)/acceptance"
```

The acceptance output directory must not exist yet; the script creates it.
[Testing](docs/development/testing.md) describes the test categories, the type-checking baseline of the audit runtime and the installation check.
CI runs the same commands; see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Conventions

- **Fail closed.** Every protective control needs a counter-test that violates it and a clean counterpart that must still pass.
- **Never weaken a test to make it pass.** Expectations on statuses, exit codes, rejections and bindings change only with a documented behavior change.
- **Untrusted text is data.** Answer, source and evaluator text must not create report structure or hide warnings in any output.
- **Report what ran.** Distinguish passed, failed, skipped and not executed. Numbers in documentation link to the check that produced them.
- **Claims.** A new or changed capability claim updates the [claim ledger](docs/research/claims.md) with its evidence and limits.
- **Scope.** Inspektorium checks evidence pointers; it does not judge meaning. Proposals that add scores or semantic verdicts need a design discussion first; see the [roadmap](docs/roadmap.md).
- **Style.** Ruff sets the code style. Documentation is English, with short sentences and each limit stated once in [limitations](docs/evaluation/limitations.md).
- **No secrets.** Never commit credentials, private data or absolute local paths.

## Propose a change

1. Open an issue first for anything larger than a small fix.
2. Keep pull requests focused and describe the observable behavior before and after.
3. Include tests and update `CHANGELOG.md` and the documentation where behavior changes.

Report security issues privately as described in [SECURITY.md](SECURITY.md).
By participating you agree to follow the [code of conduct](CODE_OF_CONDUCT.md).

## License

Contributions are licensed under the [Apache License 2.0](LICENSE), as stated in its section 5.
Contributions must be your own work or use compatible, documented dependencies.
