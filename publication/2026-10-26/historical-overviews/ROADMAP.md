# Research roadmap

**Additional capabilities below are not public v0.1 functionality.**
The public package is 0.1.1 with report schema 0.1. The existing public kernel
and its five examples are defined in [SCOPE.md](SCOPE.md); the existing
release tag is preserved. The phase names organize later research and do not
announce a new public release or authorize public implementation.

Execution authorization, budget, state/resume and environment controls are
reported implemented/tested internally (I04), with no public implementation
inspected. The owner-reported fault pilot is described with its null results
and semantic misses in [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md). This roadmap
does not rebuild an earlier internal phase or migrate that code.

The owner reports that Phases 8–10 are implemented in the internal technical
v1.0.0 closeout of a separate, non-public codebase. They were checked offline
and live-tested in a limited way on earlier internal states; the closeout code
was not live-tested again. No scientific efficacy is demonstrated, and none of
this implementation is part of the public package. Making any of it public
requires a separate inspectable package and review.

## Public maintenance — v0.1.1

v0.1.1 fixes the Markdown display of untrusted text and makes `--input`
parsing strict, with a public offline evidence package (P12–P13). It adds no
Phase 8–10 capability. Full evaluator provenance in reports and a separate
`verify` command for saved reports remain later public work (P16).

## Phase 8 — Deep Forensics

**Implemented internally (R08, owner-reported); no public implementation or
assigned public release.**

Investigate semantic/inferential defects that can survive exact citation
binding:

- a proposition ledger and composite-claim decomposition;
- population, comparator and endpoint fidelity;
- evidence semantic types and inference ceilings;
- product/entity transfer between non-equivalent targets;
- negative-evidence semantics, distinguishing absence from evidence of absence;
- analytical-repair provenance, preserving originals and transformations;
- evidence-line independence rather than treating related lines as replications;
- selected high-value statistical guards.

A model may misclassify the evidence type. Mechanically applying an inference
ceiling correctly cannot then establish semantic correctness. Test valid-quote
semantic faults, competent prompt baselines and clean counterparts before
claiming decision benefit.

## Phase 9 — Disagreement & Review

**Implemented internally (R09, owner-reported); no public implementation or
assigned public release.**

Identify material disagreements; enable independent verdict challenge and
bounded review routing. Preserve original judgments, explanations and the
decision trail. Do not hide disagreements behind consensus, or retry semantic
judgments until a preferred verdict appears.

Evaluate routing precision and recall, final decision errors and human time
at an equal review budget. A second judgment is not independent merely because
it is requested separately; disclose reviewer/model dependencies.

## Phase 10 — Reporting & Operational Finish

**Implemented internally (R10, owner-reported); no public operational release
gate or assigned public release.**

Develop a canonical release path with explicit metadata, visible UNKNOWN
states, report-schema requirements, appropriate output formats, post-render
QA and operational CLI/reproducibility. Define which action is blocked when
a mandatory requirement fails, and preserve evidence of the decision.

The existing deterministic JSON and Markdown renderers are already implemented
and tested in public v0.1 (P06); v0.1.1 adds display protection for untrusted
text (P12). Their report production and CLI exit 0 do not implement this
official-release workflow. The internal pilot's official artifact-release
endpoint was not applicable and supplies no demonstrated end-to-end gate.

## Final v1 gate

**PLANNED review gate, not a version announcement. Not met.** The internal
technical v1.0.0 closeout is not this gate; it does not demonstrate scientific
efficacy.

Require real-case operational validation, a fresh mechanism-appropriate
efficacy comparison, fault injection and explicit release criteria declared
before evaluation. Disclose negative results, regressions, clean blocking,
missing/failed attempts, costs and limits. A high count of software tests or
a successful finite fault set is insufficient by itself.

[RESEARCH_PLAN.md](RESEARCH_PLAN.md) defines falsifiable questions, analysis
units, clean counterparts and informative baselines. H01—better end decisions
at acceptable total cost—remains untested. Software governance, system-controls
research and model efficacy need their own evidence. Maintainer review,
separate implementation authorization and an inspectable evidence package
precede any claim that these phases have become public capabilities.
