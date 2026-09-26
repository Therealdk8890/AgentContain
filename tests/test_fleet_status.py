from agentcontain.policy import Policy
from agentcontain.policy_assignment import PolicyAssignment, PolicyAssignmentRegistry
from agentcontain.policy_distribution import PolicyBundle, PolicyRegistry
from agentcontain.policy_reconciliation import TargetReconciliationState, reconcile_rollout
from agentcontain.policy_rollout import Rollout
from agentcontain.fleet_status import FleetPolicyStatus, fleet_policy_status


def _rollout():
    bundle = PolicyBundle.from_policy(Policy("production", version=2))
    return bundle, Rollout.create(
        "rollout-1", bundle, ("runtime-a", "runtime-b", "runtime-c")
    )


def test_fleet_status_aggregates_reconciliation_states():
    bundle, rollout = _rollout()
    assignments = PolicyAssignmentRegistry()

    assignments.assign(
        PolicyAssignment.from_bundle("assignment-a", bundle, "runtime-a")
    )

    other = PolicyBundle.from_policy(Policy("production", version=1))
    assignments.assign(
        PolicyAssignment.from_bundle("assignment-b", other, "runtime-b")
    )

    report = fleet_policy_status(rollout, assignments)

    assert report == FleetPolicyStatus(
        rollout_id="rollout-1",
        total_targets=3,
        converged=0,
        pending=1,
        drifted=1,
        missing=1,
        rejected=0,
        superseded=0,
    )
    assert report.is_converged is False


def test_fleet_status_reports_full_convergence():
    bundle, rollout = _rollout()
    assignments = PolicyAssignmentRegistry()
    registry = PolicyRegistry()

    for target in rollout.targets:
        assignment_id = f"assignment-{target}"
        assignments.assign(
            PolicyAssignment.from_bundle(assignment_id, bundle, target)
        )
        assignments.activate(assignment_id, bundle, registry)

    report = fleet_policy_status(rollout, assignments)

    assert report.total_targets == 3
    assert report.converged == 3
    assert report.pending == 0
    assert report.drifted == 0
    assert report.missing == 0
    assert report.is_converged is True


def test_fleet_status_is_deterministic_and_serializable():
    _, rollout = _rollout()
    assignments = PolicyAssignmentRegistry()

    report = fleet_policy_status(rollout, assignments)

    assert report.to_dict() == {
        "rollout_id": "rollout-1",
        "total_targets": 3,
        "converged": 0,
        "pending": 0,
        "drifted": 0,
        "missing": 3,
        "rejected": 0,
        "superseded": 0,
        "is_converged": False,
    }


def test_reconciliation_state_enum_is_complete():
    assert {state.value for state in TargetReconciliationState} == {
        "converged",
        "pending",
        "drifted",
        "missing",
        "rejected",
        "superseded",
    }
