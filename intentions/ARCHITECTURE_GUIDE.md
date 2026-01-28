# Architecture Guide

**Companion to:** [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md)
**Version:** 1.0
**Last Updated:** October 28, 2025
**Audience:** Developers implementing hexagonal domain-driven architecture

**Related Documentation:**
- [Architecture Standards](./ARCHITECTURE_STANDARDS.md) - Mandatory rules (read first!)
- [Frontend Architecture](../../customer-ux/ARCHITECTURE.md) - How React acts as a primary adapter
- [Root CLAUDE.md](../../CLAUDE.md) - Full-stack overview

---

## Understanding Hexagonal Architecture

**This backend IS the hexagon** - the business core of the application.

Everything else (HTTP, database, event bus, React frontend) are **adapters** that connect to the hexagon through **ports**.

```
┌─────────────────────────────────────────────────────┐
│              THIS BACKEND = THE HEXAGON             │
│                  (Business Core)                    │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │        DOMAIN MODELS & BUSINESS LOGIC        │  │
│  │  - Domain entities (models.py)               │  │
│  │  - Business rules & validation               │  │
│  │  - Domain events                             │  │
│  └──────────────────────────────────────────────┘  │
│                      ▲                              │
│                      │                              │
│  ┌──────────────────────────────────────────────┐  │
│  │         SERVICE LAYER = PORTS                │  │
│  │  Public API for each domain                  │  │
│  │  (exported in __init__.py)                   │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
     ┌────────────┐     ┌────────────┐    ┌────────────┐
     │   Router   │     │ Repository │    │ Event Bus  │
     │   (HTTP)   │     │    (DB)    │    │(Analytics) │
     │  PRIMARY   │     │ SECONDARY  │    │ SECONDARY  │
     │  ADAPTER   │     │  ADAPTER   │    │  ADAPTER   │
     └────────────┘     └────────────┘    └────────────┘
             │
             ▼
     ┌────────────────┐
     │ React Frontend │
     │  (External     │
     │   Primary      │
     │   Adapter)     │
     └────────────────┘
```

**Key Concepts:**
- **Hexagon:** Contains domain models and business logic (this backend)
- **Ports:** Service layer functions - the public interface of each domain
- **Primary Adapters:** Drive the application (routers, CLI, frontend)
- **Secondary Adapters:** Driven by the application (database, external APIs)

---

This guide provides detailed explanations, complete code examples, and step-by-step guidance for implementing the hexagonal architecture defined in `ARCHITECTURE_STANDARDS.md`.

---

## Table of Contents

1. [Understanding the Model Types](#understanding-the-model-types)
2. [Complete Domain Example](#complete-domain-example)
3. [Cross-Domain Communication Patterns](#cross-domain-communication-patterns)
4. [Event System Implementation](#event-system-implementation)
5. [Migration Guide](#migration-guide)
6. [Common Patterns](#common-patterns)

---

## Understanding the Model Types

### Why Separate Models?

Different layers have different concerns:
- **Database** needs all fields including audit trails
- **Business logic** works with domain concepts
- **API** exposes only what clients need (security!)

### Database Models (`db_models.py`)

**Purpose:** Exact representation of database tables

```python
# app/intents/db_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IntentDB(Base):
    """Database model - includes ALL persistence details"""
    __tablename__ = "intents"
    
    # Business fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    output_format = Column(String, nullable=False)
    output_structure = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    
    # Audit fields (never exposed to API)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_by = Column(Integer)
    
    # Internal fields (never exposed)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    internal_notes = Column(Text)
```

### Domain Models (`models.py`)

**Purpose:** Business entities with behavior

```python
# app/intents/models.py
from pydantic import BaseModel, validator
from typing import Optional

class Intent(BaseModel):
    """Domain model - business representation"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    output_format: str
    output_structure: Optional[str] = None
    context: Optional[str] = None
    constraints: Optional[str] = None
    
    # Business validation
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('output_format')
    def output_format_must_be_valid(cls, v):
        valid_formats = ['json', 'xml', 'csv', 'markdown', 'html', 'text']
        if v.lower() not in valid_formats:
            raise ValueError(f'Output format must be one of {valid_formats}')
        return v.lower()
    
    # Business logic methods
    def is_valid(self) -> bool:
        """Business rule: is this intent valid?"""
        return bool(self.name and self.output_format)
    
    def requires_context(self) -> bool:
        """Business rule: does this intent require context?"""
        return self.context is not None and len(self.context) > 0
```

### API DTOs (`schemas.py`)

**Purpose:** API contract - what crosses the wire

```python
# app/intents/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .models import Intent

class IntentCreateRequest(BaseModel):
    """What client sends to create an intent"""
    name: str = Field(..., min_length=1, max_length=100, 
                      description="Intent name")
    description: Optional[str] = Field(None, max_length=500,
                                       description="Intent description")
    output_format: str = Field(..., description="Output format (json, xml, csv, markdown, html, text)")
    output_structure: Optional[str] = Field(None, description="Output structure")
    context: Optional[str] = Field(None, description="Context information")
    constraints: Optional[str] = Field(None, description="Constraints")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Summarize Document",
                "description": "Create a summary of the document",
                "output_format": "markdown",
                "output_structure": "bullet points",
                "context": "User is a researcher",
                "constraints": "Maximum 500 words"
            }
        }
```

class IntentUpdateRequest(BaseModel):
    """What client sends to update (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    output_format: Optional[str] = None
    output_structure: Optional[str] = None
    context: Optional[str] = None
    constraints: Optional[str] = None

class IntentResponse(BaseModel):
    """What API returns - no sensitive fields!"""
    id: int
    name: str
    description: Optional[str]
    output_format: str
    output_structure: Optional[str]
    context: Optional[str]
    constraints: Optional[str]
    # Note: No internal_notes, audit fields, etc.
    
    @classmethod
    def from_domain_model(cls, intent: Intent) -> "IntentResponse":
        """Convert domain model to API response"""
        return cls(
            id=intent.id,
            name=intent.name,
            description=intent.description,
            output_format=intent.output_format,
            output_structure=intent.output_structure,
            context=intent.context,
            constraints=intent.constraints
        )
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Summarize Document",
                "description": "Create a summary of the document",
                "output_format": "markdown",
                "output_structure": "bullet points",
                "context": "User is a researcher",
                "constraints": "Maximum 500 words"
            }
        }

class IntentListResponse(BaseModel):
    """Paginated list response"""
    intents: list[IntentResponse]
    total: int
    page: int
    page_size: int
```

#### Schema Documentation Requirements

**MANDATORY:** Schema field descriptions must match the detailed descriptions from the corresponding `*_DOMAIN.md` file.

FastAPI automatically generates OpenAPI documentation from Pydantic `Field` descriptions. These descriptions become the API specification that users see, so they must be comprehensive and match the domain model documentation.

**Why This Matters:**
- The domain model (`*_DOMAIN.md`) is the source of truth for field meanings
- FastAPI's `/docs` endpoint uses `Field` descriptions for the API specification
- Brief descriptions lose important context that exists in the domain model
- Comprehensive descriptions help API consumers understand the field's purpose and constraints

**Example: Matching Domain Model to Schema**

```python
# intentions/app/intents/INTENTS_DOMAIN.md defines:
# output_structure (string, optional): The organization and composition 
# of the result's content, independent of its technical format 
# (e.g., bullet points vs. paragraphs, table with specific columns, 
# sections with headers, or a custom template with particular fields 
# and their arrangement). The structure is maintained as text.

# ✅ CORRECT - Schema matches domain model description
class IntentCreateRequest(BaseModel):
    output_structure: Optional[str] = Field(
        None,
        description="The organization and composition of the result's content, independent of its technical format (e.g., bullet points vs. paragraphs, table with specific columns, sections with headers, or a custom template with particular fields and their arrangement). The structure is maintained as text."
    )
    context: Optional[str] = Field(
        None,
        description="Broader, dynamic information that may be retrieved from systems or external sources to inform prompt generation (e.g., user's role and permissions, recent project activity, organizational policies, current system state, or relevant historical interactions). Context is typically more fluid and situational than facts."
    )
    constraints: Optional[str] = Field(
        None,
        description="Conditions that further describe how the intent must be achieved (e.g., word limits, tone requirements, format specifications, excluded topics, or quality criteria)"
    )

# ❌ INCORRECT - Generic descriptions that lose domain context
class IntentCreateRequest(BaseModel):
    output_structure: Optional[str] = Field(None, description="Output structure")
    context: Optional[str] = Field(None, description="Intent context")
    constraints: Optional[str] = Field(None, description="Intent constraints")
```

**Best Practices:**
1. Always reference `*_DOMAIN.md` when creating or updating schema fields
2. Copy the full description from the domain model, including examples and explanations
3. If the domain model doesn't have a detailed description, add one there first
4. Review the generated API docs at `/docs` to verify descriptions are comprehensive

### Shared Value Objects (`shared/value_objects.py`)

**Purpose:** Common concepts used across domains

```python
# app/shared/value_objects.py
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime

class Money(BaseModel):
    """Monetary value - immutable value object"""
    amount: Decimal
    currency: str = "USD"
    
    class Config:
        frozen = True  # Immutable
    
    @validator('currency')
    def currency_must_be_valid(cls, v):
        valid = ['USD', 'EUR', 'GBP', 'JPY']
        if v not in valid:
            raise ValueError(f'Currency must be one of {valid}')
        return v
    
    @validator('amount')
    def amount_must_have_two_decimals(cls, v):
        return round(v, 2)
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money values"""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """Multiply money by a factor"""
        return Money(amount=self.amount * factor, currency=self.currency)

class Address(BaseModel):
    """Physical address value object"""
    street: str
    city: str
    postal_code: str
    country: str
    
    class Config:
        frozen = True
    
    def format_multiline(self) -> str:
        """Format address for display"""
        return f"{self.street}\n{self.city}, {self.postal_code}\n{self.country}"

class DateRange(BaseModel):
    """Time period value object"""
    start_date: datetime
    end_date: datetime
    
    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    def contains(self, date: datetime) -> bool:
        """Check if date is within range"""
        return self.start_date <= date <= self.end_date
    
    def duration_days(self) -> int:
        """Get duration in days"""
        return (self.end_date - self.start_date).days
```

---

## Complete Domain Example

### Intents Domain - Full Implementation

```
app/intents/
├── __init__.py
├── models.py
├── schemas.py
├── service.py
├── repository.py
├── router.py
└── events.py
```

#### `__init__.py` - Public API

```python
"""
Intents domain - Public API

Only import these functions/classes from other domains.
Internal implementation details are not exported.
"""
from .service import (
    get_intent,
    get_all_intents,
    create_intent,
    update_intent,
    delete_intent,
    search_intents,
)
from .schemas import (
    IntentResponse,
    IntentCreateRequest,
    IntentUpdateRequest,
    IntentListResponse,
)

__all__ = [
    # Service functions (public API)
    "get_intent",
    "get_all_intents",
    "create_intent",
    "update_intent",
    "delete_intent",
    "search_intents",
    # DTOs (API contract)
    "IntentResponse",
    "IntentCreateRequest",
    "IntentUpdateRequest",
    "IntentListResponse",
]
```

#### `service.py` - Business Logic

```python
"""Intent service layer - business logic and public API"""
from typing import List, Optional
from datetime import datetime
from app.shared.events import event_bus
from app.shared.logging_config import logger
from .models import Intent
from .schemas import IntentCreateRequest, IntentUpdateRequest
from .repository import intent_repository
from .events import IntentCreatedEvent, IntentUpdatedEvent, IntentDeletedEvent, IntentViewedEvent

async def get_intent(intent_id: int, viewer_user_id: Optional[int] = None) -> Optional[Intent]:
    """
    Get intent by ID - public API for other domains.
    
    Args:
        intent_id: Intent ID to retrieve
        viewer_user_id: Optional user ID for analytics
    
    Returns:
        Intent if found, None otherwise
    """
    intent = await intent_repository.get(intent_id)
    
    if intent:
        # Publish view event for analytics
        await event_bus.publish(IntentViewedEvent(
            intent_id=intent.id,
            user_id=viewer_user_id,
            viewed_at=datetime.utcnow()
        ))
    
    return intent

async def get_all_intents() -> List[Intent]:
    """Get all available intents - public API"""
    return await intent_repository.get_all()

async def create_intent(request: IntentCreateRequest) -> Intent:
    """
    Create new intent - public API.
    
    Business rules:
    - Name must not be empty
    - Output format must be valid
    
    Publishes: IntentCreatedEvent
    """
    # Create domain model (validation happens here)
    intent = Intent(
        name=request.name,
        description=request.description,
        output_format=request.output_format,
        output_structure=request.output_structure,
        context=request.context,
        constraints=request.constraints
    )
    
    # Additional business validation
    if not intent.is_valid():
        raise ValueError("Cannot create intent that is not valid")
    
    # Persist
    intent = await intent_repository.create(intent)
    
    # ✅ MANDATORY: Publish domain event
    await event_bus.publish(IntentCreatedEvent(
        intent_id=intent.id,
        name=intent.name,
        output_format=intent.output_format,
        created_at=datetime.utcnow()
    ))
    
    logger.info("Intent created", extra={
        'intent_id': intent.id,
        'intent_name': intent.name,
        'output_format': intent.output_format
    })
    
    return intent

async def update_intent(intent_id: int, request: IntentUpdateRequest) -> Intent:
    """
    Update intent - public API.
    
    Publishes: IntentUpdatedEvent
    """
    intent = await intent_repository.get(intent_id)
    if not intent:
        raise ValueError("Intent not found")
    
    # Track what changed for event
    updated_fields = []
    
    if request.name is not None:
        intent.name = request.name
        updated_fields.append("name")
    
    if request.description is not None:
        intent.description = request.description
        updated_fields.append("description")
    
    if request.output_format is not None:
        intent.output_format = request.output_format
        updated_fields.append("output_format")
    
    if request.output_structure is not None:
        intent.output_structure = request.output_structure
        updated_fields.append("output_structure")
    
    if request.context is not None:
        intent.context = request.context
        updated_fields.append("context")
    
    if request.constraints is not None:
        intent.constraints = request.constraints
        updated_fields.append("constraints")
    
    # Business validation after updates
    if not intent.is_valid():
        raise ValueError("Intent cannot be updated - invalid state")
    
    # Persist
    intent = await intent_repository.update(intent)
    
    # ✅ MANDATORY: Publish domain event
    await event_bus.publish(IntentUpdatedEvent(
        intent_id=intent.id,
        updated_fields=updated_fields,
        updated_at=datetime.utcnow()
    ))
    
    logger.info("Intent updated", extra={
        'intent_id': intent.id,
        'updated_fields': updated_fields
    })
    
    return intent

async def delete_intent(intent_id: int) -> None:
    """
    Delete intent - public API.
    
    Publishes: IntentDeletedEvent
    """
    # Verify exists
    intent = await intent_repository.get(intent_id)
    if not intent:
        raise ValueError("Intent not found")
    
    # Delete
    await intent_repository.delete(intent_id)
    
    # ✅ MANDATORY: Publish domain event
    await event_bus.publish(IntentDeletedEvent(
        intent_id=intent_id,
        deleted_at=datetime.utcnow()
    ))
    
    logger.info("Intent deleted", extra={'intent_id': intent_id})

async def search_intents(
    name: Optional[str] = None,
    output_format: Optional[str] = None,
    has_context: Optional[bool] = None
) -> List[Intent]:
    """Search intents with filters - public API"""
    return await intent_repository.search(
        name=name,
        output_format=output_format,
        has_context=has_context
    )
```

#### `repository.py` - Data Access

```python
"""Intent repository - data access layer"""
from typing import List, Optional
from .models import Intent

# Temporary in-memory storage (replace with real DB)
intents_db: List[Intent] = []
intent_id_counter = 1

class IntentRepository:
    """Intent data access layer - converts between DB and domain models"""
    
    async def get(self, intent_id: int) -> Optional[Intent]:
        """Get intent by ID"""
        for intent in intents_db:
            if intent.id == intent_id:
                return intent
        return None
    
    async def get_all(self) -> List[Intent]:
        """Get all intents"""
        return intents_db.copy()
    
    async def create(self, intent: Intent) -> Intent:
        """
        Create new intent.
        
        In real implementation:
        - Convert Intent → IntentDB
        - Save to database
        - Convert IntentDB → Intent
        - Return Intent
        """
        global intent_id_counter
        intent.id = intent_id_counter
        intent_id_counter += 1
        intents_db.append(intent)
        return intent
    
    async def update(self, intent: Intent) -> Intent:
        """Update existing intent"""
        for index, existing_intent in enumerate(intents_db):
            if existing_intent.id == intent.id:
                intents_db[index] = intent
                return intent
        raise ValueError("Intent not found")
    
    async def delete(self, intent_id: int) -> None:
        """Delete intent"""
        global intents_db
        intents_db = [intent for intent in intents_db if intent.id != intent_id]
    
    async def search(
        self,
        name: Optional[str] = None,
        output_format: Optional[str] = None,
        has_context: Optional[bool] = None
    ) -> List[Intent]:
        """Search intents with filters"""
        results = intents_db.copy()
        
        if name:
            results = [intent for intent in results 
                      if name.lower() in intent.name.lower()]
        
        if output_format:
            results = [intent for intent in results 
                      if intent.output_format.lower() == output_format.lower()]
        
        if has_context is not None:
            results = [intent for intent in results 
                      if (intent.context is not None and len(intent.context) > 0) == has_context]
        
        return results

# Singleton instance
intent_repository = IntentRepository()
```

#### `router.py` - HTTP Endpoints

```python
"""Intent HTTP endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.shared.logging_config import logger
from . import service as intent_service
from .schemas import (
    IntentResponse,
    IntentCreateRequest,
    IntentUpdateRequest,
    IntentListResponse
)

router = APIRouter(
    prefix="/intents",
    tags=["intents"],
)

@router.get("", response_model=List[IntentResponse])
async def get_intents():
    """Get all intents"""
    try:
        intents = await intent_service.get_all_intents()
        return [IntentResponse.from_domain_model(intent) for intent in intents]
    except Exception as e:
        logger.error("Failed to get intents", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{intent_id}", response_model=IntentResponse)
async def get_intent(intent_id: int):
    """Get specific intent by ID"""
    try:
        intent = await intent_service.get_intent(intent_id)
        if not intent:
            raise HTTPException(status_code=404, detail="Intent not found")
        return IntentResponse.from_domain_model(intent)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get intent {intent_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", response_model=IntentResponse, status_code=201)
async def create_intent(request: IntentCreateRequest):
    """Create new intent"""
    try:
        intent = await intent_service.create_intent(request)
        return IntentResponse.from_domain_model(intent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create intent", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{intent_id}", response_model=IntentResponse)
async def update_intent(intent_id: int, request: IntentUpdateRequest):
    """Update existing intent"""
    try:
        intent = await intent_service.update_intent(intent_id, request)
        return IntentResponse.from_domain_model(intent)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update intent {intent_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{intent_id}", status_code=204)
async def delete_intent(intent_id: int):
    """Delete intent"""
    try:
        await intent_service.delete_intent(intent_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete intent {intent_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/query", response_model=List[IntentResponse])
async def search_intents(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    output_format: Optional[str] = Query(None, description="Filter by output format"),
    has_context: Optional[bool] = Query(None, description="Filter by whether context is present")
):
    """Search intents with filters"""
    try:
        intents = await intent_service.search_intents(
            name=name,
            output_format=output_format,
            has_context=has_context
        )
        return [IntentResponse.from_domain_model(intent) for intent in intents]
    except Exception as e:
        logger.error("Failed to search intents", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### `events.py` - Domain Events

```python
"""Intent domain events for analytics and notifications"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.shared.events import DomainEvent

@dataclass
class IntentCreatedEvent(DomainEvent):
    """Published when an intent is created"""
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

@dataclass
class IntentUpdatedEvent(DomainEvent):
    """Published when an intent is updated"""
    intent_id: int
    updated_fields: list[str]
    updated_at: datetime
    
    def __init__(self, intent_id: int, updated_fields: list[str], updated_at: datetime):
        self.event_type = "intent.updated"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.updated_fields = updated_fields
        self.updated_at = updated_at

@dataclass
class IntentDeletedEvent(DomainEvent):
    """Published when an intent is deleted"""
    intent_id: int
    deleted_at: datetime
    
    def __init__(self, intent_id: int, deleted_at: datetime):
        self.event_type = "intent.deleted"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.deleted_at = deleted_at

@dataclass
class IntentViewedEvent(DomainEvent):
    """Published when an intent is viewed - for analytics"""
    intent_id: int
    user_id: Optional[int]
    viewed_at: datetime
    
    def __init__(self, intent_id: int, user_id: Optional[int], viewed_at: datetime):
        self.event_type = "intent.viewed"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.user_id = user_id
        self.viewed_at = viewed_at
```

---

## Cross-Domain Communication Patterns

### Pattern 1: Simple Data Retrieval

```python
# app/orders/service.py
"""Order service needs to validate user exists"""
from app.users import service as user_service

async def create_order(user_id: int, intent_id: int) -> Order:
    # ✅ Call through service layer
    user = await user_service.get_user(user_id)
    if not user:
        raise ValueError("User not found")
    
    # Continue with order creation...
```

### Pattern 2: Validation Across Domains

```python
# app/orders/service.py
"""Order service validates across users and intents"""
from app.users import service as user_service
from app.intents import service as intent_service

async def create_order(user_id: int, intent_id: int, quantity: int) -> Order:
    # Validate user
    user_exists = await user_service.validate_user_exists(user_id)
    if not user_exists:
        raise ValueError("Invalid user")
    
    # Validate intent
    intent = await intent_service.get_intent(intent_id)
    if not intent:
        raise ValueError("Intent not found")
    
    if not intent.is_valid():
        raise ValueError("Intent not valid")
    
    # Create order
    order = Order(
        user_id=user_id,
        intent_id=intent_id,
        quantity=quantity
    )
    
    order = await order_repository.create(order)
    
    # Publish event
    await event_bus.publish(OrderCreatedEvent(...))
    
    return order
```

### Pattern 3: Enriched Responses

```python
# app/orders/schemas.py
"""Order response with enriched data from other domains"""
from pydantic import BaseModel

class OrderDetailResponse(BaseModel):
    """Order with user and intent details"""
    id: int
    # User information (from users domain)
    user_id: int
    username: str
    user_email: str
    # Intent information (from intents domain)
    intent_id: int
    intent_name: str
    intent_output_format: str
    # Order information
    quantity: int

# app/orders/service.py
from app.users import service as user_service
from app.intents import service as intent_service

async def get_order_detail(order_id: int) -> OrderDetailResponse:
    """Get order with enriched data"""
    order = await order_repository.get(order_id)
    
    # Fetch related data from other domains
    user = await user_service.get_user(order.user_id)
    intent = await intent_service.get_intent(order.intent_id)
    
    # Compose enriched response
    return OrderDetailResponse(
        id=order.id,
        user_id=user.id,
        username=user.username,
        user_email=user.email,
        intent_id=intent.id,
        intent_name=intent.name,
        intent_output_format=intent.output_format,
        quantity=order.quantity
    )
```

---

## Event System Implementation

### Setting Up Event Bus

```python
# app/shared/events.py
"""Event bus for domain events"""
from typing import Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime
from abc import ABC
from app.shared.logging_config import logger

@dataclass
class DomainEvent(ABC):
    """Base class for all domain events"""
    timestamp: datetime
    event_type: str
    
    def to_dict(self) -> dict:
        """Serialize event for logging/analytics"""
        result = {'timestamp': self.timestamp.isoformat(), 'event_type': self.event_type}
        # Add all other attributes
        for key, value in self.__dict__.items():
            if key not in ['timestamp', 'event_type']:
                result[key] = str(value) if hasattr(value, '__str__') else value
        return result

class EventBus:
    """Event bus for publishing and subscribing to domain events"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._global_handlers: List[Callable] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe handler to specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler subscribed", extra={
            'event_type': event_type,
            'handler': handler.__name__
        })
    
    def subscribe_all(self, handler: Callable):
        """Subscribe handler to all events"""
        self._global_handlers.append(handler)
        logger.info(f"Global handler subscribed", extra={
            'handler': handler.__name__
        })
    
    async def publish(self, event: DomainEvent):
        """
        Publish domain event.
        - Logs event for analytics
        - Notifies all subscribers
        """
        # Always log for analytics
        logger.info(
            f"Domain event: {event.event_type}",
            extra={
                'event_type': event.event_type,
                'event_data': event.to_dict(),
                'event_category': 'domain_event',
                'analytics': True
            }
        )
        
        # Notify type-specific handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    f"Event handler failed",
                    extra={
                        'handler': handler.__name__,
                        'event_type': event.event_type,
                        'error': str(e)
                    },
                    exc_info=True
                )
        
        # Notify global handlers
        for handler in self._global_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    f"Global event handler failed",
                    extra={
                        'handler': handler.__name__,
                        'event_type': event.event_type,
                        'error': str(e)
                    },
                    exc_info=True
                )

# Global event bus instance
event_bus = EventBus()
```

### Analytics Event Handlers

```python
# app/analytics/handlers.py
"""Analytics event handlers"""
from app.shared.events import event_bus, DomainEvent
from app.shared.logging_config import logger

async def track_all_events(event: DomainEvent):
    """
    Track all events for analytics.
    This is where you'd send to external analytics services.
    """
    logger.info(
        "Analytics tracking",
        extra={
            'analytics_event': event.event_type,
            'event_data': event.to_dict(),
            'service': 'analytics'
        }
    )
    # TODO: Send to Mixpanel, Segment, Google Analytics, etc.

async def track_intent_events(event: DomainEvent):
    """Track intent-specific events"""
    if hasattr(event, 'intent_id'):
        logger.info(
            "Intent analytics",
            extra={
                'analytics_category': 'intent',
                'intent_id': event.intent_id,
                'event_type': event.event_type
            }
        )

async def track_user_behavior(event: DomainEvent):
    """Track user behavior for product analytics"""
    if hasattr(event, 'user_id') and event.user_id:
        logger.info(
            "User behavior tracking",
            extra={
                'analytics_category': 'user_behavior',
                'user_id': event.user_id,
                'action': event.event_type
            }
        )

def setup_analytics_handlers():
    """Register analytics handlers - call during app startup"""
    # Track everything
    event_bus.subscribe_all(track_all_events)
    
    # Specific handlers
    event_bus.subscribe("intent.created", track_intent_events)
    event_bus.subscribe("intent.updated", track_intent_events)
    event_bus.subscribe("intent.deleted", track_intent_events)
    event_bus.subscribe("intent.viewed", track_intent_events)
    event_bus.subscribe("intent.viewed", track_user_behavior)
    
    logger.info("Analytics handlers registered")
```

### Registering Handlers on Startup

```python
# app/main.py
from app.analytics.handlers import setup_analytics_handlers

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("Application starting")
    
    # Register analytics handlers
    setup_analytics_handlers()
    
    logger.info("Application ready")
```

---

## Migration Guide

### Step-by-Step: Refactor Existing Code

#### Step 1: Create Domain Folder Structure

```bash
mkdir -p app/intents app/users app/shared
touch app/intents/{__init__.py,models.py,schemas.py,service.py,repository.py,router.py,events.py}
touch app/users/{__init__.py,models.py,schemas.py,service.py,repository.py,router.py,events.py}
```

#### Step 2: Create Shared Event System

1. Create `app/shared/events.py` with EventBus (see above)
2. Create `app/analytics/handlers.py` for analytics

#### Step 3: Split Models

**Before (app/models.py):**
```python
class Intent(BaseModel):
    id: Optional[int] = None
    name: str
    output_format: str
```

**After:**
```python
# app/intents/models.py - Domain model
class Intent(BaseModel):
    id: Optional[int] = None
    name: str
    output_format: str
    
    @validator('output_format')
    def output_format_must_be_valid(cls, v):
        valid_formats = ['json', 'xml', 'csv', 'markdown', 'html', 'text']
        if v.lower() not in valid_formats:
            raise ValueError(f'Output format must be one of {valid_formats}')
        return v.lower()

# app/intents/schemas.py - API DTOs
class IntentCreateRequest(BaseModel):
    name: str
    output_format: str

class IntentResponse(BaseModel):
    id: int
    name: str
    output_format: str
```

#### Step 4: Extract Service Layer

**Before (logic in router):**
```python
@router.post("/intents")
async def create_intent(intent: Intent):
    intent.id = generate_id()
    intents_db.append(intent)
    return intent
```

**After:**
```python
# app/intents/service.py
async def create_intent(request: IntentCreateRequest) -> Intent:
    intent = Intent(name=request.name, output_format=request.output_format)
    intent = await intent_repository.create(intent)
    await event_bus.publish(IntentCreatedEvent(...))
    return intent

# app/intents/router.py
@router.post("/intents", response_model=IntentResponse)
async def create_intent(request: IntentCreateRequest):
    intent = await intent_service.create_intent(request)
    return IntentResponse.from_domain_model(intent)
```

#### Step 5: Create Repository Layer

```python
# app/intents/repository.py
class IntentRepository:
    async def create(self, intent: Intent) -> Intent:
        # Data access logic
        pass

intent_repository = IntentRepository()
```

#### Step 6: Define and Publish Events

```python
# app/intents/events.py
@dataclass
class IntentCreatedEvent(DomainEvent):
    intent_id: int
    name: str
    output_format: str
    created_at: datetime
    
    def __init__(self, ...):
        self.event_type = "intent.created"
        self.timestamp = datetime.utcnow()
        # ... set fields

# app/intents/service.py
await event_bus.publish(IntentCreatedEvent(...))
```

#### Step 7: Update Imports

```python
# app/main.py
from app.intents.router import router as intents_router
from app.users.router import router as users_router

app.include_router(intents_router)
app.include_router(users_router)
```

#### Step 8: Export Public API

```python
# app/intents/__init__.py
from .service import get_intent, create_intent, update_intent, delete_intent
from .schemas import IntentResponse, IntentCreateRequest

__all__ = ["get_intent", "create_intent", "update_intent", "delete_intent",
           "IntentResponse", "IntentCreateRequest"]
```

---

## Common Patterns

### Pattern: Pagination

```python
# app/shared/value_objects.py
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int

# app/intents/service.py
async def get_intents_paginated(pagination: PaginationParams) -> PaginatedResponse:
    intents, total = await intent_repository.get_paginated(
        offset=pagination.offset,
        limit=pagination.page_size
    )
    return PaginatedResponse(
        items=intents,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size
    )
```

### Pattern: Soft Delete

```python
# app/intents/service.py
async def delete_intent(intent_id: int, soft: bool = True) -> None:
    """Delete intent (soft delete by default)"""
    if soft:
        intent = await intent_repository.get(intent_id)
        intent.is_deleted = True
        await intent_repository.update(intent)
    else:
        await intent_repository.delete(intent_id)
    
    await event_bus.publish(IntentDeletedEvent(
        intent_id=intent_id,
        deleted_at=datetime.utcnow(),
        soft_delete=soft
    ))
```

### Pattern: Audit Trail

```python
# app/intents/events.py
@dataclass
class IntentAuditEvent(DomainEvent):
    """Audit trail for intent changes"""
    intent_id: int
    action: str  # 'created', 'updated', 'deleted'
    changed_by: int  # User ID
    changes: dict
    timestamp: datetime

# app/intents/service.py
async def update_intent(intent_id: int, request: IntentUpdateRequest, user_id: int) -> Intent:
    # ... update logic
    
    await event_bus.publish(IntentAuditEvent(
        intent_id=intent.id,
        action='updated',
        changed_by=user_id,
        changes={'fields': updated_fields},
        timestamp=datetime.utcnow()
    ))
```

---

## Summary

This guide provides practical implementation details for the architecture defined in `ARCHITECTURE_STANDARDS.md`. Key takeaways:

1. **Separate models** by concern (DB, domain, API)
2. **Service layer** is the public API between domains
3. **Always publish events** for business actions
4. **Repository** converts between DB and domain models
5. **Router** only handles HTTP concerns

For questions or clarifications, refer to the core guidelines or consult the architecture team.

