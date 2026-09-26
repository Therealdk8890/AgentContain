from agentcontain.identity import ExecutionIdentity


def test_execution_identity_is_stable_and_opaque():
    identity = ExecutionIdentity(
        execution_id="exec-1",
        agent_id="agent-1",
        policy_id="policy-1",
        policy_digest="digest-1",
        epoch=7,
    )
    assert identity.execution_id == "exec-1"
    assert identity.agent_id == "agent-1"
    assert identity.policy_id == "policy-1"
    assert identity.policy_digest == "digest-1"
    assert identity.epoch == 7
