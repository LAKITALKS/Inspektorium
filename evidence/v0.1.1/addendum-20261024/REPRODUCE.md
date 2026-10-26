# Reproduce the bounded E1/E2/E3 checks

Use Python 3.11 and a **new** scratch directory outside the checkout. The
commands below distinguish downloads from offline runs. The recorded commands,
full outer-command logs, versions and exit codes are under `results/`; the
original setup tool's nested pip records retain its standard 4,000-character
tails. Published logs replace local paths with `<WORK>`, `<REPO>` and related
placeholders; measured product/renderer text is not rewritten.

The original 70-case catalog and historical measurements need no rewrite.
`make_catalog.py` deterministically regenerates the separate 87-case file from
example 05. Its source is adapted from the supplied counterprobe, identified
by the ZIP hash in the script and closeout. Do not run it over a frozen file
without first comparing its bytes in a disposable checkout.

## Setup with downloads

```sh
REPO=/path/to/Inspektorium-v0.1.1
CHECK_WORK=/new/path/outside/checkout
mkdir "$CHECK_WORK"
cd "$CHECK_WORK"
T="$REPO/evidence/v0.1.1/tools"
A="$REPO/evidence/v0.1.1/addendum-20261024"
python3.11 -m venv dev
# For the exact recorded measurement versions use requirements-measurement.txt.
dev/bin/python -m pip install -r "$A/requirements-measurement.txt"
# Existing mandatory editable development installation, performed separately:
dev/bin/python -m pip install -e "$REPO[dev]"
PLAYWRIGHT_BROWSERS_PATH="$CHECK_WORK/browsers" dev/bin/playwright install chromium
python3.11 "$T/setup_env.py" build-venv --venv build-env --setup-log setup.jsonl
python3.11 "$T/setup_env.py" tools-venv --venv tools-env --setup-log setup.jsonl
```

Download the two upstream Noto 2.015 release ZIPs named in `fonts/manifest.json`.
Extract only the recorded regular/bold members into `fonts-2.015`, retaining
their exact filenames; copy the manifest there and verify every SHA-256. The
executed download helper is preserved as `repro-scripts/download_noto2015.py.txt`
and is runnable by Python (requires fontTools and curl). The `.txt` suffix
preserves the executed script as an evidence attachment without reformatting.
No global font configuration was changed.

Build exact versions; setup tool source paths must be in the repository:

```sh
python3.11 "$T/setup_env.py" build-wheel --repo "$REPO" \
  --commit fae18242de35facb7c493ff18e86baff3afe2c24 --out baseline-build \
  --build-python "$CHECK_WORK/build-env/bin/python" --setup-log setup.jsonl
python3.11 "$T/setup_env.py" build-wheel --repo "$REPO" \
  --commit 403bd3fac27f2406a150b2243a691ba4d0b12fbb --out candidate-build \
  --build-python "$CHECK_WORK/build-env/bin/python" --setup-log setup.jsonl
python3.11 "$T/setup_env.py" product-venv --venv baseline-env \
  --wheel baseline-build/wheels/inspektorium-0.1.1-py3-none-any.whl --setup-log setup.jsonl
python3.11 "$T/setup_env.py" product-venv --venv candidate-env \
  --wheel candidate-build/wheels/inspektorium-0.1.1-py3-none-any.whl --setup-log setup.jsonl
python3.11 "$T/setup_env.py" guard --venv dev
```

The product pins are the existing `requirements-product.txt`; old and new
product environments differ only by the product wheel. These commands refuse
any existing venv target; reuse an environment only for read-only measurements.

## Offline measurements

Unset provider credentials. The wrapper used for the recorded commands
removed environment names containing API_KEY, ANTHROPIC, OPENAI, TOKEN or
SECRET; it is included in `repro-scripts/run_command.py.txt`. Its recording
paths are relative to its own location. The venv `.pth` guard is armed before
Python imports product code. Browser page JavaScript is disabled and all routed
network requests are aborted.

```sh
export PLAYWRIGHT_BROWSERS_PATH="$CHECK_WORK/browsers"
export PYTHONDONTWRITEBYTECODE=1
EVIDENCE_NETGUARD_LOG="$CHECK_WORK/canary-netguard.jsonl" \
 dev/bin/python "$T/canary.py" --venv baseline-env --venv candidate-env --venv dev \
 --work canary-work --results canary-results
EVIDENCE_NETGUARD_LOG="$CHECK_WORK/baseline-netguard.jsonl" \
 dev/bin/python "$A/tools/check_addendum.py" --catalog "$A/catalog.json" \
 --venv baseline-env --fonts fonts-2.015 --work baseline-cases --out baseline-results \
 --commit fae18242de35facb7c493ff18e86baff3afe2c24 \
 --provenance baseline-build/build_provenance.json
EVIDENCE_NETGUARD_LOG="$CHECK_WORK/candidate-netguard.jsonl" \
 dev/bin/python "$A/tools/check_addendum.py" --catalog "$A/catalog.json" \
 --venv candidate-env --fonts fonts-2.015 --work candidate-cases --out candidate-results \
 --commit 403bd3fac27f2406a150b2243a691ba4d0b12fbb \
 --provenance candidate-build/build_provenance.json
```

**Exit 0 of the measurement script means execution completed; it does not
mean the protection passed.** Read the separate text/K7/visual counts in
`summary.json`. INVALID measurements cause exit 2. Current acceptance is
BLOCKED by the nonzero changed-product host-textbox results. The portable
reviewer scripts independently recompute pixels/hashes and check deliberate
missing-image/row/box defects; see `REVIEW.md` and `repro-scripts/`.

## Mandatory product checks and clean installation

From the checkout, with the installed dev environment:

```sh
ruff check .
mypy src
pytest --cov=inspektorium --cov-report=term-missing --cov-fail-under=80
```

The final clean installation used the already downloaded pinned product
wheels in a local wheelhouse, `PIP_NO_INDEX=1`, `PIP_FIND_LINKS=<wheelhouse>`,
and a new `final-clean-env` target. `verify_clean.py.txt --repo ... --venv ...
--out <new-output>` checked the site-packages import, all installed package
source bytes, `pip check`, and actual CLI JSON/Markdown for each of the five
examples. The 10 reports equal the committed expectations. Baseline/candidate
JSON identity is a separate 87-case check. No live provider, remote CI,
GitHub renderer, or new Python 3.12/3.13 matrix run was performed.

## Artifact boundary

All 600 original full-page PNGs were captured, hashed and independently
recounted. The compact committed evidence includes 24 selected original PNGs (12 actual/control pairs):
claim-below n=2 (residual), claim-below n=48 (old failed-line intrusion), and
last-rationale-below n=80 (old warning intrusion), each version and style.
`image_inventory.json` enumerates **all** images with hashes and identifies
which are bundled. Other full images remain in the local measurement work
area and can be regenerated with the commands above; their absence from the
compact package is not a missing measurement in the executed run.

The supplied six older screenshots remain historical source evidence. They
are not substituted for new screenshots. `historical/` preserves them and the
old prototype/README, plus independently recomputed historical counts.
