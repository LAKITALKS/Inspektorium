# Phase 5.1a — Semantic-Preservation Audit

For each new packet, verified against its committed source YAML prompt.

| check | BIAA-021 (030) | BIAA-022 (063) | BIAA-023 (036) |
|---|---|---|---|
| selected claim exists in committed source | yes | yes | yes |
| placeholder substitutions documented | yes ([Company A]) | yes ([City A]) | yes ([Researcher A]) |
| source-voice type preserved | company/press release | municipal officials | study authors |
| evidence design preserved | preclinical (mice) | uncontrolled before/after | preclinical (aged mice) |
| findings preserved | verbatim | verbatim | verbatim |
| limitations preserved | "no human efficacy data"/"preparing… human trials" | "no comparison city / no adjustment" | dosing warning + "human trials pending" |
| comparison groups preserved | lean controls; +incretin combo | (none in source; absence preserved) | (none; absence preserved) |
| evidence tier preserved | preclinical | uncontrolled municipal data | preclinical |
| no new evidence added | yes | yes | yes |
| no substantive evidence removed | yes | yes | yes |
| claim meaning unchanged (not strengthened/weakened) | yes | yes | yes |
| gold label unchanged | mechanism_vs_evidence | correlation_vs_causation | mechanism_vs_evidence |
| no synthetic multi-speaker claim | yes | yes | yes |
| only anonymization + structural normalization | yes | yes | yes |

**Transformation classification (all packets):** identifier assignment (blind ID) · anonymization
(speaker placeholder) · formatting (standard packet structure) · structural repositioning (claim vs
evidence vs source-voice sections) · wording preservation (claim/evidence verbatim) · evidence
preservation. **No material semantic change** occurred → no fail-stop, no candidate replacement.
