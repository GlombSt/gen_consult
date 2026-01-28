# Customer UX - Frontend Application

A React-based frontend that serves as a **primary adapter** to the Gen Consult backend hexagon. This is a thin client focused on presentation and user experience, with all business logic residing in the backend.

## Prerequisites

- **Node.js** 18+ and npm
- **Backend** must be running at `http://localhost:8000` (see [declaring/](../declaring/))

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Development server:** http://localhost:5173

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Vanilla JavaScript** - Language (TypeScript decision pending, see [TODO.md](../TODO.md))

## Project Structure

```
src/
├── features/              # Feature-based organization (mirrors backend domains)
│   ├── items/            # Items feature (API client, hooks, components)
│   └── [domain]/         # Each backend domain gets its own feature folder
├── shared/
│   ├── components/       # Reusable UI components
│   ├── api/              # HTTP client, API config, error handling
│   └── utils/            # Generic utilities
├── App.jsx               # Root component
└── main.jsx              # Application entry point
```

**Key principle:** Features are organized by domain (items, users, orders), not by technical layer. Each feature contains its own components, hooks, API clients, and utilities.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed layer responsibilities and patterns.

## Backend Integration

**Default configuration:**
- Backend API: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- CORS: Pre-configured for port 5173

**Change API URL:** Update `src/shared/api/apiConfig.js`

## Development Workflow

### Adding a New Feature

When adding a feature that connects to a backend domain:

1. **Create feature structure**
   ```bash
   src/features/[domain]/
   ├── api/              # API client
   ├── hooks/            # Orchestration hooks
   ├── components/       # UI components
   └── utils/            # Feature-specific utilities
   ```

2. **Build API client** (`api/[domain]Api.js`)
   - Define functions for backend endpoints
   - Use shared `httpClient` for HTTP calls

3. **Create hooks** (`hooks/useCreate[Entity].js`)
   - Orchestrate API calls
   - Manage UI state (loading, errors)

4. **Build components** (`components/[Entity]Creator/`)
   - Use hooks for data and actions
   - Focus on presentation only

**Example:** See `src/features/items/` for a complete reference implementation.

For detailed patterns and architectural guidelines, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Key Architectural Principles

1. **Thin client** - No business logic in frontend; backend validates everything
2. **Feature-based** - Organize by domain (items, users), not by technical layer (components, services)
3. **Layer separation** - Components → Hooks → API clients
4. **DTO mapping** - Frontend types mirror backend `schemas.py` (API DTOs), not `models.py` (domain models)

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Comprehensive architectural guidelines, layer responsibilities, patterns, and anti-patterns
- **[PROMPT_BUILDER_STRUCTURE.md](./PROMPT_BUILDER_STRUCTURE.md)** - Feature structure planning document
- **[../CLAUDE.md](../CLAUDE.md)** - Full-stack architecture overview
- **[../declaring/](../declaring/)** - Backend documentation and API reference

## Common Tasks

### Connecting to a Backend Endpoint

1. Add function to feature's API client (`features/[domain]/api/`)
2. Create or update hook to call the API function
3. Use hook in component

### Adding a Shared Component

Place in `src/shared/components/[ComponentName]/` if it's used across multiple features.

### Adding Feature-Specific Utilities

Place in `features/[domain]/utils/` (e.g., formatters, validators for that feature only).

## Testing

```bash
# Unit tests (when configured)
npm test

# E2E tests (when configured)
npm run test:e2e
```

## Troubleshooting

**CORS errors:**
- Ensure backend is running on port 8000
- Check backend CORS configuration in `declaring/app/main.py`

**API connection refused:**
- Verify backend is running: `http://localhost:8000/health`
- Check `src/shared/api/apiConfig.js` for correct base URL

**Port 5173 already in use:**
- Stop other Vite instances or specify different port: `npm run dev -- --port 3000`

## Architecture Role

This React application is a **primary adapter** in the hexagonal architecture:

```
┌─────────────────────────────────────────┐
│   BACKEND = HEXAGON (Business Core)     │
│   - Domain logic                        │
│   - Business rules                      │
│   - Event system                        │
└─────────────────────────────────────────┘
                    ▲
                    │ HTTP API
                    │
┌─────────────────────────────────────────┐
│   FRONTEND = PRIMARY ADAPTER            │
│   - Presentation layer                  │
│   - User interactions                   │
│   - NO business logic                   │
└─────────────────────────────────────────┘
```

The backend contains all business logic. This frontend drives the backend through its HTTP API port.

---

**For complete architectural guidelines, patterns, and decision rationale, see [ARCHITECTURE.md](./ARCHITECTURE.md).**
