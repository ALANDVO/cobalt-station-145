"""Cobalt Station 145 - Main FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from cobalt_station.api.health import router as health_router
from cobalt_station.api.agents import router as agents_router
from cobalt_station.services.agent_service import AgentService
from cobalt_station.mcp.server import create_mcp_routes


# Module-level workspace root for route setup
WORKSPACE_ROOT = Path("workspaces")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    app.state.agent_service = AgentService(WORKSPACE_ROOT)
    yield
    # Shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cobalt Station 145",
        description="A smarter, self-hosted AI assistant — multi-user, multi-agent",
        version="1.1.0",
        lifespan=lifespan,
    )

    # Setup MCP routes (must be done at app creation time)
    create_mcp_routes(app, WORKSPACE_ROOT)

    # Include routers
    app.include_router(health_router)
    app.include_router(agents_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cobalt_station.main:app", host="0.0.0.0", port=8000, reload=True)
