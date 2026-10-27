# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

agent-workspace-isolation

## Roadmap

### agent-workspace-isolation — Strict agent workspace sandbox isolation

Status: done

Acceptance:
- Agent A can only read/write files under its own workspace directory
- Agent A attempting to access Agent B's workspace returns permission error
- Path traversal attempts (../) are blocked
- Absolute paths outside workspace root are rejected

Implementation: `src/cobalt_station/security/workspace_guard.py`, `src/cobalt_station/tools/file_tools.py`

Tests: `tests/test_workspace_isolation.py`

### fastapi-skeleton — FastAPI application skeleton with health endpoint

Status: done

Acceptance:
- FastAPI app starts on configured host/port
- GET /health returns 200 with status info
- Basic project structure with pyproject.toml

Implementation: `src/cobalt_station/main.py`, `src/cobalt_station/api/health.py`, `pyproject.toml`

Tests: `tests/test_health.py`

### agent-management-api — Agent CRUD API with workspace provisioning

Status: planned

Acceptance:
- POST /api/agents creates agent with isolated workspace
- GET /api/agents lists agents
- GET /api/agents/{id} returns agent details
- DELETE /api/agents/{id} removes agent and workspace

Implementation: `src/cobalt_station/api/agents.py`, `src/cobalt_station/models/agent.py`, `src/cobalt_station/services/agent_service.py`

Tests: `tests/test_agents_api.py`

### mcp-tools-exposure — MCP tool exposure for memory system

Status: planned

Acceptance:
- MCP server exposes memory read/write tools
- External AI clients can connect via MCP protocol
- Tools are namespaced per agent workspace

Implementation: `src/cobalt_station/mcp/server.py`, `src/cobalt_station/mcp/tools.py`

Tests: `tests/test_mcp.py`

### user-isolation-preconfigured-specialists — User isolation with pre-configured specialists

Status: planned

Acceptance:
- Admin can create specialist agents with pre-configured models/skills/MCP
- Regular users get assigned specialists without configuration access
- User data/files/workspaces are isolated from each other

Implementation: `src/cobalt_station/models/user.py`, `src/cobalt_station/services/user_service.py`, `src/cobalt_station/api/users.py`

Tests: `tests/test_user_isolation.py`

### postgres-backup-restore — PostgreSQL backup/restore with pg_dump

Status: planned

Acceptance:
- Backup works with SQLite (default) and PostgreSQL
- pg_dump availability checked at startup for PostgreSQL mode
- Restore works for both database types

Implementation: `src/cobalt_station/infra/backup.py`, `src/cobalt_station/api/backup.py`

Tests: `tests/test_backup.py`

### connection-pool-robustness — PostgreSQL connection pool with liveness checks

Status: planned

Acceptance:
- Connection pool uses explicit liveness check (SELECT 1)
- Configurable max_lifetime to avoid cron-window recycling clashes
- Dead connections are detected and replaced before use

Implementation: `src/cobalt_station/infra/db_pool.py`

Tests: `tests/test_db_pool.py`

