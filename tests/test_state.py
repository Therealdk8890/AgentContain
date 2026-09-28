"""Regression tests for lifecycle evidence semantics."""

from agentcontain.identity import ExecutionIdentity
from agentcontain.state import LifecycleState, PlatformStateMachine


def _machine() -> PlatformStateMachine:
    return PlatformStateMachine(
        ExecutionIdentity.create("agent-1", "policy-1", "digest-1")
    )


def test_detect_emits_detection_event_not_verification_event() -> None:
    machine = _machine()
    machine.admit()
    machine.contain()

    event = machine.detect({"reason": "policy_violation"})

    assert machine.state is LifecycleState.DETECTED
    assert event.name == "anomaly_detected"
    assert event.details == {"reason": "policy_violation"}


def test_verify_emits_verification_event() -> None:
    machine = _machine()
    machine.admit()
    machine.contain()

    event = machine.verify()

    assert machine.state is LifecycleState.VERIFIED
    assert event.name == "verification_completed"


def test_recovery_advances_execution_epoch():
    machine = _machine()
    machine.admit()
    machine.contain()
    machine.verify()
    machine.recover()

    event = machine.recovered(1)

    assert machine.identity.epoch == 1
    assert event.epoch == 1
    assert event.execution_id == machine.identity.execution_id
    assert [e.epoch for e in machine.event_history[0].events] == [0, 0, 0, 0]
    assert [e.sequence for e in machine.event_history[0].events] == [1, 2, 3, 4]
    assert [e.sequence for e in machine.events.events] == [1]
