"""AgentContain platform primitives.

The platform layer defines policy, execution identity, lifecycle state, structured
events, and transport-neutral evidence around the AgentContainment engine.
"""

from .engine import Admission, admit, build_agentcontainment_engine, containment_receipt, evidence_envelope
from .events import Event, EventLog
from .evidence import EvidenceEnvelope, canonical_json
from .fleet import Agent, FleetRegistry, FleetScope, Organization, Project, Runtime
from .identity import ExecutionIdentity
from .policy import Policy
from .policy_assignment import AssignmentState, PolicyAssignment, PolicyAssignmentRegistry
from .policy_rollout import Rollout, RolloutState
from .policy_distribution import PolicyBundle, PolicyRegistry
from .state import LifecycleState, PlatformStateMachine
from .store import EvidenceStore, InMemoryEvidenceStore

__all__ = [
    "Admission",
    "Event",
    "EventLog",
    "EvidenceStore",
    "InMemoryEvidenceStore",
    "EvidenceEnvelope",
    "Agent",
    "FleetRegistry",
    "FleetScope",
    "Organization",
    "Project",
    "Runtime",
    "ExecutionIdentity",
    "LifecycleState",
    "PlatformStateMachine",
    "Policy",
    "AssignmentState",
    "PolicyAssignment",
    "PolicyAssignmentRegistry",
    "Rollout",
    "RolloutState",
    "PolicyBundle",
    "PolicyRegistry",
    "admit",
    "build_agentcontainment_engine",
    "canonical_json",
    "containment_receipt",
    "evidence_envelope",
]
