from agentcontain import ExecutionIdentity, LifecycleState, PlatformStateMachine, Policy


def test_policy_digest_is_deterministic() -> None:
    a = Policy("production", capabilities=("network", "filesystem"), allowed_egress=("api.example", "db.example"))
    b = Policy("production", capabilities=("filesystem", "network"), allowed_egress=("db.example", "api.example"))
    assert a.digest == b.digest


def test_execution_identity_epoch_changes_without_changing_execution() -> None:
    identity = ExecutionIdentity.create("agent-1", "production", "digest")
    next_identity = identity.advance_epoch()
    assert next_identity.execution_id == identity.execution_id
    assert next_identity.epoch == identity.epoch + 1


def test_platform_lifecycle_records_monotonic_events() -> None:
    identity = ExecutionIdentity.create("agent-1", "production", "digest")
    machine = PlatformStateMachine(identity)
    machine.admit()
    machine.contain()
    machine.fence()
    machine.halt()
    machine.verify()
    machine.recover()
    machine.recovered()

    assert machine.state == LifecycleState.RECOVERED
    assert [e.sequence for e in machine.events.events] == list(range(1, 8))
    assert machine.events.events[0].name == "admission_verified"
    assert machine.events.events[-1].name == "runtime_recovery_complete"


def test_invalid_transition_is_rejected() -> None:
    identity = ExecutionIdentity.create("agent-1", "production", "digest")
    machine = PlatformStateMachine(identity)
    try:
        machine.halt()
    except ValueError:
        pass
    else:
        raise AssertionError("invalid transition was accepted")
