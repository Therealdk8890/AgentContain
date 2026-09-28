from agentcontain import cli


def test_cli_demo_is_no_root_and_verifies_receipt(capsys) -> None:
    assert cli.main(["demo"]) == 0

    output = capsys.readouterr().out
    assert "SIMULATED (no kernel enforcement)" in output
    assert "Incident" in output
    assert "Trigger:     anomaly_detected" in output
    assert "Status:      OBSERVED" in output
    assert "Proof:       OBSERVED" in output
    assert "Evidence:    OBSERVED" in output
    assert "Verification: NOT CLAIMED (simulated)" in output
    assert "Receipt:     AUTHENTICATED" in output
    assert "Receipt ID:" in output
    assert "Verified ≠ claim is true" in output


def test_demo_lifecycle_has_distinct_detection_and_verification() -> None:
    from agentcontain.demo import SimulatedEngine
    from agentcontain.engine import admit
    from agentcontain.policy import Policy

    admission = admit(
        Policy("demo", capabilities=("simulated-containment",)),
        agent_id="demo-agent",
        engine=SimulatedEngine(),
    )
    admission.engine.contain()
    admission.machine.contain()
    admission.machine.detect({"reason": "demo_policy_violation"})
    admission.machine.fence()
    admission.machine.halt()
    admission.machine.verify()

    assert admission.machine.state.value == "verified"
    assert admission.machine.events.events[-1].name == "verification_completed"
    assert len(admission.machine.events.events) == 6
