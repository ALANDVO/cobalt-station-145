"""Health check endpoint."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    return HealthResponse(status="ok", version=request.app.version)
