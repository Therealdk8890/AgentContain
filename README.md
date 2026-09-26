# AgentContain

**Runtime enforcement and proof platform for autonomous AI agents.**

> **Don't ask the agent to enforce its own boundaries. Enforce them from outside the agent trust boundary.**

AgentContain is the platform layer around the AgentContainment runtime enforcement engine.

## Architecture

```
AgentContain
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
- **AgentContain** — the broader platform that will integrate enforcement, detection, recovery, proof, policy, and operational tooling.

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
- Integration with existing sandboxing and orchestration infrastructure.

AgentContain is designed to work **alongside** containers, Kubernetes, gVisor, Kata, cgroups, and other isolation mechanisms rather than requiring organizations to replace them.

## Security posture

This project is early-stage research/prototype software.

Passing an adversarial test demonstrates behavior in the tested environment. It is not a universal security guarantee, formal verification, or cryptographic attestation of the host.

Security-critical claims are documented in the AgentContainment security contract and backed by privileged integration tests where host/kernel behavior is required.

## Repository relationship

```
AgentContain
    │
    └── AgentContainment (security-critical runtime engine)
```

The legacy AgentContainment repository remains public and independently usable while AgentContain becomes the flagship platform repository.

## License

Apache-2.0.
