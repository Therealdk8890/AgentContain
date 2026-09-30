# WarrantKit

[![WarrantKit CI](https://github.com/Therealdk8890/WarrantKit/actions/workflows/ci.yml/badge.svg)](https://github.com/Therealdk8890/WarrantKit/actions/workflows/ci.yml)

**Runtime authorization, containment, and evidence platform for autonomous AI agents.**

> **Don't ask the agent to enforce its own boundaries. Enforce them from outside the agent trust boundary.**

WarrantKit is the runtime security platform around the AgentContainment enforcement engine. It answers a practical security question: **what is an autonomous agent allowed to do, what happens when it crosses that boundary, how do we revoke its authority, and can we prove that the security boundary held?**

## The product

Autonomous agents can execute code, access data, call external services, and manage infrastructure. The operational problem is not only observing those actions; it is controlling them, responding when policy is violated, and producing evidence that the control actually operated.

WarrantKit is designed first as an enforcement system: define policy, establish execution identity, enforce boundaries outside the agent trust boundary, detect violations, revoke authority and credential/capability use, **forcibly terminate or fence the workload when policy requires it**, and require fresh authorization for recovery. The evidence architecture then independently records and evaluates what happened so the control is not merely asserted.

The core workflow is:

**Discover → Authorize → Enforce → Detect → Revoke → Halt/Contain → Verify → Recover → Prove**

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
| **WarrantKit** | Runtime control layer — authorization, admission, execution identity, authority/credential lifecycle, containment coordination, recovery gating, fleet governance, and evidence correlation. It does not become the universal authority over independently produced facts. |
| **AgentContainment** | Runtime enforcement evidence — fencing, containment, recovery, epoch invalidation, and host/provider enforcement results. |
| **Warden** | Observation evidence — independently records agent activity and runtime state at its observation boundary. |
| **ClaimProofKit** | Verification evidence — independently evaluates whether supplied claims/actions are supported by supplied evidence under its verifier rules. |
| **DProvenanceKit** | Provenance evidence — independently records execution/reasoning provenance and produces verification-oriented proof artifacts and receipts. |
| **hermetic-sandbox** | Isolation support — constrained execution environments that complement runtime enforcement. |
| **cancelscope** | Cancellation support — structured cancellation and termination control. |
| **interleave-test** | Concurrency/regression support — deterministic interleavings and race-sensitive testing. |
| **pytest-flakedoctor** | Development/test support — flaky-test detection and diagnosis. |

The important boundary is **not** that WarrantKit replaces these components or appoints one of them as the authority over the facts. The four core evidence sources — Warden, DProvenanceKit, ClaimProofKit, and AgentContainment — produce independently derived evidence. WarrantKit correlates that evidence by execution identity, policy identity, epoch, and evidence integrity. Agreement increases confidence; disagreement becomes an explicit evidence conflict rather than being silently resolved.

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

The supporting components provide isolation, cancellation, concurrency testing, and test-reliability capabilities around that core.

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

A successful run is evidence from that tested Linux environment. It does not establish a universal host-security claim. The receipt is HMAC-authenticated and tamper-evident; it is not a non-repudiable attestation.


## Implementation status

The table below distinguishes implemented platform capabilities from environment-gated proof and future product work. **Implemented** describes code present in the repository; **CI-tested** means the behavior is covered by automated CI; **Privileged integration-tested** means the proof requires a Linux host with the required kernel/cgroup privileges. A passing test is evidence for the tested environment, not a universal security guarantee.

| Capability | Current status | Evidence boundary |
|---|---|---|
| External authorization and admission | **Implemented · CI-tested** | Policy/admission and execution identity are enforced outside the agent runtime. |
| Runtime containment, kill, and fencing | **Implemented · CI-tested** | Delegated to the pinned AgentContainment engine; the enforcement boundary is external to the agent. |
| Epoch fencing / stale-authority invalidation | **Implemented · CI-tested** | End-to-end containment → recovery → evidence regression is green on `main`. |
| Fail-closed recovery | **Implemented · CI-tested** | Recovery is runtime-authoritative; failed recovery is compensated back to containment. |
| Evidence envelopes and epoch scoping | **Implemented · CI-tested** | Structured evidence rejects stale runtime proof and preserves prior epoch history separately. |
| HMAC-authenticated receipts | **Implemented · CI-tested** | Shared-secret authentication and tamper detection; not non-repudiable attestation. |
| Linux cgroup-v2 workload containment | **Implemented · privileged integration-tested** | Real-workload proof is environment-gated and requires Linux cgroup v2 plus host privileges/delegation. |
| Adversarial containment/security regression tests | **Implemented · CI-tested** | Tests exercise fail-closed behavior and stale-authority/escape conditions in the tested environment. |
| Local fleet governance primitives | **Implemented · CI-tested** | Inventory, assignments, rollout/reconciliation, and status-history primitives are local foundations. |
| Hosted multi-tenant control plane | **Planned** | Centralized orchestration, durable evidence retention, enterprise RBAC, and hosted operations are product-layer work. |
| Enterprise integrations | **Planned / integration-dependent** | SIEM/SOAR, identity, alerting, deployment automation, and supported production operations are not implied by the open foundation. |
| Non-repudiable host attestation | **Planned** | Current receipts are HMAC-authenticated; stronger asymmetric/host-anchored attestation is a future trust model. |

The security-critical AgentContainment engine is pinned as a submodule rather than treated as an unpinned dependency. Current WarrantKit CI validates the platform against that pinned engine revision. Warden, DProvenanceKit, and ClaimProofKit are part of the platform's evidence architecture through the cross-repo evidence contract and typed external-evidence references; they are deliberately not hard runtime dependencies. Provider-specific integrations remain subject to their own host, kernel, network, and deployment requirements.

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

## Current quick start

The project is **WarrantKit**; the project-facing CLI is **`warrantkit`**. The legacy **`agentcontain`** command remains as a compatibility alias.

The platform CLI is available as `agentcontain`.

### 1. Simulated demonstration — no host privileges

Start with the no-root path:

```bash
git clone --recurse-submodules https://github.com/Therealdk8890/WarrantKit.git
cd WarrantKit
python -m pip install ./AgentContainment
python -m pip install .
warrantkit demo
```

This demonstrates the lifecycle, evidence envelope, and receipt semantics without host privileges. It is explicitly **simulated** and must not be interpreted as kernel-level containment proof.

### 2. Real runtime path — Linux

The real runtime adapter uses the pinned AgentContainment engine:

```bash
warrantkit run --policy demo --agent-id demo-agent --contain
```

The real path may require Linux, cgroup-v2 support, and the privileges/delegation required by the selected enforcement provider. The host-boundary proof above is the stronger path to use when evaluating actual workload containment.

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

```
WarrantKit
│
├── Policy / Admission / Identity
│
├── AgentContainment
│   ├── Admission
│   ├── Fencing
│   ├── Runtime enforcement
│   ├── Cgroup containment
│   └── Egress enforcement
│
├── Detection
├── Recovery
│   └── Fail-closed recovery
│
└── Proof
    ├── Adversarial evidence
    ├── Structured proof
    └── Verification receipts
```

The platform lifecycle is:

**Policy → Admit → Enforce → Detect → Revoke → Fence/Halt → Verify → Recover under fresh authority → Receipt**

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

The project intentionally distinguishes:

- **Observed** — an event or result was recorded.
- **Verified** — the defined verification procedure succeeded.
- **Authenticated receipt** — evidence was bound to a tamper-evident, HMAC-authenticated receipt.
- **Verified ≠ claim is true** — verification establishes that the specified procedure and evidence checks succeeded; it does not establish the truth of an arbitrary external claim.

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

## Repository relationship

```
                 WarrantKit
          correlation / control layer
                    │
       ┌────────────┼────────────┐
       │            │            │
    Warden   DProvenanceKit  ClaimProofKit
  observation  provenance    verification
       │            │            │
       └────────────┼────────────┘
                    │
             AgentContainment
             runtime enforcement
```

WarrantKit correlates independently derived evidence from these sources. The sources do not form a hierarchy of epistemic authority: each is responsible for facts within its own evidence boundary. Agreement is corroboration; disagreement is an evidence conflict that must remain visible. AgentContainment remains public and independently usable as the security-critical runtime enforcement engine.

## License

Apache-2.0.

## Evidence model

WarrantKit exposes a transport-neutral `EvidenceEnvelope` for machine-readable execution evidence. The current v2 envelope binds execution identity, ordered events, enforcement state, verification state, proof data, optional governance scope, provenance, and an optional authenticated receipt into one canonical representation.

The envelope validates execution identity, contiguous event sequencing, supported verification states, and receipt identity binding where present. It can be serialized to deterministic JSON for storage or transport and reconstructed offline.

Governance scope can be attached to execution evidence so downstream systems can associate an execution with its organization, project, runtime, and agent context without giving that governance layer authority over enforcement.

**Evidence is evidence, not authority:** a valid envelope or receipt records and verifies the defined evidence procedure; it does not by itself prove an arbitrary external claim is true.
