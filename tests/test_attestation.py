from datetime import datetime, timezone
import pytest
from agentcontain.attestation import ARTIFACT_RECEIPT, ARTIFACT_WARRANT, AttestationEnvelope, Ed25519Signer, Ed25519Verifier
from agentcontain.policy import Policy
from agentcontain.warrant import Warrant

def _warrant() -> Warrant:
    policy = Policy("production", capabilities=("read",))
    return Warrant.issue(warrant_id="w-1", issuer="controller", agent_id="agent-1", execution_id="exec-1", policy=policy, runtime_id="runtime-1", epoch=1, issued_at=datetime(2026,1,1,tzinfo=timezone.utc), expires_at=datetime(2026,1,1,0,5,tzinfo=timezone.utc))

def test_valid_warrant_verifies() -> None:
    signer = Ed25519Signer.generate("wk-test-01")
    envelope = signer.sign_warrant(_warrant(), issued_at=datetime(2026,1,1,tzinfo=timezone.utc))
    restored = AttestationEnvelope.from_dict(envelope.to_dict())
    assert Ed25519Verifier({"wk-test-01": signer.public_key()}).verify_warrant(restored) == _warrant()

def test_modified_payload_fails() -> None:
    signer = Ed25519Signer.generate("wk-test-01")
    document = signer.sign_warrant(_warrant()).to_dict()
    document["payload"]["authority"]["policy_id"] = "tampered"
    with pytest.raises(ValueError, match="signature"): Ed25519Verifier({"wk-test-01": signer.public_key()}).verify(document)

def test_wrong_key_fails() -> None:
    signer, other = Ed25519Signer.generate("wk-01"), Ed25519Signer.generate("wk-other")
    envelope = signer.sign_warrant(_warrant())
    with pytest.raises(ValueError, match="signature"): Ed25519Verifier({"wk-01": other.public_key()}).verify(envelope)

def test_unknown_key_id_fails() -> None:
    signer = Ed25519Signer.generate("wk-01")
    envelope = signer.sign_warrant(_warrant())
    with pytest.raises(ValueError, match="key_id"): Ed25519Verifier({}).verify(envelope)

def test_wrong_artifact_type_fails_closed() -> None:
    signer = Ed25519Signer.generate("wk-01")
    envelope = signer.sign(artifact_type=ARTIFACT_WARRANT, payload=_warrant().to_dict())
    with pytest.raises(ValueError, match="artifact type"): Ed25519Verifier({"wk-01": signer.public_key()}).verify(envelope, expected_artifact_type=ARTIFACT_RECEIPT)

def test_modified_schema_fails() -> None:
    signer = Ed25519Signer.generate("wk-01")
    document = signer.sign_warrant(_warrant()).to_dict()
    document["schema_version"] = "warrantkit.attestation/v999"
    with pytest.raises(ValueError, match="schema"): Ed25519Verifier({"wk-01": signer.public_key()}).verify(document)

def test_key_rotation_accepts_overlap_and_rejects_unknown_retired_key() -> None:
    first, second = Ed25519Signer.generate("wk-01"), Ed25519Signer.generate("wk-02")
    envelope = first.sign_warrant(_warrant())
    assert Ed25519Verifier({"wk-01": first.public_key(), "wk-02": second.public_key()}).verify(envelope)["warrant_id"] == "w-1"
    with pytest.raises(ValueError, match="key_id"): Ed25519Verifier({"wk-02": second.public_key()}).verify(envelope)

def test_receipt_profile_is_explicit() -> None:
    signer = Ed25519Signer.generate("wk-receipt")
    envelope = signer.sign_receipt({"status":"verified","execution_id":"exec-1"})
    assert envelope.algorithm == "ed25519"
    assert envelope.artifact_type == ARTIFACT_RECEIPT
