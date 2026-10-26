# Canonical local audit

## Execution and release

RELEASED — local artifact status

LIVE MODEL GENERATION (AA-P10-LIVE/1.0). Actual provider calls produced the analysed responses; model, request IDs, attempts and cost are bound below and in record.json. Local artifact decision only; no scientific truth, empirical validation, external evidence search or customer approval.

### Independent states

| Field | Recorded value |
| --- | --- |
| analysis execution | completed |
| host evidence derivation (composite) | unsupported |
| local release | RELEASED |
| mandatory review | false |
| model judgment (composite) | unsupported |
| model/host conflicts | none recorded |
| review execution | not&#95;executed |
| review route | AUTO&#95;RESOLVABLE |
| scientific judgment | unsupported |

### Explicit release intent

| Field | Recorded value |
| --- | --- |
| reason | AA-P10 live retest LR-02&#58; technical release-path check on a synthetic sketch case (not a real study, no gold label) |
| reviewer | TEST ONLY - not a scientific release |
| scope | local&#95;artifact&#95;only |

### Revision identity

| Field | Recorded value |
| --- | --- |
| created at | 2026-10-12T15&#58;15&#58;25.198503+00&#58;00 |
| parent / manifest fingerprint | 14e04abf4c55fd1e2cf17afaa7cdfb54345f746efe99109fe9680d854b0c31c7 |
| parent / revision id | 39abb806-d9db-4c35-a6d4-d3736e21ca0d |
| record fingerprint | eb4775978aff3645c0556f2301f69c06cec324d26989d6b1142ca05fc5914b5b |
| revision | 732a4d49-2f45-48f8-b4f9-adb502de6ad2 |
| selected position id | p9position&#58;37f303ae0a3424cb3d2aefa4 |

### Execution provenance per carrier

| Field | Recorded value |
| --- | --- |
|  / 1 / attempt ids | attempt-003 |
|  / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
|  / 1 / billing | usage&#95;reported |
|  / 1 / capture sha256 | 133d16e982165dbe1ce1eec66299d59da01d81cacda1387d7f371baaa5682edf |
|  / 1 / completion state | complete |
|  / 1 / confirmed cost microusd | 8316 |
|  / 1 / current execution | live&#95;generation |
|  / 1 / denial reason | Not supplied |
|  / 1 / latency ms | 49657 |
|  / 1 / message id | msg&#95;011CfxZDo6oXdHDHfkuDHoDB |
|  / 1 / model | claude-haiku-5-5 |
|  / 1 / origin | live&#95;generation |
|  / 1 / profile id | claude-haiku-5-5&#64;3 |
|  / 1 / provider | anthropic-live |
|  / 1 / replay capture verified | Not supplied |
|  / 1 / replay request identical | Not supplied |
|  / 1 / request id | req&#95;011CfxZDnHT8TojgvjiFmpQZ |
|  / 1 / requested model | claude-haiku-5-5 |
|  / 1 / reserved microusd | 28087 |
|  / 1 / retry denied | Not supplied |
|  / 1 / returned model | claude-haiku-5-5 |
|  / 1 / role | primary |
|  / 1 / slot key | aa-p10-live-retest-LR-02&#124;claude-haiku-5-5&#64;3&#124;primary |
|  / 1 / stop reason | end&#95;turn |
|  / 1 / usage / cache creation input tokens | 0 |
|  / 1 / usage / cache read input tokens | 0 |
|  / 1 / usage / input tokens | 14991 |
|  / 1 / usage / output tokens | 13632 |

## Original claim

Verbatim quoted input; foreign text is not a trusted status message.

```
Drinking green tea daily prevents memory decline in adults aged 65 and older.
```

## Scientific judgments

### Selected scientific assessment

| Field | Recorded value |
| --- | --- |
| assessed composite state | unsupported |
| assurance scope | Validates represented structure and semantic constraints; does not prove complete or correct model extraction, scientific truth or efficacy. |
| composite state | unsupported |
| contract version | AA-P8/1.2 |
| derived label | correlation&#95;vs&#95;causation |
| host composite state | unsupported |
| host derived copies | tr&#58;extraction&#58;claim&#58;p1&#58; extraction from&#95;attributes empty; meaning audit used the validated proposition attributes (host-derived copy, not model content) |
| host rule version | AA-P8-HOST/1.1 |
| input sha256 | 7bd28abce14fe9a42f3d635952e85cc0e6666a9a540b2091e77ce11ff13e77b1 |
| limitations | Checks validate represented semantics and source spans; they do not prove correct model extraction, exhaustive evidence search, scientific truth or live-model accuracy. |
| model composite state | unsupported |
| model host conflicts | No entries recorded |
| original model label | correlation&#95;vs&#95;causation |
| raw response sha256 | f302a4f9587b3d9bc1b885a9a62add8a978a1541ac1c959fef02338c30d13d9f |
| reasons | Ledger, evidence constraints and transformations evaluated under AA-P8/1.2 (AA-P8-HOST/1.1) |
| record fingerprint | 61f04b4215ed147c76cf69142e4b271569860c6302f1b8449f6e340d3d322926 |
| technical status | completed |
| transformation findings | No entries recorded |

### Proposition judgments

| Field | Recorded value |
| --- | --- |
|  / 1 / dependency status | unknown |
|  / 1 / derived state | unsupported |
|  / 1 / evidence ids | ev&#58;1<br>ev&#58;2 |
|  / 1 / host reasons | binding 1&#58; preserved observation&#58; inconclusive<br>binding 2&#58; preserved observation&#58; inconclusive<br>required bridge 1&#58; required bridge unsupported, capable evidence unresolved<br>evidence dependence&#58; unknown; no independent corroboration inferred |
|  / 1 / host state | unsupported |
|  / 1 / model host conflict | false |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reasons | The only evidence is a confounded, unadjusted, one-time cross-sectional association that does not establish prevention.<br>No effect size, confidence interval or p-value is supplied.<br>No follow-up over time is reported, so decline cannot be observed.<br>bind&#58;1&#58; A one-time cross-sectional score difference is an association, indirect for a preventive effect on decline over time.<br>preserved observation&#58; inconclusive<br>bind&#58;2&#58; The statement that the comparison was unadjusted limits any causal reading of ev&#58;1.<br>preserved observation&#58; inconclusive<br>br&#58;1&#58; required bridge unsupported, capable evidence unresolved<br>evidence dependence&#58; unknown; no independent corroboration inferred |
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
| represented trigger analysis / evidence ids | ev&#58;1<br>ev&#58;2 |
| represented trigger analysis / implies human benefit | true |
| represented trigger analysis / noncausal result used | true |
| represented trigger analysis / proposition ids | claim&#58;p1 |
| represented trigger analysis / reason | The claim asserts a preventive causal effect on decline, but the only evidence is a one-time, unadjusted, confounded cross-sectional association. No mechanism is described. |
| represented trigger analysis / trigger evidence id | ev&#58;1 |
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
| extraction provenance | Single required proposition extracted from the full task prompt; the context supplies the only evidence. |
| logic / children | No entries recorded |
| logic / operator | leaf |
| logic / proposition id | claim&#58;p1 |
| provenance id | prov&#58;input |
| required proposition ids | claim&#58;p1 |

### Proposition claim&#58;p1

| Field | Recorded value |
| --- | --- |
| derived judgment / dependency status | unknown |
| derived judgment / derived state | unsupported |
| derived judgment / evidence ids | ev&#58;1<br>ev&#58;2 |
| derived judgment / host reasons | binding 1&#58; preserved observation&#58; inconclusive<br>binding 2&#58; preserved observation&#58; inconclusive<br>required bridge 1&#58; required bridge unsupported, capable evidence unresolved<br>evidence dependence&#58; unknown; no independent corroboration inferred |
| derived judgment / host state | unsupported |
| derived judgment / model host conflict | false |
| derived judgment / proposition id | claim&#58;p1 |
| derived judgment / reasons | The only evidence is a confounded, unadjusted, one-time cross-sectional association that does not establish prevention.<br>No effect size, confidence interval or p-value is supplied.<br>No follow-up over time is reported, so decline cannot be observed.<br>bind&#58;1&#58; A one-time cross-sectional score difference is an association, indirect for a preventive effect on decline over time.<br>preserved observation&#58; inconclusive<br>bind&#58;2&#58; The statement that the comparison was unadjusted limits any causal reading of ev&#58;1.<br>preserved observation&#58; inconclusive<br>br&#58;1&#58; required bridge unsupported, capable evidence unresolved<br>evidence dependence&#58; unknown; no independent corroboration inferred |
| derived judgment / reported verdict | unsupported |
| derived judgment / required | true |
| material dimensions | population<br>intervention<br>endpoint<br>relation |
| materiality | required |
| not applicable / certainty | claim states no certainty level |
| not applicable / comparator | claim names no comparator |
| not applicable / comparison | claim does not state design or comparison |
| not applicable / dose | claim states no dose |
| not applicable / effect basis | claim states no effect basis |
| not applicable / effect magnitude | claim states no magnitude |
| not applicable / follow up | claim states no follow-up duration |
| not applicable / formulation | claim states no formulation |
| not applicable / route | claim states no route |
| observation target | Not supplied |
| parent claim id | claim |
| premise proposition ids | No entries recorded |
| proposition id | claim&#58;p1 |
| provenance id | prov&#58;input |
| reason | The only evidence is a confounded, unadjusted, one-time cross-sectional association that does not establish prevention. |
| reported verdict | unsupported |
| required bridge ids | br&#58;1 |
| search question | Does direct evidence show that daily green tea drinking prevents memory decline in adults aged 65 and older? |
| search scope ids | ss&#58;1 |
| uncertainty | No effect size, confidence interval or p-value is supplied.<br>No follow-up over time is reported, so decline cannot be observed. |

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
| certainty | Not supplied |
| comparator | Not supplied |
| comparison | Not supplied |
| dose | Not supplied |
| effect basis | Not supplied |
| effect direction | prevention of decline |
| effect magnitude | Not supplied |
| endpoint | memory decline |
| endpoint type | cognitive |
| follow up | Not supplied |
| formulation | Not supplied |
| intervention | daily green tea drinking |
| population | adults aged 65 and older |
| relation | causal |
| route | Not supplied |
| species | human |

### Evidence bindings and directness

| Field | Recorded value |
| --- | --- |
|  / 1 / binding id | bind&#58;1 |
|  / 1 / directness | indirect |
|  / 1 / evidence id | ev&#58;1 |
|  / 1 / observation | inconclusive |
|  / 1 / proposition id | claim&#58;p1 |
|  / 1 / reason | A one-time cross-sectional score difference is an association, indirect for a preventive effect on decline over time. |
|  / 1 / search scope id | ss&#58;1 |
|  / 2 / binding id | bind&#58;2 |
|  / 2 / directness | indirect |
|  / 2 / evidence id | ev&#58;2 |
|  / 2 / observation | inconclusive |
|  / 2 / proposition id | claim&#58;p1 |
|  / 2 / reason | The statement that the comparison was unadjusted limits any causal reading of ev&#58;1. |
|  / 2 / search scope id | ss&#58;1 |

### Bridges

| Field | Recorded value |
| --- | --- |
|  / 1 / bridge id | br&#58;1 |
|  / 1 / conclusion proposition id | claim&#58;p1 |
|  / 1 / dimensions | relation<br>comparison |
|  / 1 / evidence ids | ev&#58;1<br>ev&#58;2 |
|  / 1 / kind | causal&#95;identification |
|  / 1 / premise proposition ids | No entries recorded |
|  / 1 / reason | A one-time, unadjusted, confounded association cannot identify a preventive causal effect on memory decline. |
|  / 1 / state | unsupported |

### Product Transfers

| Field | Recorded value |
| --- | --- |
| Value | No entries recorded |

### Transformation tr&#58;extraction&#58;claim&#58;p1

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to text (identical) | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| from attributes | No entries recorded |
| from proposition ids | claim&#58;p1 |
| reason | Extraction keeps the full claim wording and records its semantic attributes; from&#95;attributes is left empty so the host uses the proposition attributes. |
| stage | extraction |
| target id | claim&#58;p1 |
| to attributes / certainty | Not supplied |
| to attributes / comparator | Not supplied |
| to attributes / comparison | Not supplied |
| to attributes / dose | Not supplied |
| to attributes / effect basis | Not supplied |
| to attributes / effect direction | prevention of decline |
| to attributes / effect magnitude | Not supplied |
| to attributes / endpoint | memory decline |
| to attributes / endpoint type | cognitive |
| to attributes / follow up | Not supplied |
| to attributes / formulation | Not supplied |
| to attributes / intervention | daily green tea drinking |
| to attributes / population | adults aged 65 and older |
| to attributes / relation | causal |
| to attributes / route | Not supplied |
| to attributes / species | human |
| transformation id | tr&#58;extraction&#58;claim&#58;p1 |

### Transformation tr&#58;search&#95;question&#58;claim&#58;p1

| Field | Recorded value |
| --- | --- |
| asserted state | Not supplied |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | Not supplied |
| from and to attributes (identical) / comparator | Not supplied |
| from and to attributes (identical) / comparison | Not supplied |
| from and to attributes (identical) / dose | Not supplied |
| from and to attributes (identical) / effect basis | Not supplied |
| from and to attributes (identical) / effect direction | prevention of decline |
| from and to attributes (identical) / effect magnitude | Not supplied |
| from and to attributes (identical) / endpoint | memory decline |
| from and to attributes (identical) / endpoint type | cognitive |
| from and to attributes (identical) / follow up | Not supplied |
| from and to attributes (identical) / formulation | Not supplied |
| from and to attributes (identical) / intervention | daily green tea drinking |
| from and to attributes (identical) / population | adults aged 65 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / route | Not supplied |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| reason | The search question restates the causal claim as a question to test against the reviewed set without changing its attributes. |
| stage | search&#95;question |
| target id | claim&#58;p1 |
| to text | Does direct evidence show that daily green tea drinking prevents memory decline in adults aged 65 and older? |
| transformation id | tr&#58;search&#95;question&#58;claim&#58;p1 |

### Transformation tr&#58;internal&#58;claim&#58;p1

| Field | Recorded value |
| --- | --- |
| asserted state | unsupported |
| asserts whole claim | false |
| from and to attributes (identical) / certainty | Not supplied |
| from and to attributes (identical) / comparator | Not supplied |
| from and to attributes (identical) / comparison | Not supplied |
| from and to attributes (identical) / dose | Not supplied |
| from and to attributes (identical) / effect basis | Not supplied |
| from and to attributes (identical) / effect direction | prevention of decline |
| from and to attributes (identical) / effect magnitude | Not supplied |
| from and to attributes (identical) / endpoint | memory decline |
| from and to attributes (identical) / endpoint type | cognitive |
| from and to attributes (identical) / follow up | Not supplied |
| from and to attributes (identical) / formulation | Not supplied |
| from and to attributes (identical) / intervention | daily green tea drinking |
| from and to attributes (identical) / population | adults aged 65 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / route | Not supplied |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| reason | The internal verdict summary matches the proposition&#x27;s reported verdict of unsupported. |
| stage | internal |
| target id | claim&#58;p1 |
| to text | Drinking green tea daily prevents memory decline in adults aged 65 and older.<br>Unsupported&#58; a one-time, unadjusted survey shows only a slight cross-sectional score difference, not prevention of decline. |
| transformation id | tr&#58;internal&#58;claim&#58;p1 |

### Transformation tr&#58;summary&#58;cf&#58;1

| Field | Recorded value |
| --- | --- |
| asserted state | unsupported |
| asserts whole claim | true |
| from and to attributes (identical) / certainty | Not supplied |
| from and to attributes (identical) / comparator | Not supplied |
| from and to attributes (identical) / comparison | Not supplied |
| from and to attributes (identical) / dose | Not supplied |
| from and to attributes (identical) / effect basis | Not supplied |
| from and to attributes (identical) / effect direction | prevention of decline |
| from and to attributes (identical) / effect magnitude | Not supplied |
| from and to attributes (identical) / endpoint | memory decline |
| from and to attributes (identical) / endpoint type | cognitive |
| from and to attributes (identical) / follow up | Not supplied |
| from and to attributes (identical) / formulation | Not supplied |
| from and to attributes (identical) / intervention | daily green tea drinking |
| from and to attributes (identical) / population | adults aged 65 and older |
| from and to attributes (identical) / relation | causal |
| from and to attributes (identical) / route | Not supplied |
| from and to attributes (identical) / species | human |
| from proposition ids | claim&#58;p1 |
| from text | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
| reason | The client summary matches the whole-claim judgment of unsupported and does not assert prevention. |
| stage | summary |
| target id | cf&#58;1 |
| to text | Green tea intake was associated with slightly higher memory test scores in one survey of older adults, which does not show that daily green tea prevents memory decline.<br>The survey was one-time, gave one memory test, and did not adjust for physical activity or education. The evidence cannot establish that daily green tea prevents memory decline. |
| transformation id | tr&#58;summary&#58;cf&#58;1 |

## Evidence and source quotations

Quotations are supplied source text. Evidence type, direction and semantic attributes are represented extraction; the checks do not authenticate study findings.

### Evidence ev&#58;1

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint | memory test score |
| evidence id | ev&#58;1 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | supporting |
| source id | context |
| value origin | Not supplied |

Evidence text and exact source reference (identical)&#58;

```
People who reported drinking green tea daily scored slightly higher on that test than people who rarely drank it
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / certainty | Not supplied |
| attributes / comparator | rarely drank green tea |
| attributes / comparison | between |
| attributes / dose | Not supplied |
| attributes / effect basis | Not supplied |
| attributes / effect direction | higher score in daily drinkers |
| attributes / effect magnitude | slight |
| attributes / endpoint | memory test score |
| attributes / endpoint type | cognitive |
| attributes / follow up | Not supplied |
| attributes / formulation | Not supplied |
| attributes / intervention | daily green tea drinking |
| attributes / population | adults aged 65 and older |
| attributes / relation | association |
| attributes / route | Not supplied |
| attributes / species | human |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | single time point<br>single memory test<br>not adjusted for physical activity or education |
| evidence id | ev&#58;1 |
| evidence type | observational |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | false |
| source role | one-time cross-sectional survey |
| study id | Not supplied |
| underlying evidence ids | No entries recorded |

### Evidence ev&#58;2

| Field | Recorded value |
| --- | --- |
| derivation method | Not supplied |
| derivation note | Not supplied |
| endpoint | memory test score |
| evidence id | ev&#58;2 |
| input evidence ids | No entries recorded |
| material | true |
| reported value | Not supplied |
| role | weakening |
| source id | context |
| value origin | Not supplied |

Evidence text and exact source reference (identical)&#58;

```
the comparison was not adjusted for these differences
```

### Source type, capability and dependence

| Field | Recorded value |
| --- | --- |
| attributes / certainty | Not supplied |
| attributes / comparator | rarely drank green tea |
| attributes / comparison | between |
| attributes / dose | Not supplied |
| attributes / effect basis | Not supplied |
| attributes / effect direction | Not supplied |
| attributes / effect magnitude | Not supplied |
| attributes / endpoint | memory test score |
| attributes / endpoint type | cognitive |
| attributes / follow up | Not supplied |
| attributes / formulation | Not supplied |
| attributes / intervention | daily green tea drinking |
| attributes / population | adults aged 65 and older |
| attributes / relation | association |
| attributes / route | Not supplied |
| attributes / species | human |
| cohort id | Not supplied |
| dataset id | Not supplied |
| design limitations | no adjustment for confounders |
| evidence id | ev&#58;2 |
| evidence type | observational |
| identification argument | Not supplied |
| identification evidence ids | No entries recorded |
| quality | Not supplied |
| randomized | false |
| source role | limitation of the same cross-sectional survey |
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
|  / 1 / search completeness | Not supplied |
|  / 1 / search scope id | ss&#58;1 |

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
|  / 1 / provenance id | prov&#58;input |
|  / 1 / provenance state | archived&#95;snapshot |
|  / 1 / retrieved at | Not supplied |
|  / 1 / source id | input |

### Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / allowed summary strength | not&#95;assessed |
|  / 1 / confidence status | moderate |
|  / 1 / contrary evidence ids | ev&#58;2 |
|  / 1 / finding id | claim&#58;p1 |
|  / 1 / predicted label | unsupported |
|  / 1 / proposition | Drinking green tea daily prevents memory decline in adults aged 65 and older. |
|  / 1 / provenance id | prov&#58;input |
|  / 1 / supporting evidence ids | ev&#58;1 |
|  / 1 / verdict summary | Unsupported&#58; a one-time, unadjusted survey shows only a slight cross-sectional score difference, not prevention of decline. |

### Client Findings

| Field | Recorded value |
| --- | --- |
|  / 1 / client explanation | The survey was one-time, gave one memory test, and did not adjust for physical activity or education. The evidence cannot establish that daily green tea prevents memory decline. |
|  / 1 / client finding id | cf&#58;1 |
|  / 1 / client negative assertions | No entries recorded |
|  / 1 / client strength | not&#95;assessed |
|  / 1 / display claim | Green tea intake was associated with slightly higher memory test scores in one survey of older adults, which does not show that daily green tea prevents memory decline. |
|  / 1 / parent finding id | claim&#58;p1 |
|  / 1 / provenance id | prov&#58;input |
|  / 1 / referenced evidence ids | ev&#58;1<br>ev&#58;2 |
|  / 1 / value claims | No entries recorded |

## UNKNOWN, conflicts and review history

### Current review state

| Field | Recorded value |
| --- | --- |
| assurance scope | Checks represented positions, identity, materiality and routing. No majority vote, scientific truth, reviewer independence or release authorization is inferred. |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
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
| assessment fingerprint | d1c9229798c1ee226aa1fe1c0b0004dee24e8cd9fc4e5a007ae50b1248752393 |
| history validation | Not supplied |
| interpretation | Current revalidated state |
| route | AUTO&#95;RESOLVABLE |
| source reference | record.json&#35;/run&#95;record |
| technical status | completed |

### Position p9position&#58;37f303ae0a3424cb3d2aefa4

| Field | Recorded value |
| --- | --- |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| claim id | claim |
| complete analysis reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0 |
| derived taxonomy | correlation&#95;vs&#95;causation |
| model | claude-haiku-5-5 |
| origin | original |
| original model label | correlation&#95;vs&#95;causation |
| position id | p9position&#58;37f303ae0a3424cb3d2aefa4 |
| provider | anthropic-live |
| raw response reference | record.json&#35;/run&#95;record/metadata/phase9/positions/0/agent&#95;result/raw&#95;output |
| raw sha256 | f302a4f9587b3d9bc1b885a9a62add8a978a1541ac1c959fef02338c30d13d9f |
| run id | 18cd50b8-ad19-49be-818b-33c4a99e17f4 |
| scientific state | unsupported |
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
| usage / output tokens | 13632 |

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
| analysis fingerprint | b8d72494b0ac9946f41f9e1f73f764124dbfb5d496404f656eaa793c3db2046a |
| case id | p9case&#58;75f1717da77e0694a0afbab8 |
| code / code fingerprint | a1654da6afd6991665f2e4d25824c4e21fc152d69eddef01fe9a9cacf64eb80d |
| code / complete module hash index | manifest.json&#35;/provenance/code/module&#95;hashes |
| code / module count | 74 |
| code / source binding | verified Git source bytes |
| code / verified source commit | 63399dd1c3093d21a9307630ba85a6f85e4fa450 |
| config | live-anthropic-v1 |
| contract | AA-P10/1.0 |
| contract addendum | AA-P10-LIVE/1.0 |
| evidence fingerprint | a1297f1d5408398dda278dc4b1e6a199c15949f61cce1695caca0b2318134c84 |
| execution evidence / 1 / attempt ids | attempt-003 |
| execution evidence / 1 / authorization id | AA-P10-LIVE-RETEST-20261011-004 |
| execution evidence / 1 / billing | usage&#95;reported |
| execution evidence / 1 / capture sha256 | 133d16e982165dbe1ce1eec66299d59da01d81cacda1387d7f371baaa5682edf |
| execution evidence / 1 / completion state | complete |
| execution evidence / 1 / confirmed cost microusd | 8316 |
| execution evidence / 1 / current execution | live&#95;generation |
| execution evidence / 1 / denial reason | Not supplied |
| execution evidence / 1 / latency ms | 49657 |
| execution evidence / 1 / message id | msg&#95;011CfxZDo6oXdHDHfkuDHoDB |
| execution evidence / 1 / model | claude-haiku-5-5 |
| execution evidence / 1 / origin | live&#95;generation |
| execution evidence / 1 / profile id | claude-haiku-5-5&#64;3 |
| execution evidence / 1 / provider | anthropic-live |
| execution evidence / 1 / replay capture verified | Not supplied |
| execution evidence / 1 / replay request identical | Not supplied |
| execution evidence / 1 / request id | req&#95;011CfxZDnHT8TojgvjiFmpQZ |
| execution evidence / 1 / requested model | claude-haiku-5-5 |
| execution evidence / 1 / reserved microusd | 28087 |
| execution evidence / 1 / retry denied | Not supplied |
| execution evidence / 1 / returned model | claude-haiku-5-5 |
| execution evidence / 1 / role | primary |
| execution evidence / 1 / slot key | aa-p10-live-retest-LR-02&#124;claude-haiku-5-5&#64;3&#124;primary |
| execution evidence / 1 / stop reason | end&#95;turn |
| execution evidence / 1 / usage / cache creation input tokens | 0 |
| execution evidence / 1 / usage / cache read input tokens | 0 |
| execution evidence / 1 / usage / input tokens | 14991 |
| execution evidence / 1 / usage / output tokens | 13632 |
| execution mode | live&#95;generation |
| execution mode errors | No entries recorded |
| input fingerprint | 6a8aa35c6b3ecfc5772382e9037b4be55069c9eff6697619a05d734577b8098a |
| ledger fingerprint | 0a4a7215bd94d9a543de1e8f229bb6856b5c5111a035e2d01accc0faa7761b68 |
| package version | 0.1.0 |
| phase8 summary / composite state | unsupported |
| phase8 summary / derived label | correlation&#95;vs&#95;causation |
| phase8 summary / original model label | correlation&#95;vs&#95;causation |
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
| providers / 1 / usage / input tokens | 14991 |
| providers / 1 / usage / output tokens | 13632 |
| recording notice | LIVE MODEL GENERATION (AA-P10-LIVE/1.0); see execution evidence for model, request IDs and cost |
| review counts / adjudications | 0 |
| review counts / attempts | 0 |
| review counts / conflicts | 0 |
| review counts / positions | 1 |
| review fingerprint | d1c9229798c1ee226aa1fe1c0b0004dee24e8cd9fc4e5a007ae50b1248752393 |
| run id | 18cd50b8-ad19-49be-818b-33c4a99e17f4 |
| selected position id | p9position&#58;37f303ae0a3424cb3d2aefa4 |

Complete original responses, all review carriers and machine bindings&#58; record.json. Final control decision&#58; decision.json. File hashes and full source index&#58; manifest.json. Hashes verify integrity, not actor identity or authentication.

