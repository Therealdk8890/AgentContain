"""Immutable fleet policy status history primitives.

History is an operational record above runtime enforcement. It never changes
assignments, rollout state, or enforcement authority.
"""

from __future__ import annotations

from dataclasses import dataclass

from .fleet_status import FleetPolicyStatus


@dataclass(frozen=True)
class FleetPolicyStatusSnapshot:
    """One immutable point-in-time status observation."""

    snapshot_id: str
    sequence: int
    status: FleetPolicyStatus

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshot_id": self.snapshot_id,
            "sequence": self.sequence,
            "status": self.status.to_dict(),
        }


class FleetPolicyStatusHistory:
    """Append-only local reference history for fleet status snapshots."""

    def __init__(self) -> None:
        self._items: dict[str, FleetPolicyStatusSnapshot] = {}
        self._order: list[str] = []

    def append(self, snapshot: FleetPolicyStatusSnapshot) -> FleetPolicyStatusSnapshot:
        if not isinstance(snapshot, FleetPolicyStatusSnapshot):
            raise TypeError("snapshot must be a FleetPolicyStatusSnapshot")
        if snapshot.sequence < 0:
            raise ValueError("snapshot sequence must be non-negative")

        existing = self._items.get(snapshot.snapshot_id)
        if existing is not None:
            if existing != snapshot:
                raise ValueError(
                    f"fleet status snapshot collision: {snapshot.snapshot_id}"
                )
            return existing

        if self._order:
            latest = self._items[self._order[-1]]
            if snapshot.sequence <= latest.sequence:
                raise ValueError("snapshot sequence must increase monotonically")

        self._items[snapshot.snapshot_id] = snapshot
        self._order.append(snapshot.snapshot_id)
        return snapshot

    def get(self, snapshot_id: str) -> FleetPolicyStatusSnapshot | None:
        return self._items.get(snapshot_id)

    def latest(self) -> FleetPolicyStatusSnapshot | None:
        if not self._order:
            return None
        return self._items[self._order[-1]]

    def all(self) -> tuple[FleetPolicyStatusSnapshot, ...]:
        return tuple(self._items[snapshot_id] for snapshot_id in self._order)
