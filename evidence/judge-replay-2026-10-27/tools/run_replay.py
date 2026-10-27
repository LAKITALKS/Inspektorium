"""Run the judge replay through the installed Inspektorium release, offline.

run_replay.py --out DIR [--wheel PATH] [--guard-tools DIR]

Run it with the Python of a virtual environment that has the release wheel
installed. It installs the Python network guard of the v0.1.1 evidence
package into that environment, checks the guard with its canary, builds the
strict and the space-normalized inputs, and calls `inspektorium inspect` for
the three judges and the controls. Any refused network operation fails the
run.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PACKAGE = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from build_proposals import build  # noqa: E402
from sensitivity import write_normalized_inputs  # noqa: E402

CASES = ("grok", "astra", "gemini", "controls")
SCRUB = (
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "XAI_API_KEY",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment(wheel: Path | None) -> dict:
    distribution = importlib.metadata.distribution("inspektorium")
    record = (
        Path(str(distribution.locate_file("")))
        / f"inspektorium-{distribution.version}.dist-info/RECORD"
    )
    return {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "inspektorium_version": distribution.version,
        "installed_record_sha256": sha256(record),
        "wheel_sha256": sha256(wheel) if wheel else None,
    }


def arm_guard(guard_tools: Path, out: Path) -> dict:
    sys.path.insert(0, str(guard_tools))
    import setup_env
    from canary import python_canary

    if not any(
        Path(sys.prefix).glob("lib/python*/site-packages/zz_evidence_netguard.pth")
    ):
        setup_env.install_guard(Path(sys.prefix))
    canary = python_canary(Path(sys.prefix), out / "guard-canary.jsonl")
    if not canary["passed"]:
        raise SystemExit(
            "the Python network guard did not refuse its canary connections"
        )
    return {
        "canary_passed": True,
        "refused_canary_operations": canary["refused_records"],
    }


def run_case(case_dir: Path, log: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in SCRUB}
    env.update(PYTHONNOUSERSITE="1", EVIDENCE_NETGUARD_LOG=str(log))
    cli = Path(sys.executable).parent / "inspektorium"
    args = [
        "inspect",
        "--input",
        "input.json",
        "--proposals",
        "proposals.json",
        "--format",
        "json",
        "--output",
        "report.json",
    ]
    process = subprocess.run(
        [str(cli), *args],
        cwd=case_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    run = {
        "argv": ["inspektorium", *args],
        "exit_code": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }
    (case_dir / "run.json").write_text(
        json.dumps(run, indent=1) + "\n", encoding="utf-8"
    )
    return run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument(
        "--guard-tools", type=Path, default=PACKAGE.parent / "v0.1.1" / "tools"
    )
    args = parser.parse_args()
    if sys.prefix == sys.base_prefix:
        raise SystemExit("run this inside the virtual environment of the release")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    inputs = PACKAGE / "inputs" / "judge-replay"
    guard = arm_guard(args.guard_tools.resolve(), out)
    normalized_inputs = out / "space-normalized-inputs"
    replaced = write_normalized_inputs(inputs, normalized_inputs)
    log = out / "netguard.jsonl"
    runs = {}
    for variant, variant_inputs in (
        ("strict", inputs),
        ("normalized", normalized_inputs),
    ):
        build(variant_inputs, out / variant)
        for case in CASES:
            run = run_case(out / variant / case, log)
            runs[f"{variant}/{case}"] = run["exit_code"]
    events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    network = {
        "armed_records": sum(e["event"] == "armed" for e in events),
        "refused_operations": sum(e["event"] == "refused" for e in events),
    }
    meta = {
        "environment": environment(args.wheel),
        "guard": guard,
        "network": network,
        "space_normalization_replacements": replaced,
        "exit_codes": runs,
    }
    (out / "run_meta.json").write_text(
        json.dumps(meta, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, indent=1))
    if network["refused_operations"] or network["armed_records"] < len(runs):
        raise SystemExit("a run attempted a network operation or ran without the guard")
    return 0 if all(code == 0 for code in runs.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
