# Phase 6 — Acceptance Criteria & Stop Conditions (6.0–6.4)

Testable criteria. Each subphase is "done" only when **all** its acceptance
criteria hold and **no** stop condition is triggered. Criteria are pre-specified
here (Phase 6.0) so later numeric results cannot retro-define them.

---

## Phase 6.0 acceptance criteria (this phase)

A6.0-1. HEAD equals the Phase 5 closeout commit `cfb78de` and tag
`v0.8.13-phase5-closeout`; tracked working tree had no pre-existing tracked changes
at start. *(verified)*

A6.0-2. All five planning artifacts exist and are internally consistent:
inventory, governance levels, execution plan, acceptance criteria, risk register.

A6.0-3. A deterministic, offline packet-integrity command exists that reports
**two separate** outcomes — semantic preservation and contamination/leakage — with
machine-readable JSON plus a human-readable summary.

A6.0-4. Packet-integrity is covered by tests (positive cases pass; injected
gold-leak and injected semantic-break are detected). New tests pass under
`python3 -m pytest`, and the pre-existing suite still passes.

A6.0-5. The tool refuses to operate on sealed paths (`internal_only/`, `research/`
expansion, private holdout) — verified by test.

A6.0-6. No taxonomy, gold, schema, retired-status, holdout definition/selection, or
historical Phase-5 artifact was modified. No model call was made. No research or
private path was staged or accessed.

A6.0-7. Only explicit Phase 6.0 paths are staged; the diff is inspected and all
modified paths reported before any commit.

**Phase 6.0 stop conditions:** HEAD differs from the closeout without a documented
successor; handoff missing; taxonomy/gold appears modified; a required Phase-6 file
overlaps a pre-existing uncommitted change; a destructive git action would be
required; packet-integrity cannot be built without touching sealed material.

---

## Phase 6.1 acceptance criteria (confidence semantics + protocol)

A6.1-1. Confidence semantics spec fixes: the numeric range/scale, the operational
meaning of a value, and the **mandatory non-silent handling of missing/non-numeric
confidence** (a run with unusable confidence is flagged/excluded, never coerced to
0.0 and treated as a real datum).

A6.1-2. The development pool is frozen in a preparation checkpoint, defined
**without any reference to holdout membership**, starting from the holdout-safe
set `{active} \ {eligible-21}`, with borderline handling and per-label counts
recorded.

A6.1-3. Calibration metrics (ECE and/or documented alternatives), reliability
binning, and selective-prediction / risk–coverage definitions are pre-specified,
with numeric acceptance thresholds, **before** any result is computed.

A6.1-4. Every 6.1 decision is classified Level 2 with a preparation checkpoint;
none uses results to choose criteria.

**Phase 6.1 stop conditions:** confidence cannot be defined without an open
methodology decision (escalate); pool freeze would require reading the eligible-21
or holdout; any metric is chosen after seeing its value.

---

## Phase 6.2 acceptance criteria (calibration + abstention)

A6.2-1. Calibration is computed exactly as pre-specified in 6.1, on the frozen
development pool only.

A6.2-2. Reliability diagram + a calibration-error metric are produced with a
result manifest binding numbers to (input pool + code commit + parameters + seed);
results are reproducible from the manifest.

A6.2-3. Abstention is **evaluated** via risk–coverage: both the benefit (error
reduction) and the cost (coverage lost) are reported. Abstention is adopted only if
it meets a pre-specified benefit criterion; otherwise it is reported as not
beneficial.

A6.2-4. No threshold or pool is re-tuned against observed numbers; no holdout data
used.

**Phase 6.2 stop conditions:** result-driven re-tuning; need for holdout; manifest
does not reproduce the reported numbers.

---

## Phase 6.3 acceptance criteria (minimal report prototype)

A6.3-1. The report renders claim, detected label, calibrated confidence **with its
documented meaning**, evidence spans, and an abstention indicator when applicable.

A6.3-2. The report carries explicit interpretation caveats and makes **no**
performance/superiority claim.

A6.3-3. Rendering code is tested on at least one development case end-to-end.

**Phase 6.3 stop conditions:** the report would imply a superiority/performance
claim; it would surface any holdout or private content.

---

## Phase 6.4 acceptance criteria (isolated comparison pilot)

A6.4-1. A comparison protocol is frozen/pre-registered **before** any comparison
result is seen; development material only.

A6.4-2. Results are reported as **explicitly underpowered**, with confidence
intervals and a no-universal-superiority disclaimer; the 16-case holdout is
described (if referenced) as an integrity/consistency test, not a broad-claim basis.

A6.4-3. Pilot results are **not** fed back into system-development choices before
the protocol is frozen (isolation preserved).

**Phase 6.4 stop conditions:** pilot used as a tuning loop; any broad/public claim
derived from the pilot; any external comparative claim (that is Level 3, out of
scope).

---

## Global stop conditions (all subphases)

Stop and report before proceeding if any of the following holds:
- holdout or `internal_only` access appears necessary;
- concurrent research-expansion files would need to be altered;
- a change would alter benchmark semantics, taxonomy, or gold;
- confidence/threshold/pool choice would depend on the results it is judged against;
- a destructive git action would be required;
- an ambiguity could affect scientific interpretation.
