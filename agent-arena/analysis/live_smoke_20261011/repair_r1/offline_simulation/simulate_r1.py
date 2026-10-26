"""Critic-only offline simulation (never evidence of model output).

Takes the 12 stored revision-1 answers, applies COPY-ONLY repairs that a model following the
R1 appendix literally (C1..C28) would make while keeping its own semantic choices (attributes,
relations, verdicts, roles, observations, directness, asserted_state), then runs the unchanged
validator to see which checks remain. Usage: python simulate_r1.py <repo_root> [--literal-c19]
"""
import copy
import json
import sys
from pathlib import Path

from agent_arena.output_contract import parse_structured_output
from agent_arena.phase8_models import PropositionLedger, SemanticAttributes
from agent_arena.phase8_pipeline import assess_forensic_payload
from agent_arena.phase8_semantics import PRODUCT_DIMENSIONS
from agent_arena.task_loader import load_task

ROOT = Path(sys.argv[1])
LITERAL_C19 = "--literal-c19" in sys.argv
RUN = ROOT / "analysis/live_smoke_20261011/live_run"
LEDGER_KEYS = set(PropositionLedger.model_fields)
ATTR = set(SemanticAttributes.model_fields)
REL_MAP = {"causes": "causal", "causal (makes)": "causal", "reduction": "causal", "reduced": "causal",
           "improved": "causal", "better than": "causal", "treats": "therapeutic", "design": "description"}
DIM_MAP = {"causal relation": "relation", "duration": "follow_up"}


def repair(fr: dict, task) -> tuple[dict, list[str]]:
    notes = []
    fr = copy.deepcopy(fr)
    claim = task.prompt
    sources = {"input": task.prompt, "context": task.context}
    p8 = fr.get("phase8") or {}
    if "ledger" in p8 and isinstance(p8["ledger"], dict):  # C1 unwrap
        tax = p8.get("taxonomy")
        p8 = p8["ledger"]
        if tax and not fr.get("phase8_taxonomy"):
            fr["phase8_taxonomy"] = tax
        notes.append("C1 unwrap")
    extra = set(p8) - LEDGER_KEYS
    if extra:
        notes.append(f"C1 drop {sorted(extra)}")
    p8 = {k: v for k, v in p8.items() if k in LEDGER_KEYS}
    # C2
    prov = (fr.get("provenance") or [{}])[0]
    pid_prov = prov.get("provenance_id") or "prov1"
    fr["provenance"] = [{"provenance_id": pid_prov, "exact_claim_text": claim, "source_id": "input"}]
    p8["provenance_id"] = pid_prov
    p8["original_claim"] = claim
    p8.setdefault("claim_id", "claim")
    p8.setdefault("extraction_provenance", "model")
    # C3 evidence quotes
    for ev in fr.get("evidence", []):
        src = sources.get(ev.get("source_id"))
        ref, text = ev.get("exact_reference") or "", ev.get("text") or ""
        if src is None or (ref not in src and text not in src):
            for sid, s in sources.items():
                if (ref and ref in s) or (text and text in s):
                    ev["source_id"], src = sid, s
                    break
        if src is not None:
            if text not in src and ref and ref in src:
                ev["text"] = ref
                notes.append(f"C3 text<-ref {ev['evidence_id']}")
            elif (not ref or ref not in src) and text and text in src:
                ev["exact_reference"] = text
                notes.append(f"C3 ref<-text {ev['evidence_id']}")
        # C6
        vo = ev.get("value_origin")
        if vo not in ("source_reported", "system_derived"):
            if vo is not None or ev.get("reported_value") is not None:
                ev["value_origin"] = "source_reported"
                notes.append(f"C6 {vo!r}->source_reported")
    ev_by = {e["evidence_id"]: e for e in fr.get("evidence", [])}
    # C16 scopes
    scope_id = "scope:supplied"
    fr["search_scopes"] = [{"search_scope_id": scope_id, "scope_type": "reviewed_set",
                            "reviewed_source_ids": ["input", "context"]}]
    props = p8.get("propositions", [])
    for p in props:
        # C9 spans
        sp = p.get("original_span") or {}
        t = sp.get("text") or ""
        if t and t in claim:
            i = claim.index(t)
            if (sp.get("start"), sp.get("end")) != (i, i + len(t)):
                notes.append(f"C9 {p['proposition_id']}")
            p["original_span"] = {"start": i, "end": i + len(t), "text": t}
        p["parent_claim_id"] = p8["claim_id"]
        p["provenance_id"] = pid_prov
        # C11
        md = [DIM_MAP.get(d, d) for d in p.get("material_dimensions", [])]
        p["material_dimensions"] = sorted({d for d in md if d in ATTR})
        p["not_applicable"] = {DIM_MAP.get(k, k): v for k, v in (p.get("not_applicable") or {}).items()
                               if DIM_MAP.get(k, k) in ATTR and isinstance(v, str) and v.strip()}
        # C13 relation vocabulary (semantic mapping a compliant model would choose)
        rel = (p.get("attributes") or {}).get("relation")
        if rel in REL_MAP:
            p["attributes"]["relation"] = REL_MAP[rel]
        p["search_scope_ids"] = [scope_id]
        for b in p.get("evidence_bindings", []):
            b["proposition_id"] = p["proposition_id"]
            b["search_scope_id"] = scope_id
    for d in p8.get("evidence_descriptions", []):
        rel = (d.get("attributes") or {}).get("relation")
        if rel in REL_MAP:
            d["attributes"]["relation"] = REL_MAP[rel]
        # C7
        arg = d.get("identification_argument")
        ids = [i for i in d.get("identification_evidence_ids", []) if i in ev_by]
        if arg and not any(arg in ev_by[i].get("text", "") for i in ids):
            d["identification_argument"] = ev_by[ids[0]]["text"] if ids else None
            notes.append(f"C7 {d['evidence_id']}")
    # C10
    req = [p["proposition_id"] for p in props if p.get("materiality") == "required"]
    p8["required_proposition_ids"] = req

    def leaves(n):
        if not isinstance(n, dict):
            return []
        if n.get("operator") == "leaf":
            return [n.get("proposition_id")]
        return [x for c in n.get("children", []) for x in leaves(c)]
    logic = p8.get("logic") or {}
    if set(leaves(logic)) != set(req) or (logic.get("operator") == "leaf" and len(req) != 1):
        op = logic.get("operator") if logic.get("operator") in ("and", "or") else "and"
        p8["logic"] = ({"operator": "leaf", "proposition_id": req[0], "children": []} if len(req) == 1 else
                       {"operator": op, "proposition_id": None,
                        "children": [{"operator": "leaf", "proposition_id": r, "children": []} for r in req]})
        notes.append("C10 logic")
    # C26/C27
    bids = {b["binding_id"] for p in props for b in p.get("evidence_bindings", [])}
    pt = []
    for t in p8.get("product_transfers", []):
        t["dimensions"] = [x for x in t.get("dimensions", []) if x in PRODUCT_DIMENSIONS]
        if t.get("binding_id") in bids and t["dimensions"]:
            pt.append(t)
        else:
            notes.append(f"C26 drop {t.get('transfer_id')}")
    p8["product_transfers"] = pt
    pids = {p["proposition_id"] for p in props}
    br = []
    for b in p8.get("bridges", []):
        if b.get("kind") == "mechanism_to_outcome" and not b.get("premise_proposition_ids"):
            notes.append(f"C27 drop {b.get('bridge_id')}")
            continue
        if b.get("conclusion_proposition_id") in pids:
            br.append(b)
    p8["bridges"] = br
    brids = {b["bridge_id"] for b in br}
    for p in props:
        p["required_bridge_ids"] = [x for x in p.get("required_bridge_ids", []) if x in brids]
    # C5 descriptions for every used evidence
    descs = {d["evidence_id"]: d for d in p8.get("evidence_descriptions", []) if d.get("evidence_id") in ev_by}
    used = {b["evidence_id"] for p in props for b in p.get("evidence_bindings", [])}
    used |= {e for b in br for e in b.get("evidence_ids", [])} | {e for t in pt for e in t.get("evidence_ids", [])}
    for d in list(descs.values()):
        used |= set(d.get("identification_evidence_ids", [])) | set(d.get("underlying_evidence_ids", []))
    for e in sorted(used):
        if e in ev_by and e not in descs:
            descs[e] = {"evidence_id": e, "evidence_type": "unknown", "source_role": "unspecified",
                        "attributes": {}}
            notes.append(f"C5 add description {e}")
    p8["evidence_descriptions"] = list(descs.values())
    # C4 orphan material evidence -> material false (model's alternative would be to bind it)
    for e in fr.get("evidence", []):
        if e.get("material", True) and e["evidence_id"] not in used:
            e["material"] = False
            notes.append(f"C4 immaterial {e['evidence_id']}")
    # C18 findings
    old = {f.get("finding_id"): f for f in fr.get("findings", [])}
    findings = []
    for p in props:
        if p["proposition_id"] not in req:
            continue
        f = dict(old.get(p["proposition_id"]) or {})
        bound = [b for b in p.get("evidence_bindings", [])]
        contra = [b["evidence_id"] for b in bound if b.get("observation") == "contradiction"
                  or ev_by.get(b["evidence_id"], {}).get("role") in ("contradictory", "weakening")]
        supp = [b["evidence_id"] for b in bound if b["evidence_id"] not in contra]
        f.update(finding_id=p["proposition_id"], provenance_id=pid_prov, proposition=p["proposition_text"],
                 supporting_evidence_ids=sorted(set(supp)), contrary_evidence_ids=sorted(set(contra)))
        f.setdefault("verdict_summary", "")
        f.setdefault("allowed_summary_strength", "not_assessed")
        findings.append(f)
    fr["findings"] = findings
    fids = {f["finding_id"]: f for f in findings}
    # C17 negative assertions
    negs = []
    for p in props:
        if p["proposition_id"] not in req:
            continue
        for b in p.get("evidence_bindings", []):
            if b.get("observation") == "no_evidence_found":
                negs.append({"assertion_id": f"neg:{p['proposition_id']}:{b['binding_id']}",
                             "finding_id": p["proposition_id"], "proposition": p["proposition_text"],
                             "assertion_scope": "reviewed_set", "search_scope_id": b["search_scope_id"]})
    fr["negative_assertions"] = negs
    # C19/C20 client findings
    order = ["not_assessed", "mixed", "not_directly_established", "limited_support", "not_supported",
             "contradicted", "disproven"]
    clients = []
    for c in fr.get("client_findings", []):
        if c.get("parent_finding_id") not in fids:
            if len(fids) == 1:
                c["parent_finding_id"] = next(iter(fids))
            else:
                notes.append(f"C19 drop client {c.get('client_finding_id')}")
                continue
        parent = fids[c["parent_finding_id"]]
        allowed = set(parent["supporting_evidence_ids"]) | set(parent["contrary_evidence_ids"])
        refs = [e for e in c.get("referenced_evidence_ids", []) if e in allowed]
        mat = [e for e in allowed if ev_by.get(e, {}).get("material", True)]
        dirs = {("s" if ev_by[e].get("role", "supporting") == "supporting" else "o") for e in mat}
        if len(dirs) == 2 or not LITERAL_C19:
            for dname in dirs:
                if not any(("s" if ev_by[e].get("role", "supporting") == "supporting" else "o") == dname
                           for e in refs if e in mat):
                    refs.append(next(e for e in mat if ("s" if ev_by[e].get("role", "supporting") == "supporting"
                                                         else "o") == dname))
        c["referenced_evidence_ids"] = refs
        c["provenance_id"] = pid_prov
        cs, ps = c.get("client_strength", "not_assessed"), parent.get("allowed_summary_strength")
        if cs not in order or ps not in order or order.index(cs) > order.index(ps):
            c["client_strength"] = ps if ps in order else "not_assessed"
            if ps not in order:
                parent["allowed_summary_strength"] = "not_assessed"
        c["value_claims"] = [v for v in c.get("value_claims", []) if v.get("evidence_id") in ev_by]
        for v in c["value_claims"]:
            if v.get("claimed_origin") not in ("source_reported", "system_derived", "unspecified") or \
                    v.get("claimed_origin") != ev_by[v["evidence_id"]].get("value_origin"):
                v["claimed_origin"] = "unspecified"
        cna = []
        for n in c.get("client_negative_assertions", []):
            if negs:
                cna.append({"assertion_id": negs[0]["assertion_id"], "client_scope": "reviewed_set"})
        c["client_negative_assertions"] = cna
        clients.append(c)
    fr["client_findings"] = clients
    # C21-C24 transformations: rebuilt exactly; asserted_state kept from the model's own item
    old_t = {}
    for t in p8.get("transformations", []):
        old_t.setdefault((t.get("stage"), t.get("target_id")), t)
    pmap = {p["proposition_id"]: p for p in props}
    newt = []
    for p in props:
        if p["proposition_id"] not in req:
            continue
        pid = p["proposition_id"]
        f = fids[pid]
        texts = {"extraction": (p["original_span"]["text"], p["proposition_text"]),
                 "search_question": (p["proposition_text"], p["search_question"]),
                 "internal": (p["proposition_text"], f["proposition"] + ("\n" + f["verdict_summary"]
                                                                        if f.get("verdict_summary") else ""))}
        for stage, (a, b) in texts.items():
            o = old_t.get((stage, pid)) or next((t for (s, _), t in old_t.items() if s == stage
                                                 and pid in (t.get("from_proposition_ids") or [])), {})
            newt.append({"transformation_id": f"t:{stage}:{pid}", "target_id": pid, "stage": stage,
                         "from_proposition_ids": [pid], "from_text": a, "to_text": b,
                         "from_attributes": p["attributes"], "to_attributes": p["attributes"],
                         "asserted_state": o.get("asserted_state"),
                         "asserts_whole_claim": bool(o.get("asserts_whole_claim")) if o.get("asserted_state") else False,
                         "reason": o.get("reason") or "copy"})
    for c in clients:
        p = pmap[c["parent_finding_id"]]
        o = old_t.get(("summary", c["client_finding_id"])) or next(
            (t for (s, _), t in old_t.items() if s == "summary"), {})
        state = o.get("asserted_state") or p.get("reported_verdict")
        newt.append({"transformation_id": f"t:summary:{c['client_finding_id']}", "target_id": c["client_finding_id"],
                     "stage": "summary", "from_proposition_ids": [c["parent_finding_id"]],
                     "from_text": p["proposition_text"],
                     "to_text": c["display_claim"] + ("\n" + c["client_explanation"] if c.get("client_explanation") else ""),
                     "from_attributes": p["attributes"], "to_attributes": p["attributes"],
                     "asserted_state": state, "asserts_whole_claim": bool(o.get("asserts_whole_claim")),
                     "reason": o.get("reason") or "copy"})
    p8["transformations"] = newt
    fr["phase8"] = p8
    # C28 taxonomy references
    tax = fr.get("phase8_taxonomy")
    if isinstance(tax, dict):
        tax["proposition_ids"] = [x for x in tax.get("proposition_ids", []) if x in pmap]
        tax["evidence_ids"] = [x for x in tax.get("evidence_ids", []) if x in descs]
        causal = any((pmap[x].get("attributes") or {}).get("relation") in
                     {"causal", "causal_effect", "human_clinical_benefit", "therapeutic", "preventive"}
                     for x in tax["proposition_ids"])
        if tax.get("causal_claim") is not None and tax.get("causal_claim") != causal:
            notes.append(f"C28 causal_claim {tax.get('causal_claim')}->{causal}")
            tax["causal_claim"] = causal
    return fr, notes


def main():
    tasks = {}
    for f in sorted((RUN / "tasks").glob("LS-0*.json")):
        t = load_task(f)
        tasks[t.id] = t
    for f in sorted((RUN / "captures").glob("attempt-*.json")):
        cap = json.loads(f.read_bytes())
        task = tasks[cap["task_id"]]
        parsed, diag = parse_structured_output(cap["interpretation"]["final_text"], "stop")
        fr = parsed.forensic_record
        before = assess_forensic_payload(fr, original_input=task.prompt, context=task.context)
        fixed, notes = repair(fr, task)
        after = assess_forensic_payload(fixed, original_input=task.prompt, context=task.context)
        print(f"== {f.name} {cap['profile_id']} {task.id[-5:]} before={before['technical_status']} "
              f"after={after['technical_status']} tax={after.get('taxonomy', {}).get('technical_status')} "
              f"label={after.get('derived_label')} composite={after.get('assessed_composite_state', after.get('composite_state'))}")
        states = {p['proposition_id']: (p['reported_verdict'], p['derived_state']) for p in after.get('propositions', [])}
        print("   states(reported,derived):", states)
        for r in after.get("reasons", []):
            if r.startswith("Ledger, evidence constraints"):
                continue
            print("   -", r[:220])
        if after.get("taxonomy", {}).get("technical_status") != "completed" or True:
            print("   tax:", after.get("taxonomy", {}).get("reasons"))


main()
