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
├── declaring/          # FastAPI backend (the hexagon)
├── reacting/           # React frontend (primary adapter)
├── TODO.md            # Architecture alignment tasks
└── CLAUDE.md          # This file
```

## Important Reference Files

### Backend Documentation
- `declaring/ARCHITECTURE_STANDARDS.md` - Mandatory rules
- `declaring/ARCHITECTURE_GUIDE.md` - Detailed examples and patterns
- `declaring/DEVELOPMENT_STANDARDS.md` - Development workflow requirements
- `declaring/AGENT_WORKFLOW.md` - **MANDATORY for coding agents** - Completion criteria and workflow
- `declaring/TESTING_STANDARDS.md` - Testing requirements

### Frontend Documentation
- `reacting/ARCHITECTURE.md` - Frontend architecture guide
- `reacting/README.md` - Getting started

### Project Documentation
- `TODO.md` - Current architecture alignment tasks
- `README.md` - Project overview



## Backend (`declaring/`) - The Hexagon

### Tech Stack
- FastAPI (Python 3.14+)
- Pydantic for validation
- Structured JSON logging with PII protection
- Event-driven domain architecture

### Architecture Overview

```
app/
├── {domain}/              # e.g., intents/, users/
│   ├── models.py          # Domain models with business logic
│   ├── schemas.py         # API DTOs (request/response)
│   ├── service.py         # Business logic = PORT (public API)
│   ├── repository.py      # Data access = ADAPTER (secondary)
│   ├── router.py          # HTTP endpoints = ADAPTER (primary)
│   ├── events.py          # Domain events
│   └── __init__.py        # Exports public API ONLY
├── shared/                # Cross-cutting concerns
│   ├── events.py          # Event bus system
│   ├── logging_config.py  # Structured logging with PII protection
│   └── value_objects.py   # Shared domain concepts
└── main.py                # Application entry point
```

### Critical Layer Rules

**The Hexagon Core (Business Logic):**
- `models.py` - Domain entities with business rules and validation
- `service.py` - Business operations and orchestration (**THIS IS THE PORT**)
- `events.py` - Domain events for decoupling

**Adapters (Infrastructure):**
- `router.py` - HTTP adapter (primary)
- `repository.py` - Database adapter (secondary)
- Event bus - Analytics/notification adapter (secondary)

**Data Flow:** `Router (DTO) → Service (Domain Model) → Repository (DB Model) → Database`

**Model Separation (CRITICAL):**
- `db_models.py` - Database schema (includes audit fields, soft delete, internal data)
- `models.py` - Domain models with business logic (what the hexagon works with)
- `schemas.py` - API DTOs for HTTP layer (excludes sensitive data)

**Cross-Domain Communication:**
```python
# ✅ CORRECT - Through service port
from app.intents import service as intent_service
intent = await intent_service.get_intent(intent_id)

# ❌ WRONG - Direct access to internals
from app.intents.repository import intent_repository
from app.intents.models import Intent
```

**Event System:**
- ALL significant business actions MUST publish domain events
- Events are for: analytics, logging, cross-domain communication
- Frontend does NOT consume these events directly (currently)
- Service layer publishes events, never router or repository

### Development Commands

```bash
cd declaring

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn main:app --reload
uvicorn main:app --reload --port 8001  # Different port

# Test
pytest                                  # All tests
pytest tests/unit -m unit              # Unit tests only
pytest tests/integration -m integration # Integration tests
pytest tests/api -m api                # API tests
pytest --cov=app --cov-report=html     # With coverage

# Docker
docker-compose up --build
docker-compose down
```

### Testing Requirements
- **Models:** 90%+ coverage
- **Service:** 85%+ coverage
- **Repository:** 80%+ coverage
- **Overall:** 80%+ coverage
- Event publishing MUST be tested for all business actions

## Frontend (`reacting/`) - The Primary Adapter

### Tech Stack
- React 18
- Vite (build tool)
- Vanilla JavaScript (TypeScript decision pending - see TODO.md)

### Architecture Overview

```
src/
├── features/              # Mirrors backend domains
│   ├── intents/
│   │   ├── components/    # UI components (thin, delegate to hooks)
│   │   ├── hooks/         # Orchestration layer
│   │   ├── api/           # HTTP adapter to backend
│   │   └── utils/         # Display formatting, UX validation
│   └── users/
├── shared/
│   ├── components/        # Reusable UI
│   ├── api/               # httpClient, apiConfig, apiError
│   └── utils/             # Generic utilities
├── App.jsx
└── main.jsx
```

### Critical Frontend Rules

**Responsibility Boundaries:**
- ✅ UI: Presentation, user interaction, loading states, UX feedback
- ✅ View Models: Shape DTOs for display (formatting, combining fields)
- ✅ Client Validation: UX only (instant feedback, not business rules)
- ❌ Business Rules: Backend only (pricing, authorization, domain logic)
- ❌ Complex Calculations: Backend only

**Type/Interface Mapping (IMPORTANT):**
- Frontend types mirror backend `schemas.py` (API DTOs)
- Frontend types DO NOT mirror backend `models.py` (domain models)
- Example: `IntentResponse` in `schemas.py` → `IntentResponse` type in frontend
- Domain models with business logic stay in backend only

**Layer Responsibilities:**
- `components/` - Render, handle interactions, NO API calls, NO business logic
- `hooks/` - Orchestrate API calls, manage UI state, NO business logic
- `api/` - HTTP communication, NO business logic, NO UI state
- `utils/` - Pure functions for formatting/display only

**Development Pattern:**
1. Build API client (`api/intentsApi.js`) - calls backend endpoints
2. Create hook (`hooks/useCreateIntent.js`) - orchestrates API + UI state
3. Build component (`components/IntentCreator/`) - uses hook, displays UI

### Development Commands

```bash
cd reacting

# Setup
npm install

# Run
npm run dev      # Development server (usually http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview production build
```

## Hexagonal Architecture Principles

### Ports & Adapters

**Ports (Interfaces):**
- Service layer functions are the ports
- Defined in `service.py` files
- Exported in `__init__.py` of each domain
- Other domains call through these ports

**Primary Adapters (Drive the app):**
- HTTP Router (`router.py`)
- React Frontend
- CLI tools (future)
- GraphQL API (future)

**Secondary Adapters (Driven by app):**
- Repository (database)
- Event bus
- External APIs
- Email service (future)

### Decomposition Strategy

**Create new domain when:**
- ✅ Distinct business concepts (intents ≠ users ≠ orders)
- ✅ Could be owned by different team
- ✅ Changes for different business reasons
- ✅ Has independent lifecycle

**Don't create domain for:**
- ❌ Technical layers (validation, logging)
- ❌ Shared utilities
- ❌ Simple CRUD without business logic

**Shared Value Objects:**
- Common concepts used across domains
- Located in `app/shared/value_objects.py`
- Examples: Money, Address, DateRange
- Immutable, defined by values

### Communication Patterns

**Synchronous (Direct service calls):**
```python
# Use when: Need immediate validation, must fail together
from app.users import service as user_service
user = await user_service.get_user(user_id)
```

**Asynchronous (Domain events):**
```python
# Use when: Different contexts, eventual consistency OK, reduce coupling
await event_bus.publish(IntentCreatedEvent(...))
# Other domains listen to events
```

## Development Workflows

### Adding a New Feature (Full Stack)

**MANDATORY: Read `declaring/DEVELOPMENT_STANDARDS.md` first **
**Backend:**
1. Create domain folder: `app/new_domain/`
2. Define domain model with business logic: `models.py`
3. Define API DTOs: `schemas.py`
4. Implement service layer (the port): `service.py`
5. Create repository: `repository.py`
6. Define and publish events: `events.py`
7. Add HTTP endpoints: `router.py`
8. Export public API: `__init__.py`
9. Write tests (unit, integration, API)
10. Register router in `main.py`

**Frontend:**
1. Create feature folder: `src/features/new_domain/`
2. Build API client: `api/newDomainApi.js`
3. Create orchestration hooks: `hooks/useCreateThing.js`
4. Build components: `components/ThingCreator/`
5. Add utilities if needed: `utils/thingFormatters.js`

## Anti-Patterns to Avoid

### Backend
- ❌ Business logic in routers
- ❌ Direct cross-domain repository access
- ❌ Forgetting to publish domain events
- ❌ Mixing domain models and API DTOs
- ❌ Exposing sensitive fields in schemas.py
- ❌ Service layer knowing about HTTP details

### Frontend
- ❌ Replicating backend business rules
- ❌ Creating complex entity classes with methods
- ❌ API calls directly in components (bypass hooks)
- ❌ Business rule validation (UX validation only)
- ❌ Assuming client validation is sufficient


## API Integration

### Endpoints
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

### Default Ports
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173` (Vite default)

### CORS Configuration
Backend is pre-configured for common frontend development ports (3000, 5173, 8080).
If frontend runs on different port, update `declaring/app/main.py` CORS_ORIGINS list.

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

### Before Making Changes

1. Check if feature spans multiple domains → use service layer APIs
2. Check if it's a business rule → belongs in backend service/model
3. Check if it affects types → update schemas.py, not models.py
4. Check if it's a business action → must publish domain event
5. Check TODO.md → your change might be part of pending work
