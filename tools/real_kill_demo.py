#!/usr/bin/env python3
"""Operator-facing real-kill WarrantKit demonstration.

Requires Linux, cgroup-v2, root, and the AgentContainment submodule installed.
This intentionally exercises the real runtime enforcement boundary rather than
the simulated demo path.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from secrets import token_bytes


def main() -> int:
    if sys.platform != "linux":
        print("REAL-KILL DEMO: requires Linux.", file=sys.stderr)
        return 2
    if os.geteuid() != 0:
        print("REAL-KILL DEMO: run as root (for example: sudo -E python tools/real_kill_demo.py).", file=sys.stderr)
        return 2
    if not os.path.exists("/sys/fs/cgroup/cgroup.controllers"):
        print("REAL-KILL DEMO: cgroup-v2 is not available.", file=sys.stderr)
        return 2

    from agent_containment.linux_supervisor import LinuxCgroupSupervisor
    from agent_containment.proof_receipt import ReceiptVerifier
    from agentcontain.engine import admit, build_agentcontainment_engine, containment_receipt, contain
    from agentcontain.policy import Policy

    supervisor = LinuxCgroupSupervisor("auto")
    agent_id = f"warrantkit-real-kill-{os.getpid()}"
    cgroup = supervisor.create_agent(agent_id)
    child = None
    secret = token_bytes(32)

    print("WarrantKit real-kill demo")
    print("=" * 27)
    print("Trust boundary: WarrantKit -> AgentContainment -> Linux cgroup-v2")
    print()

    try:
        print("[1/6] Launching real workload...")
        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(300)"],
        )
        supervisor.attach_pid(cgroup, child.pid)
        if not supervisor.pid_in_cgroup(child.pid, cgroup):
            raise RuntimeError("workload was not attached to the expected cgroup")
        print(f"      PID {child.pid} attached to {cgroup}")

        print("[2/6] Admitting execution and issuing Warrant...")
        policy = Policy("real-kill-demo", capabilities=("demo-workload",))
        engine = build_agentcontainment_engine(agent_id, cgroup_path=str(cgroup))
        admission = admit(policy, agent_id=agent_id, engine=engine)
        print(f"      execution={admission.identity.execution_id}")
        print(f"      epoch={admission.identity.epoch}")
        print("      Warrant: ACTIVE")

        print("[3/6] Invoking external containment...")
        started = time.monotonic()
        report = contain(admission)
        elapsed = time.monotonic() - started
        if not report.complete or not report.external_verified:
            raise RuntimeError(f"runtime enforcement was not verified: {report!r}")
        print("      AgentContainment: external enforcement completed")
        print(f"      enforcement latency: {getattr(report, 'enforcement_latency_seconds', None)}s")

        print("[4/6] Independently checking the real workload...")
        if supervisor.is_populated(cgroup):
            raise RuntimeError("cgroup remains populated after containment")
        child.wait(timeout=5)
        if child.returncode is None:
            raise RuntimeError("workload did not exit")
        print(f"      cgroup populated: NO")
        print(f"      workload exited: YES (returncode={child.returncode})")
        print(f"      current platform epoch: {admission.identity.epoch}")
        print("      old Warrant: REVOKED / STALE")

        print("[5/6] Creating and verifying authenticated receipt...")
        receipt = containment_receipt(admission, secret)
        if not ReceiptVerifier(secret).verify(receipt):
            raise RuntimeError("receipt verification failed")
        print("      receipt: VERIFIED")
        print("      profile: HMAC (shared-secret authentication)")

        print("[6/6] Result")
        print()
        print("      REAL KILL VERIFIED")
        print()
        print("What this proves:")
        print("  - a real workload entered a real Linux cgroup-v2 boundary")
        print("  - containment was performed by the external AgentContainment runtime")
        print("  - the cgroup was independently observed empty")
        print("  - the workload exited")
        print("  - the pre-containment authority was invalidated by the lifecycle transition")
        print("  - the resulting runtime receipt verified under its configured HMAC key")
        print()
        print("What this does NOT prove:")
        print("  - universal host or kernel security")
        print("  - non-repudiable attestation")
        print("  - policy correctness or benign agent intent")
        print("  - protection against a compromised host")
        print("  - reversal of side effects that occurred before containment")
        return 0

    except Exception as exc:
        print(f"REAL-KILL DEMO FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        if child is not None and child.poll() is None:
            child.kill()
            child.wait(timeout=5)
        if cgroup.exists():
            try:
                supervisor.remove(cgroup)
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
