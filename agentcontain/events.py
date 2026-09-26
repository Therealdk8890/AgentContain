"""Structured platform events."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json


@dataclass(frozen=True)
class Event:
    name: str
    execution_id: str
    epoch: int
    sequence: int
    timestamp: str
    details: dict[str, str]

    @classmethod
    def create(cls, name: str, execution_id: str, epoch: int, sequence: int, *, details: dict[str, str] | None = None) -> "Event":
        if not name.strip():
            raise ValueError("event name must not be empty")
        return cls(
            name=name,
            execution_id=execution_id,
            epoch=epoch,
            sequence=sequence,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=dict(details or {}),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class EventLog:
    """Append-only in-memory event log for one platform execution."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def append(self, event: Event) -> None:
        if self._events and event.sequence <= self._events[-1].sequence:
            raise ValueError("event sequence must increase monotonically")
        if self._events and event.execution_id != self._events[-1].execution_id:
            raise ValueError("event execution_id does not match log")
        self._events.append(event)

    @property
    def events(self) -> tuple[Event, ...]:
        return tuple(self._events)

    def to_json(self) -> str:
        return json.dumps([event.to_dict() for event in self._events], sort_keys=True, indent=2) + "\n"
