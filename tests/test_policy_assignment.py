import pytest

from agentcontain.policy import Policy
from agentcontain.policy_assignment import (
    AssignmentState,
    PolicyAssignment,
    PolicyAssignmentRegistry,
)
from agentcontain.policy_distribution import PolicyBundle, PolicyRegistry


def test_assignment_activates_only_through_local_policy_authority():
    policy = Policy("payments", version=1, capabilities=("network",))
    bundle = PolicyBundle.from_policy(policy)
    assignments = PolicyAssignmentRegistry()
    assignment = assignments.assign(
        PolicyAssignment.from_bundle("assignment-1", bundle, "runtime-1")
    )

    active = assignments.activate("assignment-1", bundle, PolicyRegistry())

    assert active.state == AssignmentState.ACTIVE
    assert assignments.get(assignment.assignment_id) == active


def test_mismatched_policy_is_rejected():
    assigned = PolicyBundle.from_policy(Policy("payments", version=1))
    different = PolicyBundle.from_policy(Policy("payments", version=2))
    assignments = PolicyAssignmentRegistry()
    assignments.assign(
        PolicyAssignment.from_bundle("assignment-1", assigned, "runtime-1")
    )

    with pytest.raises(ValueError):
        assignments.activate("assignment-1", different, PolicyRegistry())

    assert assignments.get("assignment-1").state == AssignmentState.REJECTED


def test_assignment_collision_is_rejected():
    bundle = PolicyBundle.from_policy(Policy("payments"))
    assignments = PolicyAssignmentRegistry()
    assignments.assign(PolicyAssignment.from_bundle("assignment-1", bundle, "runtime-1"))

    other = PolicyBundle.from_policy(Policy("payments", version=2))
    with pytest.raises(ValueError):
        assignments.assign(
            PolicyAssignment.from_bundle("assignment-1", other, "runtime-1")
        )
