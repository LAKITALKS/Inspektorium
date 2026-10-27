# Python API

This page lists the public Python entry points of Inspektorium 0.3.0.
Signatures are printed from the installed package with `inspect.signature`.
Models and fields are described in the [report schema](report-schema.md).

- [Package exports](#package-exports)
- [Reference checker](#reference-checker)
- [Parsing](#parsing)
- [Rendering](#rendering)
- [Fingerprints and normalization](#fingerprints-and-normalization)
- [Providers](#providers)
- [Command-line functions](#command-line-functions)
- [Audit workflow](#audit-workflow)

## Package exports

`inspektorium` exports these names in `__all__` ([`__init__.py`](../../src/inspektorium/__init__.py)):

| Name | Kind |
| --- | --- |
| `inspect_proposals` | Function |
| `AnswerInput`, `SourceDocument`, `InspectionInput` | Input models |
| `ProposedFinding`, `ProposalBatch` | Proposal models |
| `ValidatedFinding`, `InspectionReport` | Report models |
| `EvidenceRelation`, `EvidenceSufficiency`, `EvaluatorCertainty`, `DeterministicValidationStatus` | String enums |

`inspektorium.__version__` is `"0.3.0"`.

The subpackages export:

| Module | `__all__` |
| --- | --- |
| `inspektorium.core` | `inspect_proposals`, `validate_finding` |
| `inspektorium.report` | `render_json`, `render_markdown` |
| `inspektorium.providers` | `Provider`, `ProviderError`, `ProposalParseError`, `parse_proposal_json` |
| `inspektorium.providers.parsing` | `InputParseError`, `ProposalParseError`, `parse_inspection_input_json`, `parse_proposal_json` |
| `inspektorium.cli` | `build_parser`, `main`, `run_audit` |

All models are immutable Pydantic models that reject unknown fields ([models](../../src/inspektorium/core/models.py)).

## Reference checker

### `inspect_proposals`

```python
inspektorium.core.inspection.inspect_proposals(inspection_input: InspectionInput, proposals: ProposalBatch, *, generated_at: datetime | None = None) -> InspectionReport
```

Validates every proposal and assembles a report with fingerprints, summary and the fixed scope notice.
`generated_at` must be timezone-aware when given. It makes no provider call ([inspection](../../src/inspektorium/core/inspection.py)).

### `validate_finding`

```python
inspektorium.core.validation.validate_finding(inspection_input: InspectionInput, finding: ProposedFinding) -> ValidatedFinding
```

Applies the exact claim-span and citation checks to one proposal ([validation](../../src/inspektorium/core/validation.py)).
It returns the proposal with its check results; it never changes the proposal.

### Example

Run from the repository root:

```python
from pathlib import Path

from inspektorium import inspect_proposals
from inspektorium.providers.parsing import parse_inspection_input_json, parse_proposal_json
from inspektorium.report import render_json, render_markdown

example = Path("examples/inspect/05_mixed_and_fabricated_quote")
inspection_input = parse_inspection_input_json((example / "input.json").read_text(encoding="utf-8"))
proposals = parse_proposal_json((example / "proposals.json").read_text(encoding="utf-8"))
report = inspect_proposals(inspection_input, proposals)

print(report.summary)
for finding in report.findings:
    print(finding.claim_id, finding.deterministic_validation_status.value,
          finding.reportable_relation, [issue.code.value for issue in finding.validation_issues])
print(render_json(report) == (example / "expected_report.json").read_text(encoding="utf-8"))
print(render_markdown(report) == (example / "expected_report.md").read_text(encoding="utf-8"))
```

```text
claims_inspected=3 reportable_findings=2 citation_spans_verified=1 validation_failures=1
claim-1 passed supported []
claim-2 failed None ['evidence_span_mismatch']
claim-3 passed not_established []
True
True
```

## Parsing

```python
inspektorium.providers.parsing.parse_inspection_input_json(raw: str) -> InspectionInput
inspektorium.providers.parsing.parse_proposal_json(raw: str) -> ProposalBatch
```

Both decode with the strict JSON decoder, then validate the schema ([parsing](../../src/inspektorium/providers/parsing.py)).
They raise `InputParseError` or `ProposalParseError`, both subclasses of `ValueError`.
`ProposalParseError` messages start with `malformed_proposal:`.
Error messages name locations and rules, not input values.

Use these functions for untrusted JSON. `InspectionInput.model_validate_json` and `ProposalBatch.model_validate_json` do not apply the strict decoder; see [limitations](../evaluation/limitations.md#reference-checker-inspektorium-inspect).

```python
inspektorium.core.strict_json.load_strict_json(raw: str | bytes | bytearray) -> object
```

The decoder itself. It raises `StrictJSONError` ([strict JSON](../../src/inspektorium/core/strict_json.py)).

## Rendering

```python
inspektorium.report.json_report.render_json(report: InspectionReport) -> str
inspektorium.report.markdown_report.render_markdown(report: InspectionReport) -> str
```

Both are deterministic and read no clock. `render_json` sorts keys and ends with one newline.
`render_markdown` encodes untrusted text for display ([display](../../src/inspektorium/report/display.py)).

## Fingerprints and normalization

```python
inspektorium.core.normalization.normalize_text(text: str) -> str
inspektorium.core.fingerprints.fingerprint_text(text: str) -> str
inspektorium.core.fingerprints.canonical_bundle_json(inspection_input: InspectionInput) -> str
inspektorium.core.fingerprints.fingerprint_input(inspection_input: InspectionInput) -> InputFingerprints
```

| Function | Purpose |
| --- | --- |
| `normalize_text` | Converts CRLF and CR to LF and applies NFC; keeps other whitespace |
| `fingerprint_text` | SHA-256 hex of the normalized UTF-8 text |
| `canonical_bundle_json` | The canonical answer-and-sources JSON that is hashed |
| `fingerprint_input` | All fingerprints of an input, sources sorted by ID |

## Providers

```python
class inspektorium.providers.base.Provider(Protocol):
    def propose_findings(self, inspection_input: InspectionInput) -> ProposalBatch: ...
```

Any object with this method can supply proposals. `ProviderError` signals a failed request ([base](../../src/inspektorium/providers/base.py)).

```python
inspektorium.providers.anthropic.AnthropicProvider.__init__(self, *, model: str, client: Any | None = None) -> None
inspektorium.providers.anthropic.AnthropicProvider.propose_findings(self, inspection_input: InspectionInput) -> ProposalBatch
```

The optional Anthropic adapter ([anthropic](../../src/inspektorium/providers/anthropic.py)).
Without `client`, it needs the `providers` extra and creates an SDK client that reads `ANTHROPIC_API_KEY`.
`propose_findings` makes one SDK `messages.parse` call. It is not used in these docs.

## Command-line functions

```python
inspektorium.cli.main(argv: Sequence[str] | None = None) -> int
inspektorium.cli.build_parser() -> argparse.ArgumentParser
inspektorium.cli.run_audit(arguments: Sequence[str]) -> int
```

| Function | Purpose |
| --- | --- |
| `main` | The `inspektorium` entry point; returns the exit code |
| `build_parser` | The `argparse` parser for `inspektorium` and `inspect` |
| `run_audit` | Runs the `audit` command group with the given arguments and returns its exit code |

`inspektorium.cli.run_audit` takes command-line arguments. It is different from the workflow function of the same name below.
Exit codes are listed in the [CLI reference](cli.md).

## Audit workflow

The audit operations are functions in `inspektorium.audit.workflow.bundle` ([bundle](../../src/inspektorium/audit/workflow/bundle.py)).
They return the models `OperationResult` or `Verification` from [workflow models](../../src/inspektorium/audit/workflow/models.py).
`inspect_bundle`, `review_candidate` and `release_candidate` catch errors and return them in the model.

### Inputs

```python
inspektorium.audit.execution.task_loader.load_task(path: str | Path) -> Task
inspektorium.audit.workflow.pipeline.preflight(task: Task) -> list[str]
inspektorium.audit.review.runtime.OfflineReviewProvider.__init__(self, raw_output: str = '', *, error: str | None = None)
```

| Function | Purpose |
| --- | --- |
| `load_task` | Loads and validates a task file |
| `preflight` | Returns the eligibility errors that `audit validate` prints; empty means eligible |
| `OfflineReviewProvider` | The built-in recording provider; `raw_output` is the recorded response text |

### Operations

```python
run_audit(task: Task, provider, *, output_root: Path, review_state: Path | None = None) -> OperationResult
create_candidate(record: RunRecord, *, output_root: Path, parent: Parent | None = None) -> OperationResult
inspect_bundle(path: Path) -> Verification
review_candidate(path: Path, *, output_root: Path, state_dir: Path, selected_position_id: str, reviewer: str, reason: str, corrected_raw_output: str | None = None) -> OperationResult
release_candidate(path: Path, *, output_root: Path, reviewer: str, reason: str) -> OperationResult
```

| Function | CLI | Purpose |
| --- | --- | --- |
| `run_audit` | `audit run` | Preflights the task, runs the provider, evaluates the result and writes a candidate |
| `create_candidate` | — | Writes a revision for an already evaluated `RunRecord` |
| `inspect_bundle` | `audit inspect` | Verifies files, hashes and recomputed controls; makes no provider call |
| `review_candidate` | `audit review` | Appends a human decision and writes a new revision |
| `release_candidate` | `audit release` | Rechecks a `READY_FOR_RELEASE` revision and writes a `RELEASED` revision |

`run_audit` accepts an exact `OfflineReviewProvider`, or the live and replay providers of `inspektorium.audit.workflow.live`.
Any other provider object returns `PREFLIGHT_BLOCKED`. There is no fallback.

### Example

Run from the repository root:

```python
from pathlib import Path

from inspektorium.audit.execution.task_loader import load_task
from inspektorium.audit.review.runtime import OfflineReviewProvider
from inspektorium.audit.workflow.bundle import inspect_bundle, release_candidate, run_audit

examples = Path("examples/audit")
output_root = Path("reports/api-audit")
task = load_task(examples / "positive-task.json")
recording = (examples / "positive-recording.json").read_bytes().decode("utf-8")

candidate = run_audit(task, OfflineReviewProvider(recording), output_root=output_root)
print(candidate.status, candidate.errors)
print(inspect_bundle(Path(candidate.path)))

released = release_candidate(Path(candidate.path), output_root=output_root,
                             reviewer="Local offline operator",
                             reason="Explicit release of this synthetic test artifact")
print(released.status, released.errors)
print(inspect_bundle(Path(released.path)))
```

```text
READY_FOR_RELEASE []
valid=True status='READY_FOR_RELEASE' errors=[]
RELEASED []
valid=True status='RELEASED' errors=[]
```

The recording is decoded from bytes, as the CLI does, so the stored raw response equals the file.
The [audit workflow guide](../guides/audit-workflow.md) shows the review step with the CLI.
