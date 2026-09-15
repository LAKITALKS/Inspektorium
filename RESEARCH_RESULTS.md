# Research results and evidence limits

INSPEKTORIUM separates public reproducibility observations from owner-reported
internal studies. These evidence classes cannot substitute for one another.
Claims are indexed in [CLAIMS.md](CLAIMS.md). Documentation review: 2026-09-15.
Software remains public 0.1.0 with schema 0.1.

## Public v0.1 observations

**Access: public code, tests and synthetic saved-input examples.** Claims P01–P11
apply to reviewed commit `16f572168025c393e953e34ccad184ca577e2bd0`.
The supplied reviewer report says all 59 files were inspected and their fetched
Git blob hashes verified. All five offline examples reproduced their ten
expected JSON/Markdown outputs byte-for-byte on Python 3.12.14 with Pydantic
2.13.5. The reviewer did not locally run the full pytest suite or any live
provider call. These are supplied reviewer observations, not new measurements
made by this documentation task.

[Historical GitHub CI](https://github.com/LAKITALKS/Inspektorium/actions/runs/31686541040)
for that exact commit succeeded on Python 3.11 and 3.12, including lint, type
checks and tests. The [historical release checklist](RELEASE_CHECKLIST.md)
records 74 tests, 88.11% overall branch-enabled coverage and 89.10%
deterministic-core branch-enabled coverage from its 2026-08-11 audit. Those
values are dated software-quality measurements, not new scientific results.
Current local checks for this documentation change are recorded separately in
the appended documentation-review section of that checklist.

### Counterexamples and reporting boundary

- **False semantic relation (P09):** in
  [example 02](examples/02_contradicted/proposals.json), the supplied reviewer
  changed `contradicted` to `supported` while retaining the true source quote
  and offsets. The intentionally false relation remained mechanically
  reportable. The exact guard does not understand whether a passage supports
  a claim. This probe is not a new fixture shipped in the repository.
- **Finding-level containment (P03, P11):**
  [example 05](examples/05_mixed_and_fabricated_quote/expected_report.json)
  preserves a valid finding while setting the fabricated-quote finding's
  `reportable_relation` to null. The proposal remains visible, the report is
  emitted successfully, and the CLI exits 0. Exit 0 is not assurance approval
  or authorization to release an artifact.
- **Absence and coverage (P04, P10):** `not_established` can remain reportable
  with all citation fields null; this does not prove absence of evidence. A
  supplied optional citation must validate. Empty findings are allowed, so
  zero guard failures does not establish that all relevant claims were found.
- **Current content, not authentication (P05):** changing source text outside
  the cited span changes its input hash without invoking a historical-state
  authentication check. The unchanged span can still pass. Hashes are not
  signatures or evidence of source authority.
- **Deterministic representation (P06):** JSON includes `generated_at: null`
  by default; Markdown omits the date line. Equal bundle hashes are intended
  for identical canonical IDs/texts irrespective of source order, not for
  arbitrary semantically equivalent paraphrases.

The five examples use synthetic precomputed proposals. They demonstrate saved
input behavior and exact fault handling, not live-model classification
accuracy, full claim coverage or broad reliability. Robustness evidence is
limited to the specific malformed fields, offsets, quotes and normalization
disturbances covered by existing regressions.

## Owner-reported internal pilot

**Access/status: OWNER-REPORTED INTERNAL EXPERIMENT; not reproduced by public
v0.1.** Claims I01–I04, I06 and I07 refer to the owner's reported internal final
commit `6d0d5cc4b0f14b7fe256e74e81c160ff363eb8f7`. Internal code and the raw
evidence package are not part of this public snapshot. No independent
replication or accessible evidence link is claimed.

### Conditions and units

| Condition | Owner-reported role | Generations |
| --- | --- | --- |
| A | Minimal task prompt | 32 completed: 24 main cases and eight variants |
| B | Scientific v2 prompt | 32 completed: 24 main cases and eight variants |
| C | Existing processing of B | Shares B's raw responses; no additional independent generations |

There were 64 generative slots, not 96 independent responses. C's reuse of B
cannot demonstrate model stabilization. Model evaluation and processing-control
evaluation are different comparisons.

### Outcomes, including null results and misses

| Observation | Owner-reported counts | Interpretation and limit |
| --- | --- | --- |
| Main-case accuracy | A/B/C each 24/24 | B−A = 0 percentage points; ceiling effect, not equivalence or general zero uncertainty. |
| Variant consistency | All eight original/variant pairs jointly correct and consistent in each condition | Related pairs are not independent additional main cases. |
| Deliberately corrupted artifacts | Baseline processing blocked 4/12; full controls blocked 12/12 | Eight additional catches; false accepts on this injected set fell from 8/12 to 0/12. |
| Clean artifact counterparts | 6/6 accepted | No false blocking among these six controls; no population-wide guarantee. |
| Semantically wrong but structurally valid answers | Both controls accepted (2/2) | Semantic errors escaped the structural controls. |
| Shared pre-execution checks | 4/4 failure cases blocked; 2/2 clean controls passed | Shared infrastructure; not an isolated incremental B/C benefit. |
| Official artifact release | Not applicable | No demonstrated end-to-end official release gate. |

Counts describe this finite injected set. They do not establish general AI
safety or improved model accuracy. In particular, catching altered artifacts
is a different outcome from detecting a wrong scientific inference.

### Cost, latency and reported reproducibility

- Known token costs: A **$0.130323**, B **$0.254577**; total known
  **$0.384900**. The conservative upper bound including one interrupted request
  is **$0.411380**. Reserved exposure is not actual spend. No subscription
  usage claim is made (I06).
- Provider median latency: A **7.67 s**, B **14.00 s**, each from 32 completed
  generations. C interpretation median: **0.128 ms**; shared checkpoint check:
  **10.9 ms**. Interpretation timing is not the whole system's overhead (I06).
- The owner reports two identical analysis reproductions, **1,930 passing
  internal tests**, and **692 unchanged historical files**. These are neither
  public v0.1 test counts nor checks performed in this task (I07).

Execution authorization, budget ledgers, state/resume authentication and
environment binding are **REPORTED IMPLEMENTED/TESTED INTERNALLY** (I04). No
public implementation of those controls was inspected. A source fingerprint
in public v0.1 must not be represented as one of these execution controls.

### Study limitations

This was a small author-constructed set with one model, N=1, unknown pretraining
exposure and no basis for population estimates. Of 32 stimuli, 31 were reviewed
by an isolated AI reviewer and one only by the author. That is not independent
human peer review. The role describes a study procedure, not project authorship.
Ceiling effects, related variants, shared raw responses, semantic misses and
the inapplicable official-release endpoint restrict the inference.

## Owner-reported historical contract study

**Access/status: owner-reported experiment, separate from the pilot and public
v0.1; code/raw package not public here.** Claim I05 concerns a historical
scientific-contract change whose exact commit was not supplied.

| Model | Before | After | Observed change |
| --- | --- | --- | --- |
| Haiku | 61/84 (72.62%) | 78/84 (92.86%) | +20.24 percentage points |
| Sonnet | 65/84 (77.38%) | 70/84 (83.33%) | +5.95 percentage points |

Both reached 17/17 ME but shared an Overclaim→CvC regression cluster. These
labels belong to an internal scientific taxonomy, not the public four-relation
schema. The 84 units included related variants and were involved in
development; repeated outputs are not independent cases.

The observations show different responses to a scientific-contract change.
They do not establish that the entire governance control system caused the
gains, or independently establish a causal model-by-contract interaction.
Do not combine this study, the later pilot or their taxonomies into one pooled
efficacy figure. Future inspectable data/code release needs separate review,
original artifacts and hashes, and explicit version mapping.
