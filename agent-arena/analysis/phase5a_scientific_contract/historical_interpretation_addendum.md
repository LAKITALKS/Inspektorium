# Historical interpretation addendum — Study Forensics ME/OV contract

This prospective note does not modify the Phase-7 closeout, raw responses,
scores, analyses, gold labels, taxonomy or fingerprints.

The frozen Phase-7 Study Forensics prompt contained two instructions that do not
fully match the governing taxonomy and precedence documents. It treated broad
animal/“early-stage” evidence implying human benefit as
`mechanism_vs_evidence`, despite the normative requirement for a genuine
described biological-mechanism trigger and the explicit Shape-B surrogate
exclusion. In genuine overlap it also made promotional tone sufficient to choose
generic `overclaim`, whereas the normative rule gives a genuine specific label
precedence only when its trigger is present and it captures the core error;
promotional tone alone does not settle that decision.

The historical condition
`study_forensics_prompt/v1-historical-phase7` was used for the frozen Phase-7A
Haiku and Sonnet batches (420 stored response records per model; 840 total). Those
raw records and all published historical metrics remain unchanged.

For affected overlap structures, the instruction conflict complicates any claim
that an ME↔OV error measures model capability alone. It does not establish that
every ME↔OV disagreement was exposed to the conflict, that the visible prompt
caused a particular response, or that every historical gold label is necessarily
correct. The project had access to these historical data during this prospective
repair; this is not a blinded or newly held-out assessment.

The prospective condition is
`study_forensics_prompt/v2-taxonomy-aligned-phase5a` /
`study_forensics.taxonomy_aligned.v2`, SHA-256
`37d91b813bee2b4febb9dba5da66fa8e2bda1e091989785adf6ca5acc132b7ef`.
It preserves the historical output/confidence contract and changes only the two
documented scientific passages. No model validation of this condition has run.

