# External Evidence Handoff Contract

## Purpose

This contract defines the smallest interoperability boundary for correlating a WarrantKit execution with evidence produced outside WarrantKit.

The contract is deliberately narrower than a general evidence format. It does not define how an external system observes a workload, how it stores evidence, or how it decides that an observation is correct.

Its purpose is to make the handoff explicit and independently testable.

## Security boundary

WarrantKit establishes authority and execution identity.

An external evidence producer establishes observations at its declared evidence boundary.

The handoff correlates those facts. It does **not** promote external evidence into authority.

A valid signature authenticates the handoff record; it does not establish that the underlying observation is true.

## Required correlation fields

A handoff record MUST identify:

| Field | Meaning |
| --- | --- |
| `schema_version` | Version of this handoff contract |
| `execution_id` | WarrantKit execution being correlated |
| `warrant_id` | Warrant associated with the execution |
| `runtime_id` | Runtime/provider identity |
| `epoch` | Runtime authority/recovery epoch |
| `source` | Declared external evidence producer |
| `artifact_ref` | Stable reference to the external artifact |
| `artifact_digest` | Digest of the exact external artifact |
| `anchor_ref` | Optional reference to the externally anchored prior state |
| `anchor_digest` | Optional digest of that anchored state |

The correlation tuple is:

```
(execution_id, warrant_id, runtime_id, epoch)
```

The artifact digest binds the handoff to the exact external bytes or canonical artifact representation.

## Optional verification state

A producer MAY report a verification state, but the value is descriptive unless WarrantKit has a defined verification procedure for that state.

Recommended states are:

- `observed`
- `verified`
- `incomplete`
- `conflict`
- `tampered`

A producer's `verified` label MUST NOT automatically become WarrantKit's verification result.

WarrantKit should record both the supplied state and the result of its own verification procedure when both exist.

## External anchor semantics

An `anchor_ref` identifies an earlier externally established state against which a later artifact can be compared.

This supports a security property that ordinary signature verification does not provide:

> An artifact can be authentic and internally valid while still being inconsistent with an externally anchored state.

For example:

1. External system produces artifact A and establishes anchor H(A).
2. WarrantKit records the execution and the external anchor.
3. A replacement artifact B is correctly signed by the same external system.
4. B is internally valid according to that system.
5. B's digest does not match the previously anchored state.
6. The handoff result is `conflict` or `unverifiable`, not `verified`.

No signature failure is required for this test to fail. The failure is continuity against external state.

## Verification rules

A handoff verifier MUST fail closed when required correlation data is missing, malformed, or inconsistent.

At minimum it MUST distinguish:

### Authenticated

The handoff record's cryptographic authentication is valid relative to the configured trust anchor.

### Correlated

The artifact binds to the expected WarrantKit execution, runtime, and epoch.

### Anchored

The artifact agrees with the external state identified by the supplied anchor.

### Verified

The documented evidence procedure establishes all required invariants.

These are separate properties.

In particular:

```
authenticated != correlated != anchored != verified
```

A record MUST NOT be promoted to `verified` solely because its signature is valid.

## Replacement-artifact test

The interoperability test suite should contain two distinct tests.

### Test 1 — real artifact handoff

Use an artifact produced by the actual external evidence pipeline.

Do not construct a synthetic artifact merely to satisfy the contract.

The test should demonstrate:

```
external producer
    -> real artifact
    -> handoff record
    -> WarrantKit correlation
    -> documented verification result
```

### Test 2 — valid-but-wrong replacement

Start from the same externally anchored artifact.

Create or obtain a replacement artifact that:

- is structurally valid;
- has a valid signature from a trusted external key;
- passes the external system's internal integrity checks;
- has a different artifact digest from the anchored artifact.

The expected result is an explicit conflict or unverifiable state.

The test MUST NOT manufacture a fake signature or deliberately corrupt the replacement merely to force failure. The point is to demonstrate that internal validity does not establish continuity with external state.

## Trust model

The contract does not establish:

- host integrity;
- kernel integrity;
- enforcement correctness;
- policy correctness;
- agent intent;
- truth of an external claim;
- freshness beyond the defined timestamp/epoch checks;
- authorization beyond WarrantKit's existing authority verification.

Those properties remain the responsibility of their respective trust boundaries.

## Interoperability requirements

An external implementation should be able to consume or produce the handoff without importing WarrantKit internals.

The contract therefore uses:

- explicit versioning;
- stable identifiers;
- algorithm-independent artifact references;
- content digests;
- explicit trust/verification states;
- no dependency on WarrantKit's Python object model.

The first interoperability implementation should prefer an existing external artifact format over inventing a new evidence payload format.

## Non-goals

This contract does not attempt to:

- replace DProvenanceKit or another provenance system;
- define a universal evidence schema;
- define a hosted key-management service;
- create a new runtime enforcement mechanism;
- infer truth from cryptographic authenticity;
- silently reconcile conflicting evidence;
- turn external evidence into authority.

## Acceptance criteria

This contract is ready for implementation when:

1. A real external artifact can be referenced without transformation into a WarrantKit-specific synthetic payload.
2. The artifact can be bound to a WarrantKit execution, runtime, and epoch.
3. The exact artifact bytes or canonical representation can be identified by digest.
4. An earlier external anchor can be retained without granting it authority.
5. A correctly signed but differently anchored replacement is distinguishable from a tampered artifact.
6. The verification result preserves the distinction between authenticated, correlated, anchored, and verified.
7. Conflicting evidence remains explicit rather than being silently resolved.
