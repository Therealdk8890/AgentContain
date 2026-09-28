from agentcontain.identity import ExecutionIdentity
from agentcontain.incident import IncidentStatus, IncidentSummary
from agentcontain.state import PlatformStateMachine


def test_incident_projection_preserves_runtime_identity_and_trigger() -> None:
    identity = ExecutionIdentity.create("agent-1", "policy-1", "digest-1")
    machine = PlatformStateMachine(identity)
    machine.admit()
    machine.contain()
    machine.detect({"reason": "unauthorized_action"})

    incident = IncidentSummary.from_execution(identity, machine.events.events)

    assert incident.incident_id == f"incident-{identity.execution_id}"
    assert incident.agent_id == "agent-1"
    assert incident.policy_id == "policy-1"
    assert incident.status is IncidentStatus.CONTAINED
    assert incident.trigger == "anomaly_detected"
    assert incident.latest_event == "anomaly_detected"
    assert incident.event_count == 3


def test_incident_projection_tracks_verified_recovery() -> None:
    machine = PlatformStateMachine(ExecutionIdentity.create("agent-1", "policy-1", "digest-1"))
    machine.admit()
    machine.contain()
    machine.detect()
    machine.fence()
    machine.halt()
    machine.verify()
    machine.recover()
    machine.recovered(1)

    incident = IncidentSummary.from_execution(
        machine.identity,
        machine.events.events,
        proof_status="verified",
    )

    assert incident.status is IncidentStatus.RECOVERED
    assert incident.latest_event == "runtime_recovery_complete"
    assert incident.proof_status == "verified"
    assert incident.epoch == 1
