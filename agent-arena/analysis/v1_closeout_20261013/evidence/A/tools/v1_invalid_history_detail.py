"""Read-only: under the v1 code, show the reconstructed Phase-9 review of one pre-v1 bundle copy (history_validation,
reasons, uncertainty) to explain the v1 open cause 'review history invalid: ...'. Usage: v1_invalid_history_detail.py BUNDLE"""
import json, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netguard  # noqa: E402,F401
from agent_arena.phase10_bundle import _load  # noqa: E402
from agent_arena.phase10_pipeline import reconstruct, _review_cause  # noqa: E402
from agent_arena.schemas import RunRecord  # noqa: E402
audit, decision, manifest = _load(sys.argv[1])
review, selected, assessment, forensic = reconstruct(RunRecord.model_validate(audit.run_record))
stored = audit.run_record["metadata"]["phase9"]
print(json.dumps({"bundle": sys.argv[1].split("/hist-copies/")[-1],
                  "stored_contract_version": stored.get("contract_version"),
                  "stored_history_validation": stored.get("history_validation"),
                  "v1_reconstructed": {k: review.get(k) for k in ("contract_version", "history_validation", "route",
                                                                  "execution_status", "reasons", "uncertainty")},
                  "v1_open_cause": _review_cause(review)}, indent=1, ensure_ascii=False))
