"""AgentContain platform primitives.

The platform layer defines policy, execution identity, lifecycle state, structured
events, and transport-neutral evidence around the AgentContainment engine.
"""

from .events import Event, EventLog
from .evidence import EvidenceEnvelope, canonical_json
from .identity import ExecutionIdentity
from .policy import Policy
from .state import LifecycleState, PlatformStateMachine

__all__ = [
    "Event",
    "EventLog",
    "EvidenceEnvelope",
    "ExecutionIdentity",
    "LifecycleState",
    "PlatformStateMachine",
    "Policy",
    "canonical_json",
]
