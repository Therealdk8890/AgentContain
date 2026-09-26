"""Deterministic policy rollout reconciliation.

Reconciliation reports the relationship between governance intent and local
assignment state. It never grants enforcement authority to the control plane.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .policy_assignment import AssignmentState, PolicyAssignment, PolicyAssignmentRegistry
from .policy_rollout import Rollout


class TargetReconciliationState(StrEnum):
    CONVERGED = "converged"
    PENDING = "pending"
    DRIFTED = "drifted"
    MISSING = "missing"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class TargetReconciliation:
    target_id: str
    state: TargetReconciliationState
    assignment_id: str | None = None
    observed_policy_id: str | None = None
    observed_policy_version: int | None = None
    observed_policy_digest: str | None = None


@dataclass(frozen=True)
class RolloutReconciliation:
    rollout_id: str
    policy_id: str
    policy_version: int
    policy_digest: str
    targets: tuple[TargetReconciliation, ...]

    @property
    def converged(self) -> bool:
        return bool(self.targets) and all(
            target.state == TargetReconciliationState.CONVERGED
            for target in self.targets
        )


def _target_assignments(
    target_id: str,
    assignments: PolicyAssignmentRegistry,
) -> tuple[PolicyAssignment, ...]:
    return tuple(
        assignment
        for assignment in assignments.all()
        if assignment.target_id == target_id
    )


def reconcile_rollout(
    rollout: Rollout,
    assignments: PolicyAssignmentRegistry,
) -> RolloutReconciliation:
    """Report deterministic desired-vs-observed state for every rollout target."""
    results: list[TargetReconciliation] = []

    for target_id in rollout.targets:
        target_assignments = _target_assignments(target_id, assignments)
        matching = tuple(
            assignment
            for assignment in target_assignments
            if (
                assignment.policy_id == rollout.policy_id
                and assignment.policy_version == rollout.policy_version
                and assignment.policy_digest == rollout.policy_digest
            )
        )

        active = next(
            (
                assignment
                for assignment in matching
                if assignment.state == AssignmentState.ACTIVE
            ),
            None,
        )
        if active is not None:
            results.append(
                TargetReconciliation(
                    target_id=target_id,
                    state=TargetReconciliationState.CONVERGED,
                    assignment_id=active.assignment_id,
                    observed_policy_id=active.policy_id,
                    observed_policy_version=active.policy_version,
                    observed_policy_digest=active.policy_digest,
                )
            )
            continue

        rejected = next(
            (
                assignment
                for assignment in matching
                if assignment.state == AssignmentState.REJECTED
            ),
            None,
        )
        if rejected is not None:
            results.append(
                TargetReconciliation(
                    target_id=target_id,
                    state=TargetReconciliationState.REJECTED,
                    assignment_id=rejected.assignment_id,
                    observed_policy_id=rejected.policy_id,
                    observed_policy_version=rejected.policy_version,
                    observed_policy_digest=rejected.policy_digest,
                )
            )
            continue

        pending = next(
            (
                assignment
                for assignment in matching
                if assignment.state == AssignmentState.DESIRED
            ),
            None,
        )
        if pending is not None:
            results.append(
                TargetReconciliation(
                    target_id=target_id,
                    state=TargetReconciliationState.PENDING,
                    assignment_id=pending.assignment_id,
                    observed_policy_id=pending.policy_id,
                    observed_policy_version=pending.policy_version,
                    observed_policy_digest=pending.policy_digest,
                )
            )
            continue

        superseded = next(
            (
                assignment
                for assignment in matching
                if assignment.state == AssignmentState.SUPERSEDED
            ),
            None,
        )
        if superseded is not None:
            results.append(
                TargetReconciliation(
                    target_id=target_id,
                    state=TargetReconciliationState.SUPERSEDED,
                    assignment_id=superseded.assignment_id,
                    observed_policy_id=superseded.policy_id,
                    observed_policy_version=superseded.policy_version,
                    observed_policy_digest=superseded.policy_digest,
                )
            )
            continue

        observed = target_assignments[-1] if target_assignments else None
        if observed is None:
            results.append(
                TargetReconciliation(
                    target_id=target_id,
                    state=TargetReconciliationState.MISSING,
                )
            )
        else:
            results.append(
                TargetReconciliation(
                    target_id=target_id,
                    state=TargetReconciliationState.DRIFTED,
                    assignment_id=observed.assignment_id,
                    observed_policy_id=observed.policy_id,
                    observed_policy_version=observed.policy_version,
                    observed_policy_digest=observed.policy_digest,
                )
            )

    return RolloutReconciliation(
        rollout_id=rollout.rollout_id,
        policy_id=rollout.policy_id,
        policy_version=rollout.policy_version,
        policy_digest=rollout.policy_digest,
        targets=tuple(results),
    )
