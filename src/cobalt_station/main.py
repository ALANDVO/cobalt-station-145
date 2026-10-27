"""Cobalt Station 145 - Main FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cobalt_station.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cobalt Station 145",
        description="A smarter, self-hosted AI assistant — multi-user, multi-agent",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Include routers
    app.include_router(health_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cobalt_station.main:app", host="0.0.0.0", port=8000, reload=True)
