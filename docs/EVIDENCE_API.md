# AgentContain Evidence API

**Status:** v0.1 contract  
**Purpose:** Stable boundary between local runtime proof and downstream governance systems

The Evidence API transports execution evidence. It does not delegate enforcement authority.

## Design rule

> **Evidence flows outward from the runtime. Authority does not flow inward from the control plane.**

A consumer may store, index, verify, correlate, alert on, or export evidence. It must not rewrite an enforcement result into a stronger security claim.

## Evidence envelope

The canonical envelope is conceptually:

~~~json
{
  "schema_version": "agentcontain.evidence/v1",
  "execution": {
    "execution_id": "…",
    "agent_id": "…",
    "policy_id": "…",
    "policy_digest": "…",
    "epoch": 0
  },
  "events": [],
  "enforcement": {"complete": true, "provider_results": [], "failures": []},
  "verification": {"status": "verified", "method": "…", "environment": {}},
  "proof": {"claims": [], "executed_proofs": []},
  "receipt": {},
  "governance": {
    "organization_id": "…",
    "project_id": "…",
    "runtime_id": "…",
    "agent_id": "…"
  },
  "provenance": {"producer": "agentcontain", "created_at": "…"}
}
~~~

The exact serialized schema is implementation-defined until frozen, but the semantic fields above are contract-level requirements.

## Required semantics

### Execution identity
Every envelope must bind evidence to `execution_id`, `agent_id`, `policy_id`, `policy_digest`, and `epoch`. Evidence without execution identity is incomplete for authoritative lifecycle reconstruction.

### Event sequence
Events must preserve execution ID, epoch, monotonically increasing sequence, timestamp, event name, and structured details. Consumers must not silently reorder or mutate the event sequence.

### Enforcement result
The envelope must distinguish requested enforcement, provider result, independent verification, and failures/degradation. A provider being invoked is not equivalent to provider enforcement being verified.

### Proof provenance
A proof claim must identify the proof evidence that supports it. At minimum: proof identifier, executed/not-executed status, result, environment or capability requirements, and evidence reference. A claim with no executed proof marker must not be represented as an executed adversarial proof.

### Receipt
Where a receipt is present, consumers must retain receipt ID, canonical payload, integrity digest, authentication/signature metadata, and verification result. The existing HMAC receipt model is authenticated and tamper-evident; it is not non-repudiable attestation.

### Environment
Environment metadata should identify material verification context such as operating system, kernel/runtime information, enforcement provider, required privileges, integration-test mode, and relevant capability flags. Environment metadata is contextual evidence, not a universal security claim.

## Status model

| Status | Meaning |
|---|---|
| observed | Evidence was received or an event was observed |
| verified | A designated verifier established the specified property |
| degraded | Enforcement or verification was incomplete or failed |
| tampered | Receipt or evidence integrity/authentication failed |
| incomplete | Required evidence or proof is missing |

Do not map these automatically to a generic "safe/unsafe" boolean.

## Ingestion contract

An Enterprise collector should treat an incoming envelope as immutable evidence.

~~~text
Receive
  ↓
Parse schema
  ↓
Authenticate / verify receipt
  ↓
Validate identity + sequence
  ↓
Persist original envelope
  ↓
Index derived fields
  ↓
Evaluate policy / alert rules
~~~

Derived indexes and dashboard status must remain traceable to the original envelope.

## Idempotency

Ingestion must be idempotent by receipt ID where a receipt exists. Duplicate delivery must not create duplicate evidence or reinterpret the delivery as a new execution.

## Versioning

The API uses an explicit schema version. Consumers must reject unsupported major versions, tolerate additive fields within a compatible major version, preserve unknown fields when storing the original envelope, and never silently downgrade a stronger or newer evidence state.

## Security requirements

Transport authentication (HTTPS, mTLS, workload identity, or another authenticated channel) is separate from proof verification. A trusted transport does not make unverified runtime claims true.

Likewise, a cryptographically valid receipt does not prove that the underlying host or kernel behaved as claimed; it proves that the received authenticated payload has not been altered relative to the signing secret/trust model.

## Compatibility target

The first implementation should be transport-neutral. Local consumers must be able to use the same evidence object without requiring a SaaS connection, specific database, HTTP framework, or billing entitlement.

The initial implementation can therefore expose a Python-native evidence envelope and canonical serialization before adding an HTTP API.


## Governance binding

An evidence envelope MAY include a `governance` mapping containing the
originating `organization_id`, `project_id`, `runtime_id`,
and `agent_id`. When present, these values are derived from validated
local fleet inventory rather than caller-supplied control-plane metadata.

Governance scope is attribution metadata. It does not grant authority to the
control plane and does not change the meaning of runtime enforcement or proof.
Historical evidence retains the governance scope associated with its originating
execution.
