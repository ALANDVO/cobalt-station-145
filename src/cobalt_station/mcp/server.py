"""MCP Server integration for Cobalt Station."""

from pathlib import Path
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from mcp.server import Server

from cobalt_station.mcp.tools import create_mcp_server


class MCPServerManager:
    """Manages the MCP server lifecycle."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self._server: Server | None = None
        self._mcp_app = None
    
    def get_server(self) -> Server:
        """Get or create the MCP server instance."""
        if self._server is None:
            self._server = create_mcp_server(self.workspace_root)
        return self._server
    
    def get_mcp_app(self) -> FastAPI:
        """Get the MCP streamable HTTP app."""
        if self._mcp_app is None:
            server = self.get_server()
            self._mcp_app = server.streamable_http_app(
                streamable_http_path="/mcp",
                stateless_http=True,
            )
        return self._mcp_app


def create_mcp_routes(app: FastAPI, workspace_root: Path) -> None:
    """Add MCP routes to the FastAPI app."""
    manager = MCPServerManager(workspace_root)
    mcp_app = manager.get_mcp_app()
    
    # Mount the MCP app at /mcp
    app.mount("/mcp", mcp_app)
