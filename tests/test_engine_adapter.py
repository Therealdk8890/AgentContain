from dataclasses import dataclass

import pytest

from agentcontain import Policy
from agentcontain.engine import admit, contain


@dataclass(frozen=True)
class Report:
    complete: bool


class FakeEngine:
    def __init__(self, complete: bool = True) -> None:
        self.complete = complete
        self.calls = 0

    def contain(self) -> Report:
        self.calls += 1
        return Report(self.complete)


def test_admission_binds_policy_and_engine() -> None:
    engine = FakeEngine()
    admission = admit(Policy("production"), agent_id="agent-1", engine=engine)

    assert admission.identity.agent_id == "agent-1"
    assert admission.identity.policy_id == "production"
    assert admission.identity.policy_digest == Policy("production").digest
    assert admission.machine.state.value == "admitted"


def test_containment_calls_engine_before_recording_platform_state() -> None:
    engine = FakeEngine()
    admission = admit(Policy("production"), agent_id="agent-1", engine=engine)

    report = contain(admission)

    assert report.complete
    assert engine.calls == 1
    assert admission.machine.state.value == "contained"
    assert admission.machine.events.events[-1].name == "containment_verified"


def test_failed_engine_does_not_create_containment_event() -> None:
    engine = FakeEngine(complete=False)
    admission = admit(Policy("production"), agent_id="agent-1", engine=engine)

    with pytest.raises(RuntimeError, match="containment failures"):
        contain(admission)

    assert engine.calls == 1
    assert admission.machine.state.value == "admitted"
    assert admission.machine.events.events[-1].name == "admission_verified"
