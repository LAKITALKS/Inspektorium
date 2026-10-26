"""Reproduce a committed checkout using an isolated installed package, offline.

Creates a committed clone and wheel environment for canonical operation. A separate
fresh editable environment runs source-bound development tests when requested.
Durable logs and artifact evidence live under --output. No developer PYTHONPATH.
Dependency downloads are permitted; runtime model APIs are not used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

REPRODUCTION_VERSION = "AA-P10-REPRO/1.2"


def guard_countercheck_valid(check, records):
    negative = [v for k, v in check.items()
                if k not in ("armed", "loopback_positive_control")]
    return (check.get("armed") is True
            and check.get("loopback_positive_control") == "connected"
            and len(negative) == 5
            and all(v == "refused_by_guard" for v in negative)
            and any(row.get("event") == "armed" for row in records)
            and sum(row.get("event") == "refused" for row in records) == 5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--full-suite", action="store_true")
    args = parser.parse_args()
    repo, scratch, output = args.repo.resolve(), args.scratch.resolve(), args.output.resolve()
    scratch.mkdir(parents=True, exist_ok=False)
    output.mkdir(parents=True, exist_ok=False)
    checkout, venv = scratch / "checkout", scratch / "venv"
    git_root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                          cwd=repo, text=True).strip()).resolve()
    component = checkout / repo.relative_to(git_root)
    environment = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "PYTEST_ADDOPTS", "PYTEST_PLUGINS",
                "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        environment.pop(key, None)
    transcript = []

    def run(command, name, *, cwd=None, expected=0):
        print(name, flush=True)
        result = subprocess.run([str(c) for c in command], cwd=cwd or component,
                                env=environment, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        (output / (name + ".log")).write_text(result.stdout)
        transcript.append({"name": name, "command": [str(c) for c in command],
                           "cwd": str(cwd or component), "exit_code": result.returncode})
        (output / "commands.json").write_text(json.dumps(transcript, indent=2) + "\n")
        if result.returncode != expected:
            raise RuntimeError(f"{name}: exit {result.returncode}, expected {expected}; see durable log")
        return result.stdout

    def arm_and_check(target, label):
        site = Path(run([target / "bin/python", "-c",
                         "import sysconfig; print(sysconfig.get_path('purelib'))"],
                        label + "-site").strip())
        guard_source = component / "scripts/offline_netguard.py"
        (site / "evidence_netguard.py").write_bytes(guard_source.read_bytes())
        (site / "evidence_netguard.pth").write_text("import evidence_netguard\n")
        environment["EVIDENCE_NETGUARD_LOG"] = str(output / (label + "-canary-network.jsonl"))
        check = json.loads(run([target / "bin/python", "scripts/offline_canary.py"],
                               label + "-canary"))
        records = [json.loads(line) for line in
                   (output / (label + "-canary-network.jsonl")).read_text().splitlines()]
        if not guard_countercheck_valid(check, records):
            raise RuntimeError("Network guard countercheck failed")
        environment["EVIDENCE_NETGUARD_LOG"] = str(output / "offline-network.jsonl")

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    run(["git", "clone", "--quiet", "--no-hardlinks", "--no-checkout", git_root, checkout],
        "clone", cwd=scratch)
    run(["git", "checkout", "--quiet", "--detach", commit], "checkout", cwd=checkout)
    assert not run(["git", "status", "--porcelain"], "initial-status").strip()
    run([sys.executable, "-m", "venv", venv], "venv")
    python, cli = venv / "bin/python", venv / "bin/agent-arena"
    run([python, "-m", "pip", "install", ".[dev,providers]"], "install")
    arm_and_check(venv, "wheel")
    origin = run([python, "-c", "import agent_arena,sys; print(agent_arena.__file__); print(sys.version)"], "installed-origin")
    if str(venv) not in origin or str(repo / "src") in origin:
        raise RuntimeError("Package did not import from the clean environment")
    installed_code = json.loads(run([python, "-c",
        "import json; from agent_arena.phase10_pipeline import code_identity; print(json.dumps(code_identity()))"],
        "installed-code"))
    source_hashes = {p.relative_to(component / "src/agent_arena").as_posix():
                     hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (component / "src/agent_arena").rglob("*.py")}
    if installed_code["module_hashes"] != source_hashes:
        raise RuntimeError("Installed module bytes differ from the clean source checkpoint")
    packages = run([python, "-m", "pip", "freeze"], "installed-packages")
    constraints = output / "wheel-dependency-constraints.txt"
    constraints.write_text("\n".join(line for line in packages.splitlines() if "==" in line) + "\n")
    run([cli, "audit", "--help"], "cli-help")
    examples = component / "examples/phase10"
    run([cli, "audit", "validate", "--task", examples / "positive-task.json"], "validate")
    bundles = output / "cli-bundles"

    def cli_run(name, expected=0):
        return json.loads(run([cli, "audit", "run", "--offline", "--task", examples / f"{name}-task.json",
                               "--recording", examples / f"{name}-recording.json", "--output-root", bundles],
                              "run-" + name, expected=expected))

    def release(path, name):
        return json.loads(run([cli, "audit", "release", "--bundle", path, "--output-root", bundles,
                               "--reviewer", "Clean-checkout offline operator", "--reason",
                               "Explicit synthetic local artifact release for installation verification"], name))

    for name in ("positive", "negative"):
        candidate = cli_run(name)
        assert candidate["status"] == "READY_FOR_RELEASE"
        final = release(candidate["path"], "release-" + name)
        assert final["status"] == "RELEASED"
        run([cli, "audit", "inspect", "--bundle", final["path"]], "inspect-" + name)
    unknown = cli_run("unknown", 2)
    assert unknown["status"] == "REVIEW_REQUIRED"
    run([cli, "audit", "inspect", "--bundle", unknown["path"]], "inspect-blocked")
    run([cli, "audit", "release", "--bundle", unknown["path"], "--output-root", bundles,
         "--reviewer", "Offline operator", "--reason", "Test refusal"], "release-blocked", expected=2)
    record = json.loads((Path(unknown["path"]) / "record.json").read_text())
    position = record["run_record"]["metadata"]["phase9"]["positions"][0]["position_id"]
    corrected = json.loads(run([cli, "audit", "review", "--bundle", unknown["path"], "--output-root", bundles,
                               "--state-dir", output / "human-state", "--select", position,
                               "--reviewer", "Clean-checkout offline operator", "--reason",
                               "Resolve represented design uncertainty from supplied source", "--correction",
                               examples / "positive-recording.json"], "human-review"))
    final = release(corrected["path"], "release-human-review")
    run([cli, "audit", "inspect", "--bundle", final["path"]], "inspect-human-review")
    run([python, "scripts/phase10_acceptance.py", "--output", output / "acceptance"], "acceptance")
    run([python, "-m", "ruff", "check", *sorted(str(p.relative_to(component)) for p in
         (component / "src/agent_arena").glob("phase10_*.py")), "src/agent_arena/cli.py",
         *sorted(str(p.relative_to(component)) for p in (component / "tests").glob("test_phase10_*.py")),
         "scripts/phase10_acceptance.py", "scripts/phase10_clean_reproduce.py",
         "scripts/phase10_print_qa.py", "src/agent_arena/condition_contract.py",
         "scripts/extract_recorded_capture.py", "scripts/offline_netguard.py",
         "scripts/offline_canary.py", "tests/test_capture_derivation.py",
         "tests/test_monorepo_plan_binding.py", "tests/test_reproduction_guard_counter.py"], "ruff")
    run([python, "-m", "compileall", "-q", "src/agent_arena"], "compileall")
    run(["git", "diff", "--check"], "diff-check")
    run([python, "-m", "pytest", "-q", "tests/test_phase10_bundle.py",
         "tests/test_phase10_render.py"], "wheel-phase10-tests")
    development = None
    if args.full_suite:
        development_venv = scratch / "development-venv"
        run([sys.executable, "-m", "venv", development_venv], "development-venv")
        development_python = development_venv / "bin/python"
        run([development_python, "-m", "pip", "install", "-c", constraints,
             "-e", ".[dev,providers]"], "development-install")
        arm_and_check(development_venv, "development")
        development_origin = run([development_python, "-c",
            "import agent_arena,sys; print(agent_arena.__file__); print(sys.version)"],
            "development-origin")
        if Path(development_origin.splitlines()[0]).resolve() != component / "src/agent_arena/__init__.py":
            raise RuntimeError("Development install is not bound to the isolated clone")
        development_code = json.loads(run([development_python, "-c",
            "import json; from agent_arena.phase10_pipeline import code_identity; print(json.dumps(code_identity()))"],
            "development-code"))
        if development_code["module_hashes"] != source_hashes:
            raise RuntimeError("Development module bytes differ from the committed checkpoint")
        run([development_python, "-m", "pip", "freeze"], "development-packages")
        run([development_python, "-m", "pytest", "-q"], "full-suite")
        development = {"installation": "editable_same_clean_commit",
                       "environment": str(development_venv), "origin": development_origin.strip(),
                       "module_bytes_match_source": True,
                       "code_fingerprint": development_code["code_fingerprint"]}
    if source_hashes != {p.relative_to(component / "src/agent_arena").as_posix():
                         hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (component / "src/agent_arena").rglob("*.py")}:
        raise RuntimeError("Source bytes changed during validation")
    final_status = run(["git", "status", "--porcelain"], "final-status")
    if final_status.strip():
        raise RuntimeError("The clean checkout was modified during validation")
    network = [json.loads(line) for line in
               (output / "offline-network.jsonl").read_text().splitlines()]
    armed = sum(row.get("event") == "armed" for row in network)
    refused = sum(row.get("event") == "refused" for row in network)
    if not armed or refused:
        raise RuntimeError("Missing monitoring or a refused operation in the offline run")
    (output / "reproduction.json").write_text(json.dumps({
        "reproduction_version": REPRODUCTION_VERSION,
        "wheel_installation": "normal_noneditable", "development": development,
        "source_commit": commit, "checkout": str(checkout), "environment": str(venv),
        "python_creator": sys.version, "platform": platform.platform(),
        "installed_origin": origin.strip(), "full_suite_executed": args.full_suite,
        "installed_code_fingerprint": installed_code["code_fingerprint"],
        "installed_bytes_match_source": True,
        "final_checkout_status": final_status,
        "network_monitor": {"armed_records": armed, "refused_operations": refused,
                            "scope": "Python socket hook in installed execution environments; "
                                     "setup downloads and native networking are outside this measure"},
        "runtime_mode": "recorded_offline", "success": True,
    }, indent=2) + "\n")
    print("Clean reproduction completed", flush=True)


if __name__ == "__main__":
    main()
