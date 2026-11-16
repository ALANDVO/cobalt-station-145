"""User service for managing users and their workspace isolation."""

import shutil
import uuid
from pathlib import Path

from cobalt_station.models.user import User, UserCreate, UserStatus
from cobalt_station.security.workspace_guard import WorkspaceGuard


class UserService:
    """Service for managing user lifecycle and workspace provisioning."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        # Separate user workspace root under workspace_root
        self.user_workspace_root = workspace_root / "users"
        self.user_workspace_root.mkdir(parents=True, exist_ok=True)
        self._users: dict[str, User] = {}

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user with isolated workspace."""
        user_id = str(uuid.uuid4())[:8]
        workspace_path = self.user_workspace_root / user_id

        user = User(
            id=user_id,
            name=user_create.name,
            specialist_id=user_create.specialist_id,
            workspace_path=workspace_path,
            status=UserStatus.CREATED,  # Assume status from user model
        )

        workspace_path.mkdir(parents=True, exist_ok=True)
        self._users[user_id] = user
        return user

    def get_user(self, user_id: str) -> User:
        """Get a user by ID."""
        if user_id not in self._users:
            raise KeyError(f"User not found: {user_id}")
        return self._users[user_id]

    def list_users(self) -> list[User]:
        """List all users."""
        return list(self._users.values())

    def update_user(
        self,
        user_id: str,
        name: str | None = None,
        specialist_id: str | None = None,
        workspace_path: Path | None = None,
        status: UserStatus | None = None,
    ) -> User:
        """Update a user's properties."""
        user = self.get_user(user_id)
        if name is not None:
            user.name = name
        if specialist_id is not None:
            user.specialist_id = specialist_id
        if workspace_path is not None:
            user.workspace_path = workspace_path
        if status is not None:
            user.status = status
        return user

    def delete_user(self, user_id: str) -> None:
        """Delete a user and its workspace."""
        user = self.get_user(user_id)
        if user.workspace_path.exists():
            shutil.rmtree(user.workspace_path)
        del self._users[user_id]

    def get_workspace_guard(self, user_id: str) -> WorkspaceGuard:
        """Get a workspace guard for a user."""
        self.get_user(user_id)
        return WorkspaceGuard(self.user_workspace_root, user_id)

    def assign_specialist(self, user_id: str, specialist_id: str) -> None:
        """Assign a specialist agent to a user."""
        user = self.get_user(user_id)
        user.specialist_id = specialist_id
