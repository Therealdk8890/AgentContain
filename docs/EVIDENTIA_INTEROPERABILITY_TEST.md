# Evidentia Interoperability Test Protocol

## Status

**Contract defined. Live external artifact identified. Export capture pending.**

This protocol is the implementation gate for the WarrantKit ↔ Evidentia handoff.

Evidentia currently exposes stable public proofs including:

- `EV-DEMO-PUBLIC-001` — public sample AI-usage proof
- `EV-SYSTEM-PROOF-001` — system-integrity proof

The Evidentia developer documentation states that Proof records expose an event hash, Ed25519 signature/public-key metadata, Merkle metadata where applicable, and chain-anchor metadata. Public verification pages and export packages are the intended independent-review surfaces.

## Why the export matters

The interoperability test must operate on the **actual Proof/export artifact**, not a screenshot, copied summary, truncated web rendering, or hand-authored JSON.

WarrantKit must bind the exact artifact to an `artifact_digest`.

Therefore the following are insufficient as test evidence by themselves:

- the public Proof page;
- the proof ID alone;
- a screenshot;
- a copied event hash;
- a synthetic reconstruction of the Proof JSON.

The actual export bytes are the artifact boundary.

## Acquisition

Preferred acquisition order:

1. Obtain the official Evidentia verification export for `EV-SYSTEM-PROOF-001` or `EV-DEMO-PUBLIC-001`.
2. Preserve the downloaded bytes unchanged.
3. Record the source Proof ID and verification URL.
4. Compute SHA-256 over the exact export bytes.
5. Record the digest in the WarrantKit handoff.
6. Do not normalize, reserialize, or edit the export before hashing.

If the export contains multiple files, preserve the complete export package and define one deterministic package digest before creating the handoff. Do not choose a file arbitrarily.

## Test 1 — real artifact handoff

The test should use the captured Evidentia export as received.

Required assertions:

1. The artifact is produced by the actual Evidentia pipeline.
2. The artifact reference identifies the external Proof.
3. The artifact digest matches the preserved bytes.
4. The handoff identifies the WarrantKit execution, Warrant, runtime, and epoch being correlated.
5. Evidentia's supplied verification state remains external metadata.
6. WarrantKit does not promote Evidentia's proof into runtime authority.
7. The resulting state distinguishes authentication, correlation, anchoring, and verification.

The test must retain the original external artifact separately from the WarrantKit handoff record.

## Test 2 — valid-but-wrong replacement

Start with the same captured external artifact and its recorded anchor.

Obtain a second **genuine, independently valid Evidentia Proof** rather than corrupting the first artifact.

The replacement must:

- have valid Evidentia structure;
- have valid Evidentia cryptographic metadata;
- be independently verifiable by Evidentia;
- have a different artifact digest;
- not match the originally recorded external anchor.

Expected WarrantKit result:

```
authenticated: true
internal_external_verification: true
anchored_to_original_state: false
handoff: conflict / unverifiable
```

The replacement MUST NOT be accepted as the continuation of the original external state merely because its own signature verifies.

## What this proves

The two tests establish two different properties:

**Test 1:** WarrantKit can correlate a real independently produced external evidence artifact without importing that system's authority.

**Test 2:** WarrantKit can distinguish an internally authentic replacement from a replacement that preserves continuity with the previously anchored external state.

This is stronger than ordinary signature verification because the negative case does not require a broken signature.

## No fabricated evidence

Until the actual export package is available, the repository MUST NOT add a committed Evidentia JSON fixture and label it as production evidence.

Unit tests for WarrantKit's generic validation logic may use synthetic documents. The interoperability acceptance test may not.

## Expected handoff shape

The handoff remains transport-neutral:

```json
{
  "schema_version": "warrantkit.external-evidence/v1",
  "execution_id": "...",
  "warrant_id": "...",
  "runtime_id": "...",
  "epoch": 1,
  "source": "evidentia",
  "artifact_ref": "EV-SYSTEM-PROOF-001",
  "artifact_digest": "sha256:<digest-of-exact-export>",
  "anchor_ref": "...",
  "anchor_digest": "sha256:<anchored-state-digest>"
}
```

The Evidentia Proof itself remains externally owned. WarrantKit stores a reference and the exact-artifact digest rather than copying the external evidence model into its authority model.

## Acceptance gate

Do not mark the Evidentia interoperability milestone complete until:

- the real export bytes have been captured;
- the exact artifact digest is recorded;
- WarrantKit successfully correlates the artifact;
- the original artifact remains independently verifiable;
- a second independently valid Proof demonstrates the valid-but-wrong replacement case;
- the negative result is recorded as conflict/unverifiable rather than tampered merely because the artifact differs;
- no external evidence can grant, extend, or restore Warrant authority.
