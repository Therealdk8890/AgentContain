#!/usr/bin/env python3
"""Operator-facing Linux cgroup-v2 real-kill proof.

Requires the WarrantKit checkout, the AgentContainment submodule, Linux cgroup-v2,
root/delegated cgroup privileges, and the WarrantKit Python package installed.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from agentcontain.engine import admit, build_agentcontainment_engine, contain
from agentcontain.evidence import EvidenceEnvelope, canonical_json
from agentcontain.policy import Policy


def _record_binding(record: dict) -> dict:
    return {
        "digest": "sha256:" + hashlib.sha256(
            canonical_json(record).encode("utf-8")
        ).hexdigest(),
        "record": record,
    }


def main() -> int:
    if os.name != "posix" or os.geteuid() != 0:
        print("REJECTED: real-kill proof requires Linux/root privileges", file=sys.stderr)
        return 2
    if os.environ.get("AGENT_CONTAIN_RUN_REAL_CGROUP") != "1":
        print("REJECTED: set AGENT_CONTAIN_RUN_REAL_CGROUP=1", file=sys.stderr)
        return 2
    if not Path("/sys/fs/cgroup/cgroup.controllers").exists():
        print("REJECTED: cgroup-v2 is unavailable", file=sys.stderr)
        return 2

    from agent_containment.linux_supervisor import LinuxCgroupSupervisor

    supervisor = LinuxCgroupSupervisor("auto")
    agent_id = f"warrantkit-real-kill-{os.getpid()}"
    cgroup = supervisor.create_agent(agent_id)
    child = None

    try:
        print("[1/7] launching real workload")
        child = subprocess.Popen(["python3", "-c", "import time; time.sleep(300)"])
        supervisor.attach_pid(cgroup, child.pid)
        assert supervisor.pid_in_cgroup(child.pid, cgroup)
        assert supervisor.is_populated(cgroup)

        print("[2/7] admitting workload under Warrant")
        engine = build_agentcontainment_engine(agent_id, cgroup_path=str(cgroup))
        runtime_id = engine.runtime_id
        admission = admit(
            Policy("real-kill-proof", capabilities=("test-workload",)),
            agent_id=agent_id,
            engine=engine,
            runtime_id=runtime_id,
        )

        print(f"    warrant={admission.warrant.warrant_id}")
        print(f"    epoch={admission.identity.epoch}")

        print("[3/7] invoking external runtime enforcement")
        report = contain(admission)
        assert report.complete
        assert report.external_verified

        print("[4/7] independently checking terminal runtime state")
        assert not supervisor.is_populated(cgroup)
        child.wait(timeout=5)
        assert child.returncode is not None
        print(f"    workload exited with code {child.returncode}")

        print("[5/7] exporting runtime-pinned evidence")
        authority_export = getattr(admission.engine, "authority_revocation_evidence_record", None)
        if authority_export is None:
            raise RuntimeError("runtime engine does not expose authority revocation evidence")
        authority = authority_export() if callable(authority_export) else authority_export

        enforcement_export = getattr(report, "enforcement_evidence_record", None)
        if enforcement_export is None:
            raise RuntimeError("runtime report does not expose canonical enforcement evidence")
        enforcement = enforcement_export(runtime_id)

        observation_record = {
            "runtime_id": runtime_id,
            "agent_id": admission.identity.agent_id,
            "epoch": admission.identity.epoch,
            "state": "TERMINATED",
            "observed_at": time.time(),
            "can_execute": False,
        }
        binding = {
            "schema_version": "agentcontain.runtime-binding/v1",
            "runtime_id": runtime_id,
            "agent_id": admission.identity.agent_id,
            "epoch": admission.identity.epoch,
            "authority": authority,
            "enforcement": enforcement,
            "observation": _record_binding(observation_record),
        }
        envelope = EvidenceEnvelope.from_execution(
            execution={
                "execution_id": admission.identity.execution_id,
                "agent_id": admission.identity.agent_id,
                "policy_id": admission.identity.policy_id,
                "policy_digest": admission.identity.policy_digest,
                "epoch": admission.identity.epoch,
                "runtime_id": runtime_id,
            },
            events=(
                {
                    "execution_id": admission.identity.execution_id,
                    "sequence": 1,
                    "name": "containment_verified",
                    "epoch": admission.identity.epoch,
                },
            ),
            verification={"status": "observed"},
        ).with_runtime_pinned_evidence(binding)

        artifact = Path(
            os.environ.get(
                "WARRANTKIT_REAL_KILL_ARTIFACT",
                "real-kill-runtime-evidence.json",
            )
        )
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            json.dumps(envelope.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"    artifact={artifact}")

        print("[6/7] independently verifying exported artifact")
        verifier = Path(__file__).with_name("verify_runtime_evidence.py")
        result = subprocess.run(
            [sys.executable, str(verifier), str(artifact)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return 1
        print(f"    {result.stdout.strip()}")

        print("[7/7] proof complete")
        print("What this proves: the tested Linux environment enforced the configured")
        print("cgroup-v2 kill/fence boundary and produced independently checked evidence.")
        print("What this does not prove: universal host isolation, formal verification,")
        print("or non-repudiable host attestation.")
        return 0
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
