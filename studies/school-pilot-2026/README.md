# School pilot 2026: testbench

**No measurement has been run.** This folder holds data, tools and tests for a small preregistered pilot. It contains no results. The publication of the preregistration is planned for 2026-11-13, and nothing is measured before it.

## Status

| Part | State |
|---|---|
| Corpus, sentence banks, criteria | Done |
| Draw of the study groups | Done |
| Reference cases | Built and sealed, not run through any checker |
| Quote checker, import, analysis | Built, tested on invented data only |
| Prompt | Template; the writing task and the marking guide are open |
| Inserted errors | Proposed, not decided |
| Chatbot runs | Not started |

## Purpose

The pilot will ask how reliably AI grading assistants comment on and grade student essays. It uses real student texts from the open GENIUS Keylog Corpus. The sources are listed in [ATTRIBUTION.md](ATTRIBUTION.md).

## Layout

| Path | Content | In Git |
|---|---|---|
| `ATTRIBUTION.md` | Source and license of the corpus | yes |
| `data/criteria.json` | Criteria K1 to K7 | yes |
| `data/external/` | Full corpus and all sentence banks | no |
| `data/reference_cases_dev.json` | Development part of the reference cases | yes |
| `data/selected/` | Sentence banks of `pilot` and `component`, marked in their README | yes |
| `prereg/` | Seed, drawn groups, and later the preregistration | yes |
| `sealed/` | Held-out reference cases; only their hash is committed | no |
| `prompts/` | Prompt template for the chatbots | yes |
| `schemas/` | JSON Schema for the chatbot output | yes |
| `scripts/` | Tools | yes |
| `tests/` | Tests, run with `python -m pytest studies/school-pilot-2026/tests` | yes |

Tests that need the corpus skip when it has not been fetched.

## Restore the data

```bash
python studies/school-pilot-2026/scripts/fetch_genius.py
python studies/school-pilot-2026/scripts/genius_loader.py
```

`fetch_genius.py` downloads one pinned file and stops if its SHA-256 differs. Nothing is unpacked in that case.

## Sentence banks

- Every line of a WebAnno TSV file that starts with `#Text=` is one sentence.
- Each sentence is HTML-unescaped first, then normalized to Unicode NFC.
- Sentences are joined with **one ASCII space** to form `full_text`.
- `start` and `end` are Python character offsets into `full_text`, so `full_text[start:end] == text`.
- Words are counted by splitting on whitespace.

A bank has the form `{text_id, word_count, sentences: [{sid, text, start, end}], full_text}`.

The header labels of the corpus lost their umlauts. `criteria.json` keeps them in `original_label` and adds a readable `name`.

## Selection

The procedure below was committed before its first run on the corpus, so the Git history shows that it was fixed before the result existed. Only unit tests on invented ids ran before that commit.

**Participation rule.** A text takes part if it has at least 80 words and its annotation file has the layer `webanno.custom.Argument`.

**Draw.** The seed is in [prereg/seed.txt](prereg/seed.txt). `scripts/select_texts.py` ranks every eligible text id by SHA-256 of `"<seed>:<text_id>"`. It then fills separate groups in this order:

| Group | Size | Use |
|---|---|---|
| `pilot` | 3 | Pilot texts |
| `component` | 20 | Reference cases for the component test |
| `validation_holdout` | 20 | Kept for later validation |
| `reserve` | the rest | Not touched |

The script refuses to replace an existing draw with a different one.

The draw is in [prereg/selection.json](prereg/selection.json). Only `pilot` and `component` are copied to [data/selected/](data/selected/README.md); the other groups are id lists.

## Reference cases

`scripts/make_reference_cases.py` builds cases with known answers from the 20 `component` texts. A case is `{case_id, text_id, claimed_sid, quote, type, expected_strict, expected_normalized}`. Each text gets up to two cases per type, from different sentences where possible.

| Type | What it is | Strict | Normalized |
|---|---|---|---|
| `valid_exact` | Literal part of the sentence, right sentence number | valid | valid |
| `wrong_location` | Literal part, wrong sentence number | invalid | invalid |
| `altered_number` | One number changed; only if the text has a free-standing number | invalid | invalid |
| `altered_word` | One word replaced by another word of the same text | invalid | invalid |
| `fabricated` | A sentence from a `reserve` text, claimed as a sentence of this text | invalid | invalid |
| `case_change` | Capitalization of one word changed | invalid | invalid |
| `format_variant` | Only a space or quotation mark changed | invalid | valid |
| `punctuation_added` | Literal part with one `.`, `!` or `?` added at the end | invalid | valid |

**No omitted-mark variant.** A quote that merely lacks the final mark of its sentence is a literal part of that sentence. Strict mode accepts it, so it cannot carry the label `invalid`. `punctuation_added` therefore only adds a mark.

**Labels are constructed, not measured.** The generator imports neither the kernel nor `scripts/check_quotes.py`. It keeps a candidate only if plain substring logic confirms the expected values of its type. That logic restates the rules of this README in the generator on purpose, so the tool under test does not grade itself. It also covers the rule on final marks: a candidate that this rule would make valid in normalized mode is dropped from the `invalid` types.

**Split.** Within each type, cases are ranked by SHA-256 of `"<seed>:split:<case_id>"`. The first 70 % go to development, the rest are held out. The split is by case, not by text, so a text can appear in both parts.

**Sealed part.** `sealed/holdout_cases.json` is ignored by Git. Its SHA-256 is in [prereg/holdout_sha256.txt](prereg/holdout_sha256.txt), and the counts are in [prereg/reference_cases_summary.json](prereg/reference_cases_summary.json).

**Use of the reserve.** `fabricated` needs foreign sentences, so eight `reserve` texts are opened for it. The summary names them. All other `reserve` texts stay unread.

**Not run.** Neither the kernel nor the quote checker has been applied to these cases. That is the measurement after the preregistration.

## Quote check

`scripts/check_quotes.py` checks a quote with a sentence number against a sentence bank. The sentence number selects a character range through `start` and `end`. The script looks for the quote inside that range, and the Inspektorium kernel (`validate_finding`) then confirms exact text and offsets. The kernel is used unchanged, and in both modes the check passes only if the kernel confirms the span.

The result reports two things separately: whether the text occurs anywhere in the essay (`text_valid`), and whether it occurs inside the claimed sentence (`location_valid`).

| Comparison rule | Strict | Normalized |
|---|---|---|
| Kernel normalization: Unicode NFC, line endings to LF | yes | yes |
| Every Unicode whitespace character counts as one ASCII space | no | yes |
| Typographic quotation marks count as straight ones | no | yes |
| One final `.`, `!` or `?` of the quote is ignored | no | yes |

**Whitespace.** Every character for which Python's `str.isspace()` is true is replaced by one space, character by character. Runs are not merged, so a doubled space stays a difference. Zero-width characters are not whitespace.

**Quotation marks.** `„ “ ” ‟ « »` count as `"`, and `‚ ‘ ’ ‛ ‹ ›` count as `'`. This is applied to the essay and to the quote.

**Final mark.** In normalized mode, one `.`, `!` or `?` at the very end of the quote is ignored in the comparison. The rule applies to the quote only, to one mark only and to these three marks only. Two marks, a comma, a mark followed by a space or a mark inside the quote all stay differences. It repairs nothing else: a changed word, number or capital letter stays invalid, and so does a wrong sentence number.

This rule was added on 2026-11-04, before the preregistration, after a newspaper quote outside this corpus was rejected in strict mode only because of an added full stop.

**An omitted final mark needs no rule.** A quote that lacks the final mark of its sentence is a literal part of that sentence and is valid in both modes.

**Rejected in both modes.** A quote is invalid if it has no letter or digit, names an unknown sentence or runs across two sentences. A bank whose offsets or canonical form are wrong stops the check with an error.

The tests of this script use invented sentences only.

## Prompt and output format

[prompts/grading_prompt_de.md](prompts/grading_prompt_de.md) is the German prompt template. [schemas/output.schema.json](schemas/output.schema.json) defines the output. The placeholders for the writing task and the marking guide are open; their wording must not be invented.

## Import

`scripts/import_runs.py` reads `runs/<model>/<text_id>/<version>/<repetition>.json`. The file holds the answer exactly as received. `<repetition>.meta.json` next to it holds `date` and `model_name`, the name the chat interface shows. The version `original` uses the bank `<text_id>.json`, and any other version uses `<text_id>.<version>.json`.

**Failures.** A run is a failure if its output is missing, is not exactly one strict JSON value, breaks the schema, or has unusable metadata. Nothing is repaired, so an answer in a code fence or with text around the JSON is a failure. One value outside a vocabulary, such as an unknown category, makes the whole run a failure.

**No assignment.** The importer sets no pointers and assigns nothing afterwards. Each reference keeps its origin, separately for both modes:

| Origin | Meaning |
|---|---|
| `delivered_valid` | A quote was delivered and holds with its location |
| `delivered_invalid` | A quote was delivered and does not hold |
| `missing` | A local comment without a quote |
| `global_comment` | A global comment without a quote |

## Analysis

`scripts/analyze.py` computes twelve measures per model. Its tests use invented outputs only.

| # | Measure | Definition | Undefined if |
|---|---|---|---|
| 1 | Failure rate | Failed runs among attempted runs | never |
| 2 | Quote fidelity, strict, text | Delivered quotes whose text occurs in the essay | the run has no quote |
| 3 | Quote fidelity, strict, text and location | Delivered quotes whose text occurs in the claimed sentence | the run has no quote |
| 4 | Quote fidelity, normalized, text | As 2, in normalized mode | the run has no quote |
| 5 | Quote fidelity, normalized, text and location | As 3, in normalized mode | the run has no quote |
| 6 | Evidence coverage overall | Comments, local and global, with at least one valid quote; reported for both modes | the run has no comment |
| 7 | Criterion fidelity | For comments with a valid quote: named criteria that the corpus annotation marks in a quoted sentence | no such comment names a criterion |
| 8 | Criterion coverage | Criteria annotated in the text that some comment names | the text has none |
| 9 | Grade distribution | Count of each grade per text and model | no usable run |
| 10 | Detection per usable run | Inserted errors found, among usable runs of modified versions | no target |
| 11 | Detection per attempted run | As 10, with each failed run counted as finding nothing | no target |
| 12 | False alarm | Usable runs of the original with an error report at a target sentence | no target for the text |

**Estimate.** The estimate is the mean per text: the runs of a text are averaged first, then the texts.

**Special cases.** An undefined rate is reported as `nicht definiert`. It is neither 0 nor 100 %, and it leaves the mean. Failed runs never enter the denominator of a quote measure.

**Quotes counted.** Measures 2 to 5 count quotes in comments and in error reports.

**Detection.** An inserted error counts as found if an error report names its sentence, delivers a valid quote in normalized mode and uses an accepted category. A report with the right sentence but another category is no detection; `wrong_category_hits` keeps it visible. Comparing a report with the accepted descriptions needs human judgment and is not part of this script.

**False alarm.** Target sentences are correct in the original, so an error report there is a false alarm. Any category counts.

## Open decisions

These points are not settled here, and the tooling does not assume an answer.

- **Writing task.** Its wording is not in `annotations.zip`, which holds only the 262 annotation files. The study paper and the corpus repository were not consulted, because this build allowed one download only. The wording must come from a source and must not be invented.
- **Marking guide.** The maintainer supplies its wording.
- **Chatbots.** Proposed: ChatGPT, Gemini and Mistral. Claude is not a test subject.
- **Repetitions.** Proposed: three per version.
- **Inserted errors.** The candidate sites are in `prereg/injection_proposals.md`. That file stays out of Git, because this repository is public and the sites would be visible before the measurement. The maintainer decides the sealed part.
- **Definitions.** The definitions of the measures were written from the study brief, without access to audit report 2. Before the preregistration they must be compared with its table, above all measures 6 to 8 and 10 to 12.
