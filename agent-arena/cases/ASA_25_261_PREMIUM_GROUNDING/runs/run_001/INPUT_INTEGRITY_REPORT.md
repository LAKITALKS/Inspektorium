# INPUT INTEGRITY REPORT — ASA 25/261 · RUN 001

## Canonical freeze verification

| Field | Expected | Observed | Result |
|---|---|---|---|
| SHA-256 | `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069` | `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069` | **PASS** |
| Bytes | 119130 | 119130 | **PASS** |

The canonical Final Evidence Freeze is byte-identical to the expected artifact.
It was installed read-only (mode 444) and was never edited, repaired or
rewritten. Adjudication proceeded.

## All installed inputs

| File | Role | SHA-256 | Bytes |
|---|---|---|---|
| `input/01_FINAL_EVIDENCE_FREEZE_v1.md` | CANONICAL SCIENTIFIC SUBSTRATE | `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069` | 119130 |
| `provenance/01_CLOSED_CASE_SCIENTIFIC_EVIDENCE_PACKAGE_v1.md` | PROVENANCE (audit trail only) | `193877cacc4a3f3393b86b639a965a9446a3ba467b00c8baa632c024720c97d4` | 109112 |
| `provenance/02_TARGETED_EVIDENCE_CLOSURE_v1.md` | PROVENANCE (audit trail only) | `7ae78f2b84cdca24fe8c327173672706fcf9a0e6ed01c88f6291bb42a151474b` | 34052 |
| `provenance/03_PRE_FREEZE_TERMINOLOGY_ROBUSTNESS_CHECK_v1.md` | PROVENANCE (audit trail only) | `4d8df9fb9c145cba278e5a63ccf74074e3e5de3656faf56daff8b612ddc0fed2` | 18068 |


The three provenance artifacts match the hashes recorded inside the freeze
itself (section 5: A `193877ca…`, B `7ae78f2b…`, C `4d8df9fb…`), giving an
independent second confirmation that the correct source layer was installed.
Provenance files were consulted for routing confirmation only and were not used
to resurrect any superseded evidence state.

## Package transport deviation — recorded, non-blocking

The run instruction pointed to a transport ZIP at a `/mnt/data` path and an
extracted copy beside it. **Neither exists on this machine**; `/mnt` is not
present. The four substantive case documents were located in the local
INSPEKTORIUM working area and installed directly, so no re-upload was required.

| Expected package item | Status |
|---|---|
| `input/01_FINAL_EVIDENCE_FREEZE_v1.md` | **PRESENT** — hash verified against the canonical value |
| `provenance/01_CLOSED_CASE_SCIENTIFIC_EVIDENCE_PACKAGE_v1.md` | **PRESENT** — hash matches freeze section 5 artifact A |
| `provenance/02_TARGETED_EVIDENCE_CLOSURE_v1.md` | **PRESENT** — hash matches freeze section 5 artifact B |
| `provenance/03_PRE_FREEZE_TERMINOLOGY_ROBUSTNESS_CHECK_v1.md` | **PRESENT** — hash matches freeze section 5 artifact C |
| `input/02_HANDOFF_CLARIFICATION_v1.md` | **ABSENT** — see below |
| `input/03_INTEGRITY_MANIFEST.txt` | **ABSENT** — superseded by direct hash verification |
| `README_RUN_PACKAGE.md`, `PACKAGE_MANIFEST.txt`, `runs/run_001/README.md` | **ABSENT** — transport scaffolding, no scientific content |
| Transport ZIP | **ABSENT** — hash `b6ddb1fd…` could not be checked |

**Assessment: NON-BLOCKING.** The primary integrity check specified for this
run is the canonical Final Evidence Freeze SHA-256, and it passes exactly. The
ZIP is a transport container whose absence cannot affect the verified content
of the file it would have carried.

### Handoff clarification — how its content was obtained

The handoff file itself is absent, but the epistemic routing it carries was
supplied verbatim in the run instruction and has been applied in full. Each
routing decision is recorded on the proposition it governs:

| Propositions | Routing applied |
|---|---|
| P-02, P-05, V-01, E-02, I-02 | BOUNDED NEGATIVE SEARCH — documented proposition-specific negative-search work, each carrying a `documented_search` basis in the structured record |
| M-01b | REQUIRED DIRECT ENDPOINT NOT DEMONSTRATED — explicitly **not** the bounded negative-search protocol; carries no search-scope basis |
| W-01 | NOT OPERATIONALISABLE AS WORDED |
| X-01 | BUNDLE / GENERALISATION CLAIM — component adjudication performed |
| X-02 | SUPERIORITY CLAIM — comparator / metric undefined |
| Q-01, Q-02 | OUTSIDE BIOMEDICAL EVIDENCE SCOPE — commercial substantiation required |

The M-01b distinction is enforced structurally, not only in prose: the
consistency check verifies that exactly the five bounded-negative-search
propositions carry a search-scope basis and that M-01b does not.

## Source precedence applied

FINAL EVIDENCE FREEZE > HANDOFF CLARIFICATION (routing) > historical provenance
artifacts. The freeze is the canonical scientific substrate. Provenance files
were not used to resurrect superseded evidence states or older wording; in
particular the historical unsplit M-01 remains inactive, the pre-H33 menopause
negative state was not reinstated, and H31's historical `p<.01` was not used.

## Immutability

The canonical freeze at `input/01_FINAL_EVIDENCE_FREEZE_v1.md` is mode 444 and
its post-run hash is re-verified in `OUTPUT_MANIFEST.txt`. The original source
files were copied, not moved, and remain untouched at their origin.
