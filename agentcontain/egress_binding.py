"""Fail-closed provider boundary for declarative egress policy.

The platform owns Policy.allowed_egress as policy identity. A provider may
consume it only when it explicitly advertises the exact destination-allowlist
capability and exposes a binding operation.

Current AgentContainment providers do not satisfy this contract: their network
enforcement is deny-all containment. Absence of an explicit capability therefore
fails closed rather than being interpreted as support.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

DESTINATION_ALLOWLIST_CAPABILITY = "egress.destination_allowlist.v1"


class EgressBindingProvider(Protocol):
    """Provider contract for an explicitly supported destination allowlist."""

    @property
    def capabilities(self) -> frozenset[str]:
        """Return capabilities explicitly implemented by this provider."""

    def bind_egress(
        self,
        *,
        policy_id: str,
        policy_digest: str,
        agent_id: str,
        runtime_id: str,
        epoch: int,
        allowed_egress: Sequence[str],
    ):
        """Install and return provider-owned binding evidence."""


@dataclass(frozen=True)
class EgressBinding:
    """Validated result of one provider-owned egress binding."""

    policy_id: str
    policy_digest: str
    agent_id: str
    runtime_id: str
    epoch: int
    allowed_egress: tuple[str, ...]
    provider_evidence: object


class UnsupportedEgressBinding(RuntimeError):
    """Raised when a provider cannot explicitly enforce the requested policy."""


def bind_allowed_egress(
    provider: EgressBindingProvider,
    *,
    policy_id: str,
    policy_digest: str,
    agent_id: str,
    runtime_id: str,
    epoch: int,
    allowed_egress: Sequence[str],
) -> EgressBinding | None:
    """Bind policy egress only through an explicitly capable provider.

    An empty policy has no destination constraint and needs no provider binding.
    A non-empty policy must be consumed by a provider that explicitly implements
    the versioned destination-allowlist capability.
    """

    entries = tuple(allowed_egress)
    if not entries:
        return None

    capabilities = frozenset(getattr(provider, "capabilities", ()))
    if DESTINATION_ALLOWLIST_CAPABILITY not in capabilities:
        raise UnsupportedEgressBinding(
            "provider does not advertise "
            f"{DESTINATION_ALLOWLIST_CAPABILITY}; refusing to treat "
            "declarative allowed_egress as runtime enforcement"
        )

    bind = getattr(provider, "bind_egress", None)
    if not callable(bind):
        raise UnsupportedEgressBinding(
            "provider advertises destination-allowlist capability without "
            "a bind_egress implementation"
        )

    evidence = bind(
        policy_id=policy_id,
        policy_digest=policy_digest,
        agent_id=agent_id,
        runtime_id=runtime_id,
        epoch=epoch,
        allowed_egress=entries,
    )
    return EgressBinding(
        policy_id=policy_id,
        policy_digest=policy_digest,
        agent_id=agent_id,
        runtime_id=runtime_id,
        epoch=epoch,
        allowed_egress=entries,
        provider_evidence=evidence,
    )
