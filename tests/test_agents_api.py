"""Tests for agents API."""

import shutil
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from cobalt_station.main import create_app
from cobalt_station.services.agent_service import AgentService


@pytest.fixture
def temp_workspace():
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest_asyncio.fixture
async def client(temp_workspace):
    app = create_app()
    app.state.agent_service = AgentService(temp_workspace)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


class TestAgentsAPI:
    """Test the agents API endpoints."""

    @pytest.mark.asyncio
    async def test_create_agent(self, client):
        """Test creating a new agent."""
        response = await client.post("/api/agents", json={"name": "Test Agent", "description": "A test agent"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["description"] == "A test agent"
        assert data["status"] == "created"
        assert "id" in data
        assert "workspace_path" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_agent_minimal(self, client):
        """Test creating an agent with minimal fields."""
        response = await client.post("/api/agents", json={"name": "Minimal Agent"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Agent"
        assert data["description"] == ""
        assert data["status"] == "created"

    @pytest.mark.asyncio
    async def test_list_agents_empty(self, client):
        """Test listing agents when none exist."""
        response = await client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["agents"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_agents(self, client):
        """Test listing agents after creating some."""
        await client.post("/api/agents", json={"name": "Agent 1"})
        await client.post("/api/agents", json={"name": "Agent 2"})
        response = await client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["agents"]) == 2

    @pytest.mark.asyncio
    async def test_get_agent(self, client):
        """Test getting an agent by ID."""
        create_resp = await client.post("/api/agents", json={"name": "Get Test Agent"})
        agent_id = create_resp.json()["id"]
        response = await client.get(f"/api/agents/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == "Get Test Agent"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, client):
        """Test getting a non-existent agent returns 404."""
        response = await client.get("/api/agents/nonexistent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_agent(self, client):
        """Test updating an agent."""
        create_resp = await client.post("/api/agents", json={"name": "Original Name"})
        agent_id = create_resp.json()["id"]
        response = await client.patch(f"/api/agents/{agent_id}", json={"name": "Updated Name", "description": "Updated description"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_agent_not_found(self, client):
        """Test updating a non-existent agent returns 404."""
        response = await client.patch("/api/agents/nonexistent", json={"name": "New Name"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_agent(self, client):
        """Test deleting an agent."""
        create_resp = await client.post("/api/agents", json={"name": "To Delete"})
        agent_id = create_resp.json()["id"]
        response = await client.delete(f"/api/agents/{agent_id}")
        assert response.status_code == 204
        get_resp = await client.get(f"/api/agents/{agent_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_agent_not_found(self, client):
        """Test deleting a non-existent agent returns 404."""
        response = await client.delete("/api/agents/nonexistent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_agent_workspace_isolation(self, client):
        """Test that agents have isolated workspaces."""
        resp1 = await client.post("/api/agents", json={"name": "Agent A"})
        resp2 = await client.post("/api/agents", json={"name": "Agent B"})
        agent_a_id = resp1.json()["id"]
        agent_b_id = resp2.json()["id"]
        ws_a = resp1.json()["workspace_path"]
        ws_b = resp2.json()["workspace_path"]
        assert ws_a != ws_b
        assert agent_a_id in ws_a
        assert agent_b_id in ws_b

