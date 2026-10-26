# Canonical local audit

## Execution and release

READY&#95;FOR&#95;RELEASE — local artifact status

LIVE MODEL GENERATION (AA-P10-LIVE/1.0). Actual provider calls produced the analysed responses; model, request IDs, attempts and cost are bound below and in record.json. Local artifact decision only; no scientific truth, empirical validation, external evidence search or customer approval.

### Independent states

| Field | Recorded value |
| --- | --- |
| analysis execution | completed |
| host evidence derivation (composite) | supported |
| local release | READY&#95;FOR&#95;RELEASE |
| mandatory review | false |
| model judgment (composite) | supported |
| model/host conflicts | none recorded |
| review execution | not&#95;executed |
| review route | AUTO&#95;RESOLVABLE |
| scientific judgment | supported |

No host release intent&#58; this is a candidate, not a released artifact.

### Revision identity

| Field | Recorded value |
| --- | --- |
| created at | 2026-10-12T15&#58;14&#58;16.143935+00&#58;00 |
| parent | Not supplied |
| record fingerprint | 4e124bc28f911eed58b0ffd4ba245815fb59606e8e84eec66481bb307accc263 |
| revision | 0055a768-d145-437e-8b8f-6dea67819abf |
| selected position id | p9position&#58;661ee5bc3c9a0c6832464e21 |

### Execution provenance per carrier

| Field | Recorded value |
| --- | --- |
|  / 1 / attempt ids | attempt-007 |
|  / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
|  / 1 / billing | usage&#95;reported |
|  / 1 / capture sha256 | df356e9eff6b1036941273eea8195b7be21fc5589517a75968281bda6e7371ee |
|  / 1 / completion state | complete |
|  / 1 / confirmed cost microusd | 97328 |
|  / 1 / current execution | live&#95;generation |
|  / 1 / denial reason | Not supplied |
|  / 1 / latency ms | 35583 |
|  / 1 / message id | msg&#95;011CfxZTGGnytHJEDm5HToE9 |
|  / 1 / model | claude-sonnet-5-5 |
|  / 1 / origin | live&#95;generation |
|  / 1 / profile id | claude-sonnet-5-5&#64;3 |
|  / 1 / provider | anthropic-live |
|  / 1 / replay capture verified | Not supplied |
|  / 1 / replay request identical | Not supplied |
|  / 1 / request id | req&#95;011CfxZTFuj7bDahVtC7QWB1 |
|  / 1 / requested model | claude-sonnet-5-5 |
|  / 1 / reserved microusd | 242210 |
|  / 1 / retry denied | Not supplied |
|  / 1 / returned model | claude-sonnet-5-5 |
|  / 1 / role | primary |
|  / 1 / slot key | aa-p10-live-retest-LR-01&#124;claude-sonnet-5-5&#64;3&#124;primary |
|  / 1 / stop reason | end&#95;turn |
|  / 1 / usage / cache creation input tokens | 0 |
|  / 1 / usage / cache read input tokens | 0 |
|  / 1 / usage / input tokens | 15054 |
|  / 1 / usage / output tokens | 6722 |

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
| raw response sha256 | c0d122dfe3ddfb073c1d159478c108dbe523bb730602e1afb5a5cb3f71756744 |
| reasons | Ledger, evidence constraints and transformations evaluated under AA-P8/1.2 (AA-P8-HOST/1.1) |
| record fingerprint | dcb3bb6f1daa1ba8a4617d3bb74a8f1153d635bf9a99521095a41feea0bcbc2d |
| technical status | completed |
| transformation findings | No entries recorded |

### Proposition judgments

| Field | Recorded value |
| --- | --- |
|  / 1 / dependency status | unknown |
|  / 1 / derived state | supported |
|  / 1 / evidence ids | e1 |
|  / 1 / host reasons | binding 1&#58; identified effect in studied setting permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
|  / 1 / host state | supported |
|  / 1 / model host conflict | false |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reasons | A randomized between-group comparison directly matches the claim and reports a statistically significant reduction in falls.<br>b1&#58; The randomized comparison reports fewer falls over twelve months in the training group than in the general health advice group, in the same population.<br>identified effect in studied setting permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
|  / 1 / reported verdict | supported |
|  / 1 / required | true |

## Original label and taxonomy

### Original versus derived classification

| Field | Recorded value |
| --- | --- |
| derived taxonomy | solid |
| original model label | solid |
| represented trigger analysis / causal claim | true |
| represented trigger analysis / core error | none |
| represented trigger analysis / described biological mechanism | false |
| represented trigger analysis / evidence ids | e1 |
| represented trigger analysis / implies human benefit | false |
| represented trigger analysis / noncausal result used | false |
| represented trigger analysis / proposition ids | claim&#58;p1 |
| represented trigger analysis / reason | The claim rests on a randomized between-group comparison that supports the causal reading. No mechanism is invoked, and the magnitude and population are not inflated. |
| represented trigger analysis / trigger evidence id | e1 |
| represented trigger analysis / trigger proposition id | claim&#58;p1 |
| represented trigger analysis / trigger quote | randomized trial |
| taxonomy check / assurance scope | Taxonomy decisions check represented trigger, core-error and evidence/proposition consistency. Quote containment does not prove entailment or correct model interpretation. |
| taxonomy check / derived label | solid |
| taxonomy check / reasons | Honest reporting with supported represented propositions |
| taxonomy check / technical status | completed |

## Propositions and inference limits

### Claim composition

| Field | Recorded value |
| --- | --- |
| claim id | claim |
| extraction provenance | Single-proposition extraction of the full claim sentence by the analyst. |
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
| derived judgment / evidence ids | e1 |
| derived judgment / host reasons | binding 1&#58; identified effect in studied setting permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
| derived judgment / host state | supported |
| derived judgment / model host conflict | false |
| derived judgment / proposition id | claim&#58;p1 |
| derived judgment / reasons | A randomized between-group comparison directly matches the claim and reports a statistically significant reduction in falls.<br>b1&#58; The randomized comparison reports fewer falls over twelve months in the training group than in the general health advice group, in the same population.<br>identified effect in studied setting permitted<br>evidence dependence&#58; unknown; no independent corroboration inferred |
| derived judgment / reported verdict | supported |
| derived judgment / required | true |
| material dimensions | population<br>intervention<br>comparator<br>endpoint<br>follow&#95;up |
| materiality | required |
| not applicable | No entries recorded |
| observation target | support |
| parent claim id | claim |
| premise proposition ids | No entries recorded |
| proposition id | claim&#58;p1 |
| provenance id | prov1 |
| reason | A randomized between-group comparison directly matches the claim and reports a statistically significant reduction in falls. |
| reported verdict | supported |
| required bridge ids | No entries recorded |
| search question | Did community-dwelling adults aged 70 and older randomized to a home-based balance training program have fewer falls over twelve months than those randomized to general health advice? |
| search scope ids | ss1 |
| uncertainty | No entries recorded |

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
| certainty | observed |
| comparator | general health advice |
| comparison | between |
| effect direction | fewer |
| endpoint | falls |
| endpoint type | clinical&#95;event |
| follow up | twelve months |
| intervention | home-based balance training program |
| population | community-dwelling adults aged 70 and older |
| relation | causal |
| species | human |

### Evidence bindings and directness

| Field | Recorded value |
| --- | --- |
|  / 1 / binding id | b1 |
|  / 1 / directness | direct |
|  / 1 / evidence id | e1 |
|  / 1 / observation | support |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reason | The randomized comparison reports fewer falls over twelve months in the training group than in the general health advice group, in the same population. |
|  / 1 / search scope id | ss1 |

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
| asserted state | supported |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | observed |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / effect direction | fewer |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | clinical&#95;event |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from and to text (identical) | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| from proposition ids | claim&#58;p1 |
| reason | Unchanged extraction of the full claim sentence. |
| stage | extraction |
| target id | claim&#58;p1 |
| transformation id | t1 |

### Transformation t2

| Field | Recorded value |
| --- | --- |
| asserted state | supported |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | observed |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / effect direction | fewer |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | clinical&#95;event |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| reason | The search question keeps all attributes and only changes the phrasing to a question. |
| stage | search&#95;question |
| target id | claim&#58;p1 |
| to text | Did community-dwelling adults aged 70 and older randomized to a home-based balance training program have fewer falls over twelve months than those randomized to general health advice? |
| transformation id | t2 |

### Transformation t3

| Field | Recorded value |
| --- | --- |
| asserted state | supported |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | observed |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / effect direction | fewer |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | clinical&#95;event |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from and to text (identical) | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| from proposition ids | claim&#58;p1 |
| reason | The internal finding repeats the proposition unchanged. |
| stage | internal |
| target id | claim&#58;p1 |
| transformation id | t3 |

### Transformation t4

| Field | Recorded value |
| --- | --- |
| asserted state | supported |
| asserts whole claim | true |
| from and to attributes (identical) / certainty | observed |
| from and to attributes (identical) / comparator | general health advice |
| from and to attributes (identical) / comparison | between |
| from and to attributes (identical) / effect direction | fewer |
| from and to attributes (identical) / endpoint | falls |
| from and to attributes (identical) / endpoint type | clinical&#95;event |
| from and to attributes (identical) / follow up | twelve months |
| from and to attributes (identical) / intervention | home-based balance training program |
| from and to attributes (identical) / population | community-dwelling adults aged 70 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from and to text (identical) | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
| from proposition ids | claim&#58;p1 |
| reason | The client summary repeats the claim unchanged, with no added strength or scope. |
| stage | summary |
| target id | cf1 |
| transformation id | t4 |

## Evidence and source quotations

Quotations are supplied source text. Evidence type, direction and semantic attributes are represented extraction; the checks do not authenticate study findings.

### Evidence e1

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint | falls |
| evidence id | e1 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | supporting |
| source id | context |
| value origin | Not supplied |

Evidence text and exact source reference (identical)&#58;

```
Over twelve months, community-dwelling adults aged 70 and older assigned to the home-based balance training program had 31 percent fewer falls than those assigned to general health advice, and the difference was statistically significant.
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / certainty | observed |
| attributes / comparator | general health advice |
| attributes / comparison | between |
| attributes / effect direction | fewer |
| attributes / endpoint | falls |
| attributes / endpoint type | clinical&#95;event |
| attributes / follow up | twelve months |
| attributes / intervention | home-based balance training program |
| attributes / population | community-dwelling adults aged 70 and older |
| attributes / relation | causal |
| attributes / species | human |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | No entries recorded |
| evidence id | e1 |
| evidence type | controlled&#95;intervention |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | true |
| source role | trial result reported in the context |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

## Search scope

External search executed&#58; false. Scope is limited to the captured supplied material; no evidence found does not mean no evidence exists.

### Declared search scopes

| Field | Recorded value |
| --- | --- |
|  / 1 / date cutoff | Not supplied |
|  / 1 / query terms | No entries recorded |
|  / 1 / resources | No entries recorded |
|  / 1 / reviewed source ids | input<br>context |
|  / 1 / scope type | reviewed&#95;set |
|  / 1 / search completeness | Not supplied |
|  / 1 / search scope id | ss1 |

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
|  / 1 / confidence status |  |
|  / 1 / contrary evidence ids | No entries recorded |
|  / 1 / finding id | claim&#58;p1 |
|  / 1 / predicted label | solid |
|  / 1 / proposition | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
|  / 1 / provenance id | prov1 |
|  / 1 / supporting evidence ids | e1 |
|  / 1 / verdict summary |  |

### Client Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / client explanation |  |
|  / 1 / client finding id | cf1 |
|  / 1 / client negative assertions | No entries recorded |
|  / 1 / client strength | not&#95;assessed |
|  / 1 / display claim | In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based balance training program had fewer falls over twelve months than those assigned to general health advice. |
|  / 1 / parent finding id | claim&#58;p1 |
|  / 1 / provenance id | prov1 |
|  / 1 / referenced evidence ids | e1 |
|  / 1 / value claims | No entries recorded |

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
| assessment fingerprint | 5ffcb7a3bd2f5a5c6fcb2d5c63fb09feaf6c36d1ecca3a60a7eb998d99a569c8 |
| history validation | Not supplied |
| interpretation | Current revalidated state |
| route | AUTO&#95;RESOLVABLE |
| source reference | record.json&#35;/run&#95;record |
| technical status | completed |

### Position p9position&#58;661ee5bc3c9a0c6832464e21

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;6b82f53b4d87ed01514ff065 |
| claim id | claim |
| complete analysis reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0 |
| derived taxonomy | solid |
| model | claude-sonnet-5-5 |
| origin | original |
| original model label | solid |
| position id | p9position&#58;661ee5bc3c9a0c6832464e21 |
| provider | anthropic-live |
| raw response reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0/agent&#95;result/raw&#95;output |
| raw sha256 | c0d122dfe3ddfb073c1d159478c108dbe523bb730602e1afb5a5cb3f71756744 |
| run id | 83708869-9b08-4a06-9fba-8069dc7e0625 |
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
| usage / output tokens | 6722 |

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
| analysis fingerprint | af27bb2495f984acb4f06f01dd372fb72052157b88f7e616f04fdb61c61b4337 |
| case id | p9case&#58;6b82f53b4d87ed01514ff065 |
| code / code fingerprint | a1654da6afd6991665f2e4d25824c4e21fc152d69eddef01fe9a9cacf64eb80d |
| code / complete module hash index | manifest.json&#35;/provenance/code/module&#95;hashes |
| code / module count | 74 |
| code / source binding | verified Git source bytes |
| code / verified source commit | 63399dd1c3093d21a9307630ba85a6f85e4fa450 |
| config | live-anthropic-v1 |
| contract | AA-P10/1.0 |
| contract addendum | AA-P10-LIVE/1.0 |
| evidence fingerprint | 50cb968ac1a6b50c5771df365127833941d2cac7af399886d4ea90462edf7185 |
| execution evidence / 1 / attempt ids | attempt-007 |
| execution evidence / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
| execution evidence / 1 / billing | usage&#95;reported |
| execution evidence / 1 / capture sha256 | df356e9eff6b1036941273eea8195b7be21fc5589517a75968281bda6e7371ee |
| execution evidence / 1 / completion state | complete |
| execution evidence / 1 / confirmed cost microusd | 97328 |
| execution evidence / 1 / current execution | live&#95;generation |
| execution evidence / 1 / denial reason | Not supplied |
| execution evidence / 1 / latency ms | 35583 |
| execution evidence / 1 / message id | msg&#95;011CfxZTGGnytHJEDm5HToE9 |
| execution evidence / 1 / model | claude-sonnet-5-5 |
| execution evidence / 1 / origin | live&#95;generation |
| execution evidence / 1 / profile id | claude-sonnet-5-5&#64;3 |
| execution evidence / 1 / provider | anthropic-live |
| execution evidence / 1 / replay capture verified | Not supplied |
| execution evidence / 1 / replay request identical | Not supplied |
| execution evidence / 1 / request id | req&#95;011CfxZTFuj7bDahVtC7QWB1 |
| execution evidence / 1 / requested model | claude-sonnet-5-5 |
| execution evidence / 1 / reserved microusd | 242210 |
| execution evidence / 1 / retry denied | Not supplied |
| execution evidence / 1 / returned model | claude-sonnet-5-5 |
| execution evidence / 1 / role | primary |
| execution evidence / 1 / slot key | aa-p10-live-retest-LR-01&#124;claude-sonnet-5-5&#64;3&#124;primary |
| execution evidence / 1 / stop reason | end&#95;turn |
| execution evidence / 1 / usage / cache creation input tokens | 0 |
| execution evidence / 1 / usage / cache read input tokens | 0 |
| execution evidence / 1 / usage / input tokens | 15054 |
| execution evidence / 1 / usage / output tokens | 6722 |
| execution mode | live&#95;generation |
| execution mode errors | No entries recorded |
| input fingerprint | f7735b78812a479470bf2638cbfc96c69876efbafe86cf6e4944fb6ba1a741f5 |
| ledger fingerprint | a10f0e929df770f66ef46c5a178fd96e6a0c0e39348c2e384a5e5ee66f62ed33 |
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
| providers / 1 / model | claude-sonnet-5-5 |
| providers / 1 / provider | anthropic-live |
| providers / 1 / usage / cache creation input tokens | 0 |
| providers / 1 / usage / cache read input tokens | 0 |
| providers / 1 / usage / input tokens | 15054 |
| providers / 1 / usage / output tokens | 6722 |
| recording notice | LIVE MODEL GENERATION (AA-P10-LIVE/1.0); see execution evidence for model, request IDs and cost |
| review counts / adjudications | 0 |
| review counts / attempts | 0 |
| review counts / conflicts | 0 |
| review counts / positions | 1 |
| review fingerprint | 5ffcb7a3bd2f5a5c6fcb2d5c63fb09feaf6c36d1ecca3a60a7eb998d99a569c8 |
| run id | 83708869-9b08-4a06-9fba-8069dc7e0625 |
| selected position id | p9position&#58;661ee5bc3c9a0c6832464e21 |

Complete original responses, all review carriers and machine bindings&#58; record.json. Final control decision&#58; decision.json. File hashes and full source index&#58; manifest.json. Hashes verify integrity, not actor identity or authentication.

