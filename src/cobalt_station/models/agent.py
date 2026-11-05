"""Agent models for Cobalt Station."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent lifecycle status."""
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class Agent(BaseModel):
    """Agent entity with workspace isolation."""
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(default="", description="Agent description")
    status: AgentStatus = Field(default=AgentStatus.CREATED, description="Agent status")
    workspace_path: Path = Field(..., description="Absolute path to agent's workspace")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    config: dict = Field(default_factory=dict, description="Agent configuration")


class AgentCreate(BaseModel):
    """Request model for creating an agent."""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: str = Field(default="", max_length=500, description="Agent description")
    config: dict = Field(default_factory=dict, description="Agent configuration")


class AgentUpdate(BaseModel):
    """Request model for updating an agent."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    config: Optional[dict] = None
    status: Optional[AgentStatus] = None


class AgentResponse(BaseModel):
    """Response model for agent API."""
    id: str
    name: str
    description: str
    status: AgentStatus
    workspace_path: str
    created_at: datetime
    updated_at: datetime
    config: dict

    @classmethod
    def from_agent(cls, agent: Agent) -> "AgentResponse":
        return cls(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            status=agent.status,
            workspace_path=str(agent.workspace_path),
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            config=agent.config,
        )


class AgentListResponse(BaseModel):
    """Response model for listing agents."""
    agents: list[AgentResponse]
    total: int

