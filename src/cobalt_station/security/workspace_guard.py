"""
Workspace Guard - Strict sandbox isolation for agent workspaces.

Ensures each agent can only access files within its own workspace directory.
Blocks path traversal attempts and absolute paths outside workspace root.
"""

from pathlib import Path


class WorkspaceAccessError(PermissionError):
    """Raised when an agent attempts to access files outside its workspace."""


class WorkspaceGuard:
    """
    Enforces strict workspace boundaries for agents.
    
    Each agent is confined to its own workspace directory under the workspace root.
    All file operations are validated against the agent's workspace boundary.
    """
    
    def __init__(self, workspace_root: Path, agent_id: str):
        """
        Initialize the workspace guard for a specific agent.
        
        Args:
            workspace_root: Root directory containing all agent workspaces
            agent_id: Unique identifier for the agent
        """
        self.workspace_root = workspace_root.resolve()
        self.agent_id = agent_id
        self.agent_workspace = (self.workspace_root / agent_id).resolve()
        
    def ensure_workspace_exists(self) -> Path:
        """Create the agent's workspace directory if it doesn't exist."""
        self.agent_workspace.mkdir(parents=True, exist_ok=True)
        return self.agent_workspace
    
    def resolve_path(self, path: str | Path) -> Path:
        """
        Resolve and validate a path against the agent's workspace boundary.
        
        Args:
            path: Relative or absolute path to validate
            
        Returns:
            Resolved absolute path within the agent's workspace
            
        Raises:
            WorkspaceAccessError: If path escapes the workspace boundary
        """
        # Convert to Path object
        target = Path(path)
        
        # If absolute path, check it's within workspace
        if target.is_absolute():
            resolved = target.resolve()
        else:
            # Relative path: resolve relative to agent workspace
            resolved = (self.agent_workspace / target).resolve()
        
        # Ensure the resolved path is within the agent's workspace
        try:
            resolved.relative_to(self.agent_workspace)
        except ValueError:
            raise WorkspaceAccessError(
                f"Access denied: path '{path}' resolves to '{resolved}' "
                f"which is outside agent workspace '{self.agent_workspace}'"
            )
        
        # Additional check: prevent symlink escapes
        if not self._is_within_workspace(resolved):
            raise WorkspaceAccessError(
                f"Access denied: path '{path}' resolves to '{resolved}' "
                f"which escapes workspace via symlink"
            )
        
        return resolved
    
    def _is_within_workspace(self, path: Path) -> bool:
        """Check if a resolved path is truly within the workspace (handles symlinks)."""
        try:
            # Use resolve() on both to handle symlinks
            path.resolve().relative_to(self.agent_workspace.resolve())
            return True
        except ValueError:
            return False
    
    def validate_read(self, path: str | Path) -> Path:
        """Validate a path for read access."""
        return self.resolve_path(path)
    
    def validate_write(self, path: str | Path) -> Path:
        """Validate a path for write access (same as read for now)."""
        return self.resolve_path(path)
    
    def validate_delete(self, path: str | Path) -> Path:
        """Validate a path for delete access."""
        return self.resolve_path(path)
    
    def list_files(self, subdir: str = "") -> list[Path]:
        """List files in a subdirectory of the agent's workspace."""
        target = self.resolve_path(subdir)
        if not target.exists():
            return []
        if target.is_file():
            return [target]
        return [f for f in target.rglob("*") if f.is_file()]
    
    def get_workspace_root(self) -> Path:
        """Get the agent's workspace root directory."""
        return self.agent_workspace
    
    def get_relative_path(self, absolute_path: Path) -> Path:
        """Get the path relative to the agent's workspace root."""
        return absolute_path.relative_to(self.agent_workspace)


def create_workspace_guard(workspace_root: str | Path, agent_id: str) -> WorkspaceGuard:
    """Factory function to create a WorkspaceGuard instance."""
    return WorkspaceGuard(Path(workspace_root), agent_id)
