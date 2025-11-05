# Declaring - Backend API

**FastAPI backend implementing hexagonal architecture** - the business core of the Gen Consult project. This backend serves as the hexagon containing all business logic, domain models, and event-driven workflows. The frontend (React) acts as a thin adapter that consumes this API.

## Tech Stack

- **FastAPI** + Python 3.14+
- **Pydantic** for validation
- **Structured JSON logging** with PII protection
- **Event-driven** domain architecture
- **Pytest** for testing with 80%+ coverage requirement

## Quick Start

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload
```

### Access Points

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## Project Structure

```
declaring/
├── app/
│   ├── items/              # Domain: Product/inventory management
│   ├── users/              # Domain: User management
│   ├── intents/            # Domain: AI prompt generation workflow
│   ├── shared/             # Cross-cutting concerns (events, logging, etc.)
│   └── main.py             # Application entry point
├── tests/
│   ├── unit/               # Unit tests (90%+ coverage for models/service)
│   ├── integration/        # Integration tests (80%+ for repository)
│   └── api/                # API endpoint tests
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── pytest.ini              # Test configuration
```

Each domain follows hexagonal architecture:
```
domain/
├── models.py          # Domain models with business logic
├── schemas.py         # API DTOs (request/response)
├── db_models.py       # Database models (ORM)
├── service.py         # Business logic (THE PORT)
├── repository.py      # Data access (secondary adapter)
├── router.py          # HTTP endpoints (primary adapter)
├── events.py          # Domain events
└── __init__.py        # Public API exports
```

## Essential Commands

### Development
```bash
# Run with auto-reload
uvicorn main:app --reload

# Run on different port
uvicorn main:app --reload --port 8001

# Pretty-print logs (requires jq)
uvicorn main:app --reload | jq '.'
```

### Testing
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -m unit

# Integration tests
pytest tests/integration -m integration

# With coverage report
pytest --cov=app --cov-report=html

# View coverage
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Linting & Formatting
```bash
# Auto-fix issues
./lint.sh --fix

# Check only (CI mode)
./lint.sh
```

### Docker
```bash
# Build and run
docker-compose up --build

# Stop
docker-compose down
```

## Architecture at a Glance

- **Backend IS the hexagon** - The business core containing all domain logic
- **Organized by domain** - Items, users, intents (not by technical layers)
- **Service layer = ports** - Public API for cross-domain communication
- **All business actions publish events** - For analytics, logging, and decoupling
- **Three model types:** DB models, domain models, API DTOs (strictly separated)

```
┌─────────────────────────────────────────────┐
│    THIS BACKEND = THE HEXAGON               │
│    (Business Core)                          │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Domain Models & Business Logic      │  │
│  │  Service Layer = PORTS               │  │
│  └──────────────────────────────────────┘  │
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

## Current Domains

### Items
Product and inventory management with CRUD operations, search functionality, and availability tracking.

### Users
User management system with profile handling and domain event publishing.

### Intents
AI prompt generation workflow - captures user intent, facts, and context to iteratively build effective prompts for language models. Tracks prompt versions, outputs, and insights for continuous improvement.

## Documentation Guide

Start with what you need:

### Getting Started
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Commands, API examples, troubleshooting, logging quick reference

### Architecture & Design
- **[ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md)** ⚠️ **MANDATORY** - Rules all code must follow
- **[ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)** - Detailed examples, patterns, migration guide

### Development Workflow
- **[DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md)** ⚠️ **MANDATORY** - TDD workflow, validation checklist
- **[TESTING_STANDARDS.md](./TESTING_STANDARDS.md)** - Coverage requirements, test patterns, examples

### Specialized Topics
- **[LOGGING_STANDARDS.md](./LOGGING_STANDARDS.md)** + **[LOGGING_GUIDE.md](./LOGGING_GUIDE.md)** - Structured logging with PII protection
- **[LINTING_STANDARDS.md](./LINTING_STANDARDS.md)** + **[LINTING_GUIDE.md](./LINTING_GUIDE.md)** - Code quality, formatting, type checking
- **[EXCEPTION_HANDLING_STANDARDS.md](./EXCEPTION_HANDLING_STANDARDS.md)** + **[EXCEPTION_HANDLING_GUIDE.md](./EXCEPTION_HANDLING_GUIDE.md)** - Error handling patterns
- **[PII_PRIVACY_GUIDE.md](./PII_PRIVACY_GUIDE.md)** - Privacy protection and data handling
- **[REFACTORING_GUIDE.md](./REFACTORING_GUIDE.md)** - Safe refactoring practices
- **[DEBUGGING.md](./DEBUGGING.md)** - Debugging full-stack integration

### Related Documentation
- **[Root README](../README.md)** - Full-stack project overview
- **[CLAUDE.md](../CLAUDE.md)** - Architecture guidance for AI assistants
- **[Frontend README](../reacting/README.md)** - React frontend documentation

## Development Best Practices

### Before Writing Code
1. **Read DEVELOPMENT_STANDARDS.md** - Understand TDD workflow
2. **Check TODO.md** - Review pending architectural decisions
3. **Review existing domain** - Follow established patterns

### TDD Workflow (MANDATORY)
1. Write failing test (Red)
2. Write minimal code to pass (Green)
3. Refactor while keeping tests green
4. Run `./lint.sh --fix` and `pytest` before committing

### Code Quality Checklist
- [ ] Tests written first and passing
- [ ] Coverage meets requirements (80%+ overall)
- [ ] Linting passes (`./lint.sh`)
- [ ] Business logic in service layer only
- [ ] Domain events published for business actions
- [ ] No sensitive data in schemas/logs
- [ ] Documentation updated

### Common Anti-Patterns to Avoid
- ❌ Business logic in routers
- ❌ Direct cross-domain repository access
- ❌ Forgetting to publish domain events
- ❌ Mixing domain models and API DTOs
- ❌ Exposing sensitive fields in schemas
- ❌ Service layer knowing about HTTP details

## Contributing

This is a learning project demonstrating:
- Hexagonal (ports and adapters) architecture
- Domain-driven design
- Event-driven architecture
- Test-driven development
- Clear separation between business logic and infrastructure

All code changes must follow the documented standards and maintain the architectural principles.

---

**Need help?** Check [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for quick answers or [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) for detailed examples.
