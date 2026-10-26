"""Verifier: prompt hashes, number of r2 replacements, and C15/C16-C18 restriction wording."""
import hashlib
import sys

DIAG = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/diag_new"
sys.path.insert(0, DIAG + "/src")
import agent_arena  # noqa: E402
assert agent_arena.__file__.startswith(DIAG), agent_arena.__file__
from agent_arena import phase8_pipeline as pp  # noqa: E402
from agent_arena.runner import resolve_study_forensics_prompt  # noqa: E402

for v in ("study_forensics_prompt/v3-phase8-contract-r2", "study_forensics_prompt/v3-phase8-contract-r2-review-p9-2"):
    print(v, hashlib.sha256(resolve_study_forensics_prompt(v).encode()).hexdigest())
print("number of _R2_REPLACEMENTS:", len(pp._R2_REPLACEMENTS))
r1, r2 = pp.build_phase8_contract_r1(), pp.build_phase8_contract_r2()
for i, (old, new) in enumerate(pp._R2_REPLACEMENTS, 1):
    print(f"  {i}: R1 count {r1.count(old)} | starts {old[:60]!r}")
for tag in ("C15.", "C16.", "C17.", "C18."):
    start = r2.index(tag)
    seg = r2[start:r2.index("\n" + "C" + str(int(tag[1:3]) + 1) + ".", start)]
    print(tag, "mentions 'required':", "required" in seg)
    if tag == "C15.":
        print("   ", " ".join(seg.split())[:400])
hdr = r2[: r2.index("Shape")]
print("r2 header materiality sentence:", " ".join(hdr.split())[ hdr.find("A difference") - 0:][:260] if "A difference" in hdr else "?")
print("r2 header mentions taxonomy/label:", any(w in hdr.lower() for w in ("taxonom", "label")))
