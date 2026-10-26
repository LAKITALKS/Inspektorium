# One instrument: Inspektorium — 2026-10-26

The maintainer clarified that **Inspektorium is one measurement/review
instrument, formerly named Agent Arena**. The first publication placed an
existing small reference checker beside the complete audit implementation.
This follow-up provides one official public audit entry and explains the
reference checker's separate, narrower role.

## Implemented change

Install both local distributions into one fresh environment:

```sh
python -m pip install . ./agent-arena
inspektorium audit --help
```

The root distribution is now **0.2.0**. Its new entry directly invokes
`agent_arena.phase10_cli.audit`, with the same arguments and controlled exit
statuses. The existing `validate`, `run`, `inspect`, `review` and `release`
operations use the existing implementation. There is no second audit
evaluator and no fallback to the smaller reference checker.

The audit distribution remains **agent-arena 1.0.1**. All **74** audit-runtime
Python files, its package metadata and its tests are unchanged from
`94eb4fc8b26c22da6a2cebdd01e5a7799750104d`. The former `agent-arena audit`
command remains compatible. Its names inside historical records and reports
retain their original meaning and bytes.

`inspektorium inspect` remains the smaller single-answer reference tool.
Its underlying core, provider and renderer files are unchanged. Its guards
are not automatically applied to the audit workflow. No new scientific
semantics, scores, authorization or efficacy claim is introduced.

See [architecture and usage](../../docs/ONE_INSTRUMENT.md),
[P19](../../CLAIMS.md#unified-public-entry-020-source), and
[exact module/input hashes](product-identity.json).

## Executed local checks

| Check | Actual result |
| --- | --- |
| Root suite on Python 3.12.14 | 1,363 passed, 0 failed, 0 skipped; 97.90% overall coverage with branch measurement |
| Root strict Mypy | Passed, 20 source files |
| Root Ruff | Passed on the active source, tests and tools; frozen closeout evidence is excluded |
| Root-only wheel installation outside source | Reference help works; missing audit backend is explicit exit 2, without fallback |
| Joint regular-wheel installation outside source | Both packages imported from the fresh environment; all 20 root and 74 audit module hashes match source |
| Installed public workflow | 40 checks passed; all five operations, positive/negative/UNKNOWN cases, compatibility in both directions and tampered-report rejection |
| Reference outputs through installed public entry | All 10 JSON/Markdown outputs match the existing expected bytes |
| Installed guard countercheck | Five non-loopback operations refused; clean local loopback connection succeeds |
| Actual guarded installed-workflow commands | 40 guard activations; 0 refused operations |

Measured records: [installed workflow](results/installed-wheel.json),
[guard counterchecks](results/guard-canary.jsonl),
[evaluation socket events](results/offline-network.jsonl),
[root-only installation](results/missing-backend.json), and
[local acceptance summary](results/local-validation.json).

The complete root suite includes the 8 new entry-boundary tests. These are
regressions, not a new scientific study. The full unchanged audit suite was
not repeated locally; the existing complete audit CI remains required.

The first installed verification attempt stopped at the guard countercheck
because the strict execution sandbox disallowed socket creation, including
the positive local-loopback control. It ran **zero functional checks** and is
preserved as [failed](results/sandbox-canary-failed.json). The subsequent
execution allowed local sockets while retaining the unchanged Python guard;
all counterchecks and workflow checks then passed. No failed attempt is
reported as passed.

## Reproduce and CI

Build both wheels, install them into a fresh virtual environment outside the
checkout, install the existing Python socket guard using
`evidence/v0.1.1/tools/setup_env.py guard --venv ENVIRONMENT`, then run:

```sh
ENVIRONMENT/bin/python scripts/verify_instrument.py \
  --repo CHECKOUT --output NEW_DIRECTORY_OUTSIDE_CHECKOUT
```

The verifier installs nothing. The named output directory must not exist.
It requires working local sockets for the guard's positive countercheck.
Public dependency downloads belong to setup, before offline evaluation.
The guard measures Python socket hooks, not native or operating-system-wide
traffic. The separate recorded invalid-live-authorization check is rejected
before any provider call.

GitHub CI keeps the existing core and audit jobs on Python 3.11 and 3.12 and
adds two installed-instrument jobs on those versions. Each added job builds
regular wheels, checks a missing-backend installation, completes joint
installation and executes this verifier. It preserves its result and both
network logs. Current CI/release status is observed separately in GitHub;
this local record does not pre-claim a successful future run.

## Provenance and prior publication completion

The existing audit bundle code fingerprint still covers `agent_arena`
module bytes only. It does not automatically authenticate the new public
launcher. This record binds the launcher version and its module/input
hashes separately, without modifying the existing bundle schemas.

The interrupted first publication's public download check has also been
completed as a **new independent execution**. Its
[closeout report](../2026-10-26-publication-closeout/PUBLICATION-CLOSEOUT.md)
and preserved logs bind the earlier release commit/tags; they are not a claim
that the unavailable earlier Mac run completed. Existing release tags,
archives, import indexes and historical results remain unchanged.

This source update does not itself assert a new GitHub Release or additional
release attachments. Technical artifact readiness, published software and
scientific validity remain separate decisions. The scientific efficacy gate
remains unmet. Lazaros Varvatis is the sole human software/project author;
the PolyForm Noncommercial 1.0.0 license is unchanged.
