"""critic_live2/operational simulation helpers (throwaway only).

No real network: httpx.HTTPTransport is replaced by a function that raises; every live request is answered by a
MockTransport handler driven by SIM_ROOT/faults.json and SIM_ROOT/plan.json. Responses are synthetic Phase-8
recordings bound to the real LR-01..03 texts (recordings.py).
"""
import json
import os
import time
from pathlib import Path

import httpx

HARNESS = Path(__file__).resolve().parent
GUARD = HARNESS.parent.resolve()  # critic_live2/operational


def guard(path) -> Path:
    p = Path(path).resolve()
    assert str(p).startswith(str(GUARD) + "/"), f"refusing to touch {p}"
    return p


def block_real_network():
    def blocked(*_a, **_k):
        raise AssertionError("real network access attempted in the critic_live2 simulation")
    httpx.HTTPTransport.handle_request = blocked


# Realistic output tokens (repair_r1: Haiku@2 12.9k-31.1k, Sonnet@2 6.3k-10.6k output tokens).
OUTPUT_TOKENS = {"claude-haiku-5-5": 25_000, "claude-sonnet-5-5": 9_000}
DEFAULT_PLAN = {"LR-01|primary": "supported", "LR-02|primary": "unsupported_agreed",
                "LR-03|primary": "conflict2", "LR-01|review": "conflict2",
                "LR-02|review": "conflict2", "LR-03|review": "review2"}


def _load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def handler_for(sim_root: Path):
    import recordings
    from agent_arena.runner import resolve_study_forensics_prompt
    sim_root = guard(sim_root)
    primary = resolve_study_forensics_prompt("study_forensics_prompt/v3-phase8-contract-r2")
    review = resolve_study_forensics_prompt("study_forensics_prompt/v3-phase8-contract-r2-review-p9-2")
    faults = _load(sim_root / "faults.json", {})
    plan = {**DEFAULT_PLAN, **_load(sim_root / "plan.json", {})}

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        model = body["model"]
        user = body["messages"][0]["content"]
        system = body["system"]
        kind = "primary" if system == primary else "review" if system == review else "unknown-system"
        case = next((c for c, spec in recordings.LR.items()
                     if f'<task_prompt source_id="input">\n{spec["prompt"]}\n</task_prompt>' in user), "unknown-case")
        state_path = sim_root / "router_state.json"
        state = _load(state_path, {})
        key = f"{model}|{case}|{kind}"
        state[key] = state.get(key, 0) + 1
        state["_total"] = state.get("_total", 0) + 1
        state_path.write_text(json.dumps(state))
        n = state[key]
        with (sim_root / "requests.jsonl").open("a") as log:
            log.write(json.dumps({"n_total": state["_total"], "model": model, "case": case, "kind": kind, "n": n,
                                  "system_bytes": len(system.encode()), "user_bytes": len(user.encode()),
                                  "has_bound_packet": "Bound evidence packet:" in user,
                                  "has_conflict_positions": '"model_host_conflicts"' in user,
                                  "api_key_is_test_key": request.headers.get("x-api-key") == "test-key",
                                  "max_tokens": body["max_tokens"], "pid": os.getpid()}) + "\n")
        fault = faults.get(f"{key}|{n}") or faults.get(f"{model}|*") or faults.get("*") or {}
        if fault.get("hang"):
            (sim_root / "inflight.marker").write_text(json.dumps({"pid": os.getpid(), "key": key, "n": n}))
            time.sleep(fault["hang"])
        if fault.get("exit"):
            os._exit(137)  # the CLI process dies while this request is in flight
        if fault.get("raise"):
            raise getattr(httpx, fault["raise"])("simulated")
        if fault.get("status"):
            return httpx.Response(fault["status"], json={"type": "error", "error": {"type": fault.get("type", "error")}},
                                  headers={"request-id": f"req_fail_{state['_total']}"})
        variant = fault.get("variant") or plan[f"{case}|{kind}"]
        raw = recordings.build(case, variant)
        usage = fault.get("usage") or {"input_tokens": (len(system.encode()) + len(user.encode())) // 4,
                                       "output_tokens": OUTPUT_TOKENS[model],
                                       "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
        stop = fault.get("stop_reason", "end_turn")
        content = [{"type": "thinking", "thinking": "", "signature": "sig"}]
        if stop != "refusal":
            content.append({"type": "text", "text": raw})
        payload = {"id": f"msg_{state['_total']}", "type": "message", "role": "assistant", "model": model,
                   "content": content, "stop_reason": stop, "stop_sequence": None, "usage": usage}
        return httpx.Response(200, json=payload, headers={"request-id": f"req_{state['_total']}"})

    return handler


def pin(sim_root: Path):
    from agent_arena import phase10_live as live
    live.KNOWN_CLOSED_AUTHORIZATIONS = json.loads((guard(sim_root) / "pins.json").read_text())
    return live


def guard_sessions(sim_root: Path, *, inject_live: bool):
    from agent_arena import phase10_live as live
    sim_root = guard(sim_root)
    original = live.LiveSession.__init__

    def _init(self, directory, *, mode, transport=None, api_key=None, now=None):
        assert str(Path(directory).resolve()).startswith(str(sim_root) + "/"), "simulation may only open its own dirs"
        if mode == "live" and inject_live:
            transport = httpx.MockTransport(handler_for(sim_root))
            api_key = None if os.environ.get("SIM_NO_KEY") else "test-key"
        original(self, directory, mode=mode, transport=transport, api_key=api_key, now=now)

    live.LiveSession.__init__ = _init
