"""Typed policy distribution primitives for AgentContain.

The control plane may construct and distribute policy candidates, but the
runtime remains authoritative for validation and activation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .policy import Policy


@dataclass(frozen=True)
class PolicyBundle:
    """Transport-neutral, identity-bound representation of an accepted policy."""

    policy: Policy
    policy_digest: str
    canonical_document: str

    @classmethod
    def from_policy(cls, policy: Policy) -> "PolicyBundle":
        if not isinstance(policy, Policy):
            raise TypeError("policy must be a Policy")
        return cls(
            policy=policy,
            policy_digest=policy.digest,
            canonical_document=policy.canonical(),
        )

    def validate(self) -> None:
        """Validate policy identity against the canonical local representation."""
        if self.policy_digest != self.policy.digest:
            raise ValueError("policy digest does not match local policy")
        if self.canonical_document != self.policy.canonical():
            raise ValueError("policy canonical document does not match local policy")

    @property
    def policy_id(self) -> str:
        return self.policy.policy_id

    @property
    def policy_version(self) -> int:
        return self.policy.version


@dataclass
class PolicyRegistry:
    """Local authority for accepted policy versions.

    Distribution is advisory: only locally validated candidates can become
    active, and an older version cannot replace a newer accepted version.
    """

    _active: PolicyBundle | None = None

    @property
    def active(self) -> PolicyBundle | None:
        return self._active

    def accept(self, bundle: PolicyBundle) -> PolicyBundle:
        if not isinstance(bundle, PolicyBundle):
            raise TypeError("bundle must be a PolicyBundle")
        bundle.validate()

        active = self._active
        if active is not None:
            if bundle.policy_id != active.policy_id:
                raise ValueError("policy_id does not match active policy scope")
            if bundle.policy_version < active.policy_version:
                raise ValueError("stale policy version")
            if bundle.policy_version == active.policy_version and bundle.policy_digest != active.policy_digest:
                raise ValueError("policy version conflicts with active digest")

        self._active = bundle
        return bundle

    def accept_policy(self, policy: Policy) -> PolicyBundle:
        return self.accept(PolicyBundle.from_policy(policy))
