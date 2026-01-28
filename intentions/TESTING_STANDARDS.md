# Testing Standards

**Companion to:** [TESTING_GUIDE.md](./TESTING_GUIDE.md)  
**Version:** 1.0  
**Last Updated:** October 28, 2025  
**Status:** MANDATORY - All code changes must include tests  
**Audience:** Developers

For detailed examples and guidance, see [TESTING_GUIDE.md](./TESTING_GUIDE.md)

---

## Core Principles

1. **Mirror Domain Structure** - Test organization matches `app/` structure
2. **Test by Layer** - Unit, integration, and API tests clearly separated
3. **Fast Feedback** - Unit tests run in < 5 seconds
4. **Independent Tests** - Each test runs in isolation
5. **Realistic Data** - Use fixtures, avoid magic values

---

## Required Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── fixtures/                      # Test data factories
│   ├── __init__.py
│   ├── items.py
│   └── users.py
│
├── unit/                          # Fast, isolated (mocked dependencies)
│   ├── __init__.py
│   ├── {domain}/
│   │   ├── __init__.py
│   │   ├── test_models.py        # Domain logic & validation
│   │   ├── test_schemas.py       # DTO validation
│   │   ├── test_service.py       # Business logic (mocked repo)
│   │   └── test_repository.py    # Data access (mocked DB)
│   └── shared/
│       ├── test_events.py
│       └── test_value_objects.py
│
├── integration/                   # With real dependencies
│   ├── __init__.py
│   ├── {domain}/
│   │   ├── test_service_integration.py
│   │   └── test_repository_integration.py
│   └── test_cross_domain.py      # Multiple domains together
│
└── api/                           # Full HTTP stack
    ├── __init__.py
    ├── test_{domain}_api.py
    └── test_flows.py              # Complete user journeys
```

---

## Test Types

| Type | Purpose | Speed | Dependencies | Location |
|------|---------|-------|--------------|----------|
| **Unit** | Single function/class | < 100ms | Mocked | `tests/unit/{domain}/` |
| **Integration** | Multiple layers | < 1s | Real (test DB) | `tests/integration/{domain}/` |
| **API** | Full HTTP stack | < 2s | Real (test DB) | `tests/api/` |

---

## Test Scope by File

### Unit Tests - `tests/unit/{domain}/`

| File | Tests | Mocks |
|------|-------|-------|
| `test_models.py` | Validators, business logic methods, domain rules | None |
| `test_schemas.py` | Field validation, serialization, `from_domain_model()` | None |
| `test_service.py` | Business logic, event publishing, orchestration | Repository, event bus, external APIs |
| `test_repository.py` | CRUD operations, model conversions, query logic | Database session |

### Integration Tests - `tests/integration/{domain}/`

**Tests:** Service + repository, event handlers, cross-domain flows  
**Uses:** Real test database, real event bus  
**Mocks:** External APIs only

### API Tests - `tests/api/`

**Tests:** HTTP endpoints, status codes, request/response format, user journeys  
**Uses:** TestClient, full HTTP stack, test database  
**Mocks:** External APIs only

---

## Naming Convention

```python
# Format: test_{method_name}_{scenario}_{expected_result}
def test_create_item_with_valid_data_returns_item()
def test_create_item_with_negative_price_raises_error()
def test_get_item_when_not_found_returns_none()
```

---

## Mandatory Requirements

### Every Domain Must Have

- [ ] Unit tests for all domain models (`test_models.py`)
- [ ] Unit tests for all schemas (`test_schemas.py`)
- [ ] Unit tests for service layer (`test_service.py`)
- [ ] Unit tests for repository layer (`test_repository.py`)
- [ ] Integration test for service + repository
- [ ] API tests for all endpoints

### Event Testing (MANDATORY)

**All business actions that publish events MUST have tests verifying:**
1. Event is published
2. Event type is correct
3. Event data is complete

See [TESTING_GUIDE.md - Event Testing](./TESTING_GUIDE.md#event-testing) for examples.

### Cross-Domain Testing

**All cross-domain interactions MUST:**
- Use service APIs only (never repository or internal models)
- Have integration tests verifying the interaction
- Mock external dependencies appropriately

See [TESTING_GUIDE.md - Cross-Domain Testing](./TESTING_GUIDE.md#cross-domain-testing) for examples.

---

## Code Coverage Standards

| Layer | Minimum Coverage | Target |
|-------|-----------------|--------|
| Models | 90% | 100% |
| Schemas | 80% | 90% |
| Service | 85% | 95% |
| Repository | 80% | 90% |
| Router | 70% | 85% |
| **Overall** | **80%** | **90%** |

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

---

## Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

markers =
    unit: Fast unit tests with mocked dependencies
    integration: Integration tests with real dependencies
    api: Full HTTP stack tests
    slow: Tests taking > 1 second

norecursedirs = .git .venv venv __pycache__ *.egg-info
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only (fast)
pytest tests/unit -m unit

# Integration tests
pytest tests/integration -m integration

# API tests
pytest tests/api -m api

# Specific domain
pytest tests/unit/items

# With coverage
pytest --cov=app --cov-report=html

# Stop on first failure
pytest -x

# Verbose output
pytest -v
```

---

## Best Practices

### ✅ DO

- Mock external dependencies in unit tests
- Use realistic test data via fixtures
- Test error cases and edge cases
- Reset state between tests
- Use descriptive test names
- Test one thing per test
- Verify event publishing for all business actions

### ❌ DON'T

- Test implementation details
- Use sleep() or arbitrary waits
- Depend on test execution order
- Use production database
- Mock everything in integration tests
- Skip error case testing
- Leave tests commented out

---

## New Feature Checklist

When adding a new feature:

- [ ] Unit tests for domain models (validators, business logic)
- [ ] Unit tests for schemas (validation, serialization)
- [ ] Unit tests for service (business logic, event publishing)
- [ ] Unit tests for repository (CRUD, conversions)
- [ ] Integration test (service + repository)
- [ ] API tests (all endpoints)
- [ ] Cross-domain tests (if applicable)
- [ ] Coverage ≥ 80%
- [ ] All tests passing
- [ ] No skipped tests without issue reference

---

## Code Review Checklist

- [ ] Tests in correct directory (`unit/`, `integration/`, `api/`)
- [ ] Test names follow naming convention
- [ ] Unit tests mock external dependencies
- [ ] Event publishing is tested (if applicable)
- [ ] Error cases are tested
- [ ] Fixtures used for test data (no magic values)
- [ ] Tests are independent (can run in any order)
- [ ] Coverage meets minimum standards
- [ ] No skipped tests without justification

---

## Quick Reference

### Test Type Decision Tree

```
Is it testing a single function/method in isolation?
├─ YES → Unit test (tests/unit/{domain}/)
└─ NO → Does it test multiple layers/domains together?
    ├─ YES → Integration test (tests/integration/)
    └─ NO → Does it test HTTP endpoints?
        ├─ YES → API test (tests/api/)
        └─ NO → Integration test (tests/integration/)
```

### Import Patterns

```python
# Unit test - import from domain, mock dependencies
from app.items.models import Item
from app.items.service import create_item
from unittest.mock import AsyncMock, patch

# Integration test - import service APIs
from app.items import service as item_service
from app.users import service as user_service

# API test - import test client
from fastapi.testclient import TestClient
from app.main import app
```

---

## For Detailed Guidance

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for:
- Complete code examples for each test type
- Step-by-step testing workflow
- Mock and fixture patterns
- CI/CD integration examples
- Common testing scenarios

---

**Document Status:** ACTIVE  
**Enforcement:** MANDATORY for all code changes
