from agentcontain.policy import Policy
from agentcontain.policy_distribution import PolicyBundle, PolicyRegistry


def test_bundle_binds_policy_identity_and_digest():
    policy = Policy(policy_id="policy-1", version=2, allowed_egress=("api.example",))
    bundle = PolicyBundle.from_policy(policy)
    assert bundle.policy_id == "policy-1"
    assert bundle.policy_version == 2
    assert bundle.policy_digest == policy.digest
    assert bundle.canonical_document == policy.canonical()


def test_registry_accepts_valid_policy_and_keeps_local_authority():
    registry = PolicyRegistry()
    bundle = registry.accept_policy(Policy(policy_id="policy-1", version=1))
    assert registry.active is bundle


def test_registry_rejects_stale_policy():
    registry = PolicyRegistry()
    registry.accept_policy(Policy(policy_id="policy-1", version=2))
    try:
        registry.accept_policy(Policy(policy_id="policy-1", version=1))
    except ValueError as exc:
        assert str(exc) == "stale policy version"
    else:
        raise AssertionError("stale policy was accepted")


def test_registry_rejects_same_version_digest_conflict():
    registry = PolicyRegistry()
    registry.accept_policy(Policy(policy_id="policy-1", version=1, capabilities=("read",)))
    try:
        registry.accept_policy(Policy(policy_id="policy-1", version=1, capabilities=("write",)))
    except ValueError as exc:
        assert str(exc) == "policy version conflicts with active digest"
    else:
        raise AssertionError("conflicting policy was accepted")
