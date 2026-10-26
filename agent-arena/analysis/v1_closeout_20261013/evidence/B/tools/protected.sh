#!/bin/sh
# Usage: protected.sh <out.json>  -- records protected hashes and repository state (read-only).
R=__LOCAL_HOME__/Documents/Projects/agent-arena
cd "$R" || exit 1
L=$(shasum -a 256 analysis/c25_p9_20261011/live_retest/ledger.json | cut -d' ' -f1)
C=$(shasum -a 256 analysis/live_smoke_20261011/repair_r1/successor_claim.json | cut -d' ' -f1)
N=$(find analysis/c25_p9_20261011/live_retest -type f | wc -l | tr -d ' ')
H=$(git rev-parse HEAD)
T=$(git status --porcelain --untracked-files=no | wc -l | tr -d ' ')
TL=$(git status --porcelain --untracked-files=no | tr '\n' ';')
D=$(git diff HEAD | shasum -a 256 | cut -d' ' -f1)
SRC=$(git diff HEAD --stat -- src tests pyproject.toml | wc -l | tr -d ' ')
I=$(git diff --cached --name-only | wc -l | tr -d ' ')
cat > "$1" <<J
{"analysis/c25_p9_20261011/live_retest/ledger.json": "$L",
 "analysis/live_smoke_20261011/repair_r1/successor_claim.json": "$C",
 "live_retest_file_count": $N,
 "git_head": "$H",
 "tracked_modified_paths": $T,
 "tracked_modified_list": "$TL",
 "git_diff_HEAD_sha256": "$D",
 "src_tests_pyproject_diff_lines": $SRC,
 "staged_paths": $I,
 "recorded_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
J
cat "$1"
