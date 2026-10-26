"""Verifier: reproduce the documented --fake CLI run (cwd must be the checkout)."""
import json
import os
import sys

B, S = sys.argv[1], sys.argv[2]
sys.path.insert(0, B + "/src")
from agent_arena import run_library as rl  # noqa: E402
import agent_arena  # noqa: E402

print("agent_arena imported from:", os.path.dirname(agent_arena.__file__))
out = S + "/fake_run"
rc = rl.main(["--limit", "3", "--runs-per-case", "2", "--fake", "--out-dir", out])
print("rc", rc)
print("files:", sorted(os.listdir(out)), "results.jsonl bytes:", os.path.getsize(out + "/results.jsonl"))
m = json.load(open(out + "/manifest.json"))
print("manifest keys:", sorted(m))
recs = [json.loads(line) for line in open(out + "/results.jsonl")]
print("record keys:", sorted(recs[0]))
doc_fields = ("library_run_id, case_id, case_file, gold_label, run_index, provider, model, label, "
              "label_correct, score, confidence, parse_ok, finish_reason, truncation_suspected, error, "
              "error_type, latency_ms, usage, timestamp, raw_result_ref").split(", ")
print("record keys not in P4 doc list:", sorted(set(recs[0]) - set(doc_fields)))
print("doc fields missing from record:", sorted(set(doc_fields) - set(recs[0])))
for r in recs:
    print(r["case_id"], r["run_index"], r["label"], r["label_correct"], r["score"], r["parse_ok"],
          r["finish_reason"], r["truncation_suspected"], (r["phase8"] or {}).get("technical_status"),
          "raw_output_len", len(r["raw_output"] or ""))
s = json.load(open(out + "/summary.json"))
for c in s["case_stability"]:
    print(c["case_id"], c["flags"], "range", c["score_range"], "elig", c["n_confidence_eligible"])
