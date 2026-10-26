"""Area C post-processing: control extract, help/message checks, bundle archive + index, guard count aggregate.
Reads only the scratch outputs; makes no network or provider call."""
import glob, hashlib, io, json, os, re, sys, tarfile

S = "__LOCAL_AGENT_SCRATCH__/-PUBLIC-HOME-Documents-Projects-agent-arena/cda624d0-c2aa-47a5-842e-e471afe176b7/scratchpad/v1/evidence-C"
O, C, SP = f"{S}/out", f"{S}/counts", f"{S}/work/supported"
sha = lambda b: hashlib.sha256(b).hexdigest()
txt = lambda n: open(f"{O}/{n}.txt", encoding="utf-8").read()
flat = lambda s: " ".join(s.split())
rc = lambda n: int(re.search(r"--- exit_code: (\d+)\s*$", txt(n)).group(1))

# 1. controls of candidate and release
lines, controls = [], {}
for d in sorted(glob.glob(f"{SP}/*/*/decision.json")):
    j = json.load(open(d)); kind = d.split("/")[-3]
    cs = [(c.get("control_id") or c.get("id"), c.get("execution"), c.get("outcome"), c.get("version")) for c in j["controls"]]
    controls[kind] = {"status": j["status"], "controls": cs, "release_intent": j.get("release_intent")}
    lines.append(f"{kind} {j['status']} {cs} {j.get('release_intent')}")
    md = open(os.path.join(os.path.dirname(d), "report.md"), encoding="utf-8").read()
    for l in md.splitlines():
        if l.startswith("| open cause") or l.startswith("Automatic processing") or l.startswith("| automatic processing"):
            lines.append(f"  report.md: {l}")
open(f"{O}/supported_path_controls.txt", "w").write(
    "# kind status [(control_id, execution, outcome, version)] release_intent; then report.md state lines\n" + "\n".join(lines) + "\n")

# 2. checks
checks = {
  "help_root_names_audit_as_v1_path": "Supported v1 path: 'agent-arena audit'" in flat(txt("help_root")),
  "help_root_marks_run_and_official_release_disabled": flat(txt("help_root")).count("[disabled in v1]") == 2,
  "help_run_states_disabled_in_v1": "Disabled in v1:" in flat(txt("help_run")),
  "help_official_release_states_disabled_in_v1": "Disabled in v1:" in flat(txt("help_official_release")),
  "help_audit_run_profile_example_is_at3": "claude-haiku-5-5@3" in txt("help_audit_run") and "claude-haiku-5-5@1" not in txt("help_audit_run"),
  "help_forensic_report_marked_not_v1": "Not the canonical Phase10 path" in flat(txt("help_forensic_report")),
  "help_run_library_states_historical": "Historical research harness; not an AA-P10/v1 audit or release." in flat(txt("help_run_library")),
  "run_anthropic_exit2_v1_message": rc("run_rejected_anthropic") == 2 and "is disabled in v1" in flat(txt("run_rejected_anthropic")),
  "run_yaml_exit2_v1_message": rc("run_rejected_yaml") == 2 and "is disabled in v1" in flat(txt("run_rejected_yaml")),
  "official_release_exit2_v1_message": rc("official_release_rejected") == 2 and "is disabled in v1" in flat(txt("official_release_rejected")),
  "rejected_cwds_empty": all(not os.listdir(f"{S}/work/{d}") for d in ("cwd_run_anthropic", "cwd_run_yaml", "cwd_official")),
  "official_output_root_not_created": not os.path.exists(f"{S}/work/official_out"),
  "audit_cli_json_is_ascii": all(txt(n).isascii() for n in ("audit_validate", "audit_run_offline", "audit_inspect_candidate", "audit_release", "audit_inspect_release")),
  "guarded_help_identical_to_console_script": all(txt(f"help_{p}").split("--- output (stdout+stderr) ---")[1] == txt(f"guarded_help_{p}").split("--- output (stdout+stderr) ---")[1] for p in ("root", "run_library")),
}
statuses = {}
for n in ("audit_validate", "audit_run_offline", "audit_inspect_candidate", "audit_release", "audit_inspect_release"):
    body = txt(n).split("--- output (stdout+stderr) ---\n")[1].rsplit("--- exit_code:", 1)[0]
    j = json.loads(body); statuses[n] = {"exit_code": rc(n), **{k: j[k] for k in ("status", "valid", "input_valid", "release_authorized") if k in j}, "errors": j.get("errors")}
for n in ("pytest_test_release_boundary", "pytest_test_v1_entry_point"):
    statuses[n] = {"exit_code": rc(n), "summary": re.findall(r"^(\d+ passed.*)$", txt(n), re.M)[-1]}

# 3. guard counts
counts = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(f"{C}/*.json"))}
total = {}
for k, v in counts.items():
    if k == "canary": continue
    for ck, cv in v["counts"].items(): total[ck] = total.get(ck, 0) + cv
json.dump({"note": "Refusing counters per guarded invocation (guard_cli.py) and per pytest session (areac_netguard.py). "
           "Expected 0 everywhere except the canary self-test, which must count each patched path.",
           "invocations": counts, "total_excluding_canary": total}, open(f"{O}/guard_counts.json", "w"), indent=1)

# 4. bundle archive + index (members byte-checked against sources)
members = sorted(os.path.relpath(p, SP) for p in glob.glob(f"{SP}/*/*/*") if os.path.isfile(p))
arc = f"{O}/supported_path_bundles.tar.gz"
with tarfile.open(arc, "w:gz", format=tarfile.PAX_FORMAT) as tf:
    for m in members:
        ti = tf.gettarinfo(f"{SP}/{m}", arcname=m); ti.uid = ti.gid = 0; ti.uname = ti.gname = ""; ti.mtime = 0
        tf.addfile(ti, open(f"{SP}/{m}", "rb"))
idx = []
with tarfile.open(arc, "r:gz") as tf:
    for m in members:
        b = tf.extractfile(m).read(); src = open(f"{SP}/{m}", "rb").read()
        assert b == src, m
        idx.append({"path": m, "bytes": len(b), "sha256": sha(b)})
json.dump({"archive": "supported_path_bundles.tar.gz", "archive_sha256": sha(open(arc, "rb").read()),
           "source": "audit run --offline (examples/phase10/positive-task.json + positive-recording.json) and audit release, area C evidence, candidate 5560e95",
           "note": "Example recording shipped in the repo (examples/phase10); offline, no model call. Each member was checked byte-equal to its source. Loose report.md is not committed because it trips git diff --check.",
           "members": idx}, open(f"{O}/supported_path_bundles.index.json", "w"), indent=2)

res = {"checks": checks, "statuses": statuses, "controls": {k: {"status": v["status"], "n": len(v["controls"]),
       "pass": sum(1 for c in v["controls"] if c[2] == "pass"), "not_applicable": [c[0] for c in v["controls"] if c[2] == "not_applicable"],
       "not_executed": [c[0] for c in v["controls"] if c[1] != "executed"]} for k, v in controls.items()}, "guard_total_excluding_canary": total,
       "canary": counts["canary"]["counts"]}
json.dump(res, open(f"{S}/post_result.json", "w"), indent=1)
print(json.dumps(res, indent=1))
sys.exit(0 if all(checks.values()) else 1)
