"""Deterministic platform policy model.

allowed_egress is part of policy identity and distribution, but remains
declarative until an enforcement provider explicitly consumes it. It must not
be treated as runtime enforcement merely because it is present in a Policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json


@dataclass(frozen=True)
class Policy:
    """Versioned policy describing the authority granted to an execution.

    allowed_egress is a declarative policy field. Its presence in the
    canonical policy and digest does not itself configure or prove host-level
    egress enforcement.
    """

    policy_id: str
    version: int = 1
    allowed_egress: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("policy_id must not be empty")
        if self.version < 1:
            raise ValueError("version must be >= 1")

    def canonical(self) -> str:
        payload = {
            "capabilities": sorted(self.capabilities),
            "allowed_egress": sorted(self.allowed_egress),
            "metadata": dict(sorted(self.metadata.items())),
            "policy_id": self.policy_id,
            "version": self.version,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.canonical().encode("utf-8")).hexdigest()
