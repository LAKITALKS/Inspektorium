# Role C public replay fixture correction — 2026-10-26

Target: the three `test_phase10_live.py` failures in the orchestrator's dd739 full-suite log (2554 passed, 6 failed overall). This role addressed only the three assigned replay/pin test failures. Product source, runtime pins, live-authority rules, public authorization files and private originals are unchanged.

## Test-only patch

`public-replay-tests.patch` updates two files:

- `agent-arena/tests/test_phase10_live.py`
- `agent-arena/tests/fixtures/phase10/public_archive_bindings.json`

The fixture contains four exact entries extracted from the current `publication/2026-10-26/import-index.json`: original/public SHA-256, origin, action and reasons for the two earlier authorization files and their closed ledgers. A packaged subset avoids introducing an unavailable monorepo-parent file dependency when tests run from the Arena sdist. All four rows were separately compared to the current import index and matched exactly.

The historical-pin test now asserts that production pins match original source hashes, ledger bindings still refer to the original authorization hash, actual public derivative bytes match their own public hash, ledgers remain revoked with zero executable remainder, and authorization derivatives remain INERT. Actual copies of both public archives are rejected in both live and replay modes without any mutation or new file. The test's original fresh-budget, pinned-ID reuse, successor-history, closed-ledger, and re-pin counterexamples remain intact.

The two replay behavior tests generate fresh synthetic primary captures with the existing `Transport`/httpx.MockTransport, `_authorize`, `LiveAuditProvider`, `close_for_successor` and `_pin` helpers. Only two primary slots are recorded; no review slot executes. The fixtures are closed, pinned, copied unchanged and replayed. They preserve checks for READY_FOR_RELEASE versus REVIEW_REQUIRED, mandatory review denied with the correct cause, exact replay ledger hash, evidence immutability, rejected tampered pinned ledger, and CLI review state written only beside output. They make no claim of replaying a public redacted historical archive. No private path or historical ACTIVE authorization was reconstructed.

## Own executions

- Selected three corrected tests against the orchestrator's installed 1.0.1 wheel: **3 passed in 1.50s**, `targeted-r2.log` and `command-r2.json`.
- Python socket guard (connect, connect_ex, create_connection, getaddrinfo): **0 for all four**, `targeted-guard-r2.json`. Synthetic HTTP requests terminate in MockTransport. Scope is the wrapped process, not an OS-wide monitor.
- Ruff using Arena's pyproject configuration on the changed test module: **passed**.
- `git apply --check` against the current integration checkout: **passed**.
- No complete suite rerun by this role; root owns final acceptance.

The first scratch attempt passed two tests and failed the pin test because the reduced scratch tree lacked the unchanged `tests.test_phase8_9_conflict` helper. Copying the three required unchanged test helper files into scratch resolved that environment omission; no additional product or proposed test logic change followed. `targeted.log` preserves that failed attempt.

## Coverage and application

No test removed or skipped; the original three test names remain. No production code changes or version increment required beyond the already-declared 1.0.1. Apply the patch, include both explicit files, refresh their import-index entries, and run the root's planned final suite. If the four public archives are later intentionally redacted again, regenerate the four-row fixture from their updated import-index entries; never update production pins to derivative hashes.
