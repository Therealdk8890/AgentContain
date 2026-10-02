# Open-Core Boundary

## Purpose

WarrantKit is an open security foundation for bounded authority, externally enforced agent execution, and verifiable evidence.

This document defines the intended boundary between the open-source WarrantKit core and future commercial offerings. It is a product and repository boundary, not a change to the WarrantKit security architecture.

The guiding principle is:

> **Open source the security primitives and stable interoperability contracts. Commercialize the operational scale and organizational workflows built on top of them.**

The open-source core must remain independently useful, inspectable, integrable, and verifiable without a commercial WarrantKit service.

## Boundary principles

1. **Security primitives remain open.** The mechanisms that establish Warrant authority, lifecycle, identity, epoch semantics, verification, evidence contracts, and enforcement-provider boundaries belong in the open foundation.
2. **Public contracts remain implementable.** External projects should be able to issue, consume, or verify WarrantKit-compatible artifacts without adopting a commercial product.
3. **Commercial functionality must not be required to validate core security claims.** A user must be able to inspect and verify core behavior using open-source tooling.
4. **Commercial value comes from operation at organizational scale.** Fleet management, centralized governance, advanced evidence operations, compliance workflows, enterprise integrations, and support are natural commercial surfaces.
5. **Do not cripple the OSS core to create artificial upsell pressure.** The commercial layer should solve additional operational problems rather than withholding the underlying security primitive.
6. **No architecture fork.** Commercialization should consume the existing WarrantKit contracts and provider interfaces rather than creating a separate security architecture.
7. **Evidence never becomes authority.** Commercial evidence operations may correlate, reconcile, report, and export evidence, but they must not change the core authority semantics.

## Open-source foundation

The following capabilities are intended to remain part of the open WarrantKit foundation:

### Authority

- Warrant schema and canonical representation
- Warrant issuance from accepted policy
- Policy identity and policy-digest binding
- Execution identity binding
- Runtime identity and epoch binding
- Warrant lifecycle and explicit revocation
- Recovery requiring fresh authority
- Fail-closed verification semantics

### Runtime boundary

- Enforcement-provider interface
- Integration with open runtime enforcement providers
- External enforcement semantics
- Epoch fencing semantics
- Provider-neutral lifecycle contracts
- Runtime identity correlation

### Evidence

- Evidence contract and evidence-reference model
- Portable receipt representation
- Signed Warrants and receipts
- Portable verification tooling
- Evidence status semantics
- Explicit conflict visibility
- Evidence freshness/staleness semantics
- Trust-boundary documentation
- Interoperability contracts for external evidence systems

### Developer and security tooling

- Core CLI workflows
- Local/demo workflows
- Privileged Linux reference path
- Security and threat-model documentation
- Adversarial and regression tests that protect the open security contracts
- Public examples and integration documentation

The exact implementation may evolve, but these capabilities should remain available for inspection and independent use.

## Commercial surface

Commercial WarrantKit may provide functionality that operates the open foundation at organizational scale.

### Fleet and policy operations

- Organization-wide agent inventory
- Fleet policy assignment and rollout management
- Policy approval workflows
- Policy governance and change controls
- Centralized reconciliation and fleet status history
- Organizational authority delegation
- Enterprise recovery workflows

### Evidence operations

- Centralized evidence operations
- Advanced cross-system evidence correlation and reconciliation
- Incident timelines and investigation workflows
- Evidence search and retention management
- Compliance-oriented evidence packages
- Audit exports and reporting
- Organizational evidence analytics
- Workflow automation around evidence conflicts and verification failures

The underlying evidence contract and verification semantics remain open; the commercial value is in operating them across organizations and workflows.

### Enterprise integration

- Enterprise identity and RBAC
- SIEM/SOC integrations
- Ticketing and incident-response integrations
- Compliance and governance integrations
- Enterprise deployment integrations
- Centralized administrative APIs

Provider interfaces may remain open even when a maintained commercial integration is proprietary.

### Control plane and service

- Centralized commercial control plane
- Managed deployment and fleet administration
- Hosted/managed WarrantKit services
- Multi-organization tenancy
- Enterprise operational controls
- Usage and organizational analytics

### Support and assurance

- Commercial support
- Enterprise SLAs
- Deployment assistance
- Security review assistance
- Architecture/design-partner support
- Enterprise onboarding and operational guidance

## Stable public contracts

The following interfaces are strategically important ecosystem surfaces and should be treated as public contracts:

1. **Warrant schema** — external systems should be able to understand and validate Warrant authority.
2. **Evidence contract** — independent evidence producers should be able to provide evidence references without adopting the entire WarrantKit platform.
3. **Enforcement-provider contract** — runtime-specific enforcement should remain separable from WarrantKit authority semantics.
4. **Portable verification** — core artifacts should be independently verifiable without a hosted commercial service.

These contracts create ecosystem value and should not be designed as proprietary gates to the commercial product.

## What should not move into the open core merely because it is useful

A capability should not be added to the OSS core solely because it is technically convenient if its primary purpose is organizational operation rather than security enforcement.

Examples include:

- centralized fleet databases
- enterprise administration consoles
- organization-wide RBAC
- advanced compliance automation
- proprietary incident-management workflows
- proprietary analytics
- hosted service infrastructure
- enterprise support systems

This is not a prohibition against small open interfaces for these capabilities. Where interoperability benefits the ecosystem, WarrantKit should expose a clean interface while retaining the higher-level implementation as a commercial surface.

## Decision test for future features

Before adding a feature to WarrantKit, ask:

### 1. Is this a security primitive?

If it establishes or verifies bounded authority, execution identity, enforcement, epoch safety, or evidence integrity, it belongs in the open foundation unless there is a compelling architectural reason otherwise.

### 2. Is this an interoperability contract?

If other systems need it to issue, consume, enforce, or verify WarrantKit-compatible artifacts, prefer an open contract.

### 3. Is this organizational scale?

If its primary purpose is managing many agents, teams, policies, environments, incidents, or evidence streams, it is a candidate for the commercial layer.

### 4. Is this enterprise workflow?

If it primarily serves approvals, governance, compliance, administration, reporting, support, or enterprise integration, it is a candidate for the commercial layer.

### 5. Would making it commercial undermine independent verification?

If yes, keep the relevant primitive and verification capability open and commercialize the surrounding operational workflow instead.

## Non-goals of the commercial boundary

This boundary does not imply that WarrantKit must immediately build:

- a hosted SaaS product
- a web UI
- multi-tenancy
- enterprise RBAC
- a Kubernetes control plane
- a proprietary evidence format
- a proprietary enforcement runtime

Those are future product decisions. The boundary exists so that, if they are built, they have a clear home without requiring changes to the core security architecture.

## Intended relationship

The desired relationship is:

```
                 Commercial WarrantKit
        ┌──────────────────────────────────┐
        │ Fleet & policy operations        │
        │ Evidence operations              │
        │ Enterprise integrations          │
        │ Compliance & reporting           │
        │ Control plane / hosted service   │
        │ Support & SLAs                   │
        └────────────────┬─────────────────┘
                         │
                Stable public contracts
                         │
        ┌────────────────▼─────────────────┐
        │          WarrantKit Core         │
        │                                  │
        │ Warrant authority                │
        │ Lifecycle + epoch semantics      │
        │ Verification                     │
        │ Evidence contracts               │
        │ Receipt primitives               │
        │ Enforcement-provider interface   │
        └────────────────┬─────────────────┘
                         │
                    Provider API
                         │
                  Runtime providers
```

The commercial layer should therefore be **additive rather than substitutive**: it should make WarrantKit easier to operate, govern, integrate, and scale without making the open security foundation artificially incomplete.

## Status

This document describes the intended product boundary. It is not a commitment to build every listed commercial capability, pricing model, hosted service, or enterprise feature.

The boundary should be revisited as external users, design partners, and deployment evidence reveal where the highest real-world value lies.
