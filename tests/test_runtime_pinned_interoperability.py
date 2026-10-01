"""Cross-repo runtime-pinned evidence interoperability tests."""

import os
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def agent_containment_src():
    src = Path(__file__).parents[1] / "AgentContainment" / "src"
    if not src.exists():
        pytest.skip("AgentContainment submodule is unavailable")
    sys.path.insert(0, str(src))
    try:
        yield src
    finally:
        sys.path.remove(str(src))


class TestEnforcer:
    name = "test-external"

    def contain(self, agent_id):
        from agent_containment.enforcer import EnforcementResult, EnforcementStatus

        return EnforcementResult(self.name, EnforcementStatus.ENFORCED, "test boundary enforced")

    def verify_contained(self, agent_id):
        from agent_containment.enforcer import EnforcementResult, EnforcementStatus

        return EnforcementResult(self.name, EnforcementStatus.ENFORCED, "test boundary verified")


@pytest.mark.skipif(
    os.environ.get("WARRANTKIT_RUN_RUNTIME_INTEROP") != "1",
    reason="set WARRANTKIT_RUN_RUNTIME_INTEROP=1 to run the cross-repo integration contract",
)
def test_real_agentcontainment_evidence_round_trips_through_warrantkit(agent_containment_src):
    from agent_containment.containment import ContainmentController
    from agent_containment.control import ContainmentService
    from agent_containment.runtime import Runtime
    from agent_containment.runtime_observation import RuntimeObservationSource

    from agentcontain.engine import (
        AgentContainmentRuntimeAdapter,
        admit,
        contain,
        runtime_pinned_evidence,
    )
    from agentcontain.policy import Policy

    agent_id = "interop-agent"
    runtime = Runtime(agent_id)
    controller = ContainmentController(runtime, enforcers=[TestEnforcer()])
    adapter = AgentContainmentRuntimeAdapter(
        agent_id,
        controller,
        ContainmentService(),
    )

    admission = admit(
        Policy("production"),
        agent_id=agent_id,
        runtime_id=runtime.runtime_id,
        engine=adapter,
    )

    report = contain(admission)
    assert report.epoch == admission.identity.epoch == 1

    observation = RuntimeObservationSource().observe(runtime)
    envelope = runtime_pinned_evidence(admission, observation=observation)

    assert envelope.verification["status"] == "verified"
    binding = envelope.proof["runtime_binding"]
    assert binding["runtime_id"] == runtime.runtime_id
    assert binding["agent_id"] == agent_id
    assert binding["epoch"] == 1
    assert binding["authority"]["record"]["revoked"] is True
    assert binding["enforcement"]["record"]["external_boundary"] is True
    assert binding["enforcement"]["record"]["action"] == "KILL"
    assert binding["observation"]["record"]["can_execute"] is False
    assert binding["observation"]["record"]["state"] == "contained"
