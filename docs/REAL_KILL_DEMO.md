# Real-Kill Demo

The real-kill demo exercises WarrantKit against a real Linux cgroup-v2 workload rather than the simulated proof path.

## Requirements

- Linux
- cgroup-v2
- root or equivalent cgroup delegation
- AgentContainment submodule initialized
- Python environment with WarrantKit and AgentContainment installed

## Run

From the repository root:

    git submodule update --init --recursive
    python -m pip install -e ./AgentContainment
    python -m pip install -e .
    sudo -E python tools/real_kill_demo.py

The demo launches a real child process, attaches it to a dedicated cgroup-v2 boundary, admits it through WarrantKit, invokes the external AgentContainment enforcement boundary, independently verifies the cgroup is empty and the workload exited, and verifies the resulting receipt.

## Expected result

The important output is:

    REAL KILL VERIFIED

The demo also prints the current limitations directly so that the demonstration does not imply universal host security or non-repudiable attestation.

## Trust boundary

The demo deliberately keeps the responsibilities separate:

- WarrantKit issues authority and coordinates the lifecycle.
- AgentContainment performs the security-critical runtime enforcement.
- Linux cgroup-v2 provides the actual process containment boundary.
- The independent checks verify that the workload exited and the cgroup is no longer populated.
- The receipt authenticates the resulting evidence using the currently supported HMAC profile.

The HMAC receipt is intentionally labeled as shared-secret authentication. It is not non-repudiable attestation. The asymmetric attestation upgrade is tracked separately.

## Scope

A successful run is evidence for the tested Linux environment and configuration. It is not a universal security guarantee and does not establish host compromise resistance, policy correctness, agent intent correctness, or reversal of side effects.
