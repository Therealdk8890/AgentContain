# Evidence Trust Model

## Purpose

WarrantKit separates authority from evidence. This document defines what a verified receipt means, what it does not mean, and how the trust boundary changes when asymmetric signatures are used.

## Core semantics

- **Warrant** = authority granted for one execution.
- **Evidence** = an observation or result produced at a declared evidence boundary.
- **Verification** = the defined procedure successfully checked the supplied evidence and bindings.
- **Receipt** = an authenticated record that binds evidence to an execution and verification context.

**Verified does not mean the underlying claim is universally true.**

A verified receipt means that the verifier established the documented invariants against the supplied artifact and trust anchors.

## Current HMAC profile

The current runtime receipt profile uses HMAC authentication with an operator/deployer-supplied shared secret.

This provides:
- integrity/tamper detection when the secret is protected
- authentication to holders of the shared secret

It does not provide:
- non-repudiation
- proof that a unique signer produced the receipt
- protection against a holder of the shared secret fabricating receipts

HMAC remains useful for local compatibility and early deployments, but it is not described as asymmetric attestation.

## Asymmetric profile

The planned asymmetric profile uses Ed25519 unless implementation constraints require another algorithm.

A signed artifact must contain or be bound to:

- schema/version identifier
- algorithm identifier
- key identifier
- canonical signed payload
- signature
- execution identity
- policy identity and digest
- runtime identity
- relevant runtime epoch
- issuance/creation time
- verification-relevant evidence references

The signature covers canonical bytes, not an arbitrary JSON serialization.

Verification must fail closed if:
- the signature is invalid
- the algorithm is unsupported
- the key identifier is unknown
- canonicalization differs
- execution identity differs
- policy identity or digest differs
- runtime identity differs
- epoch differs
- schema/version is unsupported
- required evidence is missing or stale

## Trust anchors

An asymmetric signature establishes authenticity relative to a configured public-key trust anchor.

It does **not** by itself prove:
- that the host is uncompromised
- that the kernel is trustworthy
- that the runtime provider enforced the action correctly
- that an agent's intent was benign
- that a policy was correct
- that an external claim is true

Host/TPM/measured-boot attestation is a separate future trust layer.

## Evidence boundary

For containment, the intended evidence chain is:

1. WarrantKit establishes the authority and execution identity.
2. AgentContainment performs the security-critical external enforcement.
3. The runtime produces enforcement evidence.
4. Independent observation can establish the workload's resulting state.
5. WarrantKit correlates these facts by execution identity, runtime identity, and epoch.
6. The verifier checks the defined invariants and signature.
7. The receipt records the resulting verification state.

No evidence step grants, extends, or restores authority.

## Conflicts

Conflicting evidence is not silently resolved.

Examples:
- enforcement says epoch 18 while an external record is anchored to epoch 17
- runtime identity differs between evidence sources
- a replacement record is internally valid but inconsistent with an earlier external anchor

The result must remain explicitly conflicting or unverifiable rather than being promoted to verified.

## Key rotation

The asymmetric profile must support:
- stable key identifiers
- explicit trust-anchor configuration
- overlapping key validity during rotation
- rejection of unknown or retired keys according to verifier policy
- preservation of the key identifier in exported evidence

Rotation changes the signing key, not the authority semantics.

## Compatibility

The asymmetric profile should be introduced without breaking the authority/enforcement architecture.

Compatibility rules must be explicit:
- HMAC artifacts remain identifiable as HMAC artifacts.
- HMAC must never be presented as non-repudiable.
- Verifiers must identify which trust profile they applied.
- A stronger signature does not upgrade weak or missing runtime evidence into verified enforcement.

## Non-goals

This trust model does not claim:
- formal verification
- universal host security
- measured-boot attestation
- policy correctness
- agent intent correctness
- reversal of side effects
- universal truth of externally supplied claims
