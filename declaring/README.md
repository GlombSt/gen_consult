# Declaring - Backend (The Hexagon)

FastAPI backend implementing hexagonal architecture with domain-driven design, event-driven communication, and structured logging.

## Architecture Role

**This backend IS the hexagon** - the business core of the application. All business logic, domain models, and rules live here. The frontend and other clients are external adapters that interact with this core through its ports (service layer APIs).

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
```

For complete architecture overview, see:
- [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) - Mandatory architectural rules
- [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) - Detailed patterns and examples
- [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) - TDD workflow and development practices
- [Root CLAUDE.md](../CLAUDE.md) - Full-stack architecture overview

## Project Structure

```
declaring/
├── app/
│   ├── intents/                    # Domain: Intent management
│   ├── items/                      # Domain: Items
│   ├── users/                      # Domain: Users
│   ├── shared/                     # Cross-cutting concerns
│   │   ├── events.py               # Event bus system
│   │   ├── logging_config.py       # Structured logging with PII protection
│   │   └── value_objects.py        # Shared domain concepts
│   └── main.py                     # Application entry point
│
├── tests/                          # Test suite (unit, integration, API)
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project config & linting rules
├── lint.sh                         # Linting script
├── Dockerfile                      # Docker container
├── docker-compose.yml              # Docker Compose
│
├── README.md                       # This file
├── QUICK_REFERENCE.md              # ⭐ Quick reference card
│
├── ARCHITECTURE_STANDARDS.md       # Mandatory architectural rules
├── ARCHITECTURE_GUIDE.md           # Detailed patterns and examples
├── DEVELOPMENT_STANDARDS.md        # TDD workflow and development practices
├── TESTING_STANDARDS.md            # Testing requirements (80%+ coverage)
├── REFACTORING_GUIDE.md            # Safe refactoring patterns
│
├── LOGGING_STANDARDS.md            # Logging rules
├── LOGGING_GUIDE.md                # Logging implementation
├── PII_PRIVACY_GUIDE.md            # PII protection and compliance
│
├── LINTING_STANDARDS.md            # Code quality rules
├── LINTING_GUIDE.md                # Linting implementation
├── EXCEPTION_HANDLING_STANDARDS.md # Error handling rules
├── EXCEPTION_HANDLING_GUIDE.md     # Error handling patterns
│
└── DEBUGGING.md                    # Troubleshooting guide
```

### Domain Organization

Each domain follows hexagonal architecture:

```
app/{domain}/
├── __init__.py              # Exports public service API only
├── models.py                # Domain models with business logic
├── schemas.py               # API DTOs (request/response)
├── db_models.py             # Database models (ORM)
├── service.py               # Business logic & orchestration (PORTS)
├── repository.py            # Data access layer (SECONDARY ADAPTER)
├── router.py                # HTTP endpoints (PRIMARY ADAPTER)
└── events.py                # Domain event definitions
```

**Critical Layer Rules:**
- **Service layer** = Ports (public API, business orchestration)
- **Router** = Primary adapter (HTTP → domain)
- **Repository** = Secondary adapter (domain → database)
- **Event bus** = Secondary adapter (domain → analytics/notifications)

Cross-domain communication goes through service layer APIs only.

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Local Development

```bash
cd declaring

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Run on different port
uvicorn main:app --reload --port 8001
```

**Server runs at:** `http://localhost:8000`

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### Docker (Production)

```bash
cd declaring

# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Testing

This project follows **Test-Driven Development (TDD)** practices. See [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) for the mandatory workflow.

### Run Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -m unit

# Integration tests
pytest tests/integration -m integration

# API tests
pytest tests/api -m api

# With coverage (80%+ required)
pytest --cov=app --cov-report=html --cov-fail-under=80

# View coverage report
open htmlcov/index.html
```

### Coverage Requirements

- **Models:** 90%+ coverage
- **Service layer:** 85%+ coverage
- **Repository:** 80%+ coverage
- **Overall:** 80%+ coverage

All business actions must test event publishing.

## Architecture Principles

### 1. Hexagonal Architecture

Business logic lives in the core (domain models + service layer). Infrastructure adapters connect at the boundaries.

### 2. Domain-Driven Design

Code is organized by business domains (intents, items, users), not technical layers.

### 3. Event-Driven Communication

All significant business actions publish domain events for analytics, logging, and cross-domain decoupling.

### 4. Model Separation

Three distinct model types:
- **DB models** (`db_models.py`) - Database schema with audit fields
- **Domain models** (`models.py`) - Business entities with validation and logic
- **API DTOs** (`schemas.py`) - Request/response contracts (no sensitive data)

### 5. Ports & Adapters

**Ports (Service layer functions):**
```python
# Other domains call through service ports
from app.items import service as item_service
item = await item_service.get_item(item_id)
```

**Primary Adapters (drive the core):**
- HTTP routers
- CLI tools (future)
- GraphQL API (future)

**Secondary Adapters (driven by core):**
- Database repository
- Event bus
- External APIs (future)

## Key Features

### Structured Logging with PII Protection

- JSON format for easy parsing by CloudWatch, Datadog, Kibana
- Automatic PII redaction (emails, phones, credit cards, SSNs)
- Hash-based user correlation without exposing PII
- GDPR, CCPA, HIPAA compliance support

```bash
# Pretty-print logs during development
uvicorn main:app --reload | jq '.'
```

See [LOGGING_GUIDE.md](./LOGGING_GUIDE.md) for details.

### Code Quality & Linting

Automated linting with Black, isort, Flake8, and mypy:

```bash
# Install dev tools
pip install -e '.[dev]'

# Check code quality
./lint.sh

# Auto-fix issues
./lint.sh --fix
```

See [LINTING_STANDARDS.md](./LINTING_STANDARDS.md) for mandatory rules.

### Exception Handling

Standardized error handling with proper HTTP status codes:

- `400` - Validation errors
- `404` - Resource not found
- `422` - Unprocessable entity
- `500` - Internal server error

See [EXCEPTION_HANDLING_GUIDE.md](./EXCEPTION_HANDLING_GUIDE.md) for patterns.

## Adding New Features

### Create a New Domain

Follow TDD workflow from [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md):

1. **Plan** - Define domain model and contracts
2. **Test First** - Write failing tests
3. **Implement** - Make tests pass
4. **Events** - Publish domain events
5. **Integration** - Test cross-domain scenarios
6. **Documentation** - Update domain docs

**Essential checklist:**
- [ ] Domain models with business logic (`models.py`)
- [ ] API DTOs excluding sensitive data (`schemas.py`)
- [ ] Service layer with business orchestration (`service.py`)
- [ ] Repository for data access (`repository.py`)
- [ ] HTTP router (`router.py`)
- [ ] Domain events (`events.py`)
- [ ] Export service API in `__init__.py`
- [ ] Tests with 80%+ coverage
- [ ] Domain documentation (`{DOMAIN}_DOMAIN.md`)

See [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) for detailed examples.

## Frontend Integration

The React frontend (at `../reacting/`) is a **primary adapter** that consumes this backend's HTTP API.

**Key points:**
- Frontend has NO business logic (presentation only)
- All business rules live in this backend
- Frontend types mirror `schemas.py` (API DTOs), not `models.py`
- CORS is configured for common dev ports (3000, 5173, 8080)

See [DEBUGGING.md](./DEBUGGING.md) for troubleshooting frontend-backend integration.

## Documentation Index

### Architecture
- [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) - Mandatory rules
- [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) - Detailed patterns
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick lookup

### Development
- [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) - TDD workflow (MANDATORY)
- [TESTING_STANDARDS.md](./TESTING_STANDARDS.md) - Testing requirements
- [REFACTORING_GUIDE.md](./REFACTORING_GUIDE.md) - Safe refactoring

### Code Quality
- [LINTING_STANDARDS.md](./LINTING_STANDARDS.md) - Linting rules
- [LINTING_GUIDE.md](./LINTING_GUIDE.md) - Implementation guide
- [EXCEPTION_HANDLING_STANDARDS.md](./EXCEPTION_HANDLING_STANDARDS.md) - Error handling rules
- [EXCEPTION_HANDLING_GUIDE.md](./EXCEPTION_HANDLING_GUIDE.md) - Error patterns

### Operations
- [LOGGING_STANDARDS.md](./LOGGING_STANDARDS.md) - Logging requirements
- [LOGGING_GUIDE.md](./LOGGING_GUIDE.md) - Structured logging
- [PII_PRIVACY_GUIDE.md](./PII_PRIVACY_GUIDE.md) - Privacy compliance
- [DEBUGGING.md](./DEBUGGING.md) - Troubleshooting

## Troubleshooting

### Port already in use
```bash
uvicorn main:app --reload --port 8001
```

### Module not found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CORS errors from frontend
Add frontend URL to `origins` list in `app/main.py`.

### Tests failing
Ensure 80%+ coverage and all event publishing is tested.

See [DEBUGGING.md](./DEBUGGING.md) for complete troubleshooting guide.

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hexagonal Architecture (Ports and Adapters)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

## Need Help?

1. Check [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for common patterns
2. Read relevant STANDARDS.md and GUIDE.md files
3. Review [CLAUDE.md](../CLAUDE.md) for full-stack context
4. Explore API docs at `/docs`
