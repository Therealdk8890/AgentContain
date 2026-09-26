"""AgentContain platform primitives.

The platform layer defines policy, execution identity, lifecycle state, and
structured events around the AgentContainment enforcement engine.
"""

from .events import Event, EventLog
from .identity import ExecutionIdentity
from .policy import Policy
from .state import LifecycleState, PlatformStateMachine

__all__ = [
    "Event",
    "EventLog",
    "ExecutionIdentity",
    "LifecycleState",
    "PlatformStateMachine",
    "Policy",
]
