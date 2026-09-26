# Durable Evidence Store Contract

**Status:** v0.1 implementation contract

The AgentContain runtime produces evidence locally. A downstream control plane may persist and index that evidence, but persistence must not become a prerequisite for containment, verification, or receipt generation.

## Authority principle

> **The runtime is authoritative for execution evidence; the store is authoritative only for durable retention and retrieval.**

A store MUST NOT mutate the semantic meaning of an accepted evidence envelope.

## Store boundary

The first implementation is transport-neutral and storage-backend-neutral.

```text
Local runtime
    |
    v
EvidenceEnvelope
    |
    v
EvidenceSink
    |
    v
Durable Evidence Store
    |
    +--> retrieval
    +--> indexing
    +--> audit/export
```

The store may be remote, local, SQL-backed, object-backed, or hosted. None of those choices changes runtime authority.

## Required operations

A durable store interface SHOULD provide:

- **put** — persist one accepted envelope
- **get** — retrieve by receipt ID
- **list** — enumerate evidence by bounded governance scope
- **exists** — test idempotency before or during persistence

### Identity and immutability

For envelopes with a receipt ID:

- `receipt_id` is the idempotency key.
- A second submission with the same `receipt_id` and identical canonical evidence is idempotent.
- A second submission with the same `receipt_id` but different canonical evidence MUST be rejected.
- Existing evidence MUST NOT be silently overwritten.

Receiptless evidence may be retained, but it does not provide the same durable identity guarantee.

## Preservation rule

Persistence MUST preserve the original envelope semantics, including:

- schema version
- execution identity
- policy ID and policy digest
- epoch
- event sequence
- enforcement result
- verification status
- proof provenance
- receipt
- provenance metadata

A store may add indexing metadata, timestamps, storage identifiers, or retention metadata outside the evidence envelope. It MUST NOT rewrite the original evidence fields.

## Scope

Future Enterprise implementations may partition storage by:

`organization → project → runtime → agent → execution → evidence`

Scope metadata is governance data. It does not grant runtime authority.

## Failure behavior

If the durable store is unavailable:

1. local containment continues;
2. local verification continues;
3. local receipts continue;
4. evidence may be queued for later ingestion;
5. no store outage may weaken or bypass runtime enforcement.

## Verification boundary

The store does not establish that a claim is true.

It may preserve:

- observed evidence,
- verification results,
- authenticated/tamper-evident receipts,
- proof artifacts.

The existing evidence and receipt trust model remains authoritative for interpretation.

## Acceptance criteria

An implementation is conformant when:

1. identical receipt IDs are idempotent;
2. receipt ID collisions are rejected;
3. persisted envelopes round-trip without semantic mutation;
4. policy identity and digest are preserved;
5. event ordering is preserved;
6. store failure cannot disable local enforcement;
7. the interface has no HTTP, SaaS, billing, or authentication dependency.

## OSS / Enterprise boundary

The Apache-2.0 platform may provide the interface and a local reference implementation.

A future commercial implementation may add:

- durable hosted storage,
- retention policies,
- organization/project administration,
- search and indexing,
- audit views,
- exports,
- alerts,
- SIEM integrations.

Those services sit above this boundary and do not become runtime security authorities.