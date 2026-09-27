# Cross-Repository Evidence Contract

## Purpose

AgentContain is the platform boundary between runtime enforcement and the surrounding AI security/evidence stack.

The platform must correlate four kinds of evidence without turning any subsystem into another subsystem's authority:
- **Warden** — what was observed at the agent/tooling boundary.
- **AgentContainment** — what runtime enforcement actually did.
- **DProvenanceKit** — what instrumented execution path was recorded and how its integrity was checked.
- **ClaimProofKit** — whether supplied claims were supported by supplied evidence.

The contract is deliberately reference-oriented. AgentContain should not copy an entire external trace, observation database, or verification report into its own event model.

## Authority boundaries

| System | Primary authority | Must not claim |
|---|---|---|
| Warden | Observation of agent/tool activity | Kernel containment |
| AgentContainment | Runtime enforcement and host verification | Truth of external claims |
| DProvenanceKit | Recorded instrumented execution path and its integrity | Soundness of model reasoning |
| ClaimProofKit | Verification result for supplied claim/evidence pairs | Runtime authorization or host enforcement |
| AgentContain | Incident lifecycle, correlation, operator workflow | Authority over the local enforcement boundary |

> **AgentContain coordinates evidence; it does not manufacture authority by aggregating evidence.**

## Canonical correlation

Every AgentContain execution has a stable execution identity:
- `execution_id`
- `agent_id`
- `policy_id`
- `policy_digest`
- `epoch`

External evidence should correlate to that identity through a small reference rather than being treated as an AgentContain event.

Recommended reference shape:

~~~json
{
  "source": "warden",
  "reference_id": "warden-event-...",
  "digest": "sha256:...",
  "relation": "observed_during",
  "captured_at": "..."
}
~~~

Recommended relations: `observed_during`, `derived_from`, `verifies`, `attests`, `supports`, and `contradicts`.

These relations are descriptive links, not authority escalation.

## Evidence semantics

AgentContain must preserve the following distinctions:

**Observed → Verified → Authenticated receipt**

These are not interchangeable.

- Warden recording a shell command is **observed**.
- AgentContainment independently confirming that the workload's cgroup is empty is **verified enforcement evidence**.
- DProvenanceKit signing an instrumented trace establishes **integrity of the recorded trace**, not truth of its contents.
- ClaimProofKit returning a supported verdict establishes the verifier's defined result against supplied evidence, not that the underlying real-world claim is universally true.

An incident should therefore be able to report each of these independently without collapsing them into a single safety verdict.

## Integration direction

### Warden → AgentContain
Warden remains an observation source. Initial integration should consume action/event identity, agent/session identity, timestamp, action classification, source reference, and an event digest where available. AgentContain uses these signals to enrich incident timelines and correlate observed activity with the execution that was authorized or contained. Warden receives no containment authority.

### AgentContainment → AgentContain
This is the authoritative runtime path. AgentContain consumes containment result, enforcement latency, verification result, fencing/lease state, proof identifiers, receipt identity, and host-test provenance where available. The platform may project this into an operator incident but must preserve the engine's exact assurance semantics.

### DProvenanceKit → AgentContain
DProvenanceKit remains the provenance/trace layer. AgentContain should reference trace identifier, trace fingerprint, baseline/candidate relationship, regression verdict, attestation/proof-pack identifier, and attestation status. AgentContain must not reinterpret a DPK trace as runtime security evidence.

### ClaimProofKit → AgentContain
ClaimProofKit remains the claim/evidence verification layer. AgentContain may associate report identifier, policy fingerprint, claim fingerprints, evidence fingerprints, verifier version, verdict, and benchmark/release-gate status where relevant. A claim-proof verdict must never transition the runtime state machine by itself.

## Incident composition

~~~text
Agent
 ├─ Execution identity
 ├─ Policy identity + digest
 ├─ Warden observations
 ├─ Authorization decision
 ├─ AgentContainment enforcement
 │   ├─ containment
 │   ├─ fencing
 │   ├─ credential invalidation
 │   └─ independent verification
 ├─ DProvenanceKit trace/provenance references
 ├─ ClaimProofKit verification references
 ├─ authenticated receipt
 └─ recovery state
~~~

The incident remains valid if any optional external source is unavailable. A missing integration should produce an explicit evidence gap, not silently downgrade an external artifact into platform evidence.

## First implementation boundary

Do **not** add hard runtime dependencies on Warden, DProvenanceKit, or ClaimProofKit.

First implementation:
1. define a versioned external-evidence reference shape;
2. validate reference identity and digest fields;
3. expose references through the existing `EvidenceEnvelope`;
4. add read-only operator projection of those references;
5. add fixture-based interoperability tests;
6. add adapters independently, starting with Warden observation and DProvenanceKit provenance.

This keeps AgentContain stdlib-only and lets each project evolve independently.

## Security invariant

External integrations must never be able to:
- authorize an execution;
- weaken a local policy;
- release containment;
- extend an expired epoch;
- restore credentials;
- mark an unverified enforcement action as verified.

They may add **context, evidence, or independently verifiable references**.

The local enforcement boundary remains authoritative.