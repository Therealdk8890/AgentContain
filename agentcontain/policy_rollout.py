"""Deterministic fleet policy rollout state.

Rollout state is governance intent and observation. Local runtimes remain
authoritative for accepting and enforcing the assigned policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .policy_assignment import PolicyAssignmentRegistry
from .policy_distribution import PolicyBundle


class RolloutState(StrEnum):
    DRAFT = "draft"
    STAGED = "staged"
    ROLLING_OUT = "rolling_out"
    CONVERGED = "converged"
    PAUSED = "paused"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Rollout:
    rollout_id: str
    policy_id: str
    policy_version: int
    policy_digest: str
    targets: tuple[str, ...]
    state: RolloutState = RolloutState.DRAFT

    @classmethod
    def create(
        cls,
        rollout_id: str,
        bundle: PolicyBundle,
        targets: tuple[str, ...],
    ) -> "Rollout":
        if not rollout_id.strip():
            raise ValueError("rollout_id must not be empty")
        if not targets or any(not target.strip() for target in targets):
            raise ValueError("rollout targets must not be empty")
        if len(set(targets)) != len(targets):
            raise ValueError("rollout targets must be unique")
        bundle.validate()
        return cls(
            rollout_id=rollout_id,
            policy_id=bundle.policy_id,
            policy_version=bundle.policy_version,
            policy_digest=bundle.policy_digest,
            targets=tuple(targets),
        )

    def stage(self) -> "Rollout":
        if self.state != RolloutState.DRAFT:
            raise ValueError("only draft rollouts can be staged")
        return self._with(RolloutState.STAGED)

    def start(self) -> "Rollout":
        if self.state != RolloutState.STAGED:
            raise ValueError("only staged rollouts can start")
        return self._with(RolloutState.ROLLING_OUT)

    def pause(self) -> "Rollout":
        if self.state != RolloutState.ROLLING_OUT:
            raise ValueError("only active rollouts can be paused")
        return self._with(RolloutState.PAUSED)

    def resume(self) -> "Rollout":
        if self.state != RolloutState.PAUSED:
            raise ValueError("only paused rollouts can resume")
        return self._with(RolloutState.ROLLING_OUT)

    def reject(self) -> "Rollout":
        if self.state in {RolloutState.CONVERGED, RolloutState.REJECTED}:
            raise ValueError("rollout is already terminal")
        return self._with(RolloutState.REJECTED)

    def converge(self, assignments: PolicyAssignmentRegistry) -> "Rollout":
        if self.state not in {RolloutState.ROLLING_OUT, RolloutState.PAUSED}:
            raise ValueError("rollout is not in progress")
        for target_id in self.targets:
            matching = [
                assignment
                for assignment in assignments.all()
                if assignment.target_id == target_id
                and assignment.policy_id == self.policy_id
                and assignment.policy_version == self.policy_version
                and assignment.policy_digest == self.policy_digest
            ]
            if not matching or not any(
                assignment.state.value == "active" for assignment in matching
            ):
                raise ValueError("rollout has not converged on all targets")
        return self._with(RolloutState.CONVERGED)

    def _with(self, state: RolloutState) -> "Rollout":
        return Rollout(
            rollout_id=self.rollout_id,
            policy_id=self.policy_id,
            policy_version=self.policy_version,
            policy_digest=self.policy_digest,
            targets=self.targets,
            state=state,
        )


# Keep rollout logic dependent only on the assignment interface, not on HTTP,
# SaaS, billing, or control-plane availability.
