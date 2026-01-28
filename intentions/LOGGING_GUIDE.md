# Logging Guide

**Companion to:** [LOGGING_STANDARDS.md](./LOGGING_STANDARDS.md)
**Version:** 1.0
**Last Updated:** December 2025
**Audience:** Developers implementing logging in FastAPI applications

**Related Documentation:**
- [Logging Standards](./LOGGING_STANDARDS.md) - Mandatory rules (read first!)
- [PII Privacy Guide](./PII_PRIVACY_GUIDE.md) - PII protection guidance
- [Architecture Standards](./ARCHITECTURE_STANDARDS.md) - Hexagonal architecture rules

---

## Table of Contents

1. [Framework Overview](#framework-overview)
2. [Logger Configuration](#logger-configuration)
3. [Log Levels Explained](#log-levels-explained)
4. [FastAPI Middleware Implementation](#fastapi-middleware-implementation)
5. [Endpoint-Specific Logging](#endpoint-specific-logging)
6. [Structured Logging](#structured-logging)
7. [Exception Logging Patterns](#exception-logging-patterns)
8. [Production Configuration](#production-configuration)
9. [Advanced Concepts](#advanced-concepts)
10. [Extending the System](#extending-the-system)

---

## Framework Overview

### Python's `logging` Module

The logging system uses **Python's built-in `logging` module** (no external dependencies needed!) combined with **FastAPI's middleware system** to create comprehensive request/response logging.

**Why use Python's built-in logging?**
- ✅ **Built-in**: No need to install external packages
- ✅ **Standardized**: Industry-standard logging in Python
- ✅ **Flexible**: Multiple log levels, handlers, formatters
- ✅ **Production-ready**: Used in enterprise applications

**Alternative logging libraries:**
- **Loguru**: More user-friendly, colorful output
- **structlog**: Structured logging for complex applications
- **Python-json-logger**: JSON formatted logs

**For this project:** Standard logging is best for simplicity and zero dependencies.

---

## Logger Configuration

### Basic Setup

```python
import logging
from datetime import datetime

# Configure the basic logging settings
logging.basicConfig(
    level=logging.INFO,          # Minimum log level to display
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a named logger for this application
logger = logging.getLogger("fastapi_app")
```

**Breaking it down:**
- **`logging.basicConfig()`**: Sets up the root logger with default settings
- **`level=logging.INFO`**: Only show INFO and above (INFO, WARNING, ERROR, CRITICAL)
- **`format`**: Template for how log messages appear
  - `%(asctime)s`: Timestamp
  - `%(name)s`: Logger name ("fastapi_app")
  - `%(levelname)s`: Log level (INFO, ERROR, etc.)
  - `%(message)s`: The actual log message
- **`logger = logging.getLogger("fastapi_app")`**: Creates a named logger instance

### Structured JSON Logging (Production)

For production, use structured JSON logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'item_id'):
            log_data['item_id'] = record.item_id
            
        return json.dumps(log_data)

# Configure logger with JSON formatter
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("fastapi_app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

---

## Log Levels Explained

Python's logging has 5 standard levels (from lowest to highest):

```python
logger.debug("Detailed info for diagnosing problems")     # Level 10
logger.info("Confirmation that things are working")       # Level 20 ✅ We use this
logger.warning("Something unexpected happened")           # Level 30 ✅ We use this
logger.error("A serious problem occurred")                # Level 40 ✅ We use this
logger.critical("A very serious error, app might crash")  # Level 50
```

**Since we set `level=logging.INFO`, we'll see INFO, WARNING, ERROR, and CRITICAL (but not DEBUG).**

### When to Use Each Level

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Detailed diagnostic info (development only) | Variable values, function entry/exit |
| **INFO** | General informational messages | Request received, operation completed |
| **WARNING** | Unexpected but handled situations | Deprecated API usage, slow query |
| **ERROR** | Serious problems requiring attention | Exceptions caught, failed operations |
| **CRITICAL** | Very serious errors, app may crash | Database connection lost |

---

## FastAPI Middleware Implementation

### What is Middleware?

Middleware is code that runs **before and after** each request. It wraps around your endpoint functions like layers of an onion:

```
Request → [CORS Middleware] → [Logging Middleware] → [Your Endpoint] → Response
                                     ▲
                              Logs happen here
```

### Logging Middleware Implementation

```python
import time
from fastapi import Request
from fastapi import FastAPI
import logging

logger = logging.getLogger("fastapi_app")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """This runs for EVERY request"""
    
    # BEFORE: Log the incoming request
    start_time = time.time()
    logger.info(
        "Incoming request",
        extra={
            'method': request.method,
            'path': request.url.path,
            'client_ip': request.client.host if request.client else None,
        }
    )
    
    # DURING: Process the request (calls your endpoint)
    try:
        response = await call_next(request)  # ← Your endpoint runs here
        
        # AFTER: Log the response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration': process_time,
            }
        )
        
        return response
    except Exception as e:
        # ERROR: Log if something goes wrong
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            exc_info=True,  # REQUIRED - includes stack trace
            extra={
                'method': request.method,
                'path': request.url.path,
                'duration': process_time,
                'error': str(e),
            }
        )
        raise
```

**Key Points:**
1. **`@app.middleware("http")`**: Decorator that registers this as HTTP middleware
2. **`async def`**: Asynchronous function (FastAPI is async-first)
3. **`request: Request`**: Contains all info about the incoming request
4. **`call_next`**: Function that calls the next middleware or your endpoint
5. **`time.time()`**: Measures how long the request takes
6. **`exc_info=True`**: Includes full stack trace for errors

---

## Endpoint-Specific Logging

Inside each endpoint function, add specific logging for business events:

```python
from fastapi import APIRouter
import logging

logger = logging.getLogger("fastapi_app")
router = APIRouter()

@router.post("/items", response_model=Item, status_code=201)
async def create_item(item: Item):
    """Create a new item"""
    # Log what data we received (without PII)
    logger.info(
        "Creating new item",
        extra={
            'item_name': item.name,
            'item_price': item.price,
        }
    )
    
    # ... business logic ...
    
    # Log success
    logger.info(
        "Item created successfully",
        extra={
            'item_id': item.id,
            'status': 'created',
        }
    )
    return item
```

**Why both middleware AND endpoint logging?**
- **Middleware**: Logs EVERY request automatically (no manual work)
- **Endpoint logging**: Logs business-specific information (what item was created, etc.)

---

## Request Flow Example

Let's trace what happens when your React app sends: `POST /items`

```python
# 1. Request arrives
# Middleware logs:
{
    "timestamp": "2025-12-01T10:30:45.123Z",
    "level": "INFO",
    "message": "Incoming request",
    "method": "POST",
    "path": "/items",
    "client_ip": "127.0.0.1"
}

# 2. CORS middleware checks origin (passes)

# 3. Your endpoint function runs
# Endpoint logs:
{
    "timestamp": "2025-12-01T10:30:45.125Z",
    "level": "INFO",
    "message": "Creating new item",
    "item_name": "Laptop",
    "item_price": 999.99
}

# ... code creates the item ...

# Endpoint logs:
{
    "timestamp": "2025-12-01T10:30:45.130Z",
    "level": "INFO",
    "message": "Item created successfully",
    "item_id": 1,
    "status": "created"
}

# 4. Response is sent back
# Middleware logs:
{
    "timestamp": "2025-12-01T10:30:45.135Z",
    "level": "INFO",
    "message": "Request completed",
    "method": "POST",
    "path": "/items",
    "status_code": 201,
    "duration": 0.012
}
```

---

## Structured Logging

### Why Structured Logging?

Structured logging uses JSON format instead of plain text:
- ✅ **Searchable**: Easy to query in log aggregation tools
- ✅ **Filterable**: Filter by any field (user_id, status_code, etc.)
- ✅ **Aggregatable**: Create dashboards and alerts
- ✅ **Machine-readable**: Perfect for CloudWatch, Datadog, Kibana

### Implementation

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'message', 'pathname', 
                          'process', 'processName', 'relativeCreated', 'thread', 
                          'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("fastapi_app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Using Structured Logging

```python
logger.info(
    "Item created",
    extra={
        'event_type': 'item_created',
        'item_id': item_id,
        'user_id': user_id,
        'item_name': item.name,
        'price': item.price,
    }
)
```

---

## Exception Logging Patterns

### Basic Exception Logging

```python
try:
    risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        exc_info=True,  # REQUIRED - includes stack trace
        extra={
            'operation': 'create_item',
            'user_id': user_id,
        }
    )
    raise  # Re-raise after logging
```

### Domain Exception Logging

```python
from app.shared.exceptions import NotFoundError

try:
    item = service.get_item(item_id)
except NotFoundError as e:
    logger.warning(
        "Item not found",
        extra={
            'item_id': item_id,
            'user_id': user_id,
            'error_type': 'NotFoundError',
        }
    )
    raise
except Exception as e:
    logger.error(
        "Unexpected error getting item",
        exc_info=True,
        extra={
            'item_id': item_id,
            'user_id': user_id,
        }
    )
    raise
```

### Error Context

Always include context when logging errors:

```python
logger.error(
    "Database operation failed",
    exc_info=True,
    extra={
        'operation': 'create_item',
        'user_id': user_id,
        'item_id': item_id,
        'database': 'postgres',
        'table': 'items',
    }
)
```

---

## Production Configuration

### File Logging with Rotation

For production, log to files with rotation:

```python
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure file logging with rotation
handler = TimedRotatingFileHandler(
    'logs/app.log',
    when='midnight',      # Rotate at midnight
    interval=1,           # Every 1 day
    backupCount=30         # Keep 30 days of logs
)

handler.setFormatter(JSONFormatter())
logger = logging.getLogger("fastapi_app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Cloud Logging Integration

For cloud platforms (AWS, GCP, Azure), logs automatically go to:
- **AWS**: CloudWatch Logs
- **GCP**: Cloud Logging
- **Azure**: Log Analytics

Just use structured JSON logging - the platform will parse it automatically.

---

## Advanced Concepts

### Logger Hierarchy

Python's logging uses a hierarchy based on names:

```
root
 └── fastapi_app (our logger)
      └── fastapi_app.database (if we added this)
      └── fastapi_app.auth (if we added this)
```

Create specialized loggers:

```python
db_logger = logging.getLogger("fastapi_app.database")
auth_logger = logging.getLogger("fastapi_app.auth")
```

### Handlers (Where logs go)

Handlers determine where log output goes:

```python
# Console handler (default)
console_handler = logging.StreamHandler()

# File handler
file_handler = logging.FileHandler('app.log')

# Rotating file handler
from logging.handlers import RotatingFileHandler
rotating_handler = RotatingFileHandler(
    'app.log', 
    maxBytes=10000000,  # 10MB
    backupCount=5
)

# Add multiple handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

---

## Extending the System

### Add Request ID Tracking

```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    logger.info(
        "Incoming request",
        extra={
            'request_id': request_id,
            'method': request.method,
            'path': request.url.path,
        }
    )
    
    response = await call_next(request)
    
    return response

# Use in endpoints
@router.get("/items")
async def get_items(request: Request):
    request_id = request.state.request_id
    logger.info("Fetching items", extra={'request_id': request_id})
```

### Add User Tracking (with authentication)

```python
@router.get("/items")
async def get_items(
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "User fetching items",
        extra={
            'user_id': current_user.id,
            'username': current_user.username,  # Only if not PII
        }
    )
    return items_db
```

### Add Performance Monitoring

```python
import time

@app.middleware("http")
async def monitor_performance(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    if duration > 1.0:  # Threshold: 1 second
        logger.warning(
            "Slow request detected",
            extra={
                'method': request.method,
                'path': request.url.path,
                'duration': duration,
                'threshold': 1.0,
            }
        )
    
    return response
```

---

## Summary

**What we're using:**
- Python's built-in `logging` module (no external dependencies)
- FastAPI's middleware system for automatic request logging
- Manual logging in endpoints for business logic
- Structured JSON logging for production

**How it works:**
1. Request arrives → Middleware logs it
2. Your endpoint runs → Logs specific actions
3. Response sent → Middleware logs completion time
4. Errors → Middleware catches and logs them

**Key patterns:**
- Use middleware for request/response logging
- Use endpoint logging for business events
- Always use `exc_info=True` for exceptions
- Include context in all log messages
- Use structured JSON logging in production

This architecture is **production-ready** and follows Python/FastAPI best practices! 🎉

