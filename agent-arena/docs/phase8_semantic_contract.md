# Phase 8: normative semantic contract

Contract **AA-P8/1.0** — frozen after one pre-implementation critique, 2026-09-30.
Canonical numbering: supplied Master Blueprint, revision 2026-09-30. This document,
`phase8_review_journal.md` and `phase8_closeout.md` are the only task documents.
No model efficacy experiment, historical relabeling, release or Phase 9/10 work.

## Scientific and technical boundary (8.1)

A claim is the captured original assertion, preserved verbatim in existing
`ClaimProvenance`. A proposition is one separately auditable assertion anchored
to that claim. A material/required proposition is necessary to the original
claim's actual logical expression; optional context cannot supply its proof.
Materiality and alternatives follow the original, never observed test outcomes.
A composite expresses AND/OR over propositions, including nested alternatives.

An evidence object is a source-bound observation, reusing `QAEvidenceItem` and
its source, role, exact reference, value origin and derivation lineage. Support
means the available evidence can support this exact proposition with its stated
scope and inference; it does not assert universal truth. Contradiction requires
relevant evidence in conflict with the proposition, not lack of support.
Unsupported means a represented, executed assessment establishes an unmet
evidence requirement. Unknown means available information does not resolve the
assessment; it is neither support nor contradiction. All retain reasons.

Directness describes the evidence-to-proposition correspondence, not overall
study quality: direct / partial / indirect / remote / unknown. Capability is
separate: descriptive, association, mechanism, causal effect or human clinical
benefit, limited by the actual population, intervention, endpoint and design.
A high-quality mouse experiment can directly support a mouse mechanism, yet
cannot alone establish human benefit. A randomized human surrogate result is
not automatically clinical efficacy. An observational design alone supports
association, not a causal conclusion. A documented independent causal bridge
must resolve to actual evidence; a model's assertion of a bridge is insufficient.

An inference bridge links premise propositions, a conclusion and its evidence.
Mechanism-to-outcome requires a bridge only when that inference is claimed;
mechanism-only claims need no clinical evidence. Bridge states: supported,
partial, unsupported, unknown. Product transfer states: direct_match,
supported_transfer, unsupported_transfer, unknown_transfer. Supported transfers
require explicit evidence for the actual entity/dose/formulation/route change.

The deterministic system validates represented attributes, references, source
spans, capability constraints, logic and transformations. It cannot prove that
model extraction covered every real material claim, correctly understood a
source or chose the correct scientific interpretation. Source quote containment
is necessary but does not prove entailment. These limits must appear in output.
No confidence value overrides missing controls, semantic limits or UNKNOWN.

## Execution, preservation and aggregation (8.2, 8.9, 8.12)

Technical status is `completed`, `not_executed` or `incomplete`; scientific state
is separately `supported`, `unsupported`, `contradicted` or `unknown`. Missing
legacy analysis is not_executed. Invalid schema/references, duplicate IDs,
truncated/repaired incomplete payload, empty required set or omitted declared
required component is incomplete, with unknown derived decision and reasons.
An executed assessment may legitimately conclude unknown without being a
technical failure. Unknown must remain visible in JSON and human output.

Original model label, original proposition verdicts and raw response are never
rewritten. Derived proposition states, composite and taxonomy corrections are
separate. Repaired analyses and normalized identifiers record their provenance.
Stable IDs are claim-bound and deterministic; original spans are checked against
captured claim text. IDs, parent provenance and evidence references must resolve.

No numeric label or scientific-state ranking. For a valid nonempty logical tree:

| Operator | Conditions, in decision order | Derived state |
|---|---|---|
| AND | any contradicted child | contradicted |
| AND | otherwise any unknown child | unknown |
| AND | otherwise any unsupported child | unsupported |
| AND | otherwise all supported | supported |
| OR | any supported child | supported |
| OR | otherwise any unknown child | unknown |
| OR | otherwise any unsupported child | unsupported |
| OR | otherwise all contradicted | contradicted |

All required propositions must occur in the logical tree; optional context
cannot appear as a substitute proof leaf. Invalid/empty trees never use these
truth tables. Individual component states always remain available, including
unknown alternatives in a supported OR. Mixed/partial evidence is represented
by those components/reasons, not by an invented ordering of taxonomy labels.

## Fidelity and allowed inference (8.3–8.8)

Record relevant population (species and material subgroup), intervention/entity,
dose, formulation, route, comparator, endpoint/type, relation/causal strength,
effect direction/magnitude/relative-or-absolute basis, follow-up and certainty.
Unknown values stay unknown; explicit not-applicable is permitted with a reason,
not silently imputed. Comparisons apply to the dimensions material to the
proposition. Broadening populations, replacing endpoints, losing comparators,
ingredient-to-product changes, short-to-long follow-up, inflated magnitude and
relative-to-absolute reinterpretation require supported, source-bound bridges.
An unexplained mismatch cannot support the stronger target proposition.

Use a small capability map: descriptive/report evidence -> description;
observational evidence -> association; mechanistic/in-vitro/animal evidence ->
mechanism or description in the represented setting; controlled intervention ->
at most causal effects on studied endpoints/populations. These are capability
ceilings, not automatic permissions: causal identification must be established
by represented randomized design or an explicit, source-bound identification
argument, with the matching comparison and no unresolved design limitation.
A nonrandomized/confounded controlled intervention alone does not suffice.
Human clinical benefit additionally
requires human clinical/functional/symptom outcome evidence with the relevant
intervention/comparator. Reviews/assessments must expose the capability of their
underlying material, never obtain unconditional support from their name.
Unknown design/capability is unknown, not automatic support. A source can bind
directly to one proposition and indirectly to another; directness lives on each
binding. Within-arm change alone cannot demonstrate a between-arm effect.

Preserve distinct observations: no_evidence_found, search_incomplete,
no_effect_observed, contradiction, inconclusive, unknown. No found evidence is
limited to a substantiated existing SearchScope. No significant effect is not
proof of zero effect. Conflict does not become a one-sided support verdict.
Known common study/cohort/dataset IDs mark dependence; missing identifiers mean
unknown dependence. Duplicate/dependent evidence cannot create independent
corroboration. No statistical independence or efficacy score is inferred.

| Material binding/bridge assessment | Proposition decision constraint |
|---|---|
| Required execution/schema/reference absent or invalid | technical incomplete; derived unknown |
| Material attribute/identification/transfer unresolved | executed unknown; never support from this binding |
| Known mismatched scope or unsupported inference/transfer | unsupported by this binding |
| Bridge partial or unknown with no sufficient alternative | unknown; partial bridge is not full support |
| Bridge unsupported | unsupported conclusion unless separate direct capable evidence resolves it |
| Relevant capable contradictory evidence only | contradicted |
| Relevant capable supporting and contradictory evidence | unknown, explicit conflict |
| Only no-effect-observed / inconclusive evidence | unknown for a claimed effect or zero effect |
| Capable direct support and all material requirements resolved | supported |

Reasons from all bindings remain visible. An irrelevant/incapable contrary item
is not a contradiction; an extra irrelevant source does not cancel independent
direct capable support. A required bridge is evaluated for the actual inference,
and its evidence must satisfy the conclusion's material requirements.

## Trace, transformations and actual processing (8.10–8.12)

Trace: unchanged claim -> proposition -> search question -> reviewed/search
scope -> source -> evidence -> per-binding semantic match/directness/capability
-> inference/bridge -> proposition verdict -> composite -> output assertion.
Search questions and transformations preserve their own text and semantic
attributes with from/to references. Check hedge removal/certainty escalation,
population/endpoint/comparator/effect/entity/relation/time changes and
partial-to-whole promotion. Narrow interpretations retain original and lineage.
Final summaries bind to the assessed propositions and derived state; a label or
free-text assertion cannot promote unknown or partial evidence to full support.

Implementation must connect the existing runner, structured parser, evaluator,
library record and existing renderers. Add a new versioned prompt/schema rather
than changing frozen historical/prospective experiment prompt bytes. Preserve
explicit historical benchmark paths and scoring, but mark their Phase-8 status
not_executed; they cannot claim Phase-8 completion. New internal analysis uses
the Phase-8 prompt and emits the structured analysis and derived assessment.
Malformed or missing payloads remain visible failures, including direct/manual
legacy report inputs. Existing alternate paths must not drop the assessment.

Offline provider fakes must consume the actual prompt and serialize raw JSON,
then exercise parser -> source/evidence binding -> guards -> derived decision ->
existing output. Source and claim spans are checked against host-captured input,
not against a model-invented second source. This does not validate semantic
extraction accuracy. Reuse all five Phase-7 controls (binding, strength, symmetry,
value origin, search scope); close only minimal relevant empty-check/wiring gaps.
Optional inapplicable controls must not force every legitimate input to unknown.
The adapter computes applicability from actual objects/assertions, not a model
opt-out flag, and records executed/eligible/not_applicable plus reasons for all
five controls. Required provenance/finding/output populations cannot be empty.
Zero quantitative or negative assertions can legitimately make the corresponding
control inapplicable. Do not weaken the existing official Phase-7 release policy.

## CvC precedence (additional WP-8.3)

Taxonomy source: `docs/study_forensics_taxonomy.md` and `taxonomy_precedence.md`.
CvC requires a causal assertion from noncausal/uncontrolled/confounded evidence
AND that this is the core error. ME requires a described biological mechanism
used to imply unsupported human clinical benefit AND core-error relevance.
Shape-B surrogate inflation remains overclaim; honest limited reporting may be
solid. Established causation plus excessive magnitude/population/endpoint scope
is not automatically CvC. Preserve original label separately from any derived
correction. Unknown triggers do not justify deterministic relabeling.

Existing reported clusters must be checked against their actual summaries and
current taxonomy; historical changed expectations are not new regressions.
Prompt, parser and deterministic contributions are reported separately. No
case-ID rules, new gold or claims of measured live-accuracy improvement.

## Criteria map, ownership and predeclared acceptance pairs (8.13–8.14)

| Canonical point | WP and required evidence |
|---|---|
| 8.1 normative contract | this versioned contract, pre-implementation critic review |
| 8.2 ledger | WP1: original bytes/spans, stable IDs, states, references, materiality |
| 8.3 fidelity | WP2: dimensions above and missing/mismatch controls |
| 8.4 typing | WP2: minimal capability-bearing evidence types |
| 8.5 directness × capability | WP2: distinct fields and same-source/two-proposition test |
| 8.6 mechanism bridge | WP2: source-bound bridge and mechanism-only valid control |
| 8.7 product transfer | WP2: identity/dose/formulation mismatch and supported transfer |
| 8.8 negatives | WP2: all distinct observation states, search and null-error controls |
| 8.9 composite | WP1: table above, missing/empty/optional/nested alternative controls |
| 8.10 trace | WP2 + integration: full raw-input to existing-output path |
| 8.11 transformations | WP2: hedge/certainty/scope/endpoint/partial-whole audit |
| 8.12 UNKNOWN | WP1/2: separate technical status, scientific state and visible output |
| 8.13 validation corpus | all WPs: small synthetic development and acceptance suites |
| 8.14 closeout | final full suite, no unresolved material finding, honest report |

All rows are required; none deferred. Only full ontologies, seven product-transfer
classes, broad statistics, standalone negative-evidence modules, Phase 9/10 and
final model efficacy/holdout experiments are deferred. Existing Phase-7 facilities
count as reused only after their relevant regression checks pass.

Predeclared failure/valid pairs: missing required conjunct/full conjunction;
unsupported alternative/one supported OR; absent/empty ledger/valid single claim;
wrong evidence proposition/correct binding; animal-to-human/mouse mechanism;
biomarker-to-event/honest biomarker claim; observational causality/association;
ingredient-to-product/same entity or evidenced transfer; subgroup-to-all/same
population; mismatched/matched comparator; short-to-long/matched follow-up;
relative-to-absolute/same effect basis; inflated/matched magnitude;
within-arm-as-between/actual between comparison; incomplete search/documented
bounded no-find; nonsignificance-as-null/honest no-effect-observed statement;
conflicting/direct consistent evidence; duplicated study/known distinct studies;
unknown dependence/explicit known dependence; dropped hedge/preserved hedge;
certainty escalation/narrow interpretation with provenance; missing clinical
bridge/evidenced bridge; generic overclaim falsely labeled CvC/legitimate CvC;
surrogate falsely ME/genuine biological ME; absent legacy payload/full real-path
fake output; high confidence cannot rescue any mandatory failure.

Coordinator owns existing-file integration, prompt, parser, output and three
documents. Implementer exclusively owns new `phase8_models.py`,
`phase8_semantics.py` and `tests/test_phase8_semantics.py` until handed back.
Critic is read-only; all shared test runs coordinated. Exactly these two roles
are reused. Each WP gets one first code/test review and at most two targeted
correction/rechecks; unresolved material errors after that mean BLOCKED.

Acceptance rules/expected decisions are frozen before acceptance execution;
development regressions and a separate compact acceptance suite remain separate
from final efficacy holdout. No retrospective criterion/gold/materiality changes
to obtain PASS. Genuine contract corrections need rationale, version increment
and affected revalidation in the journal. After integration run relevant Ruff,
available type/compile checks and the complete test suite; record actual commands,
counts and failures. A green helper suite alone cannot close Phase 8.
