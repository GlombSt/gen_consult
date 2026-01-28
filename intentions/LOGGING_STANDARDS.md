# Logging Standards

**Version:** 1.0
**Last Updated:** December 2025
**Status:** MANDATORY - All code changes must follow these standards
**Audience:** Experts familiar with Python logging and FastAPI middleware

For detailed examples and explanations, see [LOGGING_GUIDE.md](./LOGGING_GUIDE.md)

**Related Documentation:**
- [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) - Hexagonal architecture rules
- [PII_PRIVACY_GUIDE.md](./PII_PRIVACY_GUIDE.md) - PII protection requirements

---

## Architecture Overview

The logging system uses **Python's built-in `logging` module** with **FastAPI middleware** for automatic request/response logging.

**Logging flow:**
```
Request → [CORS Middleware] → [Logging Middleware] → [Endpoint] → Response
                                      │
                              Logs request/response
```

---

## Required Components

### 1. Logger Configuration

**MUST** configure logging using Python's standard `logging` module:

- ✅ Use `logging.getLogger("fastapi_app")` for application logger
- ✅ Set minimum log level to `logging.INFO` in production
- ✅ Use structured JSON logging for production environments
- ✅ Configure PII sanitization (see [PII_PRIVACY_GUIDE.md](./PII_PRIVACY_GUIDE.md))

### 2. Logging Middleware

**MUST** implement HTTP middleware for automatic request/response logging:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log incoming request details
    # Measure processing time
    # Log response status
    # Log errors with exc_info=True
```

**Required logging:**
- ✅ HTTP method and path
- ✅ Client IP address
- ✅ Response status code
- ✅ Request processing duration
- ✅ Errors with full stack traces (`exc_info=True`)

### 3. Log Levels

**MUST** use appropriate log levels:

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Detailed diagnostic info (development only) | Variable values, function entry/exit |
| `INFO` | General informational messages | Request received, operation completed |
| `WARNING` | Unexpected but handled situations | Deprecated API usage, slow query |
| `ERROR` | Serious problems requiring attention | Exceptions caught, failed operations |
| `CRITICAL` | Very serious errors, app may crash | Database connection lost |

**Rules:**
- ✅ Use `INFO` for normal operations
- ✅ Use `ERROR` for exceptions (with `exc_info=True`)
- ✅ Use `WARNING` for non-fatal issues
- ✅ Never use `DEBUG` in production code

---

## Logging Requirements by Layer

### Service Layer (PORTS)

**MUST:**
- ✅ Log business actions with context (user_id, item_id, etc.)
- ✅ Log before significant operations
- ✅ Log after successful operations
- ✅ Never log sensitive data (see PII guide)

```python
logger.info("User action", extra={
    'user_id': user_id,
    'item_id': item_id,
    'action': 'created'
})
```

### Router Layer (PRIMARY ADAPTER)

**MUST:**
- ✅ Rely on middleware for request/response logging
- ✅ Log endpoint-specific business events
- ✅ Never log full request bodies with PII

### Repository Layer (SECONDARY ADAPTER)

**MUST:**
- ✅ Log database operations at `DEBUG` level (development only)
- ✅ Log errors with `exc_info=True`
- ✅ Never log SQL queries with parameters in production

---

## PII Protection Rules

**MANDATORY** - All logging must comply with PII protection:

- ❌ **NEVER** log passwords, tokens, API keys, or secrets
- ❌ **NEVER** log full request bodies containing user data
- ✅ **ALWAYS** use PII sanitization middleware
- ✅ **ALWAYS** hash identifiers for user correlation
- ✅ **ALWAYS** redact emails, phone numbers, credit cards, SSNs

See [PII_PRIVACY_GUIDE.md](./PII_PRIVACY_GUIDE.md) for complete requirements.

---

## Structured Logging Format

**MUST** use structured JSON logging in production:

```python
logger.info("Event", extra={
    'timestamp': datetime.utcnow().isoformat(),
    'event_type': 'item_created',
    'item_id': item_id,
    'user_id': user_id
})
```

**Required fields:**
- ✅ Timestamp (ISO 8601 format)
- ✅ Log level
- ✅ Logger name
- ✅ Message
- ✅ Context fields (event_type, user_id, etc.)

---

## Exception Logging

**MUST** log exceptions with full context:

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
            'item_id': item_id
        }
    )
    raise  # Re-raise after logging
```

**Rules:**
- ✅ Always use `exc_info=True` for exception logging
- ✅ Include context (user_id, request_id, etc.)
- ✅ Log before re-raising
- ✅ Never log and swallow exceptions silently

---

## Production Configuration

**MUST** configure for production:

- ✅ Use structured JSON logging
- ✅ Set log level to `INFO` (not `DEBUG`)
- ✅ Configure log rotation (file size or time-based)
- ✅ Set retention policy (e.g., 30 days)
- ✅ Send logs to aggregation service (CloudWatch, Datadog, etc.)
- ✅ Enable PII sanitization

---

## Best Practices

**MUST follow:**

1. **✅ Include context in log messages**
   - Include relevant IDs (user_id, item_id, request_id)
   - Use structured extra fields, not string interpolation

2. **✅ Use appropriate log levels**
   - `INFO` for normal operations
   - `WARNING` for unexpected but handled situations
   - `ERROR` for exceptions and failures

3. **✅ Measure and log performance**
   - Log request duration in middleware
   - Log slow operations (> 1 second) at WARNING level

4. **✅ Never log sensitive data**
   - Never log passwords, tokens, or secrets
   - Never log full request/response bodies
   - Always use PII sanitization

5. **✅ Use named loggers**
   - Use `logging.getLogger("fastapi_app")` for app logger
   - Use `logging.getLogger("fastapi_app.database")` for domain-specific loggers

---

## Summary

**Required:**
- Python's built-in `logging` module
- HTTP middleware for request/response logging
- Structured JSON logging in production
- PII sanitization (mandatory)
- Appropriate log levels (INFO, WARNING, ERROR)
- Exception logging with `exc_info=True`

**Forbidden:**
- Logging passwords, tokens, or secrets
- Logging full request bodies with PII
- Using DEBUG level in production
- Silent exception handling without logging

