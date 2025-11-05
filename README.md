# Gen Consult

A full-stack learning project demonstrating **hexagonal architecture** with strict separation between backend and frontend.

## 🏗️ Architecture Philosophy

This repository follows **hexagonal (ports and adapters) architecture** with a focus on **decomposition** and **clear boundaries**.

```
┌─────────────────────────────────────────────┐
│    BACKEND = THE HEXAGON (Business Core)    │
│  - Domain-driven architecture               │
│  - Event-based communication                │
│  - ALL business logic lives here            │
└─────────────────────────────────────────────┘
                    ▲
                    │ HTTP API (Port)
                    │
┌─────────────────────────────────────────────┐
│  FRONTEND = PRIMARY ADAPTER (Thin Client)   │
│  - Presentation and UX only                 │
│  - NO business logic                        │
│  - Consumes backend through HTTP            │
└─────────────────────────────────────────────┘
```

## 📁 Repository Structure

```
gen_consult/
├── declaring/              # Backend - FastAPI (Python)
│   ├── app/
│   │   ├── items/         # Domain: Items
│   │   ├── users/         # Domain: Users
│   │   └── shared/        # Cross-cutting concerns
│   ├── tests/
│   ├── requirements.txt
│   └── README.md          # Backend documentation
│
├── reacting/              # Frontend - React (JavaScript)
│   ├── src/
│   │   ├── features/      # Feature-based (mirrors backend domains)
│   │   └── shared/
│   ├── package.json
│   └── README.md          # Frontend documentation
│
├── .github/
│   └── workflows/         # CI/CD pipelines
│
├── CLAUDE.md              # Architecture guidance for AI assistants
├── TODO.md                # Current tasks and decisions
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Backend:** Python 3.14+
- **Frontend:** Node.js 18+
- **Tools:** Git, Docker (optional)

### Backend Setup

```bash
cd declaring

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Run tests
pytest --cov=app
```

Backend runs at: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd reacting

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

Frontend runs at: `http://localhost:5173`

### Docker Setup (Optional)

```bash
cd declaring
docker-compose up --build
```

## 📚 Documentation

- **[DOCUMENTATION_ORGANIZATION.md](./DOCUMENTATION_ORGANIZATION.md)** - How documentation is organized and where to create new documents
- **[CLAUDE.md](./CLAUDE.md)** - Complete architecture guidance and development workflows
- **[TODO.md](./TODO.md)** - Current tasks and architectural decisions needed
- **[Backend Docs](./declaring/)** - FastAPI backend documentation
  - [Architecture Standards](./declaring/ARCHITECTURE_STANDARDS.md)
  - [Architecture Guide](./declaring/ARCHITECTURE_GUIDE.md)
  - [Backend Development Standards](./declaring/DEVELOPMENT_STANDARDS.md)
  - [Testing Standards](./declaring/TESTING_STANDARDS.md)
- **[Frontend Docs](./reacting/)** - React frontend documentation
  - [Architecture](./reacting/ARCHITECTURE.md)

## 🧪 Testing

### Backend Tests
```bash
cd declaring

# All tests
pytest

# Unit tests only
pytest tests/unit -m unit

# With coverage
pytest --cov=app --cov-report=html

# Coverage requirements: 80%+ overall
```

### Frontend Tests
```bash
cd reacting

# Tests (when configured)
npm test

# E2E tests (when configured)
npm run test:e2e
```

## 🛠️ Development Workflow

### Adding a New Feature

1. **Backend (create domain)**
   - Create domain folder in `declaring/app/`
   - Define models, schemas, service, repository
   - Add tests (unit, integration, API)
   - Register router in `main.py`

2. **Frontend (create feature)**
   - Create feature folder in `reacting/src/features/`
   - Build API client, hooks, components
   - Keep thin - delegate to backend

3. **Integration**
   - Test end-to-end flow
   - Update documentation

See [CLAUDE.md](./CLAUDE.md) for detailed workflows.

## 🔑 Key Principles

1. **Hexagonal Boundaries** - Backend is the business core, frontend is an adapter
2. **Decomposition** - Organize by domain/feature, not technical layer
3. **Event-Driven** - All significant business actions publish domain events
4. **Model Separation** - DB models, domain models, and API DTOs are separate
5. **Thin Client** - No business logic in frontend
6. **Test Coverage** - Minimum 80% coverage required

## 🤝 Contributing

### Before Making Changes

1. Check [TODO.md](./TODO.md) for pending architectural decisions
2. Review [CLAUDE.md](./CLAUDE.md) for architecture guidelines
3. Ensure tests pass and coverage requirements are met
4. Follow the established patterns in existing code

### Pull Request Guidelines

- Clear description of changes
- Tests included and passing
- Documentation updated
- Follows architecture standards
- No business logic in frontend
- Events published for business actions

## 📝 License

[Add your license here]

## 👥 Authors

[Add authors/contributors]

## 🙏 Acknowledgments

This project demonstrates best practices in:
- Hexagonal (ports and adapters) architecture
- Domain-driven design
- Event-driven architecture
- Full-stack development with clear boundaries
