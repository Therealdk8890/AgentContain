"""Adapter boundary between AgentContain and AgentContainment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .events import Event
from .identity import ExecutionIdentity
from .policy import Policy
from .state import PlatformStateMachine


class EnforcementEngine(Protocol):
    """Minimal enforcement contract consumed by the platform."""

    def contain(self): ...


@dataclass
class Admission:
    """Authoritative platform admission result."""

    identity: ExecutionIdentity
    machine: PlatformStateMachine
    engine: EnforcementEngine


def admit(
    policy: Policy,
    *,
    agent_id: str,
    engine: EnforcementEngine,
) -> Admission:
    """Admit one execution and bind it to policy and enforcement state.

    The platform creates the execution identity before invoking enforcement.
    The engine remains the authority for host/runtime containment.
    """
    identity = ExecutionIdentity.create(
        agent_id,
        policy.policy_id,
        policy.digest,
    )
    machine = PlatformStateMachine(identity)
    machine.admit()
    return Admission(identity=identity, machine=machine, engine=engine)


def contain(admission: Admission) -> object:
    """Invoke the external enforcement engine and record the platform event.

    The platform never treats a requested containment operation as proof of
    containment. The returned engine report remains the source of enforcement
    evidence; the platform event records that the operation completed.
    """
    report = admission.engine.contain()
    if not getattr(report, "complete", True):
        raise RuntimeError("enforcement engine reported containment failures")
    admission.machine.contain()
    return report


def build_agentcontainment_engine(agent_id: str) -> EnforcementEngine:
    """Construct the real AgentContainment controller.

    This import is deliberately isolated to the adapter so the platform's
    policy/state primitives remain independently testable.
    """
    try:
        from agent_containment.containment import ContainmentController
        from agent_containment.runtime import Runtime
    except ImportError as exc:
        raise RuntimeError(
            "AgentContainment is not installed; initialize the pinned submodule "
            "and install its Python package before using the runtime adapter"
        ) from exc

    runtime = Runtime(agent_id)
    return ContainmentController(runtime)
