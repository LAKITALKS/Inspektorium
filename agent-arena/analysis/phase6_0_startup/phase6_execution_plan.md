# Phase 6 — Execution Plan & Contract

Converts the validated claim-forensics foundation into a calibrated, operational
system **without opening the holdout**. Each subphase lists inputs, outputs,
governance level, dependencies, deliverables, and checkpoint strategy. Subphases
are gated: **6.0 must be closed (curator-approved) before 6.1 begins**, and so on.

Cross-cutting invariants (apply to every subphase):
- calibration is **development-only** at this stage; the sealed holdout stays
  **unopened**.
- confidence must have an **explicit operational meaning** before it is calibrated.
- abstention must be **evaluated**, never assumed beneficial.
- **no universal-superiority claim** may follow from a small pilot; the 16-case
  holdout (when eventually used) is an integrity/consistency test, **not** by itself
  a statistically strong basis for broad claims.
- prompt-only comparison stays **isolated** from system-development decisions until
  its protocol is frozen.
- no result-driven selection of criteria, thresholds, or pool membership.

---

## Phase 6.0 — Governance, inventory, integrity automation, planning *(current)*

- **Inputs:** Phase 5 closeout artifacts; canonical cases; source/tests.
- **Outputs:** `phase6_0_inventory.md`, `governance_levels.md`, this plan,
  `phase6_acceptance_criteria.md`, `phase6_risk_register.md`, packet-integrity
  tool + tests, closeout doc.
- **Level:** 1 (tooling + docs). No methodology decisions are *made* here — only
  scoped and planned.
- **Checkpoint:** single Phase 6.0 closeout, curator-approved. No tag until
  approved.

---

## Phase 6.1 — Confidence semantics & development-only calibration protocol

- **Inputs:** inventory (§5 confidence readiness); frozen taxonomy; the
  **development pool** (see pool-freeze deliverable below). No model calls required
  to *define* semantics; existing recorded runs may be reused as data.
- **Outputs (documents, Level 2):**
  1. **Confidence semantics spec** — explicit range/scale; the operational meaning
     of a confidence value; mandatory handling of missing/non-numeric confidence
     (must NOT silently become 0.0 — see risk R-2); which runs are eligible.
  2. **Development-pool freeze (preparation checkpoint)** — the exact case set used
     for calibration, defined **without reference to holdout membership**: start
     from `{active} \ {eligible-21}` (holdout-safe by construction), state
     borderline handling, and record per-label counts. Frozen before any metric is
     computed. This is the single most leakage-sensitive artifact of Phase 6.
  3. **Calibration protocol spec** — the metrics (ECE and/or documented
     alternatives, reliability-diagram binning, selective-prediction / risk–coverage
     definitions), the candidate methods, the fit/evaluation split discipline, and
     pre-specified acceptance criteria — **all frozen before results** (Level 2
     separate prep vs result checkpoints).
- **Dependencies:** 6.0 closed.
- **Stop conditions:** confidence cannot be defined without an unresolved
  methodology decision → stop and escalate (Level 2/3 boundary); pool freeze would
  require inspecting the eligible-21 or holdout → stop.
- **Checkpoint:** preparation checkpoint (spec + pool freeze) approved **before**
  6.2 produces numbers.

---

## Phase 6.2 — Implement & evaluate calibration and abstention (development only)

- **Inputs:** frozen 6.1 specs + frozen development pool; recorded development-set
  model outputs (confidence + correctness). Live model calls only if separately
  authorized; otherwise reuse recorded runs.
- **Outputs:**
  1. calibration implementation (new deterministic code + tests) computing the
     pre-specified metrics and reliability diagrams;
  2. selective-prediction / risk–coverage evaluation of abstention (reporting the
     cost as well as the benefit — coverage lost vs error reduced);
  3. a **result manifest** binding each number to (input pool + code commit +
     parameters + seed).
- **Level:** 2. Result checkpoint separate from the 6.1 preparation checkpoint.
- **Dependencies:** 6.1 preparation checkpoint approved.
- **Stop conditions:** any temptation to re-tune thresholds/pool against the
  observed numbers → stop (that is result-driven selection); any need for holdout
  data → stop.
- **Acceptance:** metrics computed exactly as pre-specified; abstention evaluated
  (not assumed beneficial); reproducible from the manifest.

---

## Phase 6.3 — Minimal claim-forensics report prototype

- **Inputs:** 6.2 outputs (label + calibrated confidence + optional abstention);
  a single development case walked end-to-end.
- **Outputs:** a minimal report format that presents claim, detected label,
  calibrated confidence with its documented meaning, evidence spans, and an
  abstention indicator when applicable — with explicit interpretation caveats
  (no performance claims).
- **Level:** 2 (report interpretation rules) for the format; 1 for rendering code.
- **Dependencies:** 6.2 result checkpoint.
- **Stop conditions:** report would imply a superiority/performance claim → stop.

---

## Phase 6.4 — Isolated prompt-only comparison pilot (development only)

- **Inputs:** frozen comparison protocol (pre-registered before any comparison
  result is seen); development material only.
- **Outputs:** a small, explicitly-underpowered pilot comparing the system vs a
  prompt-only baseline, reported with confidence intervals and an explicit
  no-universal-superiority disclaimer.
- **Level:** 2 to run the pilot on development data; **any external/public
  comparative claim is Level 3** and out of Phase 6 scope.
- **Isolation rule:** the pilot must not feed back into system-development choices
  until its protocol is frozen; it is a measurement, not a tuning loop.
- **Dependencies:** 6.3; frozen comparison protocol.
- **Stop conditions:** pilot results would be used to tune the system, or to make a
  broad claim → stop.

---

## Checkpoint strategy summary

| subphase | governance | prep checkpoint | result checkpoint |
|----------|-----------|-----------------|-------------------|
| 6.0 | L1 | — | closeout (curator-approved) |
| 6.1 | L2 | semantics spec + pool freeze + protocol (frozen) | — |
| 6.2 | L2 | (uses 6.1 prep) | calibration/abstention results + manifest |
| 6.3 | L2/L1 | report format spec | prototype |
| 6.4 | L2 | frozen comparison protocol | pilot result (underpowered, disclaimed) |

**Dependencies are strictly linear.** No subphase begins until the prior subphase's
required checkpoint is approved. The holdout remains sealed across all of
Phase 6.0–6.4.
