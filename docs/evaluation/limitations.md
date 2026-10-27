# Limitations

Each limit appears once on this page. Other pages link here.
Claim IDs refer to the [claim ledger](../research/claims.md).
Mechanisms are described in [methodology](../concepts/methodology.md).

## Reference checker (`inspektorium inspect`)

- **Exact text is not meaning (P14).** An excerpt can match its source exactly and still distort it.
  The source says "did not reduce mortality"; the quotation is "reduce mortality".
  Exact binding confirms where the words are, not what the relation means.
- **True quote, false relation (P09).** A true quotation with a deliberately false relation remains mechanically reportable.
  The reviewer probe on [example 02](../../examples/inspect/02_contradicted/proposals.json) changed `contradicted` to `supported` and it stayed reportable.
- **`not_established` is not refutation (P04, P15).** It can be reportable with all citation fields null.
  It records the evaluator's judgment about the supplied material.
  It is not a scientifically examined refutation and does not prove absence of evidence.
- **Empty findings (P10).** Empty findings are accepted. Zero validation failures do not establish claim coverage.
- **Exit 0 (P11).** A report with failed citations is still emitted with exit code 0.
  Exit 0 means successful report production, not assurance approval or release authorization.
- **Strict offsets (P17).** Correct text at a wrong offset fails by design. Nothing is searched for or repositioned.
  The tests and examples do not yield a general false-alarm rate.
- **Schema-valid is not proof of origin (P16).** A report that validates against the schema 0.1 models is not re-checked against its sources.
  It is no proof that Inspektorium produced it. Reports carry input hashes, not sources.
  Full evaluator provenance and a `verify` command are later work.
- **Fingerprints identify current content (P05).** They are not signatures or historical-state authentication.
  Changing source text outside a cited span does not invalidate the unchanged span.
  Paraphrases are not hash-equivalent.
- **Atomicity is a judgment (P01).** The span check does not establish atomicity, truth or complete extraction.
- **Qualitative descriptors.** `evidence_sufficiency` and `evaluator_certainty` are not calibrated probabilities.
- **Library parsing (P13).** `InspectionInput.model_validate_json` and `ProposalBatch.model_validate_json` let the last duplicate key win.
  Only `parse_inspection_input_json` and `parse_proposal_json` apply the strict decoder.
  Errors on the `--answer`/`--source` path keep their earlier form.
- **Provider path (P08).** One application SDK invocation does not guarantee one HTTP attempt, bounded billing or authenticated execution.
- **Determinism (P06).** Stable bytes hold for fixed inputs, saved proposals and timestamp settings. Repeated live calls can differ.

## Display

These limits concern the Markdown display of the reference checker (P12).

- **Look-alike brackets.** Only the exact marker brackets U+27E6 and U+27E7 are marked.
  Look-alike brackets such as U+301A and U+301B are not. Text can resemble a marker; it adds no report structure.
- **Unmarked characters.** Private-use characters (Co) and invisible characters outside Cc, Cf, Cs, Zl and Zp stay raw.
  Up to four consecutive Mn/Me characters stay raw, including variation selectors.
- **Unicode database dependence.** Categories come from the running Python's Unicode database.
  Characters assigned in a newer Unicode version, such as recent emoji, become markers on an older Python.
  The Markdown of the same JSON report can therefore differ between Python versions.
- **Untested viewers.** GitHub web-service post-render features (@mentions, issue references, emoji shortcodes, math) were not tested.
  Other Markdown viewers were not tested.
  Python-Markdown was tested only with `tables` and `fenced_code`, not `attr_list` or `extra`.
- **Fonts.** The four-mark bound is a text property, not visual integrity in every font.
  Pixel evidence covers the named Noto and local GitHub-like configurations only ([layout follow-up](../../evidence/v0.1.1/addendum-20261024-e1-layout/README.md)).
  It measures added ink, not human readability.
- **Trailing-space stripping.** A tool that strips trailing spaces joins the lines of a multi-line quotation into one displayed line.
  Text and structure stay intact.
- **Audit reports.** The audit workflow does not apply the reference checker's display encoders. It uses its own renderers.

## Audit workflow (`inspektorium audit`)

- **Technical release is not scientific truth.** `RELEASED` means these exact local artifact bytes passed the current controls and explicit intent.
  It does not certify the original claim. A contradicted finding can also reach `RELEASED`.
- **Model/host agreement is not independent corroboration.** Semantic classification and review can err (R08, R09).
- **Closed Corpus.** Audit examines only the supplied material. It is not an exhaustive literature search.
- **Review names are not authentication.** Reviewer names and reasons are recorded provenance.
  They cannot waive a failed control. No reviewer or review queue is assumed.
  A mandatory unresolved review stays unresolved and unreleased.
- **Duplicate JSON keys.** `audit validate` accepts a task file with duplicate JSON keys. Only `inspect` rejects them.
- **No reference-checker guards.** Audit does not run the reference checker's strict decoder, exact-span rules or display protections.
- **Parent link not re-verified.** `audit inspect` checks one bundle on its own.
  It does not re-check that `parent.manifest_fingerprint` matches the parent bundle; `review` and `release` set the link after inspecting the parent.
- **Hashes, not signatures.** Bundle fingerprints provide integrity, not signatures, immutable remote storage or PKI.
- **Code-bound verification.** Bundles bind the installed audit-runtime module bytes.
  An earlier bundle is verifiable only with the code that produced it.
- **Formats.** Canonical PDF is unsupported. Browser print PDFs are test evidence for printable HTML only.
- **Inspect exit 0.** `audit inspect` exits 0 for an intact bundle even when its recorded status is blocked.

## Evidence and research status

- **Historical live evidence on older code only.** Limited live checks covered synthetic cases on earlier source states.
- **No new live validation.** There is no new live validation of the final runtime code or of 0.3.0.
- **Scientific Final v1 gate not met.** It requires real-case validation, a fresh efficacy comparison, fault injection and prior release criteria ([research plan](../research/plan.md)).
  H01 remains an untested hypothesis.
- **Owner-reported studies (I01–I07).** They were not independently replicated.
  Publication of derivatives is not replication or authentication of original live runs ([results](../research/results.md#owner-reported-internal-pilot)).
- **Pilot design.** Small author-constructed set, one model, ceiling effects and shared responses between conditions.
  Both semantically wrong control answers were accepted (I03).
- **Measured commits not public.** The v0.1.1 candidate and addendum commits are not in the public history.
  A full re-run can build only the baseline commit; later trees are checked against the recorded product hashes ([reproducibility](reproducibility.md#check-that-a-later-tree-carries-the-measured-product)).
- **Synthetic catalog.** The v0.1.1 catalog is not a holdout set and gives no detection or false-alarm rate ([evidence package](../../evidence/v0.1.1/README.md#limits)).
- **Network measurement reach.** The evidence harness guard is a Python socket hook. It does not cover native code or other programs.
- **Software tests are not efficacy.** Test counts and finite fault sets do not establish scientific efficacy.
- **Not claimed.** General AI safety, regulatory compliance, certification, alignment or framework conformance.
