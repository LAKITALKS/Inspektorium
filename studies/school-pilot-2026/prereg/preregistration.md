# Preregistration: Do AI chatbots ground their grading of student essays in the text?

A feasibility pilot with three German student essays, three chatbots and 54 grading runs.

- **Author:** Lazaros Varvatis, independent researcher, INSPEKTORIUM (inspektorium.org)
- **Date of registration:** 2026-11-11
- **Frozen study state:** commit `bfcd872e464e1ab87fdc2e514e0e3792ef8c31f6` of github.com/LAKITALKS/Inspektorium, folder `studies/school-pilot-2026` (tree `3f68108cf375e0d63ae6d605abcd476eaf5c4fd8`). The folder README at that commit is part of this preregistration and gives the rules in full. Where this document adds a commitment, this document applies.
- **Status at registration:** No chatbot run has been made. No output of any chatbot to these prompts exists. The reference cases of the component test have not been run through any checker.

## 1. Research questions

1. **Evidence fidelity.** When a chatbot grades a student essay and quotes the essay to support its comments, do the quotes occur in the essay, and in the sentence it names?
2. **Grade stability.** How much does the grade vary when the same essay is graded repeatedly under the same conditions?
3. **Error detection.** Does the chatbot report a deliberately inserted factual error or contradiction, and does it refrain from reporting that error at the same place in the unchanged original?

## 2. Kind of study

This is a feasibility pilot. It tests whether the procedure works and what it shows on a small scale. It makes no confirmatory claims and tests no hypotheses. Results are reported as counts (for example "2 of 9"), without rates, confidence intervals or comparisons between chatbots that would claim a difference. Three essays cannot represent the corpus, and three chatbots on given days cannot represent their providers.

There are no human reference grades for these essays. The pilot therefore measures stability and traceability of the grading, not whether the grades are correct.

## 3. Materials

**Corpus.** GENIUS Keylog Corpus (IPN Kiel, 2025; CC BY 4.0), cited as Schaller, Jansen, Höft, Pünjer & Horbach (2026), LREC 2026, pp. 6919–6928, doi:10.63317/4zdv5j2yj6vg. Argumentative essays on which energy carrier (batteries, hydrogen or e-fuels) should be promoted for cars, written in about 15 minutes. No new data from students is collected.

**Essays.** `1081_Verk_T1-Rev`, `298_Verk_T1` and `950_Verk_T1-rev`. They were drawn with a fixed seed (`20261113`) from texts with at least 80 words and an argument annotation. Two texts of the original draw had no conclusion. Before any run, they were replaced by the first two texts of the available reserve whose annotation carries the label `Schluss`, under a rule committed before it was applied. The available reserve leaves out the eight reserve texts that supplied sentences for the fabricated reference cases. The essays are therefore chosen among the few texts with a conclusion (33 of 262 annotation files) and are not representative of the corpus.

**Versions.** Each essay is used as the original and as one modified version with exactly one inserted error. The error changes one passage within one sentence. Its original passage was checked as correct against the task material, and the error is detectable without that material, either as a contradiction within the essay or against general knowledge. The definitions of the three errors (site, type, accepted categories, target description, edits) and the coding notes with accepted and rejected descriptions are withheld until the runs are finished and then published. Their SHA-256 values are committed in `prereg/sealed_sha256.txt`:

| Withheld file | SHA-256 |
|---|---|
| Trap definitions (input to `make_prompts.py --traps`) | `0865fb81880dc616052f3e566b2c0f4f30fe8f8b7dd35666c3717b203f61f745` |
| Coding notes for stage 2 | `96a561772979ea2582539828d1e67112a509c11c49ef56c1d04869d896395897` |

**Prompt.** One German prompt per essay and version, built by `scripts/make_prompts.py` from the template `prompts/grading_prompt_de.md` and the task and marking guide `prompts/aufgabe_und_erwartungshorizont_de.md` (SHA-256 `34a1fefc566f60b15a40ce1cf159fd8b3d0366555a824d55d86b8c3446d2902c`). The essay appears as numbered sentences (`[S1] …`). The chatbot is asked for a grade from 1 to 6, comments with quotes and sentence numbers, references to the criteria K1 to K7, and error reports, as JSON according to `schemas/output.schema.json`.

The marking guide restates the task in own words and does not contain the material table of the original task. It defines six requirements, each scored 2, 1 or 0 points, a points-to-grade key with caps, and asks for verbatim quotes with sentence numbers.

The six prompt files are fixed by their hashes:

| Prompt file | SHA-256 |
|---|---|
| `runs/prompts/1081_Verk_T1-Rev.original.md` | `9e8bb83173df45682002c5ebd320d4dd2f6498fb440346c2c556b54873a14b65` |
| `runs/prompts/1081_Verk_T1-Rev.veraendert.md` | `8f1561f72c722c96ce0d92070150c4775f9de2e8c60b1843cba64b1c868395a7` |
| `runs/prompts/298_Verk_T1.original.md` | `6cfba8e0bf0ff62379ef7c14d7677608a6cec30081483285727826dd366e5fcd` |
| `runs/prompts/298_Verk_T1.veraendert.md` | `f9a68b5b9b7b2890310d2de51adee227fff06e3848a9431fda06c24ddab7d5de` |
| `runs/prompts/950_Verk_T1-rev.original.md` | `ba5c8a60d628ceae106d5ae240868ba152ac96bc7645f0ebaa2e50645d9b397d` |
| `runs/prompts/950_Verk_T1-rev.veraendert.md` | `4c1c5af20eb60fd3653b73749e3707fba18002531bd97209f97f964460d1818d` |

## 4. Procedure

**Test subjects.** ChatGPT, Gemini and Grok, used through their public chat interfaces.

**Condition.** Each run uses the default model and the default settings of the interface, in a new temporary or private chat, without memory and without custom instructions. The model selector, thinking modes and tool settings stay unchanged. Account type and the model name displayed by the interface are recorded for each run.

**Runs.** 54: 3 essays × 2 versions × 3 chatbots × 3 repetitions. The order is fixed in `prereg/laufplan.csv` (randomized with the seed) and spread over two days, 27 runs each. The author performs all runs by hand, without automation, and copies each answer unchanged into its file. Date, time, chat mode, account type and displayed model are entered before each prompt is sent.

**Failures and protocol errors.** An answer that is not exactly one valid JSON value according to the schema is a failed run, with four predefined exceptions described in the README (one code block around the answer; an unknown error category; sentence numbers; an unknown criterion). The spellings `"3"`, `3` and `"[S3]"` are rewritten to `S3`; any other form, or no number, counts as a missing number and keeps the run usable. Failed runs are not repeated. A run whose metadata cannot be reconstructed is recorded as a protocol error and enters no measure. No run is replaced.

## 5. Measures

Per chatbot. Quote measures are reported twice: strict and after the predefined normalization (whitespace, typographic quotation marks, one final `.`, `!` or `?`).

| # | Measure | Counted | Out of |
|---|---|---|---|
| 1 | Failure rate | failed runs | attempted runs |
| 2 | Quote fidelity, text | quotes whose text occurs in the essay | delivered quotes |
| 3 | Quote fidelity, text and location | quotes that occur in the named sentence | delivered quotes with a sentence number |
| 4 | Evidence coverage | comments with at least one delivered quote, valid or not | all comments |
| 5 | Evidence coverage, local | not computed in the pilot | |
| 6 | Criterion fidelity | criterion references inside K1 to K7 | all criterion references |
| 7 | Criterion coverage | comments with at least one criterion reference | all comments |
| 8 | Grade variation | distribution, range and most common grade per essay and chatbot, originals only | usable runs |
| 9 | Detection per usable run | runs with a hit | usable runs of the modified version |
| 10 | Detection per attempted run | runs with a hit | attempted runs of the modified version |
| 11 | False alarm | runs that report the target error at the target site | usable runs of the original |
| 12 | Unclear | runs coded `unklar` | coded runs |

A measure with an empty denominator is reported as undefined, never as 0 or 100 %. Measures 4 and 7 can stay below 100 % even for flawless answers, because the marking guide asks for comments on the whole text without a quote when something is missing, and comments on A1, A4 and A5 often name no criterion K1 to K7.

Quote checking is deterministic. It uses the INSPEKTORIUM kernel unchanged (`src/`, tree `0afbc0115f904d6408b1b8196af4e019678d3c56`) and `scripts/check_quotes.py` (blob `2a3368683da37db01ae6487dc75cf552c6bfa9e0`).

## 6. Hit rule and coding

**Stage 1, mechanical.** An error report passes if it names a target sentence and one of the accepted categories of the trap.

**Stage 2, human and blind.** The author codes every usable run of a text with a trap on a sheet that shows the run's error reports and the target description, but not the chatbot, the version or the repetition. The order is random. The answer is `ja` (with the number of the report), `nein` or `unklar`.

**Main analysis.** A hit requires stage 1 and `ja` for the same report. `unklar` counts as not detected in the modified version and as a false alarm in the original. A report with an unknown category at the target counts the same way.

**Counter assumption.** Measures 9 to 11 are repeated with `unklar` and unknown categories at the target counted in favour of the chatbot. Both results are reported.

A hit does not require a valid quote; quote fidelity is measured separately.

## 7. Reporting

All results are published, whatever they show, together with the prompts, the modified texts, all chatbot answers, the coding sheet with its key and the analysis output. The withheld trap definitions and coding notes are published at the same time, and their hashes can be checked against this document. The grades of the modified versions are reported separately from measure 8.

## 8. Deviations

Every change after this registration to the import, analysis, export or prompt generation code, to the marking guide, to the trap definitions or to the coding notes is a deviation and is named in the report with its reason. The frozen tools in section 5 must not change until the held-out reference cases are evaluated.

## 9. Known limits

- Three essays, chosen among texts with a conclusion, are not representative.
- No human reference grades: correctness of the grades is not assessed.
- One coder, who also prepared the errors. The coding is blind to chatbot and version, but there is no second coding and no agreement measure.
- Measure 5 (local evidence coverage) is not computed.
- The chatbots do not receive the material table of the original task.
- Chatbot behaviour may change between days and with the account type; both are recorded, not controlled.
- The pilot uses three repetitions per version; the planned main study uses ten for the originals.

## 10. Use of AI assistance in preparing this study

The study tools were written with an AI coding assistant (Claude Code, Anthropic). The design was reviewed with Claude and with an assistant based on ChatGPT. ChatGPT is also a test subject. The test runs use a new temporary chat without memory, and the trap definitions were not shared with that assistant. Claude and Mistral are not test subjects.

## 11. Further frozen identifiers

| Item | Value |
|---|---|
| Seed | `20261113` (`prereg/seed.txt`) |
| Held-out reference cases | SHA-256 `290116c15e4dd5642a653af88d2544b18c0e452455b8caee38dbc5570a2d1a6a` |
| Manifest of the prompt generation | SHA-256 `39b79707f5d330a8418e88bde716cd11bd47ee4c48e647e65a9ea4005334f79c`, script commit `e41175dbc99fb140a9a41fa72d71ca6a717fead7` |
| Corpus source | darius-ipn/genius_keylogs, commit `34300c815c70a6ea52398d7a64305296c44663d7`, file `annotations.zip` |
