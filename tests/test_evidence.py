from agentcontain.evidence import EvidenceEnvelope


def _envelope() -> EvidenceEnvelope:
    return EvidenceEnvelope.from_execution(
        execution={
            "execution_id": "exec-1",
            "agent_id": "agent-1",
            "policy_id": "production",
            "policy_digest": "digest",
            "epoch": 0,
        },
        events=(
            {"execution_id": "exec-1", "sequence": 1, "name": "admission_verified"},
        ),
        enforcement={"complete": True},
        verification={"status": "verified", "method": "unit-test"},
        proof={"claims": ["containment"]},
        provenance={"producer": "agentcontain", "created_at": "2026-09-26T00:00:00Z"},
    )


def test_evidence_serialization_is_deterministic() -> None:
    envelope = _envelope()
    assert envelope.to_json() == EvidenceEnvelope.from_json(envelope.to_json()).to_json()


def test_evidence_roundtrip_preserves_identity() -> None:
    restored = EvidenceEnvelope.from_json(_envelope().to_json())
    assert restored.execution == _envelope().execution
    assert restored.verification["status"] == "verified"


def test_evidence_rejects_event_identity_mismatch() -> None:
    try:
        EvidenceEnvelope.from_execution(
            execution={
                "execution_id": "exec-1",
                "agent_id": "agent-1",
                "policy_id": "production",
                "policy_digest": "digest",
                "epoch": 0,
            },
            events=({"execution_id": "exec-2", "sequence": 1, "name": "bad"},),
        )
    except ValueError as exc:
        assert "execution_id" in str(exc)
    else:
        raise AssertionError("mismatched event identity was accepted")


def test_evidence_rejects_invalid_status() -> None:
    try:
        EvidenceEnvelope.from_execution(
            execution={
                "execution_id": "exec-1",
                "agent_id": "agent-1",
                "policy_id": "production",
                "policy_digest": "digest",
                "epoch": 0,
            },
            verification={"status": "bogus"},
        )
    except ValueError as exc:
        assert "invalid verification status" in str(exc)
    else:
        raise AssertionError("invalid verification status was accepted")
