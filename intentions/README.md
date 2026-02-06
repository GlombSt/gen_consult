# Intentions - Backend API

**FastAPI backend implementing hexagonal architecture** - the business core of the Gen Consult project. This backend serves as the hexagon containing all business logic, domain models, and event-driven workflows. The frontend (React) acts as a thin adapter that consumes this API.

## Tech Stack

- **FastAPI** + Python 3.13+
- **Pydantic** for validation
- **Structured JSON logging** with PII protection
- **Event-driven** domain architecture
- **Pytest** for testing with 80%+ coverage requirement

## Quick Start

### Setup

```bash
cd intentions

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (runtime + dev for lint/tests)
pip install -e ".[dev]"

# Run development server
uvicorn main:app --reload

# Run tests
pytest --cov=app
```

### Access Points

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **MCP Server:** http://localhost:8000/mcp (for Claude Desktop and other MCP clients)

## Database Configuration

The backend uses **SQLAlchemy** with async support. Database configuration is environment-based:

**Development (Default):**
- Uses **in-memory SQLite** - no setup required
- Tables are auto-created on startup
- Perfect for local development and testing

**Production:**
- Uses **PostgreSQL** (configured via environment variables)
- Requires Alembic migrations for schema management
- Set the following environment variables:

```bash
export DATABASE_TYPE=postgresql
export DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Environment Variables:**
- `DATABASE_TYPE`: Database type (`sqlite` or `postgresql`, default: `sqlite`)
- `DATABASE_URL`: Full database connection URL (required for PostgreSQL)

**Testing:**
- Tests use in-memory SQLite automatically
- No external database required for running tests
- Each test gets a fresh database instance

**Transaction Management:**
- Each HTTP request gets its own transaction boundary
- Transactions auto-commit on success, auto-rollback on error
- For complex multi-step operations, all operations within a single request share the same transaction

See [Database Configuration](./app/shared/database.py) for implementation details.

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
cd intentions
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
intentions/
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
├── pyproject.toml          # Project metadata and dependencies
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

# Coverage requirements: 80%+ overall
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

## MCP Server

The backend exposes its functionality via **Model Context Protocol (MCP)** for use with AI assistants like Claude Desktop. The MCP server acts as a primary adapter (like the HTTP router) that uses the service layer as the port.

### Running the MCP Server

The MCP server is integrated into the FastAPI application and uses **Streamable HTTP transport**. It runs alongside the HTTP API and is accessible at the `/mcp` endpoint.

**To use with Claude Desktop:**

1. Start the FastAPI server:
   ```bash
   cd intentions
   uvicorn app.main:app --reload
   ```

2. Configure Claude Desktop (see [Claude Desktop Configuration](#claude-desktop-configuration) below)

The MCP server is now available at `http://localhost:8000/mcp` (or your configured host/port).

**Note:** The stdio transport entry point (`mcp_server.py`) is deprecated but kept for backwards compatibility with stdio-based clients.

### Available Tools

The MCP server exposes the **Intents Domain V2** with the intent treated as a **composition** of Aspect and articulation entities (Input, Choice, Pitfall, Assumption, Quality). There are no separate tools for articulation entities—they are managed through the intent tools. **Examples** are excluded from the MCP surface (not in create/update payloads or get_intent response). See [INTENTS_DOMAIN_V2.md](app/intents/INTENTS_DOMAIN_V2.md) for the domain model.

**Intent (composition):**
- `create_intent` - Create a new intent with name and description; optionally include nested aspects, inputs, choices, pitfalls, assumptions, qualities (no examples)
- `get_intent` - Get intent by ID with full composition (aspects, inputs, choices, pitfalls, assumptions, qualities, prompts, insights; examples omitted)
- `list_intents` - List all intents with full composition (examples omitted)
- `delete_intent` - Delete an intent by ID
- `update_intent_name` - Update an intent's name
- `update_intent_description` - Update an intent's description
- `update_intent_articulation` - Replace the full articulation composition for an intent (aspects, inputs, choices, pitfalls, assumptions, qualities); omitted fields left unchanged, empty array clears that type; no examples

**Execution and learning (append-only):**
- `add_prompt` - Add a versioned prompt to an intent
- `add_output` - Add an output (AI response) to a prompt
- `add_insight` - Add an insight to an intent (optional: source_type, source_output_id, source_prompt_id, source_assumption_id, status)

### MCP Client Configuration

#### Claude Desktop Configuration

Claude Desktop supports HTTP transport for MCP servers. To use the intents MCP server with Claude Desktop:

1. **Start the FastAPI server:**
   ```bash
   cd intentions
   uvicorn app.main:app --reload
   ```

2. **Locate Claude Desktop configuration file:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

3. **Edit the configuration file** THIS IS FOR DEVELOPMENT (create it if it doesn't exist):
   ```json
   {
     "mcpServers": {
        "intents": {
          "command": "npx",
          "args": [
            "-y",
            "mcp-remote",
            "http://localhost:8000/mcp"
          ]
        }
   }
   ```

4. **Restart Claude Desktop** for the changes to take effect.

5. **Verify the connection:**
   - Open Claude Desktop
   - The MCP server should appear in the available tools
   - You can ask Claude to list available tools or create an intent

**Note:** If your FastAPI server is running on a different port, update the URL accordingly (e.g., `http://localhost:8001/mcp`).

**Troubleshooting:**
- Ensure the FastAPI server is running before starting Claude Desktop
- Check that the URL in the config matches your server's host and port
- Verify the `/mcp` endpoint is accessible: `curl http://localhost:8000/mcp` (should return a JSON-RPC error, not 404)
- Check Claude Desktop logs for connection errors

#### Other MCP Clients (HTTP Transport)

For other clients that support HTTP transport, configure the MCP server URL:

```json
{
  "mcpServers": {
    "intents": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Note:** Replace `localhost:8000` with your actual server host and port.

#### Using with mcptools

The server exposes **Streamable HTTP** at `/mcp` (official MCP Python SDK). If your mcptools version supports Streamable HTTP, use:

```bash
mcp tools http://localhost:8000/mcp
```

If you see `Error: timeout waiting for endpoint`, your mcptools build is likely still using the legacy **HTTP+SSE** transport. Use the SSE endpoint instead:

```bash
mcp tools http://localhost:8000/sse
```

If you prefer **stdio transport** (e.g. for scripting), use:

```bash
cd intentions
mcp tools uv run python mcp_server.py
```

Example: list tools, then call one:

```bash
mcp tools uv run python mcp_server.py
mcp call create_intent --params '{"name":"My intent","description":"Test"}' uv run python mcp_server.py
```

Run each command from the `intentions` directory so the app and database are found. To use an alias:

```bash
cd intentions
mcp alias add intents uv run python mcp_server.py
mcp tools intents
```

#### Stdio Transport Configuration (Deprecated)

For backwards compatibility with stdio-based clients, you can still use the deprecated stdio entry point:

```json
{
  "mcpServers": {
    "intents": {
      "command": "python",
      "args": ["/absolute/path/to/gen_consult/intentions/mcp_server.py"]
    }
  }
}
```

**Note:** The stdio transport is deprecated. Use HTTP transport when possible.

### Testing the MCP Server

**HTTP Transport Testing:**

You can test the MCP server using HTTP clients or the MCP Inspector with HTTP transport:

```bash
# Install MCP Inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Test with HTTP transport (recommended)
# First, start the FastAPI server:
uvicorn app.main:app --reload

# Then use MCP Inspector with HTTP URL
# The inspector will connect to http://localhost:8000/mcp
```

You can also test directly with HTTP requests:

```bash
# Initialize the MCP server
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {}
  }'

# List available tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Stdio Transport Testing (Deprecated):**

For testing the deprecated stdio transport:

```bash
# Run inspector with the stdio MCP server
npx @modelcontextprotocol/inspector python mcp_server.py
```

This will start an interactive session where you can:
- List available tools
- Call tools with arguments
- See tool responses

### Architecture

The MCP server follows hexagonal architecture principles:

```
MCP Server (Primary Adapter)
    ↓
Service Layer (Port)
    ↓
Repository (Secondary Adapter)
    ↓
Database
```

- **MCP Server** (`app/intents/mcp_server.py`) - Exposes service functions as MCP tools
- **MCP HTTP Transport** (`app/intents/mcp_http.py`) - HTTP transport wrapper for MCP server
- **Service Layer** (`app/intents/service.py`) - Business logic (the port)
- **Schemas** (`app/intents/schemas.py`) - Single source of truth for parameter documentation
- **Service Docstrings** - Single source of truth for operation descriptions

### Security Considerations

**IMPORTANT**: The MCP endpoint (`/mcp`) does NOT require API key authentication.

**Origin Validation:**
The MCP HTTP endpoint includes Origin header validation to prevent DNS rebinding attacks. Configure allowed origins via the `MCP_ALLOWED_ORIGINS` environment variable.

**Production Deployment Options:**
1. **Network-level protection** - Use firewall rules to restrict access to the MCP endpoint
2. **Reverse proxy authentication** - Use nginx/Caddy with authentication in front of FastAPI
3. **Origin restrictions** - Set `MCP_ALLOWED_ORIGINS` to specific trusted origins (comma-separated)
4. **API key authentication** - Add MCP-specific authentication if needed (future enhancement)

**Local Development:**
- Default `MCP_ALLOWED_ORIGINS=*` is safe (only accessible from localhost)
- When exposing with ngrok or similar tools, **change to specific origins**:
  ```bash
  export MCP_ALLOWED_ORIGINS="https://your-domain.ngrok.io"
  ```

**Example Production Configuration:**
```bash
# Restrict to specific origins
export MCP_ALLOWED_ORIGINS="https://app.example.com,https://admin.example.com"
```

See [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) for documentation standards.

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
- **[Frontend README](../customer-ux/README.md)** - React frontend documentation

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
