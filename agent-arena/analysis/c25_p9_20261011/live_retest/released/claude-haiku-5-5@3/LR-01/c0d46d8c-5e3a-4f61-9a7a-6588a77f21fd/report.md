# Canonical local audit

## Execution and release

RELEASED — local artifact status

LIVE MODEL GENERATION (AA-P10-LIVE/1.0). Actual provider calls produced the analysed responses; model, request IDs, attempts and cost are bound below and in record.json. Local artifact decision only; no scientific truth, empirical validation, external evidence search or customer approval.

### Independent states

| Field | Recorded value |
| --- | --- |
| analysis execution | completed |
| host evidence derivation (composite) | supported |
| local release | RELEASED |
| mandatory review | false |
| model judgment (composite) | supported |
| model/host conflicts | none recorded |
| review execution | not&#95;executed |
| review route | AUTO&#95;RESOLVABLE |
| scientific judgment | supported |

### Explicit release intent

| Field | Recorded value |
| --- | --- |
| reason | AA-P10 live retest LR-01&#58; technical release-path check on a synthetic sketch case (not a real study, no gold label) |
| reviewer | TEST ONLY - not a scientific release |
| scope | local&#95;artifact&#95;only |

### Revision identity

| Field | Recorded value |
| --- | --- |
| created at | 2026-10-12T15&#58;15&#58;24.415952+00&#58;00 |
| parent / manifest fingerprint | 3a9c02b4802eef54f65673380ca779a6bab900c1a452b691c0e0da0155177996 |
| parent / revision id | 2b3197b1-8a36-454c-af11-68bbd343d03a |
| record fingerprint | b8c15b63821a1cbc07b28e45fd3c15a459b638e2597f99c7d938028b86194279 |
| revision | c0d46d8c-5e3a-4f61-9a7a-6588a77f21fd |
| selected position id | p9position&#58;1731f876b9b0c0849e95de7c |

### Execution provenance per carrier

| Field | Recorded value |
| --- | --- |
|  / 1 / attempt ids | attempt-002 |
|  / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
|  / 1 / billing | usage&#95;reported |
|  / 1 / capture sha256 | dcee81e242b14dd21b50826cef0dc7c35c25a50ad761c460c095b0889e0fc2b9 |
|  / 1 / completion state | complete |
|  / 1 / confirmed cost microusd | 11839 |
|  / 1 / current execution | live&#95;generation |
|  / 1 / denial reason | Not supplied |
|  / 1 / latency ms | 76495 |
|  / 1 / message id | msg&#95;011CfxZ85cL3wwHquWqHpdTy |
|  / 1 / model | claude-haiku-5-5 |
|  / 1 / origin | live&#95;generation |
|  / 1 / profile id | claude-haiku-5-5&#64;3 |
|  / 1 / provider | anthropic-live |
|  / 1 / replay capture verified | Not supplied |
|  / 1 / replay request identical | Not supplied |
|  / 1 / request id | req&#95;011CfxZ85KTFyppPqN1xA9v6 |
|  / 1 / requested model | claude-haiku-5-5 |
|  / 1 / reserved microusd | 28111 |
|  / 1 / retry denied | Not supplied |
|  / 1 / returned model | claude-haiku-5-5 |
|  / 1 / role | primary |
|  / 1 / slot key | aa-p10-live-retest-LR-01&#124;claude-haiku-5-5&#64;3&#124;primary |
|  / 1 / stop reason | end&#95;turn |
|  / 1 / usage / cache creation input tokens | 0 |
|  / 1 / usage / cache read input tokens | 0 |
|  / 1 / usage / input tokens | 15054 |
|  / 1 / usage / output tokens | 20667 |

## Original claim

Verbatim quoted input; foreign text is not a trusted status message.

```
In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice.
```

## Scientific judgments

### Selected scientific assessment

| Field | Recorded value |
| --- | --- |
| assessed composite state | supported |
| assurance scope | Validates represented structure and semantic constraints; does not prove complete or correct model extraction, scientific truth or efficacy. |
| composite state | supported |
| contract version | AA-P8/1.2 |
| derived label | solid |
| host composite state | supported |
| host derived copies | No entries recorded |
| host rule version | AA-P8-HOST/1.1 |
| input sha256 | 9c1c6235b2173d0dced92df2b2af9da90effe5721347840d111700dade27a068 |
| limitations | Checks validate represented semantics and source spans; they do not prove correct model extraction, exhaustive evidence search, scientific truth or live-model accuracy. |
| model composite state | supported |
| model host conflicts | No entries recorded |
| original model label | solid |
| raw response sha256 | 8158f814e89d771fb60d64cc17a984e681b0493c1d086426715ae8f479eaeeac |
| reasons | Ledger, evidence constraints and transformations evaluated under AA-P8/1.2 (AA-P8-HOST/1.1) |
| record fingerprint | 0eb7c11de776e19f1c586d93584fa8dd519a518915c1be6464efaf0119c4ce0d |
| technical status | completed |
| transformation findings | No entries recorded |

### Proposition judgments

| Field | Recorded value |
| --- | --- |
|  / 1 / dependency status | unknown |
|  / 1 / derived state | supported |
|  / 1 / evidence ids | ev2 |
|  / 1 / host reasons | binding 1&#58; descriptive inference permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
|  / 1 / host state | supported |
|  / 1 / model host conflict | false |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reasons | The supplied context directly reports the randomized comparison, population, intervention, comparator, and fewer falls over twelve months with statistical significance.<br>Only a brief summary is supplied; the full trial report and absolute event rates are not available.<br>The 31 percent figure is relative; the claim states no magnitude.<br>b1&#58; The context directly reports 31 percent fewer falls over twelve months in the balance-training arm than in the general advice arm, with statistical significance, matching the claim&#x27;s population, intervention, comparator, endpoint, and direction.<br>descriptive inference permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
|  / 1 / reported verdict | supported |
|  / 1 / required | true |

## Original label and taxonomy

### Original versus derived classification

| Field | Recorded value |
| --- | --- |
| derived taxonomy | solid |
| original model label | solid |
| represented trigger analysis / causal claim | false |
| represented trigger analysis / core error | none |
| represented trigger analysis / described biological mechanism | false |
| represented trigger analysis / evidence ids | ev2 |
| represented trigger analysis / implies human benefit | false |
| represented trigger analysis / noncausal result used | false |
| represented trigger analysis / proposition ids | claim&#58;p1 |
| represented trigger analysis / reason | The claim reports an observed between-group falls comparison from a randomized trial; it asserts no causal relation, mechanism, or human benefit beyond that comparison, so no taxonomy error is triggered. |
| represented trigger analysis / trigger evidence id | ev2 |
| represented trigger analysis / trigger proposition id | claim&#58;p1 |
| represented trigger analysis / trigger quote | had fewer falls over twelve months than those assigned to general health advice |
| taxonomy check / assurance scope | Taxonomy decisions check represented trigger, core-error and evidence/proposition consistency. Quote containment does not prove entailment or correct model interpretation. |
| taxonomy check / derived label | solid |
| taxonomy check / reasons | Honest reporting with supported represented propositions |
| taxonomy check / technical status | completed |

## Propositions and inference limits

### Claim composition

| Field | Recorded value |
| --- | --- |
| claim id | claim |
| extraction provenance | Single required proposition extracted from the task prompt; the full claim wording is retained unchanged. |
| logic / children | No entries recorded |
| logic / operator | leaf |
| logic / proposition id | claim&#58;p1 |
| provenance id | prov1 |
| required proposition ids | claim&#58;p1 |

### Proposition claim&#58;p1

| Field | Recorded value |
| --- | --- |
| derived judgment / dependency status | unknown |
| derived judgment / derived state | supported |
| derived judgment / evidence ids | ev2 |
| derived judgment / host reasons | binding 1&#58; descriptive inference permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
| derived judgment / host state | supported |
| derived judgment / model host conflict | false |
| derived judgment / proposition id | claim&#58;p1 |
| derived judgment / reasons | The supplied context directly reports the randomized comparison, population, intervention, comparator, and fewer falls over twelve months with statistical significance.<br>Only a brief summary is supplied; the full trial report and absolute event rates are not available.<br>The 31 percent figure is relative; the claim states no magnitude.<br>b1&#58; The context directly reports 31 percent fewer falls over twelve months in the balance-training arm than in the general advice arm, with statistical significance, matching the claim&#x27;s population, intervention, comparator, endpoint, and direction.<br>descriptive inference permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
| derived judgment / reported verdict | supported |
| derived judgment / required | true |
| material dimensions | population<br>intervention<br>comparator<br>endpoint<br>endpoint&#95;type<br>relation<br>follow&#95;up<br>comparison |
| materiality | required |
| not applicable / certainty | The claim makes no certainty or strength statement; the falls comparison is assessed as an observed result. |
| observation target | support |
| parent claim id | claim |
| premise proposition ids | No entries recorded |
| proposition id | claim&#58;p1 |
| provenance id | prov1 |
| reason | The supplied context directly reports the randomized comparison, population, intervention, comparator, and fewer falls over twelve months with statistical significance. |
| reported verdict | supported |
| required bridge ids | No entries recorded |
| search question | Does the supplied material report that, in a randomized trial of community-dwelling adults aged 70 and older, the home-based balance training group had fewer falls over twelve months than the general health advice group? |
| search scope ids | scope1 |
| uncertainty | Only a brief summary is supplied; the full trial report and absolute event rates are not available.<br>The 31 percent figure is relative; the claim states no magnitude. |

Quoted proposition; this is represented input, not a release assertion.

```
In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice.
```

### Original span

| Field | Recorded value |
| --- | --- |
| end | 197 |
| start | 0 |
| text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |

### Population, endpoint, product and inference attributes

| Field | Recorded value |
| --- | --- |
| certainty | Not supplied |
| comparator | general health advice |
| comparison | between |
| dose | Not supplied |
| effect basis | Not supplied |
| effect direction | Not supplied |
| effect magnitude | Not supplied |
| endpoint | falls |
| endpoint type | event&#95;count |
| follow up | twelve months |
| formulation | Not supplied |
| intervention | home-based balance training program |
| population | community-dwelling adults aged 70 and older |
| relation | description |
| route | Not supplied |
| species | human |

### Evidence bindings and directness

| Field | Recorded value |
| --- | --- |
|  / 1 / binding id | b1 |
|  / 1 / directness | direct |
|  / 1 / evidence id | ev2 |
|  / 1 / observation | support |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reason | The context directly reports 31 percent fewer falls over twelve months in the balance-training arm than in the general advice arm, with statistical significance, matching the claim&#x27;s population, intervention, comparator, endpoint, and direction. |
|  / 1 / search scope id | scope1 |

### Bridges

| Field | Recorded value |
| --- | --- |
| Value | No entries recorded |

### Product Transfers

| Field | Recorded value |
| --- | --- |
| Value | No entries recorded |

### Transformation t1

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | Not supplied |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / dose | Not supplied |
| from and to attributes (identical) / effect basis | Not supplied |
| from and to attributes (identical) / effect direction | Not supplied |
| from and to attributes (identical) / effect magnitude | Not supplied |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | event&#95;count |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / formulation | Not supplied |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | description |
| from and to attributes (identical) / route | Not supplied |
| from and to attributes (identical) / species | human |
| from and to text (identical) | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| from proposition ids | claim&#58;p1 |
| reason | Extraction keeps the full claim as one proposition with unchanged wording and attributes. |
| stage | extraction |
| target id | claim&#58;p1 |
| transformation id | t1 |

### Transformation t2

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | Not supplied |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / dose | Not supplied |
| from and to attributes (identical) / effect basis | Not supplied |
| from and to attributes (identical) / effect direction | Not supplied |
| from and to attributes (identical) / effect magnitude | Not supplied |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | event&#95;count |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / formulation | Not supplied |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | description |
| from and to attributes (identical) / route | Not supplied |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| reason | The search question restates the claim as a question over the supplied reviewed set without changing attributes. |
| stage | search&#95;question |
| target id | claim&#58;p1 |
| to text | Does the supplied material report that, in a randomized trial of community-dwelling adults aged 70 and older, the home-based balance training group had fewer falls over twelve months than the general health advice group? |
| transformation id | t2 |

### Transformation t3

| Field | Recorded value |
| --- | --- |
| asserted state | supported |
| asserts whole claim | true |
| from and to attributes (identical) / certainty | Not supplied |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / dose | Not supplied |
| from and to attributes (identical) / effect basis | Not supplied |
| from and to attributes (identical) / effect direction | Not supplied |
| from and to attributes (identical) / effect magnitude | Not supplied |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | event&#95;count |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / formulation | Not supplied |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | description |
| from and to attributes (identical) / route | Not supplied |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| reason | The internal finding states the supported verdict for the whole single-proposition claim, consistent with the reported verdict and whole-claim judgment. |
| stage | internal |
| target id | claim&#58;p1 |
| to text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice.<br>Supplied context reports a randomized comparison with 31 percent fewer falls over twelve months and a statistically significant difference. |
| transformation id | t3 |

### Transformation t4

| Field | Recorded value |
| --- | --- |
| asserted state | supported |
| asserts whole claim | true |
| from and to attributes (identical) / certainty | Not supplied |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / dose | Not supplied |
| from and to attributes (identical) / effect basis | Not supplied |
| from and to attributes (identical) / effect direction | Not supplied |
| from and to attributes (identical) / effect magnitude | Not supplied |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | event&#95;count |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / formulation | Not supplied |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | description |
| from and to attributes (identical) / route | Not supplied |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| reason | The client summary keeps the supported verdict and the observed comparison without adding causal, mechanistic, or benefit language. |
| stage | summary |
| target id | client&#58;c1 |
| to text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice.<br>The supplied trial summary reports 31 percent fewer falls over twelve months in the home-based balance training group than in the general health advice group, with a statistically significant difference. |
| transformation id | t4 |

## Evidence and source quotations

Quotations are supplied source text. Evidence type, direction and semantic attributes are represented extraction; the checks do not authenticate study findings.

### Evidence ev1

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint |  |
| evidence id | ev1 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | supporting |
| source id | context |
| value origin | Not supplied |

Evidence text and exact source reference (identical)&#58;

```
Researchers randomly assigned community-dwelling adults aged 70 and older (600 in total) either to a home-based balance training program or to general health advice.
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / certainty | Not supplied |
| attributes / comparator | general health advice |
| attributes / comparison | between |
| attributes / dose | Not supplied |
| attributes / effect basis | Not supplied |
| attributes / effect direction | Not supplied |
| attributes / effect magnitude | Not supplied |
| attributes / endpoint | Not supplied |
| attributes / endpoint type | Not supplied |
| attributes / follow up | Not supplied |
| attributes / formulation | Not supplied |
| attributes / intervention | home-based balance training program |
| attributes / population | community-dwelling adults aged 70 and older |
| attributes / relation | description |
| attributes / route | Not supplied |
| attributes / species | human |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | Brief context statement only; allocation concealment and attrition are not described. |
| evidence id | ev1 |
| evidence type | controlled&#95;intervention |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | true |
| source role | trial design statement |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

### Evidence ev2

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint | falls |
| evidence id | ev2 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | 31 percent fewer falls |
| role | supporting |
| source id | context |
| value origin | source&#95;reported |

Evidence text and exact source reference (identical)&#58;

```
Over twelve months, community-dwelling adults aged 70 and older assigned to the home-based balance training program had 31 percent fewer falls than those assigned to general health advice, and the difference was statistically significant.
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / certainty | Not supplied |
| attributes / comparator | general health advice |
| attributes / comparison | between |
| attributes / dose | Not supplied |
| attributes / effect basis | Not supplied |
| attributes / effect direction | Not supplied |
| attributes / effect magnitude | Not supplied |
| attributes / endpoint | falls |
| attributes / endpoint type | event&#95;count |
| attributes / follow up | twelve months |
| attributes / formulation | Not supplied |
| attributes / intervention | home-based balance training program |
| attributes / population | community-dwelling adults aged 70 and older |
| attributes / relation | description |
| attributes / route | Not supplied |
| attributes / species | human |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | Single summary of the falls result; absolute event rates and the size of the relative effect&#x27;s confidence interval are not supplied. |
| evidence id | ev2 |
| evidence type | controlled&#95;intervention |
| identification argument | Researchers randomly assigned community-dwelling adults aged 70 and older (600 in total) either to a home-based balance training program or to general health advice. |
| identification evidence ids | ev1 |
| quality | Not supplied |
| randomized | true |
| source role | trial outcome result |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

## Search scope

External search executed&#58; false. Scope is limited to the captured supplied material; no evidence found does not mean no evidence exists.

### Declared search scopes

| Field | Recorded value |
| --- | --- |
|  / 1 / date cutoff | Not supplied |
|  / 1 / query terms | No entries recorded |
|  / 1 / resources | supplied task context |
|  / 1 / reviewed source ids | context |
|  / 1 / scope type | reviewed&#95;set |
|  / 1 / search completeness | supplied context only; no external search executed |
|  / 1 / search scope id | scope1 |

### Bound negative assertions

| Field | Recorded value |
| --- | --- |
| Value | No entries recorded |

Captured context (source&#95;id&#58; context)&#58;

```
Researchers randomly assigned community-dwelling adults aged 70 and older (600 in total) either to a home-based balance training program or to general health advice. The program consisted of three short sessions per week. Falls were counted in the same way in both groups. Over twelve months, community-dwelling adults aged 70 and older assigned to the home-based balance training program had 31 percent fewer falls than those assigned to general health advice, and the difference was statistically significant.
```

## Finding and client traces

### Provenance

| Field | Recorded value |
| --- | --- |
|  / 1 / canonical url | Not supplied |
|  / 1 / content fingerprint | Not supplied |
|  / 1 / context after | Not supplied |
|  / 1 / context before | Not supplied |
|  / 1 / exact claim text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
|  / 1 / page title | Not supplied |
|  / 1 / provenance id | prov1 |
|  / 1 / provenance state | archived&#95;snapshot |
|  / 1 / retrieved at | Not supplied |
|  / 1 / source id | input |

### Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / allowed summary strength | not&#95;assessed |
|  / 1 / confidence status | moderate; single brief context summary |
|  / 1 / contrary evidence ids | No entries recorded |
|  / 1 / finding id | claim&#58;p1 |
|  / 1 / predicted label | Not supplied |
|  / 1 / proposition | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
|  / 1 / provenance id | prov1 |
|  / 1 / supporting evidence ids | ev2 |
|  / 1 / verdict summary | Supplied context reports a randomized comparison with 31 percent fewer falls over twelve months and a statistically significant difference. |

### Client Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / client explanation | The supplied trial summary reports 31 percent fewer falls over twelve months in the home-based balance training group than in the general health advice group, with a statistically significant difference. |
|  / 1 / client finding id | client&#58;c1 |
|  / 1 / client negative assertions | No entries recorded |
|  / 1 / client strength | not&#95;assessed |
|  / 1 / display claim | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
|  / 1 / parent finding id | claim&#58;p1 |
|  / 1 / provenance id | prov1 |
|  / 1 / referenced evidence ids | ev2 |
|  / 1 / value claims / 1 / claimed origin | source&#95;reported |
|  / 1 / value claims / 1 / claimed source ids | context |
|  / 1 / value claims / 1 / evidence id | ev2 |

## UNKNOWN, conflicts and review history

### Current review state

| Field | Recorded value |
| --- | --- |
| assurance scope | Checks represented positions, identity, materiality and routing. No majority vote, scientific truth, reviewer independence or release authorization is inferred. |
| case id | p9case&#58;6b82f53b4d87ed01514ff065 |
| contract version | AA-P9/1.2 |
| execution status | not&#95;executed |
| mandatory | false |
| reasons | Routing preserves separate scientific/taxonomy layers; no majority or provider call executed |
| review state | not&#95;required |
| route | AUTO&#95;RESOLVABLE |
| technical status | completed |
| uncertainty | No entries recorded |

### Current revalidated assessment

| Field | Recorded value |
| --- | --- |
| assessment fingerprint | 687c1162a7260750e16e1fe64033b022e003de0acfc5ed3bc47451042d0f2007 |
| history validation | Not supplied |
| interpretation | Current revalidated state |
| route | AUTO&#95;RESOLVABLE |
| source reference | record.json&#35;/run&#95;record |
| technical status | completed |

### Position p9position&#58;1731f876b9b0c0849e95de7c

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;6b82f53b4d87ed01514ff065 |
| claim id | claim |
| complete analysis reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0 |
| derived taxonomy | solid |
| model | claude-haiku-5-5 |
| origin | original |
| original model label | solid |
| position id | p9position&#58;1731f876b9b0c0849e95de7c |
| provider | anthropic-live |
| raw response reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0/agent&#95;result/raw&#95;output |
| raw sha256 | 8158f814e89d771fb60d64cc17a984e681b0493c1d086426715ae8f479eaeeac |
| run id | 846890e3-418d-466c-b70d-a65a5ac797eb |
| scientific state | supported |
| selected | true |
| taxonomy status | completed |
| technical status | completed |

### Captured execution

| Field | Recorded value |
| --- | --- |
| error | Not supplied |
| error type | Not supplied |
| finish reason | stop |
| parse ok | true |
| usage / cache creation input tokens | 0 |
| usage / cache read input tokens | 0 |
| usage / input tokens | 15054 |
| usage / output tokens | 20667 |

Current assessment contains no recorded conflicts. This is not evidence of scientific truth.

No adjudication is recorded; absence is not human approval.

## Mandatory controls

### Executed controls

| Control and version | Execution, population and result |
| --- | --- |
| input&#95;preflight / 1.1 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Input and nonempty execution population checked |
| analysis&#95;source / 1.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Reparsed raw, supplied source spans and nonempty claim/evidence/output traces checked |
| finding&#95;artifact&#95;binding / 1.1.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Evaluated client&#95;findings |
| summary&#95;strength&#95;monotonicity / 1.0.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Evaluated client&#95;findings |
| evidence&#95;symmetry / 1.1.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Evaluated client&#95;finding&#95;material&#95;evidence&#95;contexts |
| value&#95;origin&#95;provenance / 1.0.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Evaluated client&#95;visible&#95;evidence&#95;references |
| search&#95;scope&#95;binding / 1.0.0 | Execution&#58; executed<br>Outcome&#58; not&#95;applicable<br>Eligible&#58; 0<br>Evaluated&#58; 0<br>Reason&#58; Host-derived N/A&#58; no client&#95;negative&#95;assertions; check executed successfully |
| phase8&#95;semantics&#95;taxonomy / 1.2 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Current semantic and separate taxonomy analysis required |
| phase9&#95;history&#95;review / 1.2 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; All original/review/adjudication carriers and mandatory review revalidated |
| provenance / live-1.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Current code bytes, task/raw/history/selected evidence and live execution evidence bound (AA-P10-LIVE/1.0) |

Final Markdown and HTML file checks read these actual files before promotion. Their results and exact hashes are bound in decision.json; this report does not self-certify its bytes.

### Post-render control references

| Control | Result reference | Population |
| --- | --- | --- |
| markdown&#95;qa | decision.json&#35;/controls | Actual rendered bytes |
| html&#95;qa | decision.json&#35;/controls | Actual rendered bytes |

## Limitations

Checks validate represented semantics and supplied source spans. Extraction correctness, exhaustiveness and scientific truth remain outside this assurance. Canonical PDF is unsupported.

Not supplied and No entries recorded describe missing fields, not proof of absence or not-applicability. Confidence cannot override missing mandatory evidence.

### Assessment limitations

| Field | Recorded value |
| --- | --- |
| Value | Checks validate represented semantics and source spans; they do not prove correct model extraction, exhaustive evidence search, scientific truth or live-model accuracy. |

## Provenance

### Material provenance

| Field | Recorded value |
| --- | --- |
| analysis fingerprint | 494efd70dbcd0017dc536d74a2626e7bfe0a29685e0528b00cb9dc6ed99800e9 |
| case id | p9case&#58;6b82f53b4d87ed01514ff065 |
| code / code fingerprint | a1654da6afd6991665f2e4d25824c4e21fc152d69eddef01fe9a9cacf64eb80d |
| code / complete module hash index | manifest.json&#35;/provenance/code/module&#95;hashes |
| code / module count | 74 |
| code / source binding | verified Git source bytes |
| code / verified source commit | 63399dd1c3093d21a9307630ba85a6f85e4fa450 |
| config | live-anthropic-v1 |
| contract | AA-P10/1.0 |
| contract addendum | AA-P10-LIVE/1.0 |
| evidence fingerprint | f57cbfcfb40c4df69fa7ec9f251193756e7c1c50b98a27134e966d953f49d4fc |
| execution evidence / 1 / attempt ids | attempt-002 |
| execution evidence / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
| execution evidence / 1 / billing | usage&#95;reported |
| execution evidence / 1 / capture sha256 | dcee81e242b14dd21b50826cef0dc7c35c25a50ad761c460c095b0889e0fc2b9 |
| execution evidence / 1 / completion state | complete |
| execution evidence / 1 / confirmed cost microusd | 11839 |
| execution evidence / 1 / current execution | live&#95;generation |
| execution evidence / 1 / denial reason | Not supplied |
| execution evidence / 1 / latency ms | 76495 |
| execution evidence / 1 / message id | msg&#95;011CfxZ85cL3wwHquWqHpdTy |
| execution evidence / 1 / model | claude-haiku-5-5 |
| execution evidence / 1 / origin | live&#95;generation |
| execution evidence / 1 / profile id | claude-haiku-5-5&#64;3 |
| execution evidence / 1 / provider | anthropic-live |
| execution evidence / 1 / replay capture verified | Not supplied |
| execution evidence / 1 / replay request identical | Not supplied |
| execution evidence / 1 / request id | req&#95;011CfxZ85KTFyppPqN1xA9v6 |
| execution evidence / 1 / requested model | claude-haiku-5-5 |
| execution evidence / 1 / reserved microusd | 28111 |
| execution evidence / 1 / retry denied | Not supplied |
| execution evidence / 1 / returned model | claude-haiku-5-5 |
| execution evidence / 1 / role | primary |
| execution evidence / 1 / slot key | aa-p10-live-retest-LR-01&#124;claude-haiku-5-5&#64;3&#124;primary |
| execution evidence / 1 / stop reason | end&#95;turn |
| execution evidence / 1 / usage / cache creation input tokens | 0 |
| execution evidence / 1 / usage / cache read input tokens | 0 |
| execution evidence / 1 / usage / input tokens | 15054 |
| execution evidence / 1 / usage / output tokens | 20667 |
| execution mode | live&#95;generation |
| execution mode errors | No entries recorded |
| input fingerprint | f7735b78812a479470bf2638cbfc96c69876efbafe86cf6e4944fb6ba1a741f5 |
| ledger fingerprint | b052f773043b258d278f158567697b67574fdf3a5129afd5cfbaec28e593cd2f |
| package version | 0.1.0 |
| phase8 summary / composite state | supported |
| phase8 summary / derived label | solid |
| phase8 summary / original model label | solid |
| phase8 summary / taxonomy status | completed |
| phase8 summary / technical status | completed |
| phase9 summary / execution status | not&#95;executed |
| phase9 summary / final position id | Not supplied |
| phase9 summary / history validation | Not supplied |
| phase9 summary / mandatory | false |
| phase9 summary / review state | not&#95;required |
| phase9 summary / route | AUTO&#95;RESOLVABLE |
| phase9 summary / technical status | completed |
| providers / 1 / model | claude-haiku-5-5 |
| providers / 1 / provider | anthropic-live |
| providers / 1 / usage / cache creation input tokens | 0 |
| providers / 1 / usage / cache read input tokens | 0 |
| providers / 1 / usage / input tokens | 15054 |
| providers / 1 / usage / output tokens | 20667 |
| recording notice | LIVE MODEL GENERATION (AA-P10-LIVE/1.0); see execution evidence for model, request IDs and cost |
| review counts / adjudications | 0 |
| review counts / attempts | 0 |
| review counts / conflicts | 0 |
| review counts / positions | 1 |
| review fingerprint | 687c1162a7260750e16e1fe64033b022e003de0acfc5ed3bc47451042d0f2007 |
| run id | 846890e3-418d-466c-b70d-a65a5ac797eb |
| selected position id | p9position&#58;1731f876b9b0c0849e95de7c |

Complete original responses, all review carriers and machine bindings&#58; record.json. Final control decision&#58; decision.json. File hashes and full source index&#58; manifest.json. Hashes verify integrity, not actor identity or authentication.

