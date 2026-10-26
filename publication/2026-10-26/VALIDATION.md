# Validation ledger — 2026-10-26

This ledger separates measured publication checks from historical evidence.
Commands and actual timestamps are in [commands.jsonl](results/commands.jsonl).
Logs are public path-redacted derivatives; original/public hashes are in the
[evidence derivative manifest](results/evidence-derivation-manifest.json).
Runtime identities are in the [core](results/core-product-module-hashes.json)
and [Arena](results/arena-product-module-hashes.json) module manifests.

## Core 0.1.1

| Check | Executed result | Evidence |
| --- | --- | --- |
| Final guarded full suite, Python 3.11.7 | 1,355 passed, 0 failed, 0 skipped; 98.04% overall coverage with branch measurement enabled | [pytest log](logs/offline/core-guarded-final-suite.log) |
| Ruff / strict Mypy | passed / passed, 19 files | [Ruff](logs/offline/core-ruff.log), [Mypy](logs/offline/core-mypy.log) |
| Installed core examples | 10 expected outputs identical; source module identity preserved | [installed result](results/core-installed/result.json) |
| Existing E1 bounded reproduction | 87 cases, 348 renderings; zero text/link violations; 0/75 visual hits per style, 0 INVALID; all 87 JSON outputs equal prior layout closeout | [summary](results/e1-summary.json), [manifest](results/e1-image-and-file-manifest.json) |
| Evaluation monitoring | full suite: 1 armed record / 0 refusals; E1: 176 armed processes / 0 refusals / 0 blocked browser requests | [suite events](results/core-final-netguard.jsonl), E1 archive |
| Counterchecks | 5 Python refusals plus loopback in each of three environments; 2 browser requests blocked | [canary result](results/canary-results/canary.json) |

The first core suite also passed but ran before the guard was correctly installed.
It is retained as [preliminary evidence](logs/offline/core-full-suite.log), not
used for a measured-zero network claim. The corrected guarded run above is the
final local suite. The first check did not discover or authorize a provider call.

## Arena 1.0.1

The first clean reproduction on `dd739ebfe35a9c5aba46b8ae4ede133304da74b8`
passed its installed CLI routes, **21/21 P10 acceptance** and **49 installed-wheel
tests**, then failed its complete suite: **2,554 passed / 6 failed**, 542.96 s.
The [original full-suite log](logs/arena-final-results/full-suite.log) remains.

Six public-fixture issues were corrected without changing product authorization:

- A redacted private-path negative input no longer exercised its guard; it is
  now an explicitly synthetic absolute-user-path value.
- Two continuation tests stopped at a changed public freeze before reaching
  their intended checks. Explicit synthetic self-bound fixtures exercise the
  deeper valid/tampered controls; a separate original-public binding rejection
  remains visible.
- The original closed-history pin test now checks original hashes through the
  import index and separately rejects INERT public files for live and replay.
- Two native replay tests now create and seal test-only MockTransport histories;
  never-executed review remains denied, unknown remains REVIEW_REQUIRED, tamper
  rejection and immutable history are retained. Public historical derivatives
  are not reconstructed as valid old authorizations.

Final corrected clean reproduction on `b87858c5674dd034a69f4d40b623a74077baa239`: **2,560 passed, 0 failed, 0 skipped**, two deprecation warnings, 1,507.72 s. The fresh installed package passed **21/21 P10 cases** and **49 installed-wheel tests**. Installed and editable environments matched all 74 frozen runtime modules; the final clone stayed clean. Counterchecked evaluation monitoring recorded **31 armed records / 0 refused operations**, with canaries in separate logs. See [final reproduction](logs/arena-corrected-results/reproduction.json), [full-suite log](logs/arena-corrected-results/full-suite.log) and [P10 cases](logs/arena-corrected-results/acceptance/results.json).

The count prior to fixture repairs is the historical 2,539 tests plus six
monorepo-binding tests, thirteen capture-derivation tests and two guard-counter
tests. Additional explicitly described publication controls account for any
later increase; no tests were removed or skipped to make publication pass.

## Packages and additional offline routes

Both built wheels and both source archives were installed separately in four
new environments outside the checkout: [installation results](results/asset-verification/results.json).
All imports came from site-packages and matched the 19/74 runtime modules;
core ten output comparisons and Arena positive/negative/unknown operations and
inspection passed. `pip check` passed. Setup logs are separate from guarded
execution; joint installation is not claimed. Final archive/metadata changes
and freshly downloaded artifacts are checked separately before closeout.

Public capture extraction + installed recorded-offline LR-01 analysis passed,
bundle inspection passed, and the wrong-task counterexample rejected:
[actual commands/results](results/public-capture-result.json). This does not
certify original authorization, provider, ledger, review history or Git origin.

Four P6 routes succeeded on published inputs; the older bounded-harness pilot
failed its original freeze binding on the redacted derivative:
[all five outcomes](results/extra-offline-results.json). These are not new live
experiments and do not change historical efficacy numbers.

Core Ruff is clean and strict Mypy passes. Arena's scoped historical release
lint gate, extended over changed integration paths, passes. Full-source Ruff
was measured with **368 existing findings**, identical to the origin:
[comparison](results/arena-legacy-lint-comparison.json). Arena has no established
strict Mypy gate; no strict type-check success is claimed. Compilation is a
separate successful syntax check, not a substitute for static typing.

## Review, security and public follow-through

The separate Astra reviewer distinguishes its own executions from records read.
Its [final report](FINAL_REVIEW.md) binds the frozen candidate and completed results. The [provenance review](PROVENANCE_REVIEW.md) separately covers history, assets and content. New publication tools also pass the unchanged root Ruff rules; [syntax-tree comparison](results/public-tools-format-validation.json) verifies their formatting preserves logic except import order. All roles were supplied
`model="gpt-6-astra", reasoning_effort="xhigh", fork_turns="none"`; no recursive
delegation. This is tool configuration evidence, not proof of empirical
independence or human review. Automated assistance is disclosed without adding
AI authors or Git coauthor trailers.

The focused publication audit covers selected files, all newly reachable Git
commits, archive members, JSON authorization/account structure, PDF text/metadata
and PNG textual metadata. It is not exhaustive secret detection or OCR.
Final candidate/archive scans, actual PR/main CI, tags/releases and fresh public
download checks are recorded with their actual IDs and outcomes in the release
closeout. None is inferred from a passing local test suite.
