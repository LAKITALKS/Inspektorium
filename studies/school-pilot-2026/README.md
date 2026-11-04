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
| `data/selected/` | Sentence banks of `pilot` and `component`, marked in their README | yes |
| `prereg/` | Seed, drawn groups, and later the preregistration | yes |
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
