"""Verifier scan: every tracked JSON/JSONL string that looks like a model output.

Read-only over the checkout. Counts parse strategies and finds outputs that contain
more than one decodable top-level JSON object carrying "final_answer".
"""
import sys, json, hashlib, subprocess, collections, re
B = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_base"
sys.path[:0] = [B + "/src"]
import agent_arena
assert agent_arena.__file__.startswith(B), agent_arena.__file__
from agent_arena.output_contract import parse_structured_output, extract_json_object

files = subprocess.run(["git", "-C", B, "ls-files"], capture_output=True, text=True).stdout.split("\n")
files = [f for f in files if f.endswith((".json", ".jsonl"))]

seen = {}  # sha -> (text, [locations])


def walk(v, loc, key=None):
    if isinstance(v, dict):
        for k, x in v.items():
            walk(x, loc, k)
    elif isinstance(v, list):
        for x in v:
            walk(x, loc, key)
    elif isinstance(v, str):
        if '"final_answer"' in v and len(v) > 40:
            h = hashlib.sha256(v.encode()).hexdigest()
            seen.setdefault(h, [v, [], set()])
            seen[h][1].append(loc)
            seen[h][2].add(key)


for f in files:
    p = B + "/" + f
    try:
        txt = open(p, encoding="utf-8").read()
    except Exception as e:
        continue
    if f.endswith(".jsonl"):
        for i, line in enumerate(txt.splitlines(), 1):
            if not line.strip():
                continue
            try:
                walk(json.loads(line), f"{f}:{i}")
            except Exception:
                pass
    else:
        try:
            walk(json.loads(txt), f)
        except Exception:
            pass

dec = json.JSONDecoder()


def all_objects(text):
    out, i = [], 0
    while True:
        j = text.find("{", i)
        if j == -1:
            return out
        try:
            obj, end = dec.raw_decode(text, j)
        except ValueError:
            i = j + 1
            continue
        if isinstance(obj, dict) and "final_answer" in obj:
            out.append((j, obj.get("final_answer"), obj.get("confidence")))
            i = end
        else:
            i = j + 1


keys = collections.Counter()
strat = collections.Counter()
multi = []
for h, (text, locs, ks) in seen.items():
    for k in ks:
        keys[k] += 1
    parsed, d = parse_structured_output(text)
    strat[(d.strategy, d.ok, d.truncation_suspected)] += 1
    objs = all_objects(text)
    nfence = text.count("```json")
    if len(objs) > 1 or nfence > 1:
        multi.append((locs[:3], len(locs), nfence, [(o[0], o[1], o[2]) for o in objs],
                      parsed.final_answer if parsed else None, d.strategy))

print("unique strings with final_answer:", len(seen))
print("keys:", keys.most_common())
print("strategies:", sorted(strat.items(), key=str))
print("multi-object/multi-fence outputs:", len(multi))
for m in multi:
    print(" ", m)
