# My First FastAPI Backend

A simple FastAPI backend project to help you get started with Python backend development!

## What is FastAPI?

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python. It's easy to learn, fast to code, and production-ready.

## Project Structure

```
declaring/
├── main.py                         # Main application file with API endpoints
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project config & linting rules
├── lint.sh                         # Linting script (./lint.sh --fix)
├── Dockerfile                      # Docker container configuration
├── docker-compose.yml              # Docker Compose for easy deployment
├── .dockerignore                  # Files to exclude from Docker build
├── README.md                       # This file (start here!)
├── QUICK_REFERENCE.md             # ⭐ Quick reference card
├── LINTING_GUIDE.md               # Code quality and linting guide
├── DEBUGGING.md                   # Debugging guide for React + FastAPI
├── LOGGING_ARCHITECTURE.md        # Deep dive into logging system
├── CLOUD_NATIVE_LOGGING.md        # Cloud & container deployment guide
├── STRUCTURED_LOGGING_EXAMPLES.md # Structured logging output examples
├── PII_PRIVACY_GUIDE.md           # PII protection and privacy compliance
└── react-example.jsx              # Example React components
```

## Setup Instructions

You can run this application in two ways:
1. **Local development** (with Python directly)
2. **Docker container** (recommended for production)

### Option A: Local Development

#### 1. Install Python

Make sure you have Python 3.8 or higher installed. Check your version:

```bash
python3 --version
```

#### 2. Create a Virtual Environment (Recommended)

A virtual environment keeps your project dependencies isolated:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

You'll see `(venv)` in your terminal when it's activated.

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI**: The web framework
- **Uvicorn**: The server to run your app
- **Pydantic**: For data validation
- **Python-multipart**: For handling form data

#### 4. Run the Application

```bash
uvicorn main:app --reload
```

The `--reload` flag makes the server restart when you change the code (great for development!).

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Option B: Docker (Recommended for Production)

#### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed on your machine
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

#### Quick Start with Docker Compose

```bash
# Build and run the container
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The API will be available at `http://localhost:8000`

#### Manual Docker Commands

```bash
# Build the Docker image
docker build -t fastapi-app .

# Run the container
docker run -p 8000:8000 fastapi-app

# Run with environment variables
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e ENVIRONMENT=production \
  fastapi-app

# View logs
docker logs -f <container-id>

# Stop the container
docker stop <container-id>
```

#### Why Use Docker?

✅ **Consistent environment** - Works the same everywhere  
✅ **Easy deployment** - Deploy to any cloud platform  
✅ **Isolation** - Doesn't interfere with other projects  
✅ **Production-ready** - Same setup for dev and production  
✅ **Cloud-native** - Ready for Kubernetes, AWS, GCP, Azure  

See **`CLOUD_NATIVE_LOGGING.md`** for detailed deployment guides for:
- AWS (ECS, EKS, Fargate)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Apps, AKS)
- Kubernetes

## Using Your API

### Interactive API Documentation

FastAPI automatically generates interactive API documentation! Open your browser and visit:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

You can test all your endpoints directly from the browser!

### Example API Calls

#### 1. Check if the API is running
```bash
curl http://127.0.0.1:8000/health
```

#### 2. Create a new item
```bash
curl -X POST "http://127.0.0.1:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "A powerful laptop",
    "price": 999.99,
    "is_available": true
  }'
```

#### 3. Get all items
```bash
curl http://127.0.0.1:8000/items
```

#### 4. Get a specific item (replace 1 with the item ID)
```bash
curl http://127.0.0.1:8000/items/1
```

#### 5. Search items with filters
```bash
curl "http://127.0.0.1:8000/search?name=laptop&min_price=500&available_only=true"
```

#### 6. Create a user
```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com"
  }'
```

## Available Endpoints

### General
- `GET /` - Welcome message
- `GET /health` - Health check

### Items
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get a specific item
- `POST /items` - Create a new item
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item

### Users
- `GET /users` - Get all users
- `POST /users` - Create a new user

### Search
- `GET /search` - Search items with filters (name, min_price, max_price, available_only)

## Understanding the Code

### main.py Structure

1. **Imports**: Import FastAPI and other necessary modules
2. **App Creation**: Create the FastAPI application instance
3. **Data Models**: Define Pydantic models for data validation
4. **In-memory Storage**: Simple lists to store data (in production, you'd use a database)
5. **Endpoints**: Functions decorated with `@app.get()`, `@app.post()`, etc.

### Key Concepts

- **Path Parameters**: `/items/{item_id}` - Dynamic values in the URL
- **Query Parameters**: `/search?name=laptop` - Optional filters
- **Request Body**: Data sent with POST/PUT requests
- **Response Models**: Automatic validation and documentation of responses
- **HTTP Status Codes**: 200 (OK), 201 (Created), 404 (Not Found), etc.

## Logging & Debugging

This FastAPI backend includes **comprehensive structured logging** to help you debug and monitor your application:

### Structured Logging (JSON Format) with PII Protection

The application uses **structured logging** with automatic **PII (Personally Identifiable Information) protection**:
- ✅ **Structured JSON format** - Easy to parse by log aggregation tools (CloudWatch, Datadog, Kibana)
- ✅ **Automatic PII redaction** - Emails, phone numbers, credit cards, SSNs automatically redacted
- ✅ **Compliance-ready** - Helps with GDPR, CCPA, HIPAA compliance
- ✅ **Searchable and filterable** by any field
- ✅ **Hash-based correlation** - Track users without logging PII
- ✅ **Perfect for cloud environments** and production monitoring
- ✅ **Zero external dependencies** - Uses Python's built-in libraries

### What's Logged
- ✅ All incoming HTTP requests (method, path, client IP, user agent, origin)
- ✅ Response status codes and processing time
- ✅ Endpoint-specific actions with relevant data
- ✅ Errors with full exception details and stack traces
- ✅ Application startup information

### View Logs
When you run the server, you'll see JSON logs in your terminal:
```bash
uvicorn main:app --reload
```

Example output:
```json
{"timestamp":"2025-10-27T14:30:45.123456Z","level":"INFO","logger":"fastapi_app","message":"Application starting","environment":"development","log_level":"INFO","cors_origins_count":9}
{"timestamp":"2025-10-27T14:30:50.789012Z","level":"INFO","logger":"fastapi_app","message":"Incoming request","method":"GET","path":"/items","client_ip":"127.0.0.1","user_agent":"curl/7.81.0","origin":null}
{"timestamp":"2025-10-27T14:30:50.790123Z","level":"INFO","logger":"fastapi_app","message":"Fetching all items","total_items":5}
{"timestamp":"2025-10-27T14:30:50.795678Z","level":"INFO","logger":"fastapi_app","message":"Request completed","method":"GET","path":"/items","status_code":200,"duration":0.006}
```

### Pretty-Print Logs (Development)

For better readability during development, pipe logs through `jq`:
```bash
# Local development
uvicorn main:app --reload | jq '.'

# Docker
docker-compose logs -f api | jq '.'
```

See **`STRUCTURED_LOGGING_EXAMPLES.md`** for:
- Complete log output examples
- How to query logs in CloudWatch, Kibana, Datadog
- Filtering and searching techniques
- Creating dashboards and alerts

### PII Protection

The application automatically protects sensitive data in logs:

**What's automatically redacted:**
- 📧 Email addresses → `[EMAIL_REDACTED]`
- 📱 Phone numbers → `[PHONE_REDACTED]`
- 💳 Credit card numbers → `[CC_REDACTED]`
- 🔐 Passwords, API keys, tokens → `[REDACTED]`
- 🆔 SSNs and sensitive IDs → `[SSN_REDACTED]`

**Example:**
```python
# If you accidentally try to log PII:
logger.info("Contact john.doe@example.com or call 555-123-4567")

# It gets automatically sanitized:
{"message": "Contact [EMAIL_REDACTED] or call [PHONE_REDACTED]"}
```

**For user correlation without exposing PII:**
```python
# Use hash-based identifiers
email_hash = PIISanitizer.hash_identifier(user.email)
logger.info("User action", extra={'email_hash': email_hash})
```

See **`PII_PRIVACY_GUIDE.md`** for:
- Complete PII protection guide
- What to log and what not to log
- Compliance requirements (GDPR, CCPA, HIPAA)
- Best practices and examples

### Connecting from React
If you're building a React frontend:
1. Check **`DEBUGGING.md`** for a complete troubleshooting guide
2. See **`react-example.jsx`** for working React component examples
3. Make sure your React app's origin is in the CORS allowed list
4. Watch the logs to see if requests are reaching your backend

Common issues:
- **CORS errors**: Add your React app's URL to the `origins` list in `main.py`
- **404 errors**: Make sure the URL path matches (e.g., `/items` not `/api/items`)
- **Network errors**: Verify FastAPI is running and the port is correct

## Code Quality & Linting

This project uses automated linting tools to maintain code quality:

### Quick Start

```bash
# Install linting tools
pip install -e '.[dev]'

# Check all linting rules
./lint.sh

# Fix auto-fixable issues
./lint.sh --fix
```

### Linting Tools

- **Black** - Automatic code formatting
- **isort** - Import sorting and organization  
- **Flake8** - Code quality and style checks
- **mypy** - Static type checking

All linting rules are configured in `pyproject.toml`. For detailed guidance, see **`LINTING_GUIDE.md`**.

### CI/CD

Linting runs automatically on every push and pull request via GitHub Actions. Code must pass all checks before merging.

## Next Steps

Here are some ideas to extend your backend:

1. **Add a Database**: Replace in-memory storage with SQLite, PostgreSQL, or MongoDB
2. **Authentication**: Add user login and JWT tokens
3. **Environment Variables**: Use `.env` files for configuration
4. **Testing**: Add unit tests with pytest
5. **Deployment**: Deploy to platforms like Heroku, Railway, or AWS

## Learning Resources

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)

## Troubleshooting

### Port already in use?
```bash
# Use a different port
uvicorn main:app --reload --port 8001
```

### Module not found?
Make sure your virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Need Help?

- Check the interactive docs at `/docs`
- Read the FastAPI documentation
- Look at the code comments in `main.py`

Happy coding! 🚀

