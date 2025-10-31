# Exception Handling Guide

**Companion to:** [EXCEPTION_HANDLING_STANDARDS.md](./EXCEPTION_HANDLING_STANDARDS.md)
**Version:** 2.0
**Last Updated:** October 28, 2025
**Audience:** Developers implementing exception handling in hexagonal architecture

**Related Documentation:**
- [Exception Handling Standards](./EXCEPTION_HANDLING_STANDARDS.md) - Mandatory rules (read first!)
- [Architecture Standards](./ARCHITECTURE_STANDARDS.md) - Hexagonal architecture rules

---

## Table of Contents

1. [Exception Hierarchy Implementation](#exception-hierarchy-implementation)
2. [Service Layer Patterns](#service-layer-patterns)
3. [Router Layer Patterns](#router-layer-patterns)
4. [Repository Layer Patterns](#repository-layer-patterns)
5. [Global Exception Handlers](#global-exception-handlers)
6. [Cross-Domain Exception Handling](#cross-domain-exception-handling)
7. [Database Error Handling](#database-error-handling)
8. [Event Publishing Patterns](#event-publishing-patterns)
9. [Frontend Error Handling](#frontend-error-handling)
10. [Testing Exception Handling](#testing-exception-handling)

---

## Exception Hierarchy Implementation

Create domain-specific exceptions in `app/shared/exceptions.py`:

```python
# app/shared/exceptions.py
"""
Domain exceptions for business logic errors.
These are part of the hexagon's core - NOT infrastructure concerns.
"""
from typing import Optional


class DomainException(Exception):
    """
    Base exception for all domain/business logic errors.
    These exceptions are part of the port contract.
    """
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        return self.message


class NotFoundError(DomainException):
    """
    Entity not found in the domain.
    Maps to HTTP 404.
    """
    pass


class ValidationError(DomainException):
    """
    Business rule validation failed.
    Maps to HTTP 400.

    Note: This is for BUSINESS validation, not input validation.
    Pydantic handles input validation (HTTP 422).
    """
    pass


class ConflictError(DomainException):
    """
    Operation conflicts with current state.
    Examples: Duplicate entity, constraint violation.
    Maps to HTTP 409.
    """
    pass


class AuthorizationError(DomainException):
    """
    User not authorized for this operation.
    Maps to HTTP 403.
    """
    pass


class BusinessRuleError(DomainException):
    """
    Generic business rule violation.
    Use specific exceptions when possible.
    Maps to HTTP 400.
    """
    pass
```

---

## Service Layer Patterns

### Pattern 1: Raise Exceptions, Don't Return Optional

```python
# app/items/service.py
from app.shared.exceptions import NotFoundError, ValidationError

async def get_item(item_id: int) -> Item:
    """
    Get item by ID.

    Raises:
        NotFoundError: Item does not exist
    """
    item = await item_repository.get(item_id)
    if not item:
        raise NotFoundError(
            f"Item {item_id} not found",
            details={"item_id": item_id}
        )
    return item


# ❌ WRONG - Don't return Optional for "not found"
async def get_item_wrong(item_id: int) -> Optional[Item]:
    return await item_repository.get(item_id)
```

### Pattern 2: Business Validation

```python
async def create_item(request: ItemCreateRequest) -> Item:
    """
    Create new item.

    Raises:
        ValidationError: Business rule violation
        ConflictError: Item already exists
    """
    # Business validation (NOT input validation - Pydantic does that)
    if request.price < 0:
        raise ValidationError(
            "Price must be positive",
            details={"price": request.price}
        )

    # Create domain model (Pydantic validation happens here)
    item = Item(**request.dict())

    # Additional business rules
    if not item.can_be_sold():
        raise ValidationError(
            "Cannot create item that cannot be sold",
            details={"name": item.name, "price": item.price}
        )

    # Persist
    item = await item_repository.create(item)

    # Publish event
    await event_bus.publish(ItemCreatedEvent(...))

    return item
```

### Pattern 3: Complex Business Rules

```python
async def update_item_price(item_id: int, new_price: Decimal) -> Item:
    item = await get_item(item_id)  # Raises NotFoundError

    # Complex business rule
    if new_price < item.cost_price:
        raise ValidationError(
            "Price cannot be below cost",
            details={
                "new_price": float(new_price),
                "cost_price": float(item.cost_price),
                "item_id": item_id
            }
        )

    item.price = new_price
    return await item_repository.update(item)
```

### Pattern 4: Authorization Checks

```python
async def delete_item(item_id: int, user_id: int) -> None:
    item = await get_item(item_id)

    # Check authorization
    if item.owner_id != user_id:
        raise AuthorizationError(
            "You cannot delete this item",
            details={"item_id": item_id, "user_id": user_id}
        )

    await item_repository.delete(item_id)
    await event_bus.publish(ItemDeletedEvent(...))
```

---

## Router Layer Patterns

### Correct Pattern: Let Exceptions Propagate

```python
# app/items/router.py
from fastapi import APIRouter
from . import service as item_service
from .schemas import ItemResponse, ItemCreateRequest

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """
    ✅ CORRECT - Let domain exception propagate to global handler.
    No try/except needed here.
    """
    item = await item_service.get_item(item_id)  # May raise NotFoundError
    return ItemResponse.from_domain_model(item)


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(request: ItemCreateRequest):
    """
    ✅ CORRECT - Let domain exceptions propagate.
    """
    item = await item_service.create_item(request)  # May raise ValidationError
    return ItemResponse.from_domain_model(item)


# ❌ WRONG - Don't catch domain exceptions in router
@router.get("/{item_id}")
async def get_item_wrong(item_id: int):
    try:
        item = await item_service.get_item(item_id)
        return ItemResponse.from_domain_model(item)
    except NotFoundError:  # ❌ Don't do this!
        raise HTTPException(status_code=404, detail="Not found")
```

### Exception: Adapter-Specific Errors

```python
@router.post("/upload")
async def upload_file(file: UploadFile):
    """Adapter-specific error handling is OK"""
    try:
        # File upload is adapter concern, not domain
        content = await file.read()
    except Exception as e:
        logger.error("File upload failed", exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid file")

    # Now call domain
    result = await item_service.process_upload(content)
    return result
```

---

## Repository Layer Patterns

### Pattern: Translate Infrastructure Errors

```python
# app/items/repository.py
from sqlalchemy.exc import IntegrityError, OperationalError
from app.shared.exceptions import ConflictError, ValidationError

class ItemRepository:
    """Data access layer - converts between infrastructure and domain"""

    async def create(self, item: Item) -> Item:
        """
        Persist item.

        Raises:
            ConflictError: Item already exists (unique constraint)
        """
        try:
            # Database operation
            db_item = ItemDB(**item.dict())
            session.add(db_item)
            await session.commit()
            return item
        except IntegrityError as e:
            # ✅ Translate infrastructure error to domain exception
            if "unique_name" in str(e):
                raise ConflictError(
                    f"Item with name '{item.name}' already exists",
                    details={"name": item.name}
                )
            elif "foreign_key" in str(e):
                raise ValidationError(
                    "Referenced entity does not exist",
                    details={"error": str(e)}
                )
            else:
                # Unknown integrity error
                raise ConflictError(
                    "Operation conflicts with existing data",
                    details={"db_error": str(e)}
                )
        except OperationalError as e:
            # Infrastructure errors should bubble up as-is
            # Global handler will catch and return 500
            logger.error("Database operation failed", exc_info=True)
            raise

    async def get(self, item_id: int) -> Optional[Item]:
        """
        Get item by ID.

        Returns:
            Item if found, None otherwise.

        Note: Repository CAN return Optional - service decides if None is an error.
        """
        db_item = await session.get(ItemDB, item_id)
        if not db_item:
            return None
        return Item.from_orm(db_item)
```

---

## Global Exception Handlers

Configure in `main.py`:

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.shared.exceptions import (
    DomainException,
    NotFoundError,
    ValidationError,
    ConflictError,
    AuthorizationError,
)
from app.shared.logging_config import logger
from app.shared.exception_handlers import validation_exception_handler

app = FastAPI()


# Domain exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    """Handle NotFoundError -> 404"""
    logger.warning(
        "Resource not found",
        extra={
            "error_type": "NotFoundError",
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
        }
    )
    return JSONResponse(
        status_code=404,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle ValidationError -> 400"""
    logger.warning(
        "Business validation failed",
        extra={
            "error_type": "ValidationError",
            "message": exc.message,
            "details": exc.details,
        }
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    """Handle ConflictError -> 409"""
    logger.warning(
        "Conflict detected",
        extra={
            "error_type": "ConflictError",
            "message": exc.message,
            "details": exc.details,
        }
    )
    return JSONResponse(
        status_code=409,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(AuthorizationError)
async def authorization_handler(request: Request, exc: AuthorizationError):
    """Handle AuthorizationError -> 403"""
    logger.warning(
        "Authorization failed",
        extra={
            "error_type": "AuthorizationError",
            "message": exc.message,
            "user_id": exc.details.get("user_id"),
        }
    )
    return JSONResponse(
        status_code=403,
        content={
            "error": exc.message,
            "details": {}  # Don't expose authorization details
        }
    )


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    """
    Catch-all for domain exceptions not handled above.
    Maps to 500 by default.
    """
    logger.error(
        "Domain exception",
        extra={
            "error_type": type(exc).__name__,
            "message": exc.message,
            "details": exc.details,
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "An error occurred processing your request",
            "details": {}  # Don't expose internal details for 500
        }
    )


# Pydantic validation errors (input validation)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler_wrapper(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors -> 422"""
    return await validation_exception_handler(request, exc)


# Catch-all for unexpected errors
@app.exception_handler(Exception)
async def catch_all_handler(request: Request, exc: Exception):
    """
    Last resort handler for unexpected exceptions.
    These should be investigated and fixed.
    """
    logger.error(
        "Unexpected exception",
        extra={
            "error_type": type(exc).__name__,
            "message": str(exc),
            "path": str(request.url.path),
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "details": {}
        }
    )
```

---

## Cross-Domain Exception Handling

### Pattern 1: Let Exceptions Propagate

```python
# app/orders/service.py
from app.users import service as user_service
from app.items import service as item_service
from app.shared.exceptions import NotFoundError, ValidationError

async def create_order(user_id: int, item_id: int, quantity: int) -> Order:
    """
    Create order - validates user and item exist.

    Raises:
        NotFoundError: User or item not found
        ValidationError: Business rule violation
    """
    # ✅ Let exceptions propagate - they're already domain exceptions
    user = await user_service.get_user(user_id)  # May raise NotFoundError
    item = await item_service.get_item(item_id)  # May raise NotFoundError

    # Business validation
    if not item.is_available:
        raise ValidationError(
            f"Item '{item.name}' is not available",
            details={"item_id": item_id, "available": False}
        )

    # Create order
    order = Order(user_id=user_id, item_id=item_id, quantity=quantity)
    order = await order_repository.create(order)

    await event_bus.publish(OrderCreatedEvent(...))
    return order
```

### Pattern 2: Add Context to Propagated Exceptions

```python
async def create_bulk_order(order_items: List[OrderItem]) -> List[Order]:
    """Create multiple orders, adding context to failures"""
    orders = []

    for idx, order_item in enumerate(order_items):
        try:
            order = await create_order(
                order_item.user_id,
                order_item.item_id,
                order_item.quantity
            )
            orders.append(order)
        except NotFoundError as e:
            # Add context about which item in the batch failed
            raise NotFoundError(
                f"Batch order failed at index {idx}: {e.message}",
                details={
                    "batch_index": idx,
                    "original_error": e.details,
                    **order_item.dict()
                }
            )

    return orders
```

### Pattern 3: Convert Between Exception Types

```python
async def archive_item(item_id: int, user_id: int) -> None:
    """Archive item - converts NotFoundError to different message"""
    try:
        item = await item_service.get_item(item_id)
    except NotFoundError:
        # Convert to more specific message for this use case
        raise NotFoundError(
            f"Cannot archive: item {item_id} does not exist",
            details={"item_id": item_id, "action": "archive"}
        )

    # Check authorization
    if item.owner_id != user_id:
        raise AuthorizationError(
            "You cannot archive items you don't own",
            details={"item_id": item_id, "user_id": user_id}
        )

    item.is_archived = True
    await item_repository.update(item)
```

---

## Database Error Handling

Repository layer translates database errors to domain exceptions:

```python
# app/items/repository.py
from sqlalchemy.exc import IntegrityError, OperationalError
from app.shared.exceptions import ConflictError, ValidationError

class ItemRepository:
    async def create(self, item: Item) -> Item:
        try:
            db_item = ItemDB(**item.dict())
            session.add(db_item)
            await session.commit()
            return item
        except IntegrityError as e:
            # Unique constraint violation
            if "unique_name" in str(e):
                raise ConflictError(
                    f"Item with name '{item.name}' already exists",
                    details={"name": item.name}
                )
            elif "foreign_key" in str(e):
                raise ValidationError(
                    "Referenced entity does not exist",
                    details={"error": str(e)}
                )
            else:
                # Unknown integrity error
                raise ConflictError(
                    "Operation conflicts with existing data",
                    details={"db_error": str(e)}
                )
        except OperationalError as e:
            # Database connection issues - let it bubble up
            logger.error("Database operational error", exc_info=True)
            raise  # Will be caught by catch-all handler -> 500
```

---

## Event Publishing Patterns

Event publishing failures MUST NOT fail the main operation:

```python
async def create_item(request: ItemCreateRequest) -> Item:
    # Create item
    item = Item(**request.dict())
    item = await item_repository.create(item)

    # ✅ CORRECT - Event publishing wrapped in try/except
    try:
        await event_bus.publish(ItemCreatedEvent(
            item_id=item.id,
            name=item.name,
            price=item.price,
            created_at=datetime.utcnow()
        ))
    except Exception as e:
        # Log but don't fail the operation
        logger.error(
            "Failed to publish ItemCreatedEvent - operation succeeded but event lost",
            extra={
                "item_id": item.id,
                "error": str(e)
            },
            exc_info=True
        )

    return item  # Return item even if event failed


# ❌ WRONG - Event failure fails the operation
async def create_item_wrong(request: ItemCreateRequest) -> Item:
    item = await item_repository.create(Item(**request.dict()))
    await event_bus.publish(ItemCreatedEvent(...))  # May raise!
    return item  # Never reached if event fails
```

### Event Handler Exceptions

```python
# app/analytics/handlers.py
async def track_item_created(event: ItemCreatedEvent):
    """
    Event handlers should catch their own errors.
    One failing handler shouldn't affect others.
    """
    try:
        # Send to analytics service
        await analytics_service.track_event(event)
    except Exception as e:
        logger.error(
            "Analytics tracking failed",
            extra={"event_type": event.event_type, "error": str(e)},
            exc_info=True
        )
        # Don't re-raise - let other handlers continue
```

---

## Frontend Error Handling

### Error Response Format

All API errors follow this format:

```json
{
  "error": "Human-readable error message for display",
  "details": {
    "field_name": "additional context",
    "item_id": 123
  }
}
```

### Pydantic Validation Errors (422)

Input validation errors have a different format:

```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### Frontend Implementation Example

**React/JavaScript:**

```javascript
// src/features/items/api/itemsApi.js
async function createItem(itemData) {
  try {
    const response = await httpClient.post('/items', itemData);
    return response.data;
  } catch (error) {
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 400:
          // Business validation error - show to user
          throw new Error(data.error);

        case 404:
          // Not found
          throw new Error('Item not found');

        case 409:
          // Conflict
          throw new Error(data.error); // e.g., "Item already exists"

        case 422:
          // Input validation errors
          const fieldErrors = data.detail.map(e =>
            `${e.loc.join('.')}: ${e.msg}`
          ).join(', ');
          throw new Error(fieldErrors);

        case 500:
          // Server error - retry or show generic message
          throw new Error('Server error. Please try again later.');

        default:
          throw new Error('An unexpected error occurred');
      }
    }
    throw error;
  }
}
```

**Frontend Best Practices:**
- ✅ Parse `error` field for user-facing message
- ✅ Use `details` for debugging or field-specific errors
- ✅ Retry on 500 errors (with exponential backoff)
- ❌ Don't retry on 400/404/409/422 (client errors)
- ✅ Log full error details for debugging
- ✅ Show user-friendly messages, not raw error text

---

## Testing Exception Handling

### Unit Tests - Service Layer

```python
# tests/unit/items/test_service.py
import pytest
from unittest.mock import patch, Mock
from app.items import service as item_service
from app.shared.exceptions import NotFoundError, ValidationError

@pytest.mark.asyncio
async def test_get_item_not_found_raises_exception():
    """Test that service raises NotFoundError when item doesn't exist"""
    # Mock repository to return None
    with patch('app.items.repository.item_repository.get', return_value=None):
        # Should raise NotFoundError
        with pytest.raises(NotFoundError) as exc_info:
            await item_service.get_item(999)

        # Verify exception details
        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.details.get("item_id") == 999

@pytest.mark.asyncio
async def test_create_item_negative_price_raises_validation_error():
    """Test that service validates business rules"""
    from app.items.schemas import ItemCreateRequest

    request = ItemCreateRequest(
        name="Test Item",
        price=-10.00,  # Invalid price
        is_available=True
    )

    with pytest.raises(ValidationError) as exc_info:
        await item_service.create_item(request)

    assert "positive" in str(exc_info.value).lower()
    assert exc_info.value.details.get("price") == -10.00

@pytest.mark.asyncio
async def test_create_item_publishes_event_even_if_event_fails():
    """Test that item is created even if event publishing fails"""
    from app.items.schemas import ItemCreateRequest

    request = ItemCreateRequest(name="Test", price=10.00)

    # Mock repository to succeed
    mock_item = Mock(id=1, name="Test", price=10.00)
    with patch('app.items.repository.item_repository.create', return_value=mock_item):
        # Mock event bus to fail
        with patch('app.shared.events.event_bus.publish', side_effect=Exception("Event failed")):
            # Should NOT raise - item creation should succeed
            result = await item_service.create_item(request)
            assert result.id == 1
```

### Integration Tests - Service + Repository

```python
# tests/integration/items/test_service_integration.py
import pytest
from app.items import service as item_service
from app.shared.exceptions import ConflictError

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_duplicate_item_raises_conflict(test_db):
    """Test that duplicate item creation raises ConflictError"""
    from app.items.schemas import ItemCreateRequest

    request = ItemCreateRequest(name="Unique Item", price=10.00)

    # Create first item
    item1 = await item_service.create_item(request)
    assert item1.id is not None

    # Try to create duplicate
    with pytest.raises(ConflictError) as exc_info:
        await item_service.create_item(request)

    assert "already exists" in str(exc_info.value).lower()
```

### API Tests - Full Stack

```python
# tests/api/test_items_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_item_not_found_returns_404():
    """Test that API returns 404 for non-existent item"""
    response = client.get("/items/999999")

    assert response.status_code == 404
    assert "error" in response.json()
    assert "not found" in response.json()["error"].lower()

def test_create_item_invalid_price_returns_400():
    """Test that API returns 400 for business validation errors"""
    response = client.post("/items", json={
        "name": "Test Item",
        "price": -10.00,  # Invalid
        "is_available": True
    })

    assert response.status_code == 400
    assert "error" in response.json()
    assert "positive" in response.json()["error"].lower()

def test_create_item_malformed_request_returns_422():
    """Test that API returns 422 for input validation errors"""
    response = client.post("/items", json={
        "name": "Test Item",
        "price": "not a number",  # Type error
        "is_available": True
    })

    assert response.status_code == 422
    assert "detail" in response.json()  # Pydantic format

def test_create_duplicate_item_returns_409():
    """Test that API returns 409 for conflicts"""
    item_data = {
        "name": "Unique Name",
        "price": 10.00,
        "is_available": True
    }

    # Create first item
    response1 = client.post("/items", json=item_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post("/items", json=item_data)
    assert response2.status_code == 409
    assert "error" in response2.json()
```

### Testing Global Exception Handlers

```python
# tests/api/test_exception_handlers.py
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.shared.exceptions import NotFoundError, ValidationError

client = TestClient(app)

def test_not_found_exception_returns_404():
    """Test that NotFoundError is handled correctly"""
    with patch('app.items.service.get_item', side_effect=NotFoundError("Item not found", {"item_id": 123})):
        response = client.get("/items/123")

        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "Item not found"
        assert data["details"]["item_id"] == 123

def test_validation_exception_returns_400():
    """Test that ValidationError is handled correctly"""
    with patch('app.items.service.create_item', side_effect=ValidationError("Invalid price", {"price": -10})):
        response = client.post("/items", json={"name": "Test", "price": 10.00})

        assert response.status_code == 400
        data = response.json()
        assert "Invalid price" in data["error"]
        assert "price" in data["details"]
```

---

## Summary

This guide provides practical implementation examples for the exception handling patterns defined in `EXCEPTION_HANDLING_STANDARDS.md`. Key patterns:

1. **Service layer** raises domain exceptions (not Optional)
2. **Router layer** lets exceptions propagate to global handlers
3. **Repository layer** translates infrastructure errors to domain exceptions
4. **Global handlers** convert domain exceptions to HTTP responses
5. **Event publishing** wrapped in try/except (don't fail main operation)
6. **Frontend** handles structured error responses consistently

For questions or clarifications, refer to the standards document or consult the architecture team.

