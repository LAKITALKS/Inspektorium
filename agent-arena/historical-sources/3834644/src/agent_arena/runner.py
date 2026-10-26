"""Run agents against a task and collect results."""

from __future__ import annotations

import time
import uuid

from agent_arena.output_contract import parse_structured_output
from agent_arena.providers import BaseProvider, get_provider
from agent_arena.schemas import AgentResponse, AgentResult, Task, TaskType


SYSTEM_PROMPT = """You are participating in a structured reasoning evaluation.

You MUST respond with valid JSON in exactly this format — no other text:
{
  "final_answer": "your precise answer here",
  "assumptions": ["each assumption you are making"],
  "steps": ["each reasoning step, showing your full chain of thought"],
  "alternative_hypotheses": ["other possible answers you considered and why you rejected them"],
  "uncertainties": ["things you are uncertain about or that could change the answer"],
  "key_claims": ["the most important factual claims your answer depends on"],
  "self_check": ["verification steps you took to confirm your answer is correct"],
  "confidence": 0.85
}

Instructions:
- Think carefully before answering. Show your full reasoning in steps.
- Be precise and specific in final_answer.
- List genuine assumptions, not trivial ones.
- Consider alternative explanations before committing to one answer.
- Note real uncertainties — what could make your answer wrong?
- Verify your own reasoning: check for common traps and errors.
- Set confidence honestly (0.0–1.0). Do not default to high confidence."""


STUDY_FORENSICS_PROMPT = """You are a study forensics analyst. Your job is to evaluate the epistemic quality of a research summary or press report about a scientific study.

Analyze the text for these types of issues:
- **Overclaim**: Does the conclusion exceed the evidence? Are there unsupported generalizations?
- **Correlation vs. causation**: Are causal claims made from correlational data?
- **Mechanism vs. evidence**: See the EVIDENCE-TIER CHECK below — this is the most commonly missed category.
- **Decorative uncertainty**: Is uncertainty language present but ineffective (e.g., "more research needed" while still making strong claims)?
- **Confounders**: Are obvious confounding variables ignored?
- **Solid study**: Is the study well-designed with appropriate caveats? Do NOT hallucinate problems that don't exist.

## EVIDENCE-TIER CHECK (mandatory for every analysis)

Before classifying, identify the evidence tier and conclusion tier separately:

Evidence tiers (from weakest to strongest):
  1. Cell/in-vitro studies
  2. Animal models (mice, rats, etc.)
  3. Biomarker/surrogate endpoints
  4. Limited human observation (small trials, pilot studies, failed primary endpoints)
  5. Full clinical human evidence (large RCTs, meta-analyses with positive primary endpoints)

Steps:
  A. What is the EVIDENCE TIER? (What was actually studied — cells, animals, small human pilot?)
  B. What is the CONCLUSION TIER? (What population or context does the text imply benefits for?)
  C. Is there a BRIDGE STEP — a leap from the evidence tier to the conclusion tier?
  D. If a bridge step exists: is it supported by direct evidence, or only by hedging language?

KEY RULE: Cautious wording alone does NOT resolve an evidence-tier mismatch.
If the evidence is from animal studies or early-stage research but the text implies human benefit — even with hedges like "more research needed," "clinical studies pending," or "could one day" — classify as mechanism_vs_evidence. The hedge acknowledges the gap but does not close it. The question is not "does the text claim certainty?" but "does the text imply a benefit at a tier the evidence does not reach?"

Contrast with solid: A text is solid when the conclusions stay within the evidence tier. A well-hedged human RCT reporting human results is solid. A well-hedged mouse study implying human therapeutic potential is mechanism_vs_evidence regardless of hedging quality.

## PRIORITY RULE: overclaim vs. mechanism_vs_evidence

When BOTH an evidence-tier mismatch AND rhetorical inflation are present, apply this decision:

- If the text **actively sells** clinical benefit, breakthrough, or outcome relevance — using promotional language like "major breakthrough," "transforms outcomes," "confirms effectiveness," "reduces risk" (stated as fact, not hypothesis) — classify as **overclaim**. The rhetorical inflation is the primary forensic finding; the tier gap is secondary.

- If the text stays **analytical or cautious** but the evidence tier simply does not support the implied conclusion — classify as **mechanism_vs_evidence**. The tier gap is the primary forensic finding; there is no active selling.

Ask yourself: **Is the main problem WHAT the text claims (too much) or WHERE the evidence comes from (wrong tier)?** If the claims themselves are inflated beyond any evidence, that is overclaim. If the claims are modest but rest on the wrong evidence base, that is mechanism_vs_evidence.

You MUST respond with valid JSON in exactly this format — no other text:
{
  "final_answer": "your overall classification: solid | overclaim | mechanism_vs_evidence | correlation_vs_causation",
  "evidence_tier": "cell | animal | biomarker | limited_human | clinical_human",
  "conclusion_tier": "same as evidence | human_therapeutic | human_policy | general_public",
  "bridge_supported": true or false,
  "assumptions": ["each assumption you are making about the study"],
  "steps": ["each reasoning step in your forensic analysis"],
  "alternative_hypotheses": ["other possible classifications you considered"],
  "uncertainties": ["things you are uncertain about in this analysis"],
  "key_claims": ["the most important epistemic findings"],
  "self_check": ["verification steps — did you overflag? did you miss something?"],
  "confidence": 0.85
}

IMPORTANT:
- Not every study has problems. Solid studies exist. Do not fabricate issues.
- Focus on what the TEXT actually says, not on what it might have said.
- Be specific about which parts of the text support each finding.
- Always complete the evidence-tier check before deciding on a classification.
- Set confidence honestly (0.0–1.0)."""

# The historical alias above is deliberately immutable: it is the exact model-visible
# Phase-7 condition (4,644 UTF-8 bytes; SHA-256 pinned by tests).  New-schema runs must
# select one of these explicit versions; legacy callers continue to resolve the historical
# bytes and are never silently retargeted.
STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL = "study_forensics_prompt/v1-historical-phase7"
STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE = (
    "study_forensics_prompt/v2-taxonomy-aligned-phase5a"
)
STUDY_FORENSICS_CONDITION_HISTORICAL = "study_forensics.historical.v1"
STUDY_FORENSICS_CONDITION_PROSPECTIVE = "study_forensics.taxonomy_aligned.v2"

_HISTORICAL_KEY_RULE = """KEY RULE: Cautious wording alone does NOT resolve an evidence-tier mismatch.
If the evidence is from animal studies or early-stage research but the text implies human benefit — even with hedges like "more research needed," "clinical studies pending," or "could one day" — classify as mechanism_vs_evidence. The hedge acknowledges the gap but does not close it. The question is not "does the text claim certainty?" but "does the text imply a benefit at a tier the evidence does not reach?"

Contrast with solid: A text is solid when the conclusions stay within the evidence tier. A well-hedged human RCT reporting human results is solid. A well-hedged mouse study implying human therapeutic potential is mechanism_vs_evidence regardless of hedging quality."""

_PROSPECTIVE_KEY_RULE = """KEY RULE: Cautious wording alone does NOT resolve a genuine evidence-tier mismatch, but a tier difference alone does not establish mechanism_vs_evidence.
Classify as mechanism_vs_evidence only when a described biological mechanism in animal or preclinical evidence is used to imply human clinical benefit that has not been demonstrated. Broad "early-stage research" language without that documented mechanism trigger is insufficient.

Do NOT use mechanism_vs_evidence for the biomarker/surrogate-to-clinical gap (Shape B). If that gap is honestly reported and the conclusion remains within the evidence, classify as solid. If a surrogate or biomarker is rhetorically sold as established clinical benefit, classify as overclaim.

Contrast with solid: A text is solid when its conclusions genuinely remain within the evidence tier. A hedge is decorative when the surrounding text still implies unsupported benefit; an explicit limitation that actually constrains the conclusion can keep cautious preclinical reporting solid."""

_HISTORICAL_PRIORITY_RULE = """When BOTH an evidence-tier mismatch AND rhetorical inflation are present, apply this decision:

- If the text **actively sells** clinical benefit, breakthrough, or outcome relevance — using promotional language like "major breakthrough," "transforms outcomes," "confirms effectiveness," "reduces risk" (stated as fact, not hypothesis) — classify as **overclaim**. The rhetorical inflation is the primary forensic finding; the tier gap is secondary.

- If the text stays **analytical or cautious** but the evidence tier simply does not support the implied conclusion — classify as **mechanism_vs_evidence**. The tier gap is the primary forensic finding; there is no active selling.

Ask yourself: **Is the main problem WHAT the text claims (too much) or WHERE the evidence comes from (wrong tier)?** If the claims themselves are inflated beyond any evidence, that is overclaim. If the claims are modest but rest on the wrong evidence base, that is mechanism_vs_evidence."""

_PROSPECTIVE_PRIORITY_RULE = """When generic overclaim and a specific structural failure may both apply, use this precedence rule:

- First determine whether the documented trigger for correlation_vs_causation or mechanism_vs_evidence is genuinely present. A specific label takes precedence over generic overclaim only when that trigger is present AND the specific failure captures the core error.

- If the specific trigger is absent, or the label fits only by stretching its documented scope, classify the primary problem as overclaim. In particular, Shape B surrogate/biomarker inflation remains overclaim rather than mechanism_vs_evidence.

- When rhetorical inflation coexists with a genuine specific failure, overclaim may be a secondary reading. Promotional tone alone must not automatically override a genuine specific label; equally, a tier gap alone must not automatically create mechanism_vs_evidence.

Ask yourself: **Which documented failure captures the core error?** Use correlation_vs_causation for a causal claim from a non-causal, uncontrolled, or confounded design. Use mechanism_vs_evidence for a described animal/preclinical biological mechanism used to imply unproven human clinical benefit. Otherwise use overclaim for rhetorical inflation beyond the evidence."""

assert _HISTORICAL_KEY_RULE in STUDY_FORENSICS_PROMPT
assert _HISTORICAL_PRIORITY_RULE in STUDY_FORENSICS_PROMPT
STUDY_FORENSICS_PROMPT_PROSPECTIVE = STUDY_FORENSICS_PROMPT.replace(
    _HISTORICAL_KEY_RULE, _PROSPECTIVE_KEY_RULE
).replace(_HISTORICAL_PRIORITY_RULE, _PROSPECTIVE_PRIORITY_RULE)

_STUDY_FORENSICS_PROMPT_REGISTRY = {
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL: {
        "condition_id": STUDY_FORENSICS_CONDITION_HISTORICAL,
        "prompt": STUDY_FORENSICS_PROMPT,
    },
    STUDY_FORENSICS_PROMPT_VERSION_PROSPECTIVE: {
        "condition_id": STUDY_FORENSICS_CONDITION_PROSPECTIVE,
        "prompt": STUDY_FORENSICS_PROMPT_PROSPECTIVE,
    },
}


def resolve_study_forensics_prompt(prompt_version: str) -> str:
    """Resolve one registered prompt version; unknown versions fail closed."""
    try:
        return _STUDY_FORENSICS_PROMPT_REGISTRY[prompt_version]["prompt"]
    except KeyError as exc:
        raise ValueError(f"unknown Study Forensics prompt version: {prompt_version}") from exc


def study_forensics_prompt_identity(prompt_version: str) -> dict[str, str]:
    """Return the stable version/condition identity without exposing mutable state."""
    try:
        registered = _STUDY_FORENSICS_PROMPT_REGISTRY[prompt_version]
    except KeyError as exc:
        raise ValueError(f"unknown Study Forensics prompt version: {prompt_version}") from exc
    return {"prompt_version": prompt_version, "prompt_condition_id": registered["condition_id"]}


def parse_agent_output(raw: str) -> tuple[AgentResponse | None, bool]:
    """Parse structured JSON from agent output with graceful degradation.

    Backward-compatible thin wrapper around
    :func:`agent_arena.output_contract.parse_structured_output`. The signature
    and return shape ``(AgentResponse | None, bool)`` are unchanged; robust
    extraction, truncation repair, and parse diagnostics now live in the
    dedicated ``output_contract`` module. Use ``parse_structured_output``
    directly when the diagnostics object is needed.
    """
    parsed, diag = parse_structured_output(raw)
    return parsed, diag.ok


def _select_system_prompt(
    task: Task,
    prompt_version: str = STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
) -> str:
    """Select the appropriate system prompt based on task type."""
    if task.task_type == TaskType.STUDY_FORENSICS:
        return resolve_study_forensics_prompt(prompt_version)
    if prompt_version != STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL:
        raise ValueError("a Study Forensics prompt version cannot be applied to another task type")
    return SYSTEM_PROMPT


def run_agent(
    provider: BaseProvider,
    task: Task,
    *,
    prompt_version: str = STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
) -> AgentResult:
    """Run a single agent on a task.

    Uses the provider's normalized :meth:`~agent_arena.providers.BaseProvider.generate`
    contract (Phase 2): captures ``finish_reason``/``usage``/``latency`` and
    feeds ``finish_reason`` into the Phase-1 output parser so truncation is
    marked correctly. Errors are surfaced consistently — a failed call never
    looks like a successful empty response.
    """
    label = getattr(provider, "label", "") or getattr(provider, "model", "")
    model_id = getattr(provider, "model", "")
    start = time.monotonic()
    try:
        system_prompt = _select_system_prompt(task, prompt_version)
        resp = provider.generate(task, system_prompt)
        # Fall back to wall-clock latency if the provider did not record it.
        latency = resp.latency_ms if resp.latency_ms is not None else \
            int((time.monotonic() - start) * 1000)

        if resp.error:
            return AgentResult(
                provider=label,
                model=model_id or (resp.model or ""),
                error=resp.error,
                error_type=resp.error_type,
                finish_reason=resp.finish_reason,
                usage=resp.usage,
                latency_ms=latency,
            )

        parsed, diag = parse_structured_output(resp.text, finish_reason=resp.finish_reason)
        return AgentResult(
            provider=label,
            model=model_id or (resp.model or ""),
            raw_output=resp.text,
            parsed=parsed,
            parse_ok=diag.ok,
            latency_ms=latency,
            finish_reason=resp.finish_reason,
            usage=resp.usage,
        )
    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        from agent_arena.providers.response import classify_error_type
        return AgentResult(
            provider=label,
            model=model_id,
            error=str(e),
            error_type=classify_error_type(e),
            latency_ms=latency,
        )


def run_task(task: Task, provider_names: list[str]) -> tuple[str, list[AgentResult]]:
    """Run all providers on a task. Returns (run_id, results)."""
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    results = []
    for name in provider_names:
        provider = get_provider(name)
        result = run_agent(provider, task)
        results.append(result)
    return run_id, results


def run_task_with_providers(task: Task, providers: list[BaseProvider]) -> tuple[str, list[AgentResult]]:
    """Run pre-configured providers on a task. Returns (run_id, results)."""
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    results = []
    for provider in providers:
        result = run_agent(provider, task)
        results.append(result)
    return run_id, results
