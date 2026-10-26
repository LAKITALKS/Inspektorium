"""Deterministic, offline packet-integrity checks (Phase 6.0).

A *packet* is the model-facing input for a single case: the system prompt plus the
user content that is actually sent to a provider. This module reconstructs that
packet **without any model call** and runs two **separately reported** checks:

1. **Semantic preservation** — the packet preserves the canonical claim
   (``task.prompt``) verbatim and non-empty, and carries the required structural
   scaffold (the exact study-forensics system contract, incl. the output-contract
   fields and the label answer-space).
2. **Contamination / leakage** — the packet exposes none of the curator-only gold
   / answer-key material, no case identifiers (``case_id`` / filename stem), and no
   IAA identifiers (HLD/BIAA/RVAL/FXR).

The two outcomes are never collapsed into one verdict; the report keeps both
diagnostics side by side. This automates, deterministically and repo-wide, the
manual claim-isolation / leakage audit performed by hand in Phase 5.1.

Design notes
------------
* The reconstruction reuses the real runtime contract: :func:`runner._select_system_prompt`
  for the system prompt and the provider rule that the user content is exactly
  ``task.prompt`` (verified identical across the anthropic/openai/ollama providers).
  If a provider ever starts serializing more of the ``Task`` into the model message,
  the reconstruction here must be updated in lockstep — the tests pin this contract.
* Development material only. The tool **refuses** to read sealed locations
  (``internal_only/``, the private holdout, the concurrent research-expansion
  folder); it makes no network/model calls and does not import provider clients.
* The system prompt legitimately enumerates the four label names (that is the
  answer *space*, not the answer for a given case), so the contamination check
  targets per-case leakage in the user content and verifies the system prompt is
  the unmodified static template — it never flags the label space itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from agent_arena.runner import (
    STUDY_FORENSICS_PROMPT,  # noqa: F401 - historical compatibility re-export
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
    SYSTEM_PROMPT,
    _select_system_prompt,
)
from agent_arena.schemas import Task, TaskType

# ---------------------------------------------------------------------------
# Isolation guard
# ---------------------------------------------------------------------------

class SealedPathError(RuntimeError):
    """Raised when a caller points the tool at sealed / out-of-scope material."""


# Substrings that mark material this tool must never read. Matched against the
# resolved absolute path (case-insensitive).
SEALED_PATH_MARKERS: tuple[str, ...] = (
    "internal_only",
    "agentarena_iaa_private",
    "phase5_1_holdout",
    "agent_arena_library_expansion_150",
)


def assert_path_allowed(path: str | Path) -> Path:
    """Return the resolved path, or raise :class:`SealedPathError` if it is sealed."""
    p = Path(path).resolve()
    low = str(p).lower()
    for marker in SEALED_PATH_MARKERS:
        if marker in low:
            raise SealedPathError(
                f"refusing to access sealed/out-of-scope path (marker '{marker}'): {p}"
            )
    return p


# ---------------------------------------------------------------------------
# Model-facing packet reconstruction
# ---------------------------------------------------------------------------

@dataclass
class ModelFacingPacket:
    """The exact content a provider would send for one case (offline reconstruction)."""

    case_id: str
    task_type: str
    system: str
    user: str

    @property
    def combined(self) -> str:
        return f"{self.system}\n{self.user}"

    def as_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "task_type": self.task_type,
            "system_len": len(self.system),
            "user_len": len(self.user),
        }


def build_model_facing_packet(
    task: Task,
    prompt_version: str = STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
) -> ModelFacingPacket:
    """Reconstruct the model-facing packet for ``task`` (no model call).

    Mirrors the runtime contract: system prompt from ``_select_system_prompt`` and
    user content equal to ``task.prompt`` (the sole user message every provider
    sends). This is the single source of truth the integrity checks operate on.
    """
    return ModelFacingPacket(
        case_id=task.id,
        task_type=task.task_type.value if isinstance(task.task_type, TaskType) else str(task.task_type),
        system=_select_system_prompt(task, prompt_version),
        user=task.prompt or "",
    )


# ---------------------------------------------------------------------------
# Result containers (both checks reported separately)
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    code: str
    severity: str          # "critical" | "high" | "medium"
    field: str
    detail: str

    def as_dict(self) -> dict:
        return {"code": self.code, "severity": self.severity, "field": self.field, "detail": self.detail}


@dataclass
class CheckResult:
    name: str              # "semantic_preservation" | "contamination_leakage"
    passed: bool
    findings: list[Finding] = field(default_factory=list)
    diagnostics: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "findings": [f.as_dict() for f in self.findings],
            "diagnostics": self.diagnostics,
        }


@dataclass
class PacketReport:
    case_id: str
    case_file: str
    gold_label: str | None
    semantic: CheckResult
    contamination: CheckResult

    @property
    def ok(self) -> bool:
        return self.semantic.passed and self.contamination.passed

    def as_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "case_file": self.case_file,
            "gold_label": self.gold_label,
            "ok": self.ok,
            "semantic_preservation": self.semantic.as_dict(),
            "contamination_leakage": self.contamination.as_dict(),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WS = re.compile(r"\s+")
# Technical label tokens that never occur in natural claim prose (unlike the bare
# words "solid"/"overclaim"), so their presence in user content is a real leak.
_TECHNICAL_LABEL_TOKENS = ("correlation_vs_causation", "mechanism_vs_evidence")
# IAA / remediation identifiers that must never appear in a development packet.
_IAA_ID_RE = re.compile(r"\b(?:HLD|BIAA|RVAL|FXR)-\d+", re.IGNORECASE)
# Minimum normalized length for a free-text gold blob to be worth substring-matching
# (avoids false positives from short, generic fragments).
_MIN_BLOB_LEN = 40


def _norm(text: str | None) -> str:
    return _WS.sub(" ", (text or "").strip()).lower()


def _file_stem_tokens(case_file: str) -> list[str]:
    """Identifier tokens derived from the filename, e.g. 'case013_gut_microbes'."""
    stem = Path(case_file).stem
    tokens = [stem]
    # also the leading 'caseNNN' fragment if present
    m = re.match(r"(case[_-]?\d+)", stem, re.IGNORECASE)
    if m:
        tokens.append(m.group(1))
    return [t for t in tokens if t]


# ---------------------------------------------------------------------------
# Check 1: semantic preservation
# ---------------------------------------------------------------------------

# Structural markers the study-forensics system contract must retain.
_REQUIRED_SF_MARKERS = (
    '"final_answer"',
    '"confidence"',
    "solid",
    "overclaim",
    "mechanism_vs_evidence",
    "correlation_vs_causation",
)


def check_semantic_preservation(
    task: Task,
    packet: ModelFacingPacket,
    prompt_version: str = STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
) -> CheckResult:
    findings: list[Finding] = []

    # 1. Claim preserved verbatim and non-empty.
    if not packet.user.strip():
        findings.append(Finding("empty_claim", "high", "user",
                                "model-facing user content (the claim) is empty"))
    elif packet.user != (task.prompt or ""):
        findings.append(Finding("claim_altered", "high", "user",
                                "model-facing claim differs from canonical task.prompt"))

    # 2. Required structural scaffold present, and (for study_forensics) the system
    #    prompt is the exact, unmodified static contract.
    if task.task_type == TaskType.STUDY_FORENSICS:
        if packet.system != _select_system_prompt(task, prompt_version):
            findings.append(Finding("system_prompt_modified", "high", "system",
                                    "study-forensics system prompt is not the canonical static contract"))
        missing = [m for m in _REQUIRED_SF_MARKERS if m not in packet.system]
        if missing:
            findings.append(Finding("missing_scaffold", "high", "system",
                                    f"required output/label markers missing: {missing}"))
    else:
        if packet.system != SYSTEM_PROMPT:
            findings.append(Finding("system_prompt_unexpected", "medium", "system",
                                    "non study-forensics system prompt is not the canonical default"))

    diagnostics = {
        "claim_chars": len(packet.user),
        "system_chars": len(packet.system),
        "claim_verbatim": packet.user == (task.prompt or "") and bool(packet.user.strip()),
    }
    return CheckResult("semantic_preservation", passed=not findings,
                       findings=findings, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# Check 2: contamination / leakage
# ---------------------------------------------------------------------------

def check_contamination(task: Task, packet: ModelFacingPacket, case_file: str = "") -> CheckResult:
    findings: list[Finding] = []
    user_norm = _norm(packet.user)

    # a) Technical label tokens leaking into the claim.
    for tok in _TECHNICAL_LABEL_TOKENS:
        if tok in user_norm:
            findings.append(Finding("label_token_in_claim", "critical", "user",
                                    f"technical label token '{tok}' appears in the claim"))

    # b) expected_answer as a technical token in the claim.
    ea = _norm(task.expected_answer)
    if ea and ea in _TECHNICAL_LABEL_TOKENS and ea in user_norm:
        findings.append(Finding("expected_answer_in_claim", "critical", "expected_answer",
                                f"expected_answer '{ea}' appears in the claim"))

    # c) Wholesale copy of gold rationale free-text into the claim.
    blob_fields = {
        "reference_solution": task.reference_solution,
        "gold_summary": task.gold_summary,
        "gold_justification": task.gold_justification,
        "gold_alternative_reading": task.gold_alternative_reading,
        "curator_notes": task.curator_notes,
    }
    for fname, value in blob_fields.items():
        nv = _norm(value)
        if len(nv) >= _MIN_BLOB_LEN and nv in user_norm:
            findings.append(Finding("gold_text_in_claim", "critical", fname,
                                    f"verbatim {fname} text appears in the claim"))

    # d) Evidence-span *annotations* (why_it_matters) leaking. The span text itself
    #    is a legitimate excerpt of the claim and is intentionally not flagged.
    for i, span in enumerate(task.gold_evidence_spans or []):
        wim = _norm(getattr(span, "why_it_matters", "") or "")
        if len(wim) >= _MIN_BLOB_LEN and wim in user_norm:
            findings.append(Finding("evidence_annotation_in_claim", "high",
                                    f"gold_evidence_spans[{i}].why_it_matters",
                                    "gold evidence-span annotation appears in the claim"))

    # e) Internal finding codes leaking into the claim.
    for i, ef in enumerate(task.expected_findings or []):
        code = _norm(getattr(ef, "finding", "") or "")
        if code and re.search(rf"\b{re.escape(code)}\b", user_norm):
            findings.append(Finding("finding_code_in_claim", "high",
                                    f"expected_findings[{i}].finding",
                                    f"internal finding code '{code}' appears in the claim"))

    # f) IAA / remediation identifiers anywhere in the packet.
    for m in _IAA_ID_RE.findall(packet.combined):
        findings.append(Finding("iaa_identifier_in_packet", "critical", "packet",
                                f"IAA identifier '{m}' present in packet"))

    # g) Case identifiers (case_id, filename stem) in the claim.
    id_tokens = [t for t in [task.id] if t] + _file_stem_tokens(case_file)
    for tok in id_tokens:
        if _norm(tok) and _norm(tok) in user_norm:
            findings.append(Finding("case_identifier_in_claim", "high", "case_id",
                                    f"case identifier '{tok}' appears in the claim"))

    diagnostics = {
        "checked_blob_fields": list(blob_fields.keys()),
        "n_evidence_spans": len(task.gold_evidence_spans or []),
        "n_expected_findings": len(task.expected_findings or []),
        "iaa_scan": "combined_packet",
    }
    return CheckResult("contamination_leakage", passed=not findings,
                       findings=findings, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# Per-case + library orchestration
# ---------------------------------------------------------------------------

def check_task(task: Task, case_file: str = "") -> PacketReport:
    packet = build_model_facing_packet(task)
    semantic = check_semantic_preservation(task, packet)
    contamination = check_contamination(task, packet, case_file=case_file)
    return PacketReport(
        case_id=task.id,
        case_file=case_file or "",
        gold_label=task.gold_label,
        semantic=semantic,
        contamination=contamination,
    )


@dataclass
class IntegrityReport:
    task_dir: str
    n_cases: int
    n_ok: int
    n_semantic_fail: int
    n_contamination_fail: int
    reports: list[PacketReport] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.n_semantic_fail == 0 and self.n_contamination_fail == 0

    def as_dict(self) -> dict:
        return {
            "tool": "packet_integrity",
            "task_dir": self.task_dir,
            "summary": {
                "n_cases": self.n_cases,
                "n_ok": self.n_ok,
                "n_semantic_fail": self.n_semantic_fail,
                "n_contamination_fail": self.n_contamination_fail,
                "overall_ok": self.ok,
            },
            "cases": [r.as_dict() for r in self.reports],
        }


def run_packet_integrity(
    task_dir: str | Path | None = None,
    case_id: str | None = None,
    include_retired: bool = False,
) -> IntegrityReport:
    """Scan development cases and return a two-check integrity report.

    Refuses sealed / out-of-scope directories. Uses the same discovery as the
    library harness so retired-case handling stays consistent.
    """
    # Imported here to keep module import cheap and avoid provider-client imports.
    from agent_arena.run_library import TASK_DIR, discover_cases

    resolved = assert_path_allowed(task_dir) if task_dir is not None else TASK_DIR
    cases = discover_cases(
        case_id=case_id,
        task_dir=Path(resolved),
        include_retired=include_retired,
    )
    reports = [check_task(task, case_file=path.name) for path, task in cases]
    n_sem = sum(1 for r in reports if not r.semantic.passed)
    n_con = sum(1 for r in reports if not r.contamination.passed)
    n_ok = sum(1 for r in reports if r.ok)
    return IntegrityReport(
        task_dir=str(resolved),
        n_cases=len(reports),
        n_ok=n_ok,
        n_semantic_fail=n_sem,
        n_contamination_fail=n_con,
        reports=reports,
    )


# ---------------------------------------------------------------------------
# Human-readable rendering
# ---------------------------------------------------------------------------

def render_report_text(report: IntegrityReport) -> str:
    lines: list[str] = []
    s = report
    lines.append("Packet-Integrity Report")
    lines.append("=" * 24)
    lines.append(f"task_dir: {s.task_dir}")
    lines.append(f"cases: {s.n_cases}  ok: {s.n_ok}  "
                 f"semantic-fail: {s.n_semantic_fail}  contamination-fail: {s.n_contamination_fail}")
    lines.append(f"overall: {'PASS' if s.ok else 'FAIL'}")
    lines.append("")
    # Two checks are reported separately, never merged.
    failing = [r for r in s.reports if not r.ok]
    if not failing:
        lines.append("All cases pass both checks (semantic preservation + contamination/leakage).")
    else:
        lines.append(f"{len(failing)} case(s) with findings:")
        for r in failing:
            lines.append(f"\n- {r.case_id} ({r.case_file}) [gold={r.gold_label}]")
            if not r.semantic.passed:
                lines.append("    semantic_preservation: FAIL")
                for f in r.semantic.findings:
                    lines.append(f"      [{f.severity}] {f.code} @ {f.field}: {f.detail}")
            if not r.contamination.passed:
                lines.append("    contamination_leakage: FAIL")
                for f in r.contamination.findings:
                    lines.append(f"      [{f.severity}] {f.code} @ {f.field}: {f.detail}")
    return "\n".join(lines) + "\n"
