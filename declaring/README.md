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

## API Key Authentication

The server supports optional API key authentication via the `Authorization` header. This is useful when exposing the server to the internet (e.g., via ngrok).

### Enabling API Key Authentication

1. **Set environment variables:**
```bash
export ENABLE_API_KEY_AUTH=true
export API_KEY=your-secret-api-key-here
```

Or create a `.env` file:
```bash
ENABLE_API_KEY_AUTH=true
API_KEY=your-secret-api-key-here
```

2. **Restart the server** for changes to take effect.

### Using API Key Authentication

Once enabled, all API endpoints (except public endpoints) require authentication.

**Supported Authorization header formats:**
- `Authorization: Bearer <api-key>`
- `Authorization: <api-key>`

**Public endpoints (no authentication required):**
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI schema

**Example requests with API key:**

```bash
# Using Bearer format
curl -H "Authorization: Bearer your-secret-api-key-here" \
  http://localhost:8000/users

# Using direct format
curl -H "Authorization: your-secret-api-key-here" \
  http://localhost:8000/users
```

### Disabling API Key Authentication

By default, API key authentication is **disabled** for local development. To disable it explicitly:

```bash
export ENABLE_API_KEY_AUTH=false
# Or simply don't set the variable
```

## Exposing Server to Internet with Ngrok

Ngrok allows you to expose your local server to the internet securely, which is useful for:
- Testing webhooks
- Sharing your API with others
- Mobile app development
- Integration testing

### Installing Ngrok

1. **Download ngrok:**
   - Visit https://ngrok.com/download
   - Or use package manager:
     ```bash
     # macOS
     brew install ngrok/ngrok/ngrok
     
     # Linux
     wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
     tar -xzf ngrok-v3-stable-linux-amd64.tgz
     sudo mv ngrok /usr/local/bin
     ```

2. **Sign up for a free account** at https://dashboard.ngrok.com/signup

3. **Get your authtoken** from https://dashboard.ngrok.com/get-started/your-authtoken

4. **Configure ngrok:**
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### Basic Usage

1. **Start your FastAPI server:**
```bash
cd declaring
uvicorn main:app --reload
```

2. **In a separate terminal, start ngrok:**
```bash
ngrok http 8000
```

Ngrok will display something like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

3. **Your server is now accessible at the ngrok URL!**

### Using Ngrok with API Key Authentication

**Important:** When exposing your server to the internet, you **must** enable API key authentication to prevent unauthorized access.

1. **Enable API key authentication:**
```bash
export ENABLE_API_KEY_AUTH=true
export API_KEY=your-secret-api-key-here
```

2. **Start the server:**
```bash
uvicorn main:app --reload
```

3. **Start ngrok:**
```bash
ngrok http 8000
```

4. **Test the exposed endpoint:**
```bash
# This should fail without API key
curl https://abc123.ngrok-free.app/users

# This should work with API key
curl -H "Authorization: Bearer your-secret-api-key-here" \
  https://abc123.ngrok-free.app/users
```

### API Key Best Practices

**Generating Strong API Keys:**

```bash
# Generate a secure 32-character API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Security Requirements:**
- ✅ Minimum 32 characters
- ✅ Use randomly generated keys (not passwords)
- ✅ Never commit keys to version control
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate keys regularly
- ✅ Use different keys per environment

**⚠️ Environment Variable Security:**
- Don't use `export` (leaves keys in shell history)
- Use `.env` files instead
- In production, use secure secret management (AWS Secrets Manager, HashiCorp Vault)
- Never log or print API keys
- Be aware: `ps auxe` can show environment variables

### Security Best Practices

⚠️ **Important Security Notes:**

1. **Always enable API key authentication** when using ngrok
   - Your server will be accessible to anyone with the ngrok URL
   - Without authentication, anyone can access your API

2. **Use strong API keys** (see API Key Best Practices above)
   - Generate random, long strings (at least 32 characters)
   - Don't use predictable values like "test" or "password"

3. **Rotate API keys regularly**
   - Change your API key if it's been exposed
   - Use different keys for different environments

4. **Monitor ngrok traffic**
   - Check the ngrok web interface (http://localhost:4040) regularly
   - Look for suspicious requests

5. **Don't expose production servers**
   - Only use ngrok for development and testing
   - Production should use proper hosting with HTTPS

### ⚠️ Security Considerations for Internet Exposure

**IMPORTANT:** This setup does NOT include:
- ❌ Rate limiting (vulnerable to DoS and brute force)
- ❌ Request logging for security monitoring
- ❌ DDoS protection
- ❌ IP whitelisting
- ❌ Failed authentication attempt tracking

**Before exposing to the internet:**
1. **Enable API key authentication** (required)
2. **Use strong API keys** (see best practices above)
3. **Monitor logs** for suspicious activity
4. **Consider rate limiting** via nginx or FastAPI-limiter

**For production deployments, use:**
- Nginx reverse proxy with rate limiting
- Fail2ban for brute force protection
- Proper TLS/SSL certificates
- Web Application Firewall (WAF)
- Secret management service (AWS Secrets Manager, Vault)

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

## Development Workflow

**Before writing code:** Read [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) for the mandatory TDD workflow, code quality checklist, and validation steps.

**Key reminders:**
- This project uses **Test-Driven Development (TDD)** - write tests first
- Run `./lint.sh --fix` and `pytest` before committing
- Refer to [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) for architectural rules
- Check [TODO.md](../TODO.md) for pending architectural decisions

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
