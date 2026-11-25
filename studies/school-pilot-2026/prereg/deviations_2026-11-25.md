# Deviations and notes after data collection, 2026-11-25

- **Author:** Lazaros Varvatis
- **Preregistration:** [preregistration.md](preregistration.md), DOI [10.5281/zenodo.24131848](https://doi.org/10.5281/zenodo.24131848), frozen study state commit `bfcd872e464e1ab87fdc2e514e0e3792ef8c31f6`
- **Status when this was written:** All 54 runs were performed on 2026-11-23 and 2026-11-24. No answer has been imported, coded or analyzed. The answer files were checked for their format: whether they parse as JSON, and where copy marks occur.

The files of the frozen study state under `scripts/`, `prompts/` and `prereg/`, and `src/` of the repository, are unchanged. This file, `scripts/undo_copy_marks.py` and its tests are new. All times are local times.

## 1. Capture helper

The answers were moved from the clipboard into their files with a helper script, `lauf.py`. It handled files only and did not operate any chatbot. The versions used:

| Used for | SHA-256 of `lauf.py` |
|---|---|
| Run 1, first attempt at 11:38 on 2026-11-23, reset before sending (see section 2) | `aa023f943bd413f51c26c3a134405bbe2755e195a4d95e57c8fff17bbd38c7e6` |
| Day 1, 2026-11-23 | `10885635635a1de81b59c5f4283a30d7ab1d68b6d6421427f46c316ae4af1ab4` |
| Day 2, 2026-11-24 | `20ae5b43e992e6e8f31c492be87520a5b27f570281d4586cd67ffe65bace3a0c` |

The helper will be published with the results.

## 2. Reset of run 1

Run 1 was reset before sending. Its metadata was written at 11:38, the prompt was never sent, and the run was reset at 11:49. The run notes record this. The run was then performed normally.

## 3. Copy path of ChatGPT

The copy button of ChatGPT returns Markdown-escaped text: a backslash at the end of every line except the last, and `&#x20;` for a leading space. In a test it also escaped `\`, `_` and `*`. As captured, 0 of 18 ChatGPT answers parse as JSON.

The following rule was fixed before any result was viewed. For answer files that show these marks:

1. Remove a backslash directly before a line break or at the end of the file.
2. In one pass, replace a backslash followed by ASCII punctuation by the punctuation, and decode numeric character references (`&#x..;` and `&#..;`).

The rule applies only to files with the marks. The raw files stay unchanged. `scripts/undo_copy_marks.py` applies the rule to a copy and writes a log.

Both analyses are reported:

- as preregistered, on the answers as captured: these ChatGPT answers count as failures;
- after the reversal.

In all 18 ChatGPT files the marks occur only at line starts and line ends, that is, outside every JSON string. The reversal therefore cannot change any value.

## 4. Copy paths of Gemini and Grok

The copy path of Gemini drops a backslash before a double quote. This did not occur: 18 of 18 Gemini answers parse as captured. For Grok, 18 of 18 answers parse as captured.

## 5. Interpretation notes

These notes were written before any result was viewed.

- **Grade resolution.** The grades are whole grades from 1 to 6. Fluctuation across a grade boundary can look like a full-grade jump, and differences within a grade stay invisible.
- **Snapshot.** The results refer to the models as displayed on 23 and 24 November 2026; the displayed names are recorded per run. The results do not transfer to other model versions or to school grading tools.
- **Blinding of the coding.** Identifiers are hidden, but the coder built the inserted errors and may recognise the version from quoted wording. The statement of the preregistration that the coding is "blind to chatbot and version" is therefore too strong. This is a limitation.
