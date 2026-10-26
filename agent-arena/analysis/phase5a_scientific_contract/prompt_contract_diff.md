# Study Forensics prompt contract diff

Historical identity:
`study_forensics_prompt/v1-historical-phase7` /
`study_forensics.historical.v1` /
SHA-256 `f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5`.

Prospective identity:
`study_forensics_prompt/v2-taxonomy-aligned-phase5a` /
`study_forensics.taxonomy_aligned.v2` /
SHA-256 `37d91b813bee2b4febb9dba5da66fa8e2bda1e091989785adf6ca5acc132b7ef`.

Only the following two scientific passages change. The task framing, evidence
tiers, JSON output schema, confidence requirement and all final instructions are
unchanged.

## Evidence-tier key rule

```diff
- If the evidence is from animal studies or early-stage research but the text
- implies human benefit ... classify as mechanism_vs_evidence.
- ... A well-hedged mouse study implying human therapeutic potential is
- mechanism_vs_evidence regardless of hedging quality.
+ A tier difference alone does not establish mechanism_vs_evidence.
+ Use mechanism_vs_evidence only when a described biological mechanism in
+ animal or preclinical evidence implies unproven human clinical benefit.
+ Broad "early-stage research" is insufficient.
+ Shape B is excluded: honest surrogate/biomarker reporting -> solid;
+ rhetorically sold clinical benefit -> overclaim.
+ Distinguish decorative hedging from limitations that genuinely constrain the
+ conclusion to the evidence.
```

## Primary-label precedence

```diff
- Promotional clinical-benefit language automatically makes overclaim primary;
- analytical or cautious tier mismatch automatically makes ME primary.
+ First establish the genuine documented CvC or ME trigger.
+ A specific label outranks generic overclaim only when its trigger is present
+ and it captures the core error.
+ If the trigger is absent or stretched, overclaim remains primary.
+ Shape-B inflation remains overclaim.
+ Overclaim may be a secondary reading when a genuine specific failure is
+ primary; promotional tone alone does not override that specific failure.
```

This is contract alignment, not a claim that a model will follow the revised
instruction or obtain higher accuracy.

