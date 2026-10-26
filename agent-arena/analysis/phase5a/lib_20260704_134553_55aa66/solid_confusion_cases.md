# Solid-Label Confusion Cases (Phase 5A)

Two directional metrics against the `solid` label are reported separately to avoid the ambiguous term 'solid false-positive rate'.

## 1. solid_as_problem_rate (supported claim wrongly flagged as a problem)

Definition: `gold_label == solid` but `predicted_label != solid`. This is the commercially important false-positive direction (flagging a genuinely supported/solid claim as a problem).

- Solid-gold runs: 42
- solid-as-problem runs: 0
- **solid_as_problem_rate: 0.0%**

None — every solid-gold run was correctly predicted solid (0/42).

## 2. problem_as_solid_rate (real problem under-flagged as solid)

Definition: `gold_label != solid` but `predicted_label == solid`. This is false-negative-style under-flagging (calling a case with a real forensic problem 'solid').

- Non-solid runs: 108
- problem-as-solid runs: 3
- **problem_as_solid_rate: 2.78%**

Cases contributing problem-as-solid runs:
- study-forensics-042 (gold overclaim) — 3/3 runs predicted solid

Note: case042 is a documented `borderline` case whose alternative reading is `solid`; it is not reinterpreted or relabelled here.
