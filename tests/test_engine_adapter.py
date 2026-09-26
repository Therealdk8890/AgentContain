from dataclasses import dataclass

import pytest

from agentcontain import Policy
from agentcontain.engine import admit, contain, containment_receipt, evidence_envelope


@dataclass(frozen=True)
class Report:
    complete: bool


class FakeEngine:
    def __init__(self, complete=True):
        self.complete = complete
        self.calls = 0
        self.last_report = None

    def contain(self):
        self.calls += 1
        self.last_report = Report(self.complete)
        return self.last_report


def test_admission_binds_policy_and_engine():
    engine = FakeEngine()
    admission = admit(Policy("production"), agent_id="agent-1", engine=engine)
    assert admission.identity.agent_id == "agent-1"
    assert admission.identity.policy_id == "production"
    assert admission.identity.policy_digest == Policy("production").digest
    assert admission.machine.state.value == "admitted"


def test_containment_calls_engine_before_recording_platform_state():
    engine = FakeEngine()
    admission = admit(Policy("production"), agent_id="agent-1", engine=engine)
    report = contain(admission)
    assert report.complete
    assert engine.calls == 1
    assert admission.machine.state.value == "contained"
    assert admission.machine.events.events[-1].name == "containment_verified"


def test_failed_engine_does_not_create_containment_event():
    engine = FakeEngine(complete=False)
    admission = admit(Policy("production"), agent_id="agent-1", engine=engine)
    with pytest.raises(RuntimeError, match="containment failures"):
        contain(admission)
    assert engine.calls == 1
    assert admission.machine.state.value == "admitted"
    assert admission.machine.events.events[-1].name == "admission_verified"


def test_containment_receipt_binds_platform_identity():
    class ReceiptReport:
        complete = True
        def to_receipt(self, secret, *, execution_id, policy_id):
            return type("Receipt", (), {"execution_id": execution_id, "policy_id": policy_id})()

    class ReceiptEngine(FakeEngine):
        def contain(self):
            self.calls += 1
            self.last_report = ReceiptReport()
            return self.last_report

    engine = ReceiptEngine()
    admission = admit(Policy("production"), agent_id="agent-1", engine=engine)
    contain(admission)
    receipt = containment_receipt(admission, b"secret")
    assert receipt.execution_id == admission.identity.execution_id
    assert receipt.policy_id == "production"

def test_evidence_uses_locally_accepted_policy_identity():
    policy = Policy("production", version=7, capabilities=("read",))
    engine = FakeEngine()
    admission = admit(policy, agent_id="agent-1", engine=engine)

    evidence = evidence_envelope(admission)

    assert evidence.execution["policy_id"] == policy.policy_id
    assert evidence.execution["policy_digest"] == policy.digest
    assert evidence.execution["epoch"] == admission.identity.epoch


def test_evidence_rejects_admission_policy_divergence():
    policy = Policy("production", version=1)
    engine = FakeEngine()
    admission = admit(policy, agent_id="agent-1", engine=engine)
    conflicting = Policy("production", version=2)
    object.__setattr__(
        admission,
        "policy",
        type(admission.policy).from_policy(conflicting),
    )

    with pytest.raises(RuntimeError, match="policy_id|policy_digest"):
        evidence_envelope(admission)


def test_evidence_can_bind_validated_fleet_governance_scope():
    from agentcontain.fleet import Agent, FleetRegistry, Organization, Project, Runtime

    fleet = FleetRegistry()
    organization = fleet.register_organization(Organization.create("acme"))
    project = fleet.register_project(Project.create(organization.organization_id, "payments"))
    runtime = fleet.register_runtime(Runtime.create(project.project_id, "prod"))
    agent = fleet.register_agent(Agent.create(runtime.runtime_id, "checkout", agent_id="agent-1"))

    admission = admit(Policy("production"), agent_id=agent.agent_id, engine=FakeEngine())
    evidence = evidence_envelope(admission, fleet=fleet)

    assert evidence.governance == {
        "organization_id": organization.organization_id,
        "project_id": project.project_id,
        "runtime_id": runtime.runtime_id,
        "agent_id": agent.agent_id,
    }


def test_evidence_governance_requires_registered_agent():
    from agentcontain.fleet import FleetRegistry

    admission = admit(Policy("production"), agent_id="unregistered", engine=FakeEngine())

    with pytest.raises(KeyError):
        evidence_envelope(admission, fleet=FleetRegistry())
