# WarrantKit Egress Policy Binding Contract

**Status:** v0.1 design contract

This document defines the boundary for turning the declarative `Policy.allowed_egress` field into provider-owned runtime enforcement. It does not itself configure or claim enforcement.

## 1. Accepted policy semantics

For the current contract, each `allowed_egress` entry is a destination authority expressed as:

`host:port`

where:

- `host` is a DNS hostname or IP address;
- `port` is a decimal TCP/UDP port in the range 1-65535;
- protocol is not currently encoded by the policy field.

Entries are policy inputs, not resolved network state. A provider MUST define how DNS resolution, address-family selection, and protocol handling are enforced before claiming that a destination is constrained.

WarrantKit MUST reject or leave unbound any entry that the selected provider cannot represent without widening the policy.

## 2. Binding boundary

The binding operation consumes:

- the locally accepted policy;
- its canonical policy digest;
- the execution identity;
- runtime ID;
- current execution epoch;
- the provider identity/configuration.

The binding MUST NOT accept egress authority from an external authorization decision independently of the accepted local policy.

The effective rule is:

> External authorization may narrow local authority; provider binding may enforce only the locally accepted egress policy.

A provider MUST NOT silently add destinations, ports, or broader address ranges.

## 3. Provider ownership

The provider owns:

- translation of policy destinations into its enforcement configuration;
- installation and removal of the runtime rule;
- provider-specific enforcement state;
- provider-specific evidence that the rule was installed and verified.

WarrantKit owns:

- policy identity and digest;
- execution identity;
- runtime/epoch binding;
- lifecycle sequencing;
- admission and recovery authority;
- composition of provider evidence into platform evidence.

WarrantKit MUST NOT manufacture provider enforcement evidence from the presence of `allowed_egress`.

## 4. Lifecycle binding

An egress binding is valid only for the runtime identity and epoch for which it was installed.

At containment:

1. the runtime provider fence becomes authoritative;
2. the active egress binding is no longer treated as execution authority;
3. provider evidence is retained against the containment epoch.

At recovery:

1. the previous epoch is stale;
2. a provider MUST NOT implicitly carry an old binding into the new epoch;
3. a new binding must be installed and independently verified before execution authority is reissued when the policy requires egress enforcement.

Revocation and epoch advancement therefore invalidate the prior binding even if provider state appears unchanged.

## 5. Verification contract

A provider evidence record must identify at minimum:

- provider identity/version;
- policy ID and policy digest;
- runtime ID;
- execution epoch;
- effective provider configuration digest;
- installation/verification timestamp;
- the provider's verification method and result.

The evidence must be independently checkable according to the provider's documented trust model.

A policy digest alone proves policy identity, not enforcement.

## 6. Fail-closed behavior

If a required egress policy entry cannot be represented, installed, or independently verified:

- admission/binding MUST fail closed when the policy declares egress enforcement mandatory;
- the platform MUST NOT issue an enforcement claim;
- recovery MUST NOT silently restore execution under an unverified egress binding.

A provider may support a policy with an explicit mode that makes egress non-required, but that mode must be part of the accepted policy semantics rather than an implicit fallback.

## 7. Deliberately deferred semantics

The following are not yet part of this contract:

- wildcard hosts;
- CIDR ranges;
- URL paths;
- proxy-specific semantics;
- DNS-name-to-IP pinning rules;
- application-layer protocol inspection;
- dynamic service discovery;
- provider-specific configuration formats.

These require explicit semantics and verification rules before they can become portable WarrantKit policy authority.

## Security invariant

> `allowed_egress` becomes enforceable only through an explicit provider binding that is scoped to the accepted policy digest, execution identity, runtime, and epoch, and whose enforcement is independently verifiable.
