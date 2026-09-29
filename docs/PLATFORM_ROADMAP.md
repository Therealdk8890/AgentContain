# WarrantKit Platform Roadmap

WarrantKit is the platform surface around the AgentContainment enforcement engine.

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

## v0.1.5 — Commercial architecture foundation

The commercial work begins before hosted services exist.

### Contract

- Define the Enterprise trust boundary in [ENTERPRISE_CONTRACT.md](ENTERPRISE_CONTRACT.md).
- Define the transport-neutral Evidence API in [EVIDENCE_API.md](EVIDENCE_API.md).
- Keep enforcement, verification, and local receipts usable without a control plane.

### Implementation

1. **Evidence envelope** — create a typed platform object representing one execution's evidence.
2. **Canonical serialization** — define deterministic serialization and schema versioning.
3. **Receipt binding** — bind the envelope to the existing receipt implementation without duplicating cryptographic logic.
4. **Evidence export** — expose local evidence as a machine-readable artifact.
5. **Ingestion seam** — define an interface for future Enterprise collectors without requiring HTTP/SaaS dependencies.
6. **Fleet identity model** — establish organization/project/runtime/agent/execution identifiers as a separate governance layer.
7. **Policy distribution contract** — central policy may distribute versioned policy, but local runtime remains authoritative for validation and enforcement.

### Explicitly deferred

- Hosted dashboard
- User authentication / RBAC implementation
- Billing
- Multi-tenant database
- SaaS deployment
- Enterprise-only runtime dependencies

## v0.1.5 success criterion

A local execution can produce a complete, independently verifiable evidence envelope that an eventual Enterprise control plane can ingest without changing the meaning or authority of the underlying proof.

## Non-goals for v0.1

- Replacing Kubernetes, gVisor, Kata, containers, or cgroups.
- Claiming formal verification or universal host security.
- Treating an agent-reported event as authoritative security evidence.
- Implementing full workload rehydration during recovery.
- Introducing a control plane before the local trust boundary is well-defined.

## Success criterion

A reviewer should be able to trace one execution from admission through containment and recovery and answer what execution was admitted, under which policy, what authority and epoch it received, what enforcement was applied, which proofs actually executed, what happened during containment or recovery, what evidence and receipt correspond to the execution, and what the evidence does and does not prove.
