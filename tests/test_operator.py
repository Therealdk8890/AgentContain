from agentcontain.evidence import EvidenceEnvelope
from agentcontain.fleet import Agent, FleetRegistry, Organization, Project, Runtime
from agentcontain.operator import OperatorIncidentView
from agentcontain.policy import Policy
from agentcontain.policy_assignment import PolicyAssignment, PolicyAssignmentRegistry
from agentcontain.policy_distribution import PolicyBundle


def _envelope(policy: Policy) -> EvidenceEnvelope:
    return EvidenceEnvelope.from_execution(
        execution={
            "execution_id": "exec-1",
            "agent_id": "agent-1",
            "policy_id": policy.policy_id,
            "policy_digest": policy.digest,
            "epoch": 3,
        },
        events=(
            {"name": "admission_verified", "execution_id": "exec-1", "epoch": 3, "sequence": 1, "timestamp": "2026-09-27T00:00:00+00:00", "details": {}},
            {"name": "anomaly_detected", "execution_id": "exec-1", "epoch": 3, "sequence": 2, "timestamp": "2026-09-27T00:00:01+00:00", "details": {"reason": "unauthorized_action"}},
            {"name": "containment_verified", "execution_id": "exec-1", "epoch": 3, "sequence": 3, "timestamp": "2026-09-27T00:00:02+00:00", "details": {}},
        ),
        verification={"status": "verified", "method": "test"},
        proof={"checks": ["containment"]},
    )


def test_operator_view_composes_agent_policy_incident_and_timeline() -> None:
    fleet = FleetRegistry()
    org = fleet.register_organization(Organization.create("Acme"))
    project = fleet.register_project(Project.create(org.organization_id, "Payments"))
    runtime = fleet.register_runtime(Runtime.create(project.project_id, "prod"))
    fleet.register_agent(Agent.create(runtime.runtime_id, "payments-agent", agent_id="agent-1"))

    assignments = PolicyAssignmentRegistry()
    policy = Policy(policy_id="payments", version=7, capabilities=("payments:charge",))
    bundle = PolicyBundle.from_policy(policy)
    assignments.assign(PolicyAssignment.from_bundle("assign-1", bundle, "agent-1"))

    view = OperatorIncidentView.from_evidence(_envelope(policy), fleet=fleet, assignments=assignments)

    assert view.agent["name"] == "payments-agent"
    assert view.policy["policy_version"] == 7
    assert view.policy["assignment_id"] == "assign-1"
    assert view.incident.status.value == "verified"
    assert view.incident.trigger == "anomaly_detected"
    assert [event.name for event in view.timeline] == ["admission_verified", "anomaly_detected", "containment_verified"]
    assert view.timeline[1].details["reason"] == "unauthorized_action"


def test_operator_view_does_not_mutate_evidence() -> None:
    policy = Policy(policy_id="payments", version=7)
    envelope = _envelope(policy)
    before = envelope.to_json()
    view = OperatorIncidentView.from_evidence(envelope)
    assert view.to_dict()["evidence"] == envelope.to_dict()
    assert envelope.to_json() == before
