from agentcontain.egress_binding import (
    DESTINATION_ALLOWLIST_CAPABILITY,
    EgressBinding,
    UnsupportedEgressBinding,
    bind_allowed_egress,
)


class UnsupportedProvider:
    capabilities = frozenset({"egress.deny_all_containment.v1"})


class CapableProvider:
    capabilities = frozenset({DESTINATION_ALLOWLIST_CAPABILITY})

    def __init__(self):
        self.calls = []

    def bind_egress(self, **kwargs):
        self.calls.append(kwargs)
        return {"verified": True, "provider": "test"}


def test_non_empty_egress_fails_closed_without_explicit_capability():
    try:
        bind_allowed_egress(
            UnsupportedProvider(),
            policy_id="p1",
            policy_digest="sha256:p",
            agent_id="a1",
            runtime_id="r1",
            epoch=3,
            allowed_egress=("api.example.com:443",),
        )
    except UnsupportedEgressBinding as exc:
        assert DESTINATION_ALLOWLIST_CAPABILITY in str(exc)
    else:
        raise AssertionError("unsupported provider was accepted")


def test_empty_egress_requires_no_provider_binding():
    assert bind_allowed_egress(
        UnsupportedProvider(),
        policy_id="p1",
        policy_digest="sha256:p",
        agent_id="a1",
        runtime_id="r1",
        epoch=3,
        allowed_egress=(),
    ) is None


def test_capable_provider_receives_full_runtime_binding():
    provider = CapableProvider()
    binding = bind_allowed_egress(
        provider,
        policy_id="p1",
        policy_digest="sha256:p",
        agent_id="a1",
        runtime_id="r1",
        epoch=3,
        allowed_egress=("api.example.com:443",),
    )

    assert isinstance(binding, EgressBinding)
    assert binding.policy_id == "p1"
    assert binding.policy_digest == "sha256:p"
    assert binding.agent_id == "a1"
    assert binding.runtime_id == "r1"
    assert binding.epoch == 3
    assert binding.allowed_egress == ("api.example.com:443",)
    assert provider.calls == [{
        "policy_id": "p1",
        "policy_digest": "sha256:p",
        "agent_id": "a1",
        "runtime_id": "r1",
        "epoch": 3,
        "allowed_egress": ("api.example.com:443",),
    }]
    assert binding.provider_evidence == {"verified": True, "provider": "test"}


class CapabilityWithoutBinder:
    capabilities = frozenset({DESTINATION_ALLOWLIST_CAPABILITY})


def test_capability_without_binding_operation_fails_closed():
    try:
        bind_allowed_egress(
            CapabilityWithoutBinder(),
            policy_id="p1",
            policy_digest="sha256:p",
            agent_id="a1",
            runtime_id="r1",
            epoch=3,
            allowed_egress=("api.example.com:443",),
        )
    except UnsupportedEgressBinding as exc:
        assert "bind_egress" in str(exc)
    else:
        raise AssertionError("provider without binder was accepted")
