# Intents Domain V2 — Implementation Plan

This document plans the implementation of the domain model described in **INTENTS_DOMAIN_V2.md**, refactoring from the current V1 implementation (Intent + Fact, with Intent holding output_format, output_structure, context, constraints).

---

## 1. Summary of Changes (V1 → V2)

| Area | V1 | V2 |
|------|----|----|
| **Intent** | id, name, description, output_format, output_structure, context, constraints, created_at, updated_at | id, name, description, created_at, updated_at |
| **Fact** | Removed | Replaced by six articulation entities |
| **New: Aspect** | — | intent_id, name, description?, created_at, updated_at |
| **New: Articulation** | — | Input, Choice, Pitfall, Assumption, Quality, Example (each: intent_id, optional aspect_id, entity-specific fields) |
| **Prompt** | Not in DB | intent_id, content, version, created_at, updated_at |
| **Output** | Not in DB | prompt_id, content, created_at, updated_at |
| **Insight** | Not in DB | intent_id, content, source_type?, source_output_id?, source_prompt_id?, source_assumption_id?, status?, created_at, updated_at |

**Design decisions (fixed):**

- **ID type:** Integer (consistent with existing codebase). INTENTS_DOMAIN_V2.md uses integer for all entity ids and FKs.
- **user_id:** Not used. Intent has no ownership field; no user scoping in this refactor.
- **Migration:** Old tables (e.g. `facts`) and deprecated Intent columns can be **discarded**. No data migration from V1 to V2; treat as breaking change with no backfill.

---

## 2. Implementation Phases

### Phase 1 — Database and domain foundation

**Goal:** Add new tables and domain models without removing V1 yet, so the app still runs and tests can be updated incrementally.

1. **DB models (`db_models.py`)**
   - Add: `AspectDBModel`, `InputDBModel`, `ChoiceDBModel`, `PitfallDBModel`, `AssumptionDBModel`, `QualityDBModel`, `ExampleDBModel`, `PromptDBModel`, `OutputDBModel`, `InsightDBModel`. All IDs and FKs are integer.
   - Use enums where specified: Assumption.confidence (`verified` | `likely` | `uncertain`), Quality.priority (`must_have` | `should_have` | `nice_to_have`), Example.source (`user_provided` | `llm_generated` | `from_output`), Insight.source_type (`sharpening` | `output` | `prompt` | `assumption`), Insight.status (`pending` | `incorporated` | `dismissed`).
   - Define relationships: Intent → Aspects, Inputs, Choices, Pitfalls, Assumptions, Qualities, Examples, Insights, Prompts; Aspect → (optional) backref from articulation; Prompt → Outputs; Insight optional FKs to Output, Prompt, Assumption.
   - Keep `FactDBModel` and current `IntentDBModel` columns for this phase (so both old and new schema exist; we can add new tables only).

2. **Domain models (`models.py`)**
   - Add: `Aspect`, `Input`, `Choice`, `Pitfall`, `Assumption`, `Quality`, `Example`, `Prompt`, `Output`, `Insight` with attributes per INTENTS_DOMAIN_V2.md (integer ids).
   - Extend `Intent`: add lists for aspects, inputs, choices, pitfalls, assumptions, qualities, examples, insights, prompts (and optionally aggregate outputs via prompts). Keep `output_format`, `output_structure`, `context`, `constraints`, `facts` for now so existing code and tests do not break.
   - Add validation in each new domain model (non-empty required strings, enum values where applicable).

3. **Alembic / migrations**
   - If using Alembic: one migration that creates all new tables and FKs. Old tables can be discarded in Phase 4 (no data migration).

**Exit criterion:** New tables and domain models exist; existing intent/fact code and tests still pass; new entities are not yet exposed via API.

---

### Phase 2 — Repository and service for new entities

**Goal:** CRUD for Aspect and all articulation entities (Input, Choice, Pitfall, Assumption, Quality, Example), plus Prompt, Output, Insight. No removal of Fact yet.

1. **Repository (`repository.py`)**
   - For each new entity: create, find_by_id, update, delete (and list by intent_id where applicable). For articulation entities: ensure intent_id (and optional aspect_id) are enforced.
   - Prompt: create, find_by_id, list_by_intent_id, get next version number for an intent.
   - Output: create, find_by_id, list_by_prompt_id.
   - Insight: create, find_by_id, list_by_intent_id, update (e.g. status).
   - Load relationships as needed (e.g. intent with aspects + articulation entities for a “full” intent read). Prefer explicit selectinload/joinedload to avoid N+1.
   - Keep all existing Fact and Intent methods; extend `_to_intent_domain_model` to optionally load new relationships when needed (or add `find_by_id_full` that loads everything).

2. **Service (`service.py`)**
   - Add service functions for: create/read/update/delete for Aspect and each articulation entity (Input, Choice, Pitfall, Assumption, Quality, Example); create/read/list for Prompt and Output; create/read/update/list for Insight. All must validate intent existence and publish domain events where appropriate.
   - Keep existing intent and fact service functions unchanged for this phase.

3. **Domain events (`events.py`)**
   - Add events for: Aspect (created/updated/deleted), Input, Choice, Pitfall, Assumption, Quality, Example (created/updated/deleted), Prompt (created), Output (created), Insight (created/updated). Use naming consistent with existing (e.g. `AspectAddedEvent`).

**Exit criterion:** New entities are creatable/readable/updatable/deletable via service layer; existing intent/fact flows still work; unit and integration tests for new repository and service pass.

---

### Phase 3 — API (schemas and router)

**Goal:** Expose V2 entities via HTTP; keep V1 intent/fact endpoints working during transition.

1. **Schemas (`schemas.py`)**
   - Add request/response DTOs for: Aspect, Input, Choice, Pitfall, Assumption, Quality, Example, Prompt, Output, Insight (create/update/response per entity). Use enums for confidence, priority, source, source_type, status.
   - Add nested representations where useful (e.g. IntentResponse with optional lists of aspects, inputs, … or separate endpoints that return lists by intent_id).
   - Keep existing Intent and Fact schemas for now.

2. **Router (`router.py`)**
   - **Aspects:** `POST /intents/{intent_id}/aspects`, `GET /intents/{intent_id}/aspects`, `GET /intents/{intent_id}/aspects/{aspect_id}`, `PATCH`, `DELETE`.
   - **Articulation (per type):** e.g. `POST /intents/{intent_id}/inputs`, `GET /intents/{intent_id}/inputs`, `GET /intents/{intent_id}/inputs/{input_id}`, `PATCH`, `DELETE` — same pattern for choices, pitfalls, assumptions, qualities, examples.
   - **Prompts:** `POST /intents/{intent_id}/prompts` (generate/create), `GET /intents/{intent_id}/prompts`, `GET /intents/{intent_id}/prompts/{prompt_id}`.
   - **Outputs:** `POST /intents/{intent_id}/prompts/{prompt_id}/outputs`, `GET /intents/{intent_id}/prompts/{prompt_id}/outputs`, `GET .../outputs/{output_id}`.
   - **Insights:** `POST /intents/{intent_id}/insights`, `GET /intents/{intent_id}/insights`, `GET .../insights/{insight_id}`, `PATCH` (e.g. status).
   - All must return 404 when intent (or parent resource) does not exist.

**Exit criterion:** All new resources are accessible via API; OpenAPI reflects new endpoints; API tests for new routes pass.

---

### Phase 4 — V1 removal and Intent simplification

**Goal:** Remove Fact and deprecated Intent fields; intent becomes V2-only.

1. **Database**
   - Drop `facts` table (or leave to migration).
   - Remove from `IntentDBModel`: `output_format`, `output_structure`, `context`, `constraints`. Migration: drop columns.

2. **Domain models**
   - Remove `Fact`; remove `output_format`, `output_structure`, `context`, `constraints`, `facts` from `Intent`. Intent only has: id, name, description, created_at, updated_at, and lists of Aspect, Input, Choice, Pitfall, Assumption, Quality, Example, Insight, Prompt.

3. **Repository**
   - Remove all Fact-related methods and `FactDBModel` usage. Update `_to_intent_domain_model` / `_to_intent_db_model` to use only V2 fields and new relationships.

4. **Service**
   - Remove fact-related functions. Update `create_intent` and intent update functions to use only name/description. Remove `IntentCreatedEvent.output_format` (and similar) from events.

5. **Schemas**
   - Remove Fact request/response and all Intent update schemas for output_format, output_structure, context, constraints. Intent create/response only: name, description, and nested or linked IDs for new entities.

6. **Router**
   - Remove all fact endpoints. Remove PATCH for output-format, output-structure, context, constraints. Adjust create/update intent to new shape.

7. **Events**
   - Remove FactAddedEvent, FactUpdatedEvent, FactRemovedEvent. Adjust IntentCreatedEvent/IntentUpdatedEvent payloads (no output_format).

8. **MCP server (`mcp_server.py`, `mcp_http.py`)**
   - **Yes — MCP must be updated.** Remove all fact-related tools (e.g. add fact, update fact value, remove fact). Replace or add tools so MCP reflects the V2 API: create/get/update intent (name, description only), and tools for aspects and articulation entities (inputs, choices, pitfalls, assumptions, qualities, examples), prompts, outputs, insights. Tool parameters and responses should use V2 schemas. List_tools and handlers must call the new service layer APIs; remove any references to Fact or deprecated intent fields. Run `tests/mcp/test_intents_mcp_server.py` and update tests to V2 (no facts, no output_format in intents).

9. **Tests and fixtures**
   - Update all tests and fixtures: remove Fact, use new entities; update intent fixtures to drop deprecated fields.

**Exit criterion:** No references to Fact or deprecated Intent fields; all tests pass; CI green.

---

### Phase 5 — Prompt generation and sharpening (optional / later)

**Goal:** Implement the “sharpening” flow and prompt generation described in INTENTS_DOMAIN_V2.md (Steps 2–4). This is not required for the schema/CRUD refactor but completes the product vision.

- Step 2: Identify aspects (template or LLM) and create Aspect records.
- Step 3: For each aspect, extract Input/Choice/Pitfall/Assumption/Quality/Example (e.g. via LLM) and create articulation entities; create Insights during the process.
- Step 4: Generate prompt content from intent + aspects + articulation entities and create Prompt (with version increment).

This phase may involve new ports (e.g. LLM client) and orchestration in the service layer; document as a separate plan or backlog.

---

## 3. File-by-file checklist

| File | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|---------|
| `db_models.py` | New tables, keep Fact & old Intent cols | — | — | Drop Fact, drop Intent cols |
| `models.py` | Add new domain models, Intent new lists, keep old fields | — | — | Remove Fact, simplify Intent |
| `repository.py` | — | New entity repos, extend intent load | — | Remove Fact, intent V2-only |
| `service.py` | — | New entity services | — | Remove fact services, simplify intent |
| `events.py` | — | New entity events | — | Remove Fact events, simplify Intent events |
| `schemas.py` | — | — | New DTOs | Remove Fact & deprecated Intent schemas |
| `router.py` | — | — | New routes | Remove fact routes, deprecated PATCHes |
| `mcp_http.py` / `mcp_server.py` | — | — | — | **MCP server:** remove fact tools, add/update tools for V2 (intent name/description, aspects, articulation, prompts, outputs, insights) |
| `tests/fixtures/intents.py` | Optional new fixtures | — | — | V2 fixtures only, no Fact |
| `tests/unit/intents/*` | — | New repo/service tests | — | Update/remove fact tests, add V2 tests |
| `tests/api/test_intents_api.py` | — | — | New endpoint tests | Remove fact tests, update intent tests |
| `tests/integration/intents/*` | — | New integration tests | — | V2-only |
| `tests/mcp/test_intents_mcp_server.py` | — | — | — | V2 MCP tests (no facts, V2 intent shape) |
| Alembic migrations | New migration (new tables only) | — | — | Migration to drop Fact & Intent cols (old tables discarded) |

---

## 4. Testing strategy

- **Phase 1:** Existing tests unchanged; optional unit tests for new domain models (validation, enums).
- **Phase 2:** Unit tests for new repository and service (each entity); integration tests that create intent → add aspects/inputs/… → read back. Keep existing intent/fact tests.
- **Phase 3:** API tests for each new endpoint (create, get, list, update, delete where applicable); OpenAPI snapshot or smoke if used.
- **Phase 4:** Remove or rewrite fact-related tests; update all intent tests to V2 (no output_format/facts); full regression. MCP tests updated to V2.

---

## 5. Order of implementation within each phase

**Phase 1 (suggested):**  
DB models (all new tables) → domain models (Intent extension + new entities) → migration if applicable.

**Phase 2:**  
Repository (Aspect first, then each articulation entity, then Prompt/Output/Insight) → service (same order) → events. Add repository tests then service tests as you go.

**Phase 3:**  
Schemas for all new entities → router (aspects, articulation, prompts/outputs/insights) → API tests.

**Phase 4:**  
DB/migration and db_models → models → repository → service → events → schemas → router → **MCP server** (mcp_server.py, mcp_http.py) → fixtures and all tests. Run full test suite and CI after each layer.

---

## 6. Risks and mitigations

- **Breaking API:** Phases 1–3 keep V1 endpoints; Phase 4 is breaking. Document versioning or deprecation window if clients exist.
- **Data:** Old tables (facts, deprecated intent columns) are discarded; no data migration. Deploy with empty or recreated DB, or run migrations that drop old structures.
- **Scope creep:** Phase 5 (sharpening + prompt generation) is intentionally out of scope for this refactor; implement CRUD and API first, then add behavior.

---

## 7. Definition of done (V2 refactor complete)

- [ ] Intent has only id, name, description, created_at, updated_at.
- [ ] Fact and all fact endpoints/events removed.
- [ ] Aspect and all six articulation entities (Input, Choice, Pitfall, Assumption, Quality, Example) implemented end-to-end (DB, domain, repo, service, API, events).
- [ ] Prompt and Output implemented; Insight implemented with source_type and optional source FKs.
- [ ] **MCP server updated:** fact tools removed; tools for V2 intent and new entities (aspects, articulation, prompts, outputs, insights); tests/mcp/test_intents_mcp_server.py passing.
- [ ] All tests updated and passing; CI green.
- [ ] INTENTS_DOMAIN_V2.md remains the single source of truth for the domain; this plan archived or updated for any follow-up work (e.g. Phase 5).
