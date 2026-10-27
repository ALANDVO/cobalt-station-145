"""
Tests for agent workspace isolation.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from cobalt_station.security.workspace_guard import WorkspaceAccessError, WorkspaceGuard
from cobalt_station.tools.file_tools import FileTools


class TestWorkspaceGuard:
    """Test the WorkspaceGuard class."""
    
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_root = self.temp_dir / "workspaces"
        self.workspace_root.mkdir()
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_agent_workspace_created(self):
        """Test that agent workspace is created on demand."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        workspace = guard.ensure_workspace_exists()
        assert workspace == self.workspace_root / "agent_a"
        assert workspace.exists()
        assert workspace.is_dir()
    
    def test_resolve_relative_path(self):
        """Test resolving relative paths within workspace."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        resolved = guard.resolve_path("config.json")
        expected = (self.workspace_root / "agent_a" / "config.json").resolve()
        assert resolved == expected
    
    def test_resolve_nested_path(self):
        """Test resolving nested paths within workspace."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        resolved = guard.resolve_path("subdir/nested/file.txt")
        expected = (self.workspace_root / "agent_a" / "subdir" / "nested" / "file.txt").resolve()
        assert resolved == expected
    
    def test_block_parent_traversal(self):
        """Test that ../ path traversal is blocked."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        with pytest.raises(WorkspaceAccessError):
            guard.resolve_path("../agent_b/secret.txt")
    
    def test_block_multiple_parent_traversal(self):
        """Test that multiple ../ traversals are blocked."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        with pytest.raises(WorkspaceAccessError):
            guard.resolve_path("../../../etc/passwd")
    
    def test_block_absolute_path_outside_workspace(self):
        """Test that absolute paths outside workspace are blocked."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        with pytest.raises(WorkspaceAccessError):
            guard.resolve_path("/etc/passwd")
    
    def test_block_absolute_path_to_other_agent(self):
        """Test that absolute paths to other agent workspaces are blocked."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        other_workspace = self.workspace_root / "agent_b"
        other_workspace.mkdir()
        
        with pytest.raises(WorkspaceAccessError):
            guard.resolve_path(str(other_workspace / "secret.txt"))
    
    def test_allow_absolute_path_within_workspace(self):
        """Test that absolute paths within workspace are allowed."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        abs_path = (self.workspace_root / "agent_a" / "config.json").resolve()
        resolved = guard.resolve_path(str(abs_path))
        assert resolved == abs_path
    
    def test_validate_read_write_delete(self):
        """Test that validate_read, validate_write, validate_delete all work."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        read_path = guard.validate_read("file.txt")
        write_path = guard.validate_write("file.txt")
        delete_path = guard.validate_delete("file.txt")
        
        assert read_path == write_path == delete_path
    
    def test_list_files(self):
        """Test listing files in workspace."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        # Create some test files
        (self.workspace_root / "agent_a" / "file1.txt").write_text("content1")
        
        (self.workspace_root / "agent_a" / "subdir").mkdir(parents=True, exist_ok=True)
        (self.workspace_root / "agent_a" / "subdir" / "file2.txt").write_text("content2")
        
        files = guard.list_files()
        assert len(files) == 2
    
    def test_list_files_subdir(self):
        """Test listing files in a subdirectory."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        (self.workspace_root / "agent_a" / "subdir").mkdir(parents=True, exist_ok=True)
        (self.workspace_root / "agent_a" / "subdir" / "file.txt").write_text("content")
        
        files = guard.list_files("subdir")
        assert len(files) == 1
        assert files[0].name == "file.txt"
    
    def test_get_relative_path(self):
        """Test getting relative path from absolute path."""
        guard = WorkspaceGuard(self.workspace_root, "agent_a")
        guard.ensure_workspace_exists()
        
        abs_path = (self.workspace_root / "agent_a" / "subdir" / "file.txt").resolve()
        rel_path = guard.get_relative_path(abs_path)
        assert rel_path == Path("subdir") / "file.txt"


class TestFileTools:
    """Test the FileTools class."""
    
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_root = self.temp_dir / "workspaces"
        self.workspace_root.mkdir()
        self.guard = WorkspaceGuard(self.workspace_root, "agent_a")
        self.guard.ensure_workspace_exists()
        self.tools = FileTools(self.guard)
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_write_and_read_file(self):
        """Test writing and reading a file."""
        await self.tools.write_file("test.txt", "Hello, World!")
        content = await self.tools.read_file("test.txt")
        assert content == "Hello, World!"
    
    @pytest.mark.asyncio
    async def test_create_file(self):
        """Test creating a new file."""
        path = await self.tools.create_file("new.txt", "initial content")
        assert path.name == "new.txt"
        content = await self.tools.read_file("new.txt")
        assert content == "initial content"
    
    @pytest.mark.asyncio
    async def test_create_file_fails_if_exists(self):
        """Test that create_file fails if file already exists."""
        await self.tools.create_file("exists.txt", "content")
        with pytest.raises(FileExistsError):
            await self.tools.create_file("exists.txt", "new content")
    
    @pytest.mark.asyncio
    async def test_append_file(self):
        """Test appending to a file."""
        await self.tools.write_file("append.txt", "first ")
        await self.tools.append_file("append.txt", "second")
        content = await self.tools.read_file("append.txt")
        assert content == "first second"
    
    @pytest.mark.asyncio
    async def test_delete_file(self):
        """Test deleting a file."""
        await self.tools.write_file("to_delete.txt", "content")
        assert await self.tools.file_exists("to_delete.txt")
        
        result = await self.tools.delete_file("to_delete.txt")
        assert result is True
        assert not await self.tools.file_exists("to_delete.txt")
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_fails(self):
        """Test that deleting non-existent file fails."""
        with pytest.raises(FileNotFoundError):
            await self.tools.delete_file("nonexistent.txt")
    
    @pytest.mark.asyncio
    async def test_list_files(self):
        """Test listing files."""
        await self.tools.write_file("file1.txt", "content1")
        await self.tools.make_directory("subdir")
        await self.tools.write_file("subdir/file2.txt", "content2")
        
        files = await self.tools.list_files()
        assert len(files) == 2
        names = {f.name for f in files}
        assert names == {"file1.txt", "file2.txt"}
    
    @pytest.mark.asyncio
    async def test_file_exists(self):
        """Test file_exists check."""
        assert not await self.tools.file_exists("missing.txt")
        await self.tools.write_file("present.txt", "content")
        assert await self.tools.file_exists("present.txt")
    
    @pytest.mark.asyncio
    async def test_is_directory(self):
        """Test is_directory check."""
        assert not await self.tools.is_directory("missing")
        await self.tools.make_directory("mydir")
        assert await self.tools.is_directory("mydir")
        await self.tools.write_file("myfile.txt", "content")
        assert not await self.tools.is_directory("myfile.txt")
    
    @pytest.mark.asyncio
    async def test_get_file_size(self):
        """Test getting file size."""
        await self.tools.write_file("size.txt", "12345")
        size = await self.tools.get_file_size("size.txt")
        assert size == 5
    
    @pytest.mark.asyncio
    async def test_make_directory(self):
        """Test creating directories."""
        path = await self.tools.make_directory("newdir/subdir")
        assert path.exists()
        assert path.is_dir()
        assert path.name == "subdir"


class TestCrossAgentIsolation:
    """Test that agents cannot access each other's workspaces."""
    
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_root = self.temp_dir / "workspaces"
        self.workspace_root.mkdir()
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_agent_a_cannot_access_agent_b_workspace(self):
        """Test that agent A cannot resolve paths to agent B's workspace."""
        guard_a = WorkspaceGuard(self.workspace_root, "agent_a")
        guard_a.ensure_workspace_exists()
        
        guard_b = WorkspaceGuard(self.workspace_root, "agent_b")
        guard_b.ensure_workspace_exists()
        
        # Create a file in agent B's workspace
        (self.workspace_root / "agent_b" / "secret.txt").write_text("secret")
        
        # Agent A tries to access it
        with pytest.raises(WorkspaceAccessError):
            guard_a.resolve_path("../agent_b/secret.txt")
    
    def test_agent_a_cannot_write_to_agent_b_workspace(self):
        """Test that agent A cannot write to agent B's workspace."""
        guard_a = WorkspaceGuard(self.workspace_root, "agent_a")
        guard_a.ensure_workspace_exists()
        
        guard_b = WorkspaceGuard(self.workspace_root, "agent_b")
        guard_b.ensure_workspace_exists()
        
        # Agent A tries to write to agent B's workspace via absolute path
        abs_path = (self.workspace_root / "agent_b" / "hacked.txt").resolve()
        with pytest.raises(WorkspaceAccessError):
            guard_a.resolve_path(str(abs_path))
    
    @pytest.mark.asyncio
    async def test_file_tools_enforce_isolation(self):
        """Test that FileTools enforce workspace isolation."""
        guard_a = WorkspaceGuard(self.workspace_root, "agent_a")
        guard_a.ensure_workspace_exists()
        tools_a = FileTools(guard_a)
        
        guard_b = WorkspaceGuard(self.workspace_root, "agent_b")
        guard_b.ensure_workspace_exists()
        tools_b = FileTools(guard_b)
        
        # Agent B creates a file
        await tools_b.write_file("secret.txt", "agent_b secret")
        
        # Agent A tries to read it - should fail
        with pytest.raises(WorkspaceAccessError):
            await tools_a.read_file("../agent_b/secret.txt")
        
        # Agent A tries to write to it - should fail
        with pytest.raises(WorkspaceAccessError):
            await tools_a.write_file("../agent_b/hacked.txt", "hacked")
