# Canonical local audit

## Execution and release

REVIEW&#95;REQUIRED — local artifact status

LIVE MODEL GENERATION (AA-P10-LIVE/1.0). Actual provider calls produced the analysed responses; model, request IDs, attempts and cost are bound below and in record.json. Local artifact decision only; no scientific truth, empirical validation, external evidence search or customer approval.

### Independent states

| Field | Recorded value |
| --- | --- |
| analysis execution | completed |
| host evidence derivation (composite) | unknown |
| local release | REVIEW&#95;REQUIRED |
| mandatory review | true |
| model judgment (composite) | unsupported |
| model/host conflicts | selected judgment&#58; 2 open; mandatory review pending, release blocked |
| review execution | not&#95;executed |
| review route | UNRESOLVED |
| scientific judgment | unknown |

No host release intent&#58; this is a candidate, not a released artifact.

### Revision identity

| Field | Recorded value |
| --- | --- |
| created at | 2026-10-12T15&#58;14&#58;55.425193+00&#58;00 |
| parent | Not supplied |
| record fingerprint | acc4a700fa3133dd56149366c2d0e5c8d78e25c7983a177fb29b5fbd9d7b0c67 |
| revision | 44b587d3-0d46-41c0-9984-97dbbc14c6bf |
| selected position id | p9position&#58;caf22e55c19b3fff985d3730 |

### Execution provenance per carrier

| Field | Recorded value |
| --- | --- |
|  / 1 / attempt ids | attempt-008 |
|  / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
|  / 1 / billing | usage&#95;reported |
|  / 1 / capture sha256 | 24c6687c7077c298a725821ee46482e398c383318f9b8282e05a332bbce2d95e |
|  / 1 / completion state | complete |
|  / 1 / confirmed cost microusd | 96992 |
|  / 1 / current execution | live&#95;generation |
|  / 1 / denial reason | Not supplied |
|  / 1 / latency ms | 38327 |
|  / 1 / message id | msg&#95;011CfxZVx6z983i8CkVN2hry |
|  / 1 / model | claude-sonnet-5-5 |
|  / 1 / origin | live&#95;generation |
|  / 1 / profile id | claude-sonnet-5-5&#64;3 |
|  / 1 / provider | anthropic-live |
|  / 1 / replay capture verified | Not supplied |
|  / 1 / replay request identical | Not supplied |
|  / 1 / request id | req&#95;011CfxZVwrcDhJ2ziUYv2uLF |
|  / 1 / requested model | claude-sonnet-5-5 |
|  / 1 / reserved microusd | 241726 |
|  / 1 / retry denied | Not supplied |
|  / 1 / returned model | claude-sonnet-5-5 |
|  / 1 / role | primary |
|  / 1 / slot key | aa-p10-live-retest-LR-02&#124;claude-sonnet-5-5&#64;3&#124;primary |
|  / 1 / stop reason | end&#95;turn |
|  / 1 / usage / cache creation input tokens | 0 |
|  / 1 / usage / cache read input tokens | 0 |
|  / 1 / usage / input tokens | 14991 |
|  / 1 / usage / output tokens | 6701 |

## Original claim

Verbatim quoted input; foreign text is not a trusted status message.

```
Drinking green tea daily prevents memory decline in adults aged 65 and older.
```

## Scientific judgments

### Selected scientific assessment

| Field | Recorded value |
| --- | --- |
| assessed composite state | unknown |
| assurance scope | Validates represented structure and semantic constraints; does not prove complete or correct model extraction, scientific truth or efficacy. |
| composite state | unknown |
| contract version | AA-P8/1.2 |
| derived label | correlation&#95;vs&#95;causation |
| host composite state | unknown |
| host derived copies | No entries recorded |
| host rule version | AA-P8-HOST/1.1 |
| input sha256 | 7bd28abce14fe9a42f3d635952e85cc0e6666a9a540b2091e77ce11ff13e77b1 |
| limitations | Checks validate represented semantics and source spans; they do not prove correct model extraction, exhaustive evidence search, scientific truth or live-model accuracy. |
| model composite state | unsupported |
| model host conflicts / 1 / host rule version | AA-P8-HOST/1.1 |
| model host conflicts / 1 / host state | unknown |
| model host conflicts / 1 / model state | unsupported |
| model host conflicts / 1 / proposition id | claim&#58;p1 |
| model host conflicts / 1 / reason | Model judgment and host evidence derivation differ; mandatory review decides, not either side |
| model host conflicts / 1 / required | true |
| model host conflicts / 1 / scope | proposition |
| model host conflicts / 2 / host rule version | AA-P8-HOST/1.1 |
| model host conflicts / 2 / host state | unknown |
| model host conflicts / 2 / model state | unsupported |
| model host conflicts / 2 / proposition id | Not supplied |
| model host conflicts / 2 / reason | Composite of the model judgments differs from the composite of the host derivation |
| model host conflicts / 2 / required | true |
| model host conflicts / 2 / scope | composite |
| original model label | correlation&#95;vs&#95;causation |
| raw response sha256 | ca8c6d0dd0e45e15d394ab2126a6404ad784cb908e04f4a021fee43814128053 |
| reasons | Ledger, evidence constraints and transformations evaluated under AA-P8/1.2 (AA-P8-HOST/1.1)<br>2 open model/host conflict(s); effective state unknown where they occur |
| record fingerprint | 1898ad442db84692caeb99f9a732c2e35c9cdd9b2b3f30e843f6a17a8ff9009d |
| technical status | completed |
| transformation findings | No entries recorded |

### Proposition judgments

| Field | Recorded value |
| --- | --- |
|  / 1 / dependency status | unknown |
|  / 1 / derived state | unknown |
|  / 1 / evidence ids | ev1<br>ev2 |
|  / 1 / host reasons | binding 1&#58; preserved observation&#58; inconclusive<br>binding 2&#58; preserved observation&#58; inconclusive<br>evidence dependence&#58; unknown; no independent corroboration inferred |
|  / 1 / host state | unknown |
|  / 1 / model host conflict | true |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reasons | A causal prevention claim rests only on a confounded, unadjusted, cross-sectional association.<br>Absence of causal evidence is not proof of no effect.<br>b1&#58; A cross-sectional association with a single memory score does not show prevention of decline.<br>preserved observation&#58; inconclusive<br>b2&#58; Unadjusted differences in physical activity and education confound the association.<br>preserved observation&#58; inconclusive<br>evidence dependence&#58; unknown; no independent corroboration inferred<br>model judgment unsupported differs from host evidence derivation unknown (AA-P8-HOST/1.1); open conflict, effective state unknown until a mandatory review resolves it |
|  / 1 / reported verdict | unsupported |
|  / 1 / required | true |

## Original label and taxonomy

### Original versus derived classification

| Field | Recorded value |
| --- | --- |
| derived taxonomy | correlation&#95;vs&#95;causation |
| original model label | correlation&#95;vs&#95;causation |
| represented trigger analysis / causal claim | true |
| represented trigger analysis / core error | causal&#95;inference |
| represented trigger analysis / described biological mechanism | false |
| represented trigger analysis / evidence ids | ev1<br>ev2 |
| represented trigger analysis / implies human benefit | true |
| represented trigger analysis / noncausal result used | true |
| represented trigger analysis / proposition ids | claim&#58;p1 |
| represented trigger analysis / reason | The claim asserts causal prevention, but the only evidence is an unadjusted cross-sectional association confounded by physical activity and education. |
| represented trigger analysis / trigger evidence id | ev1 |
| represented trigger analysis / trigger proposition id | claim&#58;p1 |
| represented trigger analysis / trigger quote | prevents memory decline |
| taxonomy check / assurance scope | Taxonomy decisions check represented trigger, core-error and evidence/proposition consistency. Quote containment does not prove entailment or correct model interpretation. |
| taxonomy check / derived label | correlation&#95;vs&#95;causation |
| taxonomy check / reasons | Source-bound noncausal result is used causally and is the core error |
| taxonomy check / technical status | completed |

## Propositions and inference limits

### Claim composition

| Field | Recorded value |
| --- | --- |
| claim id | claim |
| extraction provenance | Single sentence claim taken verbatim from the task prompt. |
| logic / children | No entries recorded |
| logic / operator | leaf |
| logic / proposition id | claim&#58;p1 |
| provenance id | prov1 |
| required proposition ids | claim&#58;p1 |

### Proposition claim&#58;p1

| Field | Recorded value |
| --- | --- |
| derived judgment / dependency status | unknown |
| derived judgment / derived state | unknown |
| derived judgment / evidence ids | ev1<br>ev2 |
| derived judgment / host reasons | binding 1&#58; preserved observation&#58; inconclusive<br>binding 2&#58; preserved observation&#58; inconclusive<br>evidence dependence&#58; unknown; no independent corroboration inferred |
| derived judgment / host state | unknown |
| derived judgment / model host conflict | true |
| derived judgment / proposition id | claim&#58;p1 |
| derived judgment / reasons | A causal prevention claim rests only on a confounded, unadjusted, cross-sectional association.<br>Absence of causal evidence is not proof of no effect.<br>b1&#58; A cross-sectional association with a single memory score does not show prevention of decline.<br>preserved observation&#58; inconclusive<br>b2&#58; Unadjusted differences in physical activity and education confound the association.<br>preserved observation&#58; inconclusive<br>evidence dependence&#58; unknown; no independent corroboration inferred<br>model judgment unsupported differs from host evidence derivation unknown (AA-P8-HOST/1.1); open conflict, effective state unknown until a mandatory review resolves it |
| derived judgment / reported verdict | unsupported |
| derived judgment / required | true |
| material dimensions | population<br>intervention<br>endpoint |
| materiality | required |
| not applicable / comparator | The claim states no comparator. |
| not applicable / follow up | The claim states no follow-up period. |
| observation target | Not supplied |
| parent claim id | claim |
| premise proposition ids | No entries recorded |
| proposition id | claim&#58;p1 |
| provenance id | prov1 |
| reason | A causal prevention claim rests only on a confounded, unadjusted, cross-sectional association. |
| reported verdict | unsupported |
| required bridge ids | No entries recorded |
| search question | Is there evidence that daily green tea drinking prevents memory decline in adults aged 65 and older? |
| search scope ids | ss1 |
| uncertainty | Absence of causal evidence is not proof of no effect. |

Quoted proposition; this is represented input, not a release assertion.

```
Drinking green tea daily prevents memory decline in adults aged 65 and older.
```

### Original span

| Field | Recorded value |
| --- | --- |
| end | 77 |
| start | 0 |
| text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |

### Population, endpoint, product and inference attributes

| Field | Recorded value |
| --- | --- |
| certainty | stated as fact |
| comparator | Not supplied |
| endpoint | memory decline |
| endpoint type | functional |
| follow up | Not supplied |
| intervention | daily green tea drinking |
| population | adults aged 65 and older |
| relation | causal |
| species | human |

### Evidence bindings and directness

| Field | Recorded value |
| --- | --- |
|  / 1 / binding id | b1 |
|  / 1 / directness | partial |
|  / 1 / evidence id | ev1 |
|  / 1 / observation | inconclusive |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reason | A cross-sectional association with a single memory score does not show prevention of decline. |
|  / 1 / search scope id | ss1 |
|  / 2 / binding id | b2 |
|  / 2 / directness | partial |
|  / 2 / evidence id | ev2 |
|  / 2 / observation | inconclusive |
|  / 2 / proposition id | claim&#58;p1 |
|  / 2 / reason | Unadjusted differences in physical activity and education confound the association. |
|  / 2 / search scope id | ss1 |

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
| asserted state | unsupported |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | stated as fact |
| from and to attributes (identical) / comparator | Not supplied |
| from and to attributes (identical) / endpoint | memory decline |
| from and to attributes (identical) / endpoint type | functional |
| from and to attributes (identical) / follow up | Not supplied |
| from and to attributes (identical) / intervention | daily green tea drinking |
| from and to attributes (identical) / population | adults aged 65 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from and to text (identical) | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| from proposition ids | claim&#58;p1 |
| reason | Unchanged extraction of the full claim. |
| stage | extraction |
| target id | claim&#58;p1 |
| transformation id | t1 |

### Transformation t2

| Field | Recorded value |
| --- | --- |
| asserted state | unsupported |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | stated as fact |
| from and to attributes (identical) / comparator | Not supplied |
| from and to attributes (identical) / endpoint | memory decline |
| from and to attributes (identical) / endpoint type | functional |
| from and to attributes (identical) / follow up | Not supplied |
| from and to attributes (identical) / intervention | daily green tea drinking |
| from and to attributes (identical) / population | adults aged 65 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| reason | The question keeps the claim&#x27;s meaning and attributes unchanged. |
| stage | search&#95;question |
| target id | claim&#58;p1 |
| to text | Is there evidence that daily green tea drinking prevents memory decline in adults aged 65 and older? |
| transformation id | t2 |

### Transformation t3

| Field | Recorded value |
| --- | --- |
| asserted state | unsupported |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | stated as fact |
| from and to attributes (identical) / comparator | Not supplied |
| from and to attributes (identical) / endpoint | memory decline |
| from and to attributes (identical) / endpoint type | functional |
| from and to attributes (identical) / follow up | Not supplied |
| from and to attributes (identical) / intervention | daily green tea drinking |
| from and to attributes (identical) / population | adults aged 65 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| reason | The internal finding restates the proposition with an unsupported verdict. |
| stage | internal |
| target id | claim&#58;p1 |
| to text | Drinking green tea daily prevents memory decline in adults aged 65 and older.<br>Unsupported&#58; only an unadjusted, confounded cross-sectional association with a single memory score. |
| transformation id | t3 |

### Transformation t4

| Field | Recorded value |
| --- | --- |
| asserted state | unsupported |
| asserts whole claim | true |
| from and to attributes (identical) / certainty | stated as fact |
| from and to attributes (identical) / comparator | Not supplied |
| from and to attributes (identical) / endpoint | memory decline |
| from and to attributes (identical) / endpoint type | functional |
| from and to attributes (identical) / follow up | Not supplied |
| from and to attributes (identical) / intervention | daily green tea drinking |
| from and to attributes (identical) / population | adults aged 65 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| reason | The client summary states that the causal claim is not shown, consistent with the unsupported verdict. |
| stage | summary |
| target id | cf1 |
| to text | The evidence does not show that daily green tea prevents memory decline in adults 65 and older.<br>It shows only a slight, unadjusted association in a one-time survey, confounded by activity and education. |
| transformation id | t4 |

## Evidence and source quotations

Quotations are supplied source text. Evidence type, direction and semantic attributes are represented extraction; the checks do not authenticate study findings.

### Evidence ev1

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint | memory test score |
| evidence id | ev1 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | supporting |
| source id | context |
| value origin | source&#95;reported |

Evidence text and exact source reference (identical)&#58;

```
People who reported drinking green tea daily scored slightly higher on that test than people who rarely drank it
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / certainty | Not supplied |
| attributes / comparator | rarely drinking green tea |
| attributes / comparison | Not supplied |
| attributes / effect direction | higher score in daily drinkers |
| attributes / effect magnitude | slightly higher |
| attributes / endpoint | memory test score |
| attributes / endpoint type | functional |
| attributes / follow up | Not supplied |
| attributes / intervention | daily green tea drinking |
| attributes / population | adults aged 65 and older |
| attributes / relation | association |
| attributes / species | human |
| design limitations | one-time survey<br>single memory test<br>self-reported tea habits<br>unadjusted for confounders |
| evidence id | ev1 |
| evidence type | observational |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | false |
| source role | cross-sectional survey result |
| underlying evidence ids | No entries recorded |

### Evidence ev2

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint |  |
| evidence id | ev2 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | weakening |
| source id | context |
| value origin | source&#95;reported |

Evidence text and exact source reference (identical)&#58;

```
daily tea drinkers were also more physically active and more often had completed higher education, and the comparison was not adjusted for these differences
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / intervention | daily green tea drinking |
| attributes / population | adults aged 65 and older |
| attributes / species | human |
| design limitations | unadjusted confounding by physical activity and education |
| evidence id | ev2 |
| evidence type | observational |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | false |
| source role | confounding information |
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
A one-time survey of 2,000 adults aged 65 and older asked about tea habits and gave each person a single memory test. People who reported drinking green tea daily scored slightly higher on that test than people who rarely drank it; daily tea drinkers were also more physically active and more often had completed higher education, and the comparison was not adjusted for these differences.
```

## Finding and client traces

### Provenance

| Field | Recorded value |
| --- | --- |
|  / 1 / canonical url | Not supplied |
|  / 1 / content fingerprint | Not supplied |
|  / 1 / context after | Not supplied |
|  / 1 / context before | Not supplied |
|  / 1 / exact claim text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
|  / 1 / page title | Not supplied |
|  / 1 / provenance id | prov1 |
|  / 1 / provenance state | archived&#95;snapshot |
|  / 1 / retrieved at | Not supplied |
|  / 1 / source id | input |

### Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / allowed summary strength | not&#95;directly&#95;established |
|  / 1 / confidence status |  |
|  / 1 / contrary evidence ids | ev2 |
|  / 1 / finding id | claim&#58;p1 |
|  / 1 / predicted label | correlation&#95;vs&#95;causation |
|  / 1 / proposition | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
|  / 1 / provenance id | prov1 |
|  / 1 / supporting evidence ids | ev1 |
|  / 1 / verdict summary | Unsupported&#58; only an unadjusted, confounded cross-sectional association with a single memory score. |

### Client Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / client explanation | It shows only a slight, unadjusted association in a one-time survey, confounded by activity and education. |
|  / 1 / client finding id | cf1 |
|  / 1 / client negative assertions | No entries recorded |
|  / 1 / client strength | not&#95;directly&#95;established |
|  / 1 / display claim | The evidence does not show that daily green tea prevents memory decline in adults 65 and older. |
|  / 1 / parent finding id | claim&#58;p1 |
|  / 1 / provenance id | prov1 |
|  / 1 / referenced evidence ids | ev1<br>ev2 |
|  / 1 / value claims | No entries recorded |

## UNKNOWN, conflicts and review history

### Current review state

| Field | Recorded value |
| --- | --- |
| assurance scope | Checks represented positions, identity, materiality and routing. No majority vote, scientific truth, reviewer independence or release authorization is inferred. |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| contract version | AA-P9/1.2 |
| execution status | not&#95;executed |
| mandatory | true |
| reasons | Routing preserves separate scientific/taxonomy layers; no majority or provider call executed |
| review state | unresolved |
| route | UNRESOLVED |
| technical status | completed |
| uncertainty | p9position&#58;caf22e55c19b3fff985d3730/claim&#58;p1&#58; scientific UNKNOWN |

### Current revalidated assessment

| Field | Recorded value |
| --- | --- |
| assessment fingerprint | 647d6ae1f00b82e7d0a7923356af30f1366449110de0e9821fa52fb5bda83429 |
| history validation | Not supplied |
| interpretation | Current revalidated state |
| route | UNRESOLVED |
| source reference | record.json&#35;/run&#95;record |
| technical status | completed |

### Position p9position&#58;caf22e55c19b3fff985d3730

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| claim id | claim |
| complete analysis reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0 |
| derived taxonomy | correlation&#95;vs&#95;causation |
| model | claude-sonnet-5-5 |
| origin | original |
| original model label | correlation&#95;vs&#95;causation |
| position id | p9position&#58;caf22e55c19b3fff985d3730 |
| provider | anthropic-live |
| raw response reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0/agent&#95;result/raw&#95;output |
| raw sha256 | ca8c6d0dd0e45e15d394ab2126a6404ad784cb908e04f4a021fee43814128053 |
| run id | 241dad22-2b52-40f4-b2d5-011f8f7b5415 |
| scientific state | unknown |
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
| usage / input tokens | 14991 |
| usage / output tokens | 6701 |

### Trigger

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| claim id | claim |
| code | model&#95;host&#95;conflict |
| evidence ids | ev1<br>ev2 |
| field | propositions.claim&#58;p1.model&#95;host&#95;conflict |
| mandatory | true |
| material | true |
| position ids | p9position&#58;caf22e55c19b3fff985d3730 |
| projected object fingerprint | 06a81756952c6b504c3324ec2f35d9e627bef9ba16843a03082e70ada174bdc7 |
| proposition ids | claim&#58;p1 |
| reason | Model judgment unsupported differs from host evidence derivation unknown (AA-P8-HOST/1.1); mandatory review; neither side is adopted automatically |
| source reference | record.json&#35;/run&#95;record/metadata/phase9/triggers/0 |
| trigger id | p9trigger&#58;1a8fd8b526f2ae87952ee42d |

### Trigger

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| claim id | claim |
| code | model&#95;host&#95;conflict |
| evidence ids | ev1<br>ev2 |
| field | phase8.composite&#95;model&#95;host&#95;conflict |
| mandatory | true |
| material | true |
| position ids | p9position&#58;caf22e55c19b3fff985d3730 |
| projected object fingerprint | b81fd46a81b3dca1abba6a73e727bcbb62196ffb867851bfe3619185709367a1 |
| proposition ids | No entries recorded |
| reason | Model judgment unsupported differs from host evidence derivation unknown (AA-P8-HOST/1.1); mandatory review; neither side is adopted automatically |
| source reference | record.json&#35;/run&#95;record/metadata/phase9/triggers/1 |
| trigger id | p9trigger&#58;a77d4d5b2320880c7cec0c1c |

### Trigger

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| claim id | claim |
| code | necessary&#95;unknown |
| evidence ids | ev1<br>ev2 |
| field | propositions.claim&#58;p1.derived&#95;state |
| mandatory | true |
| material | true |
| position ids | p9position&#58;caf22e55c19b3fff985d3730 |
| projected object fingerprint | 61cf1877011c35a40f6f7999fb919e39835237e41b6723390f4a960675766332 |
| proposition ids | claim&#58;p1 |
| reason | Scientific UNKNOWN affects admissible output |
| source reference | record.json&#35;/run&#95;record/metadata/phase9/triggers/2 |
| trigger id | p9trigger&#58;b1b531e54a52582393e21148 |

### Attempt

| Field | Recorded value |
| --- | --- |
| code version | cc70c2a220e6998a9c45e4e9e828722afe2df2eaed79d8ad3ff6ce631eb804c6 |
| contract version | AA-P9/1.2 |
| kind | counterreview |
| packet sha256 | 932e3bd7f97a015d2cc2e0f402dcf63e7b90cf1cc039ed7cce2641c67aa699dd |
| projected object fingerprint | 03195af32277466a93ebac9196514919d82f65205cbe01992eb3abffa6fb03d1 |
| reason | Review cap for this model reached (1 counterreview per profile under AA-P10-LIVE-RETEST-20261011-004); the review stays open |
| source reference | record.json&#35;/run&#95;record/metadata/phase9/attempts/0 |
| status | denied |
| timestamp | 2026-10-12T15&#58;14&#58;55.209444+00&#58;00 |

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
| value&#95;origin&#95;provenance / 1.0.0 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 2<br>Evaluated&#58; 2<br>Reason&#58; Evaluated client&#95;visible&#95;evidence&#95;references |
| search&#95;scope&#95;binding / 1.0.0 | Execution&#58; executed<br>Outcome&#58; not&#95;applicable<br>Eligible&#58; 0<br>Evaluated&#58; 0<br>Reason&#58; Host-derived N/A&#58; no client&#95;negative&#95;assertions; check executed successfully |
| phase8&#95;semantics&#95;taxonomy / 1.2 | Execution&#58; executed<br>Outcome&#58; pass<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; Current semantic and separate taxonomy analysis required |
| phase9&#95;history&#95;review / 1.2 | Execution&#58; executed<br>Outcome&#58; fail<br>Eligible&#58; 1<br>Evaluated&#58; 1<br>Reason&#58; All original/review/adjudication carriers and mandatory review revalidated |
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
| analysis fingerprint | e6f510332ae244a175ec997502546f577f6e1cedb815098facb8e0139a5612d1 |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| code / code fingerprint | a1654da6afd6991665f2e4d25824c4e21fc152d69eddef01fe9a9cacf64eb80d |
| code / complete module hash index | manifest.json&#35;/provenance/code/module&#95;hashes |
| code / module count | 74 |
| code / source binding | verified Git source bytes |
| code / verified source commit | 63399dd1c3093d21a9307630ba85a6f85e4fa450 |
| config | live-anthropic-v1 |
| contract | AA-P10/1.0 |
| contract addendum | AA-P10-LIVE/1.0 |
| evidence fingerprint | 64928ff96b534d52cd4c1a37bb2fd1b2334c4711e941274a6b8896d165164cfe |
| execution evidence / 1 / attempt ids | attempt-008 |
| execution evidence / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
| execution evidence / 1 / billing | usage&#95;reported |
| execution evidence / 1 / capture sha256 | 24c6687c7077c298a725821ee46482e398c383318f9b8282e05a332bbce2d95e |
| execution evidence / 1 / completion state | complete |
| execution evidence / 1 / confirmed cost microusd | 96992 |
| execution evidence / 1 / current execution | live&#95;generation |
| execution evidence / 1 / denial reason | Not supplied |
| execution evidence / 1 / latency ms | 38327 |
| execution evidence / 1 / message id | msg&#95;011CfxZVx6z983i8CkVN2hry |
| execution evidence / 1 / model | claude-sonnet-5-5 |
| execution evidence / 1 / origin | live&#95;generation |
| execution evidence / 1 / profile id | claude-sonnet-5-5&#64;3 |
| execution evidence / 1 / provider | anthropic-live |
| execution evidence / 1 / replay capture verified | Not supplied |
| execution evidence / 1 / replay request identical | Not supplied |
| execution evidence / 1 / request id | req&#95;011CfxZVwrcDhJ2ziUYv2uLF |
| execution evidence / 1 / requested model | claude-sonnet-5-5 |
| execution evidence / 1 / reserved microusd | 241726 |
| execution evidence / 1 / retry denied | Not supplied |
| execution evidence / 1 / returned model | claude-sonnet-5-5 |
| execution evidence / 1 / role | primary |
| execution evidence / 1 / slot key | aa-p10-live-retest-LR-02&#124;claude-sonnet-5-5&#64;3&#124;primary |
| execution evidence / 1 / stop reason | end&#95;turn |
| execution evidence / 1 / usage / cache creation input tokens | 0 |
| execution evidence / 1 / usage / cache read input tokens | 0 |
| execution evidence / 1 / usage / input tokens | 14991 |
| execution evidence / 1 / usage / output tokens | 6701 |
| execution mode | live&#95;generation |
| execution mode errors | No entries recorded |
| input fingerprint | 6a8aa35c6b3ecfc5772382e9037b4be55069c9eff6697619a05d734577b8098a |
| ledger fingerprint | cd1b2b27a08b68bea9a4084102a1425a9cb16250ee22585c7f18aebc61e85d77 |
| package version | 0.1.0 |
| phase8 summary / composite state | unknown |
| phase8 summary / derived label | correlation&#95;vs&#95;causation |
| phase8 summary / original model label | correlation&#95;vs&#95;causation |
| phase8 summary / taxonomy status | completed |
| phase8 summary / technical status | completed |
| phase9 summary / execution status | not&#95;executed |
| phase9 summary / final position id | Not supplied |
| phase9 summary / history validation | Not supplied |
| phase9 summary / mandatory | true |
| phase9 summary / review state | unresolved |
| phase9 summary / route | UNRESOLVED |
| phase9 summary / technical status | completed |
| providers / 1 / model | claude-sonnet-5-5 |
| providers / 1 / provider | anthropic-live |
| providers / 1 / usage / cache creation input tokens | 0 |
| providers / 1 / usage / cache read input tokens | 0 |
| providers / 1 / usage / input tokens | 14991 |
| providers / 1 / usage / output tokens | 6701 |
| recording notice | LIVE MODEL GENERATION (AA-P10-LIVE/1.0); see execution evidence for model, request IDs and cost |
| review counts / adjudications | 0 |
| review counts / attempts | 1 |
| review counts / conflicts | 0 |
| review counts / positions | 1 |
| review fingerprint | 647d6ae1f00b82e7d0a7923356af30f1366449110de0e9821fa52fb5bda83429 |
| run id | 241dad22-2b52-40f4-b2d5-011f8f7b5415 |
| selected position id | p9position&#58;caf22e55c19b3fff985d3730 |

Complete original responses, all review carriers and machine bindings&#58; record.json. Final control decision&#58; decision.json. File hashes and full source index&#58; manifest.json. Hashes verify integrity, not actor identity or authentication.

