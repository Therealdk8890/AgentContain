# AgentContain

**Runtime enforcement and proof platform for autonomous AI agents.**

> **Don't ask the agent to enforce its own boundaries. Enforce them from outside the agent trust boundary.**

AgentContain is the platform layer around the AgentContainment runtime enforcement engine.

## Why this matters to the enterprise

Autonomous agents can execute code, access data, call external services, and manage infrastructure. Traditional application controls and model-level instructions do not by themselves establish an authoritative runtime boundary around those actions.

AgentContain is designed to provide that boundary from outside the agent trust boundary, with deterministic enforcement, independent verification, and machine-readable evidence.

For enterprise security and governance teams, this translates into:

- **Containment:** limit what an agent workload can do at runtime, including process and egress controls where supported.
- **Fail-closed response:** fence and halt workloads when enforcement or recovery conditions require it.
- **Auditability:** produce structured execution evidence and tamper-evident verification receipts.
- **Policy traceability:** bind executions to policy identity, policy digests, and execution identity.
- **Defense in depth:** complement existing containers, Kubernetes, gVisor, Kata, cgroups, and other isolation mechanisms.

AgentContain can support security review and compliance evidence workflows, but it does not by itself make an organization compliant with SOC 2, HIPAA, or any other regulatory framework.

## Proof semantics

AgentContain deliberately separates three different claims about an execution:

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
git clone --recurse-submodules https://github.com/Therealdk8890/AgentContain.git
cd AgentContain
python -m pip install ./AgentContainment
python -m pip install .
agentcontain run --policy demo --agent-id demo-agent --contain
```

This exercises the real runtime adapter and may require a Linux environment with the privileges and cgroup setup required by the selected enforcement path. It is not the no-root demonstration path.

A dedicated **no-root demo path** is planned to demonstrate the platform lifecycle, evidence envelope, and receipt verification without requiring host enforcement privileges. It will be explicitly labeled as simulated containment rather than presented as kernel-level proof.

## Architecture

```
AgentContain
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
- **AgentContain** — the broader platform that integrates enforcement, detection, recovery, proof, policy, and operational tooling.

This repository pins the AgentContainment engine as a Git submodule so the security-critical implementation remains independently reviewable while the platform surface is developed here.

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

AgentContain includes local governance primitives for managing fleets above the enforcement engine. These primitives are deliberately separate from runtime authority: governance can describe desired state, rollout progress, and fleet status without weakening or replacing local enforcement.

Current platform primitives include:

- **Organization → Project → Runtime → Agent** inventory and immutable governance scope.
- **Policy assignments** carrying policy identity, version, digest, target, and explicit assignment state.
- **Deterministic policy rollouts** with draft, staged, rolling-out, paused, converged, and rejected states.
- **Deterministic reconciliation** that classifies target state such as converged, pending, drifted, missing, rejected, and superseded.
- **Fleet policy status** as a stable machine-readable aggregate.
- **Immutable status history** with monotonic snapshots, collision detection, and idempotent append behavior.

The design intentionally keeps rollout and fleet observation from becoming enforcement authority. Local runtimes remain authoritative for accepting and enforcing policy.

The open package provides these as **local governance primitives**. They do not constitute a hosted multi-tenant control plane, server-side RBAC system, or centralized enforcement authority.

## Enterprise & support

AgentContain is being developed with a clear separation between the open runtime/governance foundation and future centralized enterprise capabilities.

The open platform provides local fleet governance, runtime enforcement, verification, and evidence primitives. Future centralized capabilities can build above that foundation for organizations that need coordinated governance across many agents and runtimes, including areas such as:

- Centralized policy distribution and fleet orchestration.
- Durable evidence storage and long-term audit history.
- RBAC and enterprise identity integrations.
- Alerts, webhooks, SIEM, and observability integrations.
- Deployment and integration support.

The security-critical runtime remains authoritative for enforcement. Fleet governance and any future centralized control plane must not be able to weaken local containment because of a network outage, billing state, unavailable service, or control-plane failure.

**For enterprise integration, deployment support, or custom security engineering, contact the project maintainers.**

## Repository relationship

```
AgentContain
    │
    └── AgentContainment (security-critical runtime engine)
```

The legacy AgentContainment repository remains public and independently usable while AgentContain becomes the flagship platform repository.

## License

Apache-2.0.

## Real workload proof

The platform includes a Linux integration proof that exercises the full local path against a real workload:

1. Create a dedicated cgroup-v2 workload boundary.
2. Launch a real child process.
3. Attach the child to that boundary.
4. Bind the boundary to an AgentContain execution identity.
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

AgentContain exposes a transport-neutral `EvidenceEnvelope` for machine-readable execution evidence. The v1 envelope binds execution identity, ordered events, enforcement state, verification state, proof data, optional governance scope, provenance, and an optional authenticated receipt into one canonical representation.

The envelope validates execution identity, contiguous event sequencing, supported verification states, and receipt identity binding where present. It can be serialized to deterministic JSON for storage or transport and reconstructed offline.

Governance scope can be attached to execution evidence so downstream systems can associate an execution with its organization, project, runtime, and agent context without giving that governance layer authority over enforcement.

**Evidence is evidence, not authority:** a valid envelope or receipt records and verifies the defined evidence procedure; it does not by itself prove an arbitrary external claim is true.
