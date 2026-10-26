# Agent Arena public technical research release — 2026-10-26

Version **1.0.1**, public research prerelease, derived from technical 1.0.0
commit `9de4b76953aed778c42df994535cb29a4e0f9f5c` (tested product
`5560e950af20cee8c35fb2c8e2bfb38807043fab`). This is not byte-identical 1.0.0:
one runtime Git lookup in `condition_contract.py` now authenticates the
component-relative path (`HEAD:./...`) inside this monorepo; version metadata
is updated. Six positive/negative tests cover standalone/nested component paths,
a parent decoy, changed tracked bytes and untracked bytes. Scientific semantics,
live permissions and the historical source-root preflight guard are unchanged.

The standalone reproduction driver now understands the component subdirectory
and measures Python socket events in its installed environments, after explicit
guard counterchecks. Public dependency installation is a separate setup step.
The old hardcoded zero-call field has been removed. The guard covers Python
socket operations, not native or OS-wide network traffic. It tests five refused
operations plus a successful loopback connection before evaluations.

The new capture-extraction tool creates a **new recorded-offline analysis**
from a matching complete saved primary response. It verifies task binding and
response-text consistency, preserves the response text exactly, and writes an
explicit derivative manifest. Thirteen controls cover valid and invalid inputs
and refusal to overwrite existing output. It does not authenticate a provider,
recreate historical review history, or validate an old bundle's Git binding.

## Install and run offline

From the repository root, create a fresh environment and install
`python -m pip install ./agent-arena`. Or install the release wheel outside the
checkout. Then use the files under `agent-arena/examples/phase10/`:

```sh
agent-arena audit validate --task examples/phase10/positive-task.json
agent-arena audit run --offline --task examples/phase10/positive-task.json \
  --recording examples/phase10/positive-recording.json --output-root /new/output
agent-arena audit inspect --bundle /path/returned/by/run
```

Commands above assume the working directory is `agent-arena/`; installed imports
come from site-packages. The negative example can also reach READY_FOR_RELEASE:
that means the report is technically ready, including its negative finding.
The unknown example returns exit 2 / REVIEW_REQUIRED and release stays blocked.
Human-review requirements cannot be silently resolved by an absent reviewer.
See the existing [operational guide](README.md) for explicit review/release steps.
`agent-arena run` and `official-release` remain disabled. Old Python research
APIs and launchers can call providers and are not authorized by this release.

## Provenance and historical replay

[Import index](../publication/2026-10-26/import-index.json),
[phase inventory](../publication/2026-10-26/arena-inventory.json), and
[redaction manifest](../publication/2026-10-26/import-derivation.json) map every
selected input to its public file and hash. Private Git history is not imported.
Historical commit identifiers are provenance labels, not public Git links.
Six `historical-sources/` snapshots preserve the producing modules and package
metadata for important evidence. Those snapshots are historical, not the
installed package; original private Git objects are not supplied. Two superseded
pre-RC archive source variants were not recoverable, as the inventory records.

Three expired authorization files are explicitly INERT_PUBLIC_ARCHIVE. Local
paths and private account/billing fields are removed from separate derivatives.
Changed files and repacked archives have new hashes. Embedded historical
fingerprints still refer to originals; they are never presented as valid proofs
for redacted bytes. Native authorization-directory replay of these derivatives
is unavailable; the separately documented capture extraction path supports
transparent offline reanalysis. Original native replay was checked only against
private original-equivalent copies and is not counted as a public replay proof.

Older source-bound production preflights deliberately require a standalone
Git root. They are retained as closed historical controls, not enabled for a
new live run by the integration. The supported installed offline audit path
does not require Git. Original live evidence covers limited synthetic
construction cases and older code only; the final source has no new live test.

## Checks and scientific limits

The complete `tests/` suite includes frozen P8 and P9 acceptance cases. P10's
separate frozen acceptance driver is `python scripts/phase10_acceptance.py
--output /new/gates`. `python scripts/phase10_clean_reproduce.py --scratch
/new/scratch --output /new/results --full-suite` installs from a clean committed
clone and checks canonical operations, installed bytes and the full suite.
Both output paths must be new. Dependencies may be downloaded during setup;
provider credentials are removed, and measured evaluation phases are guarded.

The historical release lint boundary covers `phase10_*.py`, CLI, corresponding
tests and three operational scripts. This publication additionally checks the
changed condition-contract file, new tests and capture/guard scripts. Full
source Ruff has a disclosed historical baseline (368 findings), not a clean
result. Arena has no established strict type-check configuration; compilation
and tests do not replace static type checking. Core's strict Mypy is separate.
Both packages run their complete suites in GitHub CI on Python 3.11 and 3.12.
Fresh measured results are in the [publication record](../publication/2026-10-26/README.md).

Technical integrity is not scientific truth. Exact quotes can mislead; model/
host agreement is not independent corroboration. Closed Corpus examines only
supplied material. Offset, causal inference and review-coverage limits persist.
The scientific Final v1 efficacy gate is **NOT MET**. Historical counts and
negative results retain their original conditions; public source availability
is not an independent replication. No new provider call or budget reopening
is authorized. No global efficacy, safety or compliance claim follows.

## Rights

Lazaros Varvatis is the sole human project/software author. This own-code
publication applies the repository's unchanged PolyForm Noncommercial 1.0.0
license to Arena. It is source-available, not OSI open source. Cited source
excerpts retain attribution; third-party packages/fonts keep their own licenses
and are not relicensed. Dataset metadata derivatives disclose AI assistance.
See [third-party notices](../publication/2026-10-26/THIRD_PARTY.md).
