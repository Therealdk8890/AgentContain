"""Transport-neutral boundary for authorization supplied by an external identity system.

External authorization is an input to WarrantKit admission, not a replacement for
WarrantKit's policy, identity, epoch, or runtime enforcement authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

from .policy import Policy
from .warrant import EvidenceRequirements, Warrant


SCHEMA_VERSION = "warrantkit.external-authorization/v1"


@dataclass(frozen=True)
class ExternalAuthorizationDecision:
    """A narrow authorization decision imported from an external control plane.

    The decision carries authorization context only. It cannot supply evidence,
    mutate the local policy, select the runtime epoch, or perform enforcement.
    """

    decision_id: str
    issuer: str
    subject_agent_id: str
    subject_execution_id: str
    policy_id: str
    policy_digest: str
    capabilities: tuple[str, ...] = ()
    constraints: tuple[tuple[str, str], ...] = ()
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    decision: str = "allow"
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("decision_id", self.decision_id),
            ("issuer", self.issuer),
            ("subject_agent_id", self.subject_agent_id),
            ("subject_execution_id", self.subject_execution_id),
            ("policy_id", self.policy_id),
            ("policy_digest", self.policy_digest),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported authorization schema: {self.schema_version}")
        if self.decision != "allow":
            raise ValueError("only allow decisions can be imported as Warrant authority")
        if self.issued_at is not None and self.issued_at.tzinfo is None:
            raise ValueError("issued_at must be timezone-aware")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        if self.issued_at is not None and self.expires_at is not None:
            if self.expires_at <= self.issued_at:
                raise ValueError("expires_at must be after issued_at")

    def to_warrant(
        self,
        *,
        policy: Policy,
        runtime_id: str,
        epoch: int,
        issued_at: datetime | None = None,
        expires_at: datetime | None = None,
        evidence_requirements: EvidenceRequirements | None = None,
    ) -> Warrant:
        """Convert external authorization into local, epoch-bound Warrant authority.

        The locally accepted policy remains authoritative. A mismatched external
        policy identity or digest fails closed instead of widening local authority.
        """
        if self.policy_id != policy.policy_id:
            raise ValueError("external authorization policy_id does not match accepted policy")
        if self.policy_digest != policy.digest:
            raise ValueError("external authorization policy_digest does not match accepted policy")
        now = issued_at or self.issued_at or datetime.now(timezone.utc)
        expiry = expires_at or self.expires_at
        if expiry is None:
            raise ValueError("an authorization expiry is required")
        if now.tzinfo is None or expiry.tzinfo is None:
            raise ValueError("warrant validity timestamps must be timezone-aware")
        return Warrant.issue(
            warrant_id=f"external:{self.decision_id}",
            issuer=self.issuer,
            agent_id=self.subject_agent_id,
            execution_id=self.subject_execution_id,
            policy=policy,
            runtime_id=runtime_id,
            epoch=epoch,
            issued_at=now,
            expires_at=expiry,
            capabilities=self.capabilities,
            constraints=self.constraints,
            evidence_requirements=evidence_requirements,
        )


def import_authorization(
    document: Mapping[str, object],
    *,
    policy: Policy,
    runtime_id: str,
    epoch: int,
    now: datetime | None = None,
) -> Warrant:
    """Import a minimal external decision without importing external evidence."""
    required = {
        "schema_version", "decision_id", "issuer", "subject_agent_id",
        "subject_execution_id", "policy_id", "policy_digest", "capabilities",
        "constraints", "issued_at", "expires_at", "decision",
    }
    if set(document) != required:
        raise ValueError("external authorization has an invalid shape")
    issued_at = datetime.fromisoformat(str(document["issued_at"]))
    expires_at = datetime.fromisoformat(str(document["expires_at"]))
    decision = ExternalAuthorizationDecision(
        decision_id=str(document["decision_id"]),
        issuer=str(document["issuer"]),
        subject_agent_id=str(document["subject_agent_id"]),
        subject_execution_id=str(document["subject_execution_id"]),
        policy_id=str(document["policy_id"]),
        policy_digest=str(document["policy_digest"]),
        capabilities=tuple(document["capabilities"]),  # type: ignore[arg-type]
        constraints=tuple((str(k), str(v)) for k, v in dict(document["constraints"]).items()),  # type: ignore[arg-type]
        issued_at=issued_at,
        expires_at=expires_at,
        decision=str(document["decision"]),
        schema_version=str(document["schema_version"]),
    )
    warrant = decision.to_warrant(
        policy=policy,
        runtime_id=runtime_id,
        epoch=epoch,
    )
    if now is not None:
        if now.tzinfo is None:
            raise ValueError("verification time must be timezone-aware")
        if now < warrant.validity.issued_at or now >= warrant.validity.expires_at:
            raise ValueError("external authorization is outside its validity window")
    return warrant
