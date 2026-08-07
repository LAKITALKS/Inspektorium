"""Tiny provider protocol kept outside the deterministic core."""

from __future__ import annotations

from typing import Protocol

from inspektorium.core.models import InspectionInput, ProposalBatch


class ProviderError(RuntimeError):
    """A provider request failed without producing valid proposals."""


class Provider(Protocol):
    """One-call interface for evaluator-generated proposals."""

    def propose_findings(self, inspection_input: InspectionInput) -> ProposalBatch:
        """Return strict proposals for the supplied canonical input."""


__all__ = ["Provider", "ProviderError"]
