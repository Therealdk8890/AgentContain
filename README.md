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
