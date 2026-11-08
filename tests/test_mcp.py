"""Tests for MCP server and tools."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from cobalt_station.main import create_app
from cobalt_station.services.agent_service import AgentService
from cobalt_station.mcp.tools import create_mcp_server, handle_list_tools, handle_call_tool
from cobalt_station.tools.file_tools import FileTools
from cobalt_station.security.workspace_guard import WorkspaceGuard
from mcp import types


@pytest.fixture
def temp_workspace():
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestMCPTools:
    """Test the MCP tools directly."""

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_root = self.temp_dir / "workspaces"
        self.workspace_root.mkdir()
        self.server = create_mcp_server(self.workspace_root)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that MCP server exposes the correct tools."""
        # Create mock context
        context = MagicMock()
        context.server = self.server
        
        result = await handle_list_tools(context, None)
        tool_names = {t.name for t in result.tools}
        assert tool_names == {"read_memory", "write_memory", "list_memory"}

    @pytest.mark.asyncio
    async def test_write_and_read_memory(self):
        """Test writing and reading memory through MCP tools."""
        # Create an agent workspace first
        guard = WorkspaceGuard(self.workspace_root, "test-agent")
        guard.ensure_workspace_exists()
        tools = FileTools(guard)
        await tools.write_file("memory.txt", "test content")

        # Create mock context
        context = MagicMock()
        context.server = self.server
        
        # Test read_memory tool
        params = types.CallToolRequestParams(name="read_memory", arguments={
            "agent_id": "test-agent",
            "path": "memory.txt"
        })
        result = await handle_call_tool(context, params)
        assert len(result.content) == 1
        assert result.content[0].text == "test content"

        # Test write_memory tool
        params = types.CallToolRequestParams(name="write_memory", arguments={
            "agent_id": "test-agent",
            "path": "new_memory.txt",
            "content": "new content"
        })
        result = await handle_call_tool(context, params)
        assert len(result.content) == 1
        assert "Successfully wrote" in result.content[0].text

        # Verify the file was written
        params = types.CallToolRequestParams(name="read_memory", arguments={
            "agent_id": "test-agent",
            "path": "new_memory.txt"
        })
        result = await handle_call_tool(context, params)
        assert result.content[0].text == "new content"

    @pytest.mark.asyncio
    async def test_list_memory(self):
        """Test listing memory files through MCP tools."""
        guard = WorkspaceGuard(self.workspace_root, "test-agent-2")
        guard.ensure_workspace_exists()
        tools = FileTools(guard)
        await tools.write_file("file1.txt", "content1")
        await tools.write_file("file2.txt", "content2")
        await tools.make_directory("subdir")
        await tools.write_file("subdir/file3.txt", "content3")

        context = MagicMock()
        context.server = self.server
        
        params = types.CallToolRequestParams(name="list_memory", arguments={
            "agent_id": "test-agent-2",
            "path": ""
        })
        result = await handle_call_tool(context, params)
        assert len(result.content) == 1
        files = result.content[0].text.split("\n")
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "subdir/file3.txt" in files

    @pytest.mark.asyncio
    async def test_memory_isolation(self):
        """Test that agents cannot access each other's memory via MCP."""
        guard_a = WorkspaceGuard(self.workspace_root, "agent-a")
        guard_a.ensure_workspace_exists()
        tools_a = FileTools(guard_a)
        await tools_a.write_file("secret.txt", "agent-a-secret")

        guard_b = WorkspaceGuard(self.workspace_root, "agent-b")
        guard_b.ensure_workspace_exists()

        context = MagicMock()
        context.server = self.server
        
        # Agent B trying to read Agent A's memory should fail
        params = types.CallToolRequestParams(name="read_memory", arguments={
            "agent_id": "agent-b",
            "path": "../agent-a/secret.txt"
        })
        result = await handle_call_tool(context, params)
        assert len(result.content) == 1
        assert "Access denied" in result.content[0].text

        # Agent B trying to write to Agent A's workspace should fail
        params = types.CallToolRequestParams(name="write_memory", arguments={
            "agent_id": "agent-b",
            "path": "../agent-a/hacked.txt",
            "content": "hacked"
        })
        result = await handle_call_tool(context, params)
        assert len(result.content) == 1
        assert "Access denied" in result.content[0].text

    @pytest.mark.asyncio
    async def test_nonexistent_agent(self):
        """Test accessing memory for non-existent agent."""
        context = MagicMock()
        context.server = self.server
        
        params = types.CallToolRequestParams(name="read_memory", arguments={
            "agent_id": "nonexistent",
            "path": "file.txt"
        })
        result = await handle_call_tool(context, params)
        assert len(result.content) == 1
        # Should get an error (file not found or access denied)
        assert "not found" in result.content[0].text.lower() or "access denied" in result.content[0].text.lower()


class TestMCPAPI:
    """Test the MCP HTTP endpoints."""

    @pytest_asyncio.fixture
    async def client(self, temp_workspace):
        app = create_app()
        app.state.agent_service = AgentService(temp_workspace)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_mcp_endpoint_exists(self, client):
        """Test that MCP endpoint exists."""
        # The streamable HTTP endpoint should exist
        response = await client.post("/mcp", json={"jsonrpc": "2.0", "method": "initialize", "id": 1})
        # Should not be 404 (might be 400 for invalid request, but not 404)
        assert response.status_code != 404
