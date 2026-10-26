# Public release closeout — independently completed 2026-10-26

**The public download and installed-package verification passed.** This is a
new execution after interruption of the original publication session. It does
not assert that the unavailable earlier Mac process completed.

## Published source and releases

- Repository: [LAKITALKS/Inspektorium](https://github.com/LAKITALKS/Inspektorium)
- Publication merge: `94eb4fc8b26c22da6a2cebdd01e5a7799750104d`
- Integration: [PR #1](https://github.com/LAKITALKS/Inspektorium/pull/1)
- Original published-main CI: [four successful jobs](https://github.com/LAKITALKS/Inspektorium/actions/runs/40310046071)
- Reference package: [Inspektorium 0.1.1](https://github.com/LAKITALKS/Inspektorium/releases/tag/v0.1.1)
- Full audit runtime: [Agent Arena 1.0.1 research prerelease](https://github.com/LAKITALKS/Inspektorium/releases/tag/agent-arena-v1.0.1)

The two annotated release tags still point to the publication merge.
The `v0.1.1` tag object is `cee18b187eac3b6534d1bd97cc9b724f55a306b8`;
the `agent-arena-v1.0.1` object is
`2130059b5f7f65d15666b5f79507dd7b6fbc7536`.
Historical `v0.1.0` remains unchanged. The original
[import record](../2026-10-26/README.md) explains source mapping, exclusions,
redactions, rights and retained limitations.

## New execution and measured result

The successful verification ran **2026-10-26 16:32:56–16:34:21 UTC**, on
Python 3.12.14 / Linux x86_64. **24 recorded checks passed; all 88 commands
returned their expected exit codes.** The complete
[machine-readable report](summary.json),
[detailed execution](completed-attempt/results.json), and
[hashed evidence inventory](evidence-manifest.json) preserve the measurements.

- A fresh anonymous clone, all three tag identities and final remote refs
  matched the recorded expectations.
- Five actual release downloads matched the final expected hashes and the
  downloaded release checksum files, including the complete E1 image ZIP.
- Four automatic source archives matched **4,430** files each in their
  corresponding verified Git trees.
- Both wheels and both source archives installed in **four fresh
  environments outside source**. Installed versions, 19 reference-package
  modules and 74 audit-runtime modules matched the public source; all four
  dependency-consistency checks passed.
- The reference checker reproduced **20** expected outputs byte for byte.
- The full audit runtime passed the positive, negative and UNKNOWN offline
  cases in both installations. UNKNOWN stayed `REVIEW_REQUIRED`, remained
  inspectable as an intact bundle and was refused release in both cases.
- The LR01 saved capture was extracted and reanalysed as a **new recorded
  offline analysis**, which passed inspection. This is not historical native
  replay or authentication of the original live run.
- Four guard counterchecks refused **20** deliberate non-loopback
  operations and allowed **four** positive loopback connections. Actual
  offline evaluation recorded **55** guard activations and **zero**
  unexpected network operations.

The final core source archive hash is
`74428c0e2098aff3bdf015f6cd62a20855135af8565ae8a8297d84fc096db2ba`.
The prior preparation record's different hash is preserved and explicitly
explained in [expectation provenance](expectations-provenance.json): the
final archive was rebuilt after three documentation corrections. The actual
download and its published checksum match the final value.

## Preserved failure and limits

The first direct-network attempt failed during clone because this runtime
requires a proxy. No installation or offline example ran in that failed
attempt. Its [result](direct-network-attempt/results.json) remains visible.
The successful execution used a credential-free runtime transport wrapper,
kept TLS verification and every verifier assertion enabled, and supplied no
GitHub or provider credentials. See [transport and reproduction details](SUMMARY.md).

Full scientific/test suites and E1 image measurements were not repeated in
this bounded download check. Original local/CI results retain their original
conditions. The Python socket guard is not OS-wide monitoring. Private
original files on the earlier computer were not available for a new
preservation check. Historical hash-bound replay limitations, two unavailable
superseded source variants, the audit lint baseline and the unmet scientific
efficacy gate remain as disclosed in the original publication record.

This report is available in the repository. Uploading a copy as a release
attachment is a separate publishing action; this document does not assert
that such an upload already happened.

Lazaros Varvatis remains the sole human project/software author. The
source-available PolyForm Noncommercial 1.0.0 license and third-party
attributions are unchanged.
