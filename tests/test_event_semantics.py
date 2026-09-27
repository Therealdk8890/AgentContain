from agentcontain.identity import ExecutionIdentity
from agentcontain.state import PlatformStateMachine


def _machine() -> PlatformStateMachine:
    return PlatformStateMachine(
        ExecutionIdentity.create(
            "test-agent",
            "test-policy",
            "test-digest",
        )
    )


def test_detect_and_verify_have_distinct_evidence_events() -> None:
    machine = _machine()
    machine.admit()
    detected = machine.detect({"reason": "policy_violation"})

    assert detected.name == "anomaly_detected"
    assert detected.details["reason"] == "policy_violation"

    machine = _machine()
    machine.admit()
    machine.contain()
    verified = machine.verify()

    assert verified.name == "verification_completed"


def test_detection_event_is_not_verification_completion() -> None:
    machine = _machine()
    machine.admit()
    machine.detect()

    names = [event.name for event in machine.events.events]
    assert names == ["admission_verified", "anomaly_detected"]
    assert "verification_completed" not in names
