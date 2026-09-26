"""Real workload-to-cgroup containment proof.

This test is intentionally Linux/root/delegation gated. It launches a real
child process, attaches that process to a real cgroup-v2 boundary, invokes the
pinned AgentContainment provider, and independently verifies the boundary is
empty afterward.
"""
from __future__ import annotations

import os
import subprocess
import time

import pytest

from agentcontain.engine import admit, build_agentcontainment_engine, containment_receipt, contain
from agentcontain.policy import Policy


pytestmark = pytest.mark.integration


def _enabled() -> bool:
    return (
        os.name == "posix"
        and os.environ.get("AGENT_CONTAIN_RUN_REAL_CGROUP") == "1"
        and os.geteuid() == 0
        and os.path.exists("/sys/fs/cgroup/cgroup.controllers")
    )


@pytest.mark.skipif(not _enabled(), reason="requires Linux cgroup-v2, root, and AGENT_CONTAIN_RUN_REAL_CGROUP=1")
def test_real_workload_is_contained_and_receipt_is_verifiable():
    from agent_containment.cgroup_enforcer import CgroupV2Enforcer
    from agent_containment.linux_supervisor import LinuxCgroupSupervisor
    from agent_containment.proof_receipt import ReceiptVerifier

    supervisor = LinuxCgroupSupervisor("auto")
    agent_id = f"agentcontain-proof-{os.getpid()}"
    cgroup = supervisor.create_agent(agent_id)
    child = None
    secret = b"agentcontain-real-integration-secret"

    try:
        child = subprocess.Popen(
            ["python3", "-c", "import time; time.sleep(300)"],
        )
        supervisor.attach_pid(cgroup, child.pid)

        assert supervisor.pid_in_cgroup(child.pid, cgroup)
        assert supervisor.is_populated(cgroup)

        engine = build_agentcontainment_engine(agent_id, cgroup_path=str(cgroup))
        admission = admit(
            Policy("integration", capabilities=("test-workload",)),
            agent_id=agent_id,
            engine=engine,
        )

        started = time.monotonic()
        report = contain(admission)
        elapsed = time.monotonic() - started

        assert report.complete
        assert report.external_verified
        assert report.enforcement_latency_seconds is not None
        assert report.enforcement_latency_seconds <= elapsed + 0.05
        assert not supervisor.is_populated(cgroup)

        child.wait(timeout=5)
        assert child.returncode is not None

        receipt = containment_receipt(admission, secret)
        assert ReceiptVerifier(secret).verify(receipt)
        assert receipt.payload["execution_id"] == admission.identity.execution_id
        assert receipt.payload["policy_id"] == admission.identity.policy_id
        assert receipt.payload["proof_status"] == "verified"

    finally:
        if child is not None and child.poll() is None:
            child.kill()
            child.wait(timeout=5)
        if cgroup.exists():
            try:
                supervisor.remove(cgroup)
            except OSError:
                pass
