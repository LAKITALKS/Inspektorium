"""Verifier probe for the P3 row (read-only against diag_base)."""
import sys, os, re, json
from pathlib import Path
from collections import Counter

B = sys.argv[1]
sys.path.insert(0, B + "/src")
os.chdir(B)
import yaml
import agent_arena
from agent_arena.task_loader import load_task
from agent_arena.schemas import Task
from agent_arena.run_library import discover_cases, is_retired
from agent_arena.study_forensics_checker import _FINDING_PATTERNS

print("module:", agent_arena.__file__)
LABELS = {"solid", "overclaim", "mechanism_vs_evidence", "correlation_vs_causation"}
files = sorted(Path("tasks/study_forensics").glob("*.yaml"))
known = set(Task.model_fields)
rows = []
extra_keys = Counter(); extra_files = {}
for f in files:
    raw = yaml.safe_load(open(f))
    t = load_task(f)
    unk = sorted(set(raw) - known)
    if unk:
        extra_files[f.name] = unk
        extra_keys.update(unk)
    rows.append((f, raw, t))
print("files", len(files), "unique ids", len({t.id for _, _, t in rows}))
print("labels all", dict(Counter(t.gold_label for _, _, t in rows)))
print("files with dropped keys:", len(extra_files), "keys:", dict(extra_keys))
for k, v in extra_files.items():
    print("   ", k, v)
mism = [(t.id, t.expected_answer, t.gold_label, t.task_family) for _, _, t in rows
        if not (t.expected_answer == t.gold_label == t.task_family)]
print("expected_answer==gold_label==task_family mismatches:", mism)

act = discover_cases()
allc = discover_cases(include_retired=True)
print("active", len(act), "all", len(allc), "retired", [t.id for _, t in allc if is_retired(t)])
print("active labels", dict(Counter(t.gold_label for _, t in act)))

# P3 range counts
p3 = [t for _, _, t in rows if re.match(r"study-forensics-0(4[3-9]|5\d|6[0-3])$", t.id)]
print("P3 cases", len(p3), "labels", dict(Counter(t.gold_label for t in p3)),
      "difficulty", dict(Counter(t.difficulty.value for t in p3)),
      "origins", dict(Counter(t.origin for t in p3)))
print("origins all", dict(Counter(t.origin for _, _, t in rows)))
print("origins active", dict(Counter(t.origin for _, t in act)))

# Intake checklist (docs/case_intake_policy.md items 4-7) over active cases
allowed_origin = {"curated", "real_world_intake", "demo_derived", "synthetic", "curated_showcase"}
fails = Counter(); ex = {}
for _, t in act:
    checks = {
        "origin_not_in_policy_list": t.origin not in allowed_origin,
        "no_gold_justification": not (t.gold_justification or "").strip(),
        "no_gold_alternative_reading": not (t.gold_alternative_reading or "").strip(),
        "no_expected_findings": not t.expected_findings,
    }
    for k, v in checks.items():
        if v:
            fails[k] += 1; ex.setdefault(k, []).append(t.id)
print("intake checklist failures among active:", dict(fails))
for k, v in ex.items():
    print("   ", k, v[:6], "..." if len(v) > 6 else "")

# expected_findings vocabulary vs detector
detectable = set(_FINDING_PATTERNS)
print("detectable finding types:", sorted(detectable))
undetect = Counter(); per_case = {}
for _, t in act:
    for ef in t.expected_findings:
        if ef.finding not in detectable:
            undetect[ef.finding] += 1
            per_case.setdefault(t.id, []).append(ef.finding)
print("active cases with undetectable expected_findings:", len(per_case), dict(undetect))
for k, v in list(per_case.items())[:50]:
    print("   ", k, v)

# gold_evidence_spans verbatim check
n = 0; nonverb = []; ws_only = []
norm = lambda s: re.sub(r"\s+", " ", s).strip()
for _, t in act:
    for s in t.gold_evidence_spans:
        n += 1
        if s.span in t.prompt:
            continue
        if norm(s.span) in norm(t.prompt):
            ws_only.append(t.id)
        else:
            nonverb.append((t.id, s.span[:60]))
print("active spans", n, "non-verbatim", len(nonverb), "whitespace-only", len(ws_only))
n_all = sum(len(t.gold_evidence_spans) for _, _, t in rows)
print("all-50 spans", n_all)

# context label-token analysis: strict verdict statements vs incidental words
pat = {"solid": r"\bsolid\b", "overclaim": r"\boverclaim", "mechanism_vs_evidence": r"mechanism_vs_evidence|mechanism vs\.? evidence",
       "correlation_vs_causation": r"correlation_vs_causation|correlation vs\.? causation"}
any_tok = []; own = []
for _, t in act:
    ctx = t.context or ""
    hits = [l for l, p in pat.items() if re.search(p, ctx, re.I)]
    if hits:
        any_tok.append((t.id, t.gold_label, hits))
    if re.search(pat[t.gold_label], ctx, re.I):
        own.append(t.id)
print("active with any label token in context:", len(any_tok), "own gold token:", len(own))
for x in any_tok:
    ctx = [t for _, t in act if t.id == x[0]][0].context
    m = re.search("|".join(pat[h] for h in x[2]), ctx, re.I)
    print("   ", x, "|", repr(ctx[max(0, m.start() - 70): m.end() + 40]))
