# Audit workflow guide

This guide runs the five `inspektorium audit` operations on the bundled synthetic examples.
It assumes the installation from [getting started](../getting-started.md) and a checkout of the repository.
Run the commands from the repository root. All runs here are offline.

[How it works](../concepts/how-it-works.md#the-audit-bundle) explains bundles, review and release.
What a released artifact does not establish is listed in [limitations](../evaluation/limitations.md#audit-workflow-inspektorium-audit).

## Inputs

An audit needs two files:

- a **task**: a `study_forensics` task with an ID, the exact original claim (`prompt`) and its source context (`context`);
- a **recording**, offline only: one recorded model response for that task.

[`examples/audit/`](../../examples/audit/) has synthetic pairs. This guide uses three:

| Task | Recording | Run outcome |
| --- | --- | --- |
| `positive-task.json` | `positive-recording.json` | `READY_FOR_RELEASE` |
| `negative-task.json` | `negative-recording.json` | `READY_FOR_RELEASE`, scientific judgment `contradicted` |
| `unknown-task.json` | `unknown-recording.json` | `REVIEW_REQUIRED` |

Every operation prints one JSON object to standard output.
Paths in the outputs below are shortened. Revision IDs, timestamps, position IDs and hashes differ in every run.

## 1. Validate the task

```sh
inspektorium audit validate --task examples/audit/positive-task.json
```

```text
{"input_valid": true, "errors": [], "release_authorized": false}
```

`validate` makes no provider call. `release_authorized` is always `false`.
A task with curated benchmark fields is blocked with exit code 2:

```text
{"input_valid": false, "errors": ["Curated benchmark case fields present (gold_label); supply only the claim, its source context and identity fields."], "release_authorized": false}
```

A task file that cannot be loaded returns `PREFLIGHT_BLOCKED`, also with exit code 2:

```text
{"status": "PREFLIGHT_BLOCKED", "errors": ["Task file not found: texts/missing-task.json"]}
```

## 2. Run the audit

### Offline with a recording

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

The run passes the recording through the real runner, parser, semantic analysis, review routing and controls.
The recording is read as bytes, so the stored raw response equals the file exactly.
`--output-root` is created if it does not exist.

`--offline` requires `--recording` and accepts no live options. Missing either gives a usage error with exit code 2:

```text
Error: --offline requires --recording and takes no live options.
```

A recording file that cannot be read ends with exit code 1:

```text
Error: Cannot read recording: [Errno 2] No such file or directory: 'texts/missing-recording.json'
```

A blocked task returns `PREFLIGHT_BLOCKED` with `"path": null`. No bundle is written.

### Live and replay

These modes are described here and were not executed for this guide.

```sh
inspektorium audit run --live --task TASK.json \
  --authorization-dir AUTH_DIR --profile claude-haiku-5-5@3 \
  --output-root reports/live-audit
inspektorium audit run --replay --task TASK.json \
  --authorization-dir AUTH_DIR --profile claude-haiku-5-5@3 \
  --output-root reports/live-replay
```

- `--live` calls the Anthropic API. It needs a written authorization directory with `authorization.json`, the budget ledger and raw captures.
- The authorization is bound to its directory. A copied directory is not executable.
- `--profile` must be a registered profile ID ([live profiles](../../src/inspektorium/audit/providers/anthropic_live.py)). An unknown ID returns `PREFLIGHT_BLOCKED`.
- The API key is read only from `ANTHROPIC_API_KEY`.
- `--replay` re-analyses the captured live responses of an authorization directory without a model call.
- Neither mode accepts `--recording`.

Budget reservation, capture and replay rules are in [methodology](../concepts/methodology.md#controls).

## 3. Inspect the bundle

```sh
CANDIDATE='path returned by run'
inspektorium audit inspect --bundle "$CANDIDATE"
```

```text
{
  "valid": true,
  "status": "READY_FOR_RELEASE",
  "errors": []
}
```

`inspect` makes no provider call. It recomputes every control from the stored history under the installed code.
Read both fields:

- `valid` is `true` when the files, hashes and recomputed controls match. Exit code 0.
- `status` is the recorded operational status. A blocked status can be valid.

A changed byte makes the bundle invalid. Here one line was appended to `report.md` in a copy:

```text
{
  "valid": false,
  "status": "RELEASE_BLOCKED",
  "errors": [
    "Verification failed: Artifact bytes do not match manifest. Rebuild from original inputs; do not release."
  ]
}
```

The exit code is 2. A path that is not a bundle directory gives the same shape with the error `Bundle must be a real directory`.

Open `report.md` or `report.html` in the bundle for the human-readable result.
Both reports start with the status, the open cause, the independent states and the revision identity.

## 4. Record a human review

The `unknown` example ends in `REVIEW_REQUIRED`:

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

The run exits 2 and writes a complete bundle. `inspect` reports it as `"valid": true` and `"status": "REVIEW_REQUIRED"`.
This revision is immutable. Only a recorded human decision or a new run continues the case.

### Find the position ID

`--select` takes a position ID from the recorded review history.
For a first review, the original position is in `selected_position_id` of `record.json`:

```sh
UNKNOWN_CANDIDATE='path returned by the unknown run'
python -c 'import json,sys; print(json.load(open(sys.argv[1]))["selected_position_id"])' "$UNKNOWN_CANDIDATE/record.json"
```

```text
p9position:<variable>
```

The same ID appears in the report table "Revision identity" as `selected position id`.

### Submit the decision

```sh
POSITION='position ID from record.json'
inspektorium audit review --bundle "$UNKNOWN_CANDIDATE" \
  --state-dir reports/local-audit-state \
  --output-root reports/local-audit \
  --select "$POSITION" \
  --reviewer 'Local offline operator' \
  --reason 'Resolve the recorded design uncertainty using the supplied source' \
  --correction examples/audit/positive-recording.json
```

```text
{
  "status": "READY_FOR_RELEASE",
  "path": "/…/reports/local-audit/<new-revision-id>",
  "errors": []
}
```

The new revision records the review as a `human_correction` position and links its parent:
`record.json` contains `parent.revision_id` and `parent.manifest_fingerprint` of the reviewed candidate.

`--correction` supplies a corrected response file. Omit it only to select an existing admissible position.
In this example, selecting the original position without a correction is rejected with exit code 2:

```text
{
  "status": "REVIEW_REQUIRED",
  "path": null,
  "errors": [
    "Review rejected: Human selection cannot waive Phase8 controls or material UNKNOWN. Supply valid bound selection/correction; historical controls cannot be waived."
  ]
}
```

A position ID that is not in the history is also rejected:

```text
"Review rejected: Selected position is absent from the bound history. Supply valid bound selection/correction; historical controls cannot be waived."
```

Keep the `--state-dir` directory for any continuation of the case. It holds the case history and its lock.

## 5. Release explicitly

```sh
REVIEWED='path returned by review'
inspektorium audit release --bundle "$REVIEWED" \
  --output-root reports/local-audit \
  --reviewer 'Local offline operator' \
  --reason 'Explicit release after recorded review'
```

```text
{
  "status": "RELEASED",
  "path": "/…/reports/local-audit/<new-revision-id>",
  "errors": []
}
```

`release` first inspects the bundle. It accepts only a valid `READY_FOR_RELEASE` revision.
It writes a new revision with status `RELEASED` and the release intent in `decision.json`, `record.json` and `manifest.json`.
The released bundle inspects as `"valid": true` and `"status": "RELEASED"`.

The input revision is not modified. For the `negative` example, all five candidate hashes were unchanged after its release:

```text
reports/negative/<revision-id>/decision.json: OK
reports/negative/<revision-id>/manifest.json: OK
reports/negative/<revision-id>/record.json: OK
reports/negative/<revision-id>/report.html: OK
reports/negative/<revision-id>/report.md: OK
```

Release refusals return `RELEASE_BLOCKED` with `"path": null` and exit code 2:

| Input | Error |
| --- | --- |
| A `REVIEW_REQUIRED` candidate | `Candidate is REVIEW_REQUIRED; a current READY_FOR_RELEASE candidate is required.` |
| An already released revision | `Candidate is RELEASED; a current READY_FOR_RELEASE candidate is required.` |
| A blank `--reviewer` | `Bundle blocked: Host intent cannot waive a blocked control; resolve the cause first. …` |
| A tampered bundle | `Verification failed: Artifact bytes do not match manifest. …` |

There is no option to force a release.

## Status reference

| Status | Meaning | Next step |
| --- | --- | --- |
| `PREFLIGHT_BLOCKED` | The task or provider selection is not eligible; no bundle is written | Correct the task or the offline provider selection |
| `RUN_FAILED` | The run ended without usable output | Read the execution diagnostics; a new run creates a new revision |
| `ANALYSIS_INCOMPLETE` | The output could not be bound to the source | Start a new run or record a human correction |
| `REVIEW_REQUIRED` | A mandatory review is open | Record a human decision with `review`, or start a new run |
| `RELEASE_BLOCKED` | An integrity, control or render check failed | Resolve the named failure |
| `READY_FOR_RELEASE` | All controls passed | Inspect, then release explicitly |
| `RELEASED` | The explicit release intent is recorded | None; the bytes of this revision are the released local artifact |

`inspect` returns the recorded status of a valid bundle.
For a bundle it cannot verify, it returns `RELEASE_BLOCKED` together with `"valid": false`.
The status logic is in [pipeline](../../src/inspektorium/audit/workflow/pipeline.py), function `evaluate`.

## Exit codes

| Operation | 0 | 2 | 1 |
| --- | --- | --- | --- |
| `validate` | Input eligible | Input blocked or unreadable; usage error | — |
| `run` | `READY_FOR_RELEASE` | Any other status; usage error | Recording file unreadable |
| `inspect` | Bundle valid, whatever its status | Bundle invalid; usage error | — |
| `review` | `READY_FOR_RELEASE` | Any other status; usage error | Correction file unreadable |
| `release` | `RELEASED` | Any other status; usage error | — |

`inspektorium audit` without a subcommand prints its help and exits 2.

## Output directory layout

After the runs in this guide, the output root holds one directory per revision.
Each directory name is the revision ID, a random UUID:

```text
reports/
├── local-audit/
│   ├── <candidate-revision-id>/        run, READY_FOR_RELEASE or REVIEW_REQUIRED
│   │   ├── decision.json
│   │   ├── manifest.json
│   │   ├── record.json
│   │   ├── report.html
│   │   └── report.md
│   ├── <reviewed-revision-id>/         review, parent = candidate
│   └── <released-revision-id>/         release, parent = reviewed or candidate
└── local-audit-state/                  --state-dir of review
    ├── decisions.jsonl
    └── phase9/
        ├── <case-id>.json
        └── <case-id>.lock
```

A revision is first written to a temporary `.audit-staging-*` directory inside the output root.
It is verified there and then renamed into place. A failed write leaves no partial revision.
The file formats are described in the [report schema](../reference/report-schema.md#audit-bundle-files).

## Python equivalent

The same operations are available as functions in `inspektorium.audit.workflow.bundle`.
See the [Python API](../reference/python-api.md#audit-workflow).
