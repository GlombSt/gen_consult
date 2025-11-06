# MCP Authentication - Implementation Summary

## Answer: How Does It Authenticate?

### Current Status

**Before:** ❌ **NO AUTHENTICATION** - Anyone with your URL could access everything
**Now:** ✅ **API Key Authentication** - Optional but ready to enable

## Quick Answer

Your MCP server now supports **Bearer token authentication** via API keys:

### To Enable (Recommended Before Internet Exposure):

```bash
# 1. Generate a strong API key
export MCP_API_KEY="$(openssl rand -hex 32)"

# 2. Start backend
cd declaring
uvicorn main:app --reload

# 3. Configure Claude Code (~/.config/claude/mcp.json)
{
  "mcpServers": {
    "gen-consult": {
      "transport": "sse",
      "url": "https://your-tunnel-url.ngrok.io/mcp/sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY_HERE"
      }
    }
  }
}
```

### Behavior

- **No `MCP_API_KEY` set** → Authentication disabled (development mode)
- **`MCP_API_KEY` set** → All requests require valid Bearer token
- **Invalid/missing token** → Returns 401 Unauthorized

## Implementation Details

### What Was Added

**1. Authentication Module** (`declaring/app/mcp/auth.py`)
- `verify_api_key()` - Validates Bearer tokens from Authorization header
- `verify_api_key_query()` - Alternative query parameter validation
- Environment-based configuration
- Development-friendly (gracefully disabled if no key set)

**2. Protected Endpoints** (`declaring/app/mcp/router.py`)
- `/mcp/sse` - Now requires authentication
- `/mcp/messages` - Now requires authentication
- `/mcp/health` - Public (no auth needed)

**3. Comprehensive Documentation** (`declaring/app/mcp/AUTHENTICATION.md`)
- 4 authentication options explained
- Implementation guides
- Security best practices
- Testing instructions

### How It Works

```
┌─────────────────────────────────────┐
│  Claude Code sends request          │
│  Authorization: Bearer abc123...    │
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│  FastAPI receives request           │
│  Extracts Authorization header      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  verify_api_key() called            │
│  (via Depends in router)            │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌──────────┐
│ Valid?  │         │ Invalid? │
│ ✅ 200  │         │ ❌ 401   │
└────┬────┘         └──────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Process MCP request                │
│  Execute tool, return result        │
└─────────────────────────────────────┘
```

### Code Example

**Router with authentication:**
```python
from fastapi import Depends
from app.mcp.auth import verify_api_key

@router.get("/sse")
async def handle_sse(
    request: Request,
    authenticated: bool = Depends(verify_api_key)  # ← This checks auth!
):
    # Only executes if authentication succeeds
    logger.info("MCP SSE connection initiated (authenticated)")
    # ... handle MCP connection
```

**Authentication function:**
```python
async def verify_api_key(authorization: Optional[str] = Header(None)) -> bool:
    # If no API key configured, skip auth (development mode)
    if not MCP_API_KEY:
        logger.warning("MCP_API_KEY not set - authentication disabled!")
        return True

    # Require Authorization header
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")

    # Parse Bearer token
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(401, "Invalid authentication scheme")

    # Verify token matches configured key
    if token != MCP_API_KEY:
        raise HTTPException(401, "Invalid API key")

    return True
```

## Authentication Options Overview

### Option 1: Simple API Key (✅ Implemented)

**What you have now:**
- Single API key via environment variable
- Bearer token authentication
- Perfect for personal/development use

**Setup:**
```bash
export MCP_API_KEY="your-secret-key"
```

**Pros:** Simple, works immediately
**Cons:** Single key for everyone

---

### Option 2: Multiple API Keys (Documented)

**For teams:**
- Database-backed key management
- Individual keys per user/client
- Key revocation support
- Usage tracking

**Implementation:** See `declaring/app/mcp/AUTHENTICATION.md` → Option 2

---

### Option 3: JWT Tokens (Documented)

**For production apps:**
- OAuth2-style authentication
- Token expiration
- Refresh tokens
- User claims and permissions

**Implementation:** See `declaring/app/mcp/AUTHENTICATION.md` → Option 3

---

### Option 4: IP Whitelist (Documented)

**For private networks:**
- Restrict by IP address
- No client configuration needed
- Good for VPNs/internal networks

**Implementation:** See `declaring/app/mcp/AUTHENTICATION.md` → Option 4

---

## Testing Authentication

### Test 1: No Authentication (Development Mode)

```bash
# Don't set MCP_API_KEY
unset MCP_API_KEY

# Start backend
uvicorn main:app --reload

# Test endpoint (should work without auth)
curl https://YOUR_TUNNEL_URL/mcp/health
# ✅ {"status":"healthy",...}
```

**Expected log:**
```
WARNING - MCP_API_KEY not set - authentication disabled!
```

### Test 2: With Authentication Enabled

```bash
# Set API key
export MCP_API_KEY="my-secret-key-123"

# Restart backend
uvicorn main:app --reload

# Test without auth (should fail)
curl https://YOUR_TUNNEL_URL/mcp/sse
# ❌ 401 {"detail":"Missing Authorization header"}

# Test with wrong key (should fail)
curl -H "Authorization: Bearer wrong-key" \
     https://YOUR_TUNNEL_URL/mcp/sse
# ❌ 401 {"detail":"Invalid API key"}

# Test with correct key (should succeed)
curl -H "Authorization: Bearer my-secret-key-123" \
     https://YOUR_TUNNEL_URL/mcp/sse
# ✅ (SSE stream opens)
```

**Expected logs:**
```
INFO - MCP request authenticated successfully
INFO - MCP SSE connection initiated (authenticated)
```

## Security Best Practices

### 1. Generate Strong Keys

```bash
# Use cryptographically secure random generation
openssl rand -hex 32
# Output: 64 character hex string (32 bytes)
```

### 2. Never Commit Secrets

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore

# Store in environment, not code
export MCP_API_KEY="your-key"
```

### 3. Use Different Keys Per Environment

```bash
# Development
export MCP_API_KEY="dev-key-12345"

# Staging
export MCP_API_KEY="staging-key-67890"

# Production
export MCP_API_KEY="prod-key-$(openssl rand -hex 32)"
```

### 4. Rotate Keys Regularly

```bash
# Generate new key
NEW_KEY=$(openssl rand -hex 32)

# Update backend
export MCP_API_KEY="$NEW_KEY"

# Update all MCP clients
# Restart backend
```

### 5. Monitor Authentication Logs

All authentication attempts are logged:
```
INFO - MCP request authenticated successfully
WARNING - MCP request with invalid API key
WARNING - MCP request without Authorization header
```

Check logs regularly for suspicious activity.

## Integration with Claude Code

### Configuration File

**Location:**
- macOS/Linux: `~/.config/claude/mcp.json`
- Windows: `%APPDATA%\claude\mcp.json`

**With authentication:**
```json
{
  "mcpServers": {
    "gen-consult": {
      "transport": "sse",
      "url": "https://abc123.ngrok.io/mcp/sse",
      "description": "Gen Consult Backend (Authenticated)",
      "headers": {
        "Authorization": "Bearer your-secret-key-here"
      }
    }
  }
}
```

**Without authentication (development):**
```json
{
  "mcpServers": {
    "gen-consult": {
      "transport": "sse",
      "url": "http://localhost:8000/mcp/sse",
      "description": "Gen Consult Backend (Local Dev)"
    }
  }
}
```

## Troubleshooting

### Issue: Authentication not working

**Check 1: Is MCP_API_KEY set?**
```bash
echo $MCP_API_KEY
# Should output your key
```

**Check 2: Backend logs**
```bash
# Look for:
# "MCP_API_KEY not set - authentication disabled!" (if key missing)
# "MCP request authenticated successfully" (if working)
# "MCP request with invalid API key" (if wrong key)
```

**Check 3: Claude Code configuration**
```bash
cat ~/.config/claude/mcp.json
# Verify "Authorization" header is present
# Verify key matches MCP_API_KEY
```

### Issue: 401 Unauthorized

**Cause 1: Missing Authorization header**
```json
// Add to mcp.json:
"headers": {
  "Authorization": "Bearer your-key-here"
}
```

**Cause 2: Wrong key format**
```
✅ Correct: "Bearer my-secret-key"
❌ Wrong: "my-secret-key"
❌ Wrong: "Token my-secret-key"
```

**Cause 3: Key mismatch**
```bash
# Backend key
echo $MCP_API_KEY

# Must exactly match key in mcp.json
```

### Issue: Still allows access without auth

**Cause: MCP_API_KEY not set**
```bash
# Set it:
export MCP_API_KEY="your-key"

# Restart backend:
uvicorn main:app --reload

# Verify in logs:
# Should NOT see: "authentication disabled!"
```

## Production Deployment Checklist

Before exposing to internet:

- [ ] Generate strong API key: `openssl rand -hex 32`
- [ ] Set `MCP_API_KEY` environment variable
- [ ] Test authentication works (401 without key)
- [ ] Configure all MCP clients with key
- [ ] Verify logs show successful auth
- [ ] Use HTTPS only (ngrok/cloudflare provide this)
- [ ] Consider implementing rate limiting
- [ ] Monitor authentication logs
- [ ] Document key rotation procedure
- [ ] Set up different keys for dev/staging/prod

## Files Changed

```
declaring/app/mcp/
├── auth.py                   # NEW: Authentication functions
├── AUTHENTICATION.md         # NEW: Complete auth guide (591 lines)
├── router.py                 # MODIFIED: Added auth to endpoints
├── server.py                 # (unchanged)
├── __init__.py              # (unchanged)
└── README.md                # (unchanged)
```

## Next Steps

### For Development (Right Now)

```bash
# Option 1: No auth (testing only)
unset MCP_API_KEY
uvicorn main:app --reload

# Option 2: With auth (recommended)
export MCP_API_KEY="$(openssl rand -hex 32)"
echo "Your API key: $MCP_API_KEY"
uvicorn main:app --reload
```

### For Production (Later)

1. Read `declaring/app/mcp/AUTHENTICATION.md`
2. Choose authentication approach (Option 1-4)
3. Implement rate limiting
4. Set up monitoring
5. Document for your team

## Summary

### Question: How does it authenticate?

**Answer:**

1. **By default:** It doesn't (development mode)
2. **When enabled:** Bearer token API key
3. **Configuration:** `MCP_API_KEY` environment variable
4. **Client:** Sends `Authorization: Bearer <key>` header
5. **Security:** Production-ready with proper key management

### Current Implementation

✅ **Simple API Key Authentication (Option 1)**
- Environment variable based
- Bearer token standard
- Development-friendly (gracefully disabled)
- Production-ready when enabled
- Comprehensive logging
- 4 alternative options documented

### How to Enable Now

```bash
export MCP_API_KEY="$(openssl rand -hex 32)"
# Update Claude Code mcp.json with the key
# Restart backend
# Test with curl
```

---

**Bottom line:** Your MCP server is now **authentication-ready**. It's disabled by default for easy development, but can be enabled instantly by setting one environment variable. Perfect for learning now, secure for production later! 🔐
