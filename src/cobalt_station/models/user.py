"""User models for Cobalt Station."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class UserStatus(str, Enum):
    """User lifecycle status."""
    CREATED = "created"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class User(BaseModel):
    """User entity with workspace isolation."""
    id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="Human-readable user name")
    specialist_id: Optional[str] = Field(None, description="ID for assigned specialist agent")
    workspace_path: Path = Field(..., description="Absolute path to user's workspace")
    status: UserStatus = Field(default=UserStatus.CREATED, description="User status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class UserCreate(BaseModel):
    """Request model for creating a user."""
    name: str = Field(..., min_length=1, max_length=100, description="User name")
    specialist_id: Optional[str] = Field(None, description="ID of specialist agent to assign")
    status: Optional[UserStatus] = None


class UserUpdate(BaseModel):
    """Request model for updating a user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    specialist_id: Optional[str] = Field(None)
    workspace_path: Optional[Path] = None
    status: Optional[UserStatus] = None


class UserResponse(BaseModel):
    """Response model for user API."""
    id: str
    name: str
    specialist_id: Optional[str]
    workspace_path: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            specialist_id=user.specialist_id,
            workspace_path=str(user.workspace_path),
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserListResponse(BaseModel):
    """Response model for listing users."""
    users: list[UserResponse]
    total: int
