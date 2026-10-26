# Phase-5A condition-aware scientific contract

Status: **PROPOSED · NOT_AUTHORIZED_FOR_REAL_EXECUTION · NOT_EXECUTED**

This directory defines the prospective, matched old-versus-revised Study
Forensics validation specification. It does not authorize a provider call and
is not a Phase-8 artifact.

## State separation

The implementation keeps five states separate:

1. **Execution specification** — immutable plan, units, prompt conditions,
   models, repetitions, QA specification, namespaces and exact call plan.
2. **Execution authorization** — tracked governance state referring to the
   exact specification fingerprint. The committed state authorizes zero calls.
3. **Execution progress** — `NOT_EXECUTED`, `PARTIAL` or `COMPLETE`; excluded
   from immutable specification identity.
4. **Analytical completeness** — terminal, classification-valid and
   calibration-valid accounting derived from records; completion alone does not
   establish it.
5. **Release authorization** — separately evaluated Phase-7B gates and release
   boundary. Diagnostic validation artifacts are not release sources.

`NOT_EXECUTED` is a legitimate progress state. A later approved specification
could become executable after fresh preflight without changing its scientific
identity. Conversely, a completed artifact is neither authorized nor releasable
merely because it is complete.

## Fingerprint payloads

Every fingerprint is SHA-256 over canonical JSON (sorted keys, UTF-8, compact
separators). A fingerprint field is added only after its payload is hashed and
is excluded when reproduced.

- **Package:** package schema; prompt condition and version; exact system-prompt
  hash; packet descriptor version/hash; output-contract identity/hash.
- **Condition runtime contract:** runtime schema/ID; dated model and tracked
  config identity/hash; prompt/package identity; frozen transport, sampling,
  retry and parser-failure semantics. Actual source commit/environment is not
  embedded here.
- **Execution manifest:** plan/arm/analytical condition; prompt/package;
  ordered complete unit metadata and fingerprints; data role; execution mode;
  artifact namespace.
- **Call plan:** plan/arm/condition; dated models; repetitions; independent-unit
  count; exact slot-universe fingerprint over `(model, unit, repetition)`;
  transport-retry exposure; package/runtime/manifest fingerprints.
- **Arm specification:** the complete package, runtime, manifest and call-plan
  identities for one prompt condition.
- **Paired specification:** research question, fixed selection rule and strata,
  both arm specifications, models, repetitions, QA specification, analysis
  contract and call accounting. Authorization and progress are excluded.
- **Checkpoint:** the immutable plan/arm fields above plus actual authenticated
  source/environment, provider-runtime, storage namespace and exact expected
  slots. Every new-schema record repeats the material plan/condition bindings.

Fresh QA provenance and the actual execution source/commit/environment remain
separate runtime bindings. This avoids a committed plan containing the hash of
the commit that contains itself. Changing progress does not change the paired
specification or invalidate its own checkpoints.

## Trusted selection boundary

Production accepts only `plan_id`, `arm_id` and `model_key`. The plan ID resolves
through the internal registry to the fixed tracked JSON file. Prompt text,
units, repetitions, runtime contracts, fingerprints, approval state, QA scope
and provider factories are not accepted from production callers.

The committed plan contains `NOT_AUTHORIZED_FOR_REAL_EXECUTION`, an authorized
budget of zero and no tracked governance approval. Tests can use the private
synthetic seam with local counting/request-capture providers; that seam is not
exposed by the production API.

## Fixed validation proposal

- Models, pending later availability verification:
  `claude-haiku-4-5-20251001` and `claude-sonnet-4-5-20250929`.
- Prompt conditions: contemporary execution of the immutable historical prompt
  and the taxonomy-aligned prospective prompt. Historical Phase-7 responses are
  reference data, not the contemporary control arm.
- Units: 19 active, historically exposed Phase-7A Class-B independent bases.
  Nested perturbation variants, retired cases and holdout material are excluded.
- Strata: 4 genuine ME/OV overlaps; 3 ME-specific controls; 4 Shape-B controls;
  4 nonmechanistic OV controls; 4 solid/CvC controls.
- Repetitions: 3 per model, prompt condition and unit. Repeated responses are not
  counted as independent scientific units.
- Call budget: `2 models × 2 prompt conditions × 19 units × 3 repetitions = 228`
  analytical calls.
- Retry exposure for the fixed four-invocation schedule: 228 analytical slots;
  at most 3 provider-method invocations per slot under the existing outer
  provider-error pass loop (684 provider-method invocations); and at most 3 HTTP
  attempts per provider-method invocation under the existing SDK transport
  policy (2,052 HTTP attempts). These are distinct quantities. The full layer
  table, reset scopes and derivation are frozen in the plan. Semantic/quality
  retries remain prohibited.
- The 2,052 HTTP figure is finite only for one guarded invocation of each of the
  four model/arm batches. Checkpoint reuse prevents terminal slots from being
  called again, but there is no persistent attempt/spending counter for repeated
  later invocations of authenticated nonterminal failures. Any such invocation
  is outside this schedule and requires separately reviewed execution
  authorization and budget.
- Artifact namespaces: separate contemporary-historical and taxonomy-aligned
  namespaces defined in the plan; their records and analyses cannot pool.
- Primary denominator: 8 independent units across the genuine-overlap and
  Shape-B strata, reported separately per model and stratum.
- Response-level accuracy/calibration denominators remain separate and explicitly
  exclude only responses that the existing contracts classify as ineligible.
- Analysis uses classification-valid votes only: a unit resolves only with at
  least two matching labels among the three planned slots. Gold is consulted
  only after response-only aggregation. Ties and insufficient votes are
  unresolved; raw labels, missingness and validity states remain visible.
- Unit scoring reports the fixed-denominator coverage-adjusted correct-unit
  rate separately from accuracy among resolved units. Classification,
  calibration and transport/missingness completeness are distinct. The exact
  Brier/ECE implementations, denominators, mutually exclusive directional
  verdict order, paired-transition exclusions and stopping rules are frozen in
  `paired_prompt_validation_plan.json` and executable in
  `agent_arena.condition_analysis`.
- Current model availability and pricing: **UNKNOWN**, requiring a separately
  authorized pre-execution check. No cost figure is inferred without a current
  approved price source and token estimate.

No prompt tuning, unit replacement, added repetition or semantic rerun is
permitted after new responses are observed. An adverse or inconclusive outcome
must remain reportable.
