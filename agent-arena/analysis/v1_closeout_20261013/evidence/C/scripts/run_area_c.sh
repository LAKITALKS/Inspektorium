#!/bin/bash
# Area C evidence driver. No provider/network: env -u keys; guarded runs via guard_cli.py.
set -u
R=__LOCAL_HOME__/Documents/Projects/agent-arena
S=__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-C
O=$S/out; C=$S/counts
rm -rf $O $C $S/work; mkdir -p $O $C $S/work
export COLUMNS=100
ENV=(env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 COLUMNS=100)
BIN=$R/.venv/bin/agent-arena
PY=$R/.venv/bin/python
G=("$PY" -I -B $S/guard_cli.py)
CMDLOG=$O/commands.log; : > $CMDLOG

cap() { # cap <outname> <cwd> <cmd...>
  local name=$1 cwd=$2; shift 2
  local f=$O/$name.txt
  { echo "\$ (cd $cwd && ${ENV[*]} $*)"; echo "--- output (stdout+stderr) ---"; } > $f
  (cd "$cwd" && "${ENV[@]}" "$@") >> $f 2>&1
  local rc=$?
  echo "--- exit_code: $rc" >> $f
  printf '%s\t%s\t%s\n' "$name" "$rc" "(cd $cwd && $*)" >> $CMDLOG
  return 0
}

echo "# candidate HEAD $(git -C $R rev-parse HEAD)" >> $CMDLOG
# 0. Guard self-test (canary): every patched path must refuse and count
CANCWD=$S/work/canary_cwd; mkdir -p $CANCWD
cap guard_canary $CANCWD "${G[@]}" $C/canary.json canary

HELPCWD=$S/work/help_cwd; mkdir -p $HELPCWD
# 1. Help texts via the canonical console script ...
cap help_root            $HELPCWD $BIN --help
cap help_audit           $HELPCWD $BIN audit --help
for sc in validate run inspect review release; do cap help_audit_$sc $HELPCWD $BIN audit $sc --help; done
cap help_run             $HELPCWD $BIN run --help
cap help_official_release $HELPCWD $BIN official-release --help
cap help_forensic_report $HELPCWD $BIN forensic-report --help
cap help_run_library     $HELPCWD $PY -B -m agent_arena.run_library --help
cap version              $HELPCWD $BIN --version
# ... and the same help texts through the guard wrapper (counts recorded)
cap guarded_help_root    $HELPCWD "${G[@]}" $C/help_root.json cli --help
cap guarded_help_run_library $HELPCWD "${G[@]}" $C/help_run_library.json run_library --help

# 2. Rejected historical commands from empty cwds, guarded
W1=$S/work/cwd_run_anthropic; mkdir -p $W1
cap run_rejected_anthropic $W1 "${G[@]}" $C/run_anthropic.json cli run --task $R/examples/phase10/positive-task.json --agents anthropic
W2=$S/work/cwd_run_yaml; mkdir -p $W2
cap run_rejected_yaml $W2 "${G[@]}" $C/run_yaml.json cli run --task $R/examples/phase10/positive-task.json --agents $R/agents/claude_sonnet.yaml
W3=$S/work/cwd_official; mkdir -p $W3
printf '%s\n' '{"note": "SYNTHETIC TEST FIXTURE — not an empirical model response; dummy official-release input"}' > $S/work/dummy_release_input.json
cap official_release_rejected $W3 "${G[@]}" $C/official_release.json cli official-release --input $S/work/dummy_release_input.json --output-root $S/work/official_out/out --repo-root $R

# 3. Supported v1 path, guarded, offline
SP=$S/work/supported; mkdir -p $SP
cap audit_validate $SP "${G[@]}" $C/audit_validate.json cli audit validate --task $R/examples/phase10/positive-task.json
cap audit_run_offline $SP "${G[@]}" $C/audit_run_offline.json cli audit run --offline --task $R/examples/phase10/positive-task.json --recording $R/examples/phase10/positive-recording.json --output-root $SP/runs
BUNDLE=$(sed -n 's/^  "path": "\(.*\)",$/\1/p' $O/audit_run_offline.txt)
echo "bundle=$BUNDLE" >> $CMDLOG
cap audit_inspect_candidate $SP "${G[@]}" $C/audit_inspect_candidate.json cli audit inspect --bundle "$BUNDLE"
cap audit_release $SP "${G[@]}" $C/audit_release.json cli audit release --bundle "$BUNDLE" --output-root $SP/release --reviewer area-c-evidence --reason "v1 closeout area C supported-path demonstration (offline recorded example)"
REL=$(sed -n 's/^  "path": "\(.*\)",$/\1/p' $O/audit_release.txt)
echo "release=$REL" >> $CMDLOG
cap audit_inspect_release $SP "${G[@]}" $C/audit_inspect_release.json cli audit inspect --bundle "$REL"

# 4. Post-conditions: rejected commands wrote nothing
{
  echo "# Post-condition listing (find <dir> -mindepth 1); expected: no entries for the three rejected-command cwds and no official_out"
  for d in $S/work/cwd_run_anthropic $S/work/cwd_run_yaml $S/work/cwd_official; do
    echo "## $d"; find $d -mindepth 1; echo "entries: $(find $d -mindepth 1 | wc -l | tr -d ' ')"
  done
  echo "## $S/work/official_out exists: $( [ -e $S/work/official_out ] && echo yes || echo no )"
  echo "## repo runs/ and reports/ (pre-existing, informational): newest mtime entries"
  for d in $R/runs $R/reports; do [ -d $d ] && echo "$d: $(find $d -newer $S/run_area_c.sh -type f | wc -l | tr -d ' ') files newer than driver script" || echo "$d: absent"; done
  echo "## supported path tree (relative)"
  (cd $SP && find . -type f | sort)
} > $O/postconditions.txt 2>&1

# 5. Tests (network-guard plugin; no cacheprovider; basetemp in scratch)
for t in test_release_boundary test_v1_entry_point; do
  rm -rf $S/work/pt_$t
  f=$O/pytest_$t.txt
  echo "\$ (cd $R && ${ENV[*]} PYTHONPATH=$S/plugins AREAC_NETGUARD_OUT=$C/pytest_$t.json $PY -B -m pytest -p areac_netguard -p no:cacheprovider --basetemp $S/work/pt_$t -q -rA tests/$t.py)" > $f
  (cd $R && "${ENV[@]}" PYTHONPATH=$S/plugins AREAC_NETGUARD_OUT=$C/pytest_$t.json $PY -B -m pytest -p areac_netguard -p no:cacheprovider --basetemp $S/work/pt_$t -q -rA tests/$t.py) >> $f 2>&1
  rc=$?; echo "--- exit_code: $rc" >> $f
  printf '%s\t%s\t%s\n' "pytest_$t" "$rc" "pytest tests/$t.py" >> $CMDLOG
done
