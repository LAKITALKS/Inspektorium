# Publication record — 2026-10-26

This dated publication integrates Inspektorium **0.1.1 / schema 0.1** and
Agent Arena **1.0.1**, the P1–P10 technical research implementation. Arena is a
public research prerelease. Its scientific Final v1 efficacy gate is **NOT MET**.
The [maintainer authorization](AUTHORIZATION.md) covers GitHub publication only.

## Public structure and source identity

| Component | Public location | Original source |
| --- | --- | --- |
| Core package, tests, examples and evidence | repository root | closeout `58ac8e0515b7ca2f369f4981cf8254683fe5abae`; all 19 runtime modules match product `5ace2797e4a9075ca53ccd780be616719923c288` |
| Arena package, tests, prompts, tools, research and evidence | [agent-arena/](../../agent-arena/) | technical 1.0.0 snapshot `9de4b76953aed778c42df994535cb29a4e0f9f5c`; tested product `5560e950af20cee8c35fb2c8e2bfb38807043fab` |
| Historical producing modules | [14 snapshots](../../agent-arena/historical-sources/README.md) | exact commit/file/hash mapping, without private Git history |
| Current integration evidence | [results/](results/), [logs/](logs/) | dated commands, actual outcomes and derivative hashes |

The [import index](import-index.json), [phase inventory](arena-inventory.json),
[inventory explanation](arena-inventory.md), [additional historical snapshots](additional-historical-snapshots.json)
and [redaction manifest](import-derivation.json) identify selected source files,
phases, functions, tests, documentation and public derivatives. Private source
commit IDs are provenance identifiers, not links to public Git objects.

Arena's 74 runtime modules differ from the technical 1.0.0 snapshot only in
the version and one authenticated Git lookup: `HEAD:./relative-path` resolves
the component's file in this monorepo. Six tests cover valid standalone/nested
paths and rejected changed/untracked bytes. This justified patch release is
**1.0.1**, not an assertion of unchanged 1.0.0 bytes. The
[Arena integration record](../../agent-arena/PUBLICATION.md) explains the
reproduction driver, capture tool, test fixtures and package boundaries.
Core runtime bytes and schema are unchanged by integration.

## Measured checks

Results are operator-reported automated checks, not independent empirical
validation or human peer review. [Validation details](VALIDATION.md) distinguish
executed checks, initial failures, retained limitations and pending public
verification. Installation downloads are separate from guarded evaluations.

Core's final local guarded run passed **1,355 tests**, with **98.04% overall
coverage with branch measurement enabled**; this is not a standalone branch
coverage percentage. Ruff and strict Mypy passed. Ten installed example outputs
match the committed expectations. E1 repeated the existing 87-case catalog:
348 text renderings, zero text/link violations, 0/75 visual hits and 0 INVALID
per documented style, and 87 byte-identical JSON reports compared with the
prior layout closeout. The [summary](results/e1-summary.json) and
[file manifest](results/e1-image-and-file-manifest.json) bind this evidence.
Full image evidence is in the core release attachment below. No new font or
viewer universe is implied.

Arena's final local full suite passed **2,560 tests**, with **21/21 P10 acceptance**
and 49 installed-wheel tests; see [validation details](VALIDATION.md). Earlier public-derivative fixture failures
remain in the logs, with their bounded test-only corrections documented.
Core and Arena have separate CI jobs on Python 3.11 and 3.12. They use fakes and
saved data, no provider secrets, and checked Python network guards. Monitoring
covers the installed Python socket hooks; it is not OS-wide network accounting.

## Reproduce the offline routes

Use the separate fresh environments and installed CLI examples in the
[root README](../../README.md). Installation may download public dependencies.
No provider credential is needed. The [reproduction guide](REPRODUCE.md) gives
the full tests, P10 gate, public capture reanalysis and older P6 commands.
Installability was checked separately for both wheels and both source archives;
joint installation in one environment is not claimed.

Three public historical authorization files are explicitly INERT. Native replay
against those authorization directories correctly rejects. Their original pins
remain unchanged. The public capture tool instead derives a **new
recorded-offline analysis** from complete matching primary response text,
with a manifest; it does not authenticate provider identity, historical ledger
or review state. A measured public LR-01 reanalysis produced READY_FOR_RELEASE
and passed bundle inspection; a mismatched task was rejected.

## Omissions and reproducibility limits

- No private Git history, credentials, active permissions, private sessions,
  sealed HLD identity/gold maps, private attestations, unrelated projects,
  environments, caches or operating-system files are published. Four reviewed
  anonymized P6 envelopes are included; sealed originals are not.
- Private paths and account/billing fields were removed from separate public
  derivatives. Three PDF metadata derivatives attribute the human author and
  disclose AI assistance. Seventeen historical tar archives were repacked;
  original/public and member identities are recorded. Original files remain
  private and unchanged. Embedded historical hashes still identify originals.
- These byte changes intentionally prevent original-hash validation of some
  historical paths. The bounded-harness pilot's original reproduction stopped
  at its parent-freeze hash check on public derivatives. That failed execution
  is retained; it is not a reproduced pilot result. Four documented P6 offline
  generation/analysis routes did execute successfully on public inputs.
- Fourteen source snapshots preserve known producing modules, but do not
  recreate the original private Git object database or attest old bundle origin.
  Two superseded pre-RC archive variants of `projection.py` and `render.py`
  could not be recovered; their available failed logs remain. This limitation
  concerns interim evidence, not missing final P1–P10 product modules. The
  earliest P5A manifest lacks a producer commit; none has been invented.
- Arena's full-source Ruff baseline has 368 pre-existing findings, unchanged
  in the comparison. Its established scoped lint gate passes; no project-wide
  lint or strict type-check PASS is claimed. Core strict Mypy is separate.

Rights and authorship are detailed in [THIRD_PARTY.md](THIRD_PARTY.md).
Lazaros Varvatis is the sole human project/software author. The unchanged
PolyForm Noncommercial 1.0.0 license is source-available, not OSI open source.
New commits and tags use the published author identity. Existing public history
and `v0.1.0` remain intact.

## Public entry points

- [Repository](https://github.com/LAKITALKS/Inspektorium)
- [Core v0.1.1 release](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.1.1)
- [Arena 1.0.1 research prerelease](https://github.com/LAKITALKS/Inspektorium/releases/tag/agent-arena-v1.0.1)
- [GitHub CI](https://github.com/LAKITALKS/Inspektorium/actions/workflows/tests.yml)
- [Core E1 image evidence](https://github.com/LAKITALKS/Inspektorium/releases/download/v0.1.1/inspektorium-0.1.1-publication-e1-evidence.zip)

Final public commit/tag IDs, PR/CI links and fresh download verification are in
the release's `PUBLICATION-CLOSEOUT.md`. This avoids a self-referential commit
hash in the committed report. A local validation result alone is not a claim
that publication has completed.

Technical integrity is not scientific truth. Exact quotations can be misleading;
model/host agreement is not independent corroboration. Closed Corpus examines
the supplied sources only. Causal inference, offsets and review coverage retain
their limits. REVIEW_REQUIRED remains unresolved without an explicit recorded
human decision. Historical live evidence concerns bounded synthetic cases and
earlier source states; final code has not been live-tested again. No new live
study, paid provider use, budget reopening, PyPI, DOI or website change occurred
as part of this publication.
