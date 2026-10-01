"""Adversarial security regressions for the WarrantKit control boundary.

These tests model hostile or malformed inputs rather than happy-path lifecycle
behavior. The goal is to make security invariants executable: stale runtime
proof must not cross an epoch, external evidence must not become authority,
and malformed/tampered evidence must fail closed.
"""

import pytest

from agentcontain.engine import (
    admit,
    contain,
    evidence_envelope,
    recover,
    issue_recovery_authorization,
    verify,
)
from agentcontain.evidence import EvidenceEnvelope
from agentcontain.external_evidence import ExternalEvidenceReference
from agentcontain.policy import Policy


class Report:
    epoch = 1
    complete = True
    certified = True
    durable = True
    external_verified = True
    stages = ("runtime_fenced", "enforcer:cgroup-v2:verified")
    failures = ()
    persistence_failures = ()


class Engine:
    def __init__(self):
        self.last_report = None

    def contain(self):
        self.last_report = Report()
        return self.last_report

    def issue_recovery_authorization(self):
        return object()

    def recover(self, authorization):
        return 2


def _admission():
    return admit(Policy("production"), agent_id="agent-1", engine=Engine())


def _external_reference():
    return ExternalEvidenceReference(
        source="agentcontainment",
        reference_id="runtime-proof-1",
        digest="sha256:" + "a" * 64,
        relation="attests",
        captured_at="2026-09-29T00:00:00Z",
    )


def test_replayed_runtime_report_cannot_verify_a_new_epoch():
    admission = _admission()
    contain(admission)

    assert admission.identity.epoch == 1
    verify(admission)

    recover(admission, issue_recovery_authorization(admission))

    assert admission.identity.epoch == 2
    with pytest.raises(RuntimeError, match="runtime verification report is unavailable"):
        verify(admission)


def test_replayed_runtime_report_cannot_be_projected_into_new_evidence():
    admission = _admission()
    contain(admission)
    recover(admission, issue_recovery_authorization(admission))

    evidence = evidence_envelope(admission)

    assert evidence.execution["epoch"] == 2
    assert evidence.verification["status"] == "observed"
    assert evidence.verification["reason"] == "runtime-report-epoch-mismatch"
    assert evidence.proof == {}


def test_tampered_event_epoch_is_rejected():
    admission = _admission()
    contain(admission)
    document = evidence_envelope(admission).to_dict()
    document["events"][0]["epoch"] = admission.identity.epoch + 1

    with pytest.raises(ValueError, match="event epoch does not match"):
        EvidenceEnvelope.from_dict(document)


def test_tampered_event_sequence_is_rejected():
    admission = _admission()
    contain(admission)
    document = evidence_envelope(admission).to_dict()
    document["events"][0]["sequence"] = 2

    with pytest.raises(ValueError, match="contiguous"):
        EvidenceEnvelope.from_dict(document)


def test_external_evidence_cannot_upgrade_observed_state_to_verified():
    admission = _admission()
    references = (_external_reference(),)

    evidence = EvidenceEnvelope.from_execution(
        execution={
            "execution_id": admission.identity.execution_id,
            "agent_id": admission.identity.agent_id,
            "policy_id": admission.identity.policy_id,
            "policy_digest": admission.identity.policy_digest,
            "epoch": admission.identity.epoch,
        },
        events=(
            {
                "execution_id": admission.identity.execution_id,
                "sequence": 1,
                "name": "admission_verified",
                "epoch": admission.identity.epoch,
            },
        ),
        verification={"status": "observed", "method": "external-reference"},
        external_evidence=references,
    )

    assert evidence.verification["status"] == "observed"
    assert evidence.external_evidence == references


def test_external_evidence_cannot_introduce_an_authority_relation():
    reference = _external_reference()
    document = reference.to_dict()
    document["relation"] = "authorizes"

    with pytest.raises(ValueError, match="unsupported evidence relation"):
        ExternalEvidenceReference.from_dict(document)


def test_verified_evidence_without_events_fails_closed():
    with pytest.raises(ValueError, match="requires at least one event"):
        EvidenceEnvelope.from_execution(
            execution={
                "execution_id": "exec-1",
                "agent_id": "agent-1",
                "policy_id": "production",
                "policy_digest": "digest",
                "epoch": 0,
            },
            verification={"status": "verified"},
        )
