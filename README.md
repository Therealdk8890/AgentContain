# WarrantKit

[![WarrantKit CI](https://github.com/Therealdk8890/WarrantKit/actions/workflows/ci.yml/badge.svg)](https://github.com/Therealdk8890/WarrantKit/actions/workflows/ci.yml)

**Runtime authorization, containment, and evidence platform for autonomous AI agents.**

> **Don't ask the agent to enforce its own boundaries. Enforce them from outside the agent trust boundary.**

WarrantKit is the platform/control layer around the AgentContainment enforcement engine. The repository currently ships local authorization, admission, runtime containment coordination, epoch fencing, recovery gating, evidence envelopes, fleet-governance primitives, and offline verification receipts. Hosted multi-tenant operations, centralized evidence retention, enterprise RBAC, and SIEM/SOAR integrations are not shipped here yet.

The practical question is: **what is an autonomous agent allowed to do, what happens when it crosses that boundary, how is its authority revoked, and what evidence can be independently checked afterward?**

## 30-second demo

The fastest way to see the shipped product surface is the no-root demonstration:

```bash
git clone --recurse-submodules https://github.com/Therealdk8890/WarrantKit.git
cd WarrantKit
python -m pip install ./AgentContainment
python -m pip install .
warrantkit demo
```

This path is intentionally simulated. It demonstrates the authorization/containment lifecycle, evidence envelope, verification state, and receipt semantics without claiming kernel-level enforcement.

Use the environment-gated cgroup-v2 integration in the Real workload proof section when evaluating actual host enforcement.


## What is a Warrant?

A **Warrant** is WarrantKit's portable authority contract for an individual execution.

It binds:

- execution identity (`agent_id`, `execution_id`)
- accepted policy identity and canonical policy digest
- runtime identity and security epoch
- validity and revocation state
- permitted capabilities and constraints
- required enforcement, observation, and verification evidence

A Warrant answers:

> **Under exactly what authority was this execution admitted?**

It does **not** answer whether an action was safe, whether the agent's intent was correct, or whether an external claim is true.

The distinction is deliberate:

**Warrant = authority.**  
**Evidence = what was observed or produced.**  
**Verification = whether the defined evidence checks succeeded.**  
**Receipt = an authenticated record of that evidence.**

Evidence never grants authority, and a Warrant is never derived from evidence.

Epoch binding makes the lifecycle security property explicit: after containment or recovery advances the runtime epoch, the previous Warrant is stale and cannot authorize continued execution or recovery. Recovery therefore requires fresh authority.

## Implementation status

The table below distinguishes implemented platform capabilities from environment-gated proof and future product work. **Implemented** describes code present in the repository; **CI-tested** means the behavior is covered by automated CI; **Privileged integration-tested** means the proof requires a Linux host with the required kernel/cgroup privileges. A passing test is evidence for the tested environment, not a universal security guarantee.

| Capability | Current status | Evidence boundary |
|---|---|---|
| External authorization and admission | **Implemented · CI-tested** | Policy/admission and execution identity are enforced outside the agent runtime. |
| Runtime containment, kill, and fencing | **Implemented · lifecycle CI-tested** | Platform lifecycle/coordination is CI-tested; the real kernel kill proof is the separate privileged Linux cgroup-v2 integration test below. |
| Epoch fencing / stale-authority invalidation | **Implemented · CI-tested** | End-to-end containment → recovery → evidence regression is green on `main`. |
| Fail-closed recovery | **Implemented · CI-tested** | Recovery is runtime-authoritative; failed recovery is compensated back to containment. |
| Evidence envelopes and epoch scoping | **Implemented · CI-tested** | Structured evidence rejects stale runtime proof and preserves prior epoch history separately. |
| HMAC-authenticated receipts | **Implemented · CI-tested** | Shared-secret authentication and tamper detection; not non-repudiable attestation. |
| Linux cgroup-v2 workload containment | **Implemented · privileged integration-tested** | Real-workload proof is environment-gated and requires Linux cgroup v2 plus host privileges/delegation. |
| Adversarial containment/security regression tests | **Implemented · CI-tested** | Tests exercise fail-closed behavior and stale-authority/escape conditions in the tested environment. |
| Local fleet governance primitives | **Implemented · CI-tested** | Inventory, assignments, rollout/reconciliation, and status-history primitives are local foundations. |
| Evidence correlation and conflict handling | **Planned / partial** | WarrantKit defines the cross-source evidence contract and typed external references; a generalized runtime correlation engine and explicit conflict-resolution workflow are not yet shipped. |
| Hosted multi-tenant control plane | **Planned** | Centralized orchestration, durable evidence retention, enterprise RBAC, and hosted operations are product-layer work. |
| Enterprise integrations | **Planned / integration-dependent** | SIEM/SOAR, identity, alerting, deployment automation, and supported production operations are not implied by the open foundation. |
| Non-repudiable host attestation | **Planned** | Current receipts are HMAC-authenticated; stronger asymmetric/host-anchored attestation is a future trust model. |

The security-critical AgentContainment engine is pinned as a submodule rather than treated as an unpinned dependency. Current WarrantKit CI validates the platform against that pinned engine revision. Warden, DProvenanceKit, and ClaimProofKit are part of the platform's evidence architecture through the cross-repo evidence contract and typed external-evidence references; they are deliberately not hard runtime dependencies. Provider-specific integrations remain subject to their own host, kernel, network, and deployment requirements.

## The product

Autonomous agents can execute code, access data, call external services, and manage infrastructure. The operational problem is not only observing those actions; it is controlling them, responding when policy is violated, and producing evidence that the control actually operated.

WarrantKit is designed first as an enforcement system: define policy, establish execution identity, enforce boundaries outside the agent trust boundary, detect violations, revoke authority and credential/capability use, **forcibly terminate or fence the workload when policy requires it**, and require fresh authorization for recovery. The evidence architecture then independently records and evaluates what happened so the control is not merely asserted.

The core workflow is:

**Policy → Admit → Contain → Detect → Fence → Halt → Verify → Recover → Receipt**

This is the lifecycle used throughout the repository.

For enterprise security and governance teams, this translates into:

- **Authorization:** define the actions, resources, credentials, and execution conditions an agent is permitted to use.
- **Authority revocation:** invalidate stale or violated authority and revoke credential/capability use when policy requires it.
- **Containment:** limit what an agent workload can do at runtime, including process and egress controls where supported.
- **Hard-stop enforcement:** when policy is violated or recovery cannot safely proceed, the runtime enforcement layer can forcibly terminate and/or fence the workload rather than relying on the agent to cooperate.
- **Fail-closed response:** enforcement and recovery fail toward containment; the control plane does not treat an agent's willingness to stop as evidence of termination.
- **Auditability:** produce structured execution evidence and tamper-evident verification receipts.
- **Policy traceability:** bind executions to policy identity, policy digests, and execution identity.
- **Defense in depth:** complement existing containers, Kubernetes, gVisor, Kata, cgroups, and other isolation mechanisms.

WarrantKit can support security review and compliance evidence workflows, but it does not by itself make an organization compliant with SOC 2, HIPAA, or any other regulatory framework.

## Platform components

WarrantKit is a platform built from components with distinct responsibilities and independently derived evidence. The architecture is intentionally separated so that observation, verification, provenance, authorization, and runtime enforcement do not collapse into one trust boundary or a single source of truth.

| Component | Platform role |
|---|---|
| **WarrantKit** | Runtime control layer — authorization, admission, execution identity, authority/credential lifecycle, containment coordination, recovery gating, fleet governance, and evidence-reference binding. A generalized correlation/reconciliation engine is not yet shipped. |
| **AgentContainment** | Runtime enforcement evidence — fencing, containment, recovery, epoch invalidation, and host/provider enforcement results. |
| [**Warden**](https://github.com/Therealdk8890/warden) | Observation evidence — independently records agent activity and runtime state at its observation boundary. |
| [**ClaimProofKit**](https://github.com/Therealdk8890/ClaimProofKit) | Verification evidence — independently evaluates whether supplied claims/actions are supported by supplied evidence under its verifier rules. |
| [**DProvenanceKit**](https://github.com/Therealdk8890/DProvenanceKit) | Provenance evidence — independently records execution/reasoning provenance and produces verification-oriented proof artifacts and receipts. |

The cross-source contract is implemented at the reference/typed-evidence boundary; a generalized correlation engine that automatically reconciles all four sources and emits conflict objects is not yet shipped.

The important boundary is **not** that WarrantKit replaces these components or appoints one of them as the authority over the facts. The four core evidence sources — Warden, DProvenanceKit, ClaimProofKit, and AgentContainment — produce independently derived evidence. WarrantKit's current shipped boundary is the cross-source contract and typed external references; a generalized correlator is not yet shipped. The intended correlation model is to relate evidence by execution identity, policy identity, epoch, and evidence integrity, with disagreement surfaced as an explicit evidence conflict rather than silently resolved.

A simplified platform flow is:

```text
                         WarrantKit
                              │
              ┌───────────────┼────────────────┐
              │               │                │
        Authorization     Governance       Evidence
              │               │                │
              ▼               ▼                ▼
       AgentContainment     Warden       DProvenanceKit
              │                              │
              │                         ClaimProofKit
              ▼                              │
       Runtime enforcement                   │
              │                              │
              └──────────────┬───────────────┘
                             ▼
                       Audit / Operations
```

**The agent is never the authority for its own actions — and it is not trusted to kill itself.** WarrantKit applies externally supplied policy and authorization controls; AgentContainment performs the security-critical runtime kill/fencing enforcement; the evidence and verification layers record and evaluate what happened.


## The kill path is a first-class security control

WarrantKit is not an instruction to an agent to stop itself. **The security-critical enforcement action happens outside the agent trust boundary.** When a workload must be stopped, WarrantKit delegates the enforcement decision to the pinned AgentContainment engine, which provides the runtime kill/fencing mechanism and the corresponding enforcement evidence.

The intended control sequence is:

**Detect violation → Revoke authority → Invoke external enforcement → Kill/fence the runtime → Verify the workload is gone → Prove the enforcement event**

For the Linux cgroup-v2 path, the real-workload proof exercises a dedicated workload boundary, invokes the AgentContainment provider, independently checks that the cgroup is no longer populated, and verifies that the workload exited. This is the part of the system that turns **“the agent should stop”** into **“the runtime was actually stopped.”**

The distinction matters:

- **Warden observes.** It does not become the privileged hand that kills the workload.
- **WarrantKit authorizes and coordinates.** It revokes authority and decides when containment/recovery rules apply.
- **AgentContainment enforces.** It owns the security-critical runtime kill/fencing boundary.
- **The evidence layer proves.** It records and verifies what happened, including the relevant runtime epoch.

The platform therefore does not depend on an autonomous agent voluntarily honoring a stop instruction.

## Real workload proof

The platform includes a Linux integration proof that exercises the full local path against a real workload:

1. Create a dedicated cgroup-v2 workload boundary.
2. Launch a real child process.
3. Attach the child to that boundary.
4. Bind the boundary to a WarrantKit execution identity.
5. Invoke the pinned AgentContainment cgroup provider to **forcibly terminate the workload through the runtime enforcement boundary**.
6. Independently verify the cgroup is no longer populated.
7. Verify the workload exited.
8. Bind the resulting containment evidence to an authenticated proof receipt.
9. Verify that receipt with an offline verifier.

The proof is deliberately environment-gated because it requires Linux cgroup v2 and appropriate host privileges/delegation:

```bash
AGENT_CONTAIN_RUN_REAL_CGROUP=1 pytest -q tests/integration/test_real_cgroup_execution.py
```

A successful run is evidence from that tested Linux environment. It does not establish a universal host-security claim. The receipt is HMAC-authenticated and tamper-evident; it is not a non-repudiable attestation. The HMAC secret is supplied by the operator/deployer to the process that creates the receipt (via the CLI's secret-file or environment-variable path). Anyone who possesses that shared secret can create a valid HMAC, so the receipt does not establish non-repudiable authorship or identify a particular key holder.


## Independent verification

WarrantKit publishes a standalone reference verifier for the portable runtime-pinned evidence contract. The verifier uses only the Python standard library: it does not import WarrantKit or AgentContainment and does not consult control-plane state.

This is the intended **“don't trust our code”** path: an exported evidence artifact can be checked by an independent implementation against the published contract.

```bash
python tools/verify_runtime_evidence.py tests/fixtures/runtime_pinned_evidence.json
# VERIFIED
```

The fixture is a contract test artifact, not a claim about a real external execution. The verifier also rejects byte mutation, rewritten-and-rehashed records, runtime identity mismatch, and stale epoch.

## Proof semantics

WarrantKit deliberately separates three different claims about an execution:

| State | What it means |
|---|---|
| **Observed** | An event or result was recorded. |
| **Verified** | The defined verification procedure and its required evidence checks succeeded. |
| **Authenticated receipt** | The resulting evidence was bound to a tamper-evident, HMAC-authenticated receipt. |

**Verified ≠ claim is true.**

Verification establishes that the specified procedure and evidence checks succeeded. It does not establish the truth of an arbitrary external claim, and an authenticated receipt is not a non-repudiable host attestation.

The lifecycle also distinguishes **detection** from **verification**: detection records an anomaly; verification records completion of the defined verification procedure. They are separate evidence events.

## How WarrantKit differs

WarrantKit is not a replacement for the runtime-security and isolation technologies it can work alongside.

| Technology | Primary boundary | What WarrantKit adds |
|---|---|---|
| **Tetragon** | Kernel-level runtime observability and policy enforcement, including event monitoring and enforcement actions such as signals/return-value overrides. | WarrantKit addresses a different boundary: authority is bound to a runtime epoch, and containment/recovery advances that epoch so stale authority cannot authorize continued execution or recovery. A policy engine can decide what to allow; WarrantKit makes the authority lifecycle and invalidation boundary explicit around that decision. |
| **seccomp** | Linux system-call filtering for a process. | Agent-specific admission/authority lifecycle, runtime containment coordination, epoch fencing, recovery gating, and structured evidence/proof semantics around the enforcement event. |
| **gVisor** | Sandboxed application-kernel boundary for containers. | Control-plane authorization and runtime evidence that can sit above an isolation boundary rather than replacing the isolation mechanism. |

These are complementary rather than mutually exclusive. Tetragon already provides substantial runtime enforcement and observability; gVisor provides a sandboxed runtime boundary; seccomp restricts system calls. WarrantKit's narrower claim is that **agent authorization, runtime enforcement coordination, and independently verifiable evidence should remain explicit and separate from the agent itself**.

## Threat model and non-goals

The primary threat model is an autonomous agent that must be treated as untrusted. WarrantKit therefore keeps authorization, revocation, containment, and recovery outside the agent trust boundary and delegates security-critical runtime enforcement to AgentContainment.

The platform threat model is documented in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md). The lower-level AgentContainment security contract is documented in [`AgentContainment/docs/SECURITY_CONTRACT.md`](https://github.com/Therealdk8890/AgentContainment/blob/main/docs/SECURITY_CONTRACT.md). In particular, the project distinguishes controls that are implemented and tested from assumptions about the host, kernel, cgroup hierarchy, runtime, and external enforcement providers.

### Current non-goals

- **Not a universal host-isolation guarantee.** The real workload proof covers the tested Linux environment; it does not establish security properties for every kernel, container runtime, namespace, or deployment topology.
- **Not agent-cooperative containment.** Telling an agent to stop is not treated as enforcement evidence.
- **Not reversal of completed side effects.** Revocation and containment prevent further authority where the enforcement boundary permits; they cannot undo effects that already escaped the boundary.
- **Not a secret manager.** The current credential primitive models runtime-scoped revocable authority; it does not automatically revoke arbitrary third-party cloud/API credentials.
- **Not formal verification or host attestation.** Passing the tests demonstrates the tested behavior and assumptions; HMAC receipts provide authentication/tamper evidence, not non-repudiation.

### Open boundary: controller isolation

Controller isolation remains deployment-sensitive. The repository tests selected controller/agent IPC and host attack paths, but the controller, its IPC endpoint, the cgroup hierarchy, and the privileges used to enforce containment must still be protected by the deployment. The Python control plane alone is not claimed to be a kernel isolation boundary. The AgentContainment documentation describes the required host-side assumptions and current proof scope.

## Architecture

The control and enforcement boundaries are intentionally separate:

```text
                         WarrantKit
              authority / lifecycle / evidence
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     Authorization   Governance     Evidence refs
          │              │              │
          ▼              ▼              ▼
   AgentContainment    Warden      DProvenanceKit
   runtime enforcement              ClaimProofKit
          │              │              │
          └──────────────┴──────────────┘
                         │
                 operator / audit view
```

WarrantKit coordinates authority and lifecycle state; AgentContainment remains the security-critical runtime enforcement boundary. The other sources produce evidence within their own declared boundaries. WarrantKit uses explicit identity and evidence references to relate those sources; it does not treat them as one trust domain.


## Core engine

The current enforcement implementation lives in the companion repository. The broader evidence architecture spans independently derived evidence sources:

- **AgentContainment** — the runtime enforcement technology and security-critical enforcement source.
- **Warden** — the observation source.
- **DProvenanceKit** — the provenance/integrity source.
- **ClaimProofKit** — the claim/evidence verification source.
- **WarrantKit** — the correlation and control layer that relates those independent facts without turning any one source into a universal authority.

This repository pins the AgentContainment engine as a Git submodule so the security-critical implementation remains independently reviewable while the platform surface is developed here.

## What the platform is designed to provide

- Runtime enforcement outside the agent trust boundary.
- External hard-stop / kill and fencing of contained workloads.
- Deterministic admission and policy control.
- Authority and credential/capability revocation after policy violations.
- Epoch fencing and stale-authority invalidation.
- Linux cgroup v2 process containment.
- Kernel-level egress enforcement integrations.
- Adversarial security testing.
- Structured execution evidence envelopes.
- Governance-bound execution evidence.
- Tamper-evident verification receipts.
- Fail-closed recovery.
- Fleet inventory, policy rollout, reconciliation, and status history.
- Portable evidence export for downstream systems.
- Integration with existing sandboxing and orchestration infrastructure.

## Security posture

This project is **early-stage and actively developed toward a production 1.0 release**.

Passing an adversarial test demonstrates behavior in the tested environment. It is not a universal security guarantee, formal verification, or cryptographic attestation of the host.

Security-critical claims are documented in the AgentContainment security contract and backed by privileged integration tests where host/kernel behavior is required.

## Fleet governance

WarrantKit includes local governance primitives for managing fleets above the enforcement engine. These primitives are deliberately separate from runtime authority: governance can describe desired state, rollout progress, and fleet status without weakening or replacing local enforcement.

Current platform primitives include:

- **Organization → Project → Runtime → Agent** inventory and immutable governance scope.
- **Policy assignments** carrying policy identity, version, digest, target, and explicit assignment state.
- **Deterministic policy rollouts** with draft, staged, rolling-out, paused, converged, and rejected states.
- **Deterministic reconciliation** that classifies target state such as converged, pending, drifted, missing, rejected, and superseded.
- **Fleet policy status** as a stable machine-readable aggregate.
- **Immutable status history** with monotonic snapshots, collision detection, and idempotent append behavior.

The design intentionally keeps rollout and fleet observation from becoming the security enforcement boundary. Local enforcement remains the final control point for accepting and enforcing policy, while WarrantKit controls the authorization lifecycle around it.

The open package provides these as **local governance primitives**. They do not constitute a hosted multi-tenant control plane, server-side RBAC system, or centralized enforcement authority.


## Evidence model

WarrantKit exposes a transport-neutral `EvidenceEnvelope` for machine-readable execution evidence. The current v2 envelope binds execution identity, ordered events, enforcement state, verification state, proof data, optional governance scope, provenance, and an optional authenticated receipt into one canonical representation.

The envelope validates execution identity, contiguous event sequencing, supported verification states, and receipt identity binding where present. It can be serialized to deterministic JSON for storage or transport and reconstructed offline.

Governance scope can be attached to execution evidence so downstream systems can associate an execution with its organization, project, runtime, and agent context without giving that governance layer authority over enforcement.

**Evidence is evidence, not authority:** a valid envelope or receipt records and verifies the defined evidence procedure; it does not by itself prove an arbitrary external claim is true.

## License

Apache-2.0.
