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
