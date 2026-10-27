"""File Tools - Secure file operations for agents using workspace guard."""

from pathlib import Path

import aiofiles

from cobalt_station.security.workspace_guard import WorkspaceAccessError, WorkspaceGuard


class FileTools:
    """
    Provides secure file operations for an agent within its workspace.

    All operations are validated through the WorkspaceGuard to ensure
    the agent cannot escape its sandbox.
    """

    def __init__(self, guard: WorkspaceGuard):
        self.guard = guard

    async def read_file(self, path: str | Path) -> str:
        """
        Read a file from the agent's workspace.

        Args:
            path: Path relative to agent workspace

        Returns:
            File contents as string

        Raises:
            WorkspaceAccessError: If path is outside workspace
            FileNotFoundError: If file doesn't exist
        """
        resolved = self.guard.validate_read(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not resolved.is_file():
            raise IsADirectoryError(f"Path is a directory: {path}")

        async with aiofiles.open(resolved, mode="r", encoding="utf-8") as f:
            content = await f.read()
        return content

    async def write_file(self, path: str | Path, content: str) -> Path:
        """
        Write content to a file in the agent's workspace.

        Creates parent directories if they don't exist.

        Args:
            path: Path relative to agent workspace
            content: Content to write

        Returns:
            Resolved path of written file

        Raises:
            WorkspaceAccessError: If path is outside workspace
        """
        resolved = self.guard.validate_write(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(resolved, mode="w", encoding="utf-8") as f:
            await f.write(content)

        return resolved

    async def create_file(self, path: str | Path, content: str = "") -> Path:
        """
        Create a new file in the agent's workspace.

        Fails if file already exists.

        Args:
            path: Path relative to agent workspace
            content: Initial content (default empty)

        Returns:
            Resolved path of created file

        Raises:
            WorkspaceAccessError: If path is outside workspace
            FileExistsError: If file already exists
        """
        resolved = self.guard.validate_write(path)
        if resolved.exists():
            raise FileExistsError(f"File already exists: {path}")

        resolved.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(resolved, mode="w", encoding="utf-8") as f:
            await f.write(content)

        return resolved

    async def append_file(self, path: str | Path, content: str) -> Path:
        """
        Append content to a file in the agent's workspace.

        Creates file if it doesn't exist.

        Args:
            path: Path relative to agent workspace
            content: Content to append

        Returns:
            Resolved path of modified file

        Raises:
            WorkspaceAccessError: If path is outside workspace
        """
        resolved = self.guard.validate_write(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(resolved, mode="a", encoding="utf-8") as f:
            await f.write(content)

        return resolved

    async def delete_file(self, path: str | Path) -> bool:
        """
        Delete a file in the agent's workspace.

        Args:
            path: Path relative to agent workspace

        Returns:
            True if file was deleted

        Raises:
            WorkspaceAccessError: If path is outside workspace
            FileNotFoundError: If file doesn't exist
        """
        resolved = self.guard.validate_delete(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not resolved.is_file():
            raise IsADirectoryError(f"Path is a directory: {path}")

        resolved.unlink()
        return True

    async def list_files(self, path: str | Path = "") -> list[Path]:
        """
        List files in a directory within the agent's workspace.

        Args:
            path: Subdirectory path (default: workspace root)

        Returns:
            List of relative paths to files

        Raises:
            WorkspaceAccessError: If path is outside workspace
        """
        resolved = self.guard.validate_read(path)
        if not resolved.exists():
            return []
        if resolved.is_file():
            return [self.guard.get_relative_path(resolved)]

        files: list[Path] = []
        for item in resolved.rglob("*"):
            if item.is_file():
                files.append(self.guard.get_relative_path(item))
        return files

    async def file_exists(self, path: str | Path) -> bool:
        """Check if a file exists in the agent's workspace."""
        try:
            resolved = self.guard.validate_read(path)
            return resolved.exists() and resolved.is_file()
        except WorkspaceAccessError:
            return False

    async def is_directory(self, path: str | Path) -> bool:
        """Check if a path is a directory in the agent's workspace."""
        try:
            resolved = self.guard.validate_read(path)
            return resolved.exists() and resolved.is_dir()
        except WorkspaceAccessError:
            return False

    async def get_file_size(self, path: str | Path) -> int:
        """Get file size in bytes."""
        resolved = self.guard.validate_read(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return resolved.stat().st_size

    async def make_directory(self, path: str | Path) -> Path:
        """Create a directory in the agent's workspace."""
        resolved = self.guard.validate_write(path)
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved
