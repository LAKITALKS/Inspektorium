# Known residuals of the pre-registered live retest -004 (written before any provider call)

Written 12.10.2026 after the last allowed critique round of the live plan and committed together with the
freeze, before the first result. It changes no frozen rule, script, case, expectation, budget or order;
it records the open critique findings and fixes how the frozen labels are read in the summary and in the
final report.

## Critique history of the plan

| Round | Result | Record |
|---|---|---|
| Initial critique (scientific + operational lens, Opus, effort max) | LS1, LS2, LO2 material; further minors and notes | `../live_plan_critique/round0_initial_critique.txt` |
| Recheck 1 | LS2-1 material (technical failures counted as model/host deviations); minors LS2-2..9, LO2-1..13 | `../live_plan_critique/round1_recheck.txt` |
| Recheck 2 (last allowed) | **0 material**; all LS2 items fixed; LO2 items fixed except LO2-2 (partial, minor); new minors LS3-1, LS3-2, LO3-1 confirmed by adversarial verifiers; LO3-2 regraded to note; notes LS3-3..6, LO3-3..6 | `../live_plan_critique/round2_final_recheck.txt` |

Offline self-test of the frozen scripts (15 scenarios in throwaway roots, MockTransport, no key, no
network): `../live_plan_critique/offline_selftest_regression_v3.txt`, harness in
`../live_plan_critique/selftest_harness/` (absolute scratch paths, kept as documentation).

## Binding reading rules

1. **Attribute-string route (LS3-1, minor).** `host_route = string_mismatch_only` and the labels
   `host_deviation_likely_string_artifact` / `host_within_representation_artifact` mean *attribute-string
   route*, not proven artifact. Under contract C14 a model encodes a real scope difference with different
   strings, and the host cannot tell such a difference from a wording artifact. The report names the
   mismatched dimensions from the host reasons and reads them per dimension:
   - dimensions worded identically by design (LR-01: population, intervention, comparator, endpoint,
     follow_up; LR-02: population, intervention; LR-03: population, intervention, endpoint) → likely
     representation artifact;
   - any other dimension (for example LR-02 endpoint or follow_up: memory decline vs a single memory test
     score; LR-03 comparator or comparison: no five-day group, previous year) → represented real
     difference, which belongs to the reasoning the case tests.
   The clause "must not attribute it to the reasoning the case was designed to test" applies only to the
   first group. `semantic transfer unresolved` / `product transfer unresolved` stay undetermined.
2. **`capability` is the residual class (LS3-2, minor).** It means *not string-only*: capability rules,
   the directness rule, preserved model observations (for example `inconclusive`), no-evidence bindings,
   unresolved claim or evidence attributes and propositions without a binding. The report quotes the
   final host reasons instead of reading `capability` as a host design rule.
3. **Interrupted slots (LO3-1, LO2-2 partial, minor).** A slot with a terminal primary but no bundle is
   documented from the ledger, its captures and the committed Phase-9 state file under
   `phase9-state/<profile>/phase9/`; only the replay target is replayed by the frozen script. An extra
   offline replay of such a slot may be added to the report only as a labelled, non-pre-registered check.
   If the replay target was completed outside the runner log, `live_status`/`live_facts` null and
   `same_as_live: false` in `replay_check.json` mean *not compared*; the report compares with the bundle on
   disk.
4. **Expected yield (LO3-2, note).** With the frozen exposure tables Sonnet LR-02 runs only if the spend
   before it is at most 234,736 µUSD (Sonnet counterreview unclaimed) or 521,338 µUSD (claimed). At R1 cost
   levels it is expected to be skipped by the reserve rule: likely 5 primaries, and the clearly-unsupported
   control then runs on Haiku only. This is within the order (at most 6 primaries) and is logged with its
   inputs.
5. **P9 vocabulary (LS3-3, LO3-5, notes).**
   - A review refused before sending for budget is recorded as P9 `failed` with `request_sent: no`; this
     is the rule's "denied (budget)".
   - `claimed, no P9 record` is an interrupted review without a bundle.
   - `request_sent: yes` with `error_type: connection` means the client attempted the POST and got no
     provider response; it is reported as "attempted, no provider response".
   - `response_processed: true` also covers an HTTP-200 review that was refused or truncated; the review
     position's technical status is reported with it.
   - `routing_reached: false` for an ANALYSIS_INCOMPLETE slot with route HUMAN_REVIEW_REQUIRED means no
     conflict-review routing (technical route only).
   - `open (no P9 trigger recorded)` is practically unreachable.
   - `summarize_retest.py` reads Phase-9 data from the bundles only, not from `phase9-state/`.
   - `test_releases.json` is written after all slots; if summarize crashes after a release, the released
     revision is inspected directly.
6. **LR-01 route text (LS3-4, note).** The species/endpoint_type condition applies to the clinical
   relations only; with a supported capability, directness partial/unknown derives unknown and
   indirect/remote unsupported.
7. **Wording risks (LS3-5, note).** LR-02 keeps the sample size inside its only population phrase ("2,000
   adults aged 65 and older"); LR-03 says "all office staff" in its first sentence. LR-02's template
   sibling in the library is case 046 (daily beverage habit, lifestyle confounding), not copied.
8. **OR-logic edge (LS3-6, note).** For LR-01 the within-artifact label is read together with the host
   composite; a supported composite reached through a capability path is not an artifact.

## Operator rules (LO3-3, LO3-4, LO3-6, notes)

- Start the runner only after the freeze commit, detached, with the key loaded only into its process.
- If a start is refused by its pre-checks: fix the cause and start again (permitted while the ledger has
  0 attempts and 0 claims). Do **not** run `close_retest.py` after a refused start unless the retest is
  abandoned (BLOCKED): closing without a ledger opens the first live session of -004, which writes
  `analysis/live_smoke_20261011/repair_r1/successor_claim.json` and an empty ledger and then revokes it.
- Close only after the runner has ended (close does not check the runner lock; the lease is held only
  while a CLI request runs).
- Run `replay_retest.py` only after the run and the close, with the clean wheel venv of the tested
  commit, never with the editable repository venv; the first `replay_check.json` is canonical.
- Do not open the frozen folders in Finder (`.DS_Store` would fail the pre-check safely).
- `issued_at` is the freeze date (12.10.2026). A close after `expires_at` does not reconcile captured
  reservations; close before 15.10.2026.
