"""Agent service for managing agents and their workspaces."""

import shutil
import uuid
from pathlib import Path

from cobalt_station.models.agent import Agent, AgentCreate, AgentStatus
from cobalt_station.security.workspace_guard import WorkspaceGuard


class AgentService:
    """Service for managing agent lifecycle and workspace provisioning."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self._agents: dict[str, Agent] = {}

    def create_agent(self, agent_create: AgentCreate) -> Agent:
        """Create a new agent with isolated workspace."""
        agent_id = str(uuid.uuid4())[:8]
        workspace_path = self.workspace_root / agent_id

        agent = Agent(
            id=agent_id,
            name=agent_create.name,
            description=agent_create.description,
            status=AgentStatus.CREATED,
            workspace_path=workspace_path,
            config=agent_create.config,
        )

        workspace_path.mkdir(parents=True, exist_ok=True)
        self._agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> Agent:
        """Get an agent by ID."""
        if agent_id not in self._agents:
            raise KeyError(f"Agent not found: {agent_id}")
        return self._agents[agent_id]

    def list_agents(self) -> list[Agent]:
        """List all agents."""
        return list(self._agents.values())

    def update_agent(self, agent_id: str, name: str | None = None, description: str | None = None, config: dict | None = None, status: AgentStatus | None = None) -> Agent:
        """Update an agent's properties."""
        agent = self.get_agent(agent_id)
        if name is not None:
            agent.name = name
        if description is not None:
            agent.description = description
        if config is not None:
            agent.config = config
        if status is not None:
            agent.status = status
        return agent

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent and its workspace."""
        agent = self.get_agent(agent_id)
        if agent.workspace_path.exists():
            shutil.rmtree(agent.workspace_path)
        del self._agents[agent_id]

    def get_workspace_guard(self, agent_id: str) -> WorkspaceGuard:
        """Get a workspace guard for an agent."""
        self.get_agent(agent_id)
        return WorkspaceGuard(self.workspace_root, agent_id)

