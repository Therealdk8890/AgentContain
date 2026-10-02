"""Platform binding between an authenticated runtime receipt and a Warrant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class WarrantBoundReceipt:
    """Opaque runtime receipt plus non-authoritative Warrant correlation.

    The runtime receipt remains the cryptographically authenticated artifact.
    WarrantKit adds correlation fields without changing or re-signing the
    runtime payload. The binding is evidence metadata, never authority.
    """

    runtime_receipt: Any
    warrant_id: str
    execution_id: str
    agent_id: str
    policy_id: str
    policy_digest: str
    runtime_id: str
    epoch: int

    def __getattr__(self, name: str) -> Any:
        """Preserve access to attributes exposed by the runtime receipt."""
        return getattr(self.runtime_receipt, name)

    def to_dict(self) -> dict[str, Any]:
        """Return a transport-neutral binding without altering the signed receipt."""
        if isinstance(self.runtime_receipt, Mapping):
            runtime_receipt = dict(self.runtime_receipt)
        elif hasattr(self.runtime_receipt, "to_dict"):
            runtime_receipt = dict(self.runtime_receipt.to_dict())
        else:
            runtime_receipt = {"value": self.runtime_receipt}

        return {
            "runtime_receipt": runtime_receipt,
            "warrant_binding": {
                "warrant_id": self.warrant_id,
                "execution_id": self.execution_id,
                "agent_id": self.agent_id,
                "policy_id": self.policy_id,
                "policy_digest": self.policy_digest,
                "runtime_id": self.runtime_id,
                "epoch": self.epoch,
            },
        }
