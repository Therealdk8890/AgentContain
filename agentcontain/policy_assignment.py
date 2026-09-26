"""Local policy-assignment state for fleet governance.

Assignments describe desired policy placement and observed runtime state. They
never override the local PolicyRegistry or runtime enforcement authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .policy_distribution import PolicyBundle, PolicyRegistry


class AssignmentState(StrEnum):
    DESIRED = "desired"
    ACTIVE = "active"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class PolicyAssignment:
    """Policy intent scoped to one runtime or agent."""

    assignment_id: str
    policy_id: str
    policy_version: int
    policy_digest: str
    target_id: str
    state: AssignmentState = AssignmentState.DESIRED

    @classmethod
    def from_bundle(
        cls,
        assignment_id: str,
        bundle: PolicyBundle,
        target_id: str,
    ) -> "PolicyAssignment":
        if not assignment_id.strip():
            raise ValueError("assignment_id must not be empty")
        if not target_id.strip():
            raise ValueError("target_id must not be empty")
        bundle.validate()
        return cls(
            assignment_id=assignment_id,
            policy_id=bundle.policy_id,
            policy_version=bundle.policy_version,
            policy_digest=bundle.policy_digest,
            target_id=target_id,
        )


@dataclass
class PolicyAssignmentRegistry:
    """Tracks desired assignments while deferring activation to local authority."""

    _assignments: dict[str, PolicyAssignment]

    def __init__(self) -> None:
        self._assignments = {}

    def assign(self, assignment: PolicyAssignment) -> PolicyAssignment:
        existing = self._assignments.get(assignment.assignment_id)
        if existing is not None and existing != assignment:
            raise ValueError("assignment_id collision")
        self._assignments[assignment.assignment_id] = assignment
        return assignment

    def get(self, assignment_id: str) -> PolicyAssignment | None:
        return self._assignments.get(assignment_id)

    def all(self) -> tuple[PolicyAssignment, ...]:
        return tuple(self._assignments.values())

    def activate(
        self,
        assignment_id: str,
        bundle: PolicyBundle,
        policy_registry: PolicyRegistry,
    ) -> PolicyAssignment:
        assignment = self._assignments.get(assignment_id)
        if assignment is None:
            raise KeyError(assignment_id)
        bundle.validate()
        if (
            bundle.policy_id != assignment.policy_id
            or bundle.policy_version != assignment.policy_version
            or bundle.policy_digest != assignment.policy_digest
        ):
            rejected = PolicyAssignment(
                **{**assignment.__dict__, "state": AssignmentState.REJECTED}
            )
            self._assignments[assignment_id] = rejected
            raise ValueError("policy bundle does not match assignment")
        accepted = policy_registry.accept(bundle)
        active = PolicyAssignment(
            **{**assignment.__dict__, "state": AssignmentState.ACTIVE}
        )
        self._assignments[assignment_id] = active
        return active

    def supersede(self, assignment_id: str) -> PolicyAssignment:
        assignment = self._assignments.get(assignment_id)
        if assignment is None:
            raise KeyError(assignment_id)
        superseded = PolicyAssignment(
            **{**assignment.__dict__, "state": AssignmentState.SUPERSEDED}
        )
        self._assignments[assignment_id] = superseded
        return superseded
