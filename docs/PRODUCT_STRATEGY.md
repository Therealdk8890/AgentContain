# WarrantKit Product Strategy

## North star

**WarrantKit is a runtime security and evidence platform for autonomous AI agents.**

The product exists to answer four operational questions:

1. What is this agent allowed to do?
2. What happens when it attempts something outside that boundary?
3. Did the enforcement mechanism actually operate?
4. Can the organization prove what happened afterward?

The platform should optimize for a buyer who is responsible for deploying autonomous agents into environments where unauthorized execution creates material security, operational, regulatory, or financial risk.

## Product thesis

The platform is not another agent observability dashboard and it is not only a kill switch.

Its differentiated workflow is:

**Discover → Authorize → Enforce → Detect → Contain → Verify → Recover → Prove**

The commercial value comes from closing the loop between policy, runtime enforcement, incident response, and defensible evidence.

## Product architecture

### 1. Control plane — WarrantKit

Owns:

- agent and runtime inventory
- policy assignment and rollout
- execution identity
- fleet state
- incidents
- operator review
- recovery workflow
- evidence search and retention
- integrations
- enterprise identity and RBAC

The control plane coordinates and records decisions. It must never be able to weaken local runtime containment because of network failure, service outage, billing state, or stale control-plane state.

### 2. Enforcement plane — AgentContainment

Owns the security-critical runtime boundary:

- authorization
- execution and credential leases
- epoch fencing
- cgroup-v2 containment
- egress enforcement
- halt
- recovery
- privileged-host verification

AgentContainment remains independently reviewable and independently usable.

### 3. Evidence/proof plane

The platform consumes and composes evidence from:

- AgentContainment enforcement evidence
- Warden observation
- ClaimProofKit verification
- DProvenanceKit provenance and proof

The product must preserve the semantic distinction:

**Observed ≠ Verified ≠ Authenticated receipt**

And:

**Verified ≠ claim is true**

## Initial buyer problem

The first commercial wedge should be:

> **Safely operate autonomous agents that can take consequential actions without trusting the agent itself to enforce its own boundaries.**

The initial workflow is an agent attempting an unauthorized or dangerous action.

The desired operator outcome is:

1. identify the agent and execution
2. identify the applicable policy
3. record the attempted action
4. deny or contain the action
5. invalidate stale authority
6. independently verify enforcement
7. preserve evidence
8. route the incident for review
9. recover only under fresh authority
10. export a machine-readable receipt

## Initial personas

These are hypotheses to validate through design-partner discovery, not assumed buyer truth.

### Security engineering

Cares about:

- blast radius
- deterministic controls
- incident response
- integration with existing security infrastructure
- evidence quality

### AI/platform engineering

Cares about:

- safe autonomous execution
- framework/runtime integration
- deployment friction
- developer ergonomics
- policy-as-code

### Governance/risk

Cares about:

- traceability
- evidence
- control effectiveness
- review workflows
- retention and auditability

### CISO / security leadership

Cares about:

- organizational exposure
- deployment confidence
- operational accountability
- integration and support
- measurable reduction in agent risk

Buyer discovery must determine which persona owns the budget and which persona becomes the internal champion.

## Product surfaces

### Agent inventory

Every agent should have:

- stable identity
- owner
- organization/project/runtime scope
- runtime environment
- policy
- current lifecycle state
- containment state
- proof state
- recent incidents
- last verified execution

### Policy

A policy should express:

- permitted capabilities
- resources
- credentials
- network destinations
- execution constraints
- response behavior
- version and digest

Policy changes must remain auditable and must not silently invalidate the local enforcement contract.

### Incident

An incident should contain:

- detection
- execution identity
- policy identity
- authorization decision
- containment epoch
- enforcement evidence
- credential/authority revocation
- verification result
- recovery state
- receipt

### Evidence

Evidence should be:

- canonical
- versioned
- identity-bound
- sequence-valid
- portable
- independently verifiable
- explicit about what it does not prove

### Operator workflow

The minimum useful workflow is:

**Investigate → Contain → Verify → Review → Recover → Export**

The operator should not need to understand cgroup internals to investigate an incident.

## Commercial layers

### Open foundation

Purpose:

- technical adoption
- inspectability
- developer trust
- security research
- local deployments

Expected capabilities:

- local enforcement
- local policy
- local evidence
- CLI
- testable runtime primitives

### Team / production platform

Purpose:

- operational deployment

Expected capabilities:

- fleet management
- centralized policy distribution
- durable evidence
- incident management
- dashboards
- webhooks
- SIEM integration
- team RBAC
- deployment tooling

### Enterprise

Purpose:

- organization-scale governance

Expected capabilities:

- SSO/SAML
- SCIM
- advanced RBAC
- retention controls
- centralized audit
- enterprise integrations
- deployment support
- security architecture support
- SLA/support commitments

Exact packaging and pricing require buyer validation.

## What not to build first

Do not turn WarrantKit into:

- a generic SIEM
- a generic observability platform
- a replacement for Kubernetes
- a replacement for endpoint security
- a universal policy engine
- a giant agent framework
- a compliance certification product

Integrate with those systems instead.

## Initial proof of value

A design partner should be able to provide one consequential autonomous workflow.

The pilot should:

1. instrument the workflow
2. define the boundary
3. establish execution identity
4. exercise normal execution
5. exercise adversarial/unauthorized actions
6. contain violations
7. independently verify enforcement
8. produce receipts
9. measure operational overhead
10. evaluate recovery

The pilot should produce measurable evidence around:

- unauthorized actions blocked
- containment latency
- false positives
- recovery time
- integration effort
- operator time per incident
- evidence completeness
- deployment overhead

No ROI claims should be made until customer baselines exist.

## Product roadmap

### P0 — Commercial spine

- buyer-facing README and positioning
- agent inventory model
- incident model
- operator-facing lifecycle
- policy-to-incident linkage
- evidence timeline
- secure CLI secret handling
- reproducible installation
- design-partner demo

### P1 — Production control plane

- persistent fleet service
- centralized evidence store
- authentication
- RBAC
- policy distribution
- incident APIs
- webhooks
- SIEM/SOAR export
- operator dashboard

### P2 — Ecosystem

- Kubernetes integration
- OpenTelemetry integration
- agent framework adapters
- cloud workload integrations
- enterprise identity
- deployment automation

### P3 — Assurance moat

- stronger host attestation options
- signed attestations where supported
- independent verifier tooling
- expanded adversarial regression corpus
- formalized security contracts
- third-party security review

## Decision rule

Prioritize work that materially improves at least one of:

1. **Security assurance**
2. **Deployment**
3. **Operator workflow**
4. **Integration**
5. **Evidence quality**
6. **Buyer value**

Prefer work that improves multiple dimensions simultaneously.

Avoid feature accumulation that does not strengthen the commercial wedge.
