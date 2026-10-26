#!/bin/bash
# Record the protected state (read-only): ledger/claim sha256, live_retest file count + tree hash, git porcelain hash, HEAD.
cd __LOCAL_HOME__/Documents/Projects/agent-arena
date -u +%Y-%m-%dT%H:%M:%SZ
shasum -a 256 analysis/c25_p9_20261011/live_retest/ledger.json analysis/live_smoke_20261011/repair_r1/successor_claim.json
echo "live_retest_file_count $(find analysis/c25_p9_20261011/live_retest -type f | wc -l | tr -d ' ')"
echo "live_retest_tree_sha $(cd analysis/c25_p9_20261011/live_retest && find . -type f | sort | xargs shasum -a 256 | shasum -a 256 | cut -d" " -f1)"
echo "git_status_porcelain_sha $(git status --porcelain | shasum -a 256 | cut -d' ' -f1)"
echo "git_staged_files $(git diff --cached --name-only | wc -l | tr -d ' ')"
echo "HEAD $(git rev-parse HEAD)"
