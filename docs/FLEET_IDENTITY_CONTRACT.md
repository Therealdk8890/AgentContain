# AgentContain Fleet Identity Model

**Status: v0.1 contract**

The fleet identity model defines the governance hierarchy used by the AgentContain platform and future Enterprise control plane.

## Authority boundary

Identity is governance metadata, not runtime authority.

The runtime remains authoritative for admission, containment, fencing, halting, verification, and local proof. A control plane may assign or distribute governance identity, but it must not be able to weaken local enforcement.

## Hierarchy

```text
Organization
    |
    +-- Project
          |
          +-- Runtime
                |
                +-- Agent
                      |
                      +-- Execution
                            |
                            +-- Evidence
```

Each child belongs to exactly one parent in the hierarchy.

## Identity semantics

| Entity | Scope | Purpose |
|---|---|---|
| Organization | Tenant boundary | Top-level governance and ownership |
| Project | Organization | Logical workload/application boundary |
| Runtime | Project | Concrete AgentContain enforcement installation |
| Agent | Runtime | Identifies an autonomous workload or agent identity |
| Execution | Agent | One admitted execution epoch |
| Evidence | Execution | Proof and operational evidence produced by that execution |

Identifiers MUST be stable within their declared scope and MUST be treated as opaque strings. The platform must not infer security authority from an identifier's name.

## Execution binding

An execution record MUST retain:

- `execution_id`
- `agent_id`
- `policy_id`
- `policy_digest`
- `epoch`

Evidence envelopes already carry this execution identity. The fleet model adds governance scope without changing the meaning of local proof.

## Runtime independence

A runtime MUST remain able to:

1. admit or reject work using locally available policy state;
2. enforce containment without Enterprise connectivity;
3. verify local evidence without a control-plane callback;
4. produce local receipts while disconnected;
5. continue fail-closed behavior during control-plane outage.

Enterprise synchronization is therefore eventual for governance and evidence, not authoritative for enforcement.

## Cross-boundary rules

- An execution MUST NOT reference an agent outside its runtime.
- An agent MUST NOT reference a runtime outside its project.
- A runtime MUST NOT reference a project outside its organization.
- Evidence MUST retain its originating execution identity.
- Reparenting is a governance operation and MUST NOT rewrite historical execution or evidence identity.
- Historical evidence MUST remain attributable to the original governance scope.

## Future Enterprise mapping

A future control plane may use these identities for:

- fleet inventory;
- policy assignment;
- evidence indexing;
- audit history;
- RBAC;
- alerts and integrations;
- organization/project administration.

Those capabilities must consume runtime evidence rather than become part of the runtime enforcement trust boundary.
