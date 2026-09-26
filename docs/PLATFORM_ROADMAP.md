# AgentContain Platform Roadmap

AgentContain is the platform surface around the AgentContainment enforcement engine.

## v0.1 — Platform contract

The first platform milestone turns the existing security-critical runtime into a coherent operator-facing system without weakening its trust model.

### Lifecycle

**Policy → Admit → Contain → Detect → Fence → Halt → Verify → Recover → Receipt**

Each transition should produce explicit state and evidence rather than relying on implicit process state.

### Platform boundaries

| Layer | Responsibility |
|---|---|
| Policy | Declare allowed execution, authority, and egress |
| Admission | Validate policy and establish an execution identity |
| AgentContainment | Enforce runtime boundaries outside the agent |
| Detection | Observe boundary violations and suspicious state |
| Response | Fence, halt, or contain the execution |
| Recovery | Restore only after external enforcement is independently released and verified |
| Proof | Bind observed execution events to structured evidence |
| Receipt | Serialize verification results for downstream systems |

## v0.1 implementation order

1. **Policy model** — versioned, deterministic policy schema.
2. **Execution identity** — stable execution ID, agent ID, and epoch.
3. **Platform state machine** — explicit lifecycle states and legal transitions.
4. **Event model** — structured events for admission, containment, fencing, halt, verification, and recovery.
5. **Proof bridge** — consume AgentContainment proof evidence without duplicating enforcement logic.
6. **Receipt bridge** — expose existing tamper-evident receipts through the platform API.
7. **Operator CLI** — make the lifecycle inspectable from a terminal.
8. **Host integration** — wire policy and platform state into the existing Linux enforcement engine.

## Non-goals for v0.1

- Replacing Kubernetes, gVisor, Kata, containers, or cgroups.
- Claiming formal verification or universal host security.
- Treating an agent-reported event as authoritative security evidence.
- Implementing full workload rehydration during recovery.
- Introducing a control plane before the local trust boundary is well-defined.

## Success criterion

A reviewer should be able to trace one execution from admission through containment and recovery and answer:

- What execution was admitted?
- Under which policy?
- What authority and epoch did it receive?
- What boundary enforcement was applied?
- What hostile actions were attempted?
- Which proofs actually executed?
- What happened during containment or recovery?
- What evidence and receipt correspond to the execution?
- What does the evidence prove, and what does it explicitly not prove?

The platform is successful when those questions can be answered from structured artifacts rather than prose or agent self-report.