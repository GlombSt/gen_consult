# Quick Reference Card

## 🚀 Getting Started

### Local Development
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker
```bash
docker-compose up --build
```

### Access
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 Logging Quick Reference

### What Gets Logged?
✅ HTTP method, path, status code  
✅ Client IP, user agent  
✅ Request/response duration  
✅ Errors with stack traces  
✅ Business logic events  

### PII Protection
| Data Type | Status |
|-----------|--------|
| Email | 📧 Auto-redacted → `[EMAIL_REDACTED]` |
| Phone | 📱 Auto-redacted → `[PHONE_REDACTED]` |
| Password | 🔐 Auto-redacted → `[REDACTED]` |
| Credit Card | 💳 Auto-redacted → `[CC_REDACTED]` |
| User ID | ✅ Safe to log |
| Username | ⚠️ Depends on policy |

### Safe Logging Patterns

```python
# ✅ Good: Use hashed identifiers
email_hash = PIISanitizer.hash_identifier(user.email)
logger.info("User action", extra={'email_hash': email_hash})

# ✅ Good: Log IDs, not PII
logger.info("User updated", extra={'user_id': user.id})

# ❌ Bad: Logging raw PII
logger.info(f"User {user.email} updated")  # Will be sanitized anyway
```

## 🔍 Viewing Logs

### Pretty-Print (Development)
```bash
# Local
uvicorn main:app --reload | jq '.'

# Docker
docker-compose logs -f api | jq '.'
```

### Filter Logs
```bash
# Show only errors
docker-compose logs -f api | jq 'select(.level == "ERROR")'

# Show slow requests (> 0.1s)
docker-compose logs -f api | jq 'select(.duration > 0.1)'

# Show specific fields
docker-compose logs -f api | jq -r '[.timestamp, .method, .path, .status_code] | @tsv'
```

## 🌐 CORS Configuration

### Default Allowed Origins
```
http://localhost:3000    (React/Next.js)
http://localhost:5173    (Vite)
http://localhost:8080    (Vue)
```

### Add More Origins
Edit `main.py`:
```python
origins = [
    "http://localhost:3000",
    "http://localhost:4200",  # Add your port
]
```

## 📊 API Endpoints

### General
- `GET /` - Welcome message
- `GET /health` - Health check

### Items
- `GET /items` - List all items
- `GET /items/{id}` - Get specific item
- `POST /items` - Create item
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item

### Users
- `GET /users` - List users
- `POST /users` - Create user

### Search
- `GET /search?name=laptop&min_price=100` - Search items

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Item
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","price":99.99,"is_available":true}'
```

### Get All Items
```bash
curl http://localhost:8000/items
```

## 🐳 Docker Commands

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down

# Restart
docker-compose restart api

# Rebuild after code changes
docker-compose up --build
```

## ⚙️ Environment Variables

Set in `docker-compose.yml` or `.env`:

```bash
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
ENVIRONMENT=development     # development, production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🔒 Security Best Practices

### DO ✅
- Use the built-in PII sanitizer
- Log user IDs, not emails
- Hash identifiers for correlation
- Set log retention policies
- Review logs before production

### DON'T ❌
- Log passwords or tokens (auto-redacted anyway)
- Log full request bodies with user data
- Log third-party API responses without checking
- Disable PII protection
- Keep logs indefinitely

## 🐛 Troubleshooting

### Port already in use
```bash
uvicorn main:app --reload --port 8001
```

### Module not found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CORS errors from React
1. Check React app's URL is in `origins` list
2. Check browser console for specific error
3. Verify FastAPI is running: `curl http://localhost:8000/health`

### PII showing in logs
1. Check if pattern is in `PIISanitizer` patterns
2. Add custom patterns if needed
3. Report the issue to update defaults

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `LOGGING_ARCHITECTURE.md` | How logging works |
| `CLOUD_NATIVE_LOGGING.md` | Cloud deployment |
| `STRUCTURED_LOGGING_EXAMPLES.md` | Log examples |
| `PII_PRIVACY_GUIDE.md` | PII protection guide |
| `DEBUGGING.md` | Debugging with React |
| `react-example.jsx` | React code examples |

## 🌩️ Cloud Deployment

### AWS ECS/Fargate
- Logs → CloudWatch Logs automatically
- Query with CloudWatch Insights

### Google Cloud Run
- Logs → Cloud Logging automatically
- View in Logs Explorer

### Azure Container Apps
- Logs → Log Analytics automatically
- Query with KQL

### Kubernetes
```bash
kubectl logs -f deployment/fastapi-app
```

## 🎯 CloudWatch Insights Queries

```sql
# Find errors
fields @timestamp, level, message, path
| filter level = "ERROR"
| sort @timestamp desc

# Average response time by endpoint
fields path, duration
| stats avg(duration) as avg_duration by path
| sort avg_duration desc

# Slow requests
fields @timestamp, method, path, duration, status_code
| filter duration > 1.0
| sort duration desc
```

## 🔗 Useful Links

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Docker Docs](https://docs.docker.com/)
- [GDPR Compliance](https://gdpr.eu/)

## 💡 Tips

1. **Development**: Use `jq` to pretty-print JSON logs
2. **Production**: Set `ENVIRONMENT=production` for strict PII protection
3. **Debugging**: Check `/docs` for interactive API testing
4. **Performance**: Monitor `duration` field in logs
5. **Security**: Never commit `.env` files with secrets

---

**Need more details?** Check the full documentation in the other `.md` files!

