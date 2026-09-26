"""Adapter boundary between AgentContain and AgentContainment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .evidence import EvidenceEnvelope
from .fleet import FleetRegistry
from .fleet import FleetRegistry
from .identity import ExecutionIdentity
from .policy import Policy
from .policy_distribution import PolicyBundle, PolicyRegistry
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
    policy: PolicyBundle


def admit(
    policy: Policy,
    *,
    agent_id: str,
    engine: EnforcementEngine,
    registry: PolicyRegistry | None = None,
) -> Admission:
    """Validate and admit one execution against the locally accepted policy."""
    registry = registry or PolicyRegistry()
    bundle = registry.accept_policy(policy)
    identity = ExecutionIdentity.create(
        agent_id,
        bundle.policy_id,
        bundle.policy_digest,
    )
    machine = PlatformStateMachine(identity)
    machine.admit()
    return Admission(
        identity=identity,
        machine=machine,
        engine=engine,
        policy=bundle,
    )


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


def evidence_envelope(admission: Admission, *, fleet: FleetRegistry | None = None) -> EvidenceEnvelope:
    """Build evidence from the locally accepted policy and platform event log.

    Policy identity is taken from the admission's validated PolicyBundle, not
    from caller-supplied evidence fields. This keeps distributed policy
    metadata advisory while the local runtime remains authoritative.
    """
    identity = admission.identity
    if identity.policy_id != admission.policy.policy_id:
        raise RuntimeError("admission policy_id diverges from accepted policy")
    if identity.policy_digest != admission.policy.policy_digest:
        raise RuntimeError("admission policy_digest diverges from accepted policy")

    events = tuple(event.to_dict() for event in admission.machine.events.events)
    governance = None if fleet is None else fleet.governance_for_agent(identity.agent_id)
    governance = None if fleet is None else fleet.governance_for_agent(identity.agent_id)
    return EvidenceEnvelope.from_execution(
        execution={
            "execution_id": identity.execution_id,
            "agent_id": identity.agent_id,
            "policy_id": admission.policy.policy_id,
            "policy_digest": admission.policy.policy_digest,
            "epoch": identity.epoch,
        },
        events=events,
        enforcement={
            "complete": admission.machine.state.value in {
                "contained",
                "detected",
                "fenced",
                "halted",
                "verified",
                "recovering",
                "recovered",
            }
        },
        verification={
            "status": "observed",
            "method": "agentcontain-platform-events",
        },
        proof={},
        governance=governance,
        provenance={"producer": "agentcontain"},
    )


def build_agentcontainment_engine(
    agent_id: str,
    *,
    cgroup_path: str | None = None,
) -> EnforcementEngine:
    """Construct the pinned AgentContainment controller.

    If cgroup_path is supplied, use the real cgroup-v2 enforcement provider.
    The adapter never guesses or broadens the host trust boundary.
    """
    try:
        from agent_containment.containment import ContainmentController
        from agent_containment.cgroup_enforcer import CgroupV2Enforcer
        from agent_containment.runtime import Runtime
    except ImportError as exc:
        raise RuntimeError(
            "AgentContainment is not installed; initialize the pinned submodule "
            "and install its Python package before using the runtime adapter"
        ) from exc

    runtime = Runtime(agent_id)
    if cgroup_path is None:
        return ContainmentController(runtime)
    enforcer = CgroupV2Enforcer({agent_id: cgroup_path})
    return ContainmentController(runtime, enforcers=[enforcer])
