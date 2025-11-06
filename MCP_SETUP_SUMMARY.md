# MCP Remote Server Setup - Summary

Your backend can now be exposed as an **MCP (Model Context Protocol) remote server**, allowing Claude Code and other MCP clients to connect to it over the internet!

## What Was Implemented

### 1. MCP Server Adapter (Hexagonal Architecture)

Created a new **primary adapter** at `declaring/app/mcp/`:

```
app/mcp/
├── __init__.py       # Exports MCP router
├── router.py         # SSE endpoints for MCP protocol
├── server.py         # MCP server with tool implementations
└── README.md         # Comprehensive documentation
```

**Architecture alignment:**
- MCP adapter = Primary adapter (like HTTP router)
- Calls service layer functions (ports)
- NO business logic in adapter
- Follows hexagonal architecture principles

### 2. Available MCP Tools

Six tools that expose your business logic:

**Items Domain:**
- `list_items` - List all items
- `get_item` - Get item by ID
- `create_item` - Create new item

**Users Domain:**
- `list_users` - List all users
- `get_user` - Get user by ID
- `create_user` - Create new user

### 3. Configuration Updates

**Dependencies:** Added to `requirements.txt`
```
mcp>=1.0.0
sse-starlette>=2.0.0
```

**Main App:** Updated `app/main.py`
- Registered MCP router at `/mcp/*` endpoints
- Updated CORS to allow all origins in development (for MCP clients)
- Added logging for MCP connections

**Endpoints:**
- `/mcp/sse` - Main SSE endpoint for MCP protocol
- `/mcp/messages` - Message handling endpoint
- `/mcp/health` - Health check endpoint

### 4. Documentation

**Comprehensive guides:**
- `declaring/app/mcp/README.md` - Full MCP implementation docs
- `declaring/EXPOSE_VIA_TUNNEL.md` - Quick-start tunneling guide
- `MCP_SETUP_SUMMARY.md` - This summary

## Quick Start

### Step 1: Install Dependencies

```bash
cd declaring
source venv/bin/activate  # If using venv
pip install -r requirements.txt
```

### Step 2: Start Backend

```bash
uvicorn main:app --reload
```

Your backend runs at `http://localhost:8000`

### Step 3: Expose via Tunnel

**Option A: ngrok (Recommended)**
```bash
# Install: brew install ngrok  (or see EXPOSE_VIA_TUNNEL.md)
ngrok config add-authtoken YOUR_TOKEN  # Sign up at ngrok.com
ngrok http 8000
```

**Option B: Cloudflare Tunnel (Free)**
```bash
# Install cloudflared (see EXPOSE_VIA_TUNNEL.md)
cloudflared tunnel --url http://localhost:8000
```

You'll get a public URL like: `https://abc123.ngrok.io`

### Step 4: Connect Claude Code

Edit your MCP config file:
- **macOS/Linux:** `~/.config/claude/mcp.json`
- **Windows:** `%APPDATA%\claude\mcp.json`

```json
{
  "mcpServers": {
    "gen-consult": {
      "transport": "sse",
      "url": "https://abc123.ngrok.io/mcp/sse",
      "description": "Gen Consult Backend"
    }
  }
}
```

Replace `abc123.ngrok.io` with your actual tunnel URL.

### Step 5: Test It

Restart Claude Code, then ask:
- "List all items in the inventory"
- "Create a new user named John with email john@example.com"
- "Get item with ID 1"

Claude will call your backend via MCP! 🎉

## Architecture Flow

```
┌─────────────────────────────────────┐
│  User asks Claude                    │
│  "List all items"                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Claude Code (MCP Client)           │
│  Calls list_items tool              │
└──────────────┬──────────────────────┘
               │ HTTPS (SSE)
               │ MCP Protocol
               ▼
┌─────────────────────────────────────┐
│  ngrok/cloudflare                   │
│  https://abc123.ngrok.io/mcp/sse    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  MCP Router (PRIMARY ADAPTER)       │
│  /mcp/sse endpoint                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  MCP Server                         │
│  Tool handler: list_items           │
└──────────────┬──────────────────────┘
               │ Calls port
               ▼
┌─────────────────────────────────────┐
│  Service Layer (PORT)               │
│  get_all_items()                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Business Logic (HEXAGON CORE)      │
│  Domain models, validation, events  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Repository (SECONDARY ADAPTER)     │
│  Database queries                   │
└─────────────────────────────────────┘
```

## Verification

Test your setup:

```bash
# 1. Check backend is running
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# 2. Check MCP endpoint (local)
curl http://localhost:8000/mcp/health
# Expected: {"status":"healthy","server":"gen-consult-backend","transport":"SSE"}

# 3. Check tunnel URL
curl https://YOUR_TUNNEL_URL/mcp/health
# Expected: Same as above

# 4. View API docs
# Open: http://localhost:8000/docs
# Or: https://YOUR_TUNNEL_URL/docs
```

## Security Notes

⚠️ **Current setup is for development only!**

- CORS allows all origins (`*`)
- No authentication on MCP endpoints
- Suitable for testing and learning

For production:
1. Add authentication to `/mcp/*` endpoints
2. Restrict CORS origins
3. Add rate limiting
4. Use environment variables for sensitive config
5. Monitor access logs

See `declaring/app/mcp/README.md` for authentication examples.

## Extending the MCP Server

### Add More Tools

Edit `declaring/app/mcp/server.py`:

1. **Add tool definition** in `list_tools()`
2. **Add tool handler** in `call_tool()`
3. **Call service layer** (never add business logic!)

Example:
```python
# In list_tools()
Tool(
    name="delete_item",
    description="Delete an item by ID",
    inputSchema={
        "type": "object",
        "properties": {
            "item_id": {"type": "integer"}
        },
        "required": ["item_id"],
    },
)

# In call_tool()
elif name == "delete_item":
    item_id = arguments.get("item_id")
    await delete_item(item_id)  # Call service!
    return [TextContent(type="text", text=f"Deleted item {item_id}")]
```

### Add New Domains

When you create a new domain (e.g., `orders`):

1. Implement domain following hexagonal architecture
2. Export service functions in `app/orders/__init__.py`
3. Import functions in `app/mcp/server.py`
4. Add tools for the new domain

## Troubleshooting

### Can't Install Dependencies

```bash
# Update pip first
pip install --upgrade pip

# Try installing one by one
pip install mcp
pip install sse-starlette
```

### Backend Won't Start

```bash
# Check Python version (need 3.10+)
python3 --version

# Check port 8000 is free
lsof -i :8000

# Use different port if needed
uvicorn main:app --reload --port 8001
# Then: ngrok http 8001
```

### Tunnel Connection Issues

```bash
# Test local first
curl http://localhost:8000/health

# Check ngrok web UI
# Open: http://127.0.0.1:4040

# Try different tunnel service
# If ngrok fails, try cloudflare
```

### MCP Not Connecting from Claude

1. Verify mcp.json syntax (valid JSON)
2. Check URL has `/mcp/sse` at end
3. Restart Claude Code completely
4. Check backend logs for connection attempts
5. Test with curl first

## Next Steps

✅ **Setup Complete!** You can now:

1. Test the MCP tools from Claude Code
2. Add more tools to expose additional functionality
3. Create new domains and expose them via MCP
4. Learn about MCP protocol: https://modelcontextprotocol.io/
5. Add authentication before production use

## Resources

- **Full MCP Docs:** `declaring/app/mcp/README.md`
- **Tunnel Guide:** `declaring/EXPOSE_VIA_TUNNEL.md`
- **Architecture Docs:** `declaring/ARCHITECTURE_STANDARDS.md`
- **MCP Protocol:** https://modelcontextprotocol.io/
- **ngrok:** https://ngrok.com/docs
- **Cloudflare Tunnel:** https://developers.cloudflare.com/cloudflare-one/

## Files Changed

```
declaring/
├── app/
│   ├── main.py                     # Added MCP router
│   └── mcp/                        # NEW: MCP adapter
│       ├── __init__.py
│       ├── router.py
│       ├── server.py
│       └── README.md
├── requirements.txt                # Added mcp, sse-starlette
├── EXPOSE_VIA_TUNNEL.md           # NEW: Tunnel guide
└── (ready to commit)

repo_root/
└── MCP_SETUP_SUMMARY.md           # NEW: This file
```

---

**Happy MCP-ing! 🚀**

Your backend is now an MCP remote server that AI assistants can connect to from anywhere on the internet!
