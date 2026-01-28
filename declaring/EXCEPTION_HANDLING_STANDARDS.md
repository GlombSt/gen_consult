# Exception Handling Standards

**Version:** 2.0
**Last Updated:** October 28, 2025
**Status:** MANDATORY - All code changes must follow these standards
**Audience:** Experts familiar with hexagonal architecture and exception handling

For detailed examples and explanations, see [EXCEPTION_HANDLING_GUIDE.md](./EXCEPTION_HANDLING_GUIDE.md)

**Related Documentation:**
- [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) - Hexagonal architecture rules
- [Frontend Architecture](../customer-ux/ARCHITECTURE.md) - How frontend handles errors

---

## Hexagonal Architecture View

In our hexagonal architecture, exceptions flow from the **core outward** to the **adapters**.

```
┌─────────────────────────────────────────────┐
│         HEXAGON (Business Core)             │
│                                             │
│  Domain Models raise business exceptions    │
│              ↓                              │
│  Service Layer (PORTS) raises domain        │
│  exceptions - part of the port contract     │
│                                             │
└──────────────────┬──────────────────────────┘
                   │ Domain Exceptions
                   ▼
        ┌──────────────────────┐
        │   HTTP Router        │
        │  (PRIMARY ADAPTER)   │
        │                      │
        │  Global handlers     │
        │  convert domain      │
        │  exceptions →        │
        │  HTTP responses      │
        └──────────────────────┘
                   │ HTTP 4xx/5xx
                   ▼
        ┌──────────────────────┐
        │   React Frontend     │
        │  (External Adapter)  │
        │                      │
        │  Displays error      │
        │  to user             │
        └──────────────────────┘
```

**Key Principles:**
1. **Domain exceptions** are part of the business core (hexagon)
2. **Service layer (ports)** raises domain exceptions as part of its contract
3. **Primary adapters** (routers) catch and translate to HTTP responses
4. **Secondary adapters** (repository) translate infrastructure errors to domain exceptions
5. **Frontend** receives structured HTTP error responses

---

## Exception Hierarchy

**Required exception types** in `app/shared/exceptions.py`:

- `DomainException` - Base for all domain exceptions
- `NotFoundError` - Entity not found (HTTP 404)
- `ValidationError` - Business rule violation (HTTP 400)
- `ConflictError` - Duplicate or constraint violation (HTTP 409)
- `AuthorizationError` - User not authorized (HTTP 403)
- `BusinessRuleError` - Generic business rule violation (HTTP 400)

**When to create new exception types:**
- ✅ Represents a distinct business concept
- ✅ Needs different HTTP status code
- ✅ Needs special handling/logging
- ❌ Don't create too many - prefer using `details` dict

All exceptions must:
- Inherit from `DomainException`
- Accept `message: str` and `details: Optional[dict]` in constructor
- Store message in `self.message` and details in `self.details`

---

## Exception Handling by Layer

### Service Layer (PORTS) - MUST Raise Domain Exceptions

**The service layer is the boundary of the hexagon. Exceptions are part of the port contract.**

**Rules:**
- ✅ **MUST** raise domain exceptions (not return `Optional` for errors)
- ✅ Use specific exception types (`NotFoundError`, `ValidationError`, etc.)
- ✅ Include helpful `details` dict with context
- ✅ Wrap event publishing in try/except (don't fail main operation)
- ✅ Let exceptions propagate from other services
- ✅ Document raised exceptions in docstrings (`Raises:` section)

**When Optional IS appropriate:**
- When None is a valid business outcome (not an error)
- Example: `get_current_user() -> Optional[User]` for anonymous access

**Why exceptions over Optional:**
- Clearer intent - "must exist or it's an error"
- Caller doesn't need None checks
- Global exception handlers work correctly
- Better error messages and context
- Consistent with hexagonal architecture ports

### Router Layer (PRIMARY ADAPTER) - MUST NOT Catch Domain Exceptions

**Routers are adapters. Let global handlers convert domain exceptions to HTTP.**

**Rules:**
- ✅ **MUST NOT** catch domain exceptions
- ✅ Let global handlers convert to HTTP
- ✅ Only catch adapter-specific errors (file uploads, etc.)
- ❌ Never manually convert domain exceptions to HTTPException

**Exception: Adapter-specific errors**
- Only catch exceptions for adapter-specific concerns (file uploads, parsing, etc.)

### Repository Layer (SECONDARY ADAPTER) - MUST Translate Infrastructure Errors

**Repositories are adapters that convert infrastructure errors to domain exceptions.**

**Rules:**
- ✅ **MUST** translate infrastructure errors to domain exceptions
- ✅ Can return `Optional` - infrastructure layer doesn't know business rules
- ✅ Service layer converts `None` to exception if "not found" is an error
- ✅ Log infrastructure errors before letting them bubble up (for 500s)

**Common translations:**
- `IntegrityError` (unique constraint) → `ConflictError` (409)
- `IntegrityError` (foreign key) → `ValidationError` (400)
- `OperationalError` → Let bubble up → 500

---

## Global Exception Handlers

**Configure in `main.py` - these translate domain exceptions to HTTP responses.**

**Required handlers:**
- `NotFoundError` → HTTP 404
- `ValidationError` → HTTP 400
- `ConflictError` → HTTP 409
- `AuthorizationError` → HTTP 403
- `DomainException` (catch-all) → HTTP 500
- `RequestValidationError` (Pydantic) → HTTP 422
- `Exception` (catch-all) → HTTP 500

**All handlers MUST:**
- Log with structured logging (include error_type, message, details, path)
- Return JSONResponse with `{"error": str, "details": dict}` format
- Don't expose internal details for 500 errors

---

## API Error Contract

**All API errors follow this format:**

```json
{
  "error": "Human-readable error message for display",
  "details": {
    "field_name": "additional context",
    "item_id": 123
  }
}
```

### HTTP Status Codes

| Status | Exception Type | Meaning | Frontend Action |
|--------|---------------|---------|-----------------|
| **400** | `ValidationError`, `BusinessRuleError` | Business validation failed | Show error to user, don't retry |
| **403** | `AuthorizationError` | User not authorized | Redirect to login or show access denied |
| **404** | `NotFoundError` | Resource not found | Show "not found" message |
| **409** | `ConflictError` | Duplicate or constraint violation | Show conflict message, suggest alternatives |
| **422** | Pydantic `RequestValidationError` | Malformed request (input validation) | Fix request format, show field errors |
| **500** | `DomainException`, `Exception` | Server error | Show generic error, retry after delay |

### Pydantic Validation Errors (422)

Input validation errors use FastAPI's standard format with `detail` array.

---

## Cross-Domain Exception Handling

**When one domain service calls another:**

**Rules:**
- ✅ Let exceptions propagate (they're already domain exceptions)
- ✅ Add context when appropriate (which item in batch failed)
- ✅ Can convert between exception types with better messages
- ❌ Don't swallow exceptions without re-raising

---

## Event Publishing

**Event publishing failures MUST NOT fail the main operation.**

**Rules:**
- ✅ Wrap event publishing in try/except
- ✅ Log failures but don't re-raise
- ✅ Return result even if event fails
- ✅ Event handlers should catch their own errors (one failing shouldn't affect others)

---

## HTTP Status Mapping

| Exception Type | HTTP Status | When to Use | Example |
|---------------|-------------|-------------|---------|
| `NotFoundError` | **404** | Entity doesn't exist | Item with ID 123 not found |
| `ValidationError` | **400** | Business rule violation | Price must be positive |
| `BusinessRuleError` | **400** | Generic business rule | Cannot delete item with active orders |
| `ConflictError` | **409** | Duplicate or constraint | Item with this name already exists |
| `AuthorizationError` | **403** | User not authorized | You cannot delete this item |
| `DomainException` | **500** | Unexpected domain error | (should be rare - add specific type) |
| Pydantic `RequestValidationError` | **422** | Input validation | Field 'price' must be a number |
| `Exception` | **500** | Unexpected error | Database connection failed |

---

## Code Change Checklist

### Service Layer
- [ ] Services raise exceptions, not return `Optional` (for errors)
- [ ] Use specific exception types (`NotFoundError`, `ValidationError`, etc.)
- [ ] Include helpful `details` dict
- [ ] Wrap event publishing in try/except
- [ ] Let exceptions propagate from other services
- [ ] Document raised exceptions in docstrings

### Router Layer
- [ ] Don't catch domain exceptions
- [ ] Let global handlers convert to HTTP
- [ ] Only catch adapter-specific errors (file uploads, etc.)

### Repository Layer
- [ ] Translate database errors to domain exceptions
- [ ] Can return `Optional` - service decides if `None` is an error
- [ ] Log infrastructure errors before letting them bubble up

### Testing
- [ ] Test that services raise correct exceptions
- [ ] Test exception details are included
- [ ] Test HTTP status codes in API tests
- [ ] Test error response format matches contract
- [ ] Test cross-domain exception propagation

---

## Summary

**Exception handling in hexagonal architecture:**

1. **Domain exceptions** are part of the business core (hexagon)
2. **Service layer (ports)** raises exceptions as part of its contract
3. **Routers (adapters)** let global handlers translate to HTTP
4. **Repositories (adapters)** translate infrastructure errors to domain exceptions
5. **Frontend** receives consistent, structured error responses
6. **Tests** verify exception handling at all layers

**Key principle:** Exceptions flow from the core outward to the adapters, where they're translated to the appropriate format for that adapter (HTTP responses, log messages, etc.).

---

**Document Status:** ACTIVE  
**Enforcement:** MANDATORY for all code changes

