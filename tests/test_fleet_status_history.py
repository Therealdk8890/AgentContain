from agentcontain.fleet_status import FleetPolicyStatus
from agentcontain.fleet_status_history import (
    FleetPolicyStatusHistory,
    FleetPolicyStatusSnapshot,
)


def _status(converged: int, total: int = 3) -> FleetPolicyStatus:
    return FleetPolicyStatus(
        rollout_id="rollout-1",
        total_targets=total,
        converged=converged,
        pending=total - converged,
        drifted=0,
        missing=0,
        rejected=0,
        superseded=0,
    )


def test_history_preserves_append_order_and_latest():
    history = FleetPolicyStatusHistory()
    first = FleetPolicyStatusSnapshot("snapshot-1", 1, _status(0))
    second = FleetPolicyStatusSnapshot("snapshot-2", 2, _status(2))

    assert history.append(first) == first
    assert history.append(second) == second
    assert history.latest() == second
    assert history.all() == (first, second)


def test_history_is_idempotent_for_identical_snapshot():
    history = FleetPolicyStatusHistory()
    snapshot = FleetPolicyStatusSnapshot("snapshot-1", 1, _status(1))

    assert history.append(snapshot) == snapshot
    assert history.append(snapshot) == snapshot
    assert history.all() == (snapshot,)


def test_history_rejects_snapshot_id_collision():
    history = FleetPolicyStatusHistory()
    history.append(FleetPolicyStatusSnapshot("snapshot-1", 1, _status(1)))

    different = FleetPolicyStatusSnapshot("snapshot-1", 2, _status(2))

    try:
        history.append(different)
    except ValueError as exc:
        assert "collision" in str(exc)
    else:
        raise AssertionError("expected snapshot ID collision")


def test_history_rejects_non_monotonic_sequence():
    history = FleetPolicyStatusHistory()
    history.append(FleetPolicyStatusSnapshot("snapshot-1", 4, _status(1)))

    try:
        history.append(FleetPolicyStatusSnapshot("snapshot-2", 4, _status(2)))
    except ValueError as exc:
        assert "increase monotonically" in str(exc)
    else:
        raise AssertionError("expected non-monotonic sequence rejection")


def test_snapshot_is_machine_readable():
    snapshot = FleetPolicyStatusSnapshot("snapshot-1", 7, _status(3))

    assert snapshot.to_dict() == {
        "snapshot_id": "snapshot-1",
        "sequence": 7,
        "status": {
            "rollout_id": "rollout-1",
            "total_targets": 3,
            "converged": 3,
            "pending": 0,
            "drifted": 0,
            "missing": 0,
            "rejected": 0,
            "superseded": 0,
            "is_converged": True,
        },
    }
