# WarrantKit

**Runtime security and evidence platform for autonomous AI agents.**

> **Don't ask the agent to enforce its own boundaries. Enforce them from outside the agent trust boundary.**

WarrantKit is the buyer-facing platform layer around the AgentContainment runtime enforcement engine. It is designed to answer a practical enterprise question: **what is an autonomous agent allowed to do, what happens when it crosses that boundary, and can we prove what happened?**

## The product

Autonomous agents can execute code, access data, call external services, and manage infrastructure. The operational problem is not only observing those actions; it is controlling them, responding when policy is violated, and producing evidence that the control actually operated.

WarrantKit is designed as a runtime security and evidence platform: define policy, establish execution identity, enforce boundaries outside the agent trust boundary, detect violations, contain and recover workloads, and produce machine-readable evidence for security operations and audit workflows.

The core workflow is:

**Discover → Authorize → Enforce → Detect → Contain → Verify → Recover → Prove**

For enterprise security and governance teams, this translates into:

- **Containment:** limit what an agent workload can do at runtime, including process and egress controls where supported.
- **Fail-closed response:** fence and halt workloads when enforcement or recovery conditions require it.
- **Auditability:** produce structured execution evidence and tamper-evident verification receipts.
- **Policy traceability:** bind executions to policy identity, policy digests, and execution identity.
- **Defense in depth:** complement existing containers, Kubernetes, gVisor, Kata, cgroups, and other isolation mechanisms.

WarrantKit can support security review and compliance evidence workflows, but it does not by itself make an organization compliant with SOC 2, HIPAA, or any other regulatory framework.

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

The platform CLI is available as `agentcontain`. The current runtime path uses the pinned AgentContainment engine, so a source checkout must include the submodule and its Python package:

```bash
git clone --recurse-submodules https://github.com/Therealdk8890/WarrantKit.git
cd WarrantKit
python -m pip install ./AgentContainment
python -m pip install .
agentcontain run --policy demo --agent-id demo-agent --contain
```

This exercises the real runtime adapter and may require a Linux environment with the privileges and cgroup setup required by the selected enforcement path. It is not the no-root demonstration path.

A dedicated no-root demonstration is available with `agentcontain demo`. It demonstrates the lifecycle, evidence envelope, and receipt semantics without host privileges. It is explicitly **simulated** and must not be interpreted as kernel-level containment proof.

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

**Policy → Admit → Contain → Detect → Fence → Halt → Verify → Recover → Receipt**

## Core engine

The current enforcement implementation lives in the companion repository:

- **AgentContainment** — the runtime enforcement technology and security-critical core.
- **WarrantKit** — the broader platform that integrates enforcement, detection, recovery, proof, policy, and operational tooling.

This repository pins the AgentContainment engine as a Git submodule so the security-critical implementation remains independently reviewable while the platform surface is developed here.

## Buyer outcomes

WarrantKit is being built for teams operating autonomous agents where an execution boundary, incident response path, and defensible evidence trail matter.

### Core buyer workflows

- **Runtime authorization:** define what an agent, workload, credential, and network path are permitted to do.
- **Policy violation response:** detect an attempted violation and move from authorization failure to runtime containment when required.
- **Incident containment:** fence execution, invalidate stale authority, revoke credential use, and halt the workload through the enforcement layer.
- **Verification and evidence:** distinguish an observed event from successful verification and bind the resulting evidence to an authenticated receipt.
- **Recovery:** release external enforcement only after the required conditions are independently verified, then restore execution under a fresh authority epoch.
- **Fleet governance:** associate agents with organization, project, runtime, policy, status, and rollout state without allowing governance infrastructure to weaken local enforcement.

### What a buyer should eventually see

A contained incident should be understandable without reading source code:

```text
Agent:        payments-agent-1842
Policy:       payments-prod-v7
Event:        unauthorized credential use
Decision:     DENY
Containment:  runtime fenced
Credentials:  stale authority revoked
Verification: enforcement independently verified
Receipt:      authenticated
Recovery:     pending operator approval
```

The commercial platform layer will add the operator workflow, centralized evidence, identity/RBAC, integrations, and fleet operations around the open enforcement foundation.

## What the platform is designed to provide

- Runtime enforcement outside the agent trust boundary.
- Deterministic admission and policy control.
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

The design intentionally keeps rollout and fleet observation from becoming enforcement authority. Local runtimes remain authoritative for accepting and enforcing policy.

The open package provides these as **local governance primitives**. They do not constitute a hosted multi-tenant control plane, server-side RBAC system, or centralized enforcement authority.

## Commercial product boundary

The open foundation is intentionally inspectable and independently usable. The commercial WarrantKit platform is where centralized operations become the product: fleet-wide policy distribution, durable evidence retention, incident workflows, enterprise identity and RBAC, SIEM/SOAR integrations, deployment automation, and supported production operations.

The enforcement boundary remains local and authoritative. A hosted control plane must never be able to weaken containment because of network failure, billing state, service outage, or loss of connectivity.

## Enterprise & support

WarrantKit is being developed with a clear separation between the open runtime/governance foundation and future centralized enterprise capabilities.

The open platform provides local fleet governance, runtime enforcement, verification, and evidence primitives. Future centralized capabilities can build above that foundation for organizations that need coordinated governance across many agents and runtimes, including areas such as:

- Centralized policy distribution and fleet orchestration.
- Durable evidence storage and long-term audit history.
- RBAC and enterprise identity integrations.
- Alerts, webhooks, SIEM, and observability integrations.
- Deployment and integration support.

The security-critical runtime remains authoritative for enforcement. Fleet governance and any future centralized control plane must not be able to weaken local containment because of a network outage, billing state, unavailable service, or control-plane failure.

**For enterprise integration, design-partner deployments, or custom security engineering, contact the project maintainers.**

## Repository relationship

```
WarrantKit
    │
    └── AgentContainment (security-critical runtime engine)
```

The AgentContainment repository remains public and independently usable while WarrantKit is the flagship platform repository.

## License

Apache-2.0.

## Real workload proof

The platform includes a Linux integration proof that exercises the full local path against a real workload:

1. Create a dedicated cgroup-v2 workload boundary.
2. Launch a real child process.
3. Attach the child to that boundary.
4. Bind the boundary to a WarrantKit execution identity.
5. Invoke the pinned AgentContainment cgroup provider.
6. Independently verify the cgroup is no longer populated.
7. Verify the workload exited.
8. Bind the resulting containment evidence to an authenticated proof receipt.
9. Verify that receipt with an offline verifier.

The proof is deliberately environment-gated because it requires Linux cgroup v2 and appropriate host privileges/delegation:

```bash
AGENT_CONTAIN_RUN_REAL_CGROUP=1 pytest -q tests/integration/test_real_cgroup_execution.py
```

A successful run is evidence from that tested Linux environment. It does not establish a universal host-security claim. The receipt is HMAC-authenticated and tamper-evident; it is not a non-repudiable attestation.


## Evidence model

WarrantKit exposes a transport-neutral `EvidenceEnvelope` for machine-readable execution evidence. The current v2 envelope binds execution identity, ordered events, enforcement state, verification state, proof data, optional governance scope, provenance, and an optional authenticated receipt into one canonical representation.

The envelope validates execution identity, contiguous event sequencing, supported verification states, and receipt identity binding where present. It can be serialized to deterministic JSON for storage or transport and reconstructed offline.

Governance scope can be attached to execution evidence so downstream systems can associate an execution with its organization, project, runtime, and agent context without giving that governance layer authority over enforcement.

**Evidence is evidence, not authority:** a valid envelope or receipt records and verifies the defined evidence procedure; it does not by itself prove an arbitrary external claim is true.
