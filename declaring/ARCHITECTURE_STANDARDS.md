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
# app/items/__init__.py
from .service import get_item, create_item, update_item, delete_item
from .schemas import ItemResponse, ItemCreateRequest

__all__ = ["get_item", "create_item", "update_item", "delete_item",
           "ItemResponse", "ItemCreateRequest"]
```

### Cross-Domain Usage

```python
# app/orders/service.py
from app.users import service as user_service
from app.items import service as item_service

async def create_order(user_id: int, item_id: int):
    user = await user_service.get_user(user_id)  # ✅ Through service API
    item = await item_service.get_item(item_id)  # ✅ Through service API
    # ... order logic
```

---

## Event-Driven Analytics

### Requirements

**MANDATORY:** Every significant business action **MUST** publish a domain event.

✅ **Requires events:**
- Create operations (user created, item created, order placed)
- Update operations (item updated, profile changed)
- Delete operations (item deleted, user deactivated)
- State changes (order shipped, payment processed)
- Business actions (login, search, item viewed)

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
# app/items/events.py
from dataclasses import dataclass
from app.shared.events import DomainEvent

@dataclass
class ItemCreatedEvent(DomainEvent):
    item_id: int
    name: str
    price: Decimal
    created_at: datetime
    
    def __init__(self, item_id: int, name: str, price: Decimal, created_at: datetime):
        self.event_type = "item.created"
        self.timestamp = datetime.utcnow()
        self.item_id = item_id
        self.name = name
        self.price = price
        self.created_at = created_at
```

### Event Publishing

```python
# app/items/service.py
from app.shared.events import event_bus
from .events import ItemCreatedEvent

async def create_item(request: ItemCreateRequest) -> Item:
    item = await item_repository.create(item)
    
    # ✅ MANDATORY
    await event_bus.publish(ItemCreatedEvent(
        item_id=item.id, name=item.name, 
        price=item.price, created_at=datetime.utcnow()
    ))
    
    return item
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
from app.items import router                               # Cross-domain router
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

