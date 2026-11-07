# Selected texts

These files are sentence banks of the `pilot` and `component` groups and of the two `reserve` texts that replaced pilot texts, copied byte for byte from the output of `scripts/genius_loader.py`.

- **Source:** GENIUS Keylog Corpus, IPN – Leibniz-Institut für die Pädagogik der Naturwissenschaften und Mathematik (2025).
- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The full source is in [ATTRIBUTION.md](../../ATTRIBUTION.md).
- **Changes:** Texts were converted (HTML entities unescaped, Unicode NFC) and split into numbered sentences using the corpus's own sentence segmentation.
- **Modified:** None of these files has deliberately inserted errors.
- **Replaced:** `327_Verk_T1` and `975_Verk_T1-rev` are marked as replaced. Their banks stay here, and the run plan and the prompts do not use them. `298_Verk_T1` and `950_Verk_T1-rev` took their places. See [Replacing pilot texts](../../README.md#selection).

`sentence_criteria.json` lists, for each sentence of these texts, the criteria K1 to K7 that the corpus annotators marked in it.

The texts of the other groups stay in the ignored `data/external/` folder. [prereg/selection.json](../../prereg/selection.json) lists their ids.
