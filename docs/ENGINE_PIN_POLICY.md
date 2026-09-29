# AgentContainment engine pin policy

WarrantKit consumes AgentContainment as a Git submodule so the security-critical enforcement implementation remains independently reviewable and version-pinned.

## Pinning rule

Every WarrantKit release or security-significant platform change records the exact AgentContainment commit contained by that revision.

For normal development, review the engine pin at least once per week and whenever AgentContainment publishes a security-relevant release or hardening change.

A pin bump must:

1. identify the previous and new engine commits;
2. review the engine changes between those commits for adapter compatibility and security impact;
3. run WarrantKit's full unit suite;
4. run the privileged integration proof when the environment permits it;
5. record the new pin in the resulting release notes or changelog.

The platform must not silently track the engine's moving main branch. The Gitlink is the supply-chain boundary: reproducibility takes precedence over automatic freshness.

## Current pin

- AgentContainment: 1948360faa92a943308a344e2728f2e9bd1842b7
- Previous pin: 7e8ad69e1d8ffcbf9cb7aa4787f1dd713c759201
- Review range: 22 commits
- Reason for this update: incorporate the latest engine hardening, including containment-race, eBPF, hermetic-sandbox, and interleave security regressions and proofs reviewed in the 22-commit range.
