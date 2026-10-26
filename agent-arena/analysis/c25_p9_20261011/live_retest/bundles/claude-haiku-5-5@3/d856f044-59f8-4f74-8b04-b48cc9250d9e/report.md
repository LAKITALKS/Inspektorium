# Canonical local audit

## Execution and release

ANALYSIS&#95;INCOMPLETE — local artifact status

LIVE MODEL GENERATION (AA-P10-LIVE/1.0). Actual provider calls produced the analysed responses; model, request IDs, attempts and cost are bound below and in record.json. Local artifact decision only; no scientific truth, empirical validation, external evidence search or customer approval.

### Independent states

| Field | Recorded value |
| --- | --- |
| analysis execution | incomplete |
| host evidence derivation (composite) | Not supplied |
| local release | ANALYSIS&#95;INCOMPLETE |
| mandatory review | true |
| model judgment (composite) | Not supplied |
| model/host conflicts | none recorded |
| review execution | not&#95;executed |
| review route | HUMAN&#95;REVIEW&#95;REQUIRED |
| scientific judgment | unknown |

No host release intent&#58; this is a candidate, not a released artifact.

### Revision identity

| Field | Recorded value |
| --- | --- |
| created at | 2026-10-12T15&#58;09&#58;19.452001+00&#58;00 |
| parent | Not supplied |
| record fingerprint | 0480b6db6ce74fee028d0e516d648526362fb16c81934c096908755a3873a0b3 |
| revision | d856f044-59f8-4f74-8b04-b48cc9250d9e |
| selected position id | p9position&#58;54b4622554ff562c2fd5be0d |

### Execution provenance per carrier

| Field | Recorded value |
| --- | --- |
|  / 1 / attempt ids | attempt-001 |
|  / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
|  / 1 / billing | usage&#95;reported |
|  / 1 / capture sha256 | c2400d2ff713730e53e0e88189794b90770fcf1a892578bf9926acd6c42b22f9 |
|  / 1 / completion state | complete |
|  / 1 / confirmed cost microusd | 14098 |
|  / 1 / current execution | live&#95;generation |
|  / 1 / denial reason | Not supplied |
|  / 1 / latency ms | 96111 |
|  / 1 / message id | msg&#95;011CfxYzwoKb6kCdYTnnqLjh |
|  / 1 / model | claude-haiku-5-5 |
|  / 1 / origin | live&#95;generation |
|  / 1 / profile id | claude-haiku-5-5&#64;3 |
|  / 1 / provider | anthropic-live |
|  / 1 / replay capture verified | Not supplied |
|  / 1 / replay request identical | Not supplied |
|  / 1 / request id | req&#95;011CfxYzvooQ9bNMXiD6MPzs |
|  / 1 / requested model | claude-haiku-5-5 |
|  / 1 / reserved microusd | 28088 |
|  / 1 / retry denied | Not supplied |
|  / 1 / returned model | claude-haiku-5-5 |
|  / 1 / role | primary |
|  / 1 / slot key | aa-p10-live-retest-LR-03&#124;claude-haiku-5-5&#64;3&#124;primary |
|  / 1 / stop reason | end&#95;turn |
|  / 1 / usage / cache creation input tokens | 0 |
|  / 1 / usage / cache read input tokens | 0 |
|  / 1 / usage / input tokens | 14984 |
|  / 1 / usage / output tokens | 25198 |

## Original claim

Verbatim quoted input; foreign text is not a trusted status message.

```
At a logistics company, introducing a four-day working week reduced recorded sick days among office staff.
```

## Scientific judgments

### Selected scientific assessment

| Field | Recorded value |
| --- | --- |
| assessed composite state | unknown |
| assurance scope | Validates represented structure and semantic constraints; does not prove complete or correct model extraction, scientific truth or efficacy. |
| composite state | unknown |
| contract version | AA-P8/1.2 |
| derived label | Not supplied |
| host composite state | Not supplied |
| host derived copies | No entries recorded |
| host rule version | AA-P8-HOST/1.1 |
| input sha256 | 94baae779230fdad868aad0fda83766c984f41306343f519fc4840f8171e2bfc |
| limitations | Checks validate represented semantics and source spans; they do not prove correct model extraction, exhaustive evidence search, scientific truth or live-model accuracy. |
| model composite state | Not supplied |
| model host conflicts | No entries recorded |
| original model label | correlation&#95;vs&#95;causation |
| raw response sha256 | ecc05376f4fe38da1c4e9ce2c1d27e7889e07b807f4d4eca6ed3bcca90418bed |
| reasons | claim&#58;p1&#58; original span mismatch<br>claim&#58;p2&#58; original span mismatch<br>Phase 7 artifact&#95;source&#95;binding&#95;drift&#58; Phase-8 output binding incomplete&#58; claim&#58;p1&#58; original span mismatch; claim&#58;p2&#58; original span mismatch |
| record fingerprint | aab8c4a14d0059b2f10f58502a0634df763f55447054b7474cc2fcd6dc846f01 |
| technical status | incomplete |
| transformation findings | No entries recorded |

### Proposition judgments

| Field | Recorded value |
| --- | --- |
| Value | No entries recorded |

## Original label and taxonomy

### Original versus derived classification

| Field | Recorded value |
| --- | --- |
| derived taxonomy | Not supplied |
| original model label | correlation&#95;vs&#95;causation |
| represented trigger analysis / causal claim | true |
| represented trigger analysis / core error | causal&#95;inference |
| represented trigger analysis / described biological mechanism | false |
| represented trigger analysis / evidence ids | ev2<br>ev3<br>ev4 |
| represented trigger analysis / implies human benefit | false |
| represented trigger analysis / noncausal result used | true |
| represented trigger analysis / proposition ids | claim&#58;p2 |
| represented trigger analysis / reason | The causal relation in claim&#58;p2 rests on an uncontrolled before-and-after, year-over-year comparison that is confounded by the prior-year influenza season and has no concurrent comparison group. |
| represented trigger analysis / trigger evidence id | ev2 |
| represented trigger analysis / trigger proposition id | claim&#58;p2 |
| represented trigger analysis / trigger quote | were 20 percent lower that year than in the previous year |
| taxonomy check / assurance scope | Taxonomy decisions check represented trigger, core-error and evidence/proposition consistency. Quote containment does not prove entailment or correct model interpretation. |
| taxonomy check / derived label | Not supplied |
| taxonomy check / reasons | Semantic analysis did not complete; no taxonomy correction |
| taxonomy check / technical status | incomplete |

## Propositions and inference limits

### Claim composition

| Field | Recorded value |
| --- | --- |
| claim id | claim |
| extraction provenance | Supplied task prompt and task context only; no external search executed. |
| logic / children / 1 / children | No entries recorded |
| logic / children / 1 / operator | leaf |
| logic / children / 1 / proposition id | claim&#58;p1 |
| logic / children / 2 / children | No entries recorded |
| logic / children / 2 / operator | leaf |
| logic / children / 2 / proposition id | claim&#58;p2 |
| logic / operator | and |
| logic / proposition id | Not supplied |
| provenance id | prov&#58;input-claim |
| required proposition ids | claim&#58;p1<br>claim&#58;p2 |

### Proposition claim&#58;p1

| Field | Recorded value |
| --- | --- |
| derived judgment | Not supplied |
| material dimensions | intervention<br>population |
| materiality | required |
| not applicable | No entries recorded |
| observation target | Not supplied |
| parent claim id | claim |
| premise proposition ids | No entries recorded |
| proposition id | claim&#58;p1 |
| provenance id | prov&#58;input-claim |
| reason | Directly stated in the supplied context. |
| reported verdict | supported |
| required bridge ids | No entries recorded |
| search question | Does the supplied context report that a four-day working week was introduced for office staff at the logistics company? |
| search scope ids | scope&#58;context |
| uncertainty | No entries recorded |

Quoted proposition; this is represented input, not a release assertion.

```
introducing a four-day working week
```

### Original span

| Field | Recorded value |
| --- | --- |
| end | 60 |
| start | 25 |
| text | introducing a four-day working week |

### Population, endpoint, product and inference attributes

| Field | Recorded value |
| --- | --- |
| intervention | four-day working week |
| population | office staff |
| relation | description |
| species | human |

### Evidence bindings and directness

| Field | Recorded value |
| --- | --- |
|  / 1 / binding id | bind&#58;p1&#58;ev1 |
|  / 1 / directness | direct |
|  / 1 / evidence id | ev1 |
|  / 1 / observation | support |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reason | The context directly states that the four-day week was introduced for all office staff in January. |
|  / 1 / search scope id | scope&#58;context |

### Proposition claim&#58;p2

| Field | Recorded value |
| --- | --- |
| derived judgment | Not supplied |
| material dimensions | intervention<br>endpoint<br>relation<br>effect&#95;direction<br>population |
| materiality | required |
| not applicable | No entries recorded |
| observation target | Not supplied |
| parent claim id | claim |
| premise proposition ids | No entries recorded |
| proposition id | claim&#58;p2 |
| provenance id | prov&#58;input-claim |
| reason | The causal relation is not established&#58; the evidence is an uncontrolled, confounded before-and-after comparison. |
| reported verdict | unsupported |
| required bridge ids | bridge&#58;causal1 |
| search question | Does the supplied context establish that introducing a four-day working week caused a reduction in recorded sick days among office staff, rather than only reporting a before-and-after difference? |
| search scope ids | scope&#58;context |
| uncertainty | The claim names no explicit comparator.<br>The influenza effect size is not quantified. |

Quoted proposition; this is represented input, not a release assertion.

```
introducing a four-day working week reduced recorded sick days among office staff
```

### Original span

| Field | Recorded value |
| --- | --- |
| end | 106 |
| start | 25 |
| text | introducing a four-day working week reduced recorded sick days among office staff |

### Population, endpoint, product and inference attributes

| Field | Recorded value |
| --- | --- |
| effect direction | decrease |
| endpoint | recorded sick days |
| intervention | four-day working week |
| population | office staff |
| relation | causal |
| species | human |

### Evidence bindings and directness

| Field | Recorded value |
| --- | --- |
|  / 1 / binding id | bind&#58;p2&#58;ev2 |
|  / 1 / directness | partial |
|  / 1 / evidence id | ev2 |
|  / 1 / observation | inconclusive |
|  / 1 / proposition id | claim&#58;p2 |
|  / 1 / reason | The reported 20 percent reduction is a before-and-after, within-group comparison that is confounded by the prior-year influenza season, so it does not identify an intervention effect. |
|  / 1 / search scope id | scope&#58;context |
|  / 2 / binding id | bind&#58;p2&#58;ev3 |
|  / 2 / directness | indirect |
|  / 2 / evidence id | ev3 |
|  / 2 / observation | inconclusive |
|  / 2 / proposition id | claim&#58;p2 |
|  / 2 / reason | The influenza season in the comparison year is a plausible alternative explanation for the observed difference. |
|  / 2 / search scope id | scope&#58;context |
|  / 3 / binding id | bind&#58;p2&#58;ev4 |
|  / 3 / directness | indirect |
|  / 3 / evidence id | ev4 |
|  / 3 / observation | inconclusive |
|  / 3 / proposition id | claim&#58;p2 |
|  / 3 / reason | The absence of five-day-week sick-day figures means no concurrent comparison group is reported. |
|  / 3 / search scope id | scope&#58;context |

### Bridges

| Field | Recorded value |
| --- | --- |
|  / 1 / bridge id | bridge&#58;causal1 |
|  / 1 / conclusion proposition id | claim&#58;p2 |
|  / 1 / dimensions | relation<br>effect&#95;direction |
|  / 1 / evidence ids | ev2<br>ev3<br>ev4 |
|  / 1 / kind | causal&#95;identification |
|  / 1 / premise proposition ids | claim&#58;p1 |
|  / 1 / reason | The supplied before-and-after comparison, confounded by the prior-year influenza season and lacking a five-day-week comparison, does not identify a causal effect of the intervention. |
|  / 1 / state | unsupported |

### Product Transfers

| Field | Recorded value |
| --- | --- |
| Value | No entries recorded |

### Transformation tr&#58;extract&#58;claim&#58;p1

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to text (identical) | introducing a four-day working week |
| from attributes | No entries recorded |
| from proposition ids | claim&#58;p1 |
| reason | Extraction of the intervention proposition from the original claim span; from&#95;attributes left empty. |
| stage | extraction |
| target id | claim&#58;p1 |
| to attributes / intervention | four-day working week |
| to attributes / population | office staff |
| to attributes / relation | description |
| to attributes / species | human |
| transformation id | tr&#58;extract&#58;claim&#58;p1 |

### Transformation tr&#58;search&#58;claim&#58;p1

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to attributes (identical) / intervention | four-day working week |
| from and to attributes (identical) / population | office staff |
| from and to attributes (identical) / relation | description |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | introducing a four-day working week |
| reason | Search question restates the intervention proposition; attributes unchanged. |
| stage | search&#95;question |
| target id | claim&#58;p1 |
| to text | Does the supplied context report that a four-day working week was introduced for office staff at the logistics company? |
| transformation id | tr&#58;search&#58;claim&#58;p1 |

### Transformation tr&#58;internal&#58;claim&#58;p1

| Field | Recorded value |
| --- | --- |
| asserted state | supported |
| asserts whole claim | false |
| from and to attributes (identical) / intervention | four-day working week |
| from and to attributes (identical) / population | office staff |
| from and to attributes (identical) / relation | description |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | introducing a four-day working week |
| reason | Internal finding restates the proposition and its supported verdict; no meaning change. |
| stage | internal |
| target id | claim&#58;p1 |
| to text | introducing a four-day working week<br>The supplied context states that a four-day working week was introduced for all office staff in January. |
| transformation id | tr&#58;internal&#58;claim&#58;p1 |

### Transformation tr&#58;extract&#58;claim&#58;p2

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to text (identical) | introducing a four-day working week reduced recorded sick days among office staff |
| from attributes | No entries recorded |
| from proposition ids | claim&#58;p2 |
| reason | Extraction of the causal proposition from the original claim span; from&#95;attributes left empty. |
| stage | extraction |
| target id | claim&#58;p2 |
| to attributes / effect direction | decrease |
| to attributes / endpoint | recorded sick days |
| to attributes / intervention | four-day working week |
| to attributes / population | office staff |
| to attributes / relation | causal |
| to attributes / species | human |
| transformation id | tr&#58;extract&#58;claim&#58;p2 |

### Transformation tr&#58;search&#58;claim&#58;p2

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to attributes (identical) / effect direction | decrease |
| from and to attributes (identical) / endpoint | recorded sick days |
| from and to attributes (identical) / intervention | four-day working week |
| from and to attributes (identical) / population | office staff |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p2 |
| from text | introducing a four-day working week reduced recorded sick days among office staff |
| reason | Search question makes the causal test explicit; attributes unchanged and the causal relation is preserved. |
| stage | search&#95;question |
| target id | claim&#58;p2 |
| to text | Does the supplied context establish that introducing a four-day working week caused a reduction in recorded sick days among office staff, rather than only reporting a before-and-after difference? |
| transformation id | tr&#58;search&#58;claim&#58;p2 |

### Transformation tr&#58;internal&#58;claim&#58;p2

| Field | Recorded value |
| --- | --- |
| asserted state | unsupported |
| asserts whole claim | false |
| from and to attributes (identical) / effect direction | decrease |
| from and to attributes (identical) / endpoint | recorded sick days |
| from and to attributes (identical) / intervention | four-day working week |
| from and to attributes (identical) / population | office staff |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p2 |
| from text | introducing a four-day working week reduced recorded sick days among office staff |
| reason | Internal finding matches the reported unsupported verdict; the causal relation is not weakened or strengthened. |
| stage | internal |
| target id | claim&#58;p2 |
| to text | introducing a four-day working week reduced recorded sick days among office staff<br>Only an uncontrolled before-and-after comparison is reported; the prior-year influenza season confounds it, so causal support is absent. |
| transformation id | tr&#58;internal&#58;claim&#58;p2 |

### Transformation tr&#58;summary&#58;client&#58;c1

| Field | Recorded value |
| --- | --- |
| asserted state | unsupported |
| asserts whole claim | false |
| from and to attributes (identical) / effect direction | decrease |
| from and to attributes (identical) / endpoint | recorded sick days |
| from and to attributes (identical) / intervention | four-day working week |
| from and to attributes (identical) / population | office staff |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p2 |
| from text | introducing a four-day working week reduced recorded sick days among office staff |
| reason | Client summary keeps the reported 20 percent figure, states the causal link is not established, and does not assert the whole claim. |
| stage | summary |
| target id | client&#58;c1 |
| to text | The company&#x27;s annual report says recorded sick days among office staff were 20 percent lower in the year after the four-day working week was introduced, but the supplied material does not establish that the four-day week caused this reduction.<br>The comparison is with a prior year that had a severe influenza season, and the report gives no sick-day figures for staff who kept a five-day week. |
| transformation id | tr&#58;summary&#58;client&#58;c1 |

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
introduced a four-day working week for all office staff in January
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / intervention | four-day working week |
| attributes / population | office staff |
| attributes / relation | description |
| attributes / species | human |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | single supplied statement |
| evidence id | ev1 |
| evidence type | descriptive |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | Not supplied |
| source role | context&#58; company statement of intervention |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

### Evidence ev2

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint | recorded sick days |
| evidence id | ev2 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | 20 percent lower |
| role | supporting |
| source id | context |
| value origin | source&#95;reported |

Evidence text and exact source reference (identical)&#58;

```
recorded sick days among office staff were 20 percent lower that year than in the previous year
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / comparator | previous year |
| attributes / comparison | within |
| attributes / effect basis | year-over-year change |
| attributes / effect direction | decrease |
| attributes / effect magnitude | 20 percent lower |
| attributes / endpoint | recorded sick days |
| attributes / intervention | four-day working week |
| attributes / population | office staff |
| attributes / relation | association |
| attributes / species | human |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | uncontrolled before-and-after comparison<br>prior-year influenza season confound |
| evidence id | ev2 |
| evidence type | observational |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | false |
| source role | context&#58; annual report sick-day statistic |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

### Evidence ev3

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint |  |
| evidence id | ev3 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | weakening |
| source id | context |
| value origin | Not supplied |

Evidence text and exact source reference (identical)&#58;

```
a severe influenza season had affected the previous year
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / relation | description |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | alternative explanation for prior-year figures |
| evidence id | ev3 |
| evidence type | descriptive |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | Not supplied |
| source role | context&#58; report note on prior year |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

### Evidence ev4

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint | recorded sick days |
| evidence id | ev4 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | missing&#95;expected |
| source id | context |
| value origin | Not supplied |

Evidence text and exact source reference (identical)&#58;

```
gives no sick-day figures for staff who kept a five-day week
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / relation | description |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | no five-day-week sick-day figures reported |
| evidence id | ev4 |
| evidence type | descriptive |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | Not supplied |
| source role | context&#58; report note on missing comparison figures |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

## Search scope

External search executed&#58; false. Scope is limited to the captured supplied material; no evidence found does not mean no evidence exists.

### Declared search scopes

| Field | Recorded value |
| --- | --- |
|  / 1 / date cutoff | Not supplied |
|  / 1 / query terms | No entries recorded |
|  / 1 / resources | supplied task&#95;context |
|  / 1 / reviewed source ids | context |
|  / 1 / scope type | reviewed&#95;set |
|  / 1 / search completeness | complete for supplied context only; no external search executed |
|  / 1 / search scope id | scope&#58;context |

### Bound negative assertions

| Field | Recorded value |
| --- | --- |
| Value | No entries recorded |

Captured context (source&#95;id&#58; context)&#58;

```
A logistics company introduced a four-day working week for all office staff in January. In its annual report, the company stated that recorded sick days among office staff were 20 percent lower that year than in the previous year. The report notes that a severe influenza season had affected the previous year and gives no sick-day figures for staff who kept a five-day week.
```

## Finding and client traces

### Provenance

| Field | Recorded value |
| --- | --- |
|  / 1 / canonical url | Not supplied |
|  / 1 / content fingerprint | Not supplied |
|  / 1 / context after | Not supplied |
|  / 1 / context before | Not supplied |
|  / 1 / exact claim text | At a logistics company, introducing a four-day working week reduced recorded sick days among office staff. |
|  / 1 / page title | Not supplied |
|  / 1 / provenance id | prov&#58;input-claim |
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
|  / 1 / predicted label | Not supplied |
|  / 1 / proposition | introducing a four-day working week |
|  / 1 / provenance id | prov&#58;input-claim |
|  / 1 / supporting evidence ids | ev1 |
|  / 1 / verdict summary | The supplied context states that a four-day working week was introduced for all office staff in January. |
|  / 2 / allowed summary strength | not&#95;assessed |
|  / 2 / confidence status |  |
|  / 2 / contrary evidence ids | ev3<br>ev4 |
|  / 2 / finding id | claim&#58;p2 |
|  / 2 / predicted label | Not supplied |
|  / 2 / proposition | introducing a four-day working week reduced recorded sick days among office staff |
|  / 2 / provenance id | prov&#58;input-claim |
|  / 2 / supporting evidence ids | ev2 |
|  / 2 / verdict summary | Only an uncontrolled before-and-after comparison is reported; the prior-year influenza season confounds it, so causal support is absent. |

### Client Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / client explanation | The comparison is with a prior year that had a severe influenza season, and the report gives no sick-day figures for staff who kept a five-day week. |
|  / 1 / client finding id | client&#58;c1 |
|  / 1 / client negative assertions | No entries recorded |
|  / 1 / client strength | not&#95;assessed |
|  / 1 / display claim | The company&#x27;s annual report says recorded sick days among office staff were 20 percent lower in the year after the four-day working week was introduced, but the supplied material does not establish that the four-day week caused this reduction. |
|  / 1 / parent finding id | claim&#58;p2 |
|  / 1 / provenance id | prov&#58;input-claim |
|  / 1 / referenced evidence ids | ev2<br>ev3<br>ev4 |
|  / 1 / value claims / 1 / claimed origin | source&#95;reported |
|  / 1 / value claims / 1 / claimed source ids | context |
|  / 1 / value claims / 1 / evidence id | ev2 |

## UNKNOWN, conflicts and review history

### Current review state

| Field | Recorded value |
| --- | --- |
| assurance scope | Checks represented positions, identity, materiality and routing. No majority vote, scientific truth, reviewer independence or release authorization is inferred. |
| case id | p9case&#58;a8aa0c2842890a7656506234 |
| contract version | AA-P9/1.2 |
| execution status | not&#95;executed |
| mandatory | true |
| reasons | Routing preserves separate scientific/taxonomy layers; no majority or provider call executed |
| review state | pending |
| route | HUMAN&#95;REVIEW&#95;REQUIRED |
| technical status | incomplete |
| uncertainty | No entries recorded |

### Current revalidated assessment

| Field | Recorded value |
| --- | --- |
| assessment fingerprint | df482b9144d32e5a2b8f4051ee08fd68b59765e4fc88ba08dedd9f203eb9c66c |
| history validation | Not supplied |
| interpretation | Current revalidated state |
| route | HUMAN&#95;REVIEW&#95;REQUIRED |
| source reference | record.json&#35;/run&#95;record |
| technical status | incomplete |

### Position p9position&#58;54b4622554ff562c2fd5be0d

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;a8aa0c2842890a7656506234 |
| claim id | claim |
| complete analysis reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0 |
| derived taxonomy | Not supplied |
| model | claude-haiku-5-5 |
| origin | original |
| original model label | correlation&#95;vs&#95;causation |
| position id | p9position&#58;54b4622554ff562c2fd5be0d |
| provider | anthropic-live |
| raw response reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0/agent&#95;result/raw&#95;output |
| raw sha256 | ecc05376f4fe38da1c4e9ce2c1d27e7889e07b807f4d4eca6ed3bcca90418bed |
| run id | e718e663-9837-467e-922e-232e551041b0 |
| scientific state | unknown |
| selected | true |
| taxonomy status | incomplete |
| technical status | incomplete |

### Captured execution

| Field | Recorded value |
| --- | --- |
| error | Not supplied |
| error type | Not supplied |
| finish reason | stop |
| parse ok | true |
| usage / cache creation input tokens | 0 |
| usage / cache read input tokens | 0 |
| usage / input tokens | 14984 |
| usage / output tokens | 25198 |

### Trigger

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;a8aa0c2842890a7656506234 |
| claim id | claim |
| code | failed&#95;mandatory&#95;control |
| evidence ids | ev2<br>ev3<br>ev4 |
| field | phase8.taxonomy.technical&#95;status |
| mandatory | true |
| material | true |
| position ids | p9position&#58;54b4622554ff562c2fd5be0d |
| projected object fingerprint | 887720445dc017396a603b7de46b858cfef0707a5576814d12fcd811a60fd12e |
| proposition ids | claim&#58;p2 |
| reason | Semantic analysis did not complete; no taxonomy correction |
| source reference | record.json&#35;/run&#95;record/metadata/phase9/triggers/0 |
| trigger id | p9trigger&#58;0d670a97a2fe8b27064b68dd |

### Trigger

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;a8aa0c2842890a7656506234 |
| claim id | claim |
| code | critical&#95;source&#95;binding |
| evidence ids | No entries recorded |
| field | phase8.phase7&#95;controls.finding&#95;artifact&#95;binding |
| mandatory | true |
| material | true |
| position ids | p9position&#58;54b4622554ff562c2fd5be0d |
| projected object fingerprint | 4d24a29d6b318dfc17332161dc11fa8a3a90d4281fed9c3b9ecc371550603544 |
| proposition ids | No entries recorded |
| reason | Phase-8 output binding incomplete&#58; claim&#58;p1&#58; original span mismatch; claim&#58;p2&#58; original span mismatch |
| source reference | record.json&#35;/run&#95;record/metadata/phase9/triggers/1 |
| trigger id | p9trigger&#58;d659d7d78c1003bae51155dc |

### Trigger

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;a8aa0c2842890a7656506234 |
| claim id | claim |
| code | failed&#95;mandatory&#95;control |
| evidence ids | No entries recorded |
| field | phase8.technical&#95;status |
| mandatory | true |
| material | true |
| position ids | p9position&#58;54b4622554ff562c2fd5be0d |
| projected object fingerprint | bb8d83edcbb6591c7e9f163bfe021eda190e747c7d108fcc741409a7d1a68573 |
| proposition ids | No entries recorded |
| reason | claim&#58;p1&#58; original span mismatch; claim&#58;p2&#58; original span mismatch; Phase 7 artifact&#95;source&#95;binding&#95;drift&#58; Phase-8 output binding incomplete&#58; claim&#58;p1&#58; original span mismatch; claim&#58;p2&#58; original span mismatch |
| source reference | record.json&#35;/run&#95;record/metadata/phase9/triggers/2 |
| trigger id | p9trigger&#58;e01791583aa702ead4a651d0 |

Current assessment contains no recorded conflicts. This is not evidence of scientific truth.

No adjudication is recorded; absence is not human approval.

## Mandatory controls

### Executed controls

| Control and version | Execution, population and result |
| --- | --- |
| input&#95;preflight / 1.1 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Input and nonempty execution population checked |
| analysis&#95;source / 1.0 | Execution&#58; executed<br>Outcome&#58; fail<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Reparsed raw, supplied source spans and nonempty claim/evidence/output traces checked |
| finding&#95;artifact&#95;binding / 1.1.0 | Execution&#58; executed<br>Outcome&#58; fail<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Evaluated client&#95;findings |
| summary&#95;strength&#95;monotonicity / 1.0.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Evaluated client&#95;findings |
| evidence&#95;symmetry / 1.1.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Evaluated client&#95;finding&#95;material&#95;evidence&#95;contexts |
| value&#95;origin&#95;provenance / 1.0.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 3<br>Evaluated&#58; 3<br>Reason&#58; Evaluated client&#95;visible&#95;evidence&#95;references |
| search&#95;scope&#95;binding / 1.0.0 | Execution&#58; executed<br>Outcome&#58; not&#95;applicable<br>Eligible&#58; 0<br>Evaluated&#58; 0<br>Reason&#58; Host-derived N/A&#58; no client&#95;negative&#95;assertions; check executed successfully |
| phase8&#95;semantics&#95;taxonomy / 1.2 | Execution&#58; executed<br>Outcome&#58; fail<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Current semantic and separate taxonomy analysis required |
| phase9&#95;history&#95;review / 1.2 | Execution&#58; executed<br>Outcome&#58; fail<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; All original/review/adjudication carriers and mandatory review revalidated |
| provenance / live-1.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Current code bytes, task/raw/history/selected evidence and live execution evidence bound (AA-P10-LIVE/1.0) |

### Findings&#58; finding&#95;artifact&#95;binding

| Field | Recorded value |
| --- | --- |
|  / 1 / check | P8 |
|  / 1 / client finding id |  |
|  / 1 / code | artifact&#95;source&#95;binding&#95;drift |
|  / 1 / detail | Phase-8 output binding incomplete&#58; claim&#58;p1&#58; original span mismatch; claim&#58;p2&#58; original span mismatch |
|  / 1 / refs | No entries recorded |
|  / 1 / severity | critical |

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
| analysis fingerprint | 9260e94492368577945906243ff5d4e4771141167bc12c4c79b8f935094a6bd7 |
| case id | p9case&#58;a8aa0c2842890a7656506234 |
| code / code fingerprint | a1654da6afd6991665f2e4d25824c4e21fc152d69eddef01fe9a9cacf64eb80d |
| code / complete module hash index | manifest.json&#35;/provenance/code/module&#95;hashes |
| code / module count | 74 |
| code / source binding | verified Git source bytes |
| code / verified source commit | 63399dd1c3093d21a9307630ba85a6f85e4fa450 |
| config | live-anthropic-v1 |
| contract | AA-P10/1.0 |
| contract addendum | AA-P10-LIVE/1.0 |
| evidence fingerprint | e16a4e7d58d5c3dda56b9a3d598317b21f8f33364bf06802c5c67ffc4dd96a5c |
| execution evidence / 1 / attempt ids | attempt-001 |
| execution evidence / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
| execution evidence / 1 / billing | usage&#95;reported |
| execution evidence / 1 / capture sha256 | c2400d2ff713730e53e0e88189794b90770fcf1a892578bf9926acd6c42b22f9 |
| execution evidence / 1 / completion state | complete |
| execution evidence / 1 / confirmed cost microusd | 14098 |
| execution evidence / 1 / current execution | live&#95;generation |
| execution evidence / 1 / denial reason | Not supplied |
| execution evidence / 1 / latency ms | 96111 |
| execution evidence / 1 / message id | msg&#95;011CfxYzwoKb6kCdYTnnqLjh |
| execution evidence / 1 / model | claude-haiku-5-5 |
| execution evidence / 1 / origin | live&#95;generation |
| execution evidence / 1 / profile id | claude-haiku-5-5&#64;3 |
| execution evidence / 1 / provider | anthropic-live |
| execution evidence / 1 / replay capture verified | Not supplied |
| execution evidence / 1 / replay request identical | Not supplied |
| execution evidence / 1 / request id | req&#95;011CfxYzvooQ9bNMXiD6MPzs |
| execution evidence / 1 / requested model | claude-haiku-5-5 |
| execution evidence / 1 / reserved microusd | 28088 |
| execution evidence / 1 / retry denied | Not supplied |
| execution evidence / 1 / returned model | claude-haiku-5-5 |
| execution evidence / 1 / role | primary |
| execution evidence / 1 / slot key | aa-p10-live-retest-LR-03&#124;claude-haiku-5-5&#64;3&#124;primary |
| execution evidence / 1 / stop reason | end&#95;turn |
| execution evidence / 1 / usage / cache creation input tokens | 0 |
| execution evidence / 1 / usage / cache read input tokens | 0 |
| execution evidence / 1 / usage / input tokens | 14984 |
| execution evidence / 1 / usage / output tokens | 25198 |
| execution mode | live&#95;generation |
| execution mode errors | No entries recorded |
| input fingerprint | 43fbbd8e7678360ebbe6ab2adc5ad06677304370cb688a603dc7c8f910061c50 |
| ledger fingerprint | d3093a0250f43896bb298fd44f72279fc66ce4cd888efe78877c721f759d5fce |
| package version | 0.1.0 |
| phase8 summary / composite state | unknown |
| phase8 summary / derived label | Not supplied |
| phase8 summary / original model label | correlation&#95;vs&#95;causation |
| phase8 summary / taxonomy status | incomplete |
| phase8 summary / technical status | incomplete |
| phase9 summary / execution status | not&#95;executed |
| phase9 summary / final position id | Not supplied |
| phase9 summary / history validation | Not supplied |
| phase9 summary / mandatory | true |
| phase9 summary / review state | pending |
| phase9 summary / route | HUMAN&#95;REVIEW&#95;REQUIRED |
| phase9 summary / technical status | incomplete |
| providers / 1 / model | claude-haiku-5-5 |
| providers / 1 / provider | anthropic-live |
| providers / 1 / usage / cache creation input tokens | 0 |
| providers / 1 / usage / cache read input tokens | 0 |
| providers / 1 / usage / input tokens | 14984 |
| providers / 1 / usage / output tokens | 25198 |
| recording notice | LIVE MODEL GENERATION (AA-P10-LIVE/1.0); see execution evidence for model, request IDs and cost |
| review counts / adjudications | 0 |
| review counts / attempts | 0 |
| review counts / conflicts | 0 |
| review counts / positions | 1 |
| review fingerprint | df482b9144d32e5a2b8f4051ee08fd68b59765e4fc88ba08dedd9f203eb9c66c |
| run id | e718e663-9837-467e-922e-232e551041b0 |
| selected position id | p9position&#58;54b4622554ff562c2fd5be0d |

Complete original responses, all review carriers and machine bindings&#58; record.json. Final control decision&#58; decision.json. File hashes and full source index&#58; manifest.json. Hashes verify integrity, not actor identity or authentication.

