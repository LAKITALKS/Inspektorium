"""Critic-only: copy-only repairs (simulate_r1.repair) plus C12/C14 compliance scenarios."""
import copy, json, sys
from pathlib import Path
src = Path(__file__).with_name("simulate_r1.py").read_text().replace("\nmain()\n", "\n")
ns = {"__name__": "sim"}
sys_argv = list(sys.argv); sys.argv = sys_argv[:2]
exec(compile(src, "simulate_r1.py", "exec"), ns)
from agent_arena.output_contract import parse_structured_output
from agent_arena.phase8_pipeline import assess_forensic_payload
from agent_arena.phase8_semantics import CORE_DIMENSIONS, _unknown_value
from agent_arena.task_loader import load_task
RUN = ns["RUN"]
tasks = {load_task(f).id: load_task(f) for f in sorted((RUN / "tasks").glob("LS-0*.json"))}

def c12(fr):
    for p in fr["phase8"]["propositions"]:
        attrs = p["attributes"]
        dims = set(CORE_DIMENSIONS) | set(p.get("material_dimensions", [])) | {k for k, v in attrs.items() if v is not None}
        for d in dims:
            if d != "relation" and _unknown_value(attrs.get(d)) and not p["not_applicable"].get(d, "").strip():
                attrs[d] = None
                p["not_applicable"][d] = "not stated in the claim"
    return fr

def c14(fr):
    descs = {d["evidence_id"]: d for d in fr["phase8"]["evidence_descriptions"]}
    for p in fr["phase8"]["propositions"]:
        for b in p.get("evidence_bindings", []):
            d = descs.get(b["evidence_id"])
            if not d:
                continue
            for k, v in p["attributes"].items():
                if k in ("relation", "certainty") or v is None:
                    continue
                if _unknown_value(d["attributes"].get(k)):
                    d["attributes"][k] = v
    return fr

def sync_transformations(fr):
    props = {p["proposition_id"]: p for p in fr["phase8"]["propositions"]}
    for t in fr["phase8"]["transformations"]:
        p = props[t["from_proposition_ids"][0]]
        t["from_attributes"] = t["to_attributes"] = p["attributes"]
    return fr

def run(label, fn):
    passes, c25 = 0, 0
    rows = []
    for f in sorted((RUN / "captures").glob("attempt-*.json")):
        cap = json.loads(f.read_bytes()); task = tasks[cap["task_id"]]
        parsed, _ = parse_structured_output(cap["interpretation"]["final_text"], "stop")
        fixed, _ = ns["repair"](parsed.forensic_record, task)
        fixed = sync_transformations(fn(fixed))
        a = assess_forensic_payload(fixed, original_input=task.prompt, context=task.context)
        ok = a["technical_status"] == "completed" and a.get("taxonomy", {}).get("technical_status") == "completed"
        passes += ok
        out_state = [r for r in a.get("reasons", []) if "output state hides" in r]
        c25 += bool(out_state)
        st = {p["proposition_id"]: (p["reported_verdict"], p["derived_state"]) for p in a.get("propositions", [])}
        other = [r[:120] for r in a.get("reasons", []) if not r.startswith("Ledger, evidence") and "output state hides" not in r and not r.startswith("Phase 7 artifact_source_binding_drift: Phase-8 output binding incomplete")]
        rows.append((f.name, cap["profile_id"][:18], task.id[-5:], ok, st, len(out_state), other[:3], a.get("taxonomy", {}).get("reasons"), a.get("derived_label")))
    print(f"### {label}: strict pass {passes}/12; C25 asserted_state mismatch in {c25}/12")
    for r in rows:
        print("  ", *r)

run("copy-only C1-C24,C26-C28", lambda fr: fr)
run("+ C12 via not_applicable", lambda fr: c12(fr))
run("+ C12 + C14 copy into descriptions", lambda fr: c14(c12(fr)))
