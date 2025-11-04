# Architecture Documentation Alignment - TODO

**Created:** 2025-10-28
**Status:** In Progress
**Goal:** Align architecture documentation between `declaring/` (backend) and `reacting/` (frontend) projects

---

## Priority 1: Quick Fixes (High Impact, Low Effort)

### ✅ Task 1: Align Terminology in Both Docs ✅ COMPLETED
**Files to update:**
- `declaring/ARCHITECTURE_STANDARDS.md`
- `declaring/ARCHITECTURE_GUIDE.md`
- `reacting/ARCHITECTURE.md`

**Changes:**
- [x] Use "hexagonal architecture" consistently in both projects
- [x] Backend docs should explicitly state: "Backend IS the hexagon (business core)"
- [x] Frontend docs should explicitly state: "Frontend IS a primary adapter (not part of hexagon)"
- [x] Add cross-references between docs
- [x] Ensure both use same vocabulary (ports, adapters, domain, service layer)

**Estimated effort:** 30 minutes
**Actual effort:** ~30 minutes

**Summary of Changes:**
- Added hexagonal architecture overview diagrams to all three docs
- Explicitly labeled service layer as "PORTS"
- Explicitly labeled router as "PRIMARY ADAPTER"
- Explicitly labeled repository as "SECONDARY ADAPTER"
- Added cross-references between backend and frontend docs
- Updated frontend diagram to show it's outside the hexagon
- Consistent terminology: hexagon, ports, adapters throughout

---

### ✅ Task 2: Clarify Type Mapping in Frontend Docs
**Files to update:**
- `reacting/ARCHITECTURE.md`

<!-- TODO: DECISION NEEDED
Question: Should we enforce strict TypeScript usage in the frontend?
Currently: Frontend uses vanilla JavaScript with JSX
Options:
  A) Keep JavaScript, add JSDoc type comments for documentation
  B) Migrate to TypeScript for type safety
  C) Hybrid: New features in TypeScript, old code stays JS

Impact on this task:
- Option A: Document type patterns in comments
- Option B: Create proper .types.ts files
- Option C: Document both approaches

Decision maker: Project lead
Timeline: Before implementing Task 2
-->

**Changes:**
- [ ] Clarify: Frontend types mirror backend `schemas.py` (API DTOs), NOT `models.py` (domain models)
- [ ] Define "View Models" clearly: "Transformations of DTOs for display purposes"
- [ ] Add example: Backend `ItemResponse` (schemas.py) → Frontend `ItemResponse` type
- [ ] Document what types belong in `features/{domain}/types/`

**Estimated effort:** 20 minutes (if staying with JS), 2-4 hours (if migrating to TS)

---

### ✅ Task 3: Add Event Strategy Note to Both Docs
**Files to update:**
- `declaring/ARCHITECTURE_STANDARDS.md` (add section)
- `reacting/ARCHITECTURE.md` (add section)

<!-- TODO: DECISION NEEDED
Question: What is the real-time update strategy for the frontend?
Current: Frontend likely refetches after mutations (optimistic updates?)
Options:
  A) Keep current: Manual refetch after mutations
  B) Add polling: Periodic background refetch
  C) Add WebSocket/SSE: Real-time event streaming
  D) Hybrid: Critical data via WebSocket, rest via refetch

Impact on this task:
- Determines what to document about event consumption
- Affects architecture complexity
- May require backend changes (WebSocket endpoints)

Decision maker: Project lead
Timeline: Before implementing Task 3 and Task 8
Dependencies: Relates to Task 8 (Real-time updates architecture)
-->

**Changes:**
- [ ] Backend doc: Clarify that domain events are for analytics/logging/cross-domain communication
- [ ] Frontend doc: Clarify that frontend does NOT consume backend events directly (currently)
- [ ] Both: Document current strategy for keeping UI in sync (refetch after mutations)
- [ ] Both: Add note about future real-time updates (see Task 8)

**Estimated effort:** 30 minutes

---

## Priority 2: Fill Documentation Gaps (Medium Impact, Medium Effort)

### ✅ Task 4: Add Testing Documentation to Frontend
**Files to create:**
- `reacting/TESTING.md` (new file)

<!-- TODO: DECISION NEEDED
Question: What testing approach should the frontend use?
Current: No tests visible in codebase
Options:
  A) Jest + React Testing Library (industry standard)
  B) Vitest + React Testing Library (Vite-native, faster)
  C) Playwright/Cypress (E2E focus)
  D) Combination: Vitest for units, Playwright for E2E

Impact on this task:
- Determines testing framework to document
- Affects package.json dependencies
- Changes npm scripts

Decision maker: Project lead
Timeline: Before implementing Task 4
-->

**Content to add:**
- [ ] Mirror backend testing structure (unit, integration, e2e)
- [ ] Testing layers: Components (mock hooks), Hooks (mock API), API clients (mock httpClient)
- [ ] Coverage requirements (suggest 70%+ to match backend standards)
- [ ] Testing commands and setup
- [ ] Example tests for each layer

**Estimated effort:** 2-3 hours

---

### ✅ Task 5: Document Error Handling Contract
**Files to update:**
- `declaring/ARCHITECTURE_GUIDE.md` (add section on error responses)
- `reacting/ARCHITECTURE.md` (add section on error handling)

**Changes:**
- [ ] Backend: Document standard error response format
- [ ] Backend: List HTTP status codes used (400, 404, 422, 500)
- [ ] Frontend: Document how to parse backend errors
- [ ] Frontend: Document user-facing error display patterns
- [ ] Both: Example error flows (validation error, not found, server error)

**Estimated effort:** 1 hour

---

### ✅ Task 6: Create Cross-Project Request Flow Diagram
**Files to create:**
- `FULL_STACK_FLOW.md` (new file at root)

**Content to add:**
- [ ] Complete request lifecycle diagram (React → FastAPI → Database → React)
- [ ] Layer-by-layer breakdown with code examples
- [ ] Data transformation at each boundary
- [ ] Error handling flow
- [ ] Event publishing flow

**Estimated effort:** 2-3 hours

---

## Priority 3: Future Enhancements (Lower Priority, Higher Effort)

### ✅ Task 7: Type Synchronization Strategy
**Files to create/update:**
- `TOOLING.md` (new file at root)
- Update both architecture docs to reference it

<!-- TODO: DECISION NEEDED
Question: How should frontend types stay in sync with backend DTOs?
Current: Manual copy/paste and hope for the best
Options:
  A) Keep manual (simple, but error-prone)
  B) Use openapi-typescript to generate from FastAPI OpenAPI spec
  C) Use datamodel-code-generator to generate from Pydantic models
  D) Build custom script to extract types from schemas.py
  E) Shared schema definitions (e.g., JSON Schema)

Impact on this task:
- Option A: Document manual process
- Options B-E: Requires tooling setup, build pipeline changes
- Options B-C: Best with TypeScript (see Task 2 decision)

Decision maker: Project lead
Timeline: After Task 2 (depends on TS decision)
Dependencies: Blocks on Task 2 decision
-->

**Content to add:**
- [ ] Current approach documentation
- [ ] Recommended tooling options
- [ ] Setup guide for chosen approach
- [ ] Workflow for type updates

**Estimated effort:** 4-8 hours (depending on chosen approach)

---

### ✅ Task 8: Real-Time Updates Architecture
**Files to create:**
- `REALTIME_UPDATES.md` (new file at root, or defer until needed)

<!-- TODO: DECISION NEEDED
Question: Do you need real-time updates? If yes, what approach?
Current: Likely none (fetch on load, refetch on mutation)
Options:
  A) Defer: Don't implement until actually needed
  B) Server-Sent Events (SSE): One-way server → client
  C) WebSocket: Bi-directional communication
  D) Long polling: Compatible but inefficient
  E) Third-party: Pusher, Ably, Socket.io

Impact on this task:
- Option A: Document "future consideration" placeholder
- Options B-E: Requires backend endpoints, frontend integration, infrastructure

Considerations:
- Do users need to see updates from other users in real-time?
- What data needs to be real-time? (notifications, inventory, prices?)
- Scale requirements?

Decision maker: Product owner + Project lead
Timeline: Can defer until user need is clear
Related to: Task 3 (event strategy)
-->

**Content to add:**
- [ ] Use cases requiring real-time updates
- [ ] Technology comparison (WebSocket vs SSE vs polling)
- [ ] Architecture diagrams
- [ ] Implementation guide
- [ ] Backend event streaming setup
- [ ] Frontend subscription patterns

**Estimated effort:** 8-16 hours (full implementation)

---

### ✅ Task 9: Feature Addition Workflow Guide
**Files to create:**
- `ADDING_FEATURES.md` (new file at root)

**Content to add:**
- [ ] Step-by-step guide: Backend domain creation
- [ ] Step-by-step guide: Frontend feature creation
- [ ] Integration checklist
- [ ] Testing requirements
- [ ] Documentation updates needed
- [ ] Example: Adding "Orders" feature end-to-end

**Estimated effort:** 2-3 hours

---

## Task Dependencies

```
DECISIONS NEEDED FIRST:
├─ Task 2 depends on: TypeScript vs JavaScript decision
├─ Task 3 depends on: Real-time update strategy decision
├─ Task 4 depends on: Testing framework decision
├─ Task 7 depends on: Task 2 (TS decision)
└─ Task 8 depends on: Product requirements (defer if no need)

RECOMMENDED ORDER:
1. Make all decisions (see TODO comments above)
2. Execute Priority 1 tasks (1, 2, 3)
3. Execute Priority 2 tasks (4, 5, 6)
4. Execute Priority 3 tasks as needed (7, 8, 9)
```

---

## Questions for Project Lead

Before starting work, please decide:

1. **TypeScript Migration?** (Affects Tasks 2, 7)
   - Stay with JavaScript + JSDoc?
   - Migrate to TypeScript?
   - Hybrid approach?

2. **Real-Time Updates?** (Affects Tasks 3, 8)
   - Current refetch strategy sufficient?
   - Need WebSocket/SSE?
   - Specific use cases requiring real-time?

3. **Testing Framework?** (Affects Task 4)
   - Vitest (recommended for Vite projects)?
   - Jest?
   - E2E testing needed?

4. **Type Sync Approach?** (Affects Task 7, depends on Q1)
   - Manual (current)?
   - Auto-generate from OpenAPI?
   - Other tooling?

---

## Progress Tracking

- [ ] Priority 1 Complete (Tasks 1-3)
- [ ] Priority 2 Complete (Tasks 4-6)
- [ ] Priority 3 Complete (Tasks 7-9)
- [ ] All architecture docs aligned and cross-referenced
- [ ] Developer onboarding improved

---

## Notes

- Tasks 1, 3, 5, 6, 9 can proceed without major decisions
- Tasks 2, 4, 7, 8 are blocked on decisions (see TODO comments)
- Consider tackling "decision-free" tasks first while decisions are being made
- Estimated total effort: 20-40 hours (depending on scope decisions)
