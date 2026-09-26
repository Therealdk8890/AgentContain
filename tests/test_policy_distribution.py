from agentcontain.policy import Policy


def test_policy_identity_remains_available_to_execution_layer():
    policy = Policy(
        policy_id="policy-1",
        version=1,
        rules=(),
    )
    assert policy.policy_id == "policy-1"
    assert policy.version == 1


def test_policy_digest_is_deterministic_for_equivalent_policy_data():
    first = Policy(policy_id="policy-1", version=1, rules=())
    second = Policy(policy_id="policy-1", version=1, rules=())
    assert first.digest() == second.digest()
