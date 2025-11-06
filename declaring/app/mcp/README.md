# MCP Server Adapter

This module implements a **Model Context Protocol (MCP) server** as a **primary adapter** in the hexagonal architecture. It exposes business logic from the hexagon core through MCP tools that AI assistants can call.

## Architecture

```
┌─────────────────────────────────────────┐
│  MCP Client (Claude Code, Claude.ai)    │
│              (Remote)                    │
└──────────────┬──────────────────────────┘
               │ SSE over HTTPS
               │ (MCP Protocol)
               ▼
┌─────────────────────────────────────────┐
│  Tunnel (ngrok/cloudflare)              │
│  https://abc123.ngrok.io/mcp/sse        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  MCP Router (PRIMARY ADAPTER)           │
│  /mcp/sse - SSE endpoint                │
│  /mcp/messages - Message handling       │
│  /mcp/health - Health check             │
└──────────────┬──────────────────────────┘
               │ Calls ports (service layer)
               ▼
┌─────────────────────────────────────────┐
│  Business Logic (HEXAGON CORE)          │
│  - item_service.list_items()            │
│  - item_service.create_item()           │
│  - user_service.list_users()            │
│  etc.                                   │
└─────────────────────────────────────────┘
```

## Available Tools

The MCP server exposes these tools (which call service layer functions):

### Items Domain
- `list_items` - List all items in inventory
- `get_item` - Get specific item by ID
- `create_item` - Create a new item

### Users Domain
- `list_users` - List all users
- `get_user` - Get specific user by ID
- `create_user` - Create a new user

## Setup & Usage

### 1. Install Dependencies

```bash
cd declaring
pip install mcp sse-starlette
```

### 2. Start the Backend

```bash
# Start FastAPI server
uvicorn main:app --reload

# Server will be available at http://localhost:8000
# MCP endpoint will be at http://localhost:8000/mcp/sse
```

### 3. Expose via Tunnel (for Remote Access)

#### Option A: ngrok (Recommended)

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Authenticate (sign up for free at ngrok.com)
ngrok config add-authtoken YOUR_TOKEN

# Expose your backend
ngrok http 8000

# You'll get a public URL like:
# https://abc123.ngrok.io
```

#### Option B: Cloudflare Tunnel (Free, No Limits)

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Expose your backend
cloudflared tunnel --url http://localhost:8000

# You'll get a URL like:
# https://xyz.trycloudflare.com
```

### 4. Connect from Claude Code

Once you have your public URL, configure Claude Code to use the MCP server:

#### Create MCP Configuration

Edit your Claude Code MCP settings file:

**macOS/Linux:** `~/.config/claude/mcp.json`
**Windows:** `%APPDATA%\claude\mcp.json`

```json
{
  "mcpServers": {
    "gen-consult": {
      "transport": "sse",
      "url": "https://abc123.ngrok.io/mcp/sse",
      "description": "Gen Consult Backend - Items & Users Management"
    }
  }
}
```

Replace `abc123.ngrok.io` with your actual tunnel URL.

#### Restart Claude Code

After updating the configuration, restart Claude Code. The MCP server will now be available and Claude can call your business logic through MCP tools.

### 5. Test the Connection

You can verify the MCP server is working:

```bash
# Check health endpoint
curl https://abc123.ngrok.io/mcp/health

# Expected response:
# {"status":"healthy","server":"gen-consult-backend","transport":"SSE"}
```

## How It Works

### Request Flow

1. **User asks Claude**: "List all items in the inventory"
2. **Claude Code** determines it needs data from your backend
3. **MCP Client** (in Claude) calls the `list_items` tool via SSE
4. **MCP Router** receives the request at `/mcp/sse`
5. **MCP Server** (`server.py`) handles the tool call
6. **Service Layer** (`item_service.list_items()`) executes business logic
7. **Response** flows back through the layers to Claude

### Hexagonal Architecture Alignment

- **MCP Router** (`router.py`) = Primary Adapter (like HTTP router)
- **MCP Server** (`server.py`) = Adapter layer (translates MCP → service calls)
- **Service Layer** (`items.service`, `users.service`) = Ports (hexagon boundary)
- **Business Logic** = Hexagon core

**Key principle:** The MCP server has NO business logic. It only:
- Translates MCP protocol to service calls
- Formats responses back to MCP format
- Handles errors and logging

## Security Considerations

⚠️ **Important for Production:**

1. **Authentication**: Add authentication to MCP endpoints
2. **Rate Limiting**: Prevent abuse of your API
3. **CORS**: Currently allows all origins in development
4. **HTTPS**: Use ngrok/cloudflare HTTPS URLs (not HTTP)
5. **Secrets**: Don't expose sensitive data through MCP tools

### Adding Authentication (Example)

```python
# In router.py
from fastapi import Header, HTTPException

@router.get("/sse")
async def handle_sse(
    request: Request,
    authorization: str = Header(None)
):
    # Validate token
    if not is_valid_token(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ... rest of implementation
```

## Troubleshooting

### Connection Issues

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if MCP endpoint is accessible
curl http://localhost:8000/mcp/health

# Check tunnel status
# For ngrok: http://127.0.0.1:4040 (web UI)
# For cloudflare: Check terminal output
```

### CORS Issues

If Claude Code can't connect, check CORS settings in `main.py`. The MCP endpoint may need additional CORS configuration.

### Tool Execution Errors

Check logs in the backend:
```bash
# Backend logs will show:
# "MCP tool called: list_items"
# Any errors will be logged with full stack traces
```

## Extending the MCP Server

### Adding New Tools

1. **Add tool definition** in `server.py` → `list_tools()`
2. **Add tool handler** in `server.py` → `call_tool()`
3. **Call service layer** (never implement business logic here!)

Example:

```python
# In list_tools()
Tool(
    name="search_items",
    description="Search items by name",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"],
    },
)

# In call_tool()
elif name == "search_items":
    query = arguments.get("query")
    items = await item_service.search_items(query)  # Call service layer!
    return [TextContent(type="text", text=format_items(items))]
```

### Adding New Domains

When you add a new domain (e.g., `orders`):

1. Implement the domain following hexagonal architecture
2. Export service functions in `app/orders/__init__.py`
3. Import service in `mcp/server.py`
4. Add tools for the new domain

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/python-mcp)
- [ngrok Documentation](https://ngrok.com/docs)
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
