#!/usr/bin/env python3
"""Deterministic Phase 6.4A artifact generator (offline, no model calls, no network).

Regenerates the frozen prompt-only baseline artifacts and the deterministic fixture
outputs from the single source of truth in ``agent_arena.prompt_only_baseline``:

- ``prompt_only_system_prompt.txt`` / ``.sha256`` — the exact frozen baseline prompt;
- ``prompt_only_runtime_contract_haiku.json`` — the validated frozen runtime contract;
- ``deterministic_fixture_outputs/responses_parsed.json`` — parse outcomes for every
  synthetic response fixture;
- ``deterministic_fixture_outputs/projection_outputs.json`` — projection + forbidden-field
  outcomes for every synthetic Task fixture.

Determinism: everything derives from frozen module constants and the synthetic fixtures;
no wall-clock, no randomness. Repeated runs are byte-for-byte identical.

Usage::

    PYTHONPATH=src .venv/bin/python analysis/phase6_4_prompt_only_pilot/build_artifacts.py \
        [--out-dir analysis/phase6_4_prompt_only_pilot]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_arena.prompt_only_baseline import (
    baseline_prompt_digest,
    build_baseline_input_projection,
    build_runtime_contract,
    canonical_baseline_prompt_bytes,
    canonical_contract_bytes,
    parse_baseline_response,
    validate_no_forbidden_fields,
    validate_runtime_contract,
)
from agent_arena.schemas import Task

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "synthetic_fixtures"


def _dump(obj, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", default=str(HERE))
    ap.add_argument("--fixtures-dir", default=str(FIXTURES))
    args = ap.parse_args()
    out = Path(args.out_dir)
    fx = Path(args.fixtures_dir)
    (out / "deterministic_fixture_outputs").mkdir(parents=True, exist_ok=True)

    # 1. frozen prompt + sha256
    (out / "prompt_only_system_prompt.txt").write_bytes(canonical_baseline_prompt_bytes())
    (out / "prompt_only_system_prompt.sha256").write_text(baseline_prompt_digest() + "\n")

    # 2. frozen runtime contract (validated)
    contract = build_runtime_contract()
    errs = validate_runtime_contract(contract)
    if errs:
        print(f"[FAIL] runtime contract does not validate: {errs}")
        return 2
    (out / "prompt_only_runtime_contract_haiku.json").write_bytes(canonical_contract_bytes(contract))

    # 3. deterministic response-parse outputs
    responses = json.loads((fx / "responses.json").read_text())["fixtures"]
    parsed_out = []
    for f in responses:
        p = parse_baseline_response(f["raw"])
        parsed_out.append({"id": f["id"], "parsed": p.as_dict(), "expect": f["expect"]})
    _dump({"n": len(parsed_out), "results": parsed_out},
          out / "deterministic_fixture_outputs" / "responses_parsed.json")

    # 4. deterministic projection + forbidden-field outputs
    tasks = json.loads((fx / "projection_tasks.json").read_text())["fixtures"]
    proj_out = []
    for f in tasks:
        task = Task(**f["task"])
        projection = build_baseline_input_projection(task)
        forbidden = validate_no_forbidden_fields(task)
        proj_out.append({
            "id": f["id"],
            "projection_equals_task_prompt": projection == (task.prompt or ""),
            "projection_len": len(projection),
            "forbidden_field_errors": forbidden,
            "clean": not forbidden,
            "expect_clean": f["expect_clean"],
            "note": f["note"],
        })
    _dump({"n": len(proj_out), "results": proj_out},
          out / "deterministic_fixture_outputs" / "projection_outputs.json")

    print(f"prompt sha256: {baseline_prompt_digest()}")
    print(f"wrote artifacts + {len(parsed_out)} response outputs + {len(proj_out)} projection outputs to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
