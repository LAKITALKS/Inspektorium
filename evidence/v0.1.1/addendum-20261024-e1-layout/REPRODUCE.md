# Reproduce the E1 paragraph follow-up

Use the unchanged 87-case catalog at `../addendum-20261024/catalog.json` and
its pinned measurement requirements/font manifest. The earlier
[reproduction guide](../addendum-20261024/REPRODUCE.md) describes dependency,
font and Chromium installation as a separate download phase. This follow-up
reused those installations; its product installs used the local wheelhouse
with `PIP_NO_INDEX=1`, without new downloads. Paths below are placeholders.
Do not reuse existing output/venv targets: E3 deliberately refuses them.

```sh
REPO=/path/to/Inspektorium-v0.1.1
CHECK_WORK=/new/scratch/directory
OLD_WORK=/path/to/previous/local/measurement/work
mkdir "$CHECK_WORK"
cd "$CHECK_WORK"
T="$REPO/evidence/v0.1.1/tools"
A="$REPO/evidence/v0.1.1/addendum-20261024-e1-layout"
C="$REPO/evidence/v0.1.1/addendum-20261024/catalog.json"
python3.11 "$T/setup_env.py" build-wheel --repo "$REPO" \
 --commit 5ace2797e4a9075ca53ccd780be616719923c288 --out layout-build \
 --build-python "$OLD_WORK/build-env/bin/python" --setup-log setup.jsonl
PIP_NO_INDEX=1 PIP_FIND_LINKS="$OLD_WORK/wheelhouse" \
 python3.11 "$T/setup_env.py" product-venv --venv layout-env \
 --wheel layout-build/wheels/inspektorium-0.1.1-py3-none-any.whl \
 --setup-log setup.jsonl
export PYTHONDONTWRITEBYTECODE=1
export PLAYWRIGHT_BROWSERS_PATH="$OLD_WORK/browsers"
EVIDENCE_NETGUARD_LOG="$CHECK_WORK/canary-netguard.jsonl" \
 "$OLD_WORK/dev/bin/python" "$T/canary.py" --venv layout-env \
 --venv "$OLD_WORK/dev" --work canary-work --results canary-results
EVIDENCE_NETGUARD_LOG="$CHECK_WORK/layout-final-netguard.jsonl" \
 "$OLD_WORK/dev/bin/python" "$A/tools/check_addendum.py" --catalog "$C" \
 --venv layout-env --fonts "$OLD_WORK/fonts-2.015" \
 --work layout-final-cases --out layout-final-results \
 --commit 5ace2797e4a9075ca53ccd780be616719923c288 \
 --provenance layout-build/build_provenance.json
```

Use an environment without provider credentials. The recorded wrapper removes
names containing API_KEY, ANTHROPIC, OPENAI, TOKEN or SECRET; its source is
included under `repro-scripts/`. All measured Python environments have the
existing `.pth` socket guard, verified by canary, and browser request routing
is blocked. Native/OS-wide network isolation is not claimed.

The script's exit 0 means measurement completed, not acceptance. Inspect
`summary.json`: 87 cases, 348 renderer outputs, 75 measured cases per style,
zero INVALID, zero visual hits, zero text failures and zero links are required.
The compare function checks a fixed three-finding inventory for this catalog.
It is not a generic report validator. `Answer span` and the other host-control
labels must appear exactly once per finding in both DOMs and never be payload.

The old saved runs need not be regenerated. `compare_evidence.py.txt` replays
all old PNG comparisons with the new function and compares every new/old DOM
row's text and payload membership, plus all 87 raw JSON reports. Supply
`--repo "$REPO" --old-work "$OLD_WORK" --work "$CHECK_WORK"`. Scripts with
`.py.txt` suffix are the exact executed source attachments; Python can execute
them directly. The independent reviewer scripts and raw results are also
included. All source images are required for the complete pixel recount;
the compact ZIP deliberately bundles only the explicitly inventoried subset.

After the separate review, run the existing mandatory checks from the checkout
using its installed development environment:

```sh
ruff check .
mypy src
pytest --cov=inspektorium --cov-report=term-missing --cov-fail-under=80
```

That environment had already been installed editable with `.[dev]` during the
previous closeout; its pointer still imports this checkout. The follow-up does
not alter dependencies. For a new environment, install `.[dev]` in the setup
phase before the offline checks. For the clean installation proof, use a new
`final-clean-env` with the same measured wheel, PIP_NO_INDEX and local wheelhouse;
run `verify_clean.py.txt --repo ... --venv ... --out <new-output>` to verify the
site-packages import, all package source bytes, `pip check`, and all 10 example
outputs. Do not count the prior clean environment as the fresh final proof.

Original commands, timestamps, versions, exits and sanitized full logs are in
`results/`; `<WORK>`, `<OLD_WORK>` and `<REPO>` replace local paths. Historical
setup logger labels are retained, including its generic word "download";
the actual command/environment and pip output identify the offline installations.
