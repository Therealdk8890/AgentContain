"""No-privilege demonstration of AgentContain lifecycle and proof semantics."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

from .engine import admit, evidence_envelope
from .evidence import EvidenceEnvelope, canonical_json
from .operator import OperatorIncidentView
from .policy import Policy

_DEMO_KEY = b"agentcontain-demo-key-v1"


@dataclass(frozen=True)
class DemoReport:
    complete: bool = True


class SimulatedEngine:
    """Demo-only engine. It does not enforce a kernel boundary."""

    def contain(self) -> DemoReport:
        return DemoReport()


def _issue_receipt(evidence: EvidenceEnvelope) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "receipt_id": "demo-" + evidence.execution["execution_id"],
        "execution_id": evidence.execution["execution_id"],
        "agent_id": evidence.execution["agent_id"],
        "epoch": evidence.execution["epoch"],
        "containment": {
            "requested": True,
            "enforced": True,
            "independently_verified": False,
            "mode": "simulated",
        },
        "proof_status": "observed",
    }
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    signature = hmac.new(_DEMO_KEY, digest.encode("ascii"), hashlib.sha256).hexdigest()
    return {"payload": payload, "digest": digest, "signature": signature}


def _verify_receipt(receipt: dict[str, Any], evidence: EvidenceEnvelope) -> bool:
    payload = receipt["payload"]
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    signature = hmac.new(_DEMO_KEY, digest.encode("ascii"), hashlib.sha256).hexdigest()
    return (
        hmac.compare_digest(digest, receipt["digest"])
        and hmac.compare_digest(signature, receipt["signature"])
        and payload["execution_id"] == evidence.execution["execution_id"]
        and payload["agent_id"] == evidence.execution["agent_id"]
        and payload["epoch"] == evidence.execution["epoch"]
    )


def run_demo() -> int:
    admission = admit(
        Policy("demo", capabilities=("simulated-containment",)),
        agent_id="demo-agent",
        engine=SimulatedEngine(),
    )
    if not admission.engine.contain().complete:
        raise RuntimeError("simulated containment failed")

    admission.machine.contain()
    admission.machine.detect({"reason": "demo_policy_violation"})
    admission.machine.fence()
    admission.machine.halt()
    admission.machine.verify()

    base = evidence_envelope(admission)
    evidence = EvidenceEnvelope.from_execution(
        execution=base.execution,
        events=base.events,
        enforcement={"complete": True, "mode": "simulated", "external_enforcement": False},
        verification={"status": "observed", "method": "agentcontain-no-root-demo"},
        proof={"simulated": True, "host_enforcement_verified": False},
        provenance={"producer": "agentcontain-demo"},
    )
    receipt = _issue_receipt(evidence)
    evidence = evidence.with_receipt(receipt)
    evidence.validate()

    if not _verify_receipt(receipt, evidence):
        raise RuntimeError("demo receipt verification failed")

    view = OperatorIncidentView.from_evidence(evidence)
    incident = view.incident

    print("AgentContain — reference incident experience")
    print("--------------------------------------------")
    print(f"Execution:     {admission.identity.execution_id}")
    print(f"Agent:         {view.agent['agent_id']}")
    print(f"Policy:        {view.policy['policy_id']}")
    print(f"Policy digest: {view.policy['policy_digest']}")
    print("Mode:          SIMULATED (no kernel enforcement)")
    print()
    print("Incident")
    print(f"  Trigger:     {incident.trigger or 'none'}")
    print(f"  Status:      {incident.status.value.upper()}")
    print(f"  Proof:       {incident.proof_status.upper()}")
    print()
    print("Lifecycle / evidence")
    for event in view.timeline:
        print(f"  {event.sequence}. {event.name}")
    print()
    print("Proof")
    print("  Evidence:    OBSERVED")
    print("  Verification: NOT CLAIMED (simulated)")
    print("  Receipt:     AUTHENTICATED")
    print(f"  Receipt ID:  {view.receipt_id}")
    print()
    print("Verified ≠ claim is true")
    print("This reference experience demonstrates the platform procedure,")
    print("operator projection, and receipt integrity.")
    print("It does not prove real host or kernel containment.")
    return 0
