# Structured Logging Examples

This document shows examples of the structured (JSON) logs output by your FastAPI application.

## What is Structured Logging?

Structured logging means outputting logs in a **machine-readable format** (JSON) instead of human-readable text. This makes it much easier to:
- **Search and filter** logs in cloud platforms
- **Create alerts** based on specific fields
- **Aggregate and analyze** logs across multiple services
- **Query** logs with tools like CloudWatch Insights, Kibana, Datadog

## Example Log Output

### Application Startup

```json
{
  "timestamp": "2025-10-27T14:30:45.123456Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Application starting",
  "environment": "development",
  "log_level": "INFO",
  "cors_origins_count": 9
}
```

### Incoming HTTP Request

```json
{
  "timestamp": "2025-10-27T14:30:50.789012Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Incoming request",
  "method": "GET",
  "path": "/items",
  "client_ip": "127.0.0.1",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
  "origin": "http://localhost:3000"
}
```

### Fetching Items

```json
{
  "timestamp": "2025-10-27T14:30:50.790123Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Fetching all items",
  "total_items": 5
}
```

### Request Completed Successfully

```json
{
  "timestamp": "2025-10-27T14:30:50.795678Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Request completed",
  "method": "GET",
  "path": "/items",
  "status_code": 200,
  "duration": 0.006
}
```

### Creating a New Item

**Request:**
```json
{
  "timestamp": "2025-10-27T14:31:00.123456Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Incoming request",
  "method": "POST",
  "path": "/items",
  "client_ip": "127.0.0.1",
  "user_agent": "Mozilla/5.0",
  "origin": "http://localhost:3000"
}
```

**Creating item:**
```json
{
  "timestamp": "2025-10-27T14:31:00.125678Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Creating new item",
  "item_name": "Laptop",
  "item_price": 999.99,
  "is_available": true
}
```

**Item created:**
```json
{
  "timestamp": "2025-10-27T14:31:00.127890Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Item created successfully",
  "item_id": 1,
  "item_name": "Laptop"
}
```

**Response:**
```json
{
  "timestamp": "2025-10-27T14:31:00.130456Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Request completed",
  "method": "POST",
  "path": "/items",
  "status_code": 201,
  "duration": 0.007
}
```

### Item Not Found (Warning)

```json
{
  "timestamp": "2025-10-27T14:32:00.123456Z",
  "level": "WARNING",
  "logger": "fastapi_app",
  "message": "Item not found",
  "item_id": 999
}
```

### Error with Exception

```json
{
  "timestamp": "2025-10-27T14:33:00.123456Z",
  "level": "ERROR",
  "logger": "fastapi_app",
  "message": "Request failed",
  "method": "POST",
  "path": "/items",
  "duration": 0.005,
  "error_message": "Validation error",
  "exception": {
    "type": "ValidationError",
    "message": "1 validation error for Item\nprice\n  field required (type=value_error.missing)",
    "traceback": "Traceback (most recent call last):\n  File \"/app/main.py\", line 135, in log_requests\n..."
  }
}
```

## Benefits of Structured Logging

### 1. Easy Filtering

In CloudWatch, Kibana, or any log aggregation tool, you can easily filter:

```
# Find all slow requests (> 1 second)
duration > 1.0

# Find all POST requests
method = "POST"

# Find all errors for a specific endpoint
level = "ERROR" AND path = "/items"

# Find requests from a specific client
client_ip = "192.168.1.100"

# Find all failed item creations
message = "Item created successfully" AND status_code != 201
```

### 2. Create Dashboards

You can create visualizations based on structured fields:
- **Response time histogram** from `duration` field
- **Status code distribution** from `status_code` field
- **Request volume by endpoint** from `path` field
- **Error rate over time** from `level` field

### 3. Set Up Alerts

Alert when certain conditions are met:
- `level = "ERROR"` → Send notification
- `duration > 5.0` → Alert on slow requests
- `status_code >= 500` → Alert on server errors

### 4. Correlation Across Services

With request IDs (can be added), you can trace requests across multiple services:
```json
{
  "request_id": "abc-123-def-456",
  "service": "api",
  "message": "Request completed"
}
```

## CloudWatch Insights Examples

### Query slow requests

```sql
fields @timestamp, method, path, duration, status_code
| filter duration > 1.0
| sort duration desc
| limit 20
```

### Count requests by endpoint

```sql
fields path
| stats count() by path
| sort count desc
```

### Error rate over time

```sql
fields @timestamp, level
| filter level = "ERROR"
| stats count() as error_count by bin(5m)
```

### Average response time by endpoint

```sql
fields path, duration
| stats avg(duration) as avg_duration by path
| sort avg_duration desc
```

## Kibana Examples

### Search for errors from specific IP

```
level:"ERROR" AND client_ip:"192.168.1.100"
```

### Find all item creations

```
message:"Item created successfully"
```

### Requests that took over 1 second

```
duration:>1.0
```

## Datadog Examples

### Create a metric from duration

```
avg:fastapi.request.duration{path:/items}
```

### Alert on error rate

```
sum:fastapi.errors{level:ERROR} > 10
```

## Comparing Human-Readable vs Structured

### Human-Readable (Old Format)
```
2025-10-27 14:30:50 - fastapi_app - INFO - 📨 Incoming: GET /items
2025-10-27 14:30:50 - fastapi_app - INFO -    Client: 127.0.0.1
2025-10-27 14:30:50 - fastapi_app - INFO - 📦 Fetching all items (total: 5)
2025-10-27 14:30:50 - fastapi_app - INFO - ✅ Response: 200 | Time: 0.006s
```

**Challenges:**
- Hard to parse programmatically
- Difficult to extract specific values
- Can't easily query "all requests from IP X"
- Emojis don't work well in some systems

### Structured (New Format)
```json
{"timestamp":"2025-10-27T14:30:50.789012Z","level":"INFO","logger":"fastapi_app","message":"Incoming request","method":"GET","path":"/items","client_ip":"127.0.0.1","user_agent":"Mozilla/5.0","origin":"http://localhost:3000"}
{"timestamp":"2025-10-27T14:30:50.790123Z","level":"INFO","logger":"fastapi_app","message":"Fetching all items","total_items":5}
{"timestamp":"2025-10-27T14:30:50.795678Z","level":"INFO","logger":"fastapi_app","message":"Request completed","method":"GET","path":"/items","status_code":200,"duration":0.006}
```

**Advantages:**
- ✅ Each log is a valid JSON object
- ✅ Easy to parse and query
- ✅ Can filter/search by any field
- ✅ Works perfectly with log aggregation tools
- ✅ Can create metrics and dashboards
- ✅ Standard format across cloud platforms

## Viewing Logs in Docker

### View raw logs
```bash
docker-compose logs -f api
```

Output:
```json
{"timestamp":"2025-10-27T14:30:45.123456Z","level":"INFO","logger":"fastapi_app","message":"Application starting","environment":"development","log_level":"INFO","cors_origins_count":9}
{"timestamp":"2025-10-27T14:30:50.789012Z","level":"INFO","logger":"fastapi_app","message":"Incoming request","method":"GET","path":"/items","client_ip":"172.18.0.1","user_agent":"curl/7.81.0","origin":null}
```

### Pretty-print logs locally

If you want to read logs locally during development, pipe through `jq`:

```bash
docker-compose logs -f api | jq '.'
```

Output:
```json
{
  "timestamp": "2025-10-27T14:30:50.789012Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "Incoming request",
  "method": "GET",
  "path": "/items",
  "client_ip": "172.18.0.1",
  "user_agent": "curl/7.81.0",
  "origin": null
}
```

Or filter specific fields:
```bash
docker-compose logs -f api | jq -r '[.timestamp, .level, .message, .path // "", .status_code // ""] | @tsv'
```

## Adding Custom Fields

You can easily add more fields to any log:

```python
logger.info(
    "User action performed",
    extra={
        'user_id': user.id,
        'action': 'purchase',
        'amount': 99.99,
        'currency': 'USD',
        'payment_method': 'credit_card',
    }
)
```

Output:
```json
{
  "timestamp": "2025-10-27T14:30:50.123456Z",
  "level": "INFO",
  "logger": "fastapi_app",
  "message": "User action performed",
  "user_id": 12345,
  "action": "purchase",
  "amount": 99.99,
  "currency": "USD",
  "payment_method": "credit_card"
}
```

## Best Practices

### ✅ DO

- Use descriptive field names (snake_case)
- Include relevant context in extra fields
- Use appropriate log levels (INFO, WARNING, ERROR)
- Include timing information for performance tracking
- Add correlation IDs for distributed tracing

### ❌ DON'T

- Log sensitive data (passwords, tokens, credit cards)
- Use emojis or special characters in field names
- Create too many unique field names (makes querying hard)
- Log the same information multiple times
- Forget to handle exceptions properly

## Summary

Structured logging transforms your logs from:
- **Human-focused text** → **Machine-readable data**
- **Hard to query** → **Easy to filter and analyze**
- **Local debugging** → **Production observability**

This makes your application production-ready and gives you powerful insights into how it's performing in the cloud! 🎉

