# CLI reference

Inspektorium installs one command, `inspektorium`. `python -m inspektorium` is equivalent.
The help texts below are the verbatim output of Inspektorium 0.3.0.
The parser is defined in [cli.py](../../src/inspektorium/cli.py) and [audit/cli.py](../../src/inspektorium/audit/cli.py).

- [`inspektorium`](#inspektorium)
- [`inspektorium inspect`](#inspektorium-inspect)
- [`inspektorium audit`](#inspektorium-audit): [`validate`](#audit-validate), [`run`](#audit-run), [`inspect`](#audit-inspect), [`review`](#audit-review), [`release`](#audit-release)

## `inspektorium`

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

A subcommand is required. Without one, the command prints the usage line and exits 2.
There is no `--version` option; `inspektorium.__version__` holds the version.

`inspektorium audit …` is dispatched before argument parsing to the audit command group.
The audit runtime is imported only then, so `inspektorium --help` and `inspect` do not load it.

## `inspektorium inspect`

Validates evaluator proposals for one answer and renders one report.

```text
usage: inspektorium inspect [-h] (--input INPUT | --answer ANSWER)
                            [--source SOURCE_ID=PATH]
                            (--proposals PROPOSALS | --provider {anthropic})
                            [--model MODEL] [--format {json,markdown}]
                            [--output OUTPUT] [--generated-at GENERATED_AT]

options:
  -h, --help            show this help message and exit
  --input INPUT         InspectionInput JSON file
  --answer ANSWER       answer text file
  --source SOURCE_ID=PATH
                        source text file; repeat for multiple sources
  --proposals PROPOSALS
                        precomputed ProposalBatch JSON for offline inspection
  --provider {anthropic}
                        optional live evaluator provider
  --model MODEL         Anthropic model identifier; required with --provider
  --format {json,markdown}
  --output OUTPUT       output file; omit to write to standard output
  --generated-at GENERATED_AT
                        optional explicit ISO-8601 timestamp included in the
                        report
```

| Option | Rule |
| --- | --- |
| `--input` / `--answer` | Exactly one is required. `--input` is an [`InspectionInput`](report-schema.md#inspection-input) JSON file; `--answer` is a UTF-8 text file. |
| `--source SOURCE_ID=PATH` | Required at least once with `--answer`. Not allowed with `--input`. |
| `--proposals` / `--provider` | Exactly one is required. `--proposals` is a [`ProposalBatch`](report-schema.md#proposal-batch) JSON file. |
| `--provider anthropic` | Calls the Anthropic API once. Needs `--model`, the `providers` extra and `ANTHROPIC_API_KEY`. |
| `--format` | `markdown` (default) or `json`. |
| `--output` | Writes the report to this file. The parent directory must exist. |
| `--generated-at` | ISO 8601 with a timezone offset; `Z` is accepted. Without it, `generated_at` is `null`. |

Processing order: the input file and `--generated-at` are validated first.
Proposals are loaded, or the provider is constructed, only after both succeed.
The report is rendered and checked for UTF-8 encodability before anything is written.

### Exit codes

| Code | Cause |
| --- | --- |
| 0 | The report was written, including reports that contain failed findings |
| 2 | Argument usage error |
| 2 | Rejected input or proposal JSON, unreadable or missing file, invalid `--generated-at`, provider error or schema error |

Errors other than usage errors print one line, `inspektorium: error: <reason>`, to standard error. For example:

```text
inspektorium: error: --source cannot be combined with --input
inspektorium: error: at least one --source SOURCE_ID=PATH is required
inspektorium: error: --generated-at must include a timezone offset
inspektorium: error: Inspection input is not valid JSON: duplicate object key 'text'.
```

What exit code 0 means is bounded; see [limitations](../evaluation/limitations.md#reference-checker-inspektorium-inspect).

## `inspektorium audit`

```text
Usage: inspektorium audit [OPTIONS] COMMAND [ARGS]...

  Canonical AA-P10 local audit: recorded offline, authorized live or live
  replay. No canonical PDF.

Options:
  --help  Show this message and exit.

Commands:
  inspect   Revalidate files/raw/history/current controls, zero calls.
  release   Explicit local-artifact release of final checked MD/HTML.
  review    Explicit host human selection/correction, immutable revision.
  run       Run one case through the real runner/parser/P8/P9/controls.
  validate  Validate input without a provider call.
```

Without a subcommand, the group prints this help and exits 2.
Each subcommand prints one JSON object to standard output.
`run`, `review` and `release` print an operation result; `inspect` prints a verification ([formats](report-schema.md#operation-output)).
Multi-line results are indented JSON with non-ASCII characters escaped.

Common exit codes for all subcommands:

| Code | Cause |
| --- | --- |
| 2 | Click usage error, such as a missing required option |
| 1 | A file named by `--recording` or `--correction` cannot be read |

### `audit validate`

```text
Usage: inspektorium audit validate [OPTIONS]

  Validate input without a provider call. Exit 0: input eligible; 2: blocked.

Options:
  --task PATH  [required]
  --help       Show this message and exit.
```

Output for a loadable task, on one line:

```text
{"input_valid": true, "errors": [], "release_authorized": false}
```

| Exit | Meaning |
| --- | --- |
| 0 | `input_valid` is `true` |
| 2 | `input_valid` is `false`, or the task file cannot be loaded (`{"status": "PREFLIGHT_BLOCKED", "errors": [...]}`) |

`release_authorized` is always `false`.

### `audit run`

```text
Usage: inspektorium audit run [OPTIONS]

  Run one case through the real runner/parser/P8/P9/controls. 0: READY; 2:
  blocked.

Options:
  --offline                 Built-in recorded offline response (AA-P10/1.0).
  --live                    Live generation under an AA-P10-LIVE/1.0
                            authorization.
  --replay                  Offline replay of captured live responses; no
                            model call.
  --task PATH               [required]
  --recording PATH          Offline only: recorded response file.
  --authorization-dir PATH  Live/replay only: authorization, ledger and
                            captures.
  --profile TEXT            Live/replay only: registered profile ID, e.g.
                            claude-haiku-5-5@3.
  --output-root PATH        [required]
  --help                    Show this message and exit.
```

| Rule | Error |
| --- | --- |
| Exactly one of `--offline`, `--live`, `--replay` | `Choose exactly one of --offline, --live or --replay.` |
| `--offline` needs `--recording` and no live options | `--offline requires --recording and takes no live options.` |
| `--live` and `--replay` need `--authorization-dir` and `--profile`, not `--recording` | `--live/--replay require --authorization-dir and --profile, not --recording.` |
| `--profile` must be registered | `PREFLIGHT_BLOCKED` with `Unknown live profile: <id>` |
| The authorization directory must be usable | `PREFLIGHT_BLOCKED` with `Live authorization unusable: <reason>` |

The registered profiles are defined in [anthropic_live.py](../../src/inspektorium/audit/providers/anthropic_live.py).
`--output-root` is created if needed. Each result is a new subdirectory named by its revision ID.
In live mode the review state is kept in `<authorization-dir>/phase9-state`.
In replay mode it is kept in a new directory under `<output-root>/replay-state/`.

| Exit | Meaning |
| --- | --- |
| 0 | `status` is `READY_FOR_RELEASE` |
| 2 | Any other status, or a usage error |

### `audit inspect`

```text
Usage: inspektorium audit inspect [OPTIONS]

  Revalidate files/raw/history/current controls, zero calls. 0: intact (see
  status); 2: invalid.

Options:
  --bundle PATH  [required]
  --help         Show this message and exit.
```

| Exit | Meaning |
| --- | --- |
| 0 | `valid` is `true`; read `status` for the recorded outcome |
| 2 | `valid` is `false`; `status` is `RELEASE_BLOCKED` and `errors` names the failed check |

### `audit review`

```text
Usage: inspektorium audit review [OPTIONS]

  Explicit host human selection/correction, immutable revision. 0: READY; 2:
  review blocked.

Options:
  --bundle PATH       [required]
  --state-dir PATH    [required]
  --output-root PATH  [required]
  --select TEXT       [required]
  --reviewer TEXT     [required]
  --reason TEXT       [required]
  --correction PATH
  --help              Show this message and exit.
```

| Option | Meaning |
| --- | --- |
| `--bundle` | The revision to review; it must inspect as valid |
| `--state-dir` | Review state: case history, decisions and locks; keep it for continuation |
| `--output-root` | Where the new revision is written |
| `--select` | A position ID from the recorded review history |
| `--reviewer`, `--reason` | Recorded provenance of the human decision |
| `--correction` | Optional corrected response file |

| Exit | Meaning |
| --- | --- |
| 0 | The new revision is `READY_FOR_RELEASE` |
| 2 | Any other status; a rejected review returns `REVIEW_REQUIRED` with `"path": null` |

### `audit release`

```text
Usage: inspektorium audit release [OPTIONS]

  Explicit local-artifact release of final checked MD/HTML. 0: RELEASED; 2:
  blocked.

Options:
  --bundle PATH       [required]
  --output-root PATH  [required]
  --reviewer TEXT     [required]
  --reason TEXT       [required]
  --help              Show this message and exit.
```

`--reviewer` and `--reason` must be non-blank. They are stored in the release intent with the scope `local_artifact_only`.

| Exit | Meaning |
| --- | --- |
| 0 | A new revision with status `RELEASED` was written |
| 2 | `RELEASE_BLOCKED`: the bundle is invalid, not `READY_FOR_RELEASE`, or the intent is blank |

There is no force option.
Step-by-step use of all five subcommands is in the [audit workflow guide](../guides/audit-workflow.md).
