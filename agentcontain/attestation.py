"""Ed25519 attestation primitives for portable WarrantKit artifacts.

The signing layer authenticates an artifact; it does not grant authority or
upgrade evidence semantics. Callers must still run the existing Warrant and
evidence verification procedures after signature verification.
"""
from __future__ import annotations
import base64, json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
except ImportError as exc:
    raise ImportError("Ed25519 attestation requires: pip install 'warrantkit[attestation]'") from exc

SCHEMA_VERSION = "warrantkit.attestation/v1"
ALGORITHM = "ed25519"
ARTIFACT_WARRANT = "warrant"
ARTIFACT_RECEIPT = "receipt"
_DOMAIN = b"warrantkit-attestation/v1\x00"

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("issued_at must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()

def _signature_input(*, schema_version: str, artifact_type: str, payload: Mapping[str, Any]) -> bytes:
    return _DOMAIN + canonical_bytes(schema_version) + canonical_bytes(artifact_type) + canonical_bytes(payload)

@dataclass(frozen=True)
class AttestationEnvelope:
    schema_version: str
    artifact_type: str
    algorithm: str
    key_id: str
    issued_at: str
    payload: dict[str, Any]
    signature: str

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION: raise ValueError("unsupported attestation schema")
        if self.artifact_type not in {ARTIFACT_WARRANT, ARTIFACT_RECEIPT}: raise ValueError("unsupported attestation artifact type")
        if self.algorithm != ALGORITHM: raise ValueError("unsupported attestation algorithm")
        if not self.key_id.strip(): raise ValueError("key_id must not be empty")
        if not isinstance(self.payload, dict): raise TypeError("payload must be a mapping")
        if not self.signature: raise ValueError("signature must not be empty")
        try: datetime.fromisoformat(self.issued_at)
        except ValueError as exc: raise ValueError("issued_at must be ISO-8601") from exc

    def unsigned_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "artifact_type": self.artifact_type, "algorithm": self.algorithm, "key_id": self.key_id, "issued_at": self.issued_at, "payload": self.payload}

    def to_dict(self) -> dict[str, Any]:
        document = self.unsigned_dict(); document["signature"] = self.signature; return document

    @classmethod
    def from_dict(cls, document: Mapping[str, Any]) -> "AttestationEnvelope":
        required = {"schema_version","artifact_type","algorithm","key_id","issued_at","payload","signature"}
        if not isinstance(document, Mapping): raise TypeError("attestation must be a mapping")
        if set(document) != required: raise ValueError("attestation has an invalid shape")
        if not isinstance(document["payload"], Mapping): raise TypeError("attestation payload must be a mapping")
        return cls(document["schema_version"], document["artifact_type"], document["algorithm"], document["key_id"], document["issued_at"], dict(document["payload"]), document["signature"])

@dataclass(frozen=True)
class Ed25519Signer:
    key_id: str
    private_key: Ed25519PrivateKey

    def __post_init__(self) -> None:
        if not self.key_id.strip(): raise ValueError("key_id must not be empty")

    @classmethod
    def generate(cls, key_id: str) -> "Ed25519Signer":
        return cls(key_id, Ed25519PrivateKey.generate())

    def public_key(self) -> Ed25519PublicKey:
        return self.private_key.public_key()

    def sign(self, *, artifact_type: str, payload: Mapping[str, Any], issued_at: datetime | None = None) -> AttestationEnvelope:
        if artifact_type not in {ARTIFACT_WARRANT, ARTIFACT_RECEIPT}: raise ValueError("unsupported attestation artifact type")
        payload_dict = dict(payload)
        signature = self.private_key.sign(_signature_input(schema_version=SCHEMA_VERSION, artifact_type=artifact_type, payload=payload_dict))
        return AttestationEnvelope(SCHEMA_VERSION, artifact_type, ALGORITHM, self.key_id, _timestamp(issued_at or datetime.now(timezone.utc)), payload_dict, base64.b64encode(signature).decode("ascii"))

    def sign_warrant(self, warrant: "WarrantLike", *, issued_at: datetime | None = None) -> AttestationEnvelope:
        return self.sign(artifact_type=ARTIFACT_WARRANT, payload=warrant.to_dict(), issued_at=issued_at)

    def sign_receipt(self, receipt: Mapping[str, Any], *, issued_at: datetime | None = None) -> AttestationEnvelope:
        return self.sign(artifact_type=ARTIFACT_RECEIPT, payload=receipt, issued_at=issued_at)

class Ed25519Verifier:
    def __init__(self, trust_anchors: Mapping[str, Ed25519PublicKey]) -> None:
        self._trust_anchors = dict(trust_anchors)

    def verify(self, envelope: AttestationEnvelope | Mapping[str, Any], *, expected_artifact_type: str | None = None) -> dict[str, Any]:
        if not isinstance(envelope, AttestationEnvelope): envelope = AttestationEnvelope.from_dict(envelope)
        if expected_artifact_type is not None and envelope.artifact_type != expected_artifact_type: raise ValueError("attestation artifact type does not match expected type")
        public_key = self._trust_anchors.get(envelope.key_id)
        if public_key is None: raise ValueError("unknown attestation key_id")
        try: signature = base64.b64decode(envelope.signature, validate=True)
        except Exception as exc: raise ValueError("invalid attestation signature encoding") from exc
        try: public_key.verify(signature, _signature_input(schema_version=envelope.schema_version, artifact_type=envelope.artifact_type, payload=envelope.payload))
        except InvalidSignature as exc: raise ValueError("invalid attestation signature") from exc
        return dict(envelope.payload)

    def verify_warrant(self, envelope: AttestationEnvelope | Mapping[str, Any]) -> "WarrantLike":
        from .warrant import Warrant
        return Warrant.from_dict(self.verify(envelope, expected_artifact_type=ARTIFACT_WARRANT))

class WarrantLike:
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError
