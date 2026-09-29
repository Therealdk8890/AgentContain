from __future__ import annotations

import pytest

from agentcontain.engine import (
    AgentContainmentRuntimeAdapter,
    build_agentcontainment_engine,
)


def test_warrantkit_runtime_wires_revocable_credentials_into_containment():
    engine = build_agentcontainment_engine("agent-credential-test")

    assert isinstance(engine, AgentContainmentRuntimeAdapter)
    credentials = engine.credential_store
    assert credentials is not None

    lease = credentials.issue("prod-api")
    assert credentials.valid(lease)

    report = engine.contain()

    assert report.complete
    assert "credentials_revoked" in report.stages
    assert not credentials.valid(lease)


def test_warrantkit_runtime_rejects_stale_credential_after_containment():
    engine = build_agentcontainment_engine("agent-credential-stale-test")
    credentials = engine.credential_store
    lease = credentials.issue("prod-api")

    engine.contain()
    executed: list[str] = []

    result = credentials.execute_if_valid(
        lease,
        lambda: executed.append("used"),
    )

    assert result is None
    assert executed == []
    assert not credentials.valid(lease)


def test_warrantkit_runtime_cannot_issue_new_credential_while_contained():
    engine = build_agentcontainment_engine("agent-credential-authority-test")
    credentials = engine.credential_store

    engine.contain()

    with pytest.raises(RuntimeError, match="active runtime"):
        credentials.issue("prod-api")


def test_warrantkit_runtime_allows_fresh_credential_only_after_recovery():
    engine = build_agentcontainment_engine("agent-credential-recovery-test")
    credentials = engine.credential_store

    old_lease = credentials.issue("prod-api")
    engine.contain()

    assert not credentials.valid(old_lease)
    with pytest.raises(RuntimeError, match="active runtime"):
        credentials.issue("prod-api")

    authorization = engine.issue_recovery_authorization()
    recovered_epoch = engine.recover(authorization)

    fresh_lease = credentials.issue("prod-api")
    assert recovered_epoch > old_lease.epoch
    assert credentials.valid(fresh_lease)
    assert not credentials.valid(old_lease)
