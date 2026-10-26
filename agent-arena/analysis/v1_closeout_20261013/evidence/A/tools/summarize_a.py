"""A1-A3 summary: extract operator-facing rows from record.json, report.md and report.html of each replay
bundle and compare the preserved Phase-9 history with the live bundle in the scratch COPY (modulo run ids and
timestamps). Pure file reading; no agent_arena import, no network. Usage: summarize_a.py SCRATCH OUT_JSON"""
import glob
import hashlib
import html
import json
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

S = Path(sys.argv[1])
SLOTS = {"claude-sonnet-5-5-LR-02": "bundles/claude-sonnet-5-5@3/44b587d3-0d46-41c0-9984-97dbbc14c6bf",
         "claude-sonnet-5-5-LR-03": "bundles/claude-sonnet-5-5@3/cab93a7a-9b80-4d9c-bae7-14e8676941f2",
         "claude-haiku-5-5-LR-03": "bundles/claude-haiku-5-5@3/d856f044-59f8-4f74-8b04-b48cc9250d9e"}
IMMUTABLE = ("This revision is immutable: only a recorded human decision (agent-arena audit review) or a new, "
             "explicitly commissioned run creates a new revision.")
STATE_ROWS = ("scientific judgment", "model judgment (composite)", "host evidence derivation (composite)",
              "review route", "review execution", "mandatory review", "model/host conflicts",
              "automatic processing", "open cause", "analysis execution", "local release")


def md_view(path):
    lines = [html.unescape(x) for x in Path(path).read_text().split("\n")]
    out = {"h2": [x[3:] for x in lines if x.startswith("## ")], "paragraphs_execution": [], "states": {},
           "history_sentences": []}
    section, sub = None, None
    for x in lines:
        if x.startswith("## "):
            section, sub = x[3:], None
            continue
        if x.startswith("### "):
            sub = x[4:]
            continue
        if section == "Execution and release" and sub is None and x.strip() and not x.startswith("|"):
            out["paragraphs_execution"].append(x)
        if section == "Execution and release" and sub == "Independent states" and x.startswith("| ") \
                and not x.startswith("| Field") and not x.startswith("| ---"):
            k, v = [c.strip() for c in x.strip().strip("|").split(" | ", 1)]
            out["states"][k] = v
        if section == "UNKNOWN, conflicts and review history" and x.strip() and not x.startswith("|"):
            out["history_sentences"].append(x)
    out["sub_counts"] = dict(Counter(x[4:] if not x[4:].startswith("Position ") else "Position"
                                     for x in lines if x.startswith("### ")))
    return out


class H(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.ps, self.h, self.rows, self.cur, self.cell, self.last_h3 = [], [], [], {}, None, None, None
        self.buf = ""

    def handle_starttag(self, tag, attrs):
        self.stack.append((tag, dict(attrs)))
        if tag in ("p", "h2", "h3", "td"):
            self.buf = ""
        if tag == "tr":
            self.cur = []

    def handle_endtag(self, tag):
        t, a = self.stack.pop() if self.stack else (tag, {})
        if tag == "p":
            self.ps.append((a.get("class"), self.buf))
        elif tag in ("h2", "h3"):
            self.h.append((tag, self.buf))
            if tag == "h3":
                self.last_h3 = self.buf
        elif tag == "td" and self.cur is not None:
            self.cur.append(self.buf)
        elif tag == "tr" and self.cur is not None:
            if len(self.cur) == 2:
                self.rows.setdefault(self.last_h3, []).append(tuple(self.cur))
            self.cur = None

    def handle_data(self, data):
        self.buf += data


def html_view(path):
    p = H()
    p.feed(Path(path).read_text())
    status = [t for c, t in p.ps if c == "status"]
    return {"status_paragraphs": status, "notices": [t for c, t in p.ps if c == "notice"],
            "states": dict(p.rows.get("Independent states", [])),
            "h2": [t for tag, t in p.h if tag == "h2"],
            "history_sentences": [t for c, t in p.ps if t.startswith(("No disagreement", "Conflicts were not",
                                                                       "Current assessment contains",
                                                                       "No adjudication", "Conflicts between"))]}


def record_view(bundle):
    rec = json.loads((Path(bundle) / "record.json").read_text())
    dec = json.loads((Path(bundle) / "decision.json").read_text())
    p9 = rec["run_record"]["metadata"]["phase9"]
    return {"revision_id": rec["revision_id"], "run_id": rec["run_record"]["run_id"], "status": rec["status"],
            "execution_mode": rec["execution_mode"],
            "code_fingerprint": rec["provenance"]["code"]["code_fingerprint"],
            "verified_source_commit": rec["provenance"]["code"].get("verified_source_commit"),
            "phase9": {k: p9.get(k) for k in ("contract_version", "route", "mandatory", "review_state",
                                               "execution_status", "technical_status", "history_validation")},
            "attempts": [{"kind": a["kind"], "status": a["status"], "reason": a.get("reason")}
                         for a in p9.get("attempts", [])],
            "triggers": [{"code": t["code"], "field": t["field"], "mandatory": t["mandatory"],
                          "material": t["material"], "reason": t["reason"][:200]} for t in p9.get("triggers", [])],
            "positions": [{"origin": x["origin"], "raw_sha256": x["raw_sha256"], "model": x.get("model"),
                           "provider": x.get("provider")} for x in p9.get("positions", [])],
            "conflicts_count": len(p9.get("conflicts", [])),
            "conflict_resolutions": dict(Counter(str(c.get("resolution")) for c in p9.get("conflicts", []))),
            "adjudications": [{"reviewer_type": d.get("reviewer_type"), "outcome": d.get("outcome")}
                              for d in p9.get("adjudications", [])],
            "failing_controls": [{"control_id": c["control_id"], "version": c["version"], "reason": c["reason"]}
                                 for c in dec["controls"] if c["outcome"] == "fail"]}


def p8_modulo_contract(phase8):
    """AA-P8/1.2 -> AA-P8/1.3 is the intended v1 contract bump; only the version label may differ."""
    d = json.loads(json.dumps(phase8))
    d.pop("contract_version", None)
    d["reasons"] = [r.replace("AA-P8/1.2 (", "AA-P8/1.x (").replace("AA-P8/1.3 (", "AA-P8/1.x (")
                    for r in d.get("reasons", [])]
    return d


def norm(p9, strict=False):
    pos = {p["position_id"]: p for p in p9["positions"]}

    def origin(pid):
        return pos[pid]["origin"] if pid in pos else "?"
    return {
        "positions": sorted((p["origin"], p["raw_sha256"],
                             json.dumps(p["phase8"] if strict else p8_modulo_contract(p["phase8"]), sort_keys=True),
                             json.dumps(p.get("forensic_record"), sort_keys=True)) for p in p9["positions"]),
        "conflicts": Counter(json.dumps([c["dimension"], c["field"], c["material"], c.get("resolution"), c["reason"],
                                         sorted([origin(x["position_id"]), json.dumps(x["value"], sort_keys=True),
                                                 x["evidence_ids"]] for x in c["positions"])], sort_keys=True)
                             for c in p9["conflicts"]),
        "triggers": Counter(json.dumps([t["code"], t["field"], t["reason"], t["mandatory"], t["material"],
                                        sorted(origin(x) for x in t["position_ids"]) if strict else "pair-modulo-run-ids",
                                        t["proposition_ids"],
                                        t["evidence_ids"]], sort_keys=True) for t in p9["triggers"]),
        "attempts": [[a["kind"], a["status"], a.get("reason"), a.get("packet_sha256")] for a in p9.get("attempts", [])],
        "adjudications": [[d.get("reviewer_type"), d.get("origin"), d.get("outcome"),
                           origin(d.get("selected_position_id"))] for d in p9.get("adjudications", [])],
        "scalars": {k: p9.get(k) for k in ("route", "mandatory", "review_state", "execution_status",
                                           "technical_status", "history_validation")},
        "uncertainty_count": len(p9.get("uncertainty", []))}


def compare(live_bundle, replay_bundle):
    la = json.loads((Path(live_bundle) / "record.json").read_text())["run_record"]["metadata"]["phase9"]
    lb = json.loads((Path(replay_bundle) / "record.json").read_text())["run_record"]["metadata"]["phase9"]
    a, b = norm(la), norm(lb)
    sa, sb = norm(la, strict=True), norm(lb, strict=True)
    res = {k: ("equal" if a[k] == b[k] else {"live": str(a[k])[:400], "replay": str(b[k])[:400]}) for k in a}
    res["strict_equal"] = {k: sa[k] == sb[k] for k in sa}
    res["normalization"] = ("positions: raw_sha256, origin, forensic_record and full phase8 compared; phase8 "
                            "contract_version and the version label inside reasons[0] masked (intended AA-P8/1.2 -> "
                            "1.3 bump). triggers: code, field, reason, mandatory, material, proposition_ids, "
                            "evidence_ids compared; the representative position pair is masked because trigger_id "
                            "dedup keeps the last conflict in position_id order and position ids are run-bound.")
    res["phase8_contract_versions"] = {"live": sorted({p["phase8"].get("contract_version") for p in la["positions"]}),
                                       "replay": sorted({p["phase8"].get("contract_version") for p in lb["positions"]})}
    res["raw_sha256_equal_by_origin"] = ({p["origin"]: p["raw_sha256"] for p in la["positions"]} ==
                                         {p["origin"]: p["raw_sha256"] for p in lb["positions"]})
    res["counts_live"] = {"positions": len(a["positions"]), "conflicts": sum(a["conflicts"].values()),
                          "triggers": sum(a["triggers"].values()), "attempts": len(a["attempts"]),
                          "adjudications": len(a["adjudications"])}
    res["counts_replay"] = {"positions": len(b["positions"]), "conflicts": sum(b["conflicts"].values()),
                            "triggers": sum(b["triggers"].values()), "attempts": len(b["attempts"]),
                            "adjudications": len(b["adjudications"])}
    return res


summary = {"note": "Replays of COPIES of analysis/c25_p9_20261011/live_retest with agent_arena 1.0.0 (5560e95); "
           "live bundle values are read from the scratch copy (produced by code a1654da6afd6, commit claim 63399dd).",
           "slots": {}}
for slot, live_rel in SLOTS.items():
    bundles = [Path(p).parent for p in glob.glob(str(S / "replay" / slot / "*" / "record.json"))]
    assert len(bundles) == 1, bundles
    rb, lb = bundles[0], S / "copy" / live_rel
    cli = json.loads((S / "replay" / f"{slot}.cli.json").read_text())
    md, hv, rv = md_view(rb / "report.md"), html_view(rb / "report.html"), record_view(rb)
    lmd = md_view(lb / "report.md")
    ended_md = [p for p in md["paragraphs_execution"] if p.startswith("Automatic processing has ended")]
    ended_html = [t for t in hv["notices"] if t.startswith("Automatic processing has ended")]
    summary["slots"][slot] = {
        "replay_bundle": str(rb.relative_to(S)),
        "replay_bundle_file_sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(rb.iterdir())},
        "cli": {"status": cli["status"], "errors": cli["errors"],
                "exit": (S / "replay" / f"{slot}.exit").read_text().strip()},
        "status_line": {"md": md["paragraphs_execution"][0], "html": hv["status_paragraphs"]},
        "automatic_processing_ended_sentence": {"md": ended_md, "html": ended_html},
        "independent_states_md": {k: md["states"].get(k) for k in STATE_ROWS},
        "independent_states_md_equals_html": md["states"] == hv["states"],
        "immutable_revision_sentence_present": {"md": any(IMMUTABLE in p for p in ended_md),
                                                "html": any(IMMUTABLE in t for t in ended_html)},
        "visible_control_tokens_in_failing_reasons": [c["control_id"] for c in rv["failing_controls"]
                                                      if "\u27e6U+" in c["reason"]],
        "history_closing_sentences": {"md": md["history_sentences"], "html": hv["history_sentences"]},
        "report_block_counts_md": md["sub_counts"],
        "h2_md_equals_html": md["h2"] == hv["h2"],
        "record": rv,
        "history_preserved_vs_live_bundle": compare(lb, rb),
        "live_bundle_under_old_code": {"bundle": live_rel, "status_line": lmd["paragraphs_execution"][0],
                                       "has_ended_sentence": any(p.startswith("Automatic processing has ended")
                                                                 for p in lmd["paragraphs_execution"]),
                                       "independent_states": lmd["states"],
                                       "history_closing_sentences": [x for x in lmd["history_sentences"]
                                                                     if x.startswith(("No ", "Current assessment",
                                                                                      "Conflicts"))]}}
for slot, v in summary["slots"].items():
    old = [Path(p).parent for p in glob.glob(str(S / "_superseded_fd1ad7c" / "replay" / slot / "*" / "record.json"))]
    if len(old) == 1:
        o = json.loads((old[0] / "record.json").read_text())["run_record"]["metadata"]["phase9"]
        n = json.loads((S / v["replay_bundle"] / "record.json").read_text())["run_record"]["metadata"]["phase9"]
        a, b = norm(o, strict=True), norm(n, strict=True)
        ov = md_view(old[0] / "report.md")
        v["vs_superseded_fd1ad7c_replay"] = {
            "phase9_history_strict_equal": {k: a[k] == b[k] for k in a},
            "independent_state_rows_changed": {k: {"fd1ad7c": ov["states"].get(k), "5560e95": v["independent_states_md"].get(k)}
                                               for k in STATE_ROWS if ov["states"].get(k) != v["independent_states_md"].get(k)},
            "ended_sentence_fd1ad7c": [p for p in ov["paragraphs_execution"] if p.startswith("Automatic processing has ended")]}
causes = {s: v["independent_states_md"]["open cause"] for s, v in summary["slots"].items()}
summary["A2_causes_pairwise_distinct"] = len(set(causes.values())) == 3
summary["A2_cli_errors_pairwise_distinct"] = len({json.dumps(v["cli"]["errors"]) for v in summary["slots"].values()}) == 3
summary["A2_conflict_rows"] = {s: v["independent_states_md"]["model/host conflicts"] for s, v in summary["slots"].items()}
summary["A2_open_causes"] = causes
Path(sys.argv[2]).write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({s: {"status": v["record"]["status"], "ended": bool(v["automatic_processing_ended_sentence"]["md"]),
                      "parity": v["independent_states_md_equals_html"],
                      "preserved": {k: v["history_preserved_vs_live_bundle"][k] == "equal" for k in
                                    ("positions", "conflicts", "triggers", "attempts", "adjudications", "scalars")}}
                  for s, v in summary["slots"].items()}, indent=1))
print("distinct causes", summary["A2_causes_pairwise_distinct"], "distinct cli", summary["A2_cli_errors_pairwise_distinct"])
