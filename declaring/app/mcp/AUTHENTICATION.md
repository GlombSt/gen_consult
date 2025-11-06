# MCP Authentication Guide

## Current Security Status

⚠️ **CRITICAL:** The default MCP implementation has **NO authentication**. This means:

- Anyone with your public URL can access your MCP server
- They can read, create, modify, or delete data
- They can execute any exposed business logic
- **DO NOT use in production without authentication!**

## Authentication Options

This guide covers multiple authentication approaches, from simplest to most secure.

---

## Option 1: Simple API Key (✅ Implemented)

### How It Works

1. Set an API key via environment variable
2. Client sends API key in `Authorization` header
3. Server validates the key before processing requests

### Setup

**1. Generate a strong API key:**

```bash
# Generate a random 32-character key
openssl rand -hex 32
# Output: 8f9a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8
```

**2. Set environment variable:**

```bash
# Development (terminal)
export MCP_API_KEY="your-secret-key-here"

# Or in .env file (declaring/.env)
MCP_API_KEY=your-secret-key-here

# Production (set in your hosting environment)
# Railway, Heroku, etc.
```

**3. Start backend:**

```bash
cd declaring
source venv/bin/activate
uvicorn main:app --reload
```

You'll see in logs:
- "MCP_API_KEY not set - authentication disabled!" (if not set)
- "MCP request authenticated successfully" (if key is valid)

**4. Configure MCP client (Claude Code):**

Update your `~/.config/claude/mcp.json`:

```json
{
  "mcpServers": {
    "gen-consult": {
      "transport": "sse",
      "url": "https://abc123.ngrok.io/mcp/sse",
      "description": "Gen Consult Backend",
      "headers": {
        "Authorization": "Bearer your-secret-key-here"
      }
    }
  }
}
```

**5. Test it:**

```bash
# Without API key (should fail if MCP_API_KEY is set)
curl https://YOUR_TUNNEL_URL/mcp/health

# With API key (should succeed)
curl -H "Authorization: Bearer your-secret-key-here" \
     https://YOUR_TUNNEL_URL/mcp/sse
```

### Pros & Cons

✅ **Pros:**
- Simple to implement
- Easy to configure
- Good for personal/team use
- No external dependencies

❌ **Cons:**
- Single key for all users
- No granular permissions
- Key rotation requires updating all clients
- Not suitable for multi-tenant applications

---

## Option 2: Multiple API Keys (User-Based)

For supporting multiple users/clients with different keys.

### Implementation

**1. Create API keys table in database:**

```python
# app/mcp/db_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.shared.database import Base

class MCPApiKey(Base):
    __tablename__ = "mcp_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # e.g., "Claude Desktop", "Production Server"
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
```

**2. Create authentication function:**

```python
# app/mcp/auth.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database import get_db

async def verify_api_key_db(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> MCPApiKey:
    """Verify API key against database."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")

    # Query database
    result = await db.execute(
        select(MCPApiKey).where(
            MCPApiKey.key == token,
            MCPApiKey.is_active == True
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Update last used timestamp
    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    return api_key
```

**3. Create management endpoints:**

```python
# app/mcp/router.py
@router.post("/admin/keys", tags=["MCP Admin"])
async def create_api_key(
    name: str,
    description: str = None,
    db: AsyncSession = Depends(get_db),
    admin_key: str = Header(None, alias="X-Admin-Key")
):
    """Create a new API key (admin only)."""
    # Verify admin key
    if admin_key != os.getenv("MCP_ADMIN_KEY"):
        raise HTTPException(status_code=403, detail="Admin access required")

    # Generate new key
    import secrets
    new_key = secrets.token_urlsafe(32)

    # Save to database
    api_key = MCPApiKey(key=new_key, name=name, description=description)
    db.add(api_key)
    await db.commit()

    return {"key": new_key, "name": name}

@router.delete("/admin/keys/{key_id}", tags=["MCP Admin"])
async def revoke_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    admin_key: str = Header(None, alias="X-Admin-Key")
):
    """Revoke an API key (admin only)."""
    if admin_key != os.getenv("MCP_ADMIN_KEY"):
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.execute(
        select(MCPApiKey).where(MCPApiKey.id == key_id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="Key not found")

    api_key.is_active = False
    await db.commit()

    return {"message": "Key revoked"}
```

**4. Use in endpoints:**

```python
@router.get("/sse")
async def handle_sse(
    request: Request,
    api_key: MCPApiKey = Depends(verify_api_key_db)  # Use DB verification
):
    logger.info(f"MCP connection from: {api_key.name}")
    # ... rest of implementation
```

### Pros & Cons

✅ **Pros:**
- Multiple users/clients
- Individual key revocation
- Usage tracking per key
- Audit trail

❌ **Cons:**
- Requires database
- More complex to manage
- Still no fine-grained permissions

---

## Option 3: JWT Tokens (OAuth2-Style)

For more sophisticated authentication with expiration and claims.

### Implementation

**1. Install dependencies:**

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

**2. Create JWT utilities:**

```python
# app/mcp/jwt_auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, Header
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_jwt_token(authorization: str = Header(None)):
    """Verify JWT token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
```

**3. Create token endpoint:**

```python
@router.post("/auth/token")
async def login(username: str, password: str):
    """Login and get JWT token."""
    # Verify credentials (implement your own logic)
    if not verify_credentials(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token
    access_token = create_access_token(
        data={"sub": username, "scopes": ["mcp:read", "mcp:write"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

**4. Use in endpoints:**

```python
@router.get("/sse")
async def handle_sse(
    request: Request,
    token_data: dict = Depends(verify_jwt_token)
):
    logger.info(f"MCP connection from: {token_data.get('sub')}")
    # ... rest of implementation
```

### Pros & Cons

✅ **Pros:**
- Token expiration (auto-invalidate)
- Can include user info and permissions
- Industry standard (OAuth2)
- Supports refresh tokens

❌ **Cons:**
- More complex implementation
- Requires token management
- Need login flow

---

## Option 4: IP Whitelist (Simplest for Private Networks)

For restricting access to specific IP addresses.

### Implementation

```python
# app/mcp/auth.py
import os
from fastapi import Request, HTTPException

ALLOWED_IPS = os.getenv("MCP_ALLOWED_IPS", "").split(",")

async def verify_ip_address(request: Request):
    """Verify client IP is in whitelist."""
    if not ALLOWED_IPS or ALLOWED_IPS == [""]:
        # No whitelist configured, allow all
        return True

    client_ip = request.client.host

    if client_ip not in ALLOWED_IPS:
        logger.warning(f"MCP access denied from IP: {client_ip}")
        raise HTTPException(status_code=403, detail="Access denied from your IP")

    return True
```

**Usage:**

```bash
# Set allowed IPs
export MCP_ALLOWED_IPS="192.168.1.100,10.0.0.50,203.0.113.45"
```

```python
@router.get("/sse")
async def handle_sse(
    request: Request,
    ip_verified: bool = Depends(verify_ip_address)
):
    # ... implementation
```

### Pros & Cons

✅ **Pros:**
- Very simple
- No client configuration needed
- Good for internal networks

❌ **Cons:**
- Doesn't work with dynamic IPs
- Bypassed by VPNs
- Not secure for public internet

---

## Recommended Approach

### For Development/Personal Use
✅ **Option 1: Simple API Key** (already implemented)
- Easy to set up
- Good enough for personal projects
- Set `MCP_API_KEY` environment variable

### For Team Use
✅ **Option 2: Multiple API Keys**
- Individual keys per team member
- Can revoke compromised keys
- Track usage per user

### For Production/Multi-Tenant
✅ **Option 3: JWT Tokens**
- Industry standard
- Secure and scalable
- Supports complex permissions

---

## Current Implementation Summary

Your MCP server currently has **Option 1 (Simple API Key)** implemented:

### How to Enable Authentication

**1. Set API key:**
```bash
export MCP_API_KEY="your-secret-key-here"
```

**2. Configure Claude Code:**
```json
{
  "mcpServers": {
    "gen-consult": {
      "transport": "sse",
      "url": "https://abc123.ngrok.io/mcp/sse",
      "headers": {
        "Authorization": "Bearer your-secret-key-here"
      }
    }
  }
}
```

### Behavior

- **If `MCP_API_KEY` is NOT set:** Authentication disabled (development mode)
- **If `MCP_API_KEY` is set:** All requests require valid Bearer token

---

## Testing Authentication

### Test without authentication (should fail):

```bash
curl https://YOUR_TUNNEL_URL/mcp/sse
# Expected: 401 Unauthorized
```

### Test with valid key (should succeed):

```bash
curl -H "Authorization: Bearer your-secret-key-here" \
     https://YOUR_TUNNEL_URL/mcp/sse
```

### Test with invalid key (should fail):

```bash
curl -H "Authorization: Bearer wrong-key" \
     https://YOUR_TUNNEL_URL/mcp/sse
# Expected: 401 Unauthorized
```

---

## Additional Security Recommendations

### 1. Rate Limiting

```python
# Install: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/sse")
@limiter.limit("10/minute")
async def handle_sse(request: Request):
    # ... implementation
```

### 2. HTTPS Only

```python
# app/main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 3. CORS Restrictions

```python
# app/main.py
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

if ENVIRONMENT == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,  # Specific domains only
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization"],
    )
```

### 4. Logging & Monitoring

```python
# Log all authentication attempts
logger.info("MCP auth attempt", extra={
    "ip": request.client.host,
    "user_agent": request.headers.get("user-agent"),
    "success": True/False
})
```

### 5. Secret Rotation

Regularly rotate your API keys/secrets:

```bash
# Generate new key
NEW_KEY=$(openssl rand -hex 32)

# Update environment
export MCP_API_KEY="$NEW_KEY"

# Update all clients
# Restart backend
```

---

## Security Checklist

Before exposing to internet:

- [ ] Set `MCP_API_KEY` environment variable
- [ ] Use HTTPS only (ngrok/cloudflare provide this)
- [ ] Restrict CORS origins in production
- [ ] Add rate limiting
- [ ] Monitor authentication logs
- [ ] Document key rotation process
- [ ] Consider using JWT for complex scenarios
- [ ] Test authentication thoroughly
- [ ] Never commit secrets to git
- [ ] Use different keys for dev/staging/production

---

## Next Steps

1. **Enable authentication now:**
   ```bash
   export MCP_API_KEY="$(openssl rand -hex 32)"
   ```

2. **Test it works**

3. **For production:** Consider implementing Option 2 or 3

4. **Add rate limiting and monitoring**

5. **Document your authentication setup for your team**
