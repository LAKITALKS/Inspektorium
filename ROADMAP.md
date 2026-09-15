# Research roadmap

**PLANNED — additional capabilities are not public v0.1 functionality.**
Package version 0.1.0 and schema 0.1 remain unchanged. The existing public
kernel and its five examples are defined in [SCOPE.md](SCOPE.md); the existing
release tag is preserved. The phase names organize later research and do not
announce a new release or authorize implementation.

Execution authorization, budget, state/resume and environment controls are
reported implemented/tested internally (I04), with no public implementation
inspected. The owner-reported fault pilot is described with its null results
and semantic misses in [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md). This roadmap
does not rebuild an earlier internal phase or migrate that code.

## Phase 8 — Deep Forensics

**PLANNED (R08), no public implementation or assigned release.**

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

**PLANNED (R09), no public implementation or assigned release.**

Identify material disagreements; enable independent verdict challenge and
bounded review routing. Preserve original judgments, explanations and the
decision trail. Do not hide disagreements behind consensus, or retry semantic
judgments until a preferred verdict appears.

Evaluate routing precision and recall, final decision errors and human time
at an equal review budget. A second judgment is not independent merely because
it is requested separately; disclose reviewer/model dependencies.

## Phase 10 — Reporting & Operational Finish

**PLANNED (R10), no public operational release gate or assigned release.**

Develop a canonical release path with explicit metadata, visible UNKNOWN
states, report-schema requirements, appropriate output formats, post-render
QA and operational CLI/reproducibility. Define which action is blocked when
a mandatory requirement fails, and preserve evidence of the decision.

The existing deterministic JSON and Markdown renderers are already implemented
and tested in public v0.1 (P06). Their report production and CLI exit 0 do not
implement this future official-release workflow. The internal pilot's official
artifact-release endpoint was not applicable and supplies no demonstrated
end-to-end gate.

## Final v1 gate

**PLANNED review gate, not a version announcement.**

Require real-case operational validation, a fresh mechanism-appropriate
efficacy comparison, fault injection and explicit release criteria declared
before evaluation. Disclose negative results, regressions, clean blocking,
missing/failed attempts, costs and limits. A high count of software tests or
a successful finite fault set is insufficient by itself.

[RESEARCH_PLAN.md](RESEARCH_PLAN.md) defines falsifiable questions, analysis
units, clean counterparts and informative baselines. H01—better end decisions
at acceptable total cost—remains untested. Software governance, system-controls
research and model efficacy need their own evidence. Coordinator review,
separate implementation authorization and an inspectable evidence package
precede any claim that these phases have become public capabilities.
