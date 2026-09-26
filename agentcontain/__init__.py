"""AgentContain platform primitives.

The platform layer defines policy, execution identity, lifecycle state, structured
events, and transport-neutral evidence around the AgentContainment engine.
"""

from .engine import Admission, admit, build_agentcontainment_engine, containment_receipt, evidence_envelope
from .events import Event, EventLog
from .evidence import EvidenceEnvelope, canonical_json
from .identity import ExecutionIdentity
from .policy import Policy
from .policy_distribution import PolicyBundle, PolicyRegistry
from .state import LifecycleState, PlatformStateMachine

__all__ = [
    "Admission",
    "Event",
    "EventLog",
    "EvidenceEnvelope",
    "ExecutionIdentity",
    "LifecycleState",
    "PlatformStateMachine",
    "Policy",
    "PolicyBundle",
    "PolicyRegistry",
    "admit",
    "build_agentcontainment_engine",
    "canonical_json",
    "containment_receipt",
    "evidence_envelope",
]
