"""Execution identity and epoch authority."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class ExecutionIdentity:
    """Stable identity for one admitted execution."""

    execution_id: str
    agent_id: str
    policy_id: str
    policy_digest: str
    epoch: int = 0

    @classmethod
    def create(cls, agent_id: str, policy_id: str, policy_digest: str, *, epoch: int = 0) -> "ExecutionIdentity":
        if not agent_id.strip():
            raise ValueError("agent_id must not be empty")
        if not policy_id.strip():
            raise ValueError("policy_id must not be empty")
        if epoch < 0:
            raise ValueError("epoch must be >= 0")
        return cls(
            execution_id=str(uuid4()),
            agent_id=agent_id,
            policy_id=policy_id,
            policy_digest=policy_digest,
            epoch=epoch,
        )

    def advance_epoch(self) -> "ExecutionIdentity":
        return ExecutionIdentity(
            execution_id=self.execution_id,
            agent_id=self.agent_id,
            policy_id=self.policy_id,
            policy_digest=self.policy_digest,
            epoch=self.epoch + 1,
        )
