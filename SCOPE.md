# INSPEKTORIUM: implementation and research scope

> **Current scope — 2026-10-26 maintainer clarification:** **Inspektorium** is
> one instrument. `inspektorium audit` is its official public audit workflow;
> Agent Arena is the old/internal name retained in implementation and provenance.
> The root source distribution is **0.2.0**; audit delegates to the unchanged
> **`agent-arena` 1.0.1** runtime. The smaller `inspektorium inspect` reference
> checker retains its v0.1.1/schema 0.1 contract. See
> [architecture and boundaries](docs/ONE_INSTRUMENT.md) and the
> [dated consolidation record](publication/2026-10-26-unified-entry/README.md).
> New source version does not mean a new published release. The scientific
> Final v1 gate is not met. No new live calls.

The 0.2.0 entry-point change adds no evaluation semantics and does not change
the audit runtime's 74 Python files or its distribution version. The two
installable distributions serve one public instrument and are installed together
with `python -m pip install . ./agent-arena`. `agent-arena audit` remains a
compatibility entry to the same runtime. Reference-checker guarantees do not
automatically apply to audit: audit does not invoke `inspektorium inspect` or
reuse its validation pipeline.

The original v0.1 reference-checker boundary remains fixed at the 0.1.1 behavior
and report schema 0.1. Version 0.1.1 was a maintenance version of 0.1.0; it fixed
Markdown display and `--input` parsing. The detailed v0.1 sections below describe
that smaller checker, not exclusions from the broader audit implementation.
The [claim ledger](CLAIMS.md) assigns each claim a version, evidence source and
verification/access status. The original [publication mapping](publication/2026-10-26/README.md)
is bound to commit `94eb4fc8b26c22da6a2cebdd01e5a7799750104d`; its hashes are not
current-document checksums after this consolidation.

## Purpose

Inspektorium produces inspectable evidence through an audit workflow with input
validation, recorded or authorized execution, bundle inspection, explicit human
review where required, and local artifact release. These are bounded research
controls, not proof of scientific truth or general efficacy.

The smaller reference checker performs deterministic checking of selected
integrity errors in AI analysis artifacts:
exact claim spans, exact citation text and offset binding, and gated
reportability of each finding, plus a report display that treats answer,
source and evaluator text as data. The reference checker does not decide whether a
claim, a source or a proposed relation is correct.

## Reference-checker v0.1 implementation

- One answer per inspection.
- One or more explicitly user-supplied text sources.
- Evaluator-proposed atomic claims.
- Exactly four evaluator-proposed source relationships: `supported`,
  `contradicted`, `not_established`, and `attribution_mismatch`.
- Exact deterministic claim-span and citation-span validation.
- Citation-gated `reportable_relation` without claims of semantic proof.
- Qualitative evidence sufficiency and evaluator certainty.
- Unicode NFC/LF canonicalization and Python character offsets.
- Deterministic SHA-256 fingerprints.
- Deterministic JSON and Markdown reports; since 0.1.1 the Markdown report
  escapes untrusted text for its context and shows characters of the Unicode
  categories Cc, Cf, Cs, Zl and Zp, code points unassigned (Cn) in the running
  Python's Unicode database and the exact marker brackets as `⟦U+XXXX⟧`
  markers, while JSON keeps the exact characters. The at sign is also marked.
  At most four consecutive Mn/Me characters stay raw; later characters in
  each run are marked, including variation selectors. Private-use characters
  and other invisible characters outside these categories are not marked.
- Strict JSON parsing for precomputed proposals and, since 0.1.1, for
  `--input` files through the same decoder; since 0.1.1 a verified citation
  also requires a complete evidence reference in the report models.
- Exactly one optional real provider: Anthropic.
- A local single-answer CLI.
- Exactly five synthetic offline examples.

## Runtime exclusions retained for the v0.1 reference checker

- Global, weighted, trust, quality, or severity scores.
- Calibrated probabilities or empirical confidence calibration.
- Answer-level labels or hidden relationship sublabels.
- Case libraries, benchmark suites, rankings, or leaderboards.
- Multi-model comparison or a second provider in v0.1.
- Agents, multi-step traces, orchestration, or semantic retry loops.
- Batch datasets, directory crawling, or experiment infrastructure.
- Human adjudication or annotation workflows.
- Domain-specific truth certification.
- Source-quality ranking or automated web research.
- Fuzzy quotation recovery, automatic repair, or silent evidence substitution.
- Databases, web applications, hosted services, or governance platforms.
- Internal scientific Solid/Overclaim/CvC/ME taxonomy.
- Execution authorization, budget ledgers, checkpoint/resume authentication,
  environment binding, scientific inference checks, independent adjudication
  and a production release gate.
- Report authentication, full evaluator provenance and a `verify` command.

The [evidence package](evidence/v0.1.1/) under `evidence/` contains test
tooling and a synthetic catalog for reference-checker version 0.1.1. It is reproducibility
material, not a benchmark suite or runtime feature.

## Reference-checker semantic boundary

`proposed_relation` is generated by an evaluator. Deterministic code verifies
only canonical answer and citation spans plus structural requirements. When the
mandatory guards pass, the unchanged proposal may appear as
`reportable_relation`. Reportability is not semantic verification.

An exact excerpt can still misrepresent its source, for example by omitting a
negation. Exact text binding does not confirm the meaning of a relation (P14).

`not_established` may be proposed without a quotation. That omission does not
prove source insufficiency; the relation remains an evaluator judgment and is
not a scientifically examined refutation (P04, P15). Any optional explanatory
citation must validate exactly.

Failed mandatory checks set the individual `reportable_relation` to null;
they preserve the original proposal and allow the whole report to be emitted.
Example 05 exits 0 despite a failed quotation. This is not assurance approval.
An exact true quotation with a false proposed semantic relationship can still
pass, as demonstrated by the reviewer probe on example 02. Empty findings are
allowed; zero validation failures is not a coverage guarantee (P03, P09–P11).

Offsets are strict. A quotation whose text exists in the source but not at the
proposed offsets fails; nothing is searched for or repositioned. These
rejections are intended behavior, and no general false-alarm rate follows from
the tests or examples (P17).

Fingerprints bind current canonical content, not authenticated historical
state. Neither a digest nor an unchanged citation span establishes source
authority. A report that validates against the schema has not been re-checked
against its sources and is not proof of its origin (P16). Reliability claims
are limited to fixed saved inputs/settings; robustness observations are
limited to the named regression and catalog disturbances. The Markdown display
protection is evidenced for the published synthetic catalog and the named
Markdown implementations only; the 2026-10-24 correction and remaining limits, including untested
fonts/viewers and look-alike marker brackets, are listed in the
[changelog](CHANGELOG.md#known-display-limits) (P12).

The earlier `403bd3f` check found ink inside the `Answer span` text box in
6/75 Noto Serif and 5/75 local GitHub-like cases. The follow-up `5ace279`
places the claim in its own paragraph before the host-control list. The same
75-case pixel checks now record **0/75 hits and 0 INVALID per style**;
`Answer span` remains measured. See the
[layout follow-up](evidence/v0.1.1/addendum-20261024-e1-layout/README.md).
This bounded result is not a universal font/viewer or readability guarantee.

## Broader research direction and its evidence status

- **IMPLEMENTED + TESTED IN PUBLIC v0.1:** exact spans, fingerprints,
  deterministic reports and strict offline parsing (P01–P07); in 0.1.1 also
  Markdown display of untrusted text as data and strict `--input` parsing
  (P12–P13).
- **HISTORICAL EXPERIMENTS, NOW WITH PUBLIC DERIVATIVES:** artifact-fault
  containment, zero observed A/B accuracy gain and semantic misses (I01–I03).
  The [Arena evidence tree](agent-arena/analysis/) and
  [import map](publication/2026-10-26/import-index.json) expose reviewed sources
  and any redactions; historical results are not independently validated by
  this publication.
- **PUBLIC ARENA RESEARCH IMPLEMENTATION:** execution authorization, budget,
  state/resume and environment controls (I04), plus P1–P7 tooling, are in the
  retained `agent-arena/` runtime distribution. Their original limits and closed budgets
  remain in force.
- **PUBLIC ARENA PHASES 8–10:** semantic/inferential checking (R08), disagreement
  and review routing (R09), canonical artifact release and post-render QA (R10).
  These are technical research 1.0.1, derived from internal 1.0.0, not additions
  to the reference-checker pipeline. They are exposed through the public audit entry. Earlier live checks cover limited synthetic cases on
  older code. No new live validation or scientific efficacy is claimed.
- **NOT CLAIMED:** general AI safety, regulatory compliance, certification or
  alignment. No NIST, DSIT or regulatory endorsement/conformance is implied.

AI assurance research seeks inspectable evidence for bounded properties,
including negative evidence. Technical AI governance requires a named rule,
an enforcement boundary and a traceable decision. These research definitions
do not certify a deployment. Evidence integrity/provenance in public v0.1
means textual/input binding. An improved end decision at acceptable cost is
an untested hypothesis (H01), not a renamed implementation feature.

## Change control

The reference-checker boundary remains fixed through v0.1. [ROADMAP.md](ROADMAP.md) and
[RESEARCH_PLAN.md](RESEARCH_PLAN.md) describe later, separately reviewed work.
Version 0.1.1 changes Markdown rendering and its labels, `--input` parsing and
CLI error messages, one report-model invariant (a verified citation requires a
complete evidence reference), tests, documentation and development
dependencies, and adds the evidence package. It keeps relation semantics,
guard rules, offsets, fingerprints, JSON report output and schema 0.1. The
historical v0.1.0 release and tag are unchanged.

The 2026-10-26 publication includes the reviewed Arena snapshot and public
evidence derivatives with explicit version mapping and preserved originals.
Private/client cases, credentials, account data and material with unclear rights
remain excluded. Own reviewed prompts and synthetic captures are included. Keep [PolyForm Noncommercial 1.0.0](LICENSE) unchanged and use
source-available terminology. The maintainer explicitly authorized this GitHub release in the
[dated decision](publication/2026-10-26/AUTHORIZATION.md).

The maintainer's later 2026-10-26 clarification consolidates the public name,
installation and audit entry. It does not retroactively alter the earlier
publication authorization, historical results, report metadata or archived
module bytes. The 0.2.0 work changes the public dispatch layer and current
documentation; it preserves the 1.0.1 audit runtime and its controls. New checks
and publication decisions belong in the separate consolidation record.
