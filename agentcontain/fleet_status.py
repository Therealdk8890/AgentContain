"""Aggregate fleet policy reconciliation into a deterministic status snapshot."""

from __future__ import annotations

from dataclasses import dataclass

from .policy_reconciliation import (
    RolloutReconciliation,
    TargetReconciliationState,
    reconcile_rollout,
)
from .policy_assignment import PolicyAssignmentRegistry
from .policy_rollout import Rollout


@dataclass(frozen=True)
class FleetPolicyStatus:
    """Machine-readable aggregate status for one policy rollout."""

    rollout_id: str
    policy_id: str
    policy_version: int
    policy_digest: str
    total_targets: int
    converged: int
    pending: int
    drifted: int
    missing: int
    rejected: int
    superseded: int

    @property
    def is_converged(self) -> bool:
        return self.total_targets > 0 and self.converged == self.total_targets

    @classmethod
    def from_reconciliation(
        cls, reconciliation: RolloutReconciliation
    ) -> "FleetPolicyStatus":
        counts = {state: 0 for state in TargetReconciliationState}
        for target in reconciliation.targets:
            counts[target.state] += 1

        return cls(
            rollout_id=reconciliation.rollout_id,
            policy_id=reconciliation.policy_id,
            policy_version=reconciliation.policy_version,
            policy_digest=reconciliation.policy_digest,
            total_targets=len(reconciliation.targets),
            converged=counts[TargetReconciliationState.CONVERGED],
            pending=counts[TargetReconciliationState.PENDING],
            drifted=counts[TargetReconciliationState.DRIFTED],
            missing=counts[TargetReconciliationState.MISSING],
            rejected=counts[TargetReconciliationState.REJECTED],
            superseded=counts[TargetReconciliationState.SUPERSEDED],
        )

    def to_dict(self) -> dict[str, int | str | bool]:
        """Return a stable machine-readable representation."""
        return {
            "rollout_id": self.rollout_id,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "policy_digest": self.policy_digest,
            "total_targets": self.total_targets,
            "converged": self.converged,
            "pending": self.pending,
            "drifted": self.drifted,
            "missing": self.missing,
            "rejected": self.rejected,
            "superseded": self.superseded,
            "is_converged": self.is_converged,
        }


def fleet_policy_status(
    rollout: Rollout,
    assignments: PolicyAssignmentRegistry,
) -> FleetPolicyStatus:
    """Compute deterministic aggregate status without changing assignments."""
    return FleetPolicyStatus.from_reconciliation(
        reconcile_rollout(rollout, assignments)
    )
