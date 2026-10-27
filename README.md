# Cobalt Station 145 — Alan Vo

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


A smarter, self-hosted AI assistant — multi-user, multi-agent.

## Features

- **Strict agent workspace isolation**: Each agent operates in its own sandboxed workspace
- **Multi-user support**: Users are isolated from each other with pre-configured specialists
- **MCP tool exposure**: Memory system exposed via MCP for external AI clients
- **PostgreSQL/SQLite support**: Flexible storage backends with robust connection pooling

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the server
python -m cobalt_station.main

# Or with uvicorn directly
uvicorn cobalt_station.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `GET /health` - Health check

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_workspace_isolation.py -v
pytest tests/test_health.py -v
```

## Project Structure

```
src/cobalt_station/
├── main.py                 # FastAPI application entry point
├── api/                    # API routers
│   ├── health.py          # Health check endpoint
│   └── ...
├── security/              # Security and isolation
│   ├── workspace_guard.py # Workspace boundary enforcement
│   └── ...
├── tools/                 # Agent tools
│   ├── file_tools.py      # Secure file operations
│   └── ...
├── models/                # Data models
├── services/              # Business logic
└── mcp/                   # MCP server (planned)
```

## Workspace Isolation

Each agent has its own workspace directory under the workspace root:

```
/workspace_root/
├── agent_a/
│   ├── config.json
│   └── data/
└── agent_b/
    ├── config.json
    └── data/
```

Agents cannot access files outside their workspace. Path traversal attempts (../) and absolute paths outside the workspace are blocked with `WorkspaceAccessError`.

## Development

### Code Style

- Ruff for linting and formatting
- MyPy for type checking
- pytest for testing

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy src/

# Test
pytest
```

Maintainer: Alan Vo <alanvo@gmail.com>
