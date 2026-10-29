# Judge replay through the Inspektorium 0.3.0 kernel

Recorded on 2026-10-27 with the published release 0.3.0. The run followed the frozen preregistration in [`inputs/judge-replay/PREREGISTRATION.md`](inputs/judge-replay/PREREGISTRATION.md).

## Question

Three LLM judges reviewed the same published study and quoted the passages behind their findings.
Does the kernel accept the quotes that appear in the source, and reject the one that does not?

## Material

- **Source:** `inputs/judge-replay/source/early_body.txt`. Guo L, Xi Y, Jin W, et al. A 5:2 Intermittent Fasting Meal Replacement Diet and Glycemic Control for Adults With Diabetes: The EARLY Randomized Clinical Trial. *JAMA Netw Open.* 2024;7(6):e2416786. [doi:10.1001/jamanetworkopen.2024.16786](https://doi.org/10.1001/jamanetworkopen.2024.16786).
- The source text is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). It comes from PubMed Central (BioC); tables and references were omitted, the rest is unchanged.
- **Judges:** the third-run answers of `grok`, `astra` (ChatGPT) and `gemini`, as received, in `inputs/judge-replay/judges/`.
- **Pieces:** `inputs/judge-replay/extraction/pieces.json` lists 43 quotations (Grok 15, ChatGPT 8, Gemini 20) with their predictions.
- `inputs/judge-replay/MANIFEST.sha256` lists every input file. The input archive had SHA-256 `a0881e0d4f40b5ac414ee51d1ef4a06fec0fd3026a2b1152f2fe77d2a379fcae`, and every file matched the manifest.

## Mapping onto the kernel

- **Answer:** the judge's answer text, unchanged. **Source:** `early_body.txt` with `source_id = "early-body"`.
- **One proposal per piece.** The claim is the piece at its first exact occurrence in the canonical answer.
  The evidence quote is the same piece.
- **Canonical text** comes from `inspektorium.core.normalization.normalize_text` of the release. It changes only line endings to LF and applies Unicode NFC.
- **Relation:** `supported`. The release's `EvidenceRelation.requires_citation` is true for every relation except `not_established` (`core/relations.py`, lines 17–20).
- **IDs:** the kernel requires lowercase identifiers, so `grok-4B` becomes `grok-4b`. [`results/pieces_results.json`](results/pieces_results.json) records both forms.
- **Fixed fields:** every proposal has `rationale` "Replay of a judge quotation; see PREREGISTRATION.md.", `evidence_sufficiency` `sufficient` and `evaluator_certainty` `medium`.
  These fields do not affect the quotation check. `validate_finding` in `core/validation.py` (lines 27–127) reads only the claim and evidence fields and the relation; line 121 passes the rest through.

## Locator

The judges gave no character offsets, so [`tools/locator.py`](tools/locator.py) supplies them in the canonical source:

- **L1:** the first exact occurrence.
- **L2:** without one, the window of the same length with the highest `difflib.SequenceMatcher(None, piece, window).ratio()`; ties go to the earliest window.

## Results

| | Prediction | Result |
| --- | --- | --- |
| Strict, PASSED / FAILED | 39 / 4 | 39 / 4 |
| of which true positive (`grok-4B`) | FAILED | FAILED, `evidence_span_mismatch` |
| of which typography (`grok-3A`, `astra-4A`, `gemini-3A`) | FAILED | FAILED, `evidence_span_mismatch` |
| Space-normalized, PASSED / FAILED | 42 / 1 | 42 / 1 (`grok-4B`) |
| Controls | 2 PASSED, 2 FAILED | 2 PASSED, 2 FAILED |

All 43 pieces matched their prediction in both runs ([summary](results/summary.json)).
In the strict run, the 39 passing pieces were located by L1 and the 4 failing pieces by L2.

- **`grok-4B`:** the quote has no exact occurrence in the canonical or the raw source.
  The nearest window (offsets 2306–2541, ratio 0.9957) differs in one code point: the quote has `5` (U+0035) where the source has `4` (U+0034).
- **Typography:** each quote has U+0020 SPACE where the source has U+2009 THIN SPACE, around the `=` of "P = .002".

| Piece | Offsets in the quote | Quote | Source |
| --- | --- | --- | --- |
| `grok-3A` | 48, 50 | U+0020 | U+2009 |
| `astra-4A` | 30, 32 | U+0020 | U+2009 |
| `gemini-3A` | 140, 142 | U+0020 | U+2009 |

## Controls

A separate run checked four sentences of the source:

- Two exact sentences, each up to its full stop: both PASSED.
  They start with "Of the 509 participants screened" and "Two patients in the empagliflozin group experienced serious adverse events".
- The same sentences with one change, `509` to `508` and `severe rash` to `severe rush`: both FAILED with `evidence_span_mismatch`, at exactly the changed character.

The preregistration describes the second change as a changed digit. The run used the letter change that the work order specified.

## Sensitivity analysis

This is input normalization outside the product, not kernel behavior.
[`tools/sensitivity.py`](tools/sensitivity.py) maps U+2009, U+202F and U+00A0 to U+0020 in the answers, the source and the pieces.
It replaced 28 thin spaces in the source and none in the answers or pieces; the same runs were then repeated.

## Environment

- Python 3.12.14 on macOS, in a fresh virtual environment.
- Release wheel `inspektorium-0.3.0-py3-none-any.whl`, SHA-256 `d8e56b730c7a181bab1e80f35c798817d3a8cda071186ef362ddf30ef5ba2a92`, as published in the release's `SHA256SUMS.txt`.
- The Python network guard of the [v0.1.1 evidence package](../v0.1.1/tools/netguard.py) was armed in all 8 kernel runs and refused no operation. Its canary check refused all 5 test connections.
- [`results/runs/`](results/runs/) holds every input, proposal, locator record, raw report and exit code.

## Limitations

These are taken from the preregistration:

- These are development cases with a small n. They are not a performance estimate.
- Grok had seen the answer key in an earlier chat, and ChatGPT may have had memory of the project. The run-3 verdicts carry that caveat; the quote check does not depend on it.
- The locator supplies the offsets, so a fabricated quote is tested against its nearest window. The exact search shows that it stands nowhere in the source.
- Space normalization is not product behavior. It only shows how many alarms are typographic.

## Reproduce

From the repository root, with Python 3.11 or newer:

```sh
python3 -m venv .venv-replay && .venv-replay/bin/python -m pip install "https://github.com/LAKITALKS/Inspektorium/releases/download/v0.3.0/inspektorium-0.3.0-py3-none-any.whl"
.venv-replay/bin/python -I evidence/judge-replay-2026-10-27/tools/run_replay.py --out ../judge-replay-runs
.venv-replay/bin/python -I evidence/judge-replay-2026-10-27/tools/evaluate.py --runs ../judge-replay-runs --out ../judge-replay-results
```

`run_replay.py` installs the network guard into that virtual environment before the runs.
