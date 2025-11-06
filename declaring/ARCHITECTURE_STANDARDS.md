# Architecture Standards

**Version:** 1.0
**Last Updated:** October 28, 2025
**Status:** MANDATORY - All code changes must follow these standards
**Audience:** Experts familiar with domain-driven design and hexagonal architecture

For detailed examples and explanations, see [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)

**Related Documentation:**
- [Frontend Architecture](../../reacting/ARCHITECTURE.md) - How the React frontend acts as a primary adapter
- [Root CLAUDE.md](../../CLAUDE.md) - Full-stack architecture overview

---

## Hexagonal Architecture Overview

**This backend IS the hexagon (the business core).**

```
┌─────────────────────────────────────────────┐
│    THIS BACKEND = THE HEXAGON               │
│    (Business Core)                          │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Domain Models & Business Logic      │  │
│  │  Service Layer = PORTS               │  │
│  └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │  HTTP    │  │ Database │  │  Events  │
   │ (Router) │  │  (Repo)  │  │  (Bus)   │
   │ PRIMARY  │  │SECONDARY │  │SECONDARY │
   │ ADAPTER  │  │ ADAPTER  │  │ ADAPTER  │
   └──────────┘  └──────────┘  └──────────┘
         │
         ▼
   ┌──────────────┐
   │   React      │
   │   Frontend   │
   │ (External    │
   │  Adapter)    │
   └──────────────┘
```

**Key Terminology:**
- **Hexagon (Core):** Domain models and business logic (this backend)
- **Ports:** Service layer functions - the public API of each domain
- **Primary Adapters:** Drive the application (HTTP routers, CLI, GraphQL)
- **Secondary Adapters:** Driven by the application (database, event bus, external APIs)

---

## Core Principles

1. **Hexagonal Architecture** - Business logic in the core, infrastructure at the edges
2. **Domain-First Organization** - Organize by business domain/feature, not technical layer
3. **Ports as Boundaries** - Service layer functions are the ports between domains
4. **High Cohesion, Low Coupling** - Related code together, domains independent
5. **Event-Driven Analytics** - All significant business actions publish events
6. **Separation of Concerns** - Separate models for DB, domain, and API layers

---

## Required Structure

```
app/
├── {domain}/                     # One folder per business domain
│   ├── __init__.py              # Exports public API only
│   ├── models.py                # Domain/business models
│   ├── schemas.py               # API DTOs (request/response)
│   ├── db_models.py             # Database models (ORM)
│   ├── service.py               # Business logic & public API
│   ├── repository.py            # Data access layer
│   ├── router.py                # HTTP endpoints
│   └── events.py                # Domain event definitions
│
├── shared/                       # Cross-cutting concerns only
│   ├── __init__.py
│   ├── value_objects.py         # Shared value objects (Money, Address)
│   ├── events.py                # Event bus and base types
│   ├── middleware.py
│   ├── exception_handlers.py
│   └── logging_config.py
│
└── main.py                       # Application entry point
```

---

## Layer Responsibilities (Hexagonal View)

### Service Layer (`service.py`) - THE PORTS
**This is the boundary of the hexagon - the public API.**

- Implement business logic
- Orchestrate operations
- Validate business rules
- **Publish domain events (MANDATORY)**
- Serve as public API (port) for other domains
- **Must NOT:** know about HTTP, use DTOs directly, construct SQL

### Router Layer (`router.py`) - PRIMARY ADAPTER
**HTTP adapter that drives the hexagon through its ports.**

- Define HTTP endpoints
- Validate requests using DTOs (schemas.py)
- Call service layer ports
- Serialize responses using DTOs
- **Must NOT:** contain business logic, access repository/DB, publish events

### Repository Layer (`repository.py`) - SECONDARY ADAPTER
**Database adapter driven by the hexagon.**

- Data access operations (CRUD)
- Convert DB models ↔ Domain models
- Build queries
- Transaction management
- **Must NOT:** contain business logic, publish events, know about HTTP

---

## Model Types

| Type | File | Purpose | Used By | Exposed Outside Domain |
|------|------|---------|---------|----------------------|
| **DB Models** | `db_models.py` | Database schema with ORM | Repository only | ❌ Never |
| **Domain Models** | `models.py` | Business entities with logic | Service layer | ❌ Never |
| **DTOs/Schemas** | `schemas.py` | API request/response | Router layer | ✅ Yes (API contract) |
| **Value Objects** | `shared/value_objects.py` | Common concepts (Money, Address) | Multiple domains | ✅ Yes |

**Key Rules:**
- DB models include ALL database fields (audit, soft delete, internal)
- Domain models contain business logic and validation
- DTOs define API contract, exclude sensitive data
- Value objects are immutable, defined by values not identity

### Schema Documentation Requirements

**MANDATORY:** All `Field` descriptions in `schemas.py` **MUST** match the detailed descriptions from the corresponding `*_DOMAIN.md` file.

- **Domain model documentation (`*_DOMAIN.md`) is the source of truth** for field meanings and descriptions
- FastAPI's auto-generated OpenAPI documentation uses Pydantic `Field` descriptions
- Schema field descriptions must be comprehensive and include examples, constraints, and business context from the domain model
- Brief or generic descriptions (e.g., "Intent name", "Output structure") are **NOT** acceptable if the domain model provides detailed explanations

**Example:**
```python
# ✅ CORRECT - Detailed description from domain model
output_structure: Optional[str] = Field(
    None, 
    description="The organization and composition of the result's content, independent of its technical format (e.g., bullet points vs. paragraphs, table with specific columns, sections with headers, or a custom template with particular fields and their arrangement). The structure is maintained as text."
)

# ❌ INCORRECT - Generic description
output_structure: Optional[str] = Field(None, description="Output structure")
```

### Single Source of Truth for Documentation

**MANDATORY:** `schemas.py` and `service.py` serve as single sources of truth for documentation across both API and MCP interfaces.

#### `schemas.py` - Single Source for Parameter/Field Documentation

The `schemas.py` file provides parameter and field documentation that is automatically used by multiple interfaces:

- **Pydantic `Field(description=...)`** defines parameter documentation once
- **FastAPI OpenAPI/Swagger docs** are auto-generated from Pydantic field descriptions
- **MCP tool parameter schemas** are derived from Pydantic models via JSON Schema conversion
- **Must match `*_DOMAIN.md` descriptions** (existing requirement)

**Flow:**
```
schemas.py (Field descriptions)
  ├─> FastAPI OpenAPI/Swagger docs
  └─> MCP tool parameter schemas (via JSON Schema conversion)
```

**Example:**
```python
# schemas.py - Single source of truth for parameter documentation
name: str = Field(
    ...,
    description="Name of the intent. Used to identify the work that the user wants to accomplish through AI interaction."
)
```

This description is automatically used in:
- FastAPI OpenAPI documentation
- MCP tool parameter schemas (converted to JSON Schema)

#### `service.py` - Single Source for Operation Descriptions

The `service.py` file provides operation descriptions that are used by multiple interfaces:

- **Service function docstrings** define what each operation does
- **MCP tool descriptions** use service function docstrings (for LLM consumption)
- **API endpoint descriptions** should use service docstrings (currently duplicated in router)
- **Maps 1:1** to both API endpoints and MCP tools

**Flow:**
```
service.py (function docstrings)
  ├─> MCP tool descriptions
  └─> API endpoint descriptions (should be used, currently duplicated)
```

**Example:**
```python
# service.py - Single source of truth for operation description
async def create_intent(request: IntentCreateRequest, repository: IntentRepository) -> Intent:
    """
    Create a new intent (US-000).

    Args:
        request: Intent creation request
        repository: Intent repository instance

    Returns:
        Created intent
    """
    # ... implementation
```

This docstring is used in:
- MCP tool descriptions (extracted automatically)
- Should be referenced in API endpoint descriptions (to avoid duplication)

**Benefits:**
- **DRY Principle:** Documentation defined once, used everywhere
- **Consistency:** Same descriptions across API and MCP interfaces
- **Maintainability:** Update documentation in one place
- **Hexagonal Architecture:** Service layer (port) is the source of truth for operations

---

## Inter-Domain Communication

### Communication Rules

✅ **Allowed:**
- `domain_a/router.py` → `domain_a/service.py` → `domain_b/service.py`
- Any domain → `shared/`

❌ **Forbidden:**
- `domain_a/service.py` → `domain_b/repository.py`
- `domain_a/router.py` → `domain_b/router.py`
- `domain_a/models.py` → `domain_b/models.py`
- `shared/` → any domain

### Public API Export

Each domain **MUST** export its public interface in `__init__.py`:

```python
# app/intents/__init__.py
from .service import get_intent, create_intent, update_intent, delete_intent
from .schemas import IntentResponse, IntentCreateRequest

__all__ = ["get_intent", "create_intent", "update_intent", "delete_intent",
           "IntentResponse", "IntentCreateRequest"]
```

### Cross-Domain Usage

```python
# app/orders/service.py
from app.users import service as user_service
from app.intents import service as intent_service

async def create_order(user_id: int, intent_id: int):
    user = await user_service.get_user(user_id)  # ✅ Through service API
    intent = await intent_service.get_intent(intent_id)  # ✅ Through service API
    # ... order logic
```

---

## Event-Driven Analytics

### Requirements

**MANDATORY:** Every significant business action **MUST** publish a domain event.

✅ **Requires events:**
- Create operations (user created, intent created, order placed)
- Update operations (intent updated, profile changed)
- Delete operations (intent deleted, user deactivated)
- State changes (order shipped, payment processed)
- Business actions (login, search, intent viewed)

❌ **No events:**
- Simple read operations (get, list)
- Health checks
- Internal operations

### Event Structure

```python
# app/shared/events.py
from dataclasses import dataclass
from datetime import datetime
from abc import ABC

@dataclass
class DomainEvent(ABC):
    timestamp: datetime
    event_type: str
    
    def to_dict(self) -> dict:
        return {'timestamp': self.timestamp.isoformat(), 
                'event_type': self.event_type, **self.__dict__}

class EventBus:
    def subscribe(self, event_type: str, handler: Callable): ...
    async def publish(self, event: DomainEvent): ...

event_bus = EventBus()
```

### Domain Event Definition

```python
# app/intents/events.py
from dataclasses import dataclass
from app.shared.events import DomainEvent

@dataclass
class IntentCreatedEvent(DomainEvent):
    intent_id: int
    name: str
    output_format: str
    created_at: datetime
    
    def __init__(self, intent_id: int, name: str, output_format: str, created_at: datetime):
        self.event_type = "intent.created"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.name = name
        self.output_format = output_format
        self.created_at = created_at
```

### Event Publishing

```python
# app/intents/service.py
from app.shared.events import event_bus
from .events import IntentCreatedEvent

async def create_intent(request: IntentCreateRequest) -> Intent:
    intent = await intent_repository.create(intent)
    
    # ✅ MANDATORY
    await event_bus.publish(IntentCreatedEvent(
        intent_id=intent.id, name=intent.name, 
        output_format=intent.output_format, created_at=datetime.utcnow()
    ))
    
    return intent
```

---

## Code Change Checklist

### New Feature

- [ ] Created domain folder with all required files
- [ ] Separated models: `db_models.py`, `models.py`, `schemas.py`
- [ ] Created service layer with public API
- [ ] Updated `__init__.py` with public exports
- [ ] Created domain events in `events.py`
- [ ] Service publishes events for all business actions
- [ ] Router uses DTOs from `schemas.py`
- [ ] Service uses domain models from `models.py`
- [ ] Repository converts DB ↔ domain models
- [ ] Schema field descriptions match `*_DOMAIN.md` documentation
- [ ] No cross-domain imports of internals
- [ ] Updated `main.py` to include router

### Modifying Existing Feature

- [ ] Maintained layer separation (router → service → repository)
- [ ] Used correct model type in each layer
- [ ] Published domain event if business action changed
- [ ] No business logic in router
- [ ] No HTTP concerns in service
- [ ] No direct DB access from router
- [ ] Cross-domain calls through service layer only

### Code Review

- [ ] Code in correct domain folder
- [ ] Layers properly separated
- [ ] Correct model types per layer
- [ ] Events published for business actions
- [ ] Schema field descriptions match `*_DOMAIN.md` documentation
- [ ] No sensitive data in DTOs
- [ ] No cross-domain internal imports
- [ ] Service functions exported in `__init__.py`
- [ ] Structured logging with context

---

## Quick Reference

### Data Flow

```
Client 
  ↓ JSON
Router (schemas.py - DTOs)
  ↓ DTOs
Service (models.py - Domain Models, events.py - Events)
  ↓ Domain Models
Repository (db_models.py - DB Models)
  ↓ SQL/ORM
Database
```

### Import Rules

```python
# ✅ ALLOWED
from app.shared.events import event_bus                    # Any domain → shared
from app.users import service as user_service              # Domain → other domain's service
from .models import User                                    # Within same domain
from .repository import user_repository                     # Service → repository

# ❌ FORBIDDEN
from app.users.repository import user_repository           # Cross-domain repository
from app.users.models import User                          # Cross-domain domain model
from app.intents import router                             # Cross-domain router
```

### Dependency Direction

```
Allowed:  Domain → shared
Allowed:  Domain A Service → Domain B Service
Forbidden: shared → Domain
Forbidden: Domain A Internal → Domain B Internal
```

---

## For Detailed Guidance

See [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) for:
- Complete code examples
- Step-by-step migration guide
- Detailed explanations
- Common patterns
- Full domain implementation example

---

**Document Status:** ACTIVE  
**Enforcement:** MANDATORY for all code changes

