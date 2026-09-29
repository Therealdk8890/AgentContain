# Security Policy

## Security boundary

WarrantKit is a runtime security and evidence platform for autonomous AI agents. Its security model deliberately separates policy/control, observation, provenance, claim/evidence verification, and runtime enforcement.

The core evidence architecture uses independently derived evidence from:

- **Warden** — observation at its defined boundary.
- **DProvenanceKit** — execution/reasoning provenance and integrity evidence.
- **ClaimProofKit** — verification of supplied claim/evidence pairs under its defined verifier.
- **AgentContainment** — runtime enforcement and host/provider verification evidence.

WarrantKit correlates these facts by execution identity, policy identity, epoch, and evidence integrity. It does not treat one subsystem as a universal authority over the facts. Agreement is corroboration; disagreement must remain distinguishable as an evidence conflict.

The agent is never trusted to enforce its own security boundary.

## What the project does not claim

A passing test, verified evidence envelope, or authenticated receipt is not by itself:

- a universal security guarantee;
- formal verification of the implementation or host;
- proof that an arbitrary external claim is true;
- non-repudiable host attestation.

Current receipts use HMAC authentication. This provides integrity and shared-secret authentication within the configured trust domain; it is not a non-repudiable attestation mechanism.

Privileged Linux integration tests exercise the tested kernel, cgroup, network, and privilege environment. Results from those tests should be interpreted within that environment.

## Runtime enforcement

The security-critical runtime enforcement engine is **AgentContainment**, pinned as a Git submodule. WarrantKit's platform state and evidence layers do not replace that runtime enforcement boundary.

External evidence integrations must not be used to:

- authorize execution;
- weaken policy;
- release containment;
- extend an authority epoch;
- restore credentials;
- mark unverified runtime enforcement as verified.

Evidence integrations may add context or independently verifiable references.

## Supported environments

Host-level containment proof currently depends on Linux, cgroup v2, and the privileges/delegation required by the selected enforcement provider. Provider-specific behavior can depend on the host kernel, cgroup configuration, network stack, and deployment environment.

The no-root demonstration is intentionally simulated and must not be interpreted as kernel-level containment proof.

## Reporting a vulnerability

Please report suspected security vulnerabilities privately to the project maintainers rather than opening a public issue with exploit details.

Include, where practical:

- affected commit, release, or component;
- a concise description of the security impact;
- reproduction steps or a minimal proof of concept;
- relevant logs or test output;
- any suggested mitigation.

Please avoid including credentials, private keys, personal data, or unrelated sensitive information in the report.

We will acknowledge reports as promptly as practical, investigate the reported behavior, and coordinate disclosure based on severity and affected users.

## Scope

Security reports are especially relevant to:

- runtime containment and fencing;
- epoch and stale-authority invalidation;
- recovery and fail-closed behavior;
- evidence integrity and identity binding;
- authorization/admission boundaries;
- privileged host enforcement integrations;
- cross-component evidence handling that could incorrectly turn evidence into runtime authority.

Issues that affect only documentation, test flakiness, or unsupported environments may be handled through the normal issue tracker unless they expose a security consequence.
