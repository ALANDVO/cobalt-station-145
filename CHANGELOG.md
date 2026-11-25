# Changelog

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

### Added
- **Pre-configured Specialist Agents**: Agents can now be created with pre-configured models, skills, and MCP server endpoints
  - `model` field on AgentCreate/Agent for specifying pre-configured LLM models (e.g. 'gpt-4', 'claude-3', 'zhipu-glm-5')
  - `skills` field on AgentCreate/Agent for listing pre-configured capabilities (e.g. ['web_search', 'file_analysis', 'code_review'])
  - `mcp_servers` field on AgentCreate/Agent for specifying pre-configured MCP server connections (e.g. ['mcp://server:port'])
- **Pre-configured specialist assignment**: Users can be assigned specialists with full model/skills/MCP configuration in a single operation

### Changed
- Updated `src/cobalt_station/models/agent.py`: Added `model`, `skills`, `mcp_servers` fields to `AgentCreate`, `Agent`, and `AgentResponse` models
- Updated `src/cobalt_station/services/agent_service.py`: `create_agent` now passes through pre-configured fields from `AgentCreate` to `Agent` entity
- Updated API response models to include pre-configured specialist fields

Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — 2026-11-08

### Added
- **MCP Tool Exposure**: MCP server exposing memory tools for agent workspaces
  - `read_memory` - Read memory files from agent workspace
  - `write_memory` - Write memory files to agent workspace  
  - `list_memory` - List memory files in agent workspace
  - Streamable HTTP transport at `/mcp` endpoint
  - Full workspace isolation enforced per agent
- **MCP Tools Module**: Handler functions for MCP tool calls with validation
- **Tests**: 6 comprehensive tests for MCP tools and API (test_mcp.py)

### Changed
- Updated main.py to use FastAPI lifespan for startup/shutdown
- MCP routes mounted at app creation time

### Infrastructure
- Added `mcp>=1.0.0` dependency to pyproject.toml
- Workspace isolation preserved for MCP tool access


## 1.0.0 — 2026-11-05
## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 0.1.0 — 2026-11-05

### Added
- **Agent Management API**: Complete CRUD API for agents with workspace provisioning
  - `POST /api/agents` - Create agent with isolated workspace
  - `GET /api/agents` - List all agents
  - `GET /api/agents/{id}` - Get agent details
  - `PATCH /api/agents/{id}` - Update agent properties
  - `DELETE /api/agents/{id}` - Delete agent and workspace
- **Agent Models**: Pydantic models for Agent, AgentCreate, AgentUpdate, AgentResponse, AgentListResponse
- **Agent Service**: Service layer for agent lifecycle management with workspace isolation
- **Tests**: 11 comprehensive tests for agents API (test_agents_api.py)

### Infrastructure
- FastAPI app with lifespan management for agent service initialization
- Request-scoped dependency injection for agent service

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
