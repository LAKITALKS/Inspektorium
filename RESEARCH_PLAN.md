# Research plan

> **Current scope — 2026-10-26:** Inspektorium core remains 0.1.1/schema 0.1.
> Agent Arena P1–P10 is now included as a separate [public research package](agent-arena/README.md).
> [Publication mapping and current checks](publication/2026-10-26/README.md)
> supersede earlier access/publication statements below. Historical numbers,
> original dates and limits remain unchanged; publication is not independent
> replication. The scientific Final v1 gate is not met. No new live calls.

**PLAN ONLY — no new runtime, fixtures or experiments ship with this document.**
Public software is 0.1.1/schema 0.1. Phase 8, Phase 9, Phase 10 and the
final v1 gate are described in [ROADMAP.md](ROADMAP.md); their claims are
R08–R10 and H01 in [CLAIMS.md](CLAIMS.md). Phases 8–10 are implemented in the separate public Arena research 1.0.1
package, derived from internal technical 1.0.0. That
implementation answers none of the questions below; they remain open.

System-controls research asks whether a named rule prevents a forbidden action
at a defined boundary. Model evaluation asks whether answers are correct under
a common task definition. AI assurance research produces inspectable evidence
for bounded properties, including contrary evidence. Scientific claim forensics
investigates inferential defects; software governance concerns the rules and
records for changing and releasing software. These topics are related but
require different units, comparators and evidence.

## Five falsifiable questions

| Question | Comparison | Analysis unit | Outcome | Result that would defeat the claim |
| --- | --- | --- | --- | --- |
| Q1: Do exact bindings add value over schema validation? | Same frozen artifacts through schema-only processing and exact span guards, with matched clean counterparts | One distinct fault/clean artifact pair; related variants clustered | Additional invalid findings prevented from becoming reportable, with clean acceptance | No additional containment, or clean blocking that exceeds the predeclared tolerance |
| Q2: Do execution/state controls actually prevent unauthorized execution or invalid resume? | Same attempted actions under shared infrastructure, selectively enabling authorization, state and environment checks | One attempted protected action, not a log message | Forbidden action did not occur; valid resumes/executions accepted | A violation is merely logged but still executes, or allowed controls cannot proceed |
| Q3: Which epistemic contract rules affect decisions? | Competent prompt baseline versus one rule addition/ablation with identical sources, task definitions and model settings | Independent case, clustering prompt variants and repeated outputs | Correct decisions and regression counts by error family, at stated cost | No benefit on fresh cases, an adverse regression cluster, or gains explained by unequal information/compute |
| Q4: Can Phase 8 catch semantic errors with valid citations? | Exact guards alone versus Arena semantic/inferential checks, with a competent prompt baseline | Independently constructed semantic fault/clean case pair | Semantic false releases and clean release rate; evidence-type errors | Valid-citation semantic errors still pass at the same rate, or apparent gains arise only by suppressing clean releases |
| Q5: Does Phase 9 route material disagreements usefully at a fixed review budget? | Arena routing versus a prespecified simple routing baseline at equal human time | Case requiring a review decision, with independently assessed materiality | Review precision, recall, final decisions and human minutes | No decision benefit at equal budget, missed material disagreements, or worse recall hidden by high precision |

Predeclare primary outcomes, tolerances and denominators before collecting new
results. A non-significant difference does not establish equivalence. Keep
finite-fault software observations separate from model efficacy comparisons.

## Future fault suite

All rows below are proposed evaluation work, not tests included in this commit.
Execution, checkpoint, budget, inference, review and operational release
controls are inspectable in the separate Arena package. Their technical
implementation and offline tests do not answer the efficacy questions here. The small display and input catalog in
[evidence/v0.1.1](evidence/v0.1.1/) is software-regression evidence for v0.1.1,
not this fault suite.

| Category | Threat/injected fault | Expected response | Pass criterion | Clean counterpart | Metric |
| --- | --- | --- | --- | --- | --- |
| Binding/provenance | Wrong quote, source ID or offsets; source changes outside a quote | Public guard rejects mismatched spans; future state-bound control separately rejects a stale binding when required | Invalid finding has null reportable relation; any claimed historical-state control demonstrably blocks the protected action | Exact quote/current binding | Contained findings/faults and clean accepted/clean attempts, by disturbance |
| Execution | Protected operation attempted before required checks | Prevent the operation within the trusted execution boundary | No protected side effect occurs | Permitted operation with checks satisfied | Prevented unauthorized actions/attempts; clean completions/attempts |
| State/resume | Altered checkpoint, replayed state or changed bound environment | Reject invalid resume before execution | No resumed protected action from invalid state | Valid checkpoint and unchanged bound environment | Invalid resumes contained/attempts; clean resume acceptance |
| Authorization/budget | Missing authority, exhausted allocation, or spend/reservation mismatch | Reject the prohibited action; record the reason and distinguish reservations from spend | No unauthorized provider invocation; ledger reconciles observed costs | Authorized request within allocation | Prohibited calls prevented/attempts; accounting discrepancies; clean acceptance |
| Malformed output | Duplicate keys, invalid schema, unknown fields | Reject parsing without semantic repair or hidden fallback | No invalid proposal silently enters a successful inspection | Strict valid proposal JSON | Rejected malformed inputs/inputs; clean parsed/inputs |
| Scientific inference | True quote with wrong population, comparator, endpoint, entity transfer or unjustified inference | Flag the specific inferential defect with a traceable basis | Correct defect identified against independent reference; retain contrary evidence | Same-scope defensible inference | Semantic false releases/semantic-fault cases plus release rate; clean release/clean cases |
| Disagreement/review | Material conflicting judgments or spurious disagreement | Preserve originals and route according to a bounded policy | Material conflicts reached review within the fixed human budget | Compatible judgments/no material disagreement | Review precision, recall and human time; final decision errors |
| Release integrity | Missing audit link, unknown status concealed, inconsistent report metadata or post-render corruption | Explicit UNKNOWN or release block under the future operational policy | Artifact not officially released when mandatory requirements fail | Complete linked report with passing post-render QA | Invalid releases prevented/attempts; required audit links present/required links; clean releases/attempts |

Threats are scoped to the declared trusted code, state store and execution
boundary. Hashes alone cannot protect against an adversary replacing all
trusted state and code. Public v0.1 has no historical-state authentication,
execution authorization or official release gate. Report generation must not
be counted as such a gate.

## Baselines and measurement discipline

Freeze artifacts and use schema-only processing versus exact guards first,
then selective future control ablations to locate the mechanism. A no-control
baseline may illustrate a lower bound but cannot be the only scientific
comparator. Semantic methods need identical sources/common task definitions
and a competent prompt baseline. Additional model calls require explicit
compute/cost comparisons; review methods require equal human budgets.

Report counts first, always with denominators. Count missing, failed and
interrupted attempts; separate fault families, related variants and repeated
outputs. Log detection and actual containment are different endpoints. Report
finite-fault containment alongside clean acceptance; semantic false releases
alongside overall release rate; review precision alongside recall and human
time. Also measure required audit-link completeness, analysis reproducibility
and total cost/latency, including model, control, review and rendering work.
Component latency is not whole-system overhead. No weighted assurance score or
population reliability claim follows from a few fixtures.

## Demonstrations

| Status | Demonstration | What it can show |
| --- | --- | --- |
| CURRENT PUBLIC v0.1 | [Example 05](examples/05_mixed_and_fabricated_quote/input.json), using its saved proposals | Failed quotation retained with null reportable_relation; unrelated clean finding survives; CLI still exits 0 |
| CURRENT PUBLIC v0.1 LIMITATION | [Example 02](examples/02_contradicted/proposals.json); reviewer probe swaps contradicted to supported while keeping exact evidence | Valid text binding can accompany a false semantic relationship; no new fixture is added |
| CURRENT PUBLIC v0.1 | Current [fingerprint behavior](src/inspektorium/core/fingerprints.py) with source-change/order observations | Source order invariance; text changes affect digest; an unchanged quote does not authenticate historical state |
| CURRENT PUBLIC v0.1.1 | Synthetic catalog in [evidence/v0.1.1](evidence/v0.1.1/), run on public `main` `4bd0ba9` and on v0.1.1 | Whether untrusted text can forge report lines or hide warnings in the rendered page structure, and whether ambiguous `--input` JSON is rejected, with clean counterparts; no semantic or efficacy claim |
| FUTURE PUBLIC DEMO / REPORTED INTERNAL CONTROL | Checkpoint/environment mismatch and unauthorized/over-budget execution | Actual prevention at a named action boundary, if an inspectable control implementation is later admitted |
| FUTURE — PHASE 8 | Unsupported numerical confidence and semantic entity/population transfer | Whether specific inferential errors with valid text bindings can be detected |
| FUTURE — PHASE 9 | Material disagreement and budget-limited human review | Preserved judgments, routing errors and reviewer effort |
| FUTURE — PHASE 10 | Incomplete audit trail or corrupted rendered artifact | Explicit UNKNOWN and actual official-release containment, beyond existing JSON/Markdown rendering |

Reuse the five existing example directories. No sixth example, live-model demo
or new research runner is added by this plan; the v0.1.1 evidence tooling is a
reproducibility harness for display and input regressions. Future public
release of completed internal research needs a separately inspectable code/data
package, preserved originals and hashes, and a version mapping. A provenance note may explain a
historical name without creating another public product. New data collection,
paid execution and publication each require separate authorization.
