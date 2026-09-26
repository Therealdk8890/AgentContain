import pytest

from agentcontain.policy import Policy
from agentcontain.policy_assignment import PolicyAssignment, PolicyAssignmentRegistry
from agentcontain.policy_distribution import PolicyBundle
from agentcontain.policy_rollout import Rollout, RolloutState


def _setup():
    bundle = PolicyBundle.from_policy(Policy("production", version=2))
    assignments = PolicyAssignmentRegistry()
    for target in ("runtime-a", "runtime-b"):
        assignments.assign(PolicyAssignment.from_bundle(f"assignment-{target}", bundle, target))
    return bundle, assignments


def test_rollout_lifecycle_is_explicit_and_reversible_before_convergence():
    bundle, _ = _setup()
    rollout = Rollout.create("rollout-1", bundle, ("runtime-a", "runtime-b"))

    assert rollout.state == RolloutState.DRAFT
    rollout = rollout.stage().start().pause().resume()
    assert rollout.state == RolloutState.ROLLING_OUT


def test_rollout_requires_all_targets_to_be_active_before_convergence():
    bundle, assignments = _setup()
    rollout = Rollout.create("rollout-1", bundle, ("runtime-a", "runtime-b")).stage().start()

    with pytest.raises(ValueError, match="converged"):
        rollout.converge(assignments)

    registry = __import__("agentcontain.policy_distribution", fromlist=["PolicyRegistry"]).PolicyRegistry()
    for target in ("runtime-a", "runtime-b"):
        assignments.activate(f"assignment-{target}", bundle, registry)

    assert rollout.converge(assignments).state == RolloutState.CONVERGED


def test_rollout_rejects_duplicate_targets():
    bundle, _ = _setup()
    with pytest.raises(ValueError):
        Rollout.create("rollout-1", bundle, ("runtime-a", "runtime-a"))


def test_converged_rollout_cannot_be_rejected():
    bundle, assignments = _setup()
    registry = __import__("agentcontain.policy_distribution", fromlist=["PolicyRegistry"]).PolicyRegistry()
    for target in ("runtime-a", "runtime-b"):
        assignments.activate(f"assignment-{target}", bundle, registry)
    rollout = Rollout.create("rollout-1", bundle, ("runtime-a", "runtime-b")).stage().start().converge(assignments)
    with pytest.raises(ValueError):
        rollout.reject()
