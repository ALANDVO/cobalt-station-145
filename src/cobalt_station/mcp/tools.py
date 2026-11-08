"""MCP Tools for agent memory operations."""

from typing import Any
from pathlib import Path

from mcp.server import Server
from mcp import types
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

from cobalt_station.security.workspace_guard import WorkspaceGuard, WorkspaceAccessError
from cobalt_station.tools.file_tools import FileTools


class ReadMemoryParams(BaseModel):
    """Parameters for reading memory."""
    agent_id: str = Field(..., description="Agent ID to read memory from")
    path: str = Field(..., description="Relative path to the memory file")


class WriteMemoryParams(BaseModel):
    """Parameters for writing memory."""
    agent_id: str = Field(..., description="Agent ID to write memory to")
    path: str = Field(..., description="Relative path to the memory file")
    content: str = Field(..., description="Content to write")


class ListMemoryParams(BaseModel):
    """Parameters for listing memory files."""
    agent_id: str = Field(..., description="Agent ID to list memory for")
    path: str = Field(default="", description="Relative path to list (default: root)")


async def handle_list_tools(
    context: Any, params: types.PaginatedRequestParams | None
) -> types.ListToolsResult:
    """Handle list_tools request."""
    return types.ListToolsResult(
        tools=[
            Tool(
                name="read_memory",
                description="Read a memory file from an agent's workspace",
                inputSchema=ReadMemoryParams.model_json_schema(),
            ),
            Tool(
                name="write_memory",
                description="Write a memory file to an agent's workspace",
                inputSchema=WriteMemoryParams.model_json_schema(),
            ),
            Tool(
                name="list_memory",
                description="List memory files in an agent's workspace",
                inputSchema=ListMemoryParams.model_json_schema(),
            ),
        ]
    )


async def handle_call_tool(
    context: Any, params: types.CallToolRequestParams
) -> types.CallToolResult:
    """Handle call_tool request."""
    # We need access to workspace_root - this will be set on the server instance
    server = context.server
    workspace_root: Path = server.workspace_root
    
    name = params.name
    arguments = params.arguments or {}
    
    if name == "read_memory":
        try:
            params_obj = ReadMemoryParams(**arguments)
            guard = WorkspaceGuard(workspace_root, params_obj.agent_id)
            tools = FileTools(guard)
            content = await tools.read_file(params_obj.path)
            return types.CallToolResult(content=[TextContent(type="text", text=content)])
        except WorkspaceAccessError as e:
            return types.CallToolResult(content=[TextContent(type="text", text=f"Access denied: {e}")])
        except FileNotFoundError:
            return types.CallToolResult(content=[TextContent(type="text", text=f"File not found: {arguments.get('path', 'unknown')}")])
        except Exception as e:
            return types.CallToolResult(content=[TextContent(type="text", text=f"Error reading memory: {e}")])
    
    elif name == "write_memory":
        try:
            params_obj = WriteMemoryParams(**arguments)
            guard = WorkspaceGuard(workspace_root, params_obj.agent_id)
            tools = FileTools(guard)
            await tools.write_file(params_obj.path, params_obj.content)
            return types.CallToolResult(content=[TextContent(type="text", text=f"Successfully wrote to {params_obj.path}")])
        except WorkspaceAccessError as e:
            return types.CallToolResult(content=[TextContent(type="text", text=f"Access denied: {e}")])
        except Exception as e:
            return types.CallToolResult(content=[TextContent(type="text", text=f"Error writing memory: {e}")])
    
    elif name == "list_memory":
        try:
            params_obj = ListMemoryParams(**arguments)
            guard = WorkspaceGuard(workspace_root, params_obj.agent_id)
            tools = FileTools(guard)
            files = await tools.list_files(params_obj.path)
            # files are already relative paths from FileTools.list_files
            relative_files = [str(f) for f in files]
            return types.CallToolResult(content=[TextContent(type="text", text="\n".join(relative_files) if relative_files else "No files found")])
        except WorkspaceAccessError as e:
            return types.CallToolResult(content=[TextContent(type="text", text=f"Access denied: {e}")])
        except Exception as e:
            return types.CallToolResult(content=[TextContent(type="text", text=f"Error listing memory: {e}")])
    
    else:
        return types.CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])


def create_mcp_server(workspace_root: Path) -> Server:
    """Create an MCP server with memory tools for agents."""
    server = Server(
        "cobalt-station-memory",
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )
    
    # Store workspace root for tool access
    server.workspace_root = workspace_root
    
    return server
