"""Transport-neutral evidence envelope for AgentContain executions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

SCHEMA_VERSION = "agentcontain.evidence/v1"
VALID_STATUSES = {"observed", "verified", "degraded", "tampered", "incomplete"}


def canonical_json(value: Any) -> str:
    """Return deterministic JSON suitable for hashing, storage, and transport."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class EvidenceEnvelope:
    """Machine-readable evidence for one AgentContain execution."""

    execution: Mapping[str, Any]
    events: tuple[Mapping[str, Any], ...] = ()
    enforcement: Mapping[str, Any] = None  # type: ignore[assignment]
    verification: Mapping[str, Any] = None  # type: ignore[assignment]
    proof: Mapping[str, Any] = None  # type: ignore[assignment]
    receipt: Mapping[str, Any] | None = None
    governance: Mapping[str, Any] | None = None
    provenance: Mapping[str, Any] = None  # type: ignore[assignment]
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported evidence schema: {self.schema_version}")
        for name in ("execution", "enforcement", "verification", "proof", "provenance"):
            value = getattr(self, name)
            if not isinstance(value, Mapping):
                raise TypeError(f"{name} must be a mapping")
        if not isinstance(self.events, tuple):
            object.__setattr__(self, "events", tuple(self.events))
        if any(not isinstance(event, Mapping) for event in self.events):
            raise TypeError("events must contain mappings")
        self.validate()

    @classmethod
    def from_execution(
        cls,
        *,
        execution: Mapping[str, Any],
        events: tuple[Mapping[str, Any], ...] = (),
        enforcement: Mapping[str, Any] | None = None,
        verification: Mapping[str, Any] | None = None,
        proof: Mapping[str, Any] | None = None,
        receipt: Mapping[str, Any] | None = None,
        governance: Mapping[str, Any] | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> "EvidenceEnvelope":
        return cls(
            execution=dict(execution),
            events=tuple(dict(event) for event in events),
            enforcement=dict(enforcement or {}),
            verification=dict(verification or {}),
            proof=dict(proof or {}),
            receipt=dict(receipt) if receipt is not None else None,
            governance=dict(governance) if governance is not None else None,
            provenance=dict(provenance or {"producer": "agentcontain"}),
        )

    def with_receipt(self, receipt: Mapping[str, Any]) -> "EvidenceEnvelope":
        """Return a copy bound to an existing authenticated receipt.

        The receipt is treated as an opaque transport-neutral mapping. Its
        payload identity must agree with this envelope when the corresponding
        fields are present. Cryptographic verification remains the
        responsibility of the existing receipt verifier.
        """
        if not isinstance(receipt, Mapping):
            raise TypeError("receipt must be a mapping")
        required = {"payload", "digest", "signature"}
        if set(receipt) != required:
            raise ValueError("receipt has an invalid envelope")
        payload = receipt["payload"]
        if not isinstance(payload, Mapping):
            raise TypeError("receipt payload must be a mapping")

        for field in ("execution_id", "agent_id", "policy_id", "epoch"):
            receipt_value = payload.get(field)
            if receipt_value is not None and receipt_value != self.execution[field]:
                raise ValueError(f"receipt {field} does not match evidence execution")

        receipt_id = payload.get("receipt_id")
        if receipt_id is not None and not isinstance(receipt_id, str):
            raise ValueError("receipt receipt_id must be a string")

        return EvidenceEnvelope(
            execution=self.execution,
            events=self.events,
            enforcement=self.enforcement,
            verification=self.verification,
            proof=self.proof,
            receipt=dict(receipt),
            provenance=self.provenance,
            schema_version=self.schema_version,
        )

    def validate(self) -> None:
        required = {"execution_id", "agent_id", "policy_id", "policy_digest", "epoch"}
        missing = required - set(self.execution)
        if missing:
            raise ValueError("execution identity missing fields: " + ", ".join(sorted(missing)))

        status = self.verification.get("status")
        if status is not None and status not in VALID_STATUSES:
            raise ValueError(f"invalid verification status: {status}")

        execution_id = self.execution["execution_id"]
        sequences: list[int] = []
        for event in self.events:
            if event.get("execution_id") != execution_id:
                raise ValueError("event execution_id does not match envelope")
            sequence = event.get("sequence")
            if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
                raise ValueError("event sequence must be a positive integer")
            sequences.append(sequence)

        if sequences and sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("event sequence must be contiguous starting at 1")

        if status == "verified" and not self.events:
            raise ValueError("verified evidence requires at least one event")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "execution": dict(self.execution),
            "events": [dict(event) for event in self.events],
            "enforcement": dict(self.enforcement),
            "verification": dict(self.verification),
            "proof": dict(self.proof),
            "receipt": dict(self.receipt) if self.receipt is not None else None,
            "governance": dict(self.governance) if self.governance is not None else None,
            "provenance": dict(self.provenance),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, document: Mapping[str, Any]) -> "EvidenceEnvelope":
        if not isinstance(document, Mapping):
            raise TypeError("evidence envelope must be a mapping")
        expected = {
            "schema_version",
            "execution",
            "events",
            "enforcement",
            "verification",
            "proof",
            "receipt",
            "governance",
            "provenance",
        }
        if set(document) != expected:
            raise ValueError("evidence envelope has an invalid shape")
        if not isinstance(document["events"], list):
            raise TypeError("events must be a list")
        return cls(
            execution=dict(document["execution"]),
            events=tuple(dict(event) for event in document["events"]),
            enforcement=dict(document["enforcement"]),
            verification=dict(document["verification"]),
            proof=dict(document["proof"]),
            receipt=dict(document["receipt"]) if document["receipt"] is not None else None,
            governance=dict(document["governance"]) if document["governance"] is not None else None,
            provenance=dict(document["provenance"]),
            schema_version=document["schema_version"],
        )

    @classmethod
    def from_json(cls, document: str) -> "EvidenceEnvelope":
        return cls.from_dict(json.loads(document))

    @property
    def receipt_id(self) -> str | None:
        if self.receipt is None:
            return None
        value = self.receipt.get("payload", {}).get("receipt_id")
        return value if isinstance(value, str) else None
