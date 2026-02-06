# Quick Reference Card

> **New to this project?** Start with [README.md](./README.md) for setup and overview.

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
uvicorn main:app --reload | jq '.'
```

### Filter Logs
```bash
# Show only errors
uvicorn main:app --reload 2>&1 | jq 'select(.level == "ERROR")'

# Show slow requests (> 0.1s)
uvicorn main:app --reload 2>&1 | jq 'select(.duration > 0.1)'

# Show specific fields
uvicorn main:app --reload 2>&1 | jq -r '[.timestamp, .method, .path, .status_code] | @tsv'
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

### Intents
- `GET /intents` - List all intents
- `GET /intents/{id}` - Get specific intent
- `POST /intents` - Create intent
- `PUT /intents/{id}` - Update intent
- `DELETE /intents/{id}` - Delete intent

### Users
- `GET /users` - List users
- `POST /users` - Create user

### Search
- `GET /search?name=summary&output_format=json` - Search intents

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Intent
```bash
curl -X POST http://localhost:8000/intents \
  -H "Content-Type: application/json" \
  -d '{"name":"Summarize Document","description":"Create a summary","output_format":"markdown"}'
```

### Get All Intents
```bash
curl http://localhost:8000/intents
```

## ⚙️ Environment Variables

Set in `.env`:

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
source .venv/bin/activate
pip install -e ".[dev]"
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
| `README.md` | Getting started, project overview, documentation guide |
| `ARCHITECTURE_STANDARDS.md` | Mandatory architecture rules |
| `ARCHITECTURE_GUIDE.md` | Detailed examples and patterns |
| `DEVELOPMENT_STANDARDS.md` | TDD workflow and checklist |
| `TESTING_STANDARDS.md` | Coverage requirements and test patterns |
| `LOGGING_STANDARDS.md` | Logging rules and requirements |
| `LOGGING_GUIDE.md` | Logging implementation guide |
| `PII_PRIVACY_GUIDE.md` | PII protection guide |
| `DEBUGGING.md` | Debugging with React |

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
- [GDPR Compliance](https://gdpr.eu/)

## 💡 Tips

1. **Development**: Use `jq` to pretty-print JSON logs
2. **Production**: Set `ENVIRONMENT=production` for strict PII protection
3. **Debugging**: Check `/docs` for interactive API testing
4. **Performance**: Monitor `duration` field in logs
5. **Security**: Never commit `.env` files with secrets

---

**Need more details?** Check the full documentation in the other `.md` files!

