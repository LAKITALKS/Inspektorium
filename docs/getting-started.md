# Getting started

This page installs Inspektorium 0.3.0 and runs both subcommands once on the bundled synthetic examples.
Every run on this page is offline. No provider key is needed.

- `inspektorium inspect` is the reference checker for one answer and its supplied sources.
- `inspektorium audit` is the audit workflow: validate, run, inspect, review and release.

[How it works](concepts/how-it-works.md) explains the model behind both commands.

## Requirements

- Python 3.11 or newer.
- A fresh virtual environment.
- Network access to install the package and its dependencies and to fetch the examples.

```sh
python3 -m venv .venv
. .venv/bin/activate
```

## Install

Install the release wheel:

```sh
python -m pip install "https://github.com/LAKITALKS/Inspektorium/releases/download/v0.3.0/inspektorium-0.3.0-py3-none-any.whl"
```

Or install the tagged source:

```sh
python -m pip install "git+https://github.com/LAKITALKS/Inspektorium@v0.3.0"
```

Both install one distribution, `inspektorium`, with one command, `inspektorium`.
The runtime dependencies are Click, Pydantic 2 and PyYAML, as declared in `pyproject.toml`.

### Optional provider extra

The extra `providers` adds the provider SDKs used by the live paths.
`anthropic` is an alias with the same content.
The offline runs on this page do not need it.

```sh
python -m pip install "inspektorium[providers] @ https://github.com/LAKITALKS/Inspektorium/releases/download/v0.3.0/inspektorium-0.3.0-py3-none-any.whl"
```

### Check the installation

```sh
inspektorium --help
```

```text
usage: inspektorium [-h] {audit,inspect} ...

Inspektorium: audit instrument and evidence reference tool.

positional arguments:
  {audit,inspect}
    audit          run the full audit workflow (use audit --help for its
                   commands)
    inspect        reference checker: validate proposals for one answer and
                   render a report

options:
  -h, --help       show this help message and exit
```

The command has no `--version` option. Read the version from Python:

```sh
python -c "import inspektorium; print(inspektorium.__version__)"
```

```text
0.3.0
```

## Get the examples

The examples are repository files, not part of the wheel.
Clone the tag and run the remaining commands from the repository root:

```sh
git clone --branch v0.3.0 --depth 1 https://github.com/LAKITALKS/Inspektorium.git
cd Inspektorium
```

Without Git, download the files used on this page into the same layout:

```sh
BASE=https://raw.githubusercontent.com/LAKITALKS/Inspektorium/v0.3.0
for f in inspect/05_mixed_and_fabricated_quote/input.json \
         inspect/05_mixed_and_fabricated_quote/proposals.json \
         audit/positive-task.json audit/positive-recording.json \
         audit/unknown-task.json audit/unknown-recording.json; do
  mkdir -p "examples/$(dirname "$f")"
  curl -fsSL -o "examples/$f" "$BASE/examples/$f"
done
```

[`examples/inspect/`](../examples/inspect/) holds the reference-checker examples.
[`examples/audit/`](../examples/audit/) holds the audit tasks and recordings.

## First `inspect` run

[Example 05](../examples/inspect/05_mixed_and_fabricated_quote/input.json) has one answer, one source and three proposed findings.
One proposed quotation says `8 p.m.`; the source says `6 p.m.`

```sh
inspektorium inspect \
  --input examples/inspect/05_mixed_and_fabricated_quote/input.json \
  --proposals examples/inspect/05_mixed_and_fabricated_quote/proposals.json \
  --format markdown
```

Shortened output:

```text
# Inspection Report

## Summary

- Claims inspected: 3
- Relationships allowed to remain reportable: 2
- Citations with an exact text and offset match: 1
- Deterministic validation failures: 1
- Global score: not produced
…
### Finding 2: `claim-2`

**Atomic claim:** It closes at 8 p\.m. on weekdays.

- **Answer span:** `[42:74)`
- **Claim span check:** exact
- **Proposed relationship (evaluator judgment):** `supported`
- **Reportable proposed relationship:** None — deterministic guard failed
- **Deterministic guard:** `failed`
- **Citation text and offset check:** no exact match
…
## Validation Warnings

- **`claim-2` / `evidence_span_mismatch`:** The proposed quote does not equal the canonical source span at the proposed offsets.
…
```

The failed finding keeps its proposal, but its `reportable_relation` is null.
The two other findings stay reportable. The command exits 0 because the report was produced.

For machine-readable output, use `--format json` and optionally `--output report.json`.
The output is byte-identical to the committed [expected report](../examples/inspect/05_mixed_and_fabricated_quote/expected_report.json).
The [reference-checker guide](guides/reference-checker.md) covers inputs, options and errors.

## First `audit` run

An audit run takes a task file and, offline, a recorded response.
It writes an immutable bundle directory, called a candidate. Release is a separate, explicit step.

### 1. Validate the task

```sh
inspektorium audit validate --task examples/audit/positive-task.json
```

```text
{"input_valid": true, "errors": [], "release_authorized": false}
```

Exit code 0 means the input is eligible. It does not authorize a release.

### 2. Run offline with the recording

```sh
inspektorium audit run --offline \
  --task examples/audit/positive-task.json \
  --recording examples/audit/positive-recording.json \
  --output-root reports/local-audit
```

```text
{
  "status": "READY_FOR_RELEASE",
  "path": "/…/reports/local-audit/<revision-id>",
  "errors": []
}
```

The path is absolute and ends in a new random revision ID. Copy it:

```sh
CANDIDATE='path returned by run'
```

### 3. Inspect the candidate

```sh
inspektorium audit inspect --bundle "$CANDIDATE"
```

```text
{
  "valid": true,
  "status": "READY_FOR_RELEASE",
  "errors": []
}
```

`valid` says whether the bundle is intact under the installed code. `status` is the recorded outcome. Read both.
The human-readable result is in `report.md` and `report.html` inside the bundle.

### 4. Release explicitly

```sh
inspektorium audit release --bundle "$CANDIDATE" \
  --output-root reports/local-audit \
  --reviewer 'Local offline operator' \
  --reason 'Explicit release of this synthetic test artifact'
```

```text
{
  "status": "RELEASED",
  "path": "/…/reports/local-audit/<new-revision-id>",
  "errors": []
}
```

Release writes a second revision. The candidate directory stays byte-for-byte unchanged.
Inspecting the new path returns `"valid": true` and `"status": "RELEASED"`.

### What a blocked case does

The `unknown` example leaves a required proposition in the state `unknown`:

```sh
inspektorium audit run --offline \
  --task examples/audit/unknown-task.json \
  --recording examples/audit/unknown-recording.json \
  --output-root reports/local-audit
```

```text
{
  "status": "REVIEW_REQUIRED",
  "path": "/…/reports/local-audit/<revision-id>",
  "errors": [
    "phase9_history_review: Review open: mandatory review not executed: no automatic review was authorized or run in this execution"
  ]
}
```

The command exits 2. It still writes a complete, inspectable bundle.
`audit inspect` on that bundle returns `"valid": true` with `"status": "REVIEW_REQUIRED"` and exits 0.
A release attempt is refused and exits 2:

```sh
UNKNOWN_CANDIDATE='path returned by the unknown run'
inspektorium audit release --bundle "$UNKNOWN_CANDIDATE" \
  --output-root reports/local-audit \
  --reviewer 'Local offline operator' \
  --reason 'Attempt to release an unresolved case'
```

```text
{
  "status": "RELEASE_BLOCKED",
  "path": null,
  "errors": [
    "Candidate is REVIEW_REQUIRED; a current READY_FOR_RELEASE candidate is required."
  ]
}
```

Only a recorded human decision with `audit review` creates a new revision that can become releasable.
The [audit workflow guide](guides/audit-workflow.md#4-record-a-human-review) shows that step.

## Next steps

- [How it works](concepts/how-it-works.md): proposals, checks, bundles, review and release.
- [Reference-checker guide](guides/reference-checker.md) and [audit workflow guide](guides/audit-workflow.md).
- [CLI reference](reference/cli.md), [report schema](reference/report-schema.md) and [Python API](reference/python-api.md).
- [Limitations](evaluation/limitations.md): what these results do and do not establish.
