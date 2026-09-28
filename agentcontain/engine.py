"""Adapter boundary between AgentContain and AgentContainment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .evidence import EvidenceEnvelope
from .fleet import FleetRegistry
from .identity import ExecutionIdentity
from .policy import Policy
from .policy_distribution import PolicyBundle, PolicyRegistry
from .state import PlatformStateMachine


class ContainmentResult(Protocol):
    """Minimum result contract needed by the platform."""

    complete: bool


class ReceiptCapableResult(ContainmentResult, Protocol):
    """Containment result that can produce an authenticated receipt."""

    def to_receipt(
        self,
        secret: bytes,
        *,
        execution_id: str,
        policy_id: str,
    ): ...


class EnforcementEngine(Protocol):
    """Contract consumed by the platform adapter."""

    last_report: ReceiptCapableResult | None

    def contain(self) -> ContainmentResult: ...


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
    """Build evidence from the accepted policy, runtime report, and event log.

    Policy identity is taken from the admission's validated PolicyBundle, not
    from caller-supplied evidence fields. Runtime enforcement fields are
    projected from the authoritative AgentContainment report when available;
    the adapter never manufactures host-proof claims.
    """
    identity = admission.identity
    if identity.policy_id != admission.policy.policy_id:
        raise RuntimeError("admission policy_id diverges from accepted policy")
    if identity.policy_digest != admission.policy.policy_digest:
        raise RuntimeError("admission policy_digest diverges from accepted policy")

    events = tuple(event.to_dict() for event in admission.machine.events.events)
    governance = None if fleet is None else fleet.governance_for_agent(identity.agent_id)

    report = getattr(admission.engine, "last_report", None)
    if report is None:
        enforcement = {
            "complete": admission.machine.state.value in {
                "contained",
                "detected",
                "fenced",
                "halted",
                "verified",
                "recovering",
                "recovered",
            }
        }
        verification = {
            "status": "observed",
            "method": "agentcontain-platform-events",
        }
        proof = {}
    else:
        failures = tuple(getattr(report, "failures", ()))
        persistence_failures = tuple(getattr(report, "persistence_failures", ()))
        certified = bool(getattr(report, "certified", False))
        durable = bool(getattr(report, "durable", True))
        external_verified = bool(getattr(report, "external_verified", False))

        enforcement = {
            "complete": bool(getattr(report, "complete", False)),
            "external_verified": external_verified,
            "certified": certified,
            "durable": durable,
            "stages": list(getattr(report, "stages", ())),
            "failures": list(failures),
            "persistence_failures": list(persistence_failures),
            "enforcement_latency_seconds": getattr(
                report, "enforcement_latency_seconds", None
            ),
        }
        verification = {
            "status": (
                "verified"
                if certified and durable
                else "degraded"
                if failures or persistence_failures
                else "observed"
            ),
            "method": "agentcontainment-runtime-report",
            "scope": "runtime-enforcement",
        }
        proof = {
            "host_enforcement_verified": external_verified,
            "runtime_report": True,
        }

    return EvidenceEnvelope.from_execution(
        execution={
            "execution_id": identity.execution_id,
            "agent_id": identity.agent_id,
            "policy_id": admission.policy.policy_id,
            "policy_digest": admission.policy.policy_digest,
            "epoch": identity.epoch,
        },
        events=events,
        enforcement=enforcement,
        verification=verification,
        proof=proof,
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
