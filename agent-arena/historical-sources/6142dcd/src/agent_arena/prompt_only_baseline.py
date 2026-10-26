"""Frozen prompt-only baseline for the Phase 6.4A comparison pilot (offline, no calls).

This module freezes the **prompt-only baseline arm** of a paired, one-model pilot that
asks whether the Agent Arena forensic prompting/scaffolding **package** shows a
*descriptive* advantage over a competent minimal prompt-only **package**, with the model
(``claude-haiku-4-5-20251001`` dated snapshot), the 27 development cases, the
user-visible case content (``task.prompt``), the runtime parameters, the replication
count, and the evaluation targets held fixed.

**Accurate treatment contrast (do not overclaim):** the two arms are NOT "only a
different system-prompt string". They use *different model-facing response contracts*
(the Agent Arena arm elicits ~11 structured forensic fields; this baseline elicits 3:
``predicted_label``, ``confidence``, ``brief_reason``) and *different parsers* (the Agent
Arena arm's ``parse_structured_output`` performs best-effort truncation repair and
derives the label heuristically from ``final_answer``; this baseline uses a stricter
no-repair parser and reads ``predicted_label`` directly). Both arms are normalized to the
**same evaluated outputs — predicted top label and confidence**. The pilot therefore
estimates a descriptive **package-level** contrast; it does **not** isolate the causal
effect of one system-prompt string alone. Parser-completion differences are reported
separately and never conflated with classification accuracy.

Everything here is pure and deterministic and makes **no** model call:

- the exact frozen baseline system prompt (bytes + SHA-256);
- a deterministic input projection that exposes only model-visible claim/evidence
  material (``task.prompt``) and **excludes every answer-bearing field** — proven by
  reusing ``packet_integrity.check_contamination``;
- a strict response parser for ``{predicted_label, confidence, brief_reason}`` that
  rejects extra fields, unknown labels, and malformed JSON, and classifies confidence as
  VALID / MISSING / INVALID via the Phase 6.1 semantics — **never coercing to 0.0**;
- a frozen prompt-only runtime contract (``AA-RTC-6.4-HAIKU-PROMPT-ONLY-001``) binding the
  model id, prompt hash, projection hash, parser hash, runtime params, and source
  checkpoint.

The baseline is competent and non-adversarial; it is never described as inferior and it
does not reproduce the Agent Arena forensic scaffold.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence
from agent_arena.output_contract import extract_json_object
from agent_arena.packet_integrity import ModelFacingPacket, check_contamination
from agent_arena.schemas import Task, TaskType

# ---------------------------------------------------------------------------
# Frozen identity / parameters
# ---------------------------------------------------------------------------

CONTRACT_ID = "AA-RTC-6.4-HAIKU-PROMPT-ONLY-001"
CONTRACT_VERSION = "1.0"
CALIBRATION_MODE = "PROMPT_ONLY_BASELINE_VS_AGENT_ARENA_PAIRED_PILOT"
PROTOCOL_VERSION = "6.1"
PROVIDER = "anthropic"
EXACT_MODEL_ID = "claude-haiku-4-5-20251001"
MODEL_FAMILY = "claude-haiku-4-5"
MODEL_REVISION = "20251001"
AGENT_CONFIG_PATH = "agents/claude_haiku.yaml"
# PRE-PREPARATION source baseline these public artifacts are frozen against (Phase 6.3
# HEAD). This is NOT the execution HEAD: the private execution session must run from the
# eventual Phase 6.4A preparation commit (a later, post-commit checkpoint) and validate
# these frozen hashes — see private_execution_handoff.md.
REPOSITORY_SOURCE_CHECKPOINT = "9b89945b8f9af1a112e8265653d17186c70f61c0"

FROZEN_LABELS = ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence")

# Accurate, frozen description of what the pilot actually contrasts. Embedded in the
# runtime contract so contract metadata never claims a "system-prompt only" difference.
TREATMENT_CONTRAST = (
    "package-level contrast: same model (dated snapshot), 27 cases, user-visible case "
    "content (task.prompt), runtime parameters, replication count, and evaluation targets "
    "held fixed; arms differ in BOTH the model-facing response contract (~11 structured "
    "forensic fields vs 3: predicted_label/confidence/brief_reason) AND the parser "
    "(Agent Arena parse_structured_output with truncation repair + heuristic label vs "
    "baseline strict no-repair parser reading predicted_label directly). Both normalized "
    "to the same evaluated outputs (top label + confidence). NOT the causal effect of one "
    "system-prompt string alone; parser-completion differences reported separately."
)

# Result-envelope contract the (later, private) execution session emits into.
RESULT_ENVELOPE_CONTRACT = "phase6_2 anonymized_result_contract (envelope_version 6.2.0)"

# Response schema: exactly these three keys, nothing else.
RESPONSE_REQUIRED_KEYS = ("predicted_label", "confidence", "brief_reason")


# ---------------------------------------------------------------------------
# The exact frozen baseline system prompt (single source of truth)
# ---------------------------------------------------------------------------
# NOTE: this string is FROZEN. A one-character change changes the SHA-256 and must be a
# deliberate, reviewed re-freeze. It deliberately does NOT reproduce the Agent Arena
# evidence-tier decision procedure or any forensic scaffold.

BASELINE_SYSTEM_PROMPT = """You are a careful scientific-claims analyst. You are given a public claim and the evidence text that accompanies it. Classify the claim into exactly one of four categories, using only the information supplied. Do not invent facts, studies, numbers, or sources that are not present in the supplied text.

Choose exactly one label:

- solid: The claim is supported within the scope and strength of the supplied evidence.
- overclaim: The claim goes beyond what the supplied evidence supports, without a more specific label below being the best fit.
- correlation_vs_causation: An association or observational relationship is presented as establishing a causal effect.
- mechanism_vs_evidence: Biological mechanism, laboratory, animal, biomarker, or other preclinical evidence is used to imply human clinical benefit without sufficient human clinical evidence.

Guidance:
- Base your decision only on the supplied claim and evidence.
- Distinguish a claim that stays within its evidence (solid) from one that overstates it (overclaim).
- Distinguish a reported association from a demonstrated causal effect (correlation_vs_causation).
- Apply mechanism_vs_evidence only when biological or preclinical evidence is used to imply a human clinical benefit that the human evidence does not establish. Do not assign this label merely because the word "mechanism" appears, or because a biological process is described, when no human clinical benefit is being implied.
- If more than one label could fit, choose the single most specific label that best captures the main problem with the claim.

Confidence:
- Report confidence as your degree of belief that your selected label is correct.
- Confidence is a number between 0 and 1, where 0.0 means no belief and 1.0 means maximal belief.

Output:
Respond with a single strict JSON object and nothing else: no markdown, no code fence, no commentary, and no additional keys. The object must contain exactly these three keys:
{"predicted_label": "<one of: solid | overclaim | correlation_vs_causation | mechanism_vs_evidence>", "confidence": <number between 0 and 1>, "brief_reason": "<one or two sentences, grounded only in the supplied claim and evidence>"}

Do not include chain-of-thought or step-by-step reasoning. Keep brief_reason concise.
"""


def baseline_system_prompt() -> str:
    """Return the exact frozen baseline system prompt."""
    return BASELINE_SYSTEM_PROMPT


def canonical_baseline_prompt_bytes() -> bytes:
    """Deterministic UTF-8 bytes of the frozen baseline system prompt."""
    return BASELINE_SYSTEM_PROMPT.encode("utf-8")


def baseline_prompt_digest() -> str:
    """SHA-256 hex of the frozen baseline system prompt bytes."""
    return hashlib.sha256(canonical_baseline_prompt_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Deterministic input projection (model-visible claim/evidence only)
# ---------------------------------------------------------------------------
# INCLUDED (model-visible): task.prompt — the sole user-facing claim/evidence text, the
#   same content the Agent Arena arm sends as its user message.
# EXCLUDED (never sent): id (canonical), gold_label, expected_answer, gold_summary,
#   gold_justification, gold_alternative_reading, gold_confidence, gold_case_type,
#   status, excluded_from_active_metrics, expected_findings, gold_evidence_spans,
#   curator_notes, evaluator_notes, task_family/strata, key_insights, common_errors,
#   expected_failure_modes, diagnostic_focus, and any DEV id (DEV ids never enter the
#   prompt; they live only in the result envelope keyed by dev_id).

INPUT_PROJECTION_INCLUDED = ("prompt",)
INPUT_PROJECTION_EXCLUDED = (
    "id", "gold_label", "expected_answer", "reference_solution", "gold_summary",
    "gold_justification", "gold_alternative_reading", "gold_confidence", "gold_case_type",
    "status", "excluded_from_active_metrics", "expected_findings", "gold_evidence_spans",
    "curator_notes", "evaluator_notes", "task_family", "trap_type", "ambiguity_level",
    "key_insights", "common_errors", "expected_failure_modes", "discriminative_dimensions",
    "diagnostic_focus", "expected_mechanism_terms", "fragile_points", "likely_shortcuts",
    "dev_id", "stratum",
)

# Forbidden value-shaped tokens that must never appear in a model-facing message.
_CANONICAL_ID_RE = re.compile(r"study-forensics-[0-9]+", re.I)
_DEV_ID_RE = re.compile(r"\bDEV-[0-9]{3,}\b")
_BIAA_RE = re.compile(r"\bBIAA-[0-9]+", re.I)
_HLD_RE = re.compile(r"\bHLD-[0-9]+", re.I)
_TECH_LABEL_TOKENS = tuple(FROZEN_LABELS)


def build_baseline_input_projection(task: Task) -> str:
    """Deterministic projection → the model-visible user content only (``task.prompt``).

    This is the single field the baseline sends; every answer-bearing field is excluded.
    """
    return task.prompt or ""


def build_baseline_messages(task: Task) -> dict:
    """The exact model-facing message pair for one case: frozen system + projected user."""
    return {"system": BASELINE_SYSTEM_PROMPT, "user": build_baseline_input_projection(task)}


def input_projection_descriptor() -> str:
    """Stable descriptor of the projection contract (hashed into the runtime contract)."""
    return (
        "prompt_only_baseline.input_projection.v1 | "
        f"included={list(INPUT_PROJECTION_INCLUDED)} | "
        f"excluded={list(INPUT_PROJECTION_EXCLUDED)} | "
        "user=task.prompt(verbatim); system=frozen baseline prompt; "
        "no gold/expected/canonical/DEV/strata/notes ever sent"
    )


def input_projection_sha256() -> str:
    return hashlib.sha256(input_projection_descriptor().encode("utf-8")).hexdigest()


def validate_no_forbidden_fields(task: Task, case_file: str = "") -> list[str]:
    """Prove the baseline messages carry no answer-bearing / private field.

    Reuses ``packet_integrity.check_contamination`` on a packet built from the frozen
    baseline system prompt and the projected user content, then adds explicit checks for
    gold/expected label values, DEV ids, and canonical/BIAA/HLD ids anywhere in the
    combined message. Returns a list of error strings (empty = clean).
    """
    errors: list[str] = []
    messages = build_baseline_messages(task)
    combined = f"{messages['system']}\n{messages['user']}"
    packet = ModelFacingPacket(
        case_id=task.id,
        task_type=task.task_type.value if isinstance(task.task_type, TaskType) else str(task.task_type),
        system=messages["system"],
        user=messages["user"],
    )
    contamination = check_contamination(task, packet, case_file=case_file)
    for f in contamination.findings:
        errors.append(f"contamination:{f.code}:{f.field}:{f.detail}")

    low = combined.lower()
    # explicit gold/expected label value must not appear as a technical token in the user msg
    user_low = (messages["user"] or "").lower()
    for value_name, value in (("gold_label", task.gold_label),
                              ("expected_answer", task.expected_answer)):
        v = (value or "").strip().lower()
        if v and v in _TECH_LABEL_TOKENS and re.search(rf"\b{re.escape(v)}\b", user_low):
            errors.append(f"forbidden:{value_name}_token_in_user_message:{v}")
    # private identifiers anywhere in the combined message
    if _CANONICAL_ID_RE.search(combined):
        errors.append("forbidden:canonical_id_in_message")
    if _DEV_ID_RE.search(combined):
        errors.append("forbidden:dev_id_in_message")
    if _BIAA_RE.search(combined) or _HLD_RE.search(combined):
        errors.append("forbidden:biaa_or_hld_id_in_message")
    # sealed-path markers must never be embedded. Assembled from fragments so this
    # source file contains no literal private-path token (detector vocabulary only).
    sealed_markers = ("internal" + "_only", "agentarena" + "_iaa_private",
                      "/us" + "ers/", "/priv" + "ate/tmp/")
    for marker in sealed_markers:
        if marker in low:
            errors.append(f"forbidden:path_marker_in_message:{marker}")
    return errors


# ---------------------------------------------------------------------------
# Strict response parser (no chain-of-thought; exactly three keys)
# ---------------------------------------------------------------------------

@dataclass
class BaselineParse:
    ok: bool = False                       # True iff a well-formed 3-key object was parsed
    parse_ok: bool = False                 # True iff JSON extraction succeeded
    predicted_label: str | None = None
    confidence_raw: object = None
    confidence_validity: str = MISSING     # VALID / MISSING / INVALID
    confidence_value: float | None = None  # float iff VALID
    brief_reason: str | None = None
    strategy: str = "none"
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "parse_ok": self.parse_ok,
            "predicted_label": self.predicted_label,
            "confidence_validity": self.confidence_validity,
            "confidence_value": self.confidence_value,
            "brief_reason": self.brief_reason,
            "strategy": self.strategy,
            "errors": list(self.errors),
        }


def classify_baseline_confidence(raw: object) -> str:
    """VALID / MISSING / INVALID for a raw baseline confidence (Phase 6.1; no coercion)."""
    return classify_confidence(raw)


def parse_baseline_response(raw: str, finish_reason: str | None = None) -> BaselineParse:
    """Strictly parse a baseline model response. Never raises.

    A malformed / unparseable JSON body is recorded as a **parser failure**
    (``parse_ok=False``) — never a normal verdict. Extra keys, missing required keys, and
    unknown labels are rejected (``ok=False``) but still surface what was parsed. Missing
    or invalid confidence is classified and preserved, **never coerced to 0.0**.
    """
    result = BaselineParse()
    data, diag = extract_json_object(raw, finish_reason)
    result.strategy = diag.strategy
    # A genuinely malformed body — OR one only recoverable by best-effort truncation
    # repair — is a parser failure, never a verdict. The baseline does not accept a
    # reconstructed object as an answer (conservative; consistent with "no retry for
    # malformed JSON / parser failure").
    if data is None or diag.repaired:
        result.parse_ok = False
        reason = diag.error or ("repaired/truncated output not accepted as a verdict"
                                if diag.repaired else "unparseable JSON")
        result.errors.append(f"parser_failure:{reason}")
        return result
    result.parse_ok = True

    keys = set(data.keys())
    extra = sorted(keys - set(RESPONSE_REQUIRED_KEYS))
    missing = [k for k in RESPONSE_REQUIRED_KEYS if k not in data]
    if extra:
        result.errors.append(f"extra_fields:{extra}")
    if missing:
        result.errors.append(f"missing_fields:{missing}")

    label = data.get("predicted_label")
    result.predicted_label = label if isinstance(label, str) else None
    if label not in FROZEN_LABELS:
        result.errors.append(f"unknown_label:{label!r}")

    has_conf = "confidence" in data
    result.confidence_raw = data.get("confidence") if has_conf else None
    result.confidence_validity = classify_confidence(result.confidence_raw) if has_conf else MISSING
    result.confidence_value = (
        float(result.confidence_raw) if result.confidence_validity == VALID else None
    )
    if result.confidence_validity != VALID:
        result.errors.append(f"confidence_{result.confidence_validity}")

    br = data.get("brief_reason")
    result.brief_reason = br if isinstance(br, str) else None
    if br is not None and not isinstance(br, str):
        result.errors.append("brief_reason_not_string")

    result.ok = not extra and not missing and label in FROZEN_LABELS and isinstance(br, str)
    return result


def validate_baseline_result(record: dict) -> list[str]:
    """Validate one assembled prompt-only result record (envelope-ready, opaque only)."""
    errors: list[str] = []
    allowed = {"dev_id", "model", "predicted_label", "gold_label", "stratum",
               "confidence", "gold_case_type", "correct"}
    extra = sorted(set(record) - allowed)
    if extra:
        errors.append(f"record has unexpected field(s): {extra}")
    dev_id = record.get("dev_id", "")
    if not (isinstance(dev_id, str) and re.fullmatch(r"DEV-[0-9]{3,}", dev_id)):
        errors.append("dev_id must be an opaque DEV-#### id")
    if record.get("predicted_label") not in FROZEN_LABELS:
        errors.append("predicted_label is not a frozen label")
    if record.get("gold_label") not in FROZEN_LABELS:
        errors.append("gold_label is not a frozen label")
    if "confidence" in record and classify_confidence(record["confidence"]) == INVALID:
        errors.append("confidence is INVALID (non-numeric/boolean/out-of-range)")
    return errors


# ---------------------------------------------------------------------------
# Frozen prompt-only runtime contract
# ---------------------------------------------------------------------------

def parser_contract_descriptor() -> str:
    """Stable descriptor of the baseline parser behavior (hashed into the contract)."""
    return (
        "prompt_only_baseline.parser.v1 | "
        f"required_keys={list(RESPONSE_REQUIRED_KEYS)} | additionalProperties=false | "
        f"labels={list(FROZEN_LABELS)} | "
        "confidence=VALID/MISSING/INVALID (Phase 6.1; never coerce to 0.0) | "
        "malformed_or_repaired_json=parse_ok_false (parser failure, never a verdict) | "
        "no chain-of-thought; strict single JSON object"
    )


def parser_contract_sha256() -> str:
    return hashlib.sha256(parser_contract_descriptor().encode("utf-8")).hexdigest()


def build_runtime_contract() -> dict:
    """Deterministic frozen prompt-only Haiku runtime contract (JSON-serializable dict)."""
    return {
        "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION,
        "calibration_mode": CALIBRATION_MODE,
        "protocol_version": PROTOCOL_VERSION,
        "provider": PROVIDER,
        "endpoint": "Anthropic Messages API (anthropic.Anthropic().messages.create)",
        "exact_model_id": EXACT_MODEL_ID,
        "model_family": MODEL_FAMILY,
        "model_revision": MODEL_REVISION,
        "agent_config_path": AGENT_CONFIG_PATH,
        "repository_source_checkpoint": REPOSITORY_SOURCE_CHECKPOINT,
        "repository_source_checkpoint_note": (
            "pre-preparation source baseline (Phase 6.3 HEAD); NOT the execution HEAD. "
            "Execute from the Phase 6.4A preparation commit and validate these hashes."
        ),
        "treatment_contrast": TREATMENT_CONTRAST,
        "system_prompt_sha256": baseline_prompt_digest(),
        "input_projection_sha256": input_projection_sha256(),
        "parser_contract_sha256": parser_contract_sha256(),
        "result_envelope_contract": RESULT_ENVELOPE_CONTRACT,
        "temperature": 0.0,
        "top_p": "OMITTED_FROM_REQUEST",
        "seed": "UNSUPPORTED",
        "max_output_tokens": 4096,
        "replication_count": 1,
        "concurrency": 1,
        "request_timeout_seconds": 120,
        "max_transport_retries_after_initial_request": 2,
        "retry_backoff": "exponential_backoff_anthropic_sdk_default",
        "retryable_error_classes": [
            "connection_error", "request_timeout", "rate_limit_429",
            "transient_server_error_5xx", "overloaded_529",
        ],
        "semantic_or_quality_retries": "PROHIBITED",
        "parser_failure_handling": "record as failed record (parse_ok=false); never re-run",
        "missing_confidence_handling": "classify MISSING; never coerce to 0.0",
        "invalid_confidence_handling": "classify INVALID; never coerce to 0.0",
        "execution_order_rule": "deterministic filename order (discover_cases); one primary execution per case",
        "partial_run_recovery_rule": "resume only not-yet-executed cases; never re-run completed or failed cases",
        "prohibit_prompt_or_parameter_changes_during_run": True,
        "prohibit_selective_reruns": True,
        "prohibit_threshold_or_abstention_tuning_during_execution": True,
        "residual_nondeterminism_note": (
            "temperature=0.0 and seed unsupported reduce but do not eliminate variation; "
            "provider outputs may still differ run-to-run. Only the analysis is fully "
            "deterministic, not the model sampling."
        ),
    }


_CONTRACT_REQUIRED = (
    "contract_id", "exact_model_id", "system_prompt_sha256", "input_projection_sha256",
    "parser_contract_sha256", "repository_source_checkpoint", "treatment_contrast",
    "temperature", "max_output_tokens", "replication_count", "concurrency",
    "request_timeout_seconds", "max_transport_retries_after_initial_request", "top_p", "seed",
)
_DATED_MODEL_RE = re.compile(r"^claude-[a-z]+-\d+-\d+-\d{8}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_runtime_contract(contract: dict) -> list[str]:
    """Validate a prompt-only runtime contract reproduces the frozen hashes and params."""
    errors: list[str] = []
    for k in _CONTRACT_REQUIRED:
        if k not in contract:
            errors.append(f"missing required field: {k}")
    if contract.get("contract_id") != CONTRACT_ID:
        errors.append("contract_id mismatch")
    if not _DATED_MODEL_RE.match(str(contract.get("exact_model_id", ""))):
        errors.append("exact_model_id must be a dated snapshot")
    if contract.get("exact_model_id") != EXACT_MODEL_ID:
        errors.append("exact_model_id is not the frozen pilot model")
    if not _COMMIT_RE.match(str(contract.get("repository_source_checkpoint", ""))):
        errors.append("repository_source_checkpoint must be a 40-hex commit")
    if contract.get("treatment_contrast") != TREATMENT_CONTRAST:
        errors.append("treatment_contrast must be the accurate frozen package-level description")
    if "only the system prompt" in json.dumps(contract).lower():
        errors.append("contract must not claim a 'system-prompt only' contrast")
    for hk, expected in (("system_prompt_sha256", baseline_prompt_digest()),
                         ("input_projection_sha256", input_projection_sha256()),
                         ("parser_contract_sha256", parser_contract_sha256())):
        v = str(contract.get(hk, ""))
        if not _SHA_RE.match(v):
            errors.append(f"{hk} must be a 64-hex digest")
        elif v != expected:
            errors.append(f"{hk} does not reproduce the frozen value")
    if contract.get("temperature") != 0.0:
        errors.append("temperature must be 0.0")
    if contract.get("top_p") != "OMITTED_FROM_REQUEST":
        errors.append("top_p must be omitted from the request")
    if contract.get("seed") != "UNSUPPORTED":
        errors.append("seed must be UNSUPPORTED")
    if contract.get("max_output_tokens") != 4096:
        errors.append("max_output_tokens must be 4096")
    if contract.get("replication_count") != 1:
        errors.append("replication_count must be 1")
    if contract.get("concurrency") != 1:
        errors.append("concurrency must be 1")
    if contract.get("request_timeout_seconds") != 120:
        errors.append("request_timeout_seconds must be 120")
    if contract.get("max_transport_retries_after_initial_request") != 2:
        errors.append("max_transport_retries_after_initial_request must be 2")
    if contract.get("semantic_or_quality_retries") != "PROHIBITED":
        errors.append("semantic_or_quality_retries must be PROHIBITED")
    return errors


def canonical_contract_bytes(contract: dict) -> bytes:
    """Deterministic canonical JSON bytes for the runtime contract."""
    return json.dumps(contract, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
