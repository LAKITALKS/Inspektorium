# Bounded Harness-Value Pilot — pre-result protocol

Mission AA-HARNESS-VALUE-20260913-001. Architecture: **POST_GENERATION_SHARED_B_C**.
The pasted user mission authorizes this single pilot, local commits and USD 8 maximum.
No independent C generation, no Sonnet execution, no historical reruns, no Phase 8.

## Conditions and roles

Exactly 24 primary roots (six per canonical class) plus eight paraphrases from distinct
roots (two per class), English, N=1. They are an author-constructed packet sanity test,
not a representative biomedical population sample. Public-study pretraining exposure
is UNKNOWN. The original 24 provisional candidates are preserved as authoring data;
eight are replaced for overlap or source insufficiency. Final packets have 31 isolated
AI-reviewed stimuli and one AUTHOR_RECHECK-only replacement. Source-metadata fixes
were author-checked; the original blind review and disagreements are retained.

A uses the exact user instruction in A_instruction.txt. B uses the unmodified v2
component in v2_component.txt. Both append the same common_dictionary.txt and common
11-field output schema. Each stateless request contains one opaque input JSON and
no oracle, historical case, earlier answer, tool, retrieval or feedback. Source titles,
DOIs and body-version hashes are genuine source information, not label codes.

The actual AnthropicProvider.generate + installed SDK requests were captured with
httpx.MockTransport: 64 fake requests and 32 explicit C aliases to the B captures.
Generative payload and sanitized wire hashes are separate. Only the system-prompt
package differs A/B. C has no generation-affecting operation beyond B. Scientific
prompts, taxonomy, historical cases/gold, existing parser/verdict and release policy
are unchanged. A new narrowly registered mission adapter is common infrastructure.
The two legacy source edits add only this exact plan's registry/dispatch branches;
existing plan IDs, scopes, prompts and budgets retain their rules.

File roles: candidate_authoring is never model input; fresh_holdout_input contains
32 opaque packets with no gold; fresh_holdout_oracle is opened only for adjudication,
fixtures or post-freeze scoring. Execution hashes committed inputs and the freeze,
but does not read the oracle. Raw bytes and attempt ledger precede any scoring join.
Temporary synthetic tests demonstrate full execution without an oracle directory.

## Runtime, budget and stopping

Exact model claude-haiku-4-5-20251001, temperature 0.0, max output 4096, timeout
120 seconds, omit top_p, no provider seed or extra request features. Input limit
6000; count_tokens on final payloads measured a maximum 2079 and the gate requires
at least 1000 spare tokens. Token counting is an estimate, with more than 3900 tokens
of actual headroom to the 6000 accounting bound. No content is truncated to fit.

Schedule uses random.Random(20260913): shuffle sorted opaque IDs, then shuffle a
list of sixteen AB and sixteen BA orders; generate one block per stimulus. This
seed is only a scheduling/bootstrap seed. 64 terminal logical slots, at most 192
potentially billable HTTP attempts, one request at a time. The installed production
SDK retains two transport retries; the underlying HTTP transport has zero additional
retries. Only connection/timeout, 408/409 transient conflict, 429 and 5xx retries are
eligible. Other status responses cannot enable a retry through x-should-retry.
No label, confidence, schema, refusal or truncation-based retry; those are terminal.
After an exhausted provider error, stop and preserve INCOMPLETE. Resume is prohibited.
A preexisting lease prevents a new invocation, including after partial execution.

Live official pricing and matching account mode were checked: first-party prepaid,
existing credit balance sufficient for the 5.08416 USD worst-case debit, automatic
reload disabled, no new credit purchase or billing-setting changes. Browser account
ID and execution-credential organization header match by SHA256. No private address,
payment data, credential or plaintext account identifier enters the evidence bundle.
Ordinary pricing is USD 1/M input and 5/M output tokens: per-attempt maximum 0.02648,
64*3 maximum 5.08416, below 8. The ledger atomically reserves 26,480 micro-USD before
EACH HTTP attempt. All reservations, including unknown billing, remain reserved even
after token usage is reported; this is deliberately pessimistic. The lease has one
owner and no supported resume. It binds the trusted spec, exact commit, source and
environment. Expiry: 2026-09-15T00:00:00+00:00. After completion/interruption the state
is consumed/revoked, executable remaining budget zero. No old authorization reopens.

## Primary endpoint and calculations

The ONE primary semantic contrast is B minus A operational accuracy on **all 24**
preassigned roots. Common operational validity requires complete required schema,
allowed final label, correct field types, finite confidence in [0,1], no truncation
or repair, and terminal provider output. Confidence validity IS required. Invalid,
missing and noncompleted outputs are incorrect. Separate label-readable, raw-label
correct, schema-valid, confidence-valid, final interpreted label, research diagnostic
acceptance and official-release flags are retained. Raw label-only accuracy also uses
all 24 roots, with unreadable labels incorrect. Variants never enter this denominator.

Exact two-sided McNemar: binomial tail on discordant paired root counts under 0.5;
p=1 for zero discordance, alpha .05. Report both correct, X-only, Y-only, both wrong,
label and validity discordances. 10,000 paired bootstrap draws, seed 20260913, sampling
six roots with replacement independently in each gold class while preserving arm
pairing; percentile 2.5/97.5 interval in pp. Constant bootstrap draws are flagged as
degenerate, never as absence of uncertainty. Marginal Wilson 95% intervals. No
multiple-comparison superiority claims; A->C and B->C are descriptive secondary
processing comparisons. On INCOMPLETE, no registered efficacy verdict or causal
interpretation of missing-as-error differences; only conservative descriptive counts.

Report absolute pp, relative accuracy change (NA if X=0), relative error reduction
(NA if X=1; negative values mean worsening). A is sufficiently specified foundation-
model task performance, not an identifiable percentage of intelligence. B-A measures
the prompt package on this constructed task. B/C raw identity rules out a separately
measured raw semantic contribution of C; final interpretation/acceptance is separate.

## Fixed secondary families

* Six-per-class recall and four-class confusion with invalid/missing column; worsening
  root IDs. False solid endorsements /18 non-solid roots. A released critique does
  not endorse its target claim. High-confidence wrong at >=.90: count /all 24 and
  /readable-label-plus-valid-confidence roots, with both denominators shown.
* Selected-label correctness Brier mean((p-correct_label)^2), only readable labels and
  finite valid confidence. Main paired difference on the common eligible intersection;
  each arm's available-case score and invalid count also shown. Missing is NA. ECE5
  exploratory: bins [0,.2), [.2,.4), [.4,.6), [.6,.8), [.8,1]. No multiclass Brier,
  recalibration, bin search or after-result endpoint selection. Improvement is X-Y;
  relative score reduction only for positive X with the paired n disclosed.
* B's standard diagnostic view accepts valid common schema. C invokes unchanged
  production parse_structured_output/_detect_label, analytical_state,
  is_calibration_valid, seal_new_record and validate_resume_checkpoint at the bound
  research-artifact scope. Gold is joined after raw freeze for correctness metadata;
  no oracle correctness is an acceptance rule. Report retained correct and wrong,
  wrong accepted /accepted, and accepted /all assigned; risk NA for zero accepted.
  Existing official release_official_artifact takes a different ForensicRecord and
  SourceExecutionBinding. There is no existing automatic conversion for these
  diagnostic validation records. Official release is therefore N/A, flag false,
  coverage zero, conditional risk NA. No new semantic verifier, publication or
  release threshold is introduced. Research acceptance is not official release.
* Eight dependent root/variant pairs: jointly correct and label-consistent counts,
  exact correctness/label transitions. Stable wrong labels are not success.
* Paid input/output/cache usage, known token-priced cost, pessimistically reserved
  exposure and unknown billing; HTTP attempts vs logical slots. Monotonic provider,
  standard parsing and incremental C interpretation timings: p50/p95 and n. One
  post-freeze production checkpoint-control measurement is saved separately. B/C
  model cost and provider duration are shared; no independent C end-to-end claim.
  Setup/canonical QA is separate from recurring operation. Raw ledger retains IDs,
  request/response hashes, server model identity, usage, stop reasons and failures.

## Fixed controls and material findings

Freeze 26 pre-spend offline probes: six artifact families each with one clean mate
and two corruptions (12 faults +6 cleans), two shared pre-execution families each
with one clean mate and two faults (4+2), and two full-bound technically valid but
semantically wrong negative controls. offline_controls.py specifies all mutations
and imports actual production entry points. No network may run. The primary artifact
summary is paired invalid accepted among the 12 and false blocks among the six,
shown by family. Pre-execution and semantic probes are separate; no p-value or
production-prevalence estimate is made from the synthetic challenge mixture.
A confirmed bypass of an EXISTING mandatory control, or its matched clean rejection,
ends the mission before spending. Missing optional capabilities are stated as such.

## Freeze and roadmap

Code, data, oracle, requests, analysis, fixture definitions/results, schedule and this
protocol are frozen before any generation. The code commit precedes the separate
preregistration/authorization commit recorded in the external lease, avoiding circular
hashes. Existing protected files are checked against the starting snapshot, with only
the two disclosed registration/dispatch infrastructure additions excluded. No source,
gold, prompt, endpoint or scientific logic edit is allowed after first paid output.
Raw artifacts + ledger are frozen, budget revoked, analysis run twice for identical
outputs, history rechecked, full delivered-state suite run after revocation, and local
results committed. No push/publication. Reporting-only corrections must be disclosed.

Coordinator research screen: complete provenance/no leakage/reproducible analysis,
QA and historic integrity, zero budget; C at least 18/24 and at least 3/6 per class;
at most one net extra error versus A; at most one solid false endorsement /18 and
at most one extra versus A; no mandatory-control bypass or matched false block;
cap and overhead reported. Positive/significant gain is NOT required for bounded
research continuation. No gain does not prove equivalence. Recommendations are
exactly GO TO PHASE 8, REPAIR SPECIFIC BLOCKER, or ONE SMALL ADDITIONAL EXPERIMENT
REQUIRED, pending independent coordinator review. Do not start Phase 8 or run more
models. Carry historical NEU-002/PRT-02 regression and model-sensitivity limits forward.

## Pre-spend gate correction, retained initial freeze

The first registered preflight at 1a4950f803c847a5107f4f5badfbf1ee0b128e53
selected the older condition QA profile in the NEW mission adapter. Its tests all
passed (313/313), but its fixed historical expectation is 312. No provider was
constructed, no lease was created and no generation was attempted. A focused offline
diagnostic established that the existing current full-replication profile includes
the same tests plus production preflight/full-contract checks and correctly expects
369. The extra provider-runtime test dates to f5eabe94ee10af835f4e40b38f8f7f3e687cf96d.
No existing QA profile, expectation, validator, scientific prompt or endpoint changes.
The new adapter now calls that existing 369-test executor/validator. Its early failure
path also preserves QA evidence and revokes active authorization before rethrowing;
a fake failing-gate test proves zero provider constructions and zero remaining budget.
The initial freeze/authorization/log are preserved under evidence/initial_preflight_20260913.
The same mission is refrozen before its first paid request, while its authorization
is non-executable during correction; no terminal key or consumed lease is bypassed.
This is the final bounded new-adapter preflight correction, not a scientific repair.
