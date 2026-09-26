# AgentContain Enterprise Contract

**Status:** v0.1 commercial architecture contract  
**Scope:** Control-plane boundary, not runtime enforcement

AgentContain Enterprise adds centralized governance and fleet operations around the open AgentContain runtime. It does not replace, weaken, or become a prerequisite for the local enforcement trust boundary.

## Design principle

> **The runtime remains authoritative for enforcement. The control plane is authoritative for governance, coordination, and durable evidence management.**

An Enterprise control plane must never be able to turn a failed local enforcement operation into a successful security result.

## Product boundary

| Capability | AgentContain / AgentContainment | Enterprise |
|---|---:|---:|
| Local policy evaluation | Yes | Optional centralized policy distribution |
| Execution identity | Yes | Fleet inventory and lifecycle |
| Runtime containment | Yes | No replacement |
| cgroup / kernel enforcement integrations | Yes | No replacement |
| Local verification | Yes | No replacement |
| Local proof receipts | Yes | Central ingestion and retention |
| Adversarial proof execution | Yes | Fleet evidence aggregation |
| Policy management | Local | Centralized |
| Fleet/workload inventory | Local execution context | Yes |
| Central evidence store | No | Yes |
| Audit history | Local artifacts | Yes |
| Organization/project boundaries | No | Yes |
| RBAC | No | Yes |
| Alerts/integrations | Local integration points | Yes |
| Billing/subscription | No | Yes |

## Trust boundaries

The system has three distinct authorities:

1. **Agent** — untrusted workload. It cannot establish its own containment result.
2. **Runtime enforcement** — security-critical authority. It performs and independently verifies enforcement.
3. **Enterprise control plane** — governance authority. It manages policy, fleet state, evidence retention, access, and integrations.

The control plane may request an action, but the runtime must independently establish whether the action occurred.

## Failure semantics

Loss of Enterprise connectivity must not disable local containment.

If the control plane is unavailable:
- local enforcement continues;
- local verification continues;
- local receipts may continue to be generated;
- evidence may queue for later ingestion;
- a runtime must not report containment as successful merely because the control plane accepted a request.

If control-plane state conflicts with independently produced runtime evidence, the two must remain distinguishable.

## Evidence ingestion

Enterprise consumes the Evidence API defined in [EVIDENCE_API.md](EVIDENCE_API.md). The minimum ingestion unit is an execution evidence envelope containing execution identity, policy identity/digest, event sequence, enforcement result, verification result, proof references, receipt, provenance, and environment metadata.

Enterprise storage must preserve the original evidence rather than replacing it with a derived status.

## Policy distribution

Central policy management is a distribution mechanism, not an enforcement mechanism. A policy should be authored centrally, versioned, canonically serialized, hashed, delivered to a runtime, independently validated by the runtime, bound to the execution identity, and enforced locally.

A runtime must reject or quarantine a policy it cannot validate against its expected schema or digest.

## Tenant isolation

Enterprise data is scoped at minimum by:

`organization → project → runtime → agent → execution → evidence`

Authorization must be enforced server-side for every tenant-scoped read and write. Evidence from one organization must not become visible through another organization's API, dashboard, export, or search path.

## Commercial boundary

Billing belongs above the runtime boundary. The runtime package must not require a SaaS account, billing token, network access to an AgentContain service, subscription check, or control-plane callback to perform local enforcement or verification.

Commercial entitlement may govern Enterprise services such as fleet management, centralized retention, RBAC, integrations, and hosted audit capabilities.

## Security claims

Enterprise dashboards must preserve the same evidence semantics as the open runtime:
- **Observed** means an event or report was received.
- **Verified** means a designated verifier established a specified property in a tested environment.
- **Authenticated receipt** means the receipt passed its cryptographic integrity/authentication checks.
- None of these labels alone establishes that an underlying system claim is universally true.

The UI and APIs must not collapse these distinctions into a generic "secure" or "safe" status.

## Initial Enterprise non-goals

- Moving enforcement authority into the SaaS control plane.
- Making network connectivity a prerequisite for containment.
- Replacing Kubernetes, containers, gVisor, Kata, cgroups, or host controls.
- Claiming universal host security from centralized evidence.
- Introducing billing logic into AgentContainment.
- Treating agent-generated telemetry as authoritative proof.

## Acceptance criteria

The commercial architecture is ready for implementation when a reviewer can demonstrate that:
1. an execution can be fully contained with no Enterprise connectivity;
2. its local evidence can be verified independently;
3. evidence can be ingested without changing its semantics;
4. policy distribution preserves policy identity and digest;
5. tenant boundaries are explicit in the data model and authorization layer;
6. an Enterprise outage does not create a containment bypass;
7. billing or entitlement failure cannot disable runtime enforcement.
