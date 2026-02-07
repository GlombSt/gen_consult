# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Philosophy & Architecture

This is a **full-stack learning project** built with **hexagonal architecture** principles and a strong focus on **decomposition**.

### Core Architectural Principle

```
┌─────────────────────────────────────────────┐
│    BACKEND = THE HEXAGON (Business Core)    │
│                                             │
│  Domain-driven, event-based architecture    │
│  Contains ALL business logic and rules      │
└─────────────────────────────────────────────┘
                    ▲
                    │ HTTP API (Port)
                    │
┌─────────────────────────────────────────────┐
│  FRONTEND = PRIMARY ADAPTER (Thin Client)   │
│                                             │
│  Presentation layer only, NO business logic │
└─────────────────────────────────────────────┘
```

**Critical Understanding:**
- Backend IS the hexagon (business core)
- Frontend IS an adapter (talks through HTTP port)
- Business logic lives ONLY in backend
- Frontend is for presentation and UX only

## Repository Structure

This is a **multi-project repository** (NOT a formal monorepo):
- Single git repository
- Two independent projects
- No code sharing between projects
- Separate package managers (pip vs npm)
- Enforces hexagonal boundaries through physical separation

```
gen_consult/
├── intentions/          # FastAPI backend (the hexagon)
├── customer-ux/        # React frontend (primary adapter)
├── TODO.md            # Architecture alignment tasks
└── CLAUDE.md          # This file
```

## Important Reference Files

### Backend Documentation
- `intentions/ARCHITECTURE_STANDARDS.md` - Mandatory rules
- `intentions/ARCHITECTURE_GUIDE.md` - Detailed examples and patterns
- `intentions/DEVELOPMENT_STANDARDS.md` - Development workflow requirements
- `intentions/AGENT_WORKFLOW.md` - **MANDATORY for coding agents** - Completion criteria and workflow
- `intentions/TESTING_STANDARDS.md` - Testing requirements

### Frontend Documentation
- `customer-ux/ARCHITECTURE.md` - Frontend architecture guide
- `customer-ux/README.md` - Getting started

### Project Documentation
- `AGENTS.md` - Readable code conventions for coding agents (simplicity, structure, naming). Backend Python: see `intentions/PYTHON_IDIOM_STANDARDS.md`
- `TODO.md` - Current architecture alignment tasks
- `README.md` - Project overview
- `CI.md` - CI/CD workflow triggers and configuration

## GitHub: always use the CLI

**Use the GitHub CLI (`gh`) for all GitHub operations.** Do not assume the user will push, open PRs, or check CI in the browser.

- **Push:** `git push -u origin <branch>` (git); use `gh` for anything that talks to GitHub after push.
- **Pull requests:** `gh pr create --base main --head <branch> --title "..." --body "..."`.
- **CI / Actions:** `gh run list --workflow=<name>`, `gh run view <run-id>`, `gh run watch <run-id>` to monitor until green.
- **Repo/branch context:** `gh pr list`, `gh pr view`, `gh run list` as needed.

When the user asks to push, open a PR, or monitor CI, use `gh` (and git for commit/push). See also `intentions/AGENT_WORKFLOW.md` for the full workflow.

## Backend (`intentions/`) - The Hexagon

**The backend IS the hexagon** - it contains all business logic. The frontend is a thin adapter.

### Key Architectural Concepts

- **Service layer = Ports** - Public API for cross-domain communication
- **Three model types:** DB models (`db_models.py`), domain models (`models.py`), API DTOs (`schemas.py`)
- **Data flow:** `Router (DTO) → Service (Domain Model) → Repository (DB Model) → Database`
- **Cross-domain communication:** Always through service layer ports, never direct repository/model access
- **Event system:** All business actions publish domain events (service layer only)

**For detailed architecture rules, see:**
- `intentions/ARCHITECTURE_STANDARDS.md` - **MANDATORY** - Complete layer rules and structure requirements
- `intentions/ARCHITECTURE_GUIDE.md` - Detailed examples and patterns

**For setup, commands, and testing:**
- `intentions/README.md` - Quick start, development commands, testing requirements
- `intentions/TESTING_STANDARDS.md` - Coverage requirements and test patterns

## Frontend (`customer-ux/`) - The Primary Adapter

**The frontend IS a primary adapter** - it drives the backend hexagon through HTTP. No business logic in frontend.

### Key Architectural Concepts

- **Thin client** - Presentation and UX only; all business logic in backend
- **Feature-based organization** - Organized by domain (intents, users), not technical layer
- **Layer separation** - Components → Hooks → API clients
- **Type mapping** - Frontend types mirror backend `schemas.py` (API DTOs), NOT `models.py` (domain models)
- **Development pattern** - API client → Hook → Component

**For detailed architecture rules, see:**
- `customer-ux/ARCHITECTURE.md` - **MANDATORY** - Complete layer responsibilities, patterns, and anti-patterns

**For setup, commands, and workflow:**
- `customer-ux/README.md` - Quick start, development commands, feature development workflow

## Hexagonal Architecture Principles

**Key concepts:**
- **Ports** = Service layer functions (public API of each domain)
- **Primary Adapters** = Drive the app (HTTP router, React frontend)
- **Secondary Adapters** = Driven by app (database, event bus)
- **Decomposition** = Organize by business domain, not technical layer
- **Communication** = Through service ports (synchronous) or events (asynchronous)

**For detailed patterns and examples, see:**
- `intentions/ARCHITECTURE_STANDARDS.md` - Ports, adapters, decomposition rules
- `intentions/ARCHITECTURE_GUIDE.md` - Communication patterns, examples

## Development Workflows

**For step-by-step feature development:**
- Backend: `intentions/ARCHITECTURE_STANDARDS.md` + `intentions/DEVELOPMENT_STANDARDS.md`
- Frontend: `customer-ux/ARCHITECTURE.md` + `customer-ux/README.md`

## Anti-Patterns

**For comprehensive anti-patterns and what to avoid:**
- Backend: `intentions/ARCHITECTURE_STANDARDS.md` and `intentions/ARCHITECTURE_GUIDE.md`
- Frontend: `customer-ux/ARCHITECTURE.md` (Anti-Patterns section)

## API Integration

**For endpoints, ports, and configuration:**
- `intentions/README.md` - API endpoints, ports, CORS configuration

## Working with This Codebase

### Key Principles for Claude Code

1. **Respect the hexagon** - Business logic stays in backend service layer
2. **Use the ports** - Cross-domain calls through service layer only
3. **Publish events** - All business actions must publish domain events
4. **Three model types** - DB, domain, and DTO models are separate
5. **Frontend stays thin** - No business logic in React components/hooks
6. **Check TODO.md** - Some decisions are pending, check before implementing
7. **Follow the layers** - Router → Service → Repository, no shortcuts
8. **Test thoroughly** - 80%+ coverage required
9. **TDD is mandatory** - Read `DEVELOPMENT_STANDARDS.md`
10. **Complete workflow** - Read `AGENT_WORKFLOW.md` - MUST push code and verify CI passes before completion
11. **GitHub = use CLI** - Use **GitHub CLI (`gh`)** for all GitHub operations: push (after git commit), `gh pr create`, `gh run list` / `gh run watch` to monitor CI. Do not ask the user to open PRs or check Actions in the browser.
12. **Readable code** - Apply conventions in `AGENTS.md`; for backend Python also `intentions/PYTHON_IDIOM_STANDARDS.md`.

### Before Making Changes

1. Check if feature spans multiple domains → use service layer APIs
2. Check if it's a business rule → belongs in backend service/model
3. Check if it affects types → update schemas.py, not models.py
4. Check if it's a business action → must publish domain event
5. Check TODO.md → your change might be part of pending work
