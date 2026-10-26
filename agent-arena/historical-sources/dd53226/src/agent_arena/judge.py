"""Optional LLM-as-judge layer for agent-arena v0.3.

Provides blind evaluation of agent responses using a separate LLM call.
The judge sees only the task + agent output (no scores, no other agents).
"""

from __future__ import annotations

import json
import os

from agent_arena.schemas import (
    AgentResponse,
    JudgeClaimAudit,
    JudgeResult,
    Task,
)

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator assessing the quality of an AI agent's reasoning response.

You will receive:
1. A TASK (the original problem)
2. An AGENT RESPONSE (structured JSON with reasoning fields)

Evaluate the response and return valid JSON with this exact structure:
{
  "dimension_scores": {
    "correctness": 0.0-1.0,
    "structural_reasoning": 0.0-1.0,
    "assumption_discipline": 0.0-1.0,
    "uncertainty_calibration": 0.0-1.0,
    "alternative_hypothesis_awareness": 0.0-1.0,
    "self_verification_quality": 0.0-1.0,
    "insight_depth": 0.0-1.0,
    "communication_efficiency": 0.0-1.0
  },
  "evidence_citations": ["quote from the response that supports each score"],
  "failure_modes": ["any reasoning failure modes you detect"],
  "claim_audit": [
    {
      "claim": "a key claim from the response",
      "status": "supported|unsupported|contradicted|incomplete",
      "evidence": "why you assigned this status",
      "confidence": 0.0-1.0
    }
  ],
  "comparative_note": "brief overall assessment",
  "judge_confidence": 0.0-1.0
}

Guidelines:
- Score each dimension independently from 0.0 to 1.0
- For claim_audit, check each key_claim against the reasoning steps and reference solution
- Be specific in evidence_citations — quote the actual text
- Do not be lenient. High scores require genuine quality.
- judge_confidence reflects how confident YOU are in your evaluation"""


def _build_judge_prompt(task: Task, parsed: AgentResponse) -> str:
    return f"""## TASK

**Title:** {task.title}
**Domain:** {task.domain}
**Difficulty:** {task.difficulty.value}
**Prompt:** {task.prompt}

**Reference Solution:**
{task.reference_solution or "(not provided)"}

**Expected Answer:** {task.expected_answer or "(not provided)"}

## AGENT RESPONSE

**Final Answer:** {parsed.final_answer}

**Key Claims:** {json.dumps(parsed.key_claims)}

**Assumptions:** {json.dumps(parsed.assumptions)}

**Reasoning Steps:** {json.dumps(parsed.steps)}

**Alternative Hypotheses:** {json.dumps(parsed.alternative_hypotheses)}

**Uncertainties:** {json.dumps(parsed.uncertainties)}

**Self-Verification:** {json.dumps(parsed.self_check)}

**Confidence:** {parsed.confidence}"""


def run_judge(task: Task, parsed: AgentResponse, provider_name: str = "anthropic",
              model: str | None = None) -> JudgeResult:
    """Run LLM judge on a single agent response. Requires API key."""
    try:
        from agent_arena.providers import get_provider
    except ImportError:
        return JudgeResult(enabled=False, comparative_note="Provider not available")

    judge_model = model or os.environ.get("JUDGE_MODEL", "claude-sonnet-4-20250514")

    try:
        provider = get_provider(provider_name, model=judge_model, temperature=0.0)
    except Exception as e:
        return JudgeResult(enabled=False, comparative_note=f"Judge provider error: {e}")

    prompt = _build_judge_prompt(task, parsed)

    try:
        raw = provider.send_prompt(
            task=Task(
                id="judge-eval",
                title="Judge Evaluation",
                domain="meta",
                difficulty=task.difficulty,
                task_type=task.task_type,
                prompt=prompt,
            ),
            system_prompt=JUDGE_SYSTEM_PROMPT,
        )
    except Exception as e:
        return JudgeResult(enabled=False, comparative_note=f"Judge call failed: {e}")

    return _parse_judge_output(raw)


def _parse_judge_output(raw: str) -> JudgeResult:
    # Phase 2.5: delegate fragile JSON extraction to the shared, hardened
    # output-contract parser (handles unclosed ```json fences, pre/post prose,
    # and truncated JSON without raising). Judge field mapping is unchanged.
    from agent_arena.output_contract import extract_json_object

    data, _diag = extract_json_object(raw)
    if data is None:
        return JudgeResult(enabled=True, raw_output=raw,
                           comparative_note="Judge output not parseable")

    claim_audit = []
    for item in data.get("claim_audit", []):
        claim_audit.append(JudgeClaimAudit(
            claim=item.get("claim", ""),
            status=item.get("status", "unsupported"),
            evidence=item.get("evidence", ""),
            confidence=item.get("confidence", 0.0),
        ))

    return JudgeResult(
        enabled=True,
        dimension_scores=data.get("dimension_scores", {}),
        evidence_citations=data.get("evidence_citations", []),
        failure_modes=data.get("failure_modes", []),
        claim_audit=claim_audit,
        comparative_note=data.get("comparative_note", ""),
        judge_confidence=data.get("judge_confidence", 0.0),
        raw_output=raw,
    )
