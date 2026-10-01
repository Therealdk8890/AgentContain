# WarrantKit Platform Contract

**Status:** v0.1 design contract

This document defines the trust boundary and evidence semantics for the WarrantKit platform.

## Trust boundary

The agent is an untrusted workload.

The platform controller and its enforcement providers operate outside the agent's authority domain. The agent must not be the source of truth for whether its own containment succeeded.

Authoritative security state comes from externally enforced operations and independently verifiable results.

## Policy semantics

A Policy is the locally accepted source of policy identity and authorization scope.

The current policy fields have deliberately bounded semantics:

- capabilities describes the authority that can be represented in a Warrant.
- allowed_egress is included in canonical policy identity and therefore affects the policy digest.
- allowed_egress is declarative until an enforcement provider explicitly consumes it. Its presence in a policy, digest, or WarrantKit evidence record does not by itself establish host-level egress enforcement.
- Runtime egress enforcement is owned by the selected enforcement provider. Provider-specific enforcement evidence must come from that provider rather than being inferred from the policy field.

Warrant issuance MUST NOT silently convert a declarative policy field into an enforcement claim. A future egress binding must define the accepted semantics, provider configuration, and independent verification path before allowed_egress becomes an enforced authority dimension.

## Execution identity

A platform execution is identified by:

- execution ID
- agent ID
- policy ID and policy digest
- current execution epoch

Epoch changes invalidate previously issued execution authority.

A stale execution must not regain authority merely because an old credential, process, or message remains available.

## Evidence semantics

WarrantKit distinguishes three concepts:

1. **Observation** — something was observed or reported.
2. **Proof evidence** — a designated test or verifier established a specific property in a tested environment.
3. **Receipt** — a structured, authenticated/tamper-evident representation of evidence.

A valid receipt does not by itself prove that an underlying host or kernel claim was true. The verifier must understand the provenance and trust assumptions of the evidence.

## Fail-closed recovery

Recovery is a transaction, not a state flip.

The platform must:

1. request recovery;
2. independently verify release of external enforcement;
3. recover runtime state;
4. record the resulting evidence.

If runtime recovery fails after external enforcement has been released, containment is re-established before the recovery operation is reported as failed.

If compensation cannot itself be verified, the platform enters a degraded state rather than claiming successful recovery.

## Required platform events

The initial event vocabulary is:

- admission_requested
- admission_verified
- containment_requested
- containment_verified
- anomaly_detected
- fence_requested
- halt_requested
- verification_completed
- recovery_requested
- external_release_verified
- runtime_recovery_complete
- runtime_recovery_failed
- recontainment_verified
- receipt_issued

Detection and verification are intentionally distinct evidence events: anomaly_detected records that a detection condition was observed, while verification_completed records completion of a verification procedure.

Events are evidence records, not authority by themselves. The implementation must define which external operation establishes each event.

## Security claims

The platform must not describe a passing test as a universal security guarantee.

Claims should identify:

- the exact property tested;
- the execution/environment in which it was tested;
- the evidence produced;
- the verifier or verification method;
- known trust limitations.

This contract deliberately preserves the distinction between **verified evidence** and **truth of the underlying system claim**.
