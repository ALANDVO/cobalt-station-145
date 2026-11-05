"""Agents API router for Cobalt Station."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from cobalt_station.models.agent import AgentCreate, AgentResponse, AgentListResponse, AgentUpdate, AgentStatus
from cobalt_station.services.agent_service import AgentService


router = APIRouter(prefix="/api/agents", tags=["agents"])


def get_agent_service(request: Request) -> AgentService:
    """Dependency to get the agent service instance from app state."""
    return request.app.state.agent_service


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_create: AgentCreate, service: AgentService = Depends(get_agent_service)) -> AgentResponse:
    """Create a new agent with isolated workspace."""
    agent = service.create_agent(agent_create)
    return AgentResponse.from_agent(agent)


@router.get("", response_model=AgentListResponse)
async def list_agents(service: AgentService = Depends(get_agent_service)) -> AgentListResponse:
    """List all agents."""
    agents = service.list_agents()
    return AgentListResponse(
        agents=[AgentResponse.from_agent(a) for a in agents],
        total=len(agents),
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, service: AgentService = Depends(get_agent_service)) -> AgentResponse:
    """Get an agent by ID."""
    try:
        agent = service.get_agent(agent_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent not found: {agent_id}")
    return AgentResponse.from_agent(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent_update: AgentUpdate, service: AgentService = Depends(get_agent_service)) -> AgentResponse:
    """Update an agent's properties."""
    try:
        agent = service.update_agent(
            agent_id,
            name=agent_update.name,
            description=agent_update.description,
            config=agent_update.config,
            status=agent_update.status,
        )
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent not found: {agent_id}")
    return AgentResponse.from_agent(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, service: AgentService = Depends(get_agent_service)) -> None:
    """Delete an agent and its workspace."""
    try:
        service.delete_agent(agent_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent not found: {agent_id}")

