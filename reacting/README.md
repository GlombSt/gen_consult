# Reacting - Frontend (Primary Adapter)

React application acting as a **primary adapter** to the backend hexagon, implementing presentation and user interaction with strict separation of concerns.

## Architecture Role

**This frontend IS a primary adapter** - NOT part of the hexagon. It drives the backend's business core through the HTTP API port.

```
┌─────────────────────────────────────────────┐
│         BACKEND = THE HEXAGON               │
│         (Business Core)                     │
│                                             │
│    ┌─────────────────────────────────┐     │
│    │  Domain Models & Business Logic │     │
│    │  Service Layer = PORTS          │     │
│    └─────────────────────────────────┘     │
│                                             │
└─────────────────────────────────────────────┘
                    │
                    │ HTTP API
                    ▼
┌─────────────────────────────────────────────┐
│   THIS FRONTEND = PRIMARY ADAPTER           │
│   (Presentation Layer Only)                 │
│                                             │
│  - React Components (UI)                    │
│  - Feature Hooks (orchestration)            │
│  - API Clients (HTTP communication)         │
│  - View Models (display formatting)         │
│  - NO business logic                        │
└─────────────────────────────────────────────┘
```

**Critical Understanding:**
- ALL business logic lives in the backend
- Frontend is for presentation and UX only
- Frontend types mirror backend `schemas.py` (API DTOs), NOT `models.py` (domain models)
- Client validation is for UX feedback only, not business rules

For complete architecture overview, see:
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Frontend architecture patterns and responsibilities
- [Backend ARCHITECTURE_STANDARDS.md](../declaring/ARCHITECTURE_STANDARDS.md) - Backend hexagon rules
- [Root CLAUDE.md](../CLAUDE.md) - Full-stack architecture overview

## Project Structure

```
reacting/
├── src/
│   ├── features/                   # Feature modules (mirror backend domains)
│   │   └── items/
│   │       ├── components/         # UI components (thin, delegate to hooks)
│   │       ├── hooks/              # Orchestration layer (API + UI state)
│   │       ├── api/                # HTTP adapter to backend
│   │       └── utils/              # Display formatting, UX helpers
│   │
│   ├── shared/                     # Reusable cross-cutting code
│   │   ├── components/             # Reusable UI components
│   │   ├── api/                    # httpClient, apiConfig, apiError
│   │   └── utils/                  # Generic utilities
│   │
│   ├── App.jsx                     # Application root
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
│
├── index.html                      # HTML template
├── package.json                    # Dependencies and scripts
├── vite.config.js                  # Vite configuration
│
├── README.md                       # This file
├── ARCHITECTURE.md                 # Frontend architecture guide
└── PROMPT_BUILDER_STRUCTURE.md     # Feature-specific documentation
```

### Feature Organization

Each feature mirrors a backend domain and follows this structure:

```
src/features/{domain}/
├── components/         # React components (NO API calls, NO business logic)
│   └── ItemList/
│       ├── ItemList.jsx
│       └── ItemList.css
│
├── hooks/             # Orchestration (API calls + UI state)
│   ├── useItems.js
│   └── useCreateItem.js
│
├── api/               # HTTP communication (NO business logic)
│   └── itemsApi.js
│
└── utils/             # Pure functions (formatting, display helpers)
    └── itemFormatters.js
```

**Layer Responsibilities:**
- **Components:** Render UI, handle interactions, NO API calls, NO business logic
- **Hooks:** Orchestrate API calls, manage UI state (loading, error), NO business logic
- **API Clients:** HTTP communication only, NO business logic, NO UI state
- **Utils:** Pure functions for formatting/display only

## Quick Start

### Prerequisites

- Node.js 18+
- npm

### Development Setup

```bash
cd reacting

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Development server runs at:** `http://localhost:5173`

The application will automatically reload when you make changes.

## Architecture Principles

### 1. Thin Client Architecture

This frontend is intentionally thin. It delegates all business logic to the backend.

**✅ Frontend Responsibilities:**
- Presentation (render data attractively)
- User interaction (clicks, forms, navigation)
- Loading states and error display
- Optimistic UI updates
- Client validation for UX feedback only

**❌ NOT Frontend Responsibilities:**
- Business rule validation
- Complex calculations (pricing, tax)
- Authorization decisions
- Domain entity classes with methods
- Cross-entity business logic

### 2. Feature-Based Organization

Features mirror backend domains (not technical layers):

```
✅ Good: src/features/items/, src/features/users/
❌ Bad: src/components/, src/services/, src/utils/
```

Benefits:
- Easy to locate feature code
- Clear domain boundaries
- Can delete entire feature folders
- Mirrors backend domain structure

### 3. Component → Hook → API Pattern

Standard development pattern:

```javascript
// 1. API Client (infrastructure)
// src/features/items/api/itemsApi.js
export const itemsApi = {
  getAll: () => httpClient.get('/items'),
  create: (data) => httpClient.post('/items', data)
}

// 2. Hook (orchestration)
// src/features/items/hooks/useItems.js
export const useItems = () => {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    itemsApi.getAll()
      .then(setItems)
      .finally(() => setLoading(false))
  }, [])

  return { items, loading }
}

// 3. Component (presentation)
// src/features/items/components/ItemList/ItemList.jsx
export const ItemList = () => {
  const { items, loading } = useItems()

  if (loading) return <Spinner />
  return <ul>{items.map(item => <li>{item.name}</li>)}</ul>
}
```

**Flow:** Component uses Hook → Hook calls API Client → API Client calls Backend

### 4. Type Mapping (Important!)

Frontend types mirror **backend `schemas.py`** (API DTOs), NOT `models.py` (domain models):

```
Backend schemas.py:
  class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

Frontend types:
  // Mirror the API contract
  interface ItemResponse {
    id: number;
    name: string;
    price: number;
  }

Backend models.py:
  class Item:  # Domain model with business logic
    # DON'T mirror this in frontend!
```

**Why?** Frontend only sees what the API exposes. Domain models contain sensitive internal data and business methods that don't belong in the UI.

### 5. View Models

Transform backend DTOs for display purposes:

```javascript
// View model: shape data for display
const formatItemForDisplay = (item) => ({
  ...item,
  displayPrice: `$${item.price.toFixed(2)}`,
  displayDate: new Date(item.created_at).toLocaleDateString()
})
```

**View models are NOT domain entities** - they're display-specific transformations.

## Connecting to Backend

### Backend API

The backend runs at `http://localhost:8000` (by default).

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Client Configuration

Configure the base URL in `src/shared/api/apiConfig.js`:

```javascript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### CORS Configuration

The backend is pre-configured for common frontend dev ports (3000, 5173, 8080).

If you run on a different port, update the CORS origins in `declaring/app/main.py`.

### Error Handling

Handle backend errors gracefully:

```javascript
try {
  const item = await itemsApi.create(data)
  // Success!
} catch (error) {
  if (error.response?.status === 422) {
    // Validation error from backend
    showValidationErrors(error.response.data)
  } else {
    // Generic error
    showErrorMessage('Something went wrong')
  }
}
```

See backend [EXCEPTION_HANDLING_GUIDE.md](../declaring/EXCEPTION_HANDLING_GUIDE.md) for error response format.

## Adding New Features

### Create a New Feature Module

When the backend adds a new domain, mirror it in the frontend:

1. **Create feature folder:**
   ```bash
   mkdir -p src/features/orders/{components,hooks,api,utils}
   ```

2. **Build API client** (`api/ordersApi.js`):
   ```javascript
   export const ordersApi = {
     getAll: () => httpClient.get('/orders'),
     create: (data) => httpClient.post('/orders', data)
   }
   ```

3. **Create hooks** (`hooks/useOrders.js`):
   ```javascript
   export const useOrders = () => {
     // Orchestrate API + UI state
   }
   ```

4. **Build components** (`components/OrderList/OrderList.jsx`):
   ```javascript
   export const OrderList = () => {
     const { orders, loading } = useOrders()
     // Render UI
   }
   ```

5. **Add utilities if needed** (`utils/orderFormatters.js`):
   ```javascript
   export const formatOrderDate = (date) => { /* ... */ }
   ```

**Key principles:**
- Mirror backend domain names
- Keep components thin (delegate to hooks)
- NO business logic in frontend
- Types mirror backend `schemas.py`

## Development Guidelines

### Component Best Practices

```javascript
// ✅ Good: Thin component, delegates to hook
const ItemList = () => {
  const { items, loading, error } = useItems()

  if (loading) return <Spinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <ul>
      {items.map(item => (
        <ItemCard key={item.id} item={item} />
      ))}
    </ul>
  )
}

// ❌ Bad: Business logic in component
const ItemList = () => {
  const [items, setItems] = useState([])

  // ❌ Don't replicate backend business rules
  const availableItems = items.filter(item => {
    // Complex business logic doesn't belong here!
    return item.stock > 0 && item.price > 0 && !item.expired
  })

  return <ul>{/* ... */}</ul>
}
```

### Hook Best Practices

```javascript
// ✅ Good: Orchestrates API and UI state
const useCreateItem = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const createItem = async (data) => {
    setLoading(true)
    setError(null)
    try {
      const item = await itemsApi.create(data)
      return item
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { createItem, loading, error }
}

// ❌ Bad: Business validation in hook
const useCreateItem = () => {
  const createItem = async (data) => {
    // ❌ Don't validate business rules in frontend
    if (data.price < 0 || data.price > 10000) {
      throw new Error('Invalid price')
    }
    // Backend should handle this validation!
  }
}
```

### API Client Best Practices

```javascript
// ✅ Good: Simple HTTP abstraction
export const itemsApi = {
  getAll: () => httpClient.get('/items'),
  getById: (id) => httpClient.get(`/items/${id}`),
  create: (data) => httpClient.post('/items', data)
}

// ❌ Bad: Business logic in API client
export const itemsApi = {
  create: (data) => {
    // ❌ Don't transform or validate business data
    const adjustedPrice = calculateDiscountedPrice(data)
    return httpClient.post('/items', { ...data, price: adjustedPrice })
  }
}
```

## Testing (Future)

Testing structure will mirror backend approach:

- **Component tests:** Mock hooks, test rendering
- **Hook tests:** Mock API clients, test orchestration
- **API client tests:** Mock httpClient, test HTTP calls

See [TODO.md](../TODO.md) for testing framework decision.

## Troubleshooting

### CORS Errors

**Problem:** Browser blocks requests due to CORS policy

**Solution:**
1. Check backend is running at `http://localhost:8000`
2. Verify your frontend port is in backend's CORS allowed origins
3. Add your port to `declaring/app/main.py` if needed

### 404 Errors

**Problem:** API returns 404 for requests

**Solution:**
1. Verify endpoint exists in backend: http://localhost:8000/docs
2. Check path matches (e.g., `/items` not `/api/items`)
3. Ensure backend is running

### Network Errors

**Problem:** "Network request failed"

**Solution:**
1. Confirm backend is running: `curl http://localhost:8000/health`
2. Check API base URL in `src/shared/api/apiConfig.js`
3. Review browser console for details

### Type Mismatches

**Problem:** Frontend expects different data shape than backend provides

**Solution:**
1. Check backend API docs: http://localhost:8000/docs
2. Verify you're mirroring `schemas.py` (API DTOs), not `models.py`
3. Update frontend types to match backend response

See [Backend DEBUGGING.md](../declaring/DEBUGGING.md) for more troubleshooting.

## Key Reminders

### ✅ DO

- Keep components thin
- Delegate to backend for business logic
- Mirror backend domain structure
- Use hooks for orchestration
- Handle loading and error states
- Provide good UX feedback

### ❌ DON'T

- Replicate backend business rules
- Create complex entity classes
- Make business decisions in frontend
- Validate business constraints
- Assume client validation is sufficient
- Bypass hooks and call API directly from components

## Learning Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Backend Architecture](../declaring/ARCHITECTURE_STANDARDS.md)

## Need Help?

1. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for frontend patterns
2. Review backend API docs: http://localhost:8000/docs
3. Read [CLAUDE.md](../CLAUDE.md) for full-stack context
4. Consult [Backend DEBUGGING.md](../declaring/DEBUGGING.md) for integration issues
