# Focused E1 layout review — 2026-10-24

Review state: FOCUSED_E1_REVIEW_PASS. The E1 criteria are met for the recorded conditions. No open finding remains in this focused review. Overall `READY_FOR_PUBLICATION_REVIEW` still requires the root task's pending mandatory product checks and clean-install verification; this review does not claim those have already passed and grants none of the four publication decisions.

## Authority, scope and effective configuration

One separate read-only review of the E1 follow-up requested in the supplied Eudora text; no broad audit and no recursive delegation. Reviewed AGENTS.md and CONTRIBUTING.md. Product anchor: `5ace2797e4a9075ca53ccd780be616719923c288`; starting closeout anchor: `75ffd03e82a377f07027cfc0b884b454146c0a1e`; previous measured product: `403bd3fac27f2406a150b2243a691ba4d0b12fbb`.

The parent task reports the explicit user-approved substitute and actual invocation as GPT-6 Astra, Extra High (`gpt-6-astra`, `xhigh`). This is a separate review context, not a claim of independent model backend, provider, browser implementation or machine. No additional agent was spawned. Review scripts/results live only in this external work area. The reviewer made no repository edit, installation, download, live model/provider call or publication action. Python scripts used the pre-existing guarded Python 3.11.7 environment, `PYTHONDONTWRITEBYTECODE=1`, and a separate `review-netguard.jsonl`.

## Display path and mapping

The product diff has one display change: the encoded Atomic claim changes from a list item to a standalone paragraph immediately before the unchanged tight host-control list. The same `encode_inline(finding.claim_text)` call remains. No encoder, JSON, offsets, fingerprints, evaluator semantics, E2, E3 or license change is present in the product diff. Five expected Markdown reports and the structural helper/tests track that change.

The DOM mapping change accepts a P as well as an LI for the already bounded Atomic claim label, section and finding. It does not mark the whole Findings section, an unordered list or the following Answer span as payload. The retained tight list has no child paragraphs. The mapper excludes exactly one targeted payload row; every other selected h1/h2/h3/p/li row remains measured. Actual inventories and renderer HTML trees are checked below.

## Review finding and bounded correction

The initial new harness inherited an inadequacy from the previous harness: if the same Answer span row was missing from both DOMs, compare() still returned MEASURED without overlap. The previous validity script checked the three explicitly critical rows for matching omissions but did not test Answer span. A real preflight artifact (`E1-last_below-80`, Noto Serif) reproduced the issue: 60 measured host rows became 59 and still passed. This was a measurement-validity weakness, not evidence that an actual saved Answer span had disappeared.

The root task corrected only measurement validation: for this fixed three-finding catalog, both DOMs must contain the three finding headings and each of the ten prescribed finding labels exactly once; host-control labels cannot be classified as payload. CSS, crop, threshold, browser, font, case catalog and denominator are unchanged. The corrected harness hash is `14c1f3bb75321597f566188643bbd082a567b5370a6fb2bdcf3c711eba36ae5d`.

Reviewer retest: 1 unchanged actual positive and 36 deliberate invalid variants behaved as expected. The invalid variants cover all ten labels removed from both twins for each of the three findings (30), Answer span replacing the real payload, duplicate claim LI/P containers, changed Answer span text, and missing/corrupt images. Results: `review-e1-validity-fixed.json`; the initially failing probe is retained in `review-e1-probes.json`.

## Completed historical recount

All 600 historical PNG files were hash-verified and 18,000 host text crops were independently recalculated from pixels with grayscale <160, >=10 newly dark pixels and the unchanged two-pixel border. All counts matched saved measurements: baseline 45/75 Noto Serif and 42/75 local GitHub-like; prior product 6/75 and 5/75. All 900 historical Answer span measurements (450 per product) remain included.

Also checked all 696 actual historical input/proposal/JSON/Markdown file hashes and all 348 renderer records per product. Previous-product text max is four raw combining marks, with zero links; baseline maximum is 80 with 18 link-bearing records. The 87 JSON hashes match across the two historical products. The original artifacts were rehashed after the read-only recount and were unchanged. Evidence: `review-e1-recount-historical.json`.

## Completed final-run verification

The first full layout run belongs to the harness before the validity correction and remains preliminary evidence. This review consumed `layout-final-results` only after its summary was complete. Its manifest binds product `5ace2797e4a9075ca53ccd780be616719923c288`, catalog SHA-256 `245f945b39168ba0fdb250ebcce633d44fef080d7348738a64672e297e1e8380`, and the corrected harness hash stated above. The product wheel was separately hash-checked as `f8452a4f8d9b7be1778d1ef33a70de083ace95ad2c6e1bbf375388de8650da9c`, matching the recorded build/install provenance.

| Check performed by this reviewer | Result |
| --- | --- |
| New PNG hashes and independent pixel recount | 300/300 PNG hashes and 9,000/9,000 host crops match |
| Noto Serif | 75 measured, 0 INVALID, 0 overlaps |
| Local GitHub-like | 75 measured, 0 INVALID, 0 overlaps |
| New actual input/proposal/JSON/Markdown file hashes | 348/348 match saved records |
| JSON across baseline, previous product and layout product | All 87 byte hashes and objects identical |
| Four renderer configurations | 348/348 records: maximum raw/rendered run 4, zero links |
| Three ordinary multilingual clean cases | Retained within the 87-case catalog and all four text configurations |
| Answer span in current pixel measurements | All 450 row occurrences retained as host rows |
| Old/current DOM comparison, both actual and control | 18,300 row comparisons: identical text, section, finding, payload and visibility; only the three Atomic claim tags change LI to P |
| Fresh parsing of emitted Markdown through the four renderers | 348 HTML trees each have exactly three standalone claim paragraphs followed by tight nine-row control lists |

Every current visual record has 61 selected DOM rows, exactly one payload row and 60 measured host rows. Every other host row retains its previous text and membership; none is silently added to the payload exclusion. Atomic claim P nodes have no LI ancestor, and control LI nodes contain no P children. Thus the LI/P duplicate-container concern is excluded by the actual output structure rather than by deduplicating measurement data. Synthetic duplication still fails validation.

The complete final recount covers all three products: 900 PNG hashes, 27,000 host crops and 1,044 case-file hashes. All 1,944 reviewed source artifacts were rehashed unchanged at completion. Historical severe counterexamples remain detectable at 45/42 overlaps; the previous product still shows 6/5. The unchanged pixel criterion therefore still distinguishes both old failures from the new 0/0 result. Evidence: `review-e1-recount-final.json` and `review-e1-recount-final.log`.

Recorded measurement environment: macOS 14.6.1 arm64, Python 3.11.7 / Unicode 14.0.0, Chromium 156.0.8078.4, Playwright 1.64.1, Noto Serif and Noto Sans 2.015, 16 px, viewport 1000×900, device scale factor 1. Noto Serif uses normal line-height; the local GitHub-like layout uses Noto Sans with line-height 1.5. Four text renderers are cmark-gfm safe and unsafe, markdown-it-py with HTML enabled, and Python-Markdown. CSS, dark threshold, overlap threshold and crop remain unchanged.

One reviewer-only helper error occurred after the first final pixel recount: `list.index` compared cyclic HTML-tree dictionaries and raised RecursionError. It was corrected to use object identity, the initial script was retained as `review-e1-recount-initial.py`, and the focused recount was repeated successfully. This was neither a product failure nor a changed measurement rule. The original scripts contain local workspace bindings; any publication copy that removes those bindings must be identified as sanitized, not as the exact executed source. No full product suite or new browser capture was run by this reviewer. Full product checks and the final clean installation remain the root task's next step.

## Limits

This review inspects the product display path, saved CLI outputs, parsed HTML, saved DOM records and saved image pixels. It does not independently recapture all browser images. Results apply to the fixed catalog and recorded Chromium, fonts, viewport and layout configurations. The local GitHub-like layout is not the GitHub service. Added-dark-pixel counting is not a complete measure of text occlusion or human readability and establishes neither universal font safety nor scientific correctness. The fixed three-finding inventory validator is specific to this evidence catalog. Python socket guards do not establish system-wide network isolation. Publication decisions remain separately pending.
