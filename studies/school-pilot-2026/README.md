# School pilot 2026: testbench

**No measurement has been run.** This folder holds data, tools and tests for a small preregistered pilot. It contains no results. The publication of the preregistration is planned for 2026-11-13, and nothing is measured before it.

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

`scripts/check_quotes.py` checks a quote with a sentence number against a sentence bank. The sentence number selects a character range through `start` and `end`. The script looks for the quote inside that range, and the Inspektorium kernel (`validate_finding`) then confirms exact text and offsets. The kernel is used unchanged. It has its say in both modes, and the check only passes if it agrees.

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
