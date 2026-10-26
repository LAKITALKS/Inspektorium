# Inspektorium audit runtime

> **Current public entry — 2026-10-26:** Inspektorium is one instrument; this
> folder holds the Inspektorium audit runtime (internal/former name Agent Arena,
> retained in package, module and folder names for provenance). Use **`inspektorium audit`**
> after the joint installation below. This directory retains the **`agent-arena`
> 1.0.1** distribution and its unchanged 74 Python runtime files; the root source
> distribution is **0.2.0**. `agent-arena audit` remains a compatibility entry to
> the same runtime. See [one instrument](../docs/ONE_INSTRUMENT.md) and the
> [current consolidation record](../publication/2026-10-26-unified-entry/README.md).
> New source version is not a claim of a new published release.
>
> The [original 1.0.1 publication record](PUBLICATION.md) remains historical.
> Closeout wording below refers to internal 1.0.0 where stated. The scientific
> Final v1 gate remains NOT MET. No new live run is authorized.

Local evidence and review tooling. The supported **AA-P10/1.0** workflow turns an
input claim and a recorded response into a checked audit candidate, preserves
Phase-8 analysis and Phase-9 review history, and requires an explicit local
artifact release. This engineering checkpoint supports **recorded offline** runs and, under a separate
work-order authorization, **live** runs with Claude Haiku 5.5 / Sonnet 5.5 ([AA-P10-LIVE/1.0](docs/phase10_live_addendum.md)).
It does not establish model accuracy, reviewer quality, scientific truth, an
exhaustive literature search, customer approval, or a public software release.

This checkout is the **public technical research 1.0.1** integration of the
internal 1.0.0 source (package `agent-arena` 1.0.1, assessment
AA-P8/1.3, review AA-P9/1.3, host rules AA-P8-HOST/1.1). Its supported scope, the meaning of
"ended", "unresolved", "technically incomplete" and "released", and its known limits are summarised in
[V1_SCOPE.md](V1_SCOPE.md) (German). The official public entry is `inspektorium audit`; `agent-arena audit` is
retained for compatibility, with the same controls and outcomes.

## Install from a clean local checkout

Python **3.11 or newer** is declared. Run these commands from the repository
root (the directory containing both this folder and the root `pyproject.toml`):

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install . ./agent-arena
inspektorium audit --help
```

This is the canonical installation for Inspektorium: two retained distribution
identities in one fresh environment. Install the packages rather than adding
`src` to `PYTHONPATH`. The root public entry lazily delegates to this runtime;
it does not automatically apply the smaller `inspektorium inspect` reference
checker's parser, exact-span or display guards.

For development, install both distributions with their required test extras
in a fresh development environment. Run the runtime suite from this directory:

```sh
python3 -m venv .venv-dev
. .venv-dev/bin/activate
python -m pip install -e '.[dev]' -e './agent-arena[dev,providers]'
cd agent-arena
python -m pytest tests
```

The provider SDKs support existing adapter tests; installation does not authorize
model calls. No credentials are needed for the offline example or tests. The
provider extra explicitly declares `httpx`; Anthropic is constrained to `<1`
because the existing counted transport uses `httpx.Client`, while SDK 1.x
requires `httpx2`. This is a tested adapter compatibility boundary from the
1.0.1 integration, not new live-provider validation. The full legacy suite
exercises source-bound guards and repository assets, so retain the complete
checkout and the editable development layout. The normal installation above
remains the canonical operational installation.

Installation uses the configured normal Python package index and setuptools
build backend. Example inputs and acceptance tooling are repository files.
Runtime dependencies include Click, PyYAML and Pydantic, declared in
`pyproject.toml`. No browser, PDF engine or online provider is needed for
canonical Markdown/HTML generation and byte verification.

## Run, inspect and explicitly release an offline example

Run these commands from the repository root with the joint environment active.
Output directories are operator choices. `run`, `review` and `release` return
JSON with `status`, `path` and `errors`; use the returned absolute `path` as
`CANDIDATE` or `RELEASED` below. `validate` reports input eligibility, and
`inspect` reports bundle validity and the recorded status.

```sh
inspektorium audit validate --task agent-arena/examples/phase10/positive-task.json
inspektorium audit run --offline \
  --task agent-arena/examples/phase10/positive-task.json \
  --recording agent-arena/examples/phase10/positive-recording.json --output-root reports/local-audit
inspektorium audit inspect --bundle "$CANDIDATE"
inspektorium audit release --bundle "$CANDIDATE" \
  --output-root reports/local-audit --reviewer 'Local offline operator' \
  --reason 'Explicit release of this synthetic test artifact'
inspektorium audit inspect --bundle "$RELEASED"
```

The run produces `READY_FOR_RELEASE`, not a release. The release command checks
the candidate again and writes a **new immutable revision**, with final-status
reports checked before promotion. Original candidate bytes remain unchanged.
The `negative-*` pair exercises a legitimate **contradicted** scientific result
that may also reach `RELEASED`. Neither status affirms the original claim.

Each bundle has exactly five files:

| File | Purpose |
| --- | --- |
| `record.json` | Complete run, raw responses, analysis, original/review/adjudication history |
| `decision.json` | Current control findings, inspected report hashes, explicit local release intent |
| `manifest.json` | Version, input/case/run/code/evidence/review bindings and file fingerprints |
| `report.md` | Deterministic reference report |
| `report.html` | Equivalent escaped, responsive and printable report |

Canonical PDF is **unsupported**. The older optional WeasyPrint diagnostic
export is not a canonical release. Browser-generated print PDFs used during
engineering QA are test evidence for printable HTML only.

## Review a blocked case

The `unknown-*` example completes its technical analysis but returns
`REVIEW_REQUIRED` because a necessary scientific proposition remains UNKNOWN.
Read its reports and `record.json`; the original position ID appears in the
Phase-9 history. Set `UNKNOWN_CANDIDATE` to the run's returned path and `POSITION`
to that ID. The following synthetic correction uses the supplied source and
appends a human decision through the existing Phase-9 path:

```sh
inspektorium audit run --offline \
  --task agent-arena/examples/phase10/unknown-task.json \
  --recording agent-arena/examples/phase10/unknown-recording.json --output-root reports/local-audit
inspektorium audit review --bundle "$UNKNOWN_CANDIDATE" \
  --state-dir reports/local-audit-state --output-root reports/local-audit \
  --select "$POSITION" --reviewer 'Local offline operator' \
  --reason 'Resolve the recorded design uncertainty using the supplied source' \
  --correction agent-arena/examples/phase10/positive-recording.json
```

This example shows the existing human-decision mechanism. The v1 operating mode assumes **no**
human reviewer: an unresolved revision stays unresolved and unreleased unless such a recorded decision
exists. Use the review result's new `path` for inspection and a separate release command.
Omit `--correction` to select an existing admissible position. A reviewer name or
release reason cannot waive a failed control. Keep the state directory for any
continuation: Phase-9 case leases, history and durable attempt reservations must
survive reopening. Importing incomplete/inconsistent history is rejected before
mutation. Inspecting or reconstructing existing reports starts no provider calls.
The operator's recorded identity is provenance, not identity authentication.

## Live and replay runs (AA-P10-LIVE/1.0)

`audit run` takes exactly one of `--offline`, `--live` or `--replay`. Live and replay need an
authorization directory (authorization, ledger, raw captures) and a registered profile:

```sh
inspektorium audit run --live --task TASK.json --authorization-dir AUTH_DIR \
  --profile claude-haiku-5-5@3 --output-root reports/live-audit
inspektorium audit run --replay --task TASK.json --authorization-dir AUTH_DIR \
  --profile claude-haiku-5-5@3 --output-root reports/live-replay
```

- **Budget reservation:** every provider call, including Phase-9 reviews and retries, first reserves
  its maximal exposure in the ledger. Unknown billing stays reserved.
- **Raw captures:** the raw response is written to disk before it is interpreted. Answered slots are
  never resent.
- **Replay:** re-analyses captured live responses without any model call and keeps their live origin.
- **Provenance:** live and replayed bundles state their mode and bind model, request IDs, attempts
  and cost. Mixed or unbound execution carriers block.
- **Credentials:** read only from the `ANTHROPIC_API_KEY` environment variable and never stored.
- **Profile revisions:** a profile binds its prompt versions. `@1` uses the frozen
  `study_forensics_prompt/v3-phase8`. The repair revision `@2` uses `…-contract-r1`, which
  additionally states the existing deterministic Phase-8 validator rules. `@3` (current) uses
  `…-contract-r2` and `…-r2-review-p9-2`, the prompts of the separate model/host judgment contract;
  new live authorizations accept only these profiles. Recorded runs replay with the profile they were
  generated with. A new live run needs a new work-order authorization: all existing authorizations are
  closed, and the remaining headroom under the cumulative code ceilings would cover Haiku but not Sonnet
  calls.

Normal `pytest` makes no live call. Rules, limits and acceptance:
[docs/phase10_live_addendum.md](docs/phase10_live_addendum.md).

## States and failure handling

Scientific state, taxonomy, execution, review and release are separate dimensions.
Uncertainty and conflicts remain visible after human review. A nonmaterial
UNKNOWN or a nonmaterial model/host conflict can remain visible in a complete
report; a mandatory unresolved review blocks.

Every revision states that **automatic processing has ended** and, in the row
`open cause`, why it is not resolved (mandatory review not executed, executed with
the conflict still open, executed but failed, or a technically incomplete
analysis with its reason). No human reviewer or review queue is assumed; the
internal Phase-9 label `HUMAN_REVIEW_REQUIRED` means "not resolvable
automatically". The failing analysis, semantics/taxonomy and review controls
name their cause in the CLI `errors`; the five Phase-7B gates keep their
fixed reasons and list their findings in the report.

| Operational status | Meaning and next step |
| --- | --- |
| `PREFLIGHT_BLOCKED` | Correct the task or offline provider/input selection |
| `RUN_FAILED` | Ended without usable output; inspect execution/parser diagnostics, a new run creates a new revision |
| `ANALYSIS_INCOMPLETE` | Ended; the output could not be bound to the source (cause in the report); not reviewed, not released. A new run or a recorded human correction is needed |
| `REVIEW_REQUIRED` | Ended; not conclusively resolved and not released. The revision is immutable: only a recorded human decision (`audit review`) or a new, explicitly commissioned run creates a new revision; otherwise it stays unreleased |
| `RELEASE_BLOCKED` | Resolve the named integrity, control or render failure |
| `READY_FOR_RELEASE` | Inspect candidate; an explicit local release is still required |
| `RELEASED` | These exact local artifact bytes passed the current controls and explicit intent; a local artifact decision, not a scientific release |

`validate` exits 0 for valid input, 2 for blocked input. `run`, `review` and
`release` exit 0 for their successful READY/RELEASED outcome, 2 for a controlled
block. **`inspect` exits 0 for an intact bundle even when its recorded status is
blocked**; always read both `valid` and `status`. Invalid/tampered bundles exit 2.
Click usage errors exit 2; technical file/command errors may exit 1. A failed
operation reports its cause and remedy. No force-release switch exists.

## Architecture, controls and provenance

The root `inspektorium audit` dispatch layer calls this existing audit command
without rewriting reports, adding guards or changing evaluator semantics. The
smaller `inspektorium inspect` reference checker remains a distinct pipeline.
The audit implementation's package/version, code binding and historical command
metadata remain unchanged. The [architecture guide](../docs/ONE_INSTRUMENT.md#runtime-boundaries)
sets out these boundaries.

`audit` calls the existing runner and `BaseProvider` interface, structured-output
parser, evaluator, Phase-8 semantics/taxonomy and Phase-9 history reconstruction.
Offline mode accepts only the exact built-in recording provider and never
resolves a live provider name or falls back to a network call. Live mode accepts
only the dedicated AA-P10-LIVE Claude 5.5 adapter under a bound authorization; the
older provider adapters (including the 4.5 Anthropic adapter) remain separate,
unchanged integrations that the audit path does not use.

The fixed inventory covers preflight, parse/source/completeness, the five
Phase-7 binding/strength/symmetry/value-origin/search-scope checks, Phase-8
semantics/taxonomy, Phase-9 history/review, provenance and both actual report
files. A gate must execute at its current version. Host-derived N/A is limited to
an absent optional population, with an executed check and recorded reason.
Required claim/evidence/finding/client traces cannot be empty. This versioned
policy does not weaken the older stricter Phase-7-only release policy.

Records retain exact raw outputs. Reports use a deterministic semantic
projection; there is no extra model call for prose. Foreign strings are escaped
or literal, and cannot supply trusted HTML/status markup. Actual UTF-8 report
bytes are checked for ordered content, completeness and format parity. An
inspection recomputes controls from raw-bound history under the installed code,
so old green fields alone cannot authorize a changed artifact.

The acyclic fingerprint convention is: reports bind the record/provenance core;
decision binds checked reports; manifest binds record, decision and reports;
the manifest's self-fingerprint excludes only its own `fingerprint` field.
Revisions link their parent's manifest fingerprint. All installed audit-runtime Python module
bytes define its existing code identity; the new root dispatch layer is not
added to that unchanged binding scheme. A Git source commit is claimed only when independently
matched to those bytes; installed wheels can honestly report no Git association.
Hashes provide integrity, not signatures, immutable remote storage or PKI.

`agent-arena run` (historical research harness: provider calls without AA-P10-LIVE
authorization and without task context) and `agent-arena official-release` (historical
Phase-7B release path without AA-P8/P9/P10 controls) are **disabled in v1** and exit 2
with the retained runtime pointer to `agent-arena audit` (the compatibility
spelling of `inspektorium audit`); the release-boundary Python API stays available for
historical verification. The `report`/`client-report`/`forensic-report` outputs are
diagnostic, and every non-`audit` command is marked as not v1 in `agent-arena --help`.
Directly invoked research modules such as `python -m agent_arena.run_library` are not
v1 entry points and are not gated by an AA-P10-LIVE authorization. Inspect a canonical
bundle with `audit inspect`.

Reports treat model and source text as data: control, bidirectional and invisible
format characters are displayed as `⟦U+XXXX⟧` tokens (record.json keeps the exact
characters), and captions use host ordinals instead of model-supplied identifiers.
Bundles bind all installed module bytes, so an earlier bundle is verifiable only with
the code that produced it: an installation of the producing commit inside a matching
checkout, with matching package metadata.

Scientific rules and earlier phase boundaries are maintained in
[taxonomy](docs/study_forensics_taxonomy.md),
[taxonomy precedence](docs/taxonomy_precedence.md),
[Phase 8](docs/phase8_semantic_contract.md),
[Phase 9](docs/phase9_review_contract.md), and
[AA-P10/1.0](docs/phase10_operational_contract.md).
The [later efficacy/release gates](docs/v1_release_gates.md) remain a separate
required activity; the internal technical v1.0.0 does not satisfy the efficacy gate R1.

## Reproduction and local RC evidence

The independent acceptance corpus is
`tests/fixtures/phase10/acceptance_v1.json`, with fixed expectations and input
fingerprints. It is distinct from development tests and any future efficacy
holdout. From an installed clean checkout, run from `agent-arena/` with the environment
active:

```sh
python scripts/phase10_acceptance.py --output /absolute/new/acceptance-directory
```

Use a fresh output directory; the harness refuses to overwrite prior evidence.
It records results, exact expectation/harness hashes and artifact paths. Every
provider response is recorded offline and every test authorization is synthetic.

The retained component reproduction helper checks committed audit-runtime
source in a fresh local clone and environment, including its normal wheel
installation, all five CLI operations through the compatibility entry,
independent acceptance, the historical 49-test Phase10 subset, and the full
suite in a second fresh editable environment. From `agent-arena/`:

```sh
python3 scripts/phase10_clean_reproduce.py \
  --scratch /absolute/new/clean-checkout-directory \
  --output /absolute/new/durable-evidence-directory --full-suite
```

This helper checks the retained runtime; it does not verify the new root public
entry or joint installation. Use the [consolidation verifier](../scripts/verify_instrument.py)
and [dated record](../publication/2026-10-26-unified-entry/README.md) for those.
Both directories must be new. The helper reads committed files only, clears the
developer Python path and provider API keys for child processes, verifies the
wheel package's installed location and all module bytes against the committed
clone. For `--full-suite`, it independently verifies the editable environment's
origin and identical module bytes, with dependencies constrained to the wheel
environment's exact versions. It records both modes, commands, exit codes and
dependencies and requires an unchanged final checkout. It never uses the original
checkout's `.venv` or untracked examples. Legacy source-origin guards stay active;
a wheel-only full legacy suite is not the supported development test layout.

Representative browser/print QA uses `scripts/phase10_render_qa.mjs`, Node.js,
Playwright and a local Chromium browser. Set `PLAYWRIGHT_MODULE` and
`CHROME_EXECUTABLE` to your own installed paths, then pass `results.json` and a
new output directory. This optional engineering procedure records browser
version, report hashes, desktop/narrow dimensions, active-content/network/error
checks and print-PDF hashes. Inspect rendered pages visually; text extraction
alone is not visual acceptance. These tools are not implicit runtime dependencies.
`scripts/phase10_print_qa.py RENDER_DIRECTORY` additionally uses **pypdf** and
Poppler **pdftoppm** to check all visible text values in the print output and
rasterize first/middle/last pages for inspection. Repeated table headings at page
starts are excluded from the text-continuity comparison; material values remain
unchanged. Detailed audit histories can produce long reports.

Exact tested platform, installation/package versions, supported formats, local
RC code checkpoint, results and limits are recorded in the
[Phase-10 journal](docs/phase10_review_journal.md) and
`analysis/phase10_validation/`. Declared Python support is not a claim that every
Python/platform combination has been tested. Ruff explicitly retains the existing
`E4/E7/E9/F` rule policy across tool-version changes; historical findings remain
separate from checks on the new files. No publication is implied; the local tag `v1.0.0` marks only
the internal technical v1 closeout ([V1_SCOPE.md](V1_SCOPE.md)).

The completed local checkpoint is recorded in [RC1](analysis/phase10_validation/RC1.json)
and the [Phase10 closeout](docs/phase10_closeout.md). Compressed evidence archives
retain the original bundles and logs; extract into a new evidence directory when
needed. The archive indexes contain checksums, and each retained member was
compared with its original bytes. This checkpoint remains an offline technical RC.


## Historical names, provenance and rights

Existing reports, archives, runtime report headings and version fields may
retain the internal name and `agent-arena audit`; preserve these bytes as
provenance. The original
[publication index](../publication/2026-10-26/import-index.json) is bound to
publication commit `94eb4fc8b26c22da6a2cebdd01e5a7799750104d`, rather than to
subsequently edited current documentation. The current public name does not
revalidate old evidence or change old release/tag identities.

Lazaros Varvatis remains the author and maintainer. This runtime remains
source-available under the unchanged [PolyForm Noncommercial 1.0.0](../LICENSE),
not OSI open source; existing source attribution and third-party licenses remain
in force.
