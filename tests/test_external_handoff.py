from agentcontain.external_handoff import (
    CorrelationState,
    ExternalEvidenceHandoff,
    correlate_handoff,
)


def _handoff(**overrides) -> ExternalEvidenceHandoff:
    values = {
        "execution_id": "exec-1",
        "warrant_id": "warrant-1",
        "runtime_id": "runtime-1",
        "epoch": 3,
        "source": "evidentia",
        "artifact_ref": "EV-SYSTEM-PROOF-001",
        "artifact_digest": "sha256:" + "a" * 64,
        "anchor_ref": "anchor-1",
        "anchor_digest": "sha256:" + "a" * 64,
    }
    values.update(overrides)
    return ExternalEvidenceHandoff(**values)


def test_handoff_roundtrips() -> None:
    handoff = _handoff()

    assert ExternalEvidenceHandoff.from_dict(handoff.to_dict()) == handoff


def test_matching_anchor_is_correlated_but_not_verified() -> None:
    result = correlate_handoff(
        _handoff(),
        execution_id="exec-1",
        warrant_id="warrant-1",
        runtime_id="runtime-1",
        epoch=3,
    )

    assert result.state == CorrelationState.CORRELATED
    assert result.correlated is True
    assert result.anchored is True


def test_valid_but_wrong_replacement_is_conflict() -> None:
    result = correlate_handoff(
        _handoff(artifact_digest="sha256:" + "b" * 64),
        execution_id="exec-1",
        warrant_id="warrant-1",
        runtime_id="runtime-1",
        epoch=3,
    )

    assert result.state == CorrelationState.CONFLICT
    assert "anchored digest" in result.reasons[0]


def test_missing_anchor_is_not_verified() -> None:
    result = correlate_handoff(
        _handoff(anchor_ref=None, anchor_digest=None),
        execution_id="exec-1",
        warrant_id="warrant-1",
        runtime_id="runtime-1",
        epoch=3,
    )

    assert result.state == CorrelationState.UNANCHORED
    assert result.correlated is False


def test_identity_mismatch_fails_closed() -> None:
    result = correlate_handoff(
        _handoff(),
        execution_id="exec-other",
        warrant_id="warrant-1",
        runtime_id="runtime-1",
        epoch=3,
    )

    assert result.state == CorrelationState.CONFLICT
    assert "execution_id mismatch" in result.reasons
