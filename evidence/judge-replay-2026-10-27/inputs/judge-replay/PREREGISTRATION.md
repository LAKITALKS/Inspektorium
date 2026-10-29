# Judge replay through the INSPEKTORIUM kernel: preregistration

Fixed on 27 October 2026, before any kernel run. Author: Lazaros Varvatis. Prepared with Claude.

## Question

Three LLM judges (Gemini, Grok, ChatGPT) reviewed the same published study (run 3) and quoted the passages that support their findings. Does the INSPEKTORIUM 0.3.0 kernel accept the quotes that really appear in the source, and reject the one quote that does not?

## Material

- `source/early_body.txt`: the study text exactly as the judges received it. Guo L, Xi Y, Jin W, et al. A 5:2 Intermittent Fasting Meal Replacement Diet and Glycemic Control for Adults With Diabetes: The EARLY Randomized Clinical Trial. JAMA Netw Open. 2024;7(6):e2416786. doi:10.1001/jamanetworkopen.2024.16786. CC BY 4.0. Text from PubMed Central (BioC); tables and references omitted, otherwise unchanged.
- `judges/*_lauf3.txt`: the three judges' answers as received.
- `extraction/*_l3.json`: the quotes extracted from those answers before any kernel run.
- `extraction/pieces.json`: the canonical list of 43 evidence pieces (Grok 15, ChatGPT 8, Gemini 20), with the predictions below. Quotes joined with " ... " were split into separate pieces.

## Mapping onto the kernel

- **Answer:** the judge's full answer text. **Source:** `early_body.txt`, `source_id = "early-body"`.
- **One proposal per piece.** The claim is the piece as it appears in the judge's answer (first exact occurrence), and so is the evidence quote. Meaning: the judge asserts that this string stands in the source.
- **Relation:** the relation that requires a citation (expected `supported`); taken from the code, not assumed.
- **Evidence offsets.** The judges gave no character offsets, so a fixed locator supplies them. This replay therefore measures the kernel's verdict on the judges' quotes, not an evaluator's offset proposals.
  - L1: the first exact occurrence in the canonical source (after the kernel's own `normalize_text`).
  - L2: if there is none, the window of the same length with the highest `difflib.SequenceMatcher` ratio, ties going to the earliest.

## Predictions

**Strict, unchanged kernel 0.3.0:** 39 PASSED, 4 FAILED.
- `grok-4B`: **true positive.** A montage of Abstract wording and Results numbers that appears nowhere in the source.
- `grok-3A`, `astra-4A`, `gemini-3A`: **false positives.** The source has thin spaces (U+2009) around "=" in "P = .002"; the judges typed ordinary spaces. The kernel normalizes only LF and NFC.

**Sensitivity analysis (input normalization outside the product):** map U+2009, U+202F and U+00A0 to U+0020 in both source and quotes, then run again. Prediction: 42 PASSED, 1 FAILED (`grok-4B`).

**Controls:** 2 exact sentences from the source → PASSED; the same 2 with one digit changed → FAILED. If the controls do not behave as predicted, the run is invalid.

## Limitations stated in advance

- These are development cases with a small n. They are not a performance estimate.
- Grok had seen the answer key in an earlier chat; ChatGPT may have had memory of the project. The run 3 verdicts carry that caveat. The quote check itself does not depend on it.
- The locator supplies the offsets, so a fabricated quote is tested against its nearest window. Rejection there shows that the quote does not stand in the source at that position, and the exact search shows it stands nowhere.
- Space normalization is not product behavior. It only shows how many alarms are typographic.
