"""Durable, transport-neutral evidence storage primitives."""

from __future__ import annotations

from typing import Protocol

from .evidence import EvidenceEnvelope


class EvidenceStore(Protocol):
    """Persistence boundary that never becomes runtime authority."""

    def put(self, envelope: EvidenceEnvelope) -> EvidenceEnvelope: ...

    def get(self, receipt_id: str) -> EvidenceEnvelope | None: ...

    def exists(self, receipt_id: str) -> bool: ...


class InMemoryEvidenceStore:
    """Reference durable-store semantics for tests and local integrations."""

    def __init__(self) -> None:
        self._items: dict[str, EvidenceEnvelope] = {}
        self._anonymous: list[EvidenceEnvelope] = []

    def put(self, envelope: EvidenceEnvelope) -> EvidenceEnvelope:
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

    def exists(self, receipt_id: str) -> bool:
        return receipt_id in self._items

    def all(self) -> tuple[EvidenceEnvelope, ...]:
        return tuple(self._items.values()) + tuple(self._anonymous)
