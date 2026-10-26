"""Diagnose (read-only) why a bundle does not verify under the installed code: bound vs installed code identity and
the controls whose recomputed outcome differs from decision.json. Usage: why_not_verifiable.py BUNDLE..."""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netguard  # noqa: E402,F401
import agent_arena  # noqa: E402
from importlib.metadata import version  # noqa: E402
from agent_arena.phase10_bundle import _load  # noqa: E402
from agent_arena.phase10_pipeline import code_identity, digest, evaluate, source_claim_valid  # noqa: E402
from agent_arena.schemas import RunRecord  # noqa: E402

ci = code_identity()
out = {"agent_arena_version": agent_arena.__version__, "distribution_version": version("agent-arena"),
       "installed_code_fingerprint": ci["code_fingerprint"], "bundles": []}
for b in sys.argv[1:]:
    audit, decision, manifest = _load(b)
    bound = audit.provenance
    status, controls, *_ = evaluate(RunRecord.model_validate(audit.run_record), digest(audit.model_dump(mode="json")), bound)
    stored = {c.control_id: (c.outcome, c.version) for c in decision.controls}
    changed_modules = sorted(k for k in set(bound["code"]["module_hashes"]) | set(ci["module_hashes"])
                             if bound["code"]["module_hashes"].get(k) != ci["module_hashes"].get(k))
    out["bundles"].append({
        "bundle": b.split("/hist-copies/")[-1], "recorded_status": audit.status, "recomputed_status": status,
        "bound_package_version": bound.get("package_version"),
        "bound_code_fingerprint": bound["code"]["code_fingerprint"],
        "code_identity_matches_installed": bound["code"]["code_fingerprint"] == ci["code_fingerprint"],
        "modules_differing_from_bound": changed_modules,
        "source_claim_valid_here": source_claim_valid(bound["code"]),
        "controls_changed_vs_decision_json": {c.control_id: {"recorded": stored.get(c.control_id), "now": [c.outcome, c.version],
                                                             "reason_now": c.reason[:240]}
                                              for c in controls if stored.get(c.control_id) != (c.outcome, c.version)}})
print(json.dumps(out, indent=1))
