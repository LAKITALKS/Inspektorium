#!/bin/bash
# protected.sh <outfile>: snapshot of protected state
R=__LOCAL_HOME__/Documents/Projects/agent-arena
cd $R
{
date -u +%Y-%m-%dT%H:%M:%SZ
git rev-parse HEAD
shasum -a 256 analysis/c25_p9_20261011/live_retest/ledger.json
shasum -a 256 analysis/live_smoke_20261011/repair_r1/successor_claim.json
echo "live_retest_file_count $(find analysis/c25_p9_20261011/live_retest -type f | wc -l | tr -d ' ')"
echo "tracked_changes $(git status --porcelain --untracked-files=no | wc -l | tr -d ' ')"
echo "tracked_changes_list $(git status --porcelain --untracked-files=no | awk '{print $2}' | tr '\n' ' ')"
echo "git_diff_HEAD_sha256 $(git diff HEAD | shasum -a 256 | cut -d' ' -f1)"
echo "staged_changes $(git diff --cached --name-only | wc -l | tr -d ' ')"
} > "$1"
