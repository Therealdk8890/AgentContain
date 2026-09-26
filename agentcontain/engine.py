"""Adapter boundary between AgentContain and AgentContainment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

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
        raise RuntimeError("enforcement engine reported containment failures")
    admission.machine.contain()
    return report


def containment_receipt(admission: Admission, secret: bytes):
    """Create a signed/tamper-evident receipt bound to platform identity."""
    report = getattr(admission.engine, "last_report", None)
    if report is None:
        raise RuntimeError("containment has not been executed")
    return report.to_receipt(secret, execution_id=admission.identity.execution_id, policy_id=admission.identity.policy_id)


def build_agentcontainment_engine(agent_id: str, *, cgroup_path: str | None = None) -> EnforcementEngine:
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