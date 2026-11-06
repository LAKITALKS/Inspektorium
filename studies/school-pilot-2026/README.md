# School pilot 2026: testbench

**No measurement has been run.** This folder holds data, tools and tests for a small preregistered pilot. It contains no results. The publication of the preregistration is planned for 2026-11-13, and nothing is measured before it.

## Status

| Part | State |
|---|---|
| Corpus, sentence banks, criteria | Done |
| Draw of the study groups | Done |
| Reference cases | Built and sealed, not run through any checker |
| Quote checker, import, analysis, coding sheet, prompt generator | Built, tested on invented data only |
| Prompt | Template; the writing task is a marked paraphrase, the marking guide is open |
| Inserted errors | Proposed, not decided |
| Run plan | Done; the prompt files do not exist yet |
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
| `prereg/` | Seed, drawn groups, run plan, and later the preregistration | yes |
| `runs/` | Chatbot outputs, prepared files, prompt files, the sentence banks of both versions and the manifest | no |
| `sealed/` | Held-out reference cases, off limits; only their hash is committed | no |
| `prompts/` | Prompt template for the chatbots | yes |
| `schemas/` | JSON Schema for the chatbot output | yes |
| `scripts/` | Tools | yes |
| `tests/` | Tests, run with `python -m pytest studies/school-pilot-2026/tests` | yes |

Tests that need the corpus skip when it has not been fetched. CI runs these tests through `testpaths`, without the corpus.

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

**Used reserve texts.** The `fabricated` cases took sentences from eight `reserve` texts. `selection.json` lists these texts under `used_for_fabricated`, and every later sample excludes them. A later sample must draw from `available_reserve` in `scripts/reserve.py`, which refuses a selection without this list.

The list was added after the draw, and the groups are unchanged. The eight texts stay in the group `reserve`, so the draw and the sealed hash stay reproducible. Because the file now differs from a fresh draw, `select_texts.py` refuses to run again. The test that repeats the draw compares everything except this list.

**Checking the draw from outside.** Use a fresh checkout of the commit that made the draw. There, `selection.json` has no later marking, so `select_texts.py` runs and refuses any result that differs.

```bash
git clone https://github.com/LAKITALKS/Inspektorium.git
cd Inspektorium
git checkout 129f9b5
python3 studies/school-pilot-2026/scripts/fetch_genius.py
python3 studies/school-pilot-2026/scripts/genius_loader.py
python3 studies/school-pilot-2026/scripts/select_texts.py
git status --short
```

The draw is confirmed if `select_texts.py` ends without an error and `git status --short` prints nothing. The scripts need only the standard library. On a Python build without system certificates, `fetch_genius.py` also needs the package `certifi`.

Two more commands show that the procedure came first and that the groups stayed the same. The first prints nothing. The second, once this study is merged, shows only the added list.

```bash
git diff b9c0aaa 129f9b5 -- studies/school-pilot-2026/scripts/select_texts.py studies/school-pilot-2026/prereg/seed.txt
git diff 129f9b5 origin/main -- studies/school-pilot-2026/prereg/selection.json
```

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

**The folder `sealed/` is off limits.** It is not opened, read or changed, and no test or analysis uses it. It is opened only at the final check, after the maintainer's release. For the same reason, the generator refuses to replace an existing sealed file. Nothing in this repository verifies the hash before that check.

Before the folder was closed on 2026-11-04, the generator wrote the file, and a hash check and a test read it by machine. Its content was not displayed.

**Use of the reserve.** `fabricated` needs foreign sentences, so eight `reserve` texts are opened for it. The summary names them, and later samples exclude them (see [Selection](#selection)). All other `reserve` texts stay unread.

**Not run.** Neither the kernel nor the quote checker has been applied to these cases. That is the measurement after the preregistration.

**Known limits.** The maintainer accepted both.

- **`format_variant` tests changed spaces.** All development cases of this type change a space. The selected texts hold one straight quotation mark in total, so the rule for typographic quotation marks is in effect tested on invented sentences only.
- **The 70/30 split is by case.** A text can appear in the development part and in the held-out part, so the two parts are not independent.

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

[prompts/grading_prompt_de.md](prompts/grading_prompt_de.md) is the German prompt template. [schemas/output.schema.json](schemas/output.schema.json) defines the output. The placeholder for the marking guide is open; its wording must not be invented.

**Prompt files.** `scripts/make_prompts.py` writes the six prompt files that the run plan names: three texts, each as the original and as the modified version.

```bash
python studies/school-pilot-2026/scripts/make_prompts.py --guide <marking-guide.md> --traps <traps.json>
```

- **Inputs.** The marking guide and the trap file are paths on the command line. Neither has a default, and the script opens only the files it is given.
- **Content.** Only the part of the template below its line is sent. Each sentence stands on its own line as `[S1] Satztext`.
- **Modified version.** It is the original plus the `edits` of the trap file; see [Hit rule](#hit-rule). The sentence numbers are the same in both versions.
- **Difference check.** The script compares the two banks sentence by sentence and the two finished prompts line by line. It stops if anything differs apart from the defined passages, or if a defined change is missing.
- **Output.** The prompts go to `runs/prompts/`, and the banks of both versions go to `runs/banks/`, where the import reads them. All of them stay out of Git, because the modified texts would show the inserted errors before the measurement.
- **Manifest.** `runs/manifest.json` records the SHA-256 of the guide, the trap file, all banks and all prompts, and the commit of the script. These values go into the preregistration. A script that differs from its commit writes nothing, because the manifest could not name it.
- **Repeatable.** The same inputs and the same script commit give the same bytes. Nothing uses the clock or chance.
- **No overwriting.** The script writes everything or nothing. A different existing file is never replaced, so a prompt that was already sent cannot change.

Its tests use invented texts and the example file `tests/fixtures/example_traps.json`. One more test runs the committed plan and banks with a placeholder as the edit.

## Import

`scripts/import_runs.py` reads `runs/<model>/<text_id>/<version>/<repetition>.json`. The file holds the answer exactly as received. `<repetition>.meta.json` next to it holds the metadata of the [run protocol](#run-protocol). The version `original` uses the bank `<text_id>.json`, and any other version uses `<text_id>.<version>.json`. Both lie in `runs/banks/`, where `make_prompts.py` writes them. The import stops if a bank is missing there.

**Failures.** A run is a failure if its output is missing, is not exactly one strict JSON value, or breaks the schema. Invalid JSON always stays a failure. Four exceptions apply, and nothing else is repaired.

**Exception 1: code block.** One code block around the whole answer is removed, and the run is not a failure.

- The opening fence is ` ``` ` or ` ```json ` in any case, and the closing fence is ` ``` `. Each stands on its own line.
- Only whitespace may stand outside the block.
- Text around the block, a second block, another language tag or invalid JSON inside the block stays a failure.

**Exception 2: unknown category.** An error entry whose category is a text outside the vocabulary gets the mark `invalid_category` (ungültige Kategorie), and the run stays usable.

- The quote of the entry is checked as usual.
- The entry can never count as a detection.
- A missing category, a category that is not a text and every other unknown value, such as a criterion `K9`, stay failures.

**Exception 3: sentence number.** The agreed form is `S3`. A wrong number is never treated more strictly than a missing one, because the pilot measures evidence, not JSON types.

- The text `"3"`, the JSON number `3` and the text `"[S3]"` are rewritten to `S3`. `"[S3]"` is the spelling of the prompt. Every rewrite is counted by its form, and the import keeps the original under `sid_rewrites`. The number is then checked like `S3`.
- Only a positive whole number counts as a number. `true`, `false`, `3.0`, `0` and negative values are another form.
- Any other form counts as a missing number, for example null, an empty text, `s3`, `S03`, `[3]` or `Satz 3`.
- A quote or error report without a number keeps the run usable. The quote counts in measure 2 and in `quotes_without_sid` only, and the report cannot pass stage 1.

**Exception 4: unknown criterion.** A criterion outside the grid keeps the run usable. The reference is marked with `id: null` and counts in measure 6 as outside the grid. A criterion written as its exact name from `data/criteria.json`, in any case, counts as its id. That list of names is the agreed list of spellings.

**Counted.** Per chatbot, the analysis reports three things under `import_notes`: `code_fences_removed` counts usable runs, `sids_rewritten` counts rewritten numbers in usable runs, in total and by form (`text`, `number`, `brackets`), and `invalid_category_entries` counts entries. Under `counts`, `quotes_without_sid` counts quotes, and measure 6 counts the references outside the grid.

**Metadata.** A missing field is an operating error, not a failure of the tool.

- The import rejects a run file with a missing or unreadable field and names the file and the field. It writes nothing until all such files are fixed.
- The operator adds the field from the chat history.
- If a field cannot be reconstructed, the metadata file holds `protocol_error` with a reason. Such a run counts separately as a protocol error. It enters no measure, its output is not read, and it is not replaced.

**No assignment.** The importer sets no pointers and assigns nothing afterwards. Each reference keeps its origin, separately for both modes:

| Origin | Meaning |
|---|---|
| `delivered_valid` | A quote was delivered and holds with its location |
| `delivered_invalid` | A quote was delivered and does not hold |
| `missing` | A local comment without a quote |
| `global_comment` | A global comment without a quote |

## Analysis

`scripts/analyze.py` computes the measures per model. Its tests use invented outputs only. The numbers follow the study plan.

| # | Measure | Count | Of | Undefined if |
|---|---|---|---|---|
| 1 | Failure rate | Failed runs | Attempted runs | never |
| 2 | Quote fidelity, text | Quotes whose text occurs in the essay | Delivered quotes | no quote |
| 3 | Quote fidelity, text and location | Quotes that occur in the claimed sentence | Delivered quotes with a sentence number | no such quote |
| 4 | Evidence coverage, overall | Comments with at least one delivered quote, valid or not | All comments | no comment |
| 5 | Evidence coverage, local | Not part of the pilot | | |
| 6 | Criterion fidelity | References inside the grid | All criterion references | no reference |
| 7 | Criterion coverage | Comments with at least one criterion reference | All comments | no comment |
| 8 | Grade variation | Originals only, per text and model: distribution, range, most common grade | | no usable run |
| 9 | Detection per usable run | Runs with a hit | Usable runs of the modified version | no trap |
| 10 | Detection per attempted run | Runs with a hit | Attempted runs of the modified version | no trap |
| 11 | False alarm | Runs with stage 1 and `ja` at the target | Usable runs of the original | no trap |
| 12 | Unclear | Runs coded `unklar` | Coded runs | no trap |

Measures 2 and 3 are reported strict and normalized. They count quotes in comments and in error reports.

**Also reported, without a measure of their own.**

- `invalid_quotes` lists every quote that fails in at least one mode, one by one, with both results. A quote with silently corrected spelling is invalid in both modes and appears here.
- `quotes_without_sid` counts quotes without a sentence number, including numbers in a form other than the agreed ones.
- `ambiguous_quotes` counts quotes whose text occurs more than once in the essay.
- `self_marked_global` counts comments the chatbot itself marks as global. It is descriptive only.
- `misplaced_hits` counts runs with `ja` without stage 1.
- `unknown_category` counts reports with an unknown category, by place.

**Report.** The written report gives counts such as `2 von 9`; see [Adaptations for the pilot](#adaptations-for-the-pilot-anpassung-für-den-pilot). The mean per text stays in the code under `rates` for the main study. It is not part of the pilot's report.

**Special cases.** A measure with an empty denominator is reported as `nicht definiert`. It is neither 0 nor 100 %, and it leaves any mean. Failed runs never enter the denominator of a quote measure, and they count as "not found" in measure 10 only. Protocol errors enter no measure.

**Grades.** Measure 8 uses the originals only, with one cell per text and model. The grades of the modified versions are reported separately under `grades_modified`, with one cell per text, version and model. Each cell gives the distribution, the range, and the most common grade with its count. A cell with fewer than three usable runs is marked.

**Exploratory.** `annotation_agreement_count` compares criteria with the corpus annotation. It is exploratory and not part of the pilot's report.

## Hit rule

A trap is one inserted error per text. Its definition has this form and comes to `analyze.py` and `make_prompts.py` as a file:

```json
{"<text_id>": {"version": "veraendert", "type": "Zahl", "accepted_categories": ["Zahl", "Widerspruch"], "sids": ["S2"], "description": "...", "edits": [{"sid": "S2", "from": "...", "to": "..."}]}}
```

The type is exactly one of `Zahl`, `Faktum`, `Widerspruch` and `Unsinn`, and it stays for the reports. `accepted_categories` lists one or two of these four, and the type is one of them. The target is one sentence; only a trap of the type `Widerspruch` may name two. The analysis refuses any other form.

`edits` says how the modified version arises, and only `make_prompts.py` reads it. An edit replaces one passage by one line of text. The passage must occur exactly once in a target sentence. A sentence takes one edit only, and no sentence is added or removed. A contradiction may edit one of its two sentences or both.

**Stage 1 is mechanical.** A report passes if it names a target sentence and a category from `accepted_categories`. A report without a sentence number cannot pass.

**Stage 2 is human.** The coder answers one question per run: does a report describe the target error? The answer is `ja` with the number of the report, `nein` or `unklar`.

| Situation | Modified version | Original |
|---|---|---|
| Stage 1 and `ja` for the same report | Hit | False alarm |
| `ja` without stage 1 | No hit; counted as a hit under a wrong category or sentence | No false alarm; counted the same way |
| `nein` | No hit | No false alarm; other criticism at the site does not count |
| `unklar` | No hit; measure 12 | False alarm; measure 12 |
| `ja` for a report at the target with an unknown category | No hit | False alarm |

A hit needs no valid quote, because measures 2 and 3 measure quote fidelity.

**Counter assumption.** `counter_assumption` repeats measures 9 to 11 with the last two rows reversed: a hit in the modified version, no false alarm in the original. Both results are reported. A report with an unknown category away from the target stays `ja` without stage 1 in both results.

## Coding

`scripts/export_for_coding.py` writes the coding sheet, and `analyze.py` reads it back.

```bash
python studies/school-pilot-2026/scripts/export_for_coding.py --imported <imported.json> --targets <traps.json> --sheet <sheet.csv> --key <key.json>
python studies/school-pilot-2026/scripts/analyze.py --imported <imported.json> --targets <traps.json> --coding-sheet <sheet.csv> --coding-key <key.json> --out <report.json>
```

- The sheet has one row per run, in random order. A row shows all error reports of the run, numbered, and the target description of the text.
- It shows neither the model nor the version nor the repetition.
- The key file leads each row back to its run. Keep it out of sight until the coding is done.
- A row without reports is already answered `nein`. A failed run looks the same, and its answer is not used.
- The order comes from a new random value on each export. An existing sheet or key is never replaced, so a finished coding cannot lose its key.
- The filled sheet is read back with comma or semicolon. A blank or impossible answer, or a missing or repeated row, stops the analysis and is named by row. Every usable run of a text with a trap needs an answer.
- The text of the reports is not edited, so a chatbot that names itself stays recognizable. Text that a spreadsheet would run as a formula gets a leading apostrophe.

## Adaptations for the pilot (Anpassung für den Pilot)

The maintainer decided these differences from the main study's plan.

- **Repetitions.** Three per version, the original included, for 54 runs. The main study plans ten for the originals. A grade cell is marked if fewer than three runs are usable. Krippendorff's alpha is not computed; the pilot reports the distribution, the range and the most common grade.
- **Reporting.** The pilot is reported as a feasibility check: counts such as `2 von 9`, no rates with confidence intervals. This also holds for the component test, which reports `0 von n` and no error rate. Criterion A1 of the main study (at least 300 invalid quotes) is not claimed.
- **Normalization.** The plan names NFC, line endings and HTML entities. The rule on final marks of 2026-11-04 comes on top. NFC and line endings are in the kernel. HTML entities are converted only when the sentence banks are built, in `convert_sentence`. The quote checker does not convert them in a quote, so a quote with `&lt;` does not match a `<` in the essay, in either mode. The three pilot texts contain no HTML entities.
- **Reference cases.** The plan estimated about 200. There are 302: 211 for development and 91 held out.
- **Second coding.** The pilot has no second person, so there is no second coding and no agreement between coders. This is a limit of the pilot. The [coding sheet](#coding) keeps the single coding blind.
- **Stage 2.** All runs are coded, with one answer per run. So the check of a sample of non-hits falls away, and `ja` without stage 1 is reported separately. Measure 12 therefore counts runs, not reports.
- **Measure 5.** It is not part of the pilot, because it needs human coding of local and global comments. This is a limit of the pilot. The report only gives the number of comments the chatbot itself marks as global.
- **Silent corrections.** A quote with silently corrected spelling is invalid in both modes, unlike the plan says. All invalid quotes are listed one by one, without a measure of their own.

## Changes before preregistration

These changes were made before the preregistration, while the tools were being checked.

- **Sentence numbers.** The agreed spellings `"3"`, `3` and `"[S3]"` become `S3`, and each rewrite is counted by its form. Every other form counts as a missing number, so a wrong number no longer makes a run a failure. See exception 3 under [Import](#import).
- **Accepted categories.** Stage 1 first asked for exactly one category. A trap now names one or two accepted categories, because some errors fit two of them: a wrong number that contradicts a statement in the same text can accept `Zahl` and `Widerspruch`. The type of the trap stays for the reports. See [Hit rule](#hit-rule).
- **Prompt files and banks.** `scripts/make_prompts.py` builds the modified version from the trap file and writes all prompts, the banks of both versions and a manifest below `runs/`. The import now reads the banks from `runs/banks/`, because a quote must be checked against the text that was sent. See [Prompt and output format](#prompt-and-output-format).
- **Task material.** The prompts describe the task in own words and do not contain the material table. Whether and how the table may be used is still being clarified.

## Run protocol

**Test subjects.** ChatGPT, Gemini and Grok. Mistral and Claude are not test subjects.

**Runs.** 54 in total: 3 texts, 2 versions (the original and one modified version), 3 chatbots, 3 repetitions. The maintainer does them by hand in the chat windows, without automation.

**Chatbot condition.** Each run uses the default model and the default settings of the interface, in a new temporary or private chat, without memory and without custom instructions. The model selector, thinking modes and tool settings stay unchanged. Account type and displayed model are recorded per run.

**Run plan.** [prereg/laufplan.csv](prereg/laufplan.csv) has one row per run with its number, day, chatbot, prompt file, target file and metadata file. `scripts/make_run_plan.py` mixes the order with the seed from `prereg/seed.txt`. Every chatbot has nine runs on each of the two days, and the repetitions of one text and version fall on both days.

The script also prepares one empty, named output file and one blank metadata form per run under `runs/`. It never touches an existing file. The import rejects blank forms, so a run that was not done cannot pass as one. The prompt files named in the plan do not exist yet, because they need the marking guide and the inserted errors. `scripts/make_prompts.py` writes them once both are decided, and they stay out of Git.

**Metadata.** Each run has these fields in `<repetition>.meta.json`. All of them are entered before the prompt is sent.

| Field | Content |
|---|---|
| `model_name` | Model as the chat interface displays it |
| `date` | Date, `YYYY-MM-DD` |
| `time` | Time, `HH:MM` |
| `chat_mode` | Chat mode used, as the chat interface calls it |
| `account_type` | Kontoart: the kind of account used, for example free or paid |

## Frozen tools

The held-out file can be rebuilt from public inputs, because the generator has no secret and no random part. So its secrecy protects nothing. What protects the test is that the tools under test do not change.

These two stay unchanged until the held-out cases are evaluated:

| Tool | Git id |
|---|---|
| `src/` (tree) | `0afbc0115f904d6408b1b8196af4e019678d3c56` |
| `scripts/check_quotes.py` (blob) | `2a3368683da37db01ae6487dc75cf552c6bfa9e0` |

`tests/test_frozen_tools.py` fails if either one changes.

With the preregistration, the commit of the whole study folder is recorded, without `runs/` and `sealed/`. Every later change to import, analysis, export or prompt generator code is a deviation and is named in the report. So is every change to the files behind `--guide` and `--traps` after the preregistration.

`runs/` stays out of Git until the results are published. The maintainer, Lazaros Varvatis, backs up the folder.

## Open decisions

These points are not settled here, and the tooling does not assume an answer.

- **Marking guide.** It follows after the maintainer's release. The placeholder stays until then.
- **Inserted errors.** The candidate sites are in `prereg/injection_proposals.md` and `prereg/injection_proposals_v2.md`, with a draft of the trap file in `prereg/traps_draft.json`. These files stay out of Git, because this repository is public and the sites would be visible before the measurement. The maintainer decides the sites, with one type and one or two accepted categories per trap. An error goes only where the original was verified as correct beforehand; otherwise the site is dropped. Figures from the task material cannot be verified without that material. The final definitions will go to `sealed/`, and only their SHA-256 will be committed.

**Writing task.** The prompt uses a marked paraphrase after Schaller et al., LREC 2026. The original wording is not available.
