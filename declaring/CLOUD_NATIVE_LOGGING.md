# Cloud-Native Logging Guide

## TL;DR - Is Our Logging Setup Cloud-Ready?

✅ **YES!** The current logging setup is **perfect for Docker and cloud-native environments** because:
- Logs go to **stdout/stderr** (not files) ← This is exactly what containers need
- Works with Docker, Kubernetes, AWS ECS, Google Cloud Run, etc.
- Compatible with log aggregation services (CloudWatch, Stackdriver, Datadog, etc.)

## Why It Works for Containers

### The 12-Factor App Principle

Our logging follows the [12-Factor App](https://12factor.net/logs) methodology:

> **"A twelve-factor app never concerns itself with routing or storage of its output stream. 
> It should not attempt to write to or manage logfiles. Instead, each running process 
> writes its event stream, unbuffered, to stdout."**

**What we're doing:**
```python
logging.basicConfig(...)  # ✅ Defaults to stdout - perfect for containers!
logger.info("...")        # ✅ Goes to stdout
```

**What we're NOT doing:**
```python
# ❌ Not writing to files (good for containers!)
logging.FileHandler('app.log')  # Would be problematic in containers
```

### How Container Logging Works

```
┌─────────────────────────────────────────────────────────────┐
│                      Your FastAPI App                        │
│                                                               │
│  logger.info("Request received")  → stdout                   │
│  logger.error("Error occurred")   → stderr                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Docker Container                        │
│                                                               │
│  Captures stdout/stderr from all processes                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Container Orchestration System                  │
│                                                               │
│  • Docker Desktop: docker logs <container>                   │
│  • Kubernetes: kubectl logs <pod>                            │
│  • AWS ECS: CloudWatch Logs                                  │
│  • Google Cloud Run: Cloud Logging                           │
│  • Azure Container Apps: Log Analytics                       │
└─────────────────────────────────────────────────────────────┘
```

## Docker Example

### 1. Create a Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port
EXPOSE 8000

# Important: Use unbuffered Python output for real-time logs
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key points:**
- `ENV PYTHONUNBUFFERED=1` ensures logs appear immediately (not buffered)
- No log files needed - everything goes to stdout
- Container runtime captures all output automatically

### 2. Build and Run

```bash
# Build the image
docker build -t fastapi-app .

# Run the container
docker run -p 8000:8000 fastapi-app

# View logs in real-time
docker logs -f <container-id>

# You'll see your logs:
# 2025-10-27 14:30:45 - fastapi_app - INFO - 🚀 FastAPI Application Starting...
# 2025-10-27 14:30:50 - fastapi_app - INFO - 📨 Incoming: GET /items
```

### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    # Logs are automatically captured by Docker
```

```bash
# Run with docker-compose
docker-compose up

# View logs
docker-compose logs -f api
```

## Kubernetes Deployment

### 1. Deployment YAML

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        - name: LOG_LEVEL
          value: "INFO"
        # Resource limits (best practice)
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 2. View Logs in Kubernetes

```bash
# Get pods
kubectl get pods

# View logs from a specific pod
kubectl logs fastapi-app-5d7c9f8b4-abc12

# Follow logs in real-time
kubectl logs -f fastapi-app-5d7c9f8b4-abc12

# View logs from all replicas
kubectl logs -l app=fastapi-app --all-containers=true

# View logs from previous crashed container
kubectl logs fastapi-app-5d7c9f8b4-abc12 --previous
```

## Cloud Provider Integration

### AWS (ECS, EKS, Fargate)

Your logs automatically go to **CloudWatch Logs**:

```python
# No code changes needed! Logs automatically captured

# View in AWS Console:
# CloudWatch → Log Groups → /ecs/fastapi-app
# or
# CloudWatch → Log Groups → /aws/eks/fastapi-app
```

**ECS Task Definition:**
```json
{
  "family": "fastapi-app",
  "containerDefinitions": [{
    "name": "fastapi",
    "image": "your-image",
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/fastapi-app",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "environment": [
      {"name": "PYTHONUNBUFFERED", "value": "1"}
    ]
  }]
}
```

### Google Cloud (Cloud Run, GKE)

Logs automatically go to **Cloud Logging** (formerly Stackdriver):

```bash
# Deploy to Cloud Run
gcloud run deploy fastapi-app \
  --image gcr.io/your-project/fastapi-app \
  --platform managed \
  --region us-central1

# View logs
gcloud run logs read fastapi-app

# Or in GCP Console:
# Logging → Logs Explorer → filter by resource type
```

**Important for GCP:** Structured logs work better!

```python
import json
import logging

class GCPFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": record.created,
            "logger": record.name
        }
        return json.dumps(log_obj)

# Use this formatter for GCP
handler = logging.StreamHandler()
handler.setFormatter(GCPFormatter())
logger.addHandler(handler)
```

### Azure (Container Apps, AKS)

Logs go to **Azure Monitor / Log Analytics**:

```bash
# Deploy to Azure Container Apps
az containerapp create \
  --name fastapi-app \
  --resource-group myResourceGroup \
  --image your-registry.azurecr.io/fastapi-app:latest \
  --target-port 8000 \
  --ingress external

# View logs
az containerapp logs show --name fastapi-app --resource-group myResourceGroup --follow
```

## Production Enhancements

### 1. Structured Logging (JSON Format)

For better log parsing and querying in cloud platforms:

```python
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "path": record.pathname,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure JSON logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("fastapi_app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Benefits:**
- Easy to parse and query in log aggregation tools
- Can filter by any field
- Works great with Elasticsearch, CloudWatch Insights, etc.

### 2. Request ID Tracking (Distributed Tracing)

Essential for tracking requests across multiple services:

```python
import uuid
from contextvars import ContextVar

# Store request ID in context (works across async calls)
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # Generate or extract request ID
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    request_id_var.set(request_id)
    
    # Add to all logs
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Include in response headers
    response.headers['X-Request-ID'] = request_id
    
    return response
```

### 3. Environment-Based Configuration

```python
import os
import logging

# Get log level from environment variable
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Use JSON in production, human-readable in development
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development') == 'production'

if IS_PRODUCTION:
    # Structured JSON logging for production
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
else:
    # Human-readable logs for development
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger("fastapi_app")
logger.setLevel(LOG_LEVEL)
```

### 4. Health Checks (Important for Containers!)

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    # Don't log health checks (they happen frequently)
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Or use a separate access log filter
class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return '/health' not in record.getMessage()

logger.addFilter(HealthCheckFilter())
```

## Log Aggregation Services

Your stdout logs work seamlessly with:

### Datadog
```yaml
# docker-compose.yml with Datadog
services:
  api:
    build: .
    labels:
      com.datadoghq.ad.logs: '[{"source": "python", "service": "fastapi-app"}]'
```

### Elasticsearch + Kibana (ELK Stack)
```yaml
# Uses Filebeat or Fluentd to collect container logs
# No code changes needed
```

### Splunk
```yaml
# Splunk Universal Forwarder collects Docker logs
# Works with stdout automatically
```

### New Relic
```python
# Install: pip install newrelic
# newrelic-admin run-program uvicorn main:app
```

## What NOT to Do in Containers

### ❌ Don't Write to Files

```python
# ❌ BAD for containers
logging.FileHandler('/var/log/app.log')
```

**Why not?**
- Container filesystem is ephemeral (data lost when container restarts)
- No easy way to access files across multiple containers
- Requires volume mounts (complexity)
- Doesn't work with cloud log aggregation

### ❌ Don't Rotate Logs Yourself

```python
# ❌ Not needed in containers
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
```

**Why not?**
- Container orchestration handles log retention
- Cloud providers have built-in log rotation
- Adds unnecessary complexity

### ❌ Don't Buffer Logs

```python
# ❌ BAD - logs won't appear immediately
# (default Python behavior)
```

**Always set:**
```dockerfile
ENV PYTHONUNBUFFERED=1
```

Or:
```bash
python -u main.py
```

## Complete Production-Ready Example

```python
# main.py (production-ready)
import os
import json
import logging
import time
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

# --- JSON Formatter for Production ---
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": ENVIRONMENT,
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# --- Setup Logging ---
if IS_PRODUCTION:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(LOG_LEVEL)
else:
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger("fastapi_app")

# --- Create App ---
app = FastAPI(title="FastAPI App")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Logging ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Skip health check logging
    if request.url.path == "/health":
        return await call_next(request)
    
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"Response: {response.status_code} | {duration:.3f}s")
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error: {str(e)} | {duration:.3f}s", exc_info=True)
        raise

# --- Startup ---
@app.on_event("startup")
async def startup():
    logger.info(f"Application starting (environment: {ENVIRONMENT})")

# --- Health Check ---
@app.get("/health")
async def health():
    return {"status": "healthy"}

# --- Your endpoints here ---
```

```dockerfile
# Dockerfile (production-ready)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY main.py .

# Run as non-root user (security best practice)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Summary

### ✅ What Makes Our Logging Cloud-Native Ready

1. **Stdout/stderr output** - Container orchestration systems capture automatically
2. **No file dependencies** - Logs aren't written to disk
3. **Unbuffered** - Logs appear immediately
4. **Structured (optional)** - Easy to parse in log aggregation tools
5. **12-Factor compliant** - Follows cloud-native best practices

### 📋 Checklist for Production

- [ ] Set `PYTHONUNBUFFERED=1` in Dockerfile
- [ ] Use environment variables for configuration
- [ ] Consider JSON logging for production
- [ ] Add request ID tracking for distributed tracing
- [ ] Filter out noisy health check logs
- [ ] Set appropriate log levels (INFO for production, DEBUG for development)
- [ ] Test with `docker logs` before deploying
- [ ] Configure log retention in your cloud provider
- [ ] Set up alerts for ERROR/CRITICAL logs

### Your Current Setup: Perfect Foundation! ✅

Your current logging implementation is **already cloud-ready**. The only thing you might want to add for production is:
1. JSON formatting (for better querying)
2. Request ID tracking (for distributed tracing)
3. Environment-based configuration

But the core architecture is solid and will work perfectly in Docker, Kubernetes, and any cloud platform! 🎉

