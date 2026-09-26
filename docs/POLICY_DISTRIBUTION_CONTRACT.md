# AgentContain Policy Distribution Contract

**Status: v0.1 contract**

This contract defines how a future Enterprise control plane may distribute policy to AgentContain runtimes without becoming part of the runtime enforcement trust boundary.

## Authority principle

**Centralized policy management may author and distribute policy. The local runtime remains authoritative for validation and enforcement.**

A runtime MUST be able to reject malformed, unsupported, stale, or otherwise invalid policy without consulting the control plane.

## Policy lifecycle

```text
Author
  ↓
Version
  ↓
Canonicalize
  ↓
Hash
  ↓
Distribute
  ↓
Local validate
  ↓
Local admit
  ↓
Local enforce
  ↓
Bind policy identity + digest to execution evidence
```

## Policy identity

A distributed policy MUST have:

- `policy_id` — stable opaque identifier;
- `policy_version` — monotonically increasing version within its policy scope;
- `policy_digest` — digest of the canonical policy representation;
- `policy_document` — the canonical policy representation or a locally resolvable equivalent.

The execution evidence MUST retain the policy ID and digest actually used by the runtime.

## Canonicalization

Policy identity MUST be derived from a deterministic representation.

The same policy document MUST produce the same canonical representation and digest regardless of transport or ordering of semantically unordered fields.

Transport metadata, billing state, delivery timestamps, and control-plane routing information MUST NOT alter the policy digest.

## Distribution semantics

Distribution is advisory to the runtime until locally validated.

A runtime SHOULD:

1. receive a candidate policy;
2. validate schema and supported capabilities;
3. canonicalize the policy;
4. compute and compare its digest;
5. validate scope and version rules;
6. activate only an accepted policy;
7. bind the accepted identity and digest to subsequent executions.

A failed distribution MUST NOT silently replace the currently accepted policy with an invalid candidate.

## Staleness and rollback

Policy versions MUST be evaluated against local runtime state.

The runtime MUST define explicit behavior for:

- duplicate delivery;
- out-of-order delivery;
- stale versions;
- unsupported policy versions;
- digest mismatch;
- rollback authorization.

A control plane MUST NOT regain authority merely by replaying an older policy.

## Offline behavior

The runtime MUST continue enforcing its last accepted local policy while disconnected, subject to local policy expiration or fail-closed rules that are explicitly defined by the policy itself.

Network loss MUST NOT implicitly disable containment.

## Execution binding

Every admitted execution MUST retain the policy identity it actually used:

```text
execution
├── policy_id
├── policy_digest
└── epoch
```

Evidence produced later MUST preserve those values even if a newer policy has been distributed.

## Enterprise boundary

The future Enterprise control plane may provide:

- policy authoring;
- version management;
- approval workflows;
- fleet targeting;
- rollout state;
- policy history.

It MUST NOT:

- directly command a runtime to weaken containment;
- require a network callback for every enforcement decision;
- make billing or subscription state a runtime prerequisite;
- rewrite historical execution policy identity;
- bypass local policy validation.

## Acceptance criteria

1. A runtime can enforce a locally accepted policy with no control-plane connectivity.
2. Policy digests are deterministic and transport-independent.
3. Invalid or stale policies cannot silently replace accepted policy.
4. Execution evidence records the exact policy identity and digest used.
5. Control-plane outage does not disable local enforcement.
6. Historical evidence remains bound to its original policy identity.
