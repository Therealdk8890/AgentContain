# Changelog

All notable changes to WarrantKit are documented here.

The project is currently pre-1.0. Entries describe shipped repository changes; they do not imply a production security guarantee.

## Unreleased

- Clarify the enforcement-engine adapter contract, including the retained containment report used to create authenticated receipts.
- Add repository and issue links to package metadata.
- Restrict setuptools package discovery to the `agentcontain*` namespace.

## 0.1.0

Initial platform release line, including:

- local policy admission and execution identity;
- runtime containment adapter for AgentContainment;
- structured execution evidence and authenticated receipt integration;
- fleet governance primitives;
- operator and evidence-inspection tooling;
- no-root simulated demonstration path;
- privileged Linux integration proof for real cgroup-v2 containment.
