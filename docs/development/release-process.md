# Release process

This page describes how an Inspektorium release is made.
Releases are published as GitHub releases of [LAKITALKS/Inspektorium](https://github.com/LAKITALKS/Inspektorium/releases).
There is no PyPI publication yet.
Past releases and their tags are listed in [history](../research/history.md#releases).

## Principles

- A release ships one distribution, `inspektorium`, as a wheel and an sdist.
- The maintainer authorizes each release. Commits, tags and releases are made under the maintainer's name.
- Existing tags are never moved. Published release assets are never rebuilt or replaced.
- Report only checks that were executed for this release. Historical counts are never reused as current results.
- Release notes state the limits that apply, with a link to [limitations](../evaluation/limitations.md).

## 1. Prepare the release branch

Work on a branch such as `release/vX.Y.Z` from current `main`.

- Set the version in [`pyproject.toml`](../../pyproject.toml) and in `__version__` of [`src/inspektorium/__init__.py`](../../src/inspektorium/__init__.py).
- Keep the report schema version unless the release deliberately changes it.
- Add a dated entry to [`CHANGELOG.md`](../../CHANGELOG.md).
- Set `version` and `date-released` in [`CITATION.cff`](../../CITATION.cff). The file must stay valid YAML.
- Keep [`LICENSE`](../../LICENSE) unchanged and [`NOTICE`](../../NOTICE) current.
- Update the documentation pages that name the version.

## 2. Run the local checks

Run every check from [testing](testing.md) in a fresh environment:

- `python -m pytest`, including the byte-for-byte reference examples;
- `ruff check .` and `ruff format --check .`;
- `mypy src`, and the audit-runtime type-checking baseline;
- `python scripts/run_acceptance.py --output DIR` against the installed package;
- a relative-link check over the changed Markdown files.

Run with provider variables unset. A release never needs a provider call.

## 3. Pull request and merge

1. Open a pull request from the release branch to `main`.
2. Wait until CI is green on the pull request.
3. Merge with a merge commit, not a squash or rebase. `gh pr merge --merge` does this; the local equivalent is:

   ```sh
   git switch main
   git merge --no-ff release/vX.Y.Z
   git push origin main
   ```

4. Wait until CI is green on the merge commit.

## 4. Tag

Create an annotated tag on the merge commit and push it:

```sh
git tag -a vX.Y.Z -m "Inspektorium X.Y.Z"
git push origin vX.Y.Z
```

## 5. Build the assets from the tagged commit

Build in a fresh clone at the tag and in a fresh build environment, never from a working checkout.

```sh
git clone --branch vX.Y.Z https://github.com/LAKITALKS/Inspektorium.git build-vX.Y.Z
cd build-vX.Y.Z
python3 -m venv ../build-env
../build-env/bin/python -m pip install build "hatchling>=1.27"
export SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
../build-env/bin/python -m build --no-isolation --outdir ../dist
cd ../dist
shasum -a 256 inspektorium-X.Y.Z-py3-none-any.whl inspektorium-X.Y.Z.tar.gz > SHA256SUMS.txt
```

Hatchling 1.27 or newer writes the `License-Expression` metadata; the build backend floor in `pyproject.toml` reflects this.

Check the assets before publishing:

- Install the wheel into a fresh environment outside the checkout. The installed package, not the source tree, must be imported.
- `inspektorium --help` and `inspektorium audit --help` run without provider credentials.
- The acceptance driver passes against the installed wheel.
- Both archives contain `LICENSE` and `NOTICE`. Neither contains `.pyc` files, `.DS_Store`, virtual environments or local paths.
- Scan the tracked content for credentials, private paths and personal data.

## 6. Publish the GitHub release

Write the release notes to a file. State the version, the install command, the executed checks with CI links and the limits.

```sh
gh release create vX.Y.Z --verify-tag \
  --title "Inspektorium X.Y.Z" --notes-file RELEASE_NOTES.md \
  dist/inspektorium-X.Y.Z-py3-none-any.whl dist/inspektorium-X.Y.Z.tar.gz dist/SHA256SUMS.txt
```

## 7. Public counter-check

After publication, check the release as an anonymous user:

1. Clone the repository afresh. Confirm that `main` and `vX.Y.Z` point to the merge commit and that earlier tags are unchanged.
2. Download all assets. Run `shasum -a 256 -c SHA256SUMS.txt`.
3. Compare each download with the local build, byte for byte, and with the asset digest that GitHub shows.
4. Install the downloaded wheel and, separately, the sdist into fresh environments. Repeat the checks of step 5.
5. Read the release page without signing in. Every link in the notes must resolve.
6. Add the CI run links of the release to [evidence](../evaluation/evidence.md#continuous-integration).
