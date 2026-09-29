# Commercial Productization Gap Analysis

**Status:** Working productization plan  
**Scope:** WarrantKit platform layer  
**Date:** 2026-09-26

## Purpose

This document translates the existing WarrantKit architecture into a buyer-facing product path. It is intentionally grounded in the capabilities already present in this repository and in the trust boundary defined by AgentContainment.

The goal is not to rebuild the enforcement engine. The goal is to put a usable control-plane and operator experience around the existing runtime, evidence, policy, fleet, and verification primitives.

## Product promise

WarrantKit answers four operational questions for autonomous-agent workloads:

1. **What is this execution authorized to do?**
2. **What happened when it crossed that boundary?**
3. **Did containment and verification actually occur?**
4. **What evidence can an operator independently inspect and retain?**

The product loop is:

**Observe → Authorize → Enforce → Detect → Contain → Verify → Prove → Recover**

The runtime remains authoritative for enforcement. The control plane coordinates policy and operations but must never become a prerequisite for local containment.

## Commercial gap trace

| Buyer journey stage | Current state | Classification | Productization work |
|---|---|---|---|
| Install runtime | Source install and submodule workflow | Implemented | Package a supported deployment path |
| Register organization/project | Local fleet hierarchy exists | Partial | Add persistent tenant/project service |
| Register runtime/agent | Fleet primitives exist | Partial | API + durable identity registry |
| Define policy | Policy model and deterministic digests exist | Implemented | Persist, version, diff, and assign through control plane |
| Assign policy | Local assignment/rollout primitives exist | Implemented locally | Central assignment API and rollout UX |
| Start execution | Execution identity/lifecycle exist | Implemented locally | Ingest execution lifecycle centrally |
| Enforce boundary | AgentContainment | Implemented in runtime layer | Product integration + supported deployment profiles |
| Detect violation | Detection/event primitives | Implemented | Central incident creation and correlation |
| Contain workload | Runtime enforcement/fencing | Implemented in runtime layer | Surface state and evidence to operator |
| Verify enforcement | Verification/evidence/receipt path | Implemented locally | Central verification result and offline-verifier workflow |
| Produce evidence | Evidence envelope/export | Implemented | Durable retention, indexing, search |
| Investigate incident | Incident projection exists | Partial | Operator incident workspace and timeline |
| Recover | Recovery lifecycle exists | Implemented locally | Operator approval/recovery workflow |
| Manage fleet | Inventory, rollout, reconciliation, history | Implemented locally | Persistent fleet service + fleet UI |
| Authenticate users | Not present as hosted service | Missing | Enterprise identity/RBAC |
| Tenant isolation | Contract defined | Contract only | Server-side authorization and isolation |
| Central evidence retention | Abstraction/seam exists | Missing | Durable multi-tenant evidence store |
| Alert/integrate | Contract-level enterprise capability | Missing | Webhooks, SIEM/SOAR, observability integrations |
| Deployment automation | Not productized | Missing | Helm/container/agent installation paths as appropriate |
| Hosted operator console | Not present | Missing | Web application/API |
| Billing/entitlements | Explicitly deferred | Missing | Commercial service only; never runtime authority |
| Supportability | Pilot specification exists | Partial | Installation diagnostics, health, upgrade and support workflows |

## What is already valuable

WarrantKit already contains the foundations that should remain the product's technical spine:

- deterministic policy identity and digests
- execution identity and authority epochs
- explicit lifecycle/state-machine semantics
- organization/project/runtime/agent fleet hierarchy
- policy assignment and rollout primitives
- deterministic reconciliation and drift classification
- fleet status history
- structured evidence envelopes
- evidence ingestion boundaries
- durable evidence-store abstraction
- incident projections
- verification receipts
- local/offline verification semantics
- operator CLI
- real-host integration proof paths
- explicit enterprise trust-boundary contracts
- explicit design-partner pilot criteria

These should be exposed through a coherent product experience rather than duplicated in a separate architecture.

## Target commercial architecture

```text
                    WarrantKit Control Plane
          ┌─────────────────────────────────────────┐
          │ Organizations / Projects / RBAC         │
          │ Fleet / Policy / Rollouts                │
          │ Incidents / Evidence / Receipts         │
          │ Integrations / Audit / Retention        │
          └───────────────────┬─────────────────────┘
                              │
                    authenticated control API
                              │
          ┌───────────────────▼─────────────────────┐
          │        WarrantKit Runtime Adapter     │
          │ identity • policy • events • evidence    │
          └───────────────────┬─────────────────────┘
                              │
                    local authoritative path
                              │
          ┌───────────────────▼─────────────────────┐
          │             AgentContainment             │
          │ cgroups • eBPF • fencing • egress       │
          │ runtime enforcement and recovery        │
          └───────────────────┬─────────────────────┘
                              │
                         agent workload

   Warden ──► observation/events
   DProvenanceKit ──► provenance/receipts
   ClaimProofKit ──► verification
```

The control plane may distribute desired policy and receive evidence, but loss of connectivity must not weaken local enforcement.

## MVP control plane

The first commercial implementation should be deliberately narrow.

### API

Minimum resources:

- organizations
- projects
- runtimes
- agents
- policies
- policy assignments
- executions
- incidents
- evidence records
- receipts

Every resource must carry explicit tenant/project scope where applicable.

### Persistence

The first production-oriented service needs durable storage for:

- identities
- policy versions/digests
- assignments and rollout state
- execution metadata
- incident state/timeline
- evidence metadata and immutable payload references
- verification results
- receipt metadata
- audit events

Original evidence must be retained. Derived summaries must never replace source evidence.

### Operator workflow

The first UI should optimize for one question:

> **Show me exactly what happened to this agent execution, why containment occurred, and what evidence proves the specified containment procedure succeeded.**

A useful navigation path is:

**Fleet → Agent → Execution → Incident → Evidence → Receipt → Recovery**

Do not begin with generic KPI dashboards.

## First end-to-end commercial demonstration

A supported demonstration should produce this sequence using the real runtime path:

1. Register a runtime and agent.
2. Assign a deterministic policy.
3. Start an execution with a stable execution identity.
4. Perform an authorized action.
5. Attempt an explicitly unauthorized action.
6. Record the detection.
7. Trigger runtime containment through AgentContainment.
8. Verify the required containment property.
9. Persist the evidence envelope.
10. Verify or bind the authenticated receipt.
11. Display the incident timeline.
12. Require explicit recovery conditions.
13. Recover under a fresh authority epoch.
14. Export the complete evidence package.

The demo must clearly label simulated/no-root paths versus real host enforcement paths.

## Commercial boundaries

### Open/local foundation

- runtime enforcement
- local policy evaluation
- execution identity
- local evidence
- local verification
- receipt verification
- CLI
- local fleet/governance primitives

### Paid platform

- hosted or private control plane
- centralized fleet operations
- durable centralized evidence retention
- incident management
- enterprise RBAC/SSO
- integrations
- deployment automation
- long-term audit/search
- supported production operations

### Non-negotiable boundary

Billing, subscription status, SaaS availability, or control-plane connectivity must never be able to disable or weaken runtime enforcement.

## Build sequence

### Phase 1 — Control-plane foundation

- service boundary
- API contract
- persistent schema
- tenant/project authorization
- runtime/agent registration
- policy persistence and assignment
- execution/event ingestion
- evidence and receipt ingestion
- incident persistence

### Phase 2 — Operator console

- authenticated operator session
- fleet view
- agent detail
- execution detail
- incident timeline
- evidence viewer
- receipt/verification view
- recovery workflow
- audit history

### Phase 3 — Real E2E product path

- one supported deployment profile
- real AgentContainment enforcement
- centralized event/evidence ingestion
- offline verification
- failure-mode testing with control plane unavailable
- complete exportable evidence package

### Phase 4 — Design-partner packaging

- installation guide
- architecture diagram
- 15-minute demonstration
- adversarial scenario pack
- pilot configuration
- evidence report template
- deployment requirements
- support runbook
- paid pilot proposal

### Phase 5 — Enterprise expansion

- SSO/RBAC
- SIEM/SOAR/webhook integrations
- retention policies
- fleet-wide rollout controls
- private control plane
- audit exports
- usage/billing metering

## Acceptance criteria for the commercial MVP

The product is ready for a design-partner deployment when a buyer can:

- install a supported runtime without reading the source tree
- register an agent and assign a policy
- see an execution with stable identity
- trigger a real policy violation
- see containment occur
- inspect the incident timeline
- inspect the underlying evidence
- distinguish observed evidence from verified evidence
- inspect the authenticated receipt
- recover only under the defined recovery conditions
- export evidence for offline review
- continue local enforcement when the control plane is unavailable

## Acquisition-oriented product properties

The product should optimize for durable technical differentiation, not merely a dashboard:

- real runtime enforcement outside the agent trust boundary
- deterministic authority and epoch semantics
- independently inspectable evidence
- a common execution identity spanning observation, enforcement, incidents, and proof
- integration surfaces for Warden, AgentContainment, DProvenanceKit, and ClaimProofKit
- developer-accessible local foundation
- enterprise control-plane monetization
- operational data and evidence workflows that become more valuable as fleet size grows

The objective is to make WarrantKit a control and evidence layer that security teams can deploy alongside existing infrastructure, not a replacement for every existing security product.

## Explicit non-goals

This phase does not attempt to:

- move enforcement authority into SaaS
- invent a new sandbox when existing infrastructure is sufficient
- claim universal host security
- replace Kubernetes, cgroups, gVisor, Kata, or existing orchestration
- make network connectivity mandatory for enforcement
- put billing logic in the runtime
- treat agent telemetry as proof
- expose a dashboard without a complete underlying execution/evidence path

## Success signal

The strongest early commercial signal is not dashboard usage.

It is a security team saying:

> "We have an autonomous workflow we cannot comfortably run without this boundary and evidence path."

The design-partner program should therefore measure production-risk reduction, containment behavior, evidence-review effort, deployment friction, and willingness to pay for continued operation.
