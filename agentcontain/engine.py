"""Adapter boundary between AgentContain and AgentContainment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .evidence import EvidenceEnvelope
from .identity import ExecutionIdentity
from .policy import Policy
from .state import PlatformStateMachine


class EnforcementEngine(Protocol):
    """Minimal enforcement contract consumed by the platform."""

    def contain(self): ...

    def receipt(self, secret: bytes, *, execution_id: str, policy_id: str): ...


@dataclass
class Admission:
    """Authoritative platform admission result."""

    identity: ExecutionIdentity
    machine: PlatformStateMachine
    engine: EnforcementEngine


def admit(policy: Policy, *, agent_id: str, engine: EnforcementEngine) -> Admission:
    """Admit one execution and bind it to AgentContainment enforcement."""
    identity = ExecutionIdentity.create(agent_id, policy.policy_id, policy.digest)
    machine = PlatformStateMachine(identity)
    machine.admit()
    return Admission(identity=identity, machine=machine, engine=engine)


def contain(admission: Admission) -> object:
    """Invoke AgentContainment and record the successful platform transition."""
    report = admission.engine.contain()
    if not getattr(report, "complete", True):
        raise RuntimeError(
            "enforcement engine reported containment failures: "
            + "; ".join(getattr(report, "failures", ()))
        )
    admission.machine.contain()
    return report


def containment_receipt(admission: Admission, secret: bytes):
    """Create a signed/tamper-evident receipt bound to platform identity."""
    report = getattr(admission.engine, "last_report", None)
    if report is None:
        raise RuntimeError("containment has not been executed")
    return report.to_receipt(
        secret,
        execution_id=admission.identity.execution_id,
        policy_id=admission.identity.policy_id,
    )


def evidence_envelope(
    admission: Admission,
    *,
    report: object | None = None,
    receipt: object | None = None,
) -> EvidenceEnvelope:
    """Build portable evidence from one admitted execution.

    Receipt creation remains separate so callers can choose whether to include
    authenticated receipt material. When supplied, the receipt is bound to the
    platform execution identity without rewriting its cryptographic fields.
    """
    enforcement = {}
    verification = {"status": "observed", "method": "platform-lifecycle"}
    proof = {}
    if report is not None:
        enforcement = {
            "complete": bool(getattr(report, "complete", False)),
            "external_verified": bool(getattr(report, "external_verified", False)),
            "failures": list(getattr(report, "failures", ())),
        }
        certified = bool(getattr(report, "certified", False))
        durable = bool(getattr(report, "durable", False))
        verification = {
            "status": "verified" if certified and durable else "degraded",
            "method": "agentcontainment",
            "certified": certified,
            "durable": durable,
            "enforcement_latency_seconds": getattr(
                report, "enforcement_latency_seconds", None
            ),
        }
        proof = {
            "claims": list(getattr(report, "stages", ())),
        }

    envelope = EvidenceEnvelope.from_execution(
        execution={
            "execution_id": admission.identity.execution_id,
            "agent_id": admission.identity.agent_id,
            "policy_id": admission.identity.policy_id,
            "policy_digest": admission.identity.policy_digest,
            "epoch": admission.identity.epoch,
        },
        events=tuple(event.to_dict() for event in admission.machine.events.events),
        enforcement=enforcement,
        verification=verification,
        proof=proof,
        provenance={"producer": "agentcontain"},
    )
    if receipt is not None:
        envelope = envelope.with_receipt(
            receipt.to_dict() if hasattr(receipt, "to_dict") else receipt
        )
    return envelope
