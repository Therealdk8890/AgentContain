"""Fleet and runtime governance primitives for AgentContain.

Governance identity describes ownership and inventory scope. It never becomes
runtime enforcement authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4()}"


@dataclass(frozen=True)
class Organization:
    organization_id: str
    name: str

    @classmethod
    def create(cls, name: str) -> "Organization":
        if not name.strip():
            raise ValueError("organization name must not be empty")
        return cls(_new_id("org"), name)


@dataclass(frozen=True)
class Project:
    project_id: str
    organization_id: str
    name: str

    @classmethod
    def create(cls, organization_id: str, name: str) -> "Project":
        if not organization_id.strip():
            raise ValueError("organization_id must not be empty")
        if not name.strip():
            raise ValueError("project name must not be empty")
        return cls(_new_id("project"), organization_id, name)


@dataclass(frozen=True)
class Runtime:
    runtime_id: str
    project_id: str
    name: str

    @classmethod
    def create(cls, project_id: str, name: str) -> "Runtime":
        if not project_id.strip():
            raise ValueError("project_id must not be empty")
        if not name.strip():
            raise ValueError("runtime name must not be empty")
        return cls(_new_id("runtime"), project_id, name)


@dataclass(frozen=True)
class Agent:
    agent_id: str
    runtime_id: str
    name: str

    @classmethod
    def create(cls, runtime_id: str, name: str, *, agent_id: str | None = None) -> "Agent":
        if not runtime_id.strip():
            raise ValueError("runtime_id must not be empty")
        if not name.strip():
            raise ValueError("agent name must not be empty")
        return cls(agent_id or _new_id("agent"), runtime_id, name)


@dataclass(frozen=True)
class FleetScope:
    """Immutable governance ancestry for one runtime installation."""

    organization_id: str
    project_id: str
    runtime_id: str

    @classmethod
    def create(
        cls,
        organization: Organization,
        project: Project,
        runtime: Runtime,
    ) -> "FleetScope":
        if project.organization_id != organization.organization_id:
            raise ValueError("project does not belong to organization")
        if runtime.project_id != project.project_id:
            raise ValueError("runtime does not belong to project")
        return cls(
            organization_id=organization.organization_id,
            project_id=project.project_id,
            runtime_id=runtime.runtime_id,
        )


@dataclass
class FleetRegistry:
    """Local governance registry for fleet inventory.

    The registry validates parent/child scope but does not authorize or
    enforce executions. Runtime enforcement remains outside this registry.
    """

    organizations: dict[str, Organization]
    projects: dict[str, Project]
    runtimes: dict[str, Runtime]
    agents: dict[str, Agent]

    def __init__(self) -> None:
        self.organizations = {}
        self.projects = {}
        self.runtimes = {}
        self.agents = {}

    def register_organization(self, organization: Organization) -> Organization:
        self.organizations[organization.organization_id] = organization
        return organization

    def register_project(self, project: Project) -> Project:
        if project.organization_id not in self.organizations:
            raise ValueError("project references unknown organization")
        self.projects[project.project_id] = project
        return project

    def register_runtime(self, runtime: Runtime) -> Runtime:
        if runtime.project_id not in self.projects:
            raise ValueError("runtime references unknown project")
        self.runtimes[runtime.runtime_id] = runtime
        return runtime

    def register_agent(self, agent: Agent) -> Agent:
        if agent.runtime_id not in self.runtimes:
            raise ValueError("agent references unknown runtime")
        existing = self.agents.get(agent.agent_id)
        if existing is not None and existing.runtime_id != agent.runtime_id:
            raise ValueError("agent identity cannot move to another runtime")
        self.agents[agent.agent_id] = agent
        return agent

    def scope_for_agent(self, agent_id: str) -> FleetScope:
        agent = self.agents.get(agent_id)
        if agent is None:
            raise KeyError(agent_id)
        runtime = self.runtimes[agent.runtime_id]
        project = self.projects[runtime.project_id]
        organization = self.organizations[project.organization_id]
        return FleetScope.create(organization, project, runtime)
