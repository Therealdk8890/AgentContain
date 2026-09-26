from agentcontain.policy import Policy


def test_policy_identity_remains_available_to_execution_layer():
    policy = Policy(policy_id="policy-1", version=1)
    assert policy.policy_id == "policy-1"
    assert policy.version == 1
    assert isinstance(policy.digest, str)
    assert len(policy.digest) == 64


def test_policy_digest_is_deterministic_for_equivalent_policy_data():
    first = Policy(policy_id="policy-1", version=1, allowed_egress=("api.example", "db.example"))
    second = Policy(policy_id="policy-1", version=1, allowed_egress=("db.example", "api.example"))
    assert first.canonical() == second.canonical()
    assert first.digest == second.digest
