"""Transport-neutral ingestion boundary for AgentContain evidence."""

from __future__ import annotations
from typing import Protocol
from .evidence import EvidenceEnvelope

class EvidenceSink(Protocol):
    """Minimal downstream boundary for accepted evidence."""
    def submit(self, envelope: EvidenceEnvelope) -> EvidenceEnvelope:
        """Accept evidence and return the accepted original."""

class InMemoryEvidenceSink:
    """Reference sink for local use and tests."""
    def __init__(self) -> None:
        self._items: dict[str, EvidenceEnvelope] = {}
        self._anonymous: list[EvidenceEnvelope] = []

    def submit(self, envelope: EvidenceEnvelope) -> EvidenceEnvelope:
        if not isinstance(envelope, EvidenceEnvelope):
            raise TypeError("envelope must be an EvidenceEnvelope")
        receipt_id = envelope.receipt_id
        if receipt_id is None:
            self._anonymous.append(envelope)
            return envelope
        existing = self._items.get(receipt_id)
        if existing is None:
            self._items[receipt_id] = envelope
            return envelope
        if existing.to_json() != envelope.to_json():
            raise ValueError(f"evidence receipt_id collision: {receipt_id}")
        return existing

    def get(self, receipt_id: str) -> EvidenceEnvelope | None:
        return self._items.get(receipt_id)

    def all(self) -> tuple[EvidenceEnvelope, ...]:
        return tuple(self._items.values()) + tuple(self._anonymous)
