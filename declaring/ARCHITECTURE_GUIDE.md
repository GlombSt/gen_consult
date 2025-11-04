# Architecture Guide

**Companion to:** [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md)
**Version:** 1.0
**Last Updated:** October 28, 2025
**Audience:** Developers implementing hexagonal domain-driven architecture

**Related Documentation:**
- [Architecture Standards](./ARCHITECTURE_STANDARDS.md) - Mandatory rules (read first!)
- [Frontend Architecture](../../reacting/ARCHITECTURE.md) - How React acts as a primary adapter
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
# app/items/db_models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ItemDB(Base):
    """Database model - includes ALL persistence details"""
    __tablename__ = "items"
    
    # Business fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    
    # Audit fields (never exposed to API)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_by = Column(Integer)
    
    # Internal fields (never exposed)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    internal_notes = Column(String)
    cost_price = Column(Float)  # Supplier cost - sensitive!
```

### Domain Models (`models.py`)

**Purpose:** Business entities with behavior

```python
# app/items/models.py
from pydantic import BaseModel, validator
from typing import Optional
from decimal import Decimal

class Item(BaseModel):
    """Domain model - business representation"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: Decimal
    is_available: bool = True
    
    # Business validation
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    # Business logic methods
    def calculate_tax(self, tax_rate: Decimal) -> Decimal:
        """Calculate tax for this item"""
        return self.price * tax_rate
    
    def calculate_total_with_tax(self, tax_rate: Decimal) -> Decimal:
        """Calculate total price including tax"""
        return self.price + self.calculate_tax(tax_rate)
    
    def mark_unavailable(self) -> None:
        """Business operation: mark as unavailable"""
        self.is_available = False
    
    def can_be_sold(self) -> bool:
        """Business rule: can this item be sold?"""
        return self.is_available and self.price > 0
```

### API DTOs (`schemas.py`)

**Purpose:** API contract - what crosses the wire

```python
# app/items/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from .models import Item

class ItemCreateRequest(BaseModel):
    """What client sends to create an item"""
    name: str = Field(..., min_length=1, max_length=100, 
                      description="Item name")
    description: Optional[str] = Field(None, max_length=500,
                                       description="Item description")
    price: Decimal = Field(..., gt=0, description="Item price (must be positive)")
    is_available: bool = Field(True, description="Is item available for sale")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Laptop",
                "description": "High-performance laptop",
                "price": 999.99,
                "is_available": True
            }
        }
```

class ItemUpdateRequest(BaseModel):
    """What client sends to update (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[Decimal] = Field(None, gt=0)
    is_available: Optional[bool] = None

class ItemResponse(BaseModel):
    """What API returns - no sensitive fields!"""
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    is_available: bool
    # Note: No cost_price, internal_notes, audit fields, etc.
    
    @classmethod
    def from_domain_model(cls, item: Item) -> "ItemResponse":
        """Convert domain model to API response"""
        return cls(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            is_available=item.is_available
        )
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop",
                "price": 999.99,
                "is_available": True
            }
        }

class ItemListResponse(BaseModel):
    """Paginated list response"""
    items: list[ItemResponse]
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
# declaring/app/intents/INTENTS_DOMAIN.md defines:
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

### Items Domain - Full Implementation

```
app/items/
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
Items domain - Public API

Only import these functions/classes from other domains.
Internal implementation details are not exported.
"""
from .service import (
    get_item,
    get_all_items,
    create_item,
    update_item,
    delete_item,
    search_items,
)
from .schemas import (
    ItemResponse,
    ItemCreateRequest,
    ItemUpdateRequest,
    ItemListResponse,
)

__all__ = [
    # Service functions (public API)
    "get_item",
    "get_all_items",
    "create_item",
    "update_item",
    "delete_item",
    "search_items",
    # DTOs (API contract)
    "ItemResponse",
    "ItemCreateRequest",
    "ItemUpdateRequest",
    "ItemListResponse",
]
```

#### `service.py` - Business Logic

```python
"""Item service layer - business logic and public API"""
from typing import List, Optional
from datetime import datetime
from app.shared.events import event_bus
from app.shared.logging_config import logger
from .models import Item
from .schemas import ItemCreateRequest, ItemUpdateRequest
from .repository import item_repository
from .events import ItemCreatedEvent, ItemUpdatedEvent, ItemDeletedEvent, ItemViewedEvent

async def get_item(item_id: int, viewer_user_id: Optional[int] = None) -> Optional[Item]:
    """
    Get item by ID - public API for other domains.
    
    Args:
        item_id: Item ID to retrieve
        viewer_user_id: Optional user ID for analytics
    
    Returns:
        Item if found, None otherwise
    """
    item = await item_repository.get(item_id)
    
    if item:
        # Publish view event for analytics
        await event_bus.publish(ItemViewedEvent(
            item_id=item.id,
            user_id=viewer_user_id,
            viewed_at=datetime.utcnow()
        ))
    
    return item

async def get_all_items() -> List[Item]:
    """Get all available items - public API"""
    return await item_repository.get_all()

async def create_item(request: ItemCreateRequest) -> Item:
    """
    Create new item - public API.
    
    Business rules:
    - Name must not be empty
    - Price must be positive
    
    Publishes: ItemCreatedEvent
    """
    # Create domain model (validation happens here)
    item = Item(
        name=request.name,
        description=request.description,
        price=request.price,
        is_available=request.is_available
    )
    
    # Additional business validation
    if not item.can_be_sold():
        raise ValueError("Cannot create item that cannot be sold")
    
    # Persist
    item = await item_repository.create(item)
    
    # ✅ MANDATORY: Publish domain event
    await event_bus.publish(ItemCreatedEvent(
        item_id=item.id,
        name=item.name,
        price=item.price,
        created_at=datetime.utcnow()
    ))
    
    logger.info("Item created", extra={
        'item_id': item.id,
        'item_name': item.name,
        'price': float(item.price)
    })
    
    return item

async def update_item(item_id: int, request: ItemUpdateRequest) -> Item:
    """
    Update item - public API.
    
    Publishes: ItemUpdatedEvent
    """
    item = await item_repository.get(item_id)
    if not item:
        raise ValueError("Item not found")
    
    # Track what changed for event
    updated_fields = []
    
    if request.name is not None:
        item.name = request.name
        updated_fields.append("name")
    
    if request.price is not None:
        item.price = request.price
        updated_fields.append("price")
    
    if request.description is not None:
        item.description = request.description
        updated_fields.append("description")
    
    if request.is_available is not None:
        item.is_available = request.is_available
        updated_fields.append("is_available")
    
    # Business validation after updates
    if not item.can_be_sold() and item.is_available:
        raise ValueError("Item cannot be marked available - invalid price")
    
    # Persist
    item = await item_repository.update(item)
    
    # ✅ MANDATORY: Publish domain event
    await event_bus.publish(ItemUpdatedEvent(
        item_id=item.id,
        updated_fields=updated_fields,
        updated_at=datetime.utcnow()
    ))
    
    logger.info("Item updated", extra={
        'item_id': item.id,
        'updated_fields': updated_fields
    })
    
    return item

async def delete_item(item_id: int) -> None:
    """
    Delete item - public API.
    
    Publishes: ItemDeletedEvent
    """
    # Verify exists
    item = await item_repository.get(item_id)
    if not item:
        raise ValueError("Item not found")
    
    # Delete
    await item_repository.delete(item_id)
    
    # ✅ MANDATORY: Publish domain event
    await event_bus.publish(ItemDeletedEvent(
        item_id=item_id,
        deleted_at=datetime.utcnow()
    ))
    
    logger.info("Item deleted", extra={'item_id': item_id})

async def search_items(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available_only: bool = False
) -> List[Item]:
    """Search items with filters - public API"""
    return await item_repository.search(
        name=name,
        min_price=min_price,
        max_price=max_price,
        available_only=available_only
    )
```

#### `repository.py` - Data Access

```python
"""Item repository - data access layer"""
from typing import List, Optional
from .models import Item

# Temporary in-memory storage (replace with real DB)
items_db: List[Item] = []
item_id_counter = 1

class ItemRepository:
    """Item data access layer - converts between DB and domain models"""
    
    async def get(self, item_id: int) -> Optional[Item]:
        """Get item by ID"""
        for item in items_db:
            if item.id == item_id:
                return item
        return None
    
    async def get_all(self) -> List[Item]:
        """Get all items"""
        return items_db.copy()
    
    async def create(self, item: Item) -> Item:
        """
        Create new item.
        
        In real implementation:
        - Convert Item → ItemDB
        - Save to database
        - Convert ItemDB → Item
        - Return Item
        """
        global item_id_counter
        item.id = item_id_counter
        item_id_counter += 1
        items_db.append(item)
        return item
    
    async def update(self, item: Item) -> Item:
        """Update existing item"""
        for index, existing_item in enumerate(items_db):
            if existing_item.id == item.id:
                items_db[index] = item
                return item
        raise ValueError("Item not found")
    
    async def delete(self, item_id: int) -> None:
        """Delete item"""
        global items_db
        items_db = [item for item in items_db if item.id != item_id]
    
    async def search(
        self,
        name: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        available_only: bool = False
    ) -> List[Item]:
        """Search items with filters"""
        results = items_db.copy()
        
        if name:
            results = [item for item in results 
                      if name.lower() in item.name.lower()]
        
        if min_price is not None:
            results = [item for item in results 
                      if item.price >= min_price]
        
        if max_price is not None:
            results = [item for item in results 
                      if item.price <= max_price]
        
        if available_only:
            results = [item for item in results 
                      if item.is_available]
        
        return results

# Singleton instance
item_repository = ItemRepository()
```

#### `router.py` - HTTP Endpoints

```python
"""Item HTTP endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.shared.logging_config import logger
from . import service as item_service
from .schemas import (
    ItemResponse,
    ItemCreateRequest,
    ItemUpdateRequest,
    ItemListResponse
)

router = APIRouter(
    prefix="/items",
    tags=["items"],
)

@router.get("", response_model=List[ItemResponse])
async def get_items():
    """Get all items"""
    try:
        items = await item_service.get_all_items()
        return [ItemResponse.from_domain_model(item) for item in items]
    except Exception as e:
        logger.error("Failed to get items", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get specific item by ID"""
    try:
        item = await item_service.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return ItemResponse.from_domain_model(item)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get item {item_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(request: ItemCreateRequest):
    """Create new item"""
    try:
        item = await item_service.create_item(request)
        return ItemResponse.from_domain_model(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create item", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, request: ItemUpdateRequest):
    """Update existing item"""
    try:
        item = await item_service.update_item(item_id, request)
        return ItemResponse.from_domain_model(item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update item {item_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """Delete item"""
    try:
        await item_service.delete_item(item_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete item {item_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/query", response_model=List[ItemResponse])
async def search_items(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    available_only: bool = Query(False, description="Show only available items")
):
    """Search items with filters"""
    try:
        items = await item_service.search_items(
            name=name,
            min_price=min_price,
            max_price=max_price,
            available_only=available_only
        )
        return [ItemResponse.from_domain_model(item) for item in items]
    except Exception as e:
        logger.error("Failed to search items", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### `events.py` - Domain Events

```python
"""Item domain events for analytics and notifications"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.shared.events import DomainEvent

@dataclass
class ItemCreatedEvent(DomainEvent):
    """Published when an item is created"""
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

@dataclass
class ItemUpdatedEvent(DomainEvent):
    """Published when an item is updated"""
    item_id: int
    updated_fields: list[str]
    updated_at: datetime
    
    def __init__(self, item_id: int, updated_fields: list[str], updated_at: datetime):
        self.event_type = "item.updated"
        self.timestamp = datetime.utcnow()
        self.item_id = item_id
        self.updated_fields = updated_fields
        self.updated_at = updated_at

@dataclass
class ItemDeletedEvent(DomainEvent):
    """Published when an item is deleted"""
    item_id: int
    deleted_at: datetime
    
    def __init__(self, item_id: int, deleted_at: datetime):
        self.event_type = "item.deleted"
        self.timestamp = datetime.utcnow()
        self.item_id = item_id
        self.deleted_at = deleted_at

@dataclass
class ItemViewedEvent(DomainEvent):
    """Published when an item is viewed - for analytics"""
    item_id: int
    user_id: Optional[int]
    viewed_at: datetime
    
    def __init__(self, item_id: int, user_id: Optional[int], viewed_at: datetime):
        self.event_type = "item.viewed"
        self.timestamp = datetime.utcnow()
        self.item_id = item_id
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

async def create_order(user_id: int, item_id: int) -> Order:
    # ✅ Call through service layer
    user = await user_service.get_user(user_id)
    if not user:
        raise ValueError("User not found")
    
    # Continue with order creation...
```

### Pattern 2: Validation Across Domains

```python
# app/orders/service.py
"""Order service validates across users and items"""
from app.users import service as user_service
from app.items import service as item_service

async def create_order(user_id: int, item_id: int, quantity: int) -> Order:
    # Validate user
    user_exists = await user_service.validate_user_exists(user_id)
    if not user_exists:
        raise ValueError("Invalid user")
    
    # Validate item
    item = await item_service.get_item(item_id)
    if not item:
        raise ValueError("Item not found")
    
    if not item.is_available:
        raise ValueError("Item not available")
    
    # Create order
    order = Order(
        user_id=user_id,
        item_id=item_id,
        quantity=quantity,
        total_price=item.price * quantity
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
    """Order with user and item details"""
    id: int
    # User information (from users domain)
    user_id: int
    username: str
    user_email: str
    # Item information (from items domain)
    item_id: int
    item_name: str
    item_price: Decimal
    # Order information
    quantity: int
    total_price: Decimal

# app/orders/service.py
from app.users import service as user_service
from app.items import service as item_service

async def get_order_detail(order_id: int) -> OrderDetailResponse:
    """Get order with enriched data"""
    order = await order_repository.get(order_id)
    
    # Fetch related data from other domains
    user = await user_service.get_user(order.user_id)
    item = await item_service.get_item(order.item_id)
    
    # Compose enriched response
    return OrderDetailResponse(
        id=order.id,
        user_id=user.id,
        username=user.username,
        user_email=user.email,
        item_id=item.id,
        item_name=item.name,
        item_price=item.price,
        quantity=order.quantity,
        total_price=order.total_price
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

async def track_item_events(event: DomainEvent):
    """Track item-specific events"""
    if hasattr(event, 'item_id'):
        logger.info(
            "Item analytics",
            extra={
                'analytics_category': 'item',
                'item_id': event.item_id,
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
    event_bus.subscribe("item.created", track_item_events)
    event_bus.subscribe("item.updated", track_item_events)
    event_bus.subscribe("item.deleted", track_item_events)
    event_bus.subscribe("item.viewed", track_item_events)
    event_bus.subscribe("item.viewed", track_user_behavior)
    
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
mkdir -p app/items app/users app/shared
touch app/items/{__init__.py,models.py,schemas.py,service.py,repository.py,router.py,events.py}
touch app/users/{__init__.py,models.py,schemas.py,service.py,repository.py,router.py,events.py}
```

#### Step 2: Create Shared Event System

1. Create `app/shared/events.py` with EventBus (see above)
2. Create `app/analytics/handlers.py` for analytics

#### Step 3: Split Models

**Before (app/models.py):**
```python
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
```

**After:**
```python
# app/items/models.py - Domain model
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    price: Decimal
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

# app/items/schemas.py - API DTOs
class ItemCreateRequest(BaseModel):
    name: str
    price: Decimal

class ItemResponse(BaseModel):
    id: int
    name: str
    price: Decimal
```

#### Step 4: Extract Service Layer

**Before (logic in router):**
```python
@router.post("/items")
async def create_item(item: Item):
    item.id = generate_id()
    items_db.append(item)
    return item
```

**After:**
```python
# app/items/service.py
async def create_item(request: ItemCreateRequest) -> Item:
    item = Item(name=request.name, price=request.price)
    item = await item_repository.create(item)
    await event_bus.publish(ItemCreatedEvent(...))
    return item

# app/items/router.py
@router.post("/items", response_model=ItemResponse)
async def create_item(request: ItemCreateRequest):
    item = await item_service.create_item(request)
    return ItemResponse.from_domain_model(item)
```

#### Step 5: Create Repository Layer

```python
# app/items/repository.py
class ItemRepository:
    async def create(self, item: Item) -> Item:
        # Data access logic
        pass

item_repository = ItemRepository()
```

#### Step 6: Define and Publish Events

```python
# app/items/events.py
@dataclass
class ItemCreatedEvent(DomainEvent):
    item_id: int
    name: str
    price: Decimal
    created_at: datetime
    
    def __init__(self, ...):
        self.event_type = "item.created"
        self.timestamp = datetime.utcnow()
        # ... set fields

# app/items/service.py
await event_bus.publish(ItemCreatedEvent(...))
```

#### Step 7: Update Imports

```python
# app/main.py
from app.items.router import router as items_router
from app.users.router import router as users_router

app.include_router(items_router)
app.include_router(users_router)
```

#### Step 8: Export Public API

```python
# app/items/__init__.py
from .service import get_item, create_item, update_item, delete_item
from .schemas import ItemResponse, ItemCreateRequest

__all__ = ["get_item", "create_item", "update_item", "delete_item",
           "ItemResponse", "ItemCreateRequest"]
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

# app/items/service.py
async def get_items_paginated(pagination: PaginationParams) -> PaginatedResponse:
    items, total = await item_repository.get_paginated(
        offset=pagination.offset,
        limit=pagination.page_size
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size
    )
```

### Pattern: Soft Delete

```python
# app/items/service.py
async def delete_item(item_id: int, soft: bool = True) -> None:
    """Delete item (soft delete by default)"""
    if soft:
        item = await item_repository.get(item_id)
        item.is_deleted = True
        await item_repository.update(item)
    else:
        await item_repository.delete(item_id)
    
    await event_bus.publish(ItemDeletedEvent(
        item_id=item_id,
        deleted_at=datetime.utcnow(),
        soft_delete=soft
    ))
```

### Pattern: Audit Trail

```python
# app/items/events.py
@dataclass
class ItemAuditEvent(DomainEvent):
    """Audit trail for item changes"""
    item_id: int
    action: str  # 'created', 'updated', 'deleted'
    changed_by: int  # User ID
    changes: dict
    timestamp: datetime

# app/items/service.py
async def update_item(item_id: int, request: ItemUpdateRequest, user_id: int) -> Item:
    # ... update logic
    
    await event_bus.publish(ItemAuditEvent(
        item_id=item.id,
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

