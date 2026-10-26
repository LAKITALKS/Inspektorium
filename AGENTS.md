# Working rules for agents

These rules bind automated coding agents and agent-assisted changes in this
repository. They complement [CONTRIBUTING.md](CONTRIBUTING.md); where both
apply, follow both. They replace no test, CI check or human review.

## Current authorization

The maintainer authorized the 2026-10-26 GitHub publication of both components
and its push/PR/merge/tags/releases. See
[the dated decision](publication/2026-10-26/AUTHORIZATION.md). Earlier internal-only
restrictions are superseded within that scope. Other protections remain.

A later maintainer clarification on 2026-10-26 establishes **one instrument named
Inspektorium**; Agent Arena is its old/internal implementation name. The current
consolidation scope is a root 0.2.0 public `inspektorium audit` entry, one joint
installation and current documentation. The audit entry delegates lazily to
`agent_arena.phase10_cli.audit`; preserve the `agent-arena` 1.0.1 distribution
and all 74 audit runtime Python files byte-for-byte. Retain `agent-arena audit`
for compatibility. Keep `inspektorium inspect` explicitly scoped as the smaller
reference checker; its v0.1.1 guards are not automatically applied to audit.
See [ONE_INSTRUMENT.md](docs/ONE_INSTRUMENT.md).

This clarification is additional current scope, not a rewrite of the dated
publication authorization. Do not rewrite `publication/2026-10-26/` or historical
evidence to make names, versions or hashes look current. Its import index is
bound to publication commit `94eb4fc8b26c22da6a2cebdd01e5a7799750104d`.
Record new checks separately under `publication/2026-10-26-unified-entry/`;
report them as not executed until actually measured. No new live calls or
budget reopening follows from the unified entry or source-version change.

## Scope, license and publication

- Name the product Inspektorium. In prose, call the audit runtime the
  Inspektorium audit runtime. `agent-arena`, `agent_arena` and the
  `agent-arena/` folder are technical identities retained for provenance;
  never present them as a separate product, brand or release title.
- Stay within [SCOPE.md](SCOPE.md). Do not add scores, new relation labels,
  new evaluation semantics, fuzzy quote recovery or offset repositioning as a
  side effect of another change.
- Keep [LICENSE](LICENSE), the unchanged Apache License 2.0 text, and
  [NOTICE](NOTICE) intact. From version 0.2.0 Inspektorium is licensed under
  Apache-2.0; earlier releases remain under PolyForm Noncommercial 1.0.0, as
  published. Do not relicense third-party material or rewrite the license
  statements of historical records.
- Respect existing work: do not discard, overwrite or reformat uncommitted
  changes, files outside the task, Git history or tags.
- Local preparation is not publication. An agent does not push, open pull
  requests, merge, tag, create GitHub releases, upload packages, request DOIs
  or change the website without the maintainer's explicit decision.
- Tests and examples run offline with fakes; no live provider call, no
  credentials. Never commit secrets, private material, unapproved internal material, session
  logs, personal data beyond the published authorship metadata, or absolute
  local paths.

## Evidence and status

- Status values and metrics come only from checks that were actually executed.
  Do not copy expected, remembered or historical numbers into new results.
- Keep outcomes distinguishable: `passed`, `failed`, `skipped`,
  `not executed` and `blocked`. A skipped, blocked or missing check, or a
  missing log or result line, is never reported as passed.
- Bind every acceptance result to a version or commit, its inputs (with hashes
  where practical) and a reproducible command.
- Every protective control needs a negative counter-test (a deliberate
  violation that must be caught) and a clean positive counterpart (valid input
  that must still pass). A rejected input is not a passed rendering test.
- Never change historical values; add new dated records instead. Do not pool
  results from incompatible studies, phases or case sets.

## Untrusted text

- Answer, source and evaluator text (claims, rationales, quotations, titles,
  identifiers and anything derived from them) is data in every display path:
  Markdown and JSON reports, terminal and error messages, logs, and messages
  that a host composes around such text. A trusted prefix does not make
  appended untrusted text trustworthy.
- Such text must not create report structure or status lines, and must not
  hide warnings, later findings or the limitations section. Encode it once,
  for its context, where it is embedded; never store the encoded form.
  Document any known way in which the display still falls short (for example,
  combining marks drawn over neighbouring lines) instead of claiming that the
  rule always holds.
- Keep display changes separate from raw-data changes. Escaping or marking
  characters for display must not alter JSON values, offsets, fingerprints,
  raw proposals or canonical text, and must not normalize Unicode silently.
  State which of the two a change touches.

## Claims

- In the reference checker, a reportable relation is an evaluator proposal
  that passed exact text checks, not a verified semantic relation. Its CLI exit
  0 means a report was produced, not approval. Audit has its own status and exit
  semantics: an intact blocked bundle can pass inspection; technical artifact
  release is not scientific truth or release authorization for the software.
- Update [CLAIMS.md](CLAIMS.md) for every new or revised capability claim, and
  keep owner-reported internal results labelled as such.
