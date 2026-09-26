import pytest

from agentcontain.policy import Policy
from agentcontain.policy_assignment import PolicyAssignment, PolicyAssignmentRegistry
from agentcontain.policy_distribution import PolicyBundle, PolicyRegistry
from agentcontain.policy_reconciliation import (
    TargetReconciliationState,
    reconcile_rollout,
)
from agentcontain.policy_rollout import Rollout


def _rollout():
    bundle = PolicyBundle.from_policy(Policy("production", version=2))
    rollout = Rollout.create("rollout-1", bundle, ("runtime-a", "runtime-b"))
    return bundle, rollout


def test_reconciliation_reports_missing_and_pending_targets():
    bundle, rollout = _rollout()
    assignments = PolicyAssignmentRegistry()
    assignments.assign(PolicyAssignment.from_bundle("assignment-a", bundle, "runtime-a"))

    report = reconcile_rollout(rollout, assignments)

    assert [target.state for target in report.targets] == [
        TargetReconciliationState.PENDING,
        TargetReconciliationState.MISSING,
    ]
    assert report.converged is False


def test_reconciliation_reports_converged_targets():
    bundle, rollout = _rollout()
    assignments = PolicyAssignmentRegistry()
    registry = PolicyRegistry()
    for target in rollout.targets:
        assignments.assign(
            PolicyAssignment.from_bundle(f"assignment-{target}", bundle, target)
        )
        assignments.activate(f"assignment-{target}", bundle, registry)

    report = reconcile_rollout(rollout, assignments)

    assert report.converged is True
    assert all(
        target.state == TargetReconciliationState.CONVERGED
        for target in report.targets
    )


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("rejected", TargetReconciliationState.REJECTED),
        ("superseded", TargetReconciliationState.SUPERSEDED),
    ],
)
def test_reconciliation_reports_terminal_assignment_states(state, expected):
    bundle, rollout = _rollout()
    assignments = PolicyAssignmentRegistry()
    assignment = PolicyAssignment.from_bundle("assignment-a", bundle, "runtime-a")
    assignments.assign(assignment)

    if state == "rejected":
        different = PolicyBundle.from_policy(Policy("production", version=3))
        with pytest.raises(ValueError):
            assignments.activate("assignment-a", different, PolicyRegistry())
    else:
        assignments.supersede("assignment-a")

    report = reconcile_rollout(rollout, assignments)

    assert report.targets[0].state == expected


def test_reconciliation_reports_drift_when_target_has_other_policy():
    _, rollout = _rollout()
    assignments = PolicyAssignmentRegistry()
    other = PolicyBundle.from_policy(Policy("production", version=1))
    assignments.assign(PolicyAssignment.from_bundle("assignment-a", other, "runtime-a"))

    report = reconcile_rollout(rollout, assignments)

    assert report.targets[0].state == TargetReconciliationState.DRIFTED
    assert report.targets[0].observed_policy_version == 1
