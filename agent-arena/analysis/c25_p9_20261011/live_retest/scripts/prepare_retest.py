"""Freeze the AA-P8/1.2 + AA-P9/1.2 live retest: 3 synthetic cases, expectations, the successor
authorization -004 (schema 1.1) bound to the closed -002/-003 ledgers, the frozen scripts and the manifest.

Run from the repository root with the project venv AFTER the tested code is committed:
  .venv/bin/python <draft>/prepare_retest.py            # freeze into analysis/c25_p9_20261011/live_retest
  .venv/bin/python <draft>/prepare_retest.py DRY_DIR    # dry run; the written authorization is made non-executable
Makes no model or provider call and opens no live session (the successor claim is written by the
first live session of -004, not here).
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from agent_arena import phase10_live as live
from agent_arena.phase10_pipeline import REGISTRY
from agent_arena.phase8_models import HOST_RULE_VERSION, Phase8Assessment
from agent_arena.phase9_models import CONTRACT_VERSION as P9_VERSION
from agent_arena.providers.anthropic_live import PROFILES, build_user_message, max_exposure_microusd
from agent_arena.runner import resolve_study_forensics_prompt
from agent_arena.schemas import Task

ROOT = Path.cwd()
DEFAULT_OUT = ROOT / "analysis/c25_p9_20261011/live_retest"
DRY_RUN = len(sys.argv) > 1
OUT = Path(sys.argv[1]).resolve() if DRY_RUN else DEFAULT_OUT
DRAFT = Path(__file__).resolve().parent
BASE = ROOT / "analysis/live_smoke_20261011"
PREDECESSORS = (("AA-P10-LIVE-SMOKE-20261011-002", BASE / "live_run"),
                ("AA-P10-LIVE-SMOKE-20261011-003", BASE / "repair_r1"))
NEW_ID = "AA-P10-LIVE-RETEST-20261011-004"
WORK_ORDER = "AGENT ARENA — C25 korrigieren, verpflichtende P9-Konfliktprüfung und Gesamtdiagnose P1–P10 (11.10.2026)"
PROFILE_IDS = ("claude-haiku-5-5@3", "claude-sonnet-5-5@3")
ORDER_ATTEMPTS, ORDER_RETRIES, PER_CALL = 12, 2, 300_000
SYNTHETIC = "synthetic sketch written for this retest; not a real study, not a library case, no gold label"
SCRIPTS = ("run_retest.py", "summarize_retest.py", "replay_retest.py", "close_retest.py")
EXPECTATIONS = json.loads((DRAFT / "expectations.json").read_text())

CASES = {
    "LR-01": {
        "role": "supported: a randomized between-group comparison whose population, intervention, comparator, "
                "endpoint and horizon are worded identically in claim and source (template sibling of LS-01's "
                "positive-control role on a new topic)",
        "prompt": ("In a randomized trial, community-dwelling adults aged 70 and older assigned to a home-based "
                   "balance training program had fewer falls over twelve months than those assigned to general "
                   "health advice."),
        "context": ("Researchers randomly assigned community-dwelling adults aged 70 and older (600 in total) either "
                    "to a home-based balance training program or to general health advice. The program consisted "
                    "of three short sessions per week. Falls were counted in the same way in both groups. Over "
                    "twelve months, community-dwelling adults aged 70 and older assigned to the home-based balance "
                    "training program had 31 percent fewer falls than those assigned to general health advice, and "
                    "the difference was statistically significant."),
    },
    "LR-02": {
        "role": "clearly unsupported with sufficient evidence: a single cross-sectional association used for a causal, "
                "longitudinal claim (shares the observational-confounding element of LS-06, without its RCT)",
        "prompt": "Drinking green tea daily prevents memory decline in adults aged 65 and older.",
        "context": ("A one-time survey of 2,000 adults aged 65 and older asked about tea habits and gave each person "
                    "a single memory test. People who reported drinking green tea daily scored slightly higher on "
                    "that test than people who rarely drank it; daily tea drinkers were also more physically active "
                    "and more often had completed higher education, and the comparison was not adjusted for these "
                    "differences."),
    },
    "LR-03": {
        "role": "conflict-capable: a before-after change in one group with a stated confounder and no comparison "
                "figures; unsupported versus unknown is a genuine judgment call (same trap template as library "
                "case 063, a before-after policy change with a concurrent confounder and no comparison group, and "
                "topic close to library case 022; different topic and wording, copied from neither)",
        "prompt": "At a logistics company, introducing a four-day working week reduced recorded sick days among "
                  "office staff.",
        "context": ("A logistics company introduced a four-day working week for all office staff in January. In its "
                    "annual report, the company stated that recorded sick days among office staff were 20 percent "
                    "lower that year than in the previous year. The report notes that a severe influenza season had "
                    "affected the previous year and gives no sick-day figures for staff who kept a five-day week."),
    },
}
ORDER = [("claude-haiku-5-5@3", "LR-03"), ("claude-haiku-5-5@3", "LR-01"), ("claude-haiku-5-5@3", "LR-02"),
         ("claude-sonnet-5-5@3", "LR-03"), ("claude-sonnet-5-5@3", "LR-01"), ("claude-sonnet-5-5@3", "LR-02")]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def task_for(case):
    spec = CASES[case]
    return Task(id=f"aa-p10-live-retest-{case}", title=f"AA-P10 live retest {case} ({SYNTHETIC})",
                domain="study_forensics", difficulty="medium", task_type="study_forensics",
                prompt=spec["prompt"], context=spec["context"])


def main():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip():
        sys.exit("tracked tree is not clean; commit the tested code first")
    if OUT.exists():
        sys.exit("retest directory exists; a frozen retest is never rewritten")
    if (PREDECESSORS[-1][1] / live.SUCCESSOR_CLAIM).exists():
        sys.exit("-003 already carries a successor claim; refusing to prepare another successor")
    predecessors, consumed, attempts, retries = [], 0, 0, 0
    for auth_id, directory in PREDECESSORS:
        ledger = json.loads((directory / "ledger.json").read_text())
        assert ledger["state"] == "REVOKED" and ledger["executable_remaining_microusd"] == 0
        assert sha(directory / "ledger.json") == live.KNOWN_CLOSED_AUTHORIZATIONS[auth_id]["ledger_sha256"]
        used = sum(1 for a in ledger["attempts"] if a.get("retry_of"))
        predecessors.append({"authorization_id": auth_id, "directory": str(directory.resolve()),
                             "ledger_sha256": sha(directory / "ledger.json"),
                             "consumed_microusd": ledger["reserved_microusd"], "attempts": len(ledger["attempts"]),
                             "technical_retries": used})
        consumed += ledger["reserved_microusd"]
        attempts += len(ledger["attempts"])
        retries += used
    budget = live.CEILING_TOTAL_MICROUSD - consumed
    assert attempts + ORDER_ATTEMPTS <= live.CEILING_ATTEMPTS and retries + ORDER_RETRIES <= live.CEILING_RETRIES
    tasks = {case: task_for(case) for case in CASES}
    OUT.mkdir(parents=True)
    (OUT / "tasks").mkdir()
    for case, task in tasks.items():
        (OUT / "tasks" / f"{case}.json").write_text(json.dumps(task.model_dump(mode="json"), indent=2,
                                                               ensure_ascii=False) + "\n")
    (OUT / "scripts").mkdir()
    for name in SCRIPTS:
        shutil.copy2(DRAFT / name, OUT / "scripts" / name)
    shutil.copy2(DRAFT / "prepare_retest.py", OUT / "scripts" / "prepare_retest.py")
    (OUT / "expectations.json").write_bytes((DRAFT / "expectations.json").read_bytes())
    auth = {
        "schema": live.AUTH_SCHEMA_SUCCESSOR, "authorization_id": NEW_ID, "work_order": WORK_ORDER,
        "issued_at": "2026-10-12T00:00:00+00:00", "expires_at": "2026-10-15T00:00:00+00:00", "status": "ACTIVE",
        "canonical_directory": str(OUT.resolve()), "endpoint": live.LIVE_ENDPOINT,
        "total_budget_microusd": budget, "max_generation_attempts": ORDER_ATTEMPTS,
        "max_technical_retries": ORDER_RETRIES, "max_attempts_per_request": 2, "per_call_ceiling_microusd": PER_CALL,
        "allowed_profiles": {pid: PROFILES[pid].fingerprint() for pid in PROFILE_IDS},
        "task_bindings": {t.id: live.task_sha256(t) for t in tasks.values()},
        "slots": [live.slot_key(t.id, pid, kind) for t in tasks.values() for pid in PROFILE_IDS for kind in live.KINDS],
        "supersedes": {
            "prior_authorization_id": PREDECESSORS[-1][0], "state": "CLOSED_ORDER_COMPLETE",
            "prior_ledger_sha256_after_closure": predecessors[-1]["ledger_sha256"],
            "reason": ("-003 was closed as ORDER_COMPLETE (its remainder was not carried over by that order). The work "
                       "order of 11.10.2026 explicitly re-authorizes exactly the old remainder for this retest: "
                       f"{budget} microUSD, {ORDER_ATTEMPTS} attempts, {ORDER_RETRIES} technical retries, within the "
                       "cumulative ceilings. -002/-003 stay closed and replayable; no other budget exists.")},
        "predecessors": predecessors,
        "review_caps": {pid: {"counterreview": 1, "stability": 1} for pid in PROFILE_IDS},
    }
    (OUT / "authorization.json").write_text(json.dumps(auth, indent=2, ensure_ascii=False) + "\n")
    completed = False
    try:
        freeze(auth, tasks, commit, predecessors, consumed, attempts, retries, budget)
        completed = True
    finally:
        if DRY_RUN or not completed:
            # A dry-run or failed preparation must never leave an executable authorization: it would claim
            # -003 for this directory on its first live session. Rewritten before anything else can use it.
            auth["status"] = "DRY_RUN_NOT_EXECUTABLE" if DRY_RUN else "PREPARE_FAILED_NOT_EXECUTABLE"
            (OUT / "authorization.json").write_text(json.dumps(auth, indent=2, ensure_ascii=False) + "\n")


def freeze(auth, tasks, commit, predecessors, consumed, attempts, retries, budget):
    _, fingerprint = live.load_authorization(OUT)  # read-only validation incl. the predecessor chain
    exposure, review_reserve = {}, {}
    for pid in PROFILE_IDS:
        primary_v, review_v = PROFILES[pid].prompt_versions
        for case, task in tasks.items():
            user = build_user_message(task)
            primary, _ = max_exposure_microusd(PROFILES[pid], resolve_study_forensics_prompt(primary_v), user)
            # Conservative counterreview reserve: review prompt, 4x the user message plus 20,000 bytes for the
            # conflict packet (positions, reasons, evidence), full max_tokens output.
            review, _ = max_exposure_microusd(PROFILES[pid], resolve_study_forensics_prompt(review_v),
                                              user * 4 + "x" * 20_000)
            exposure[f"{pid}|{case}"] = primary
            review_reserve[f"{pid}|{case}"] = review
            assert primary <= PER_CALL and review <= PER_CALL, (pid, case, primary, review)
    p8_version = Phase8Assessment.model_fields["contract_version"].default
    manifest = {
        "schema": "aa-p10-live-retest-manifest/1.1",
        "contract": {"evaluation": p8_version, "review": P9_VERSION, "host_rule_version": HOST_RULE_VERSION,
                     "model_output_format": "AA-P8/1.0 ledger (unchanged)",
                     "prompts": list(PROFILES[PROFILE_IDS[0]].prompt_versions),
                     "registry": {k: REGISTRY[k] for k in ("input_preflight", "evidence_symmetry",
                                                           "phase8_semantics_taxonomy", "phase9_history_review")},
                     "documents": "docs/phase8_9_conflict_addendum.md §2-§8, docs/phase10_live_addendum.md"},
        "authorization_id": NEW_ID, "authorization_sha256": fingerprint, "tested_code_commit": commit,
        "cases": [{"case_id": c, "task_id": t.id, "role": CASES[c]["role"], "label": SYNTHETIC,
                   "task_file": f"tasks/{c}.json", "task_file_sha256": sha(OUT / "tasks" / f"{c}.json"),
                   "task_sha256": live.task_sha256(t)} for c, t in tasks.items()],
        "expectations_file": "expectations.json", "expectations_sha256": sha(OUT / "expectations.json"),
        "scripts": {f"scripts/{name}": sha(OUT / "scripts" / name) for name in (*SCRIPTS, "prepare_retest.py")},
        "profiles": {pid: {"fingerprint": PROFILES[pid].fingerprint(), "prompt_versions": list(PROFILES[pid].prompt_versions),
                           "prompt_sha256": [hashlib.sha256(resolve_study_forensics_prompt(v).encode()).hexdigest()
                                             for v in PROFILES[pid].prompt_versions],
                           "max_tokens": PROFILES[pid].max_tokens} for pid in PROFILE_IDS},
        "budget": {"order_total_microusd": live.CEILING_TOTAL_MICROUSD, "predecessor_consumed_microusd": consumed,
                   "authorized_microusd": budget, "per_call_ceiling_microusd": PER_CALL,
                   "attempts": {"predecessors": attempts, "this_order_max": ORDER_ATTEMPTS, "ceiling": live.CEILING_ATTEMPTS},
                   "technical_retries": {"predecessors": retries, "this_order_max": ORDER_RETRIES,
                                         "ceiling": live.CEILING_RETRIES},
                   "review_caps_per_profile": {"counterreview": 1, "stability": 1},
                   "max_primary_exposure_microusd": exposure,
                   "counterreview_reserve_microusd": review_reserve},
        "call_plan": {
            "order": [f"{pid} {case}" for pid, case in ORDER],
            "rules": [
                "Fixed order; at most 6 primary slots; a skipped or denied slot is never reallocated.",
                "Pre-checks before the first call: src at HEAD equals tested_code_commit and src has no uncommitted or "
                "untracked change; the frozen retest files (authorization.json, manifest.json, expectations.json, "
                "tasks/, scripts/) are committed and unchanged at HEAD, and the freeze commit is logged; the "
                "authorization, task, expectations and script hashes equal this manifest; the provider key is present "
                "in the runner's environment (presence only, never printed); -003 carries no successor claim or "
                "exactly this one.",
                "Single start: one runner process at a time (exclusive runner lock). The runner refuses to start when "
                "the -004 ledger is not ACTIVE or records any attempt or review allowance claim. A restart is permitted "
                "only while the ledger is absent or ACTIVE with zero attempts and zero claims (for example after failed "
                "pre-checks); it is logged, and the summary evaluates only the records after the last start whose "
                "pre-checks passed.",
                "Reserve rule (cap-aware): before each primary the remaining executable budget must cover the primary "
                "maximal exposure plus, while the profile's counterreview allowance is still unclaimed in the ledger, "
                "the counterreview reserve. Otherwise this primary is skipped (not executed) with the logged cause, "
                "and later primaries are checked again under the same rule. The inputs are logged for every primary.",
                "Reviews run only through the canonical P10 path: on REVIEW_RECOMMENDED of a technically complete "
                "analysis the mandatory counterreview, then, only if it completed, the single stability variant "
                "(evidence order reversed; a reversal that changes nothing is rejected as a no-op without a call, and "
                "its claimed allowance counts as used). Per profile at most 1 counterreview and 1 stability "
                "(authorization review_caps). A review that is denied, rejected, failed or not sent leaves the case "
                "UNRESOLVED (status REVIEW_REQUIRED).",
                "At most 1 technical retry per request and 2 in total (ledger); no retry for content.",
                "Stop rule: after each slot the runner reads that slot's new ledger attempts and stops the whole run "
                "(remaining slots logged as not run) on any FAILED_PERMANENT attempt, any attempt still "
                "RESERVED_POSSIBLY_BILLABLE, any overrun, a request whose final attempt is FAILED_TRANSIENT without a "
                "permitted retry left (its retry was not granted, or 2 of 2 order-wide retries are used), a ledger "
                "that is not ACTIVE, or a result without a bundle (status None, PREFLIGHT_BLOCKED or RELEASE_BLOCKED, "
                "or no path).",
                "Not a stop: a 429/529/5xx/timeout/connection failure that persists after its single retry while an "
                "order-wide retry remains is a technical slot failure (PARTIAL) and the run continues; refusal, "
                "truncation, missing text, ANALYSIS_INCOMPLETE and REVIEW_REQUIRED are model or process outcomes.",
                "Overrun: the per-call ceiling is enforced before sending by the maximal-exposure reservation "
                "(max_tokens bound); the ledger revokes itself when confirmed cost exceeds the authorized total. An "
                "overrun is detected by the runner only after its slot, so that slot's own review calls may already "
                "have been sent; any overrun is reported as a breach of the work-order limits.",
                "An interrupted run counts as PARTIAL and is not resumed (single start); an unresolved reservation "
                "stays bound; the interrupted case is documented from the ledger and, where a terminal capture "
                "exists, by offline replay.",
                "The runner is started detached (background) and monitored; it is never run inside a foreground "
                "tool timeout. Each request has the profile's 300 s client timeout and no SDK retry; the runner adds "
                "no subprocess timeout, because killing a running CLI would leave an unresolved reservation."]},
        "evaluation_rule": EXPECTATIONS["evaluation_rule"],
        "p9_reporting": EXPECTATIONS["p9_reporting"],
        "release_policy": ("A test release is attempted once per READY_FOR_RELEASE or REVIEW_REQUIRED bundle with reviewer "
                           "'TEST ONLY - not a scientific release' and a reason naming the synthetic case, and its "
                           "result is recorded once in evidence/test_releases.json; a bundle with an open mandatory "
                           "review or material conflict must stay RELEASE_BLOCKED."),
        "recording": ["transport (http status, request id, error type)", "format/parse", "evidence completeness",
                      "model judgment", "host state, host reasons and host route", "conflict (material/bounded)",
                      "P9 route and real review calls, counterreview and stability outcomes separately",
                      "the four P9 statuses (routing reached, model call made, response processed, conflict)",
                      "review resolution", "bundle integrity", "release", "tokens", "cost and overrun", "latency"],
        "replay_target": ("the first slot in the fixed order with a sent live review request; else the first slot in "
                          "the fixed order with a terminal primary capture (normally Haiku LR-03); chosen by "
                          "replay_retest.py from the ledger"),
        "after_run": [
            "close_retest.py immediately after the runner has ended: closes -004 by a direct ledger revoke with an "
            "ORDER_COMPLETE reason under the lease (as -003 was closed; after expires_at under the lease file without "
            "a live session); unresolved reservations stay bound; an already REVOKED ledger counts as closed; while "
            "a live process still holds the lease it refuses and writes nothing; evidence/closure.json is written "
            "once and later checks are appended to evidence/closure_checks.jsonl; replay stays possible",
            "replay_retest.py with the installed wheel of tested_code_commit (offline; SCRATCH_DIR outside the "
            "repository; writes evidence/replay_check.json after the comparison, also when the replay fails)",
            "summarize_retest.py (offline; per-attempt and per-slot evidence, expectation checks, P9 statuses, test "
            "releases recorded once in evidence/test_releases.json; includes closure.json and replay_check.json; "
            "re-runnable)",
            "evidence commit: the whole retest directory including evidence/, plus "
            "analysis/live_smoke_20261011/repair_r1/successor_claim.json (the O_EXCL binding of -004 to -003, written "
            "by the first live session of -004)"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"authorization": NEW_ID, "dry_run": DRY_RUN, "budget_microusd": budget,
                      "authorization_sha256_at_validation": fingerprint, "primary_exposure": exposure,
                      "counterreview_reserve": review_reserve}, indent=1))
    return fingerprint


if __name__ == "__main__":
    main()
