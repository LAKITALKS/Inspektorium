# Fresh public verification: prepared script

`verify_public_release.py` performs the requested bounded post-publication check. It does not publish, push, merge, tag, upload, run a full test suite, or invoke a provider. This preparation has not downloaded or verified unreleased artifacts.

## After publication

1. Copy `public-verification-expectations.template.json` to `public-verification-expectations.json`.
2. Replace every REPLACE placeholder with values from the reviewed local publication record and final reviewed release files. Do not derive expected hashes from the same public download being verified. The pre-existing v0.1.0 object/commit pair in the template was read from the current integration checkout; retain the independently recorded original values.
3. Confirm the two releases are public, with their wheel, sdist and a file named exactly `SHA256SUMS.txt`. The core release also has `inspektorium-0.1.1-publication-e1-evidence.zip`, already listed in the template's `attachments` with its independently reviewed SHA-256 to fill in. List any further release attachments there before running. The script requires an exact asset inventory; an unexpected or omitted attachment fails the check. Arena must be a published prerelease; core must be a published non-prerelease. The two new tags must be annotated.
4. Run using Python >=3.11 and an output directory that does not yet exist:

```sh
python3 verify_public_release.py \
  --expectations public-verification-expectations.json \
  --output fresh-public-verification
```

An optional `--python /absolute/path/to/python3.11` selects the interpreter used to create all four fresh environments. The invoking interpreter also needs >=3.11. Run from the work folder, or supply absolute paths to the script/config/output. Installation uses anonymous PyPI setup access. The child environment omits `HOME` and does not repurpose it or `CODEX_HOME`. Provider keys, authentication tokens, proxies and askpass settings are excluded; Git global/system config and credential helpers are disabled. Pip uses `/dev/null` configuration, disabled keyring and `/dev/null` netrc. Repository and release downloads use anonymous HTTPS.

Exit 0 means every requested check actually passed. Exit 1 leaves measured partial results and failure details. Unstarted environments retain `not_executed`; no missing check becomes success. Existing output directories are refused. The script does not erase failed output or retry a publication operation.

## What it checks

- New HTTPS clone of `https://github.com/LAKITALKS/Inspektorium.git`, expected main commit, expected tag object and peeled commit for core, Arena and historical v0.1.0; a final anonymous remote-ref read confirms they stayed unchanged.
- Actual GitHub release metadata: published, not draft, component-appropriate prerelease flags.
- Actual public wheel, sdist, `SHA256SUMS.txt` and every listed release attachment for each component. Every package and attachment, including the E1 evidence ZIP, must match both the public checksum file and the independently supplied reviewed SHA-256. Both the release asset inventory and checksum entries must match the reviewed inventory exactly. E1's byte identity is verified here; its scientific measurements are not rerun or relabeled as fresh executions.
- The ZIP and tar.gz automatic source archive of each component tag, read directly from GitHub's public tag URLs. Regular file contents must match a local Git archive of the verified tag; traversal, duplicate paths and nonregular files are rejected. Current tracked publication tree has no symlinks.
- Four fresh venvs outside the fresh source clone: core wheel, core sdist, Arena wheel, Arena sdist. Dependencies/build setup occurs before guard installation.
- The fresh clone's checked Python socket guard copied into each environment, with its .pth activation. Its existing canary must refuse five non-loopback operations and allow a loopback connection before measured examples begin. Every subsequent interpreter invocation must log an armed guard and no refused network operation.
- Installed metadata/runtime versions, imports inside the new venv's site-packages, and exact 19 core / 74 Arena Python module hashes against the fresh public source clone.
- Ten core outputs per installation: five examples in JSON and Markdown, byte-equal to published expected reports.
- Arena positive, negative and UNKNOWN validation/run/inspection in both installs; unresolved UNKNOWN release must remain blocked.
- In the installed Arena wheel environment, extract public LR-01 attempt-002 response text through the published helper, run it with --offline, inspect its READY_FOR_RELEASE bundle. The result is explicitly recorded_offline reanalysis, not native historical replay or original bundle validation.
- `pip check` in all four environments and final unchanged source clone.

## Output and privacy

`fresh-public-verification/public/results.json` and `public/logs/` contain scrubbed measured results/commands. Setup, download and offline logs are separate. Transient signed GitHub redirect query strings are not logged. Local output roots, home/account paths and common token forms are scrubbed from public text. These are the candidate publication outputs to review.

`fresh-public-verification/work/` contains the actual clone, downloaded archives, virtual environments, internal network logs and generated bundles. Keep this local working state out of release uploads. The socket guard's reach is Python's published socket hooks in those environments; it is not an OS-wide network monitor. Installation/download networking is not counted as offline evaluation.

## Preparation verification actually executed

- `python3 -m py_compile verify_public_release.py`: passed.
- `python3 verify_public_release.py --self-test`: passed, with no network or release verification execution. It exercises evidence attachment expectations, checksum parsing, invalid paths and tar/ZIP content manifests.
- `ruff check --isolated --select E4,E7,E9,F,I verify_public_release.py`: passed.
- The complete public-clone/download/install workflow is **not executed** at this preparation stage. It must be run after the real public releases exist.
