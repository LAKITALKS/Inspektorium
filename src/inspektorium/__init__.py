"""Inspektorium: evidence-bound inspection for model outputs."""

from inspektorium.core.inspection import inspect_proposals
from inspektorium.core.models import (
    AnswerInput,
    InspectionInput,
    InspectionReport,
    ProposalBatch,
    ProposedFinding,
    SourceDocument,
    ValidatedFinding,
)
from inspektorium.core.relations import (
    DeterministicValidationStatus,
    EvaluatorCertainty,
    EvidenceRelation,
    EvidenceSufficiency,
)

__all__ = [
    "AnswerInput",
    "DeterministicValidationStatus",
    "EvidenceRelation",
    "EvidenceSufficiency",
    "EvaluatorCertainty",
    "InspectionInput",
    "InspectionReport",
    "ProposalBatch",
    "ProposedFinding",
    "SourceDocument",
    "ValidatedFinding",
    "inspect_proposals",
]

__version__ = "0.1.1"
