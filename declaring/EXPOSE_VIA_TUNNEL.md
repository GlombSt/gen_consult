# Exposing the Backend via Internet Tunnel

Quick guide to expose your local FastAPI backend to the internet using tunneling services, with support for MCP (Model Context Protocol) remote server connections.

## Quick Start

### 1. Start Your Backend

```bash
cd declaring
source venv/bin/activate  # If using virtual environment
uvicorn main:app --reload
```

Your backend is now running at `http://localhost:8000`

### 2. Choose a Tunneling Service

#### Option A: ngrok (Recommended)

**Install:**
```bash
# macOS
brew install ngrok

# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok

# Or download directly
# wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
# tar xvzf ngrok-v3-stable-linux-amd64.tgz
```

**Setup:**
```bash
# Sign up at https://ngrok.com and get your auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

**Expose Backend:**
```bash
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Account                       you@example.com
Version                       3.x.x
Region                        United States (us)
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

**Your public URL:** `https://abc123.ngrok.io`

#### Option B: Cloudflare Tunnel (Free, No Limits)

**Install:**
```bash
# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# macOS
brew install cloudflare/cloudflare/cloudflared
```

**Expose Backend:**
```bash
cloudflared tunnel --url http://localhost:8000
```

You'll see output with your public URL:
```
Your public URL: https://xyz-abc-123.trycloudflare.com
```

#### Option C: localtunnel (Simple, Open Source)

**Install:**
```bash
npm install -g localtunnel
```

**Expose Backend:**
```bash
lt --port 8000
```

You'll get: `your url is: https://random-name.loca.lt`

#### Option D: serveo (No Install Required)

**Expose Backend:**
```bash
ssh -R 80:localhost:8000 serveo.net
```

## Verify Exposure

Once you have your public URL, test it:

```bash
# Replace YOUR_PUBLIC_URL with your actual URL
curl https://YOUR_PUBLIC_URL/health

# Expected response:
# {"status":"healthy"}

# Test MCP endpoint
curl https://YOUR_PUBLIC_URL/mcp/health

# Expected response:
# {"status":"healthy","server":"gen-consult-backend","transport":"SSE"}
```

## Using as MCP Remote Server

### What is MCP?

MCP (Model Context Protocol) allows AI assistants like Claude to connect to your backend and call functions/tools. With a public URL, Claude Code can access your local backend from anywhere.

### Available Endpoints

- **Main API:** `https://YOUR_PUBLIC_URL/docs` (Swagger UI)
- **MCP Server:** `https://YOUR_PUBLIC_URL/mcp/sse` (SSE endpoint)
- **Health Check:** `https://YOUR_PUBLIC_URL/health`
- **MCP Health:** `https://YOUR_PUBLIC_URL/mcp/health`

### Connect Claude Code to Your Backend

1. **Get your public URL** from ngrok/cloudflare (e.g., `https://abc123.ngrok.io`)

2. **Create MCP configuration file:**

   **macOS/Linux:** `~/.config/claude/mcp.json`
   **Windows:** `%APPDATA%\claude\mcp.json`

3. **Add your server:**

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

   Replace `abc123.ngrok.io` with your actual URL.

4. **Restart Claude Code**

5. **Test it:** Ask Claude to "list all items" or "create a new user"

### Available MCP Tools

Claude can now call these tools from your backend:

- `list_items` - List all items in inventory
- `get_item` - Get specific item by ID
- `create_item` - Create a new item
- `list_users` - List all users
- `get_user` - Get specific user by ID
- `create_user` - Create a new user

## Architecture

```
┌──────────────────┐
│  Claude Code     │  (Your machine or remote)
│  (MCP Client)    │
└────────┬─────────┘
         │ HTTPS (MCP Protocol via SSE)
         ▼
┌──────────────────┐
│ ngrok/cloudflare │  (Tunnel Service)
│ Public HTTPS URL │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  FastAPI Backend │  (localhost:8000)
│  + MCP Server    │  (Your local machine)
└──────────────────┘
```

## Security Notes

⚠️ **Development Only:**
- Current setup allows all CORS origins (`*`)
- No authentication on MCP endpoints
- Suitable for development and testing only

🔒 **For Production:**
- Add authentication to MCP endpoints
- Restrict CORS origins to specific domains
- Use rate limiting
- Monitor access logs
- Set `ENVIRONMENT=production` environment variable

## Troubleshooting

### Backend Not Starting

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill process using port 8000
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8001
# Then tunnel: ngrok http 8001
```

### Tunnel Connection Issues

```bash
# Test local backend first
curl http://localhost:8000/health

# If that works, test tunnel
curl https://YOUR_TUNNEL_URL/health

# Check ngrok web UI for requests
# Open: http://127.0.0.1:4040
```

### MCP Connection Issues

```bash
# Verify MCP endpoint is accessible
curl https://YOUR_TUNNEL_URL/mcp/health

# Check backend logs
# Look for: "MCP SSE connection initiated"

# Verify mcp.json configuration
cat ~/.config/claude/mcp.json
```

### CORS Errors

If you see CORS errors in browser/client:
1. Check `app/main.py` CORS configuration
2. Ensure `ENVIRONMENT` is not set to "production" (or CORS_ORIGINS includes your client)
3. Restart backend after changes

## Advanced: Custom Domain

Instead of random URLs, you can use ngrok with a custom domain (requires paid plan):

```bash
ngrok http 8000 --domain=your-custom-domain.ngrok.app
```

Or use Cloudflare Tunnel with your own domain (requires Cloudflare account).

## Keeping Tunnel Running

### Screen (Linux)

```bash
# Start screen session
screen -S backend

# Start backend
cd declaring && uvicorn main:app --reload

# Detach: Ctrl+A, then D

# In another terminal, start tunnel
screen -S tunnel
ngrok http 8000

# Detach: Ctrl+A, then D

# Reattach later
screen -r backend
screen -r tunnel
```

### tmux (Linux/macOS)

```bash
# Start tmux
tmux new -s backend

# Start backend
cd declaring && uvicorn main:app --reload

# Detach: Ctrl+B, then D

# New session for tunnel
tmux new -s tunnel
ngrok http 8000

# List sessions
tmux ls

# Reattach
tmux attach -t backend
```

## Resources

- **MCP Documentation:** [app/mcp/README.md](app/mcp/README.md)
- **ngrok Docs:** https://ngrok.com/docs
- **Cloudflare Tunnel:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **MCP Protocol:** https://modelcontextprotocol.io/
- **API Documentation:** http://localhost:8000/docs (when running locally)

## Next Steps

1. ✅ Expose backend via tunnel
2. ✅ Verify endpoints are accessible
3. ✅ Configure Claude Code with MCP server
4. ✅ Test MCP tools from Claude
5. 🔒 Add authentication before production use
6. 📊 Monitor usage and logs

Happy tunneling! 🚀
