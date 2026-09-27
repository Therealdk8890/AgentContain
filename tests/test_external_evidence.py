from agentcontain.external_evidence import ExternalEvidenceReference


def _reference(**overrides) -> ExternalEvidenceReference:
    values = {
        "source": "warden",
        "reference_id": "warden-event-1",
        "digest": "sha256:" + "a" * 64,
        "relation": "observed_during",
        "captured_at": "2026-09-27T00:00:00Z",
    }
    values.update(overrides)
    return ExternalEvidenceReference(**values)


def test_external_evidence_reference_roundtrip() -> None:
    reference = _reference()
    assert ExternalEvidenceReference.from_dict(reference.to_dict()) == reference


def test_external_evidence_reference_rejects_unknown_source() -> None:
    try:
        _reference(source="unknown")
    except ValueError as exc:
        assert "source" in str(exc)
    else:
        raise AssertionError("unknown evidence source was accepted")


def test_external_evidence_reference_rejects_bad_digest() -> None:
    try:
        _reference(digest="sha256:not-a-digest")
    except ValueError as exc:
        assert "sha256" in str(exc)
    else:
        raise AssertionError("invalid digest was accepted")


def test_external_evidence_reference_rejects_unknown_relation() -> None:
    try:
        _reference(relation="authorizes")
    except ValueError as exc:
        assert "relation" in str(exc)
    else:
        raise AssertionError("authority relation was accepted")
