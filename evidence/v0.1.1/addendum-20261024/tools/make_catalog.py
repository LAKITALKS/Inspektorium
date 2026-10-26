"""Frozen narrow E1/E2 catalog; E1 payloads adapted from supplied Opus probe.

Source ZIP SHA256: 30c537180f3b349a5a3687eed393c78b234092945d6da4913040796d0ee9431a.
Run from repository root: python evidence/v0.1.1/addendum-20261024/tools/make_catalog.py
No product import; fixtures use the documented NFC/character-offset contract.
"""

import copy
import json
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EX = REPO / "examples" / "05_mixed_and_fabricated_quote"
BASE_IN = json.loads((EX / "input.json").read_text())
BASE_PR = json.loads((EX / "proposals.json").read_text())

ABOVE = [
    0x030D,
    0x030E,
    0x0304,
    0x0305,
    0x033F,
    0x0311,
    0x0306,
    0x0310,
    0x0352,
    0x0357,
    0x0351,
    0x0307,
    0x0308,
    0x030A,
    0x0342,
    0x0343,
    0x0344,
    0x034A,
    0x034B,
    0x034C,
    0x0303,
    0x0302,
    0x030C,
    0x0350,
    0x0300,
    0x0301,
    0x030B,
    0x030F,
    0x0312,
    0x0313,
]
BELOW = [
    0x0316,
    0x0317,
    0x0318,
    0x0319,
    0x031C,
    0x031D,
    0x031E,
    0x031F,
    0x0320,
    0x0324,
    0x0325,
    0x0326,
    0x0329,
    0x032A,
    0x032B,
    0x032C,
    0x032D,
    0x032E,
    0x032F,
    0x0330,
    0x0331,
    0x0332,
    0x0333,
    0x0339,
    0x033A,
    0x033B,
    0x033C,
    0x0345,
    0x0347,
    0x0348,
]

assert all(unicodedata.category(chr(c)) == "Mn" for c in ABOVE + BELOW)


def zalgo(text: str, above: int = 0, below: int = 0) -> str:
    out = []
    for i, ch in enumerate(text):
        out.append(ch)
        if ch.isalnum():
            out.extend(chr(ABOVE[(i + k) % len(ABOVE)]) for k in range(above))
            out.extend(chr(BELOW[(i + k) % len(BELOW)]) for k in range(below))
    return "".join(out)


RATIONALE = "The proposed quotation states the same time."
CLAIM2 = "It closes at 8 p.m. on weekdays."
QUOTE1 = "Northbridge Library is open on Saturdays from 10 a.m. to 2 p.m."


def case_fail_self_above(n: int):
    pr = copy.deepcopy(BASE_PR)
    pr["findings"][1]["rationale"] = zalgo(RATIONALE, above=n)
    return copy.deepcopy(BASE_IN), pr, ("findings", 1, "rationale")


def case_fail_self_below(n: int):
    pr = copy.deepcopy(BASE_PR)
    pr["findings"][1]["rationale"] = zalgo(RATIONALE, below=n)
    return copy.deepcopy(BASE_IN), pr, ("findings", 1, "rationale")


def case_last_below(n: int):
    pr = copy.deepcopy(BASE_PR)
    pr["findings"][2]["rationale"] = zalgo(RATIONALE, below=n)
    return copy.deepcopy(BASE_IN), pr, ("findings", 2, "rationale")


def case_answer_claim_below(n: int):
    """The inspected ANSWER itself carries the marks, in the claim that fails."""
    inp, pr = copy.deepcopy(BASE_IN), copy.deepcopy(BASE_PR)
    c1 = "Northbridge Library is open on Saturdays."
    c2 = unicodedata.normalize("NFC", zalgo(CLAIM2, below=n))
    c3 = "It opened in 1998."
    answer = f"{c1} {c2} {c3}"
    inp["answer"]["text"] = answer
    starts = [0, len(c1) + 1, len(c1) + 1 + len(c2) + 1]
    for f, s, c in zip(pr["findings"], starts, (c1, c2, c3), strict=True):
        f["claim_text"], f["claim_start"], f["claim_end"] = c, s, s + len(c)
    return inp, pr, ("findings", 1, "claim_text")


def case_source_quote_below(n: int):
    """The SOURCE carries the marks inside the quotation of the passing finding 1."""
    inp, pr = copy.deepcopy(BASE_IN), copy.deepcopy(BASE_PR)
    q1 = unicodedata.normalize("NFC", zalgo(QUOTE1, below=n))
    rest = inp["sources"][0]["text"][len(QUOTE1) :]
    inp["sources"][0]["text"] = q1 + rest
    f1 = pr["findings"][0]
    f1["evidence_quote"], f1["evidence_start"], f1["evidence_end"] = q1, 0, len(q1)
    shift = len(q1) - len(QUOTE1)
    f2 = pr["findings"][
        1
    ]  # fabricated quote stays fabricated; keep its relative offsets
    f2["evidence_start"] += shift
    f2["evidence_end"] += shift
    return inp, pr, ("findings", 0, "evidence_quote")


SCENARIOS = {
    "fail_self_above": case_fail_self_above,
    "fail_self_below": case_fail_self_below,
    "last_below": case_last_below,
    "answer_claim_below": case_answer_claim_below,
    "source_quote_below": case_source_quote_below,
}
NS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 24, 32, 48, 80]


def embed(field, text):
    inp, pr = copy.deepcopy(BASE_IN), copy.deepcopy(BASE_PR)
    text = unicodedata.normalize("NFC", text)
    if field == "rationale":
        pr["findings"][1][field] = text
        index = 1
    elif field == "claim_text":
        claims = [f["claim_text"] for f in pr["findings"]]
        claims[1] = text
        inp["answer"]["text"] = " ".join(claims)
        start = 0
        for f, c in zip(pr["findings"], claims, strict=True):
            f.update(claim_text=c, claim_start=start, claim_end=start + len(c))
            start += len(c) + 1
        index = 1
    else:
        old = pr["findings"][0][field]
        inp["sources"][0]["text"] = text + inp["sources"][0]["text"][len(old) :]
        pr["findings"][0].update(
            evidence_quote=text, evidence_start=0, evidence_end=len(text)
        )
        for key in ("evidence_start", "evidence_end"):
            pr["findings"][1][key] += len(text) - len(old)
        index = 0
    return inp, pr, index


rows = []
for name, build in SCENARIOS.items():
    for n in NS:
        inp, pr, (_, i, field) = build(n)
        rows.append(
            dict(
                id=f"E1-{name}-{n:02d}",
                kind="combining",
                scenario=name,
                n=n,
                finding=i,
                field=field,
                input=inp,
                proposals=pr,
            )
        )
for field in ("claim_text", "rationale", "evidence_quote"):
    for name, text in [
        ("ordinary", "Contact reviewer@example.invalid."),
        ("mailto", "Contact mailto:reviewer@example.invalid."),
        ("xmpp", "Contact xmpp:reviewer@example.invalid."),
    ]:
        inp, pr, i = embed(field, text)
        rows.append(
            dict(
                id=f"E2-{field}-{name}",
                kind="email",
                finding=i,
                field=field,
                input=inp,
                proposals=pr,
            )
        )
    inp, pr, i = embed(field, "Größe café Ελληνικά שָׁלוֹם مُرَحَّبًا हिंदी a\u0301\u0323.")
    rows.append(
        dict(
            id=f"CLEAN-{field}",
            kind="clean",
            finding=i,
            field=field,
            input=inp,
            proposals=pr,
        )
    )
path = Path(__file__).resolve().parent.parent / "catalog.json"
path.write_text(
    json.dumps(
        {
            "id": "v0.1.1-E1-E2-addendum",
            "version": "2026-10-24.1",
            "historical_catalog": "catalog 1.0: 70 cases, unchanged",
            "criteria": {
                "E1-text": (
                    "No emitted raw Mn/Me run greater than four "
                    "(Markdown and rendered text)"
                ),
                "E1-image": (
                    "at least 10 added grayscale<160 pixels in a "
                    "non-payload host text box; invalid pairs cannot pass"
                ),
                "K7-email": (
                    "Zero anchor elements; record every href and visible "
                    "link text, no exception"
                ),
            },
            "cases": rows,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n"
)
print(f"Frozen {len(rows)} cases to {path.name}")
