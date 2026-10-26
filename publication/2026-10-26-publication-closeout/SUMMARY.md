# Independent public release verification — 2026-10-26

**Passed:** a new bounded public verification ran from 16:32:56 to 16:34:21 UTC against commit `94eb4fc8b26c22da6a2cebdd01e5a7799750104d`. Its 24 recorded checks passed and all 88 commands returned their expected exit code. This is a newly executed verification, not a claim that the earlier interrupted Mac run completed.

## Executed and passed

- Fresh anonymous HTTPS clone, clean checkout and unchanged final remote main/tag references. Historical v0.1.0 and both release tags match the explicit object/peeled-commit expectations; the two release tags are annotated.
- Actual published release metadata and exact asset inventories. Core is a published non-prerelease; Arena is a published prerelease.
- All five downloaded release artifacts match both the independently supplied final SHA256 expectations and the downloaded published SHA256SUMS.txt records. This includes the E1 evidence ZIP. The final core sdist hash is `74428c0e2098aff3bdf015f6cd62a20855135af8565ae8a8297d84fc096db2ba`; the earlier preparation digest is retained in `expectations-provenance.json`.
- All four automatic GitHub source archives (ZIP and tar.gz for each release tag) match 4,430 files in the corresponding verified tag tree.
- Four fresh environments outside the source checkout: core wheel, core sdist, Arena wheel and Arena sdist. Imports come from each environment's site-packages; installed metadata/runtime versions match 0.1.1 and 1.0.1. All 19 core / 74 Arena Python module hashes match the fresh pinned public source, in each installation. All four `pip check` commands passed.
- Twenty exact core reference-output comparisons: five cases × JSON/Markdown × two installation formats.
- Six Arena synthetic validations/runs/inspections: positive, negative and unknown in both installation formats. Positive and negative yielded READY_FOR_RELEASE; unknown yielded REVIEW_REQUIRED, inspected validly and was refused by the release command with RELEASE_BLOCKED (two refusal checks).
- One LR01 attempt-002 text extraction and fresh recorded_offline analysis in the Arena wheel environment, yielding READY_FOR_RELEASE and a valid inspection. Its recording SHA256 is `8158f814e89d771fb60d64cc17a984e681b0493c1d086426715ae8f479eaeeac`.
- Four guard counterchecks: 20 non-loopback operations refused and four clean loopback connections allowed. The subsequent measured runtime commands logged 55 guard activations and zero unexpected network operations.

## Failed attempt preserved

The first execution used the unmodified verifier's direct-network configuration and failed during clone because direct DNS is unavailable in this runtime. Downloads and all four installs were not executed in that attempt. Its report and clone log remain under `direct-network-attempt/`.

The successful attempt used `run_runtime_transport.py` to retain this runtime's credential-free proxy and trusted CA settings. TLS verification and every verification assertion remained enabled; the pinned original verifier is byte-identical. No GitHub/provider credentials were supplied. Setup and download networking is separate from guarded offline evaluation.

## Not executed and limitations

The full research/test suites and E1 scientific measurements were not rerun. No live provider calls were made. The LR01 result is a new recorded_offline reanalysis, not native historical replay or validation of an original live bundle. Historical authorization, ledger/review binding, provider authenticity and unredacted original identity remain unverified. The socket guard covers these Python processes, not the entire operating system. Packaging checks and bounded examples do not establish general semantic correctness or scientific efficacy.

See `summary.json`, `completed-attempt/results.json` and the setup/download/offline logs for machine-readable evidence. Public copies redact runtime interpreter and temporary pip-cache paths in addition to the verifier's own scrub; measured values and hashes are unchanged.
