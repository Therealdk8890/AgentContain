# Asymmetric Attestation Design

## Goal

Add an asymmetric signing profile for WarrantKit Warrants and receipts while preserving the existing authority, lifecycle, enforcement-provider, and evidence boundaries.

The first profile should use Ed25519.

## Boundary

WarrantKit remains responsible for authority contracts, execution identity, policy identity, runtime identity, epoch binding, lifecycle state, evidence correlation, and verification semantics.

The runtime enforcement provider remains responsible for security-critical enforcement, runtime-specific enforcement evidence, and host/provider behavior.

The signing layer authenticates artifacts. It does not become an enforcement mechanism.

## Artifact model

The signed representation should be a versioned envelope:

    AttestationEnvelope
      schema_version
      artifact_type
      algorithm
      key_id
      issued_at
      payload
      signature

Payload contains the canonical authority or evidence representation.

The signature input should be domain-separated and canonical:

    domain || schema_version || artifact_type || canonical_payload

This prevents a signature for one artifact class from being interpreted as another artifact class.

## Warrant signing

A signed Warrant authenticates the authority contract.

The signature does not authorize anything by itself. A verifier must still perform the existing exact-binding checks for execution identity, policy identity/digest, runtime identity, epoch, lifecycle, and validity.

## Receipt signing

A signed receipt authenticates an evidence artifact and its declared verification state.

The receipt must preserve the distinction between evidence, verification result, and authority.

A valid signature cannot turn incomplete, stale, conflicting, or missing evidence into verified evidence.

## Key handling

The first implementation should not invent a hosted key-management service.

Instead, support explicit local trust configuration:
- signing key supplied by the operator/deployer
- public verification key or trust-anchor registry supplied to the verifier
- stable key_id
- explicit algorithm
- documented rotation procedure

Private keys must never be serialized into receipts or logs.

## Rotation

A verifier may trust multiple active keys during rotation.

A key should be identified by a stable key_id, and exported artifacts retain that identifier permanently.

Retirement policy belongs to the verifier trust configuration; it should not mutate historical receipts.

## Backward compatibility

HMAC remains a separately identified legacy/local authentication profile while migration occurs.

Do not:
- relabel HMAC as asymmetric
- infer non-repudiation from HMAC
- silently accept an HMAC artifact where an asymmetric profile is required
- change the meaning of existing receipt verification

## Independent verification

The portable verifier should eventually support both:
- hmac-shared-secret
- ed25519-public-key

The verifier output should identify the profile used, for example:

    VERIFIED
    profile: ed25519
    key_id: wk-demo-01

## Tests required before implementation is complete

1. Valid Ed25519 Warrant verifies.
2. Modified Warrant fails signature verification.
3. Modified payload with reused signature fails.
4. Wrong key fails.
5. Unknown key identifier fails.
6. Wrong artifact type/domain fails.
7. Wrong schema version fails.
8. Wrong execution identity fails.
9. Wrong policy digest fails.
10. Wrong runtime identity fails.
11. Wrong epoch fails.
12. Expired/revoked Warrant still fails existing authority verification.
13. Valid signature with incomplete evidence does not become verified.
14. Valid signature with conflicting evidence remains conflict/unverifiable.
15. Key rotation accepts configured overlapping keys and rejects retired keys according to trust policy.
16. HMAC artifacts remain explicitly classified as HMAC.

## Implementation sequence

1. Introduce canonical signing envelope and domain separation.
2. Add Ed25519 signer/verifier primitives.
3. Add signed Warrant representation.
4. Add signed receipt representation without changing runtime receipt semantics.
5. Extend standalone portable verifier.
6. Add rotation tests and negative tests.
7. Update trust-model documentation and README status.
8. Only then consider host/TPM attestation as a separate provider/trust-anchor layer.

This design intentionally avoids changing WarrantKit core architecture.
