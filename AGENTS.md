# Working rules for agents

These rules bind automated coding agents and agent-assisted changes in this
repository. They complement [CONTRIBUTING.md](CONTRIBUTING.md); where both
apply, follow both. They replace no test, CI check or human review.

## Current authorization

The maintainer authorized the 2026-10-26 GitHub publication of both components
and its push/PR/merge/tags/releases. See
[the dated decision](publication/2026-10-26/AUTHORIZATION.md). Earlier internal-only
restrictions are superseded within that scope. Other protections remain.

## Scope, license and publication

- Stay within [SCOPE.md](SCOPE.md). Do not add scores, new relation labels,
  new evaluation semantics, fuzzy quote recovery or offset repositioning as a
  side effect of another change.
- Keep [LICENSE](LICENSE) unchanged. Describe the project as source-available
  under PolyForm Noncommercial 1.0.0, not as OSI open source.
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

- A reportable relation is an evaluator proposal that passed exact text
  checks, not a verified semantic relation. CLI exit 0 means a report was
  produced, not approval.
- Update [CLAIMS.md](CLAIMS.md) for every new or revised capability claim, and
  keep owner-reported internal results labelled as such.
