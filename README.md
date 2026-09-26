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
- Structured execution evidence.
- Tamper-evident verification receipts.
- Fail-closed recovery.
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

## Enterprise & support

AgentContain is being developed with a clear separation between the open runtime and future centralized enterprise capabilities.

The open platform is intended to provide the runtime enforcement, local verification, and evidence foundations. Enterprise capabilities can build above that foundation for organizations that need centralized governance across many agents and runtimes, including areas such as:

- Fleet and workload inventory.
- Centralized policy distribution.
- Durable evidence storage and audit history.
- Organization and project boundaries.
- RBAC and enterprise identity integrations.
- Alerts, webhooks, SIEM, and observability integrations.
- Deployment and integration support.

The security-critical runtime remains authoritative for enforcement. A future control plane must not be able to weaken local containment because of a network outage, billing state, unavailable service, or control-plane failure.

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
