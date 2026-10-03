import hashlib
import os
from pathlib import Path

import pytest

from agentcontain.external_evidence import ExternalEvidenceReference, digest_artifact


def test_digest_artifact_binds_exact_bytes() -> None:
    artifact = b'{"proof":"example"}\n'

    assert digest_artifact(artifact) == "sha256:" + hashlib.sha256(artifact).hexdigest()


def test_digest_artifact_rejects_text() -> None:
    with pytest.raises(TypeError):
        digest_artifact("not-bytes")  # type: ignore[arg-type]


@pytest.mark.integration
def test_real_evidentia_export_binds_exact_bytes() -> None:
    export_path = os.environ.get("WARRANTKIT_EVIDENTIA_EXPORT")
    proof_id = os.environ.get("WARRANTKIT_EVIDENTIA_PROOF_ID")

    if not export_path or not proof_id:
        pytest.skip(
            "set WARRANTKIT_EVIDENTIA_EXPORT and WARRANTKIT_EVIDENTIA_PROOF_ID "
            "to run against a real Evidentia export"
        )

    artifact = Path(export_path).read_bytes()
    reference = ExternalEvidenceReference(
        source="evidentia",
        reference_id=proof_id,
        digest=digest_artifact(artifact),
        relation="attests",
        captured_at=os.environ.get(
            "WARRANTKIT_EVIDENTIA_CAPTURED_AT",
            "unknown",
        ),
    )

    assert reference.source == "evidentia"
    assert reference.reference_id == proof_id
    assert reference.digest == digest_artifact(artifact)
