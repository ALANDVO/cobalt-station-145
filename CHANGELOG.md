# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

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

