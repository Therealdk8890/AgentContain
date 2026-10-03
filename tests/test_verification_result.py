from agentcontain.verification_result import (
    VerificationStatus,
    compose_verification,
)


def test_complete_result_is_verified() -> None:
    result = compose_verification(
        authority_valid=True,
        runtime_valid=True,
        authenticated=True,
        correlated=True,
        anchored=True,
        verifier_executed=True,
    )

    assert result.status == VerificationStatus.VERIFIED
    assert result.is_verified is True


def test_missing_anchor_is_incomplete() -> None:
    result = compose_verification(
        authority_valid=True,
        runtime_valid=True,
        authenticated=True,
        correlated=True,
        anchored=False,
        verifier_executed=True,
        missing=("external anchor",),
    )

    assert result.status == VerificationStatus.INCOMPLETE
    assert result.is_verified is False


def test_conflict_dominates_other_successes() -> None:
    result = compose_verification(
        authority_valid=True,
        runtime_valid=True,
        authenticated=True,
        correlated=True,
        anchored=True,
        verifier_executed=True,
        conflicts=("external artifact differs from anchor",),
    )

    assert result.status == VerificationStatus.CONFLICT


def test_unauthenticated_cannot_be_verified() -> None:
    result = compose_verification(
        authority_valid=True,
        runtime_valid=True,
        authenticated=False,
        correlated=True,
        anchored=True,
        verifier_executed=True,
    )

    assert result.status == VerificationStatus.UNAUTHENTICATED
    assert result.is_verified is False


def test_verification_does_not_create_authority_or_truth() -> None:
    result = compose_verification(
        authority_valid=True,
        runtime_valid=True,
        authenticated=True,
        correlated=True,
        anchored=True,
        verifier_executed=True,
    )

    assert result.is_authorized is False
    assert result.claim_is_true is False


def test_missing_evidence_never_defaults_to_success() -> None:
    result = compose_verification(
        authority_valid=True,
        runtime_valid=True,
        authenticated=True,
        correlated=True,
        anchored=True,
        verifier_executed=False,
        missing=("verification procedure",),
    )

    assert result.status == VerificationStatus.INCOMPLETE


def test_serialization_preserves_each_dimension() -> None:
    result = compose_verification(
        authority_valid=True,
        runtime_valid=False,
        authenticated=True,
        correlated=False,
        anchored=False,
        verifier_executed=False,
        missing=("runtime proof", "anchor"),
    )

    document = result.to_dict()

    assert document["authority_valid"] is True
    assert document["runtime_valid"] is False
    assert document["authenticated"] is True
    assert document["correlated"] is False
    assert document["anchored"] is False
    assert document["verifier_executed"] is False
    assert document["status"] == "incomplete"
