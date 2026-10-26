# Nachdiagnose R1: model/host deviations (evidence for AA-P8/1.1)

Offline and read-only. No model call. Provenance class 2: a new analysis of the unchanged R1
captures and bundles (repair cycle R1, `analysis/live_smoke_20261011/repair_r1/`) with the code
of commit `c4c2a4c`. Nothing archived was changed.

- `second_opinion_result.json` holds the full result of the read-only second-opinion workflow
  (finder and adversarial verifier per model, P9 route simulation, phase map, claim check).
- `scripts/<agent>/` holds the counterfactual harnesses, copied unchanged from the session
  scratchpad. They insert scratchpad paths into `sys.path` and expect the archived bundles in
  a scratchpad copy, so a rerun needs those paths adjusted. Each harness first reproduced every
  archived host state exactly before running any counterfactual.

## The 12 deviating propositions (9 R1 slots)

Final class = class after the independent adversarial check.

| Slot | Proposition | Model | Host | Final class |
|---|---|---|---|---|
| Haiku LS-02 | claim:p1 | unsupported | unknown | representation artifact (C12 omission, no transfer bridge) |
| Haiku LS-03 | claim:p1 | supported | unknown | representation artifact (evidence_type `unknown` on a description) |
| Haiku LS-04 | claim:p1 | supported | unknown | host scientific caution (latent; fired via model C12 and transfer faults) |
| Haiku LS-04 | claim:p2 | unsupported | unknown | uncertain (host absence-to-unknown policy plus model C12 fault) |
| Haiku LS-05 | claim:p1 | unsupported | unknown | uncertain (state vocabulary divergence) |
| Haiku LS-06 | claim:p1 | contradicted | unknown | representation artifact (review without underlying items) |
| Sonnet LS-02 | claim:p1 | unsupported | unknown | representation artifact (finder said unclear; refuted) |
| Sonnet LS-03 | claim:p1 | supported | unknown | host scientific caution (no control arm described) |
| Sonnet LS-03 | claim:p2 | unsupported | unknown | representation artifact (finder said unclear; refuted) |
| Sonnet LS-04 | claim:p1 | supported | unknown | representation artifact (comparison null; host returned a false within-arm reason) |
| Sonnet LS-04 | claim:p2 | unsupported | unknown | representation artifact (finder said unclear; refuted) |
| Sonnet LS-06 | claim:p1 | contradicted | unknown | representation artifact (review without underlying items) |

Count: 8 representation artifacts, 2 host scientific caution, 2 uncertain, 0 model errors.
Every model verdict is defensible from the source text; Haiku LS-04 p1 and Sonnet LS-03 p1 only
partly (causal attribution without a described control arm).

Empty extraction `from_attributes` (C23 gap): 4 Sonnet slots (LS-03, LS-04, LS-05, LS-06),
0 Haiku slots. Overlap with the deviation slots: 3 (LS-03, LS-04, LS-06). Sonnet LS-05 has no
model/host deviation (both unknown); its only blocker was the empty `from_attributes`.

## What this corrected

The R1 report attributed C25 to model quality. That was a stop rule of the R1 order, not a
finding. In fact C25 compared the model's asserted state with the host state, so any
model/host disagreement failed as a format error. AA-P8/1.1 compares the asserted state with
the model's own judgment and routes the disagreement into a mandatory P9 conflict review
(`docs/phase8_9_conflict_addendum.md` §1, §3, §5).

The re-analysis of all 24 captures under the new contract is in `../historical_reanalysis.json`
(script `../reanalyse_captures.py`). The same script run against the original code reproduces
all 24 archived results without a single difference (`../harness_check_original_code_c4c2a4c.json`).
In the new analysis the 12 conflicting propositions are exactly the 12 rows above.
