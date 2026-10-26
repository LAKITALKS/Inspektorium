"""Inspect copies of the 9 live_retest revisions with whatever agent_arena is first on sys.path (PYTHONPATH selects
the 558e920 worktree or, unset, the v1 editable install). Reports bound vs installed code identity. Read-only."""
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netguard  # noqa: E402,F401
import agent_arena  # noqa: E402
from agent_arena.phase10_bundle import inspect_bundle  # noqa: E402
from agent_arena.phase10_pipeline import code_identity  # noqa: E402

root = Path(sys.argv[1])
ident = code_identity()
out = {"agent_arena_version": agent_arena.__version__,
       "agent_arena_path": os.path.dirname(agent_arena.__file__).replace(str(root.parent), "<scratch>"),
       "installed_code_fingerprint": ident["code_fingerprint"],
       "installed_verified_source_commit": ident.get("verified_source_commit"), "revisions": []}
for rec in sorted(root.glob("**/record.json")):
    b = rec.parent
    r = json.loads(rec.read_text())
    v = inspect_bundle(b)
    out["revisions"].append({"bundle": str(b.relative_to(root)), "recorded_status": r["status"],
                             "bound_code_fingerprint": r["provenance"]["code"]["code_fingerprint"],
                             "bound_verified_source_commit": r["provenance"]["code"].get("verified_source_commit"),
                             "code_identity_matches_installed": r["provenance"]["code"]["code_fingerprint"] == ident["code_fingerprint"],
                             "inspect": {"valid": v.valid, "status": v.status, "errors": [e[:300] for e in v.errors]},
                             "valid_with_recorded_status": v.valid and v.status == r["status"]})
out["all_valid_with_recorded_status"] = all(x["valid_with_recorded_status"] for x in out["revisions"])
out["none_valid"] = not any(x["inspect"]["valid"] for x in out["revisions"])
print(json.dumps(out, indent=1))
