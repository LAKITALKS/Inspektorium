# Final publication provenance review B — 2026-10-26

**PASS for the frozen history, listed release assets and reviewed working delta.** No unresolved publication-content finding remains in that scope. This concludes review B for the audited bytes. It is not the overall push gate: full-suite acceptance belongs to the orchestrator and final reviewer D; final evidence-commit delta and final source-archive scans remain mandatory as stated below. No original or integration product file was edited by this reviewer.

## Frozen history coverage

Public base: `4bd0ba9218df80a69089838f824ae0ac28881ac4`.
Frozen candidate: `b87858c5674dd034a69f4d40b623a74077baa239`.
Frozen tree: `f21c995edcc3e82bf6eee4375d87796d960defcb`.

The three newly reachable commits are `0424d450103654669b0a200e460c48ef5fc6dbec`, `dd739ebfe35a9c5aba46b8ae4ede133304da74b8`, and the frozen candidate. Direct Git enumeration confirms **3,496 unique blob objects** in those commit trees. The sorted blob-ID set SHA-256 is `7404ca16ef29d579d2c988485527c2b0eed1737020e90f3b41f1eb46bb7762cd`. No private source-history ancestry was imported into this range.

The orchestrator executed the full range scan, `corrected-history-scan.json`: **PASS, zero findings, 7,286 examined objects including 17 archives, 16 PDFs and 80 PNGs**. Reviewer B checked the resulting record, its public copy identity, the actual commit graph and unique-blob count rather than repeating that expensive content scan. All three new commits have Lazaros Varvatis and the authorized published email as both author and committer; no Co-authored-by trailer appears. Existing public history is unchanged.

## Actual release artifacts and metadata

Reviewer B independently reread and hashed the actual five payload artifacts and both checksum files. All five payload hashes match the corresponding SHA256SUMS files and the recorded release hash list. The four built-package hashes also match `final-package-member-identity.json`; its recorded module-byte comparisons cover 19 core modules and 74 Arena modules. Wheel metadata was inspected directly: core 0.1.1 and Arena 1.0.1, Python >=3.11, Lazaros Varvatis, the published email, and included PolyForm license files. Root and Arena LICENSE bytes are identical. The third-party notice preserves dependency/font rights and source attribution without treating citations as project-owned text.

| Artifact | SHA-256 |
|---|---|
| `inspektorium-0.1.1-py3-none-any.whl` | `7191276995f9f87cb4e7a699ca020d6aa2decd844c123d97601d96fb08c0c721` |
| `inspektorium-0.1.1.tar.gz` | `665d4011927c7e0b959ac5e5593e19f7e622b0af02bb6d127ff4d84b07e1ca70` |
| `inspektorium-0.1.1-publication-e1-evidence.zip` | `7fad066f094e8fcba385ebd39d86ae4a3676d87b7981c3a06dd0e72f58246e1a` |
| `agent_arena-1.0.1-py3-none-any.whl` | `0899b28bd3c02e97a814b7a8c43fc251ced61ab79d178f6a26ddfdf7e892ccd1` |
| `agent_arena-1.0.1.tar.gz` | `0b17f88bfc1c1b274295ec4fc9912c5b32f1f36e747570ebc19759aabe66a598` |

The completed asset scan reports **PASS, zero findings, 7,912 objects, three ZIP-format archives, 19 tar archives, 380 PNGs and 12 PDFs**. These include nested evidence archives. Reviewer B did not rerun the same heavy scan. `arena-sdist-normalization.json` contains 3,292 member proofs: every original/public payload hash is equal, all payload/permission invariants are true, and ownership/mtime normalization is recorded. The archive digest changed solely through packaging metadata; the private original is retained by the normalizer.

## New snapshots and current evidence delta

The eight added historical snapshots contain **405 source/package-metadata files**, individually matched to the inventory's origin hashes. Fourteen producing-source snapshots are now present in total. The earlier targeted follow-up examined 415 changed/snapshot/result files without a content finding. Historical snapshots remain source archives rather than public Git objects or new live authorizations. The disclosed unavailable superseded pre-RC variants and the P5A manifest's missing producer-code ID are not silently reconstructed or assigned invented provenance.

The post-freeze evidence/tool delta directly scanned by reviewer B contains **11 files**. Reviewer B scanned those bytes and recorded their SHA-256 values in `final-b-working-delta.json`: **PASS, zero findings**. A prior scanner self-match was its literal private-path detection expression, not an actual private path. The public expression is now split into equivalent adjacent byte literals; reviewer B confirmed the compiled pattern is byte-identical and the self-match is gone. This does not narrow the protection. The orchestrator subsequently added public verification tools and recorded a separate seven-file PASS in `public-verifier-import-scan.json`. A generated Python bytecode cache was moved outside the integration checkout; no such cache remains under the publication directory at report finalization. Future tool imports use `PYTHONDONTWRITEBYTECODE=1`. These later additions and this report are covered by the required final committed delta scan.

Private account fields, user paths and active historical authorization files remain excluded or explicitly derived as recorded in the import manifest. Historical embedded hashes still identify originals. Public authorizations are INERT; native replay on those altered authorization directories is intentionally unavailable. The new capture-to-recording route is labelled recorded offline and does not claim old-bundle authentication. No new live test, budget opening or scientific efficacy claim is introduced.

## Required final closure before push

1. The orchestrator and reviewer D record the actually completed corrected full suite and final acceptance outcome. That acceptance is outside review B; this provenance review does not replace it.
2. Commit the final reports/docs/tools. Then scan **all newly reachable commit metadata and new blob IDs after the frozen candidate**, not only a final-tree diff. Byte-identical blob IDs already covered by the frozen full scan can be reused. Confirm no runtime/package/test/script product change occurred after the frozen tested candidate; otherwise repeat affected acceptance.
3. Scan the actual final Git source archive, bind its hash and final commit, and verify that no unintended untracked files entered it. Public package/source/release archives must derive from the audited selection.
4. Preserve the existing public tag and source origins. After publication, verify the actually fetched commits/tags/artifacts against these hashes and the final evidence delta.

`publication_delta_audit.py` implements the bounded history-plus-delta check and records the frozen scan's own digest, commit IDs, covered-blob digest and every new blob/commit. Its clean positive control passed. Its invalid counterexample contained a synthetic credential-shaped string only in an intermediate commit, then deleted it from the final tree; the delta audit still detected it. This demonstrates the intended new-history coverage without re-reading old large archives. The final committed audit must also include this report and any later reviewer records.

The scanner is a focused content/structure check, not exhaustive secret detection or OCR of every screenshot. Publication does not resolve sealed input availability, old private Git associations or the scientific Final v1 efficacy gate. Within the reviewed publication scope, no additional secret, private-data, authorship, package-content or rights-attribution blocker was identified.
