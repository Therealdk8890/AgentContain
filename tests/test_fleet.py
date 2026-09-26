import pytest

from agentcontain.fleet import (
    Agent,
    FleetRegistry,
    FleetScope,
    Organization,
    Project,
    Runtime,
)


def test_registers_hierarchical_fleet_scope():
    registry = FleetRegistry()
    organization = registry.register_organization(Organization.create("acme"))
    project = registry.register_project(Project.create(organization.organization_id, "payments"))
    runtime = registry.register_runtime(Runtime.create(project.project_id, "prod"))
    agent = registry.register_agent(Agent.create(runtime.runtime_id, "checkout"))

    assert registry.scope_for_agent(agent.agent_id) == FleetScope(
        organization.organization_id,
        project.project_id,
        runtime.runtime_id,
    )


def test_rejects_unknown_parent_boundaries():
    registry = FleetRegistry()
    with pytest.raises(ValueError):
        registry.register_project(Project.create("missing-org", "project"))
    with pytest.raises(ValueError):
        registry.register_runtime(Runtime.create("missing-project", "runtime"))
    with pytest.raises(ValueError):
        registry.register_agent(Agent.create("missing-runtime", "agent"))


def test_agent_identity_cannot_move_between_runtimes():
    registry = FleetRegistry()
    organization = registry.register_organization(Organization.create("acme"))
    project = registry.register_project(Project.create(organization.organization_id, "project"))
    first = registry.register_runtime(Runtime.create(project.project_id, "one"))
    second = registry.register_runtime(Runtime.create(project.project_id, "two"))

    agent = registry.register_agent(Agent.create(first.runtime_id, "worker", agent_id="agent-fixed"))

    with pytest.raises(ValueError):
        registry.register_agent(Agent.create(second.runtime_id, "worker", agent_id=agent.agent_id))
