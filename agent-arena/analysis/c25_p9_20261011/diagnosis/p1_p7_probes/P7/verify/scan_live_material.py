"""Scan live smoke / repair R1 captures (read-only) for evidence items with material false,
and whether such items are bound (Phase-8 bindings) or listed in a finding's evidence ids."""
import glob, json, sys
BASE = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"

def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + f"/{i}")
    else:
        yield path, o

def records(o):
    # find any string that parses as JSON containing forensic_record, or dicts with forensic_record
    if isinstance(o, dict):
        if "forensic_record" in o and isinstance(o["forensic_record"], dict):
            yield o["forensic_record"]
        for v in o.values():
            yield from records(v)
    elif isinstance(o, list):
        for v in o:
            yield from records(v)
    elif isinstance(o, str) and "forensic_record" in o:
        s = o
        for cand in (s, s[s.find("{"): s.rfind("}") + 1] if "{" in s else ""):
            try:
                yield from records(json.loads(cand)); break
            except Exception:
                continue

files = sorted(glob.glob(BASE + "/analysis/live_smoke_20261011/**/captures/*.json", recursive=True))
print("capture files:", len(files))
tot_ev = tot_false = 0
for f in files:
    data = json.load(open(f))
    for fr in records(data):
        ev = fr.get("evidence", []) or []
        p8 = fr.get("phase8") or {}
        bound = {b.get("evidence_id") for p in (p8.get("propositions") or []) if isinstance(p, dict)
                 for b in (p.get("evidence_bindings") or []) if isinstance(b, dict)}
        fid_ev = {e for fd in (fr.get("findings") or []) if isinstance(fd, dict)
                  for e in (fd.get("supporting_evidence_ids") or []) + (fd.get("contrary_evidence_ids") or [])}
        for e in ev:
            if not isinstance(e, dict):
                continue
            tot_ev += 1
            if e.get("material") is False:
                tot_false += 1
                print(f.split("live_smoke_20261011/")[1], e.get("evidence_id"), "role", e.get("role"),
                      "bound", e.get("evidence_id") in bound, "in_finding", e.get("evidence_id") in fid_ev)
print("evidence items:", tot_ev, "material false:", tot_false)
print("records per file:", [(f.split("live_smoke_20261011/")[1], sum(1 for _ in records(json.load(open(f))))) for f in files][:24])
