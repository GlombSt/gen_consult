# Architecture Guidelines

## Overview

This React application is a **primary adapter** to the backend's hexagonal architecture. The backend contains the true domain model, business rules, and core logic. Our UI is thin and focused on presentation.

## Core Understanding: The UI's Role

```
┌─────────────────────────────────────────────────────────┐
│                    BACKEND SYSTEM                       │
│              (True Hexagonal Architecture)              │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │            DOMAIN CORE                           │ │
│  │   - Entities (Item, User, Order)                 │ │
│  │   - Business Rules & Validation                  │ │
│  │   - Domain Events                                │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │      API LAYER (Primary Adapter/Port)            │ │
│  │   - REST/GraphQL Endpoints                       │ │
│  │   - DTOs for data transfer                       │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 REACT UI APPLICATION                    │
│                  (This Codebase)                        │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │      PRESENTATION LAYER                          │ │
│  │   - React Components                             │ │
│  │   - UI State & Interactions                      │ │
│  │   - Display Logic                                │ │
│  └──────────────────────────────────────────────────┘ │
│                     │                                   │
│                     ▼                                   │
│  ┌──────────────────────────────────────────────────┐ │
│  │      APPLICATION LAYER                           │ │
│  │   - Feature Hooks (orchestration)                │ │
│  │   - View Models (shape data for UI)             │ │
│  │   - Client-side state management                 │ │
│  └──────────────────────────────────────────────────┘ │
│                     │                                   │
│                     ▼                                   │
│  ┌──────────────────────────────────────────────────┐ │
│  │      INFRASTRUCTURE LAYER                        │ │
│  │   - API Client (abstraction over HTTP)           │ │
│  │   - LocalStorage/SessionStorage                  │ │
│  │   - WebSocket clients                            │ │
│  │   - Browser APIs                                 │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Key Insight**: We're not building a full hexagonal architecture on the client. We're building a well-organized adapter (the UI) that talks to the backend's hexagonal architecture. The internal layering helps keep the UI maintainable, but the business logic stays in the backend.

## Responsibility Boundaries

### ✅ UI Responsibilities (This React App):

- **Presentation**: Render data in a user-friendly way
- **User Interaction**: Handle clicks, form inputs, navigation
- **Client-side UX**: Immediate feedback, optimistic updates, loading states
- **View Models**: Shape backend data for display (e.g., formatting dates, combining fields)
- **Client-side Validation**: For UX only (fast feedback), NOT business rules
- **UI State**: Modals, tabs, filters, pagination state
- **API Abstraction**: Hide HTTP details so you can swap implementations

### ❌ NOT UI Responsibilities (Belongs in Backend):

- **Business Rules**: "Can this order be cancelled?" "Is this price valid?"
- **Domain Validation**: "Email format must be X" "Name length must be Y"
- **Complex Calculations**: Pricing, tax, inventory calculations
- **Domain Entities**: The "real" Item, User, Order objects live in the backend
- **Authorization**: "Can this user perform this action?"
- **Data Consistency**: Ensuring aggregates maintain their invariants

### 🤔 Gray Areas (Use Judgment):

- **TypeScript Types/Interfaces**: Mirror backend DTOs for type safety
- **Simple Validation**: Duplicate basic validation for instant UX feedback (but backend is source of truth)
- **Enums/Constants**: Can duplicate backend enums if they're stable
- **UI-specific Business Logic**: Shopping cart state before checkout, draft mode, etc.

**Key Question**: *"Is this logic about how to display data, or about business rules?"*  
**Display logic** → frontend. **Business rules** → backend.

## Folder Structure

```
src/
├── features/                       # Feature-based organization (Screaming Architecture)
│   ├── items/                     # Everything related to Items
│   │   ├── components/            # UI components
│   │   │   ├── ItemCreator/
│   │   │   ├── ItemList/
│   │   │   └── ItemDetails/
│   │   ├── hooks/                 # Feature-specific hooks
│   │   │   ├── useCreateItem.js  # Orchestrates API call + UI state
│   │   │   ├── useItemList.js    # Fetch and manage items
│   │   │   └── useDeleteItem.js
│   │   ├── api/                   # API client for this feature
│   │   │   └── itemsApi.js       # API calls for items
│   │   ├── types/                 # TypeScript types (if using TS)
│   │   │   └── item.types.ts     # Mirrors backend DTOs
│   │   └── utils/                 # Feature-specific utilities
│   │       ├── itemFormatters.js # Format items for display
│   │       └── itemValidation.js # Client-side validation (UX only)
│   │
│   ├── users/                     # Everything related to Users
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── types/
│   │
│   └── orders/                    # Everything related to Orders
│       ├── components/
│       ├── hooks/
│       ├── api/
│       └── types/
│
├── shared/                        # Shared across features
│   ├── components/                # Reusable UI components
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Modal/
│   │   └── Spinner/
│   ├── hooks/                     # Generic hooks
│   │   ├── useDebounce.js
│   │   └── useLocalStorage.js
│   ├── api/                       # Shared API infrastructure
│   │   ├── httpClient.js         # Configured HTTP client
│   │   ├── apiConfig.js          # Base URL, headers, interceptors
│   │   └── apiError.js           # Error handling utilities
│   └── utils/                     # Generic utilities
│       ├── dateFormatters.js
│       └── validators.js
│
├── layouts/                       # Page layouts
│   ├── MainLayout.jsx
│   └── AuthLayout.jsx
│
├── config/                        # App configuration
│   ├── constants.js              # App-wide constants
│   └── env.js                    # Environment variables
│
├── App.jsx                        # Root component
└── main.jsx                       # Entry point
```

## Layer Responsibilities

### Infrastructure Layer (`shared/api/`, `features/*/api/`)
- Abstract HTTP communication (fetch, axios, GraphQL)
- Handle authentication tokens
- Parse and throw structured errors
- Define API endpoints
- **No business logic, no UI state**

### Application Layer (`features/*/hooks/`)
- Orchestrate API calls
- Manage UI state (loading, errors)
- Parse backend validation errors
- Handle optimistic updates
- **No business logic, no direct HTTP calls**

### Presentation Layer (`features/*/components/`, `shared/components/`)
- Render UI based on state
- Handle user interactions
- Delegate logic to hooks
- Display validation errors
- **No business logic, no direct API calls**

### Utilities (`features/*/utils/`, `shared/utils/`)
- Format data for display
- Client-side validation (UX only)
- Pure helper functions
- **No side effects, no business rules**

## Guidelines for Daily Development

### When Adding a New Feature:

1. **Create the Feature Folder Structure**
   - `src/features/[feature-name]/`
   - Add subdirectories: `components/`, `hooks/`, `api/`, `utils/`

2. **Build the API Client** (`api/[feature]Api.js`)
   - Define functions for all backend endpoints
   - Return plain DTOs from backend (no transformation)
   - Use shared `httpClient` for actual HTTP calls

3. **Add Utilities** (if needed)
   - `utils/[feature]Formatters.js` - for display formatting
   - `utils/[feature]Validation.js` - for client-side UX validation

4. **Create Feature Hooks**
   - `hooks/useCreate[Entity].js` - for create operations
   - `hooks/use[Entity]List.js` - for fetching lists
   - `hooks/use[Entity].js` - for fetching single entity
   - Hooks orchestrate API calls and manage UI state

5. **Build Components**
   - Keep them thin - delegate to hooks
   - Handle user interactions
   - Display data and errors
   - No business logic!

### File Naming Conventions:

- **Components**: PascalCase with folder (e.g., `ItemCreator/ItemCreator.jsx`)
- **Hooks**: camelCase with 'use' prefix (e.g., `useCreateItem.js`)
- **API Clients**: camelCase with 'Api' suffix (e.g., `itemsApi.js`)
- **Utilities**: camelCase descriptive names (e.g., `itemFormatters.js`)
- **Types** (if TypeScript): camelCase with '.types.ts' (e.g., `item.types.ts`)

### Testing Strategy:

```
src/features/items/
├── api/
│   ├── itemsApi.js
│   └── itemsApi.test.js         # Test with mock httpClient
├── hooks/
│   ├── useCreateItem.js
│   └── useCreateItem.test.js    # Test with mock API
├── utils/
│   ├── itemFormatters.js
│   └── itemFormatters.test.js   # Pure function tests
└── components/
    └── ItemCreator/
        ├── ItemCreator.jsx
        └── ItemCreator.test.jsx # Test with mock hook
```

**Testing Principles:**
- Test each layer independently
- Mock dependencies at layer boundaries
- Infrastructure: Test error handling and request building
- Hooks: Test orchestration logic with mock APIs
- Components: Test rendering and interactions with mock hooks
- Utils: Test pure functions (no mocks needed)

## Anti-Patterns to Avoid

### ❌ Don't Duplicate Domain Logic
Don't replicate backend business rules. Let the backend tell you what's valid.

### ❌ Don't Create Complex Entity Classes
Work with plain DTOs. No rich domain objects with business methods on the client.

### ❌ Don't Mix API Calls into Components
Always go through hooks. Never call API directly from components.

### ❌ Don't Put Business Rules in Formatters
Formatters are for display only (e.g., date formatting, truncation). Not for decisions.

### ❌ Don't Validate Business Rules Client-Side
Client validation is for UX only. Backend must re-validate everything.

## When to Break the Rules

These guidelines are principles, not dogma:

1. **Duplicate simple validation for UX**: "Email must contain @" is fine for instant feedback
2. **Cache data locally**: LocalStorage/IndexedDB for offline support is acceptable
3. **Optimistic updates**: Update UI before backend responds (but be ready to roll back)
4. **UI-specific business logic**: Complex form wizards, drag-and-drop state management

## Migration Path

For existing code:

1. **Phase 1**: Create new folder structure
   - Create `src/features/items/` with subdirectories
   - Create `src/shared/api/` for HTTP client

2. **Phase 2**: Extract and enhance API client
   - Move `src/services/api.js` → `src/shared/api/httpClient.js`
   - Create `src/features/items/api/itemsApi.js`
   - Add error handling with `ApiError` class

3. **Phase 3**: Create feature hook
   - Extract `useCreateItem` hook from component logic
   - Add optional client-side validation

4. **Phase 4**: Refactor component
   - Move `ItemCreator` to `src/features/items/components/`
   - Update to use the new hook
   - Remove any business logic

5. **Phase 5**: Add utilities as needed
   - Add formatters for display logic
   - Add validation helpers for UX

## Key Benefits

### Testability
API clients can be mocked easily. Each layer tests independently. No complex setup.

### Flexibility
Swap HTTP client implementation (fetch → axios → GraphQL) without touching features.

### Maintainability
Clear separation of concerns. Features are isolated. Single source of truth in backend.

### Scalability
Add features independently. Team members don't step on each other. No duplication of logic.

## Summary

This React app is a **thin client** and a **primary adapter** to your backend:

- ✅ **Focus on presentation and user experience**
- ✅ **Abstract infrastructure** (HTTP, WebSocket, storage) so it's swappable
- ✅ **Organize by features** so the codebase is easy to navigate
- ✅ **Use hooks to orchestrate** API calls and UI state
- ❌ **Don't replicate backend business logic**
- ❌ **Don't create complex domain entities**
- ❌ **Don't try to build a full hexagonal architecture**

---

**Architecture serves the team and the product.** Start simple, refactor as complexity grows, and always prioritize clarity over cleverness. The backend has the business logic. The frontend makes it accessible and delightful.
