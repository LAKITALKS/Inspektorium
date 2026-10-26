# One instrument: Inspektorium

**Inspektorium** is the public instrument. Its audit implementation is the
**Inspektorium audit runtime** (internal/former name Agent Arena, retained in
package, module and folder names for provenance). The official public workflow is
`inspektorium audit`; its five operations are `validate`, `run`, `inspect`,
`review` and `release`. The retained `agent-arena audit` command is a
compatibility entry to the same implementation.

Inspektorium 0.2.0 consists of the root distribution **0.2.0** and the audit
runtime distribution **`agent-arena` 1.0.2**. The root adds a public dispatch
layer; it does not add evaluation semantics or merge the two validation
pipelines. Runtime 1.0.2 is a license and metadata change: of the runtime's 74
Python files only `agent_arena/__init__.py` changes, for its version string.
Release checks are recorded with the [v0.2.0 release](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.2.0); the
consolidation checks of the 0.2.0 source are in the
[dated record](../publication/2026-10-26-unified-entry/README.md).

## Install once from a complete checkout

Use Python 3.11 or newer and a fresh virtual environment. Run all commands in
this guide from the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install . ./agent-arena
inspektorium audit --help
```

The single install command installs both local distributions into that
environment. Their separate distribution/import identities remain useful for
compatibility and evidence provenance. No manual `PYTHONPATH` is needed.
Examples and historical evidence are checkout files, so keep the complete
checkout available. Dependency installation may download public packages;
the recorded examples below require no provider key or live model call.

## Validate, run, inspect and release

Validate and run the positive synthetic example:

```sh
inspektorium audit validate --task agent-arena/examples/phase10/positive-task.json
inspektorium audit run --offline \
  --task agent-arena/examples/phase10/positive-task.json \
  --recording agent-arena/examples/phase10/positive-recording.json \
  --output-root reports/local-audit
```

A successful run returns `READY_FOR_RELEASE` and a candidate `path`. Read the
report and assign that returned path to `CANDIDATE`:

```sh
CANDIDATE='path returned by run'
inspektorium audit inspect --bundle "$CANDIDATE"
inspektorium audit release --bundle "$CANDIDATE" \
  --output-root reports/local-audit \
  --reviewer 'Local offline operator' \
  --reason 'Explicit release of this synthetic test artifact'
```

Assign the new returned path to `RELEASED` and inspect the released revision:

```sh
RELEASED='path returned by release'
inspektorium audit inspect --bundle "$RELEASED"
```

Release rechecks the candidate and creates a new immutable revision. The
candidate bytes remain unchanged. Each bundle contains `record.json`,
`decision.json`, `manifest.json`, `report.md` and `report.html`. Canonical PDF is
unsupported. Local artifact release does not publish the software, certify the
original claim, or establish scientific truth. The negative example can also
be technically eligible for release while retaining its contradicted finding.

## Review an unresolved case

The supplied unknown case ends in `REVIEW_REQUIRED` (controlled exit 2):

```sh
inspektorium audit run --offline \
  --task agent-arena/examples/phase10/unknown-task.json \
  --recording agent-arena/examples/phase10/unknown-recording.json \
  --output-root reports/local-audit
```

Read the returned candidate's reports and `record.json`. Assign its returned
path to `UNKNOWN_CANDIDATE` and the original position ID in its Phase-9 history
to `POSITION`. A human operator can record the supplied synthetic correction:

```sh
UNKNOWN_CANDIDATE='path returned by the unknown run'
POSITION='original position ID from the recorded Phase-9 history'
inspektorium audit inspect --bundle "$UNKNOWN_CANDIDATE"
inspektorium audit review --bundle "$UNKNOWN_CANDIDATE" \
  --state-dir reports/local-audit-state --output-root reports/local-audit \
  --select "$POSITION" --reviewer 'Local offline operator' \
  --reason 'Resolve the recorded design uncertainty using the supplied source' \
  --correction agent-arena/examples/phase10/positive-recording.json
```

Use the review result's new path for a fresh inspection and a separate explicit
release. Omit `--correction` only when selecting an existing admissible position.
Preserve the state directory for continuation. Reviewer names provide recorded
provenance, not identity authentication, and a name or reason cannot waive a
failed control. Without a recorded human decision, a mandatory unresolved
review remains unresolved and unreleased. The default operating assumptions do
not supply a reviewer or an automatic review queue.

## Read both validity and status

| Operation | Exit and decision boundary |
| --- | --- |
| `validate` | 0 means eligible input; 2 means blocked input. No release is authorized. |
| `run` / `review` | 0 means a successful ready outcome; 2 means a controlled block, including unresolved required review. Read the returned status and errors. |
| `inspect` | 0 means an intact bundle, even if its recorded status is blocked. Read both `valid` and `status`. Invalid or tampered bundles exit 2. |
| `release` | 0 means the exact local artifact revision passed current controls and explicit release intent; 2 means a controlled block. |

Usage errors exit 2; technical file/command errors may exit 1. There is no
force-release switch. Full state meanings, controls and the live/replay contract
are in the [runtime operational guide](../agent-arena/README.md). Live execution
still requires the existing work-order authorization, ledger and registered
profile. Existing budgets remain closed; this consolidation authorizes no live
call. [Historical research launchers](../agent-arena/research/legacy-launchers/README.md)
outside the official audit entry have
different contracts and must not be used as offline examples.

## Runtime boundaries

| Layer | Identity and implementation | Scope |
| --- | --- | --- |
| Public instrument | Inspektorium | One public name, joint installation and official audit workflow |
| Public dispatch | Root `inspektorium` 0.2.0; [`inspektorium.audit`](../src/inspektorium/audit.py) and [CLI](../src/inspektorium/cli.py) | Lazily invokes `agent_arena.phase10_cli.audit`; no independent audit evaluator, report rewrite or additional guard pipeline |
| Audit runtime | Inspektorium audit runtime: distribution `agent-arena` 1.0.2, package `agent_arena`; [audit CLI](../agent-arena/src/agent_arena/phase10_cli.py) | Existing P1–P10 implementation, own task parsing, execution controls, semantics/taxonomy, review, bundle binding and release controls |
| Smaller reference checker | `inspektorium inspect`; [`inspektorium.core`](../src/inspektorium/core/) | Retained v0.1.1 behavior and schema 0.1: one answer, exact claim/citation binding, a per-finding reportability gate and its own JSON/Markdown output |
| Compatibility entry | `agent-arena audit` | Existing spelling for the same audit runtime; retained for scripts and provenance |

**Audit does not automatically run the reference checker.** In particular, the
root checker's strict input decoder, exact-span rules and Markdown display
protections are not newly inserted into audit by the public name change. Audit
continues to use its own existing parser, validators, renderers and versioned
controls. Conversely, `inspektorium inspect` does not gain audit's authorization,
budget, history or release machinery merely because both commands share a
public name. Any future pipeline integration would require a separately reviewed
implementation and evidence.

`inspektorium inspect` remains available for its smaller reference use case:

```sh
inspektorium inspect \
  --input examples/05_mixed_and_fabricated_quote/input.json \
  --proposals examples/05_mixed_and_fabricated_quote/proposals.json \
  --format markdown
```

A failed finding in this reference report can coexist with CLI exit 0 because
its exit status concerns report production. The detailed contract and known
limits remain in the [root README](../README.md#smaller-reference-checker-inspektorium-inspect)
and [scope](../SCOPE.md). Do not apply those exit semantics to `audit run` or
`audit release`.

## Version and historical evidence

Root 0.2.0 identifies the public entry. The audit runtime distribution is 1.0.2:
it carries the Apache-2.0 license and updated metadata, and its new version
string changes the bytes of `agent_arena/__init__.py`, so its installed code
identity differs from 1.0.1. Audit manifests and code bindings still follow the existing runtime's
rules. The root dispatch layer does not become part of a stronger authenticated
provenance claim merely by forwarding to that runtime.

Existing reports, archives, command strings, module names and version fields may
carry the internal name, `agent-arena audit`, 1.0.1 or an earlier producing version. Those
are historical facts and byte evidence; do not relabel them in place. Earlier
bundles remain subject to their original code/package binding requirements.
This consolidation neither authenticates old provider responses nor upgrades
old evidence to a new scientific validation.

The original [publication record](../publication/2026-10-26/README.md), import
index and redaction mapping describe publication commit
`94eb4fc8b26c22da6a2cebdd01e5a7799750104d`. Their hashes remain useful at that
commit; they are not promises that current edited documentation has unchanged
hashes. The historical [v0.1.1 release](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.1.1)
and [audit runtime 1.0.1 research prerelease](https://github.com/LAKITALKS/Inspektorium/releases/tag/agent-arena-v1.0.1)
remain separately identifiable under the license they were published with.
Checks of the 0.2.0 source are in the
[consolidation record](../publication/2026-10-26-unified-entry/README.md);
release checks are recorded with the [v0.2.0 release](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.2.0).

The public-entry claim is [P19](../CLAIMS.md#unified-public-entry-020-source).
Its [regressions](../tests/test_audit_entry.py) and
[installed-workflow verifier](../scripts/verify_instrument.py) are verification
tooling, not a scientific efficacy study. Only executed checks may be reported
as passed; historical suite counts cannot be reused as current results.

## Scientific limits and rights

Technical integrity is not scientific truth. Exact quotations can mislead;
Closed Corpus examines only supplied material; model/host agreement is not
independent corroboration. Semantic classification and review can err. Historical
live evidence concerns bounded synthetic cases and older source states, with no
new live validation of the final runtime. The scientific Final v1 gate remains
**NOT MET**. No general efficacy, safety, compliance, certification or alignment
claim follows from the unified public entry.

Lazaros Varvatis remains the author and maintainer. From version 0.2.0 the
instrument is licensed under the [Apache License 2.0](../LICENSE); see
[NOTICE](../NOTICE). Earlier releases remain under PolyForm Noncommercial 1.0.0,
as published. Existing third-party attribution and historical evidence
limitations remain in force.
