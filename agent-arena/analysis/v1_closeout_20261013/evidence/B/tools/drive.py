"""Area B evidence driver (v1 closeout, candidate 5560e95). Offline only; network refused by netguard.

SYNTHETIC TEST FIXTURE — not an empirical model response.

1. Materialises the SYNTHETIC TEST FIXTURES of tests/test_v1_closeout_report.py (conflict_fixture) and
   tests/test_v1_semantics.py (variant) into evidence/B/fixtures/.
2. Runs each through the canonical CLI (guarded_cli.py == console script agent_arena.cli:cli after netguard):
   audit validate, audit run --offline, audit inspect, audit release, audit inspect (released).
3. Analyses every bundle: real materiality logic on the stored position, P8/P9 records, the record-derived
   projection rows, report.md (raw bytes and decoded) and report.html, outcome sentence, history closing
   sentence, claim scan, CLI stdout ASCII check.
4. Before/after: the same fixture bytes through the archived code of 558e920 (investigation baseline) and
   fd1ad7c (previous candidate), via git archive into scratch.
5. Cross-check: B1 through the literal console script .venv/bin/agent-arena (netguard via sitecustomize).
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tarfile
from html.parser import HTMLParser
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import netguard  # noqa: E402

REPO = Path("__LOCAL_HOME__/Documents/Projects/agent-arena")
sys.path.insert(0, str(REPO))  # `tests` package (fixture builders)
SCRATCH = TOOLS.parent
EVID = REPO / "analysis/v1_closeout_20261013/evidence/B"
FIX = EVID / "fixtures"
WORK = SCRATCH / "work"
BUNDLES = SCRATCH / "bundles"
OLD = {"558e920": SCRATCH / "old558" / "src", "fd1ad7c": SCRATCH / "oldfd1" / "src"}
PY = str(REPO / ".venv/bin/python")
CONSOLE = str(REPO / ".venv/bin/agent-arena")
CANDIDATE = "5560e95"
LABEL = "SYNTHETIC TEST FIXTURE — not an empirical model response"
REVIEWER = "TEST ONLY - not a scientific release"
REASON = "v1 closeout Area B evidence; SYNTHETIC TEST FIXTURE"
NETLOG = SCRATCH / "netguard.jsonl"
CMDLOG = SCRATCH / "commands.log"

from agent_arena.phase10_pipeline import OPEN_SENTENCE, OUTCOME_SENTENCES  # noqa: E402
from agent_arena.phase10_projection import TITLES  # noqa: E402
from agent_arena.phase9_models import ReviewPosition  # noqa: E402
from agent_arena.phase9_review import (  # noqa: E402
    _decides_derived_label, _directly_influences_output, _influences_output, _ledger, _states,
)
from tests.test_v1_closeout_report import conflict_fixture, projected  # noqa: E402
from tests.test_v1_semantics import variant  # noqa: E402

CASES = [
    # name, builder description, builder, expected candidate status, expected release status
    ("B1_bounded_optional_conflict", "tests/test_v1_closeout_report.py::conflict_fixture()",
     lambda: conflict_fixture(), "READY_FOR_RELEASE", "RELEASED"),
    ("B2a_material_premise", "tests/test_v1_closeout_report.py::conflict_fixture('premise')",
     lambda: conflict_fixture("premise"), "REVIEW_REQUIRED", "RELEASE_BLOCKED"),
    ("B2b_material_taxonomy_label", "tests/test_v1_closeout_report.py::conflict_fixture('label')",
     lambda: conflict_fixture("label"), "REVIEW_REQUIRED", "RELEASE_BLOCKED"),
    ("B2c_material_decisive_summary", "tests/test_v1_closeout_report.py::conflict_fixture('summary')",
     lambda: conflict_fixture("summary"), "REVIEW_REQUIRED", "RELEASE_BLOCKED"),
    ("VB1_M4b_whole_claim_summary_conflicted_optional",
     "tests/test_v1_semantics.py::variant('M4b_whole_claim_summary_divergent_optional')",
     lambda: variant("M4b_whole_claim_summary_divergent_optional"), "REVIEW_REQUIRED", "RELEASE_BLOCKED"),
    ("VB1_M4d_agreed_unsupported_optional_whole_claim_summary",
     "tests/test_v1_semantics.py::variant('M4d_whole_claim_summary_agreed_unsupported_optional')",
     lambda: variant("M4d_whole_claim_summary_agreed_unsupported_optional"), "ANALYSIS_INCOMPLETE",
     "RELEASE_BLOCKED"),
]
ROWS = ("model/host conflicts", "open cause", "automatic processing", "local release", "review route",
        "review execution", "mandatory review", "scientific judgment", "model judgment (composite)",
        "host evidence derivation (composite)", "analysis execution")
# Phrases that would claim a review, a counterreview or an agreement took place.
CLAIM_PATTERNS = [r"mandatory review executed", r"automatic reviews? executed", r"counterreview", r"\breviewed\b",
                  r"\bagree(?:d|ment|s)?\b", r"resolved by", r"contains no recorded conflicts",
                  r"closed by documented human adjudication", r"case adjudicated", r"review completed",
                  r"mandatory review interrupted"]
# A hit is 'negated/descriptive' when it occurs inside one of these spans (reported separately, never dropped).
NEGATED = [r"not reviewed", r"reviewed source ids", r"reviewed_source_ids"]
P8_RULE_PHRASES = ["mandatory review decides, not either side", "until a mandatory review resolves it"]
TOKENS = ["⟦U+000A⟧", "⟦U+0009⟧", "model-supplied"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scrub(text: str) -> str:
    return text.replace(str(SCRATCH), "<scratch>").replace(str(REPO), "<repo>")


def log(text):
    with open(CMDLOG, "a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def _env(old=None, console=False):
    env = {k: v for k, v in os.environ.items() if k not in {"ANTHROPIC_API_KEY", "OPENAI_API_KEY"}}
    env.update(PYTHONDONTWRITEBYTECODE="1", NETGUARD_LOG=str(NETLOG))
    env.pop("OLD_SRC", None)
    if old:
        env["OLD_SRC"] = str(OLD[old])
    if console:
        env["PYTHONPATH"] = str(TOOLS / "site")
    return env


def cli(args, *, old=None, console=False):
    if console:
        command = [CONSOLE, *args]
        head = "PYTHONPATH=<scratch>/tools/site env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 " \
               "<repo>/.venv/bin/agent-arena "
    else:
        command = [PY, "-B", str(TOOLS / "guarded_cli.py"), *args]
        head = (f"OLD_SRC=<scratch>/{OLD[old].parent.name}/src " if old else "") + \
            "env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY PYTHONDONTWRITEBYTECODE=1 python -B guarded_cli.py "
    shown = head + " ".join(json.dumps(a) if " " in a else a for a in args)
    done = subprocess.run(command, cwd=WORK, env=_env(old, console), capture_output=True)
    stdout, stderr = done.stdout.decode("utf-8", "replace"), done.stderr.decode("utf-8", "replace")
    log(f"$ {scrub(shown)}\n# exit={done.returncode}\n# stderr: "
        + scrub(" | ".join(line for line in stderr.splitlines() if line.strip()))
        + "\n# stdout:\n" + scrub(stdout).rstrip())
    try:
        payload = json.loads(stdout)
    except ValueError:
        payload = None
    return {"exit": done.returncode, "json": payload, "stdout_is_ascii": all(b < 128 for b in done.stdout),
            "stdout_sha256": sha(done.stdout),
            "stderr_agent_arena": scrub(next((l for l in stderr.splitlines() if l.startswith("AGENT_ARENA")),
                                             "console script (no marker line)"))}


class Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.cell, self.texts = [], None, None, []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append("".join(self.cell))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        self.texts.append(data)


def md_row(raw: bytes, field):
    prefix = f"| {field} |".encode()
    hits = [line for line in raw.split(b"\n") if line.startswith(prefix)]
    if not hits:
        return None
    line = hits[0]
    decoded = html.unescape(line.decode("utf-8"))
    cell = decoded[len(f"| {field} | "):-len(" |")]
    return {"raw_line_bytes_utf8": line.decode("utf-8"), "raw_line_sha256": sha(line), "decoded_line": decoded,
            "decoded_value": cell, "occurrences": len(hits)}


def html_row(parser, raw: bytes, field):
    cells = [r for r in parser.rows if r and r[0] == field]
    match = re.search(rb"<tr><td>" + re.escape(html.escape(field, quote=False).encode()) + rb"</td><td>.*?</td></tr>",
                      raw)
    return {"raw_snippet": match.group(0).decode("utf-8") if match else None,
            "decoded_value": cells[0][1] if cells else None, "occurrences": len(cells)}


def materiality(record):
    phase9 = record["run_record"]["metadata"]["phase9"]
    selected = record.get("selected_position_id")
    positions = phase9.get("positions", [])
    stored = next((p for p in positions if p["position_id"] == selected), positions[0] if positions else None)
    if stored is None:
        return {"note": "no stored position"}
    position = ReviewPosition.model_validate(stored)
    ledger, states = _ledger(position), _states(position)
    conflicted = [c.get("proposition_id") for c in position.phase8.get("model_host_conflicts", [])
                  if c.get("scope") != "composite"]
    out = {"position_id": position.position_id, "position_origin": position.origin,
           "selected_position_id_in_record": selected,
           "evaluated_on": "record.json#/run_record/metadata/phase9/positions (selected stored position)",
           "propositions": {}}
    for pid in sorted(set(conflicted) | {p["proposition_id"] for p in position.phase8.get("propositions", [])}):
        entry = {"has_model_host_conflict": pid in conflicted, "derived_state": states.get(pid),
                 "_influences_output": _influences_output(position, pid),
                 "_directly_influences_output": _directly_influences_output(position, pid)}
        entry["_decides_derived_label"] = (_decides_derived_label(position, ledger, states, pid)
                                           if ledger is not None and pid in states else "n/a (no ledger/state)")
        entry["classification"] = "material" if entry["_influences_output"] else "not material"
        out["propositions"][pid] = entry
    return out


def claim_scan(host_texts, md_text, html_text):
    claims = {}
    for pattern in CLAIM_PATTERNS:
        regex = re.compile(pattern, re.I)
        entry = {"projection_host_texts": [t for _, t in host_texts if regex.search(t)]}
        for name, text in (("report_md", md_text), ("report_html", html_text)):
            total, negated = 0, 0
            for match in regex.finditer(text):
                total += 1
                window = text[max(0, match.start() - 12):match.end() + 16]
                if any(re.search(n, window, re.I) for n in NEGATED):
                    negated += 1
            entry[f"{name}_count"] = total
            entry[f"{name}_negated_or_field_name"] = negated
            entry[f"{name}_affirmative"] = total - negated
        claims[pattern] = entry
    return claims


def analyse(path):
    path = Path(path)
    raw_md, raw_html = (path / "report.md").read_bytes(), (path / "report.html").read_bytes()
    record = json.loads((path / "record.json").read_text())
    decision = json.loads((path / "decision.json").read_text())
    run_record = record["run_record"]
    p8 = run_record["results"][0]["agent_result"]["phase8"]
    p9 = run_record["metadata"]["phase9"]
    parser = Rows()
    parser.feed(raw_html.decode("utf-8"))
    html_text = html.unescape("".join(parser.texts))
    md_text = html.unescape(raw_md.decode("utf-8"))
    sections = projected(path)
    table = next(block for title, section in sections if title == TITLES[0] for block in section["blocks"]
                 if block["kind"] == "table" and block["caption"] == "Independent states")
    proj = {row[0]: row[1] for row in table["rows"]}
    host_texts = [(title, block["text"]) for title, section in sections for block in section["blocks"]
                  if block["kind"] == "text"]
    execution_texts = [t for title, t in host_texts if title == TITLES[0]]
    history_texts = [t for title, t in host_texts if title == TITLES[8]]
    rows = {}
    for field in ROWS:
        m, h = md_row(raw_md, field), html_row(parser, raw_html, field)
        rows[field] = {"projection": proj.get(field), "report_md": m, "report_html": h,
                       "three_formats_agree": proj.get(field) == (m or {}).get("decoded_value") ==
                       h.get("decoded_value")}
    status = record["status"]
    expected_sentence = OUTCOME_SENTENCES.get(status, OPEN_SENTENCE)
    # The conflict sentence of the history section is the text block right before the adjudication sentence.
    history_close = [t for t in history_texts if "conflict" in t.lower()][-1:]
    return {
        "bundle_dir": scrub(str(path)),
        "status": status, "execution_mode": record.get("execution_mode"),
        "decision_status": decision.get("status"),
        "failing_controls": [(c["control_id"], c["reason"]) for c in decision["controls"] if c["outcome"] == "fail"],
        "materiality_real_logic": materiality(record),
        "p8": {"technical_status": p8.get("technical_status"), "composite_state": p8.get("composite_state"),
               "model_composite_state": p8.get("model_composite_state"),
               "host_composite_state": p8.get("host_composite_state"),
               "model_host_conflicts": [{k: c.get(k) for k in ("scope", "proposition_id", "model_state",
                                                                "host_state", "reason")}
                                        for c in p8.get("model_host_conflicts", [])],
               "transformation_findings": p8.get("transformation_findings", []),
               "derived_label": (p8.get("taxonomy") or {}).get("derived_label"),
               "reasons_head": p8.get("reasons", [])[:2]},
        "p9": {"route": p9.get("route"), "mandatory": p9.get("mandatory"), "review_state": p9.get("review_state"),
               "execution_status": p9.get("execution_status"), "conflicts": p9.get("conflicts"),
               "attempts": p9.get("attempts", []), "adjudications": p9.get("adjudications", []),
               "triggers": [{k: t.get(k) for k in ("code", "mandatory", "material", "proposition_ids", "field",
                                                   "reason")} for t in p9.get("triggers", [])]},
        "rows": rows,
        "all_rows_agree": all(r["three_formats_agree"] for r in rows.values()),
        "outcome_sentence": {"expected_from_pipeline_constants": expected_sentence,
                             "kind": "OUTCOME_SENTENCES[status]" if status in OUTCOME_SENTENCES else "OPEN_SENTENCE",
                             "in_projection_host_texts": expected_sentence in execution_texts,
                             "in_report_md": expected_sentence in md_text,
                             "in_report_html": expected_sentence in html_text},
        "execution_host_texts": execution_texts,
        "history_closing_sentence": {"projection": history_close,
                                     "in_report_md": [t in md_text for t in history_close],
                                     "in_report_html": [t in html_text for t in history_close]},
        "history_host_texts": history_texts,
        "claim_scan": claim_scan(host_texts, md_text, html_text),
        "review_or_agreement_lines_report_md": [f"{i}: {l[:240]}" for i, l in enumerate(md_text.splitlines(), 1)
                                                if re.search(r"review|agree|adjudicat", l, re.I)],
        "p8_rule_text_residual": {phrase: {"record_json_count": json.dumps(record, ensure_ascii=False).count(phrase),
                                           "report_md_count": md_text.count(phrase),
                                           "report_html_count": html_text.count(phrase)}
                                  for phrase in P8_RULE_PHRASES},
        "display_token_counts": {t: {"report_md": md_text.count(t), "report_html": html_text.count(t)}
                                 for t in TOKENS},
        "files_sha256": {name: sha((path / name).read_bytes()) for name in
                         ("record.json", "decision.json", "report.md", "report.html")},
    }


def materialise():
    FIX.mkdir(parents=True, exist_ok=True)
    index = {"label": LABEL, "generated_from_commit": CANDIDATE, "fixtures": []}
    for name, builder_name, builder, expected, expected_release in CASES:
        task, raw = builder()
        task_bytes = task.model_dump_json(indent=2).encode()
        raw_bytes = raw.encode("utf-8")
        (FIX / f"{name}.task.json").write_bytes(task_bytes)
        (FIX / f"{name}.recording.json").write_bytes(raw_bytes)
        index["fixtures"].append({
            "case": name, "label": LABEL, "builder": builder_name,
            "task_file": f"{name}.task.json", "task_sha256": sha(task_bytes), "task_id": task.id,
            "recording_file": f"{name}.recording.json", "recording_sha256": sha(raw_bytes),
            "record_id": json.loads(raw)["forensic_record"]["record_id"],
            "expected_candidate_status": expected, "expected_release_status": expected_release})
    (FIX / "INDEX.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    (FIX / "LABEL.txt").write_text(LABEL + "\nEvery *.task.json and *.recording.json in this directory is a synthetic "
                                   "test fixture built by the repository test builders named in INDEX.json.\n")
    return index


def run_case(name, old=None, console=False):
    task, recording = FIX / f"{name}.task.json", FIX / f"{name}.recording.json"
    prefix = (f"old{old}__" if old else "") + ("console__" if console else "")
    root = BUNDLES / (prefix + name)
    kw = {"old": old, "console": console}
    out = {"validate": cli(["audit", "validate", "--task", str(task)], **kw)}
    out["run"] = cli(["audit", "run", "--offline", "--task", str(task), "--recording", str(recording),
                      "--output-root", str(root / "candidate")], **kw)
    candidate = (out["run"]["json"] or {}).get("path")
    out["inspect_candidate"] = cli(["audit", "inspect", "--bundle", candidate], **kw) if candidate else None
    out["release"] = cli(["audit", "release", "--bundle", candidate, "--output-root", str(root / "released"),
                          "--reviewer", REVIEWER, "--reason", REASON], **kw) if candidate else None
    released = ((out["release"] or {}).get("json") or {}).get("path")
    out["inspect_released"] = cli(["audit", "inspect", "--bundle", released], **kw) if released else None
    return out, candidate, released


def short(result):
    if not result:
        return None
    payload = result["json"] or {}
    keep = {k: payload.get(k) for k in ("status", "valid", "input_valid", "errors", "release_authorized")
            if k in payload}
    if payload.get("path"):
        keep["path"] = scrub(payload["path"])
    return {"exit": result["exit"], **keep, "stdout_is_ascii": result["stdout_is_ascii"],
            "code": result["stderr_agent_arena"]}


def old_contrast(name, old, detail):
    runs, candidate, released = run_case(name, old=old)
    out = {"commands": {k: short(v) for k, v in runs.items()}}
    if not detail:
        return out
    for label, path in (("candidate", candidate), ("released", released)):
        if not path:
            continue
        raw_md = (Path(path) / "report.md").read_bytes()
        raw_html = (Path(path) / "report.html").read_bytes()
        parser = Rows()
        parser.feed(raw_html.decode("utf-8"))
        md_text = html.unescape(raw_md.decode("utf-8"))
        html_text = html.unescape("".join(parser.texts))
        out[label] = {
            "bundle_dir": scrub(path),
            "rows": {f: {"report_md": md_row(raw_md, f), "report_html": html_row(parser, raw_html, f)}
                     for f in ("model/host conflicts", "open cause", "automatic processing", "local release",
                               "mandatory review", "review route")},
            "history_sentences_md": [line for line in md_text.splitlines()
                                     if "recorded conflicts" in line or "No disagreement" in line
                                     or "not evaluated" in line.lower()],
            "automatic_processing_sentences_md": [line for line in md_text.splitlines()
                                                  if line.startswith("Automatic processing has ended")],
            "phrase_counts": {p: {"report_md": md_text.count(p), "report_html": html_text.count(p)}
                              for p in ["contains no recorded conflicts", "not material for the composite",
                                        "not reviewed", "Automatic processing has ended",
                                        "no blocking cause recorded", "none recorded"] + P8_RULE_PHRASES},
        }
    return out


def console_crosscheck(name, reference):
    runs, candidate, released = run_case(name, console=True)
    out = {"commands": {k: short(v) for k, v in runs.items()}}
    if candidate and released:
        rel = analyse(released)
        out["released_rows_equal_guarded_run"] = {f: rel["rows"][f]["projection"] == reference["rows"][f]["projection"]
                                                  for f in ROWS}
        out["released_report_md_rows"] = {f: rel["rows"][f]["report_md"]["decoded_value"]
                                          for f in ("model/host conflicts", "open cause")}
    return out


INVESTIGATION = Path(str(SCRATCH.parent) + "/B/cli_out/B1b_inconclusive_model_supported")


def investigation_extract():
    """Read-only extract of the investigation bundle at 558e920 (scratch v1/B, equivalent B1 construction)."""
    out = {"source": "<scratch-v1>/B/cli_out/B1b_inconclusive_model_supported (558e920 investigation, read-only)"}
    for label in ("cand", "rel"):
        for bundle in sorted((INVESTIGATION / label).glob("*/report.md")):
            raw = bundle.read_bytes()
            text = raw.decode("utf-8")
            out[label] = {"report_md": str(bundle).replace(str(SCRATCH.parent), "<scratch-v1>"),
                          "report_md_sha256": sha(raw),
                          "lines": [f"{i}: {l}" for i, l in enumerate(text.splitlines(), 1)
                                    if l.startswith(("| model/host conflicts |", "| mandatory review |",
                                                     "| open cause |", "| local release |"))
                                    or "recorded conflicts" in l or l.startswith("Automatic processing")]}
    return out


def build_tar():
    tar_path = SCRATCH / "bundles.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(BUNDLES, arcname="bundles")
    members = []
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                members.append({"path": member.name, "size": member.size,
                                "sha256": sha(tar.extractfile(member).read())})
    (SCRATCH / "bundles_index.json").write_text(json.dumps(
        {"label": LABEL, "archive": "bundles.tar.gz", "archive_sha256": sha(tar_path.read_bytes()),
         "member_count": len(members), "members": members}, indent=2, ensure_ascii=False) + "\n")


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    BUNDLES.mkdir(parents=True, exist_ok=True)
    for stale in (CMDLOG, NETLOG):
        stale.unlink(missing_ok=True)
    index = materialise()
    summary = {"label": LABEL, "candidate_commit": CANDIDATE, "cases": {}}
    for name, _, _, expected, expected_release in CASES:
        runs, candidate, released = run_case(name)
        case = {"expected": {"candidate": expected, "release": expected_release},
                "commands": {k: short(v) for k, v in runs.items()},
                "candidate": analyse(candidate) if candidate else None,
                "released": analyse(released) if released else None}
        release_status = (runs["release"]["json"] or {}).get("status") if runs["release"] else None
        case["observed"] = {"validate_exit": runs["validate"]["exit"],
                            "candidate": (runs["run"]["json"] or {}).get("status"),
                            "inspect_candidate_valid": ((runs["inspect_candidate"] or {}).get("json") or {}).get("valid"),
                            "release": release_status, "release_exit": (runs["release"] or {}).get("exit"),
                            "inspect_released_valid": ((runs["inspect_released"] or {}).get("json") or {}).get("valid"),
                            "all_stdout_ascii": all(v["stdout_is_ascii"] for v in runs.values() if v)}
        case["matches_expectation"] = (case["observed"]["candidate"] == expected and release_status == expected_release)
        summary["cases"][name] = case
    summary["before_after"] = {}
    for old in OLD:
        summary["before_after"][old] = {name: old_contrast(name, old, detail=(name == CASES[0][0]))
                                        for name, *_ in CASES}
    summary["console_script_crosscheck_B1"] = console_crosscheck(
        CASES[0][0], summary["cases"][CASES[0][0]]["released"])
    summary["investigation_558e920_extract"] = investigation_extract()
    summary["fixtures_index"] = index
    summary["netguard_driver_process"] = {"counts": netguard.COUNTS, "total": netguard.total()}
    (SCRATCH / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    build_tar()
    print(json.dumps({n: (c["observed"], c["matches_expectation"]) for n, c in summary["cases"].items()}, indent=1))
    print(json.dumps({o: {n: {k: (v or {}).get("status") for k, v in c["commands"].items()} for n, c in d.items()}
                      for o, d in summary["before_after"].items()}, indent=1))
    print(json.dumps(summary["console_script_crosscheck_B1"], indent=1))


if __name__ == "__main__":
    main()
