# Intents Domain Implementation Plan

**Version:** 1.0  
**Date:** January 2025  
**Status:** Planning Phase  
**Following:** TDD (Test-Driven Development) as per DEVELOPMENT_STANDARDS.md

---

## Overview

This document outlines the implementation plan for the Intents domain based on:
- `INTENTS_DOMAIN.md` - Domain model and entities
- `USER_STORIES.MD` - Increment 1 user stories (US-001 to US-012)
- `ARCHITECTURE_STANDARDS.md` - Hexagonal architecture requirements
- `DEVELOPMENT_STANDARDS.md` - TDD requirements

---

## Domain Entities

### Intent Entity
**Properties:**
- `id` (int, optional): Database identifier
- `name` (string): Name of the intent
- `description` (string): Textual description of what is to be accomplished
- `output_format` (string): Technical representation (JSON, XML, CSV, plain text, Markdown, HTML)
- `output_structure` (string, optional): Organization and composition of result content
- `context` (string, optional): Dynamic information to inform prompt generation
- `constraints` (string, optional): Conditions describing how intent must be achieved
- `created_at` (datetime): When the intent was created
- `updated_at` (datetime): When the intent was last updated

**Business Rules:**
- Name cannot be empty
- Description cannot be empty
- Output format cannot be empty
- Timestamps are automatically managed

### Fact Entity
**Properties:**
- `id` (int, optional): Database identifier
- `intent_id` (int): Foreign key to Intent
- `value` (string): The actual fact content or data point
- `created_at` (datetime): When the fact was created
- `updated_at` (datetime): When the fact was last updated

**Business Rules:**
- Value cannot be empty
- Must be associated with an Intent
- Timestamps are automatically managed

**Relationship:**
- Intent has many Facts (one-to-many)
- Fact belongs to one Intent

---

## User Stories Mapping

### Increment 1: Declaration

| US ID | Story | Service Function | API Endpoint |
|-------|-------|------------------|--------------|
| US-001 | Edit intent name | `update_intent_name(intent_id, name)` | `PATCH /intents/{intent_id}/name` |
| US-002 | Edit intent description | `update_intent_description(intent_id, description)` | `PATCH /intents/{intent_id}/description` |
| US-003 | Edit intent output format | `update_intent_output_format(intent_id, output_format)` | `PATCH /intents/{intent_id}/output-format` |
| US-004 | Edit intent output structure | `update_intent_output_structure(intent_id, output_structure)` | `PATCH /intents/{intent_id}/output-structure` |
| US-005 | Edit intent context | `update_intent_context(intent_id, context)` | `PATCH /intents/{intent_id}/context` |
| US-006 | Edit intent constraints | `update_intent_constraints(intent_id, constraints)` | `PATCH /intents/{intent_id}/constraints` |
| US-007 | Edit fact value | `update_fact_value(intent_id, fact_id, value)` | `PATCH /intents/{intent_id}/facts/{fact_id}/value` |
| US-008 | Add fact to intent | `add_fact_to_intent(intent_id, value)` | `POST /intents/{intent_id}/facts` |
| US-009 | Remove fact from intent | `remove_fact_from_intent(intent_id, fact_id)` | `DELETE /intents/{intent_id}/facts/{fact_id}` |
| US-010 | View intent aspects | `get_intent(intent_id)` | `GET /intents/{intent_id}` |
| US-012 | Auto-save | Implicit via update operations | (All update endpoints) |

**Note:** US-010 (viewing outputs/prompts) and US-011 (chat window) are frontend concerns and will be handled in later increments.

---

## Implementation Structure

Following hexagonal architecture:

```
app/intents/
├── __init__.py          # Public API exports
├── models.py             # Domain models (Intent, Fact)
├── db_models.py          # Database models (IntentDBModel, FactDBModel)
├── schemas.py            # API DTOs (request/response schemas)
├── service.py            # Service layer (ports) - business logic
├── repository.py         # Repository layer (secondary adapter)
├── router.py             # HTTP router (primary adapter)
└── events.py             # Domain events
```

---

## Implementation Steps (TDD)

### Phase 1: Domain Models & Tests
1. ✅ Write unit tests for `Intent` domain model
2. ✅ Implement `Intent` domain model
3. ✅ Write unit tests for `Fact` domain model
4. ✅ Implement `Fact` domain model

### Phase 2: Database Models & Repository
5. ✅ Write unit tests for `IntentDBModel` and `FactDBModel`
6. ✅ Implement database models
7. ✅ Write unit tests for `IntentRepository`
8. ✅ Implement repository with Intent-Fact relationship management

### Phase 3: Service Layer (Ports)
9. ✅ Write unit tests for service functions (US-001 to US-009)
10. ✅ Implement service functions with event publishing
11. ✅ Write unit tests for domain events

### Phase 4: API Layer
12. ✅ Write unit tests for API schemas
13. ✅ Implement API schemas/DTOs
14. ✅ Write API tests for all endpoints
15. ✅ Implement HTTP router with all endpoints

### Phase 5: Integration
16. ✅ Export public API in `__init__.py`
17. ✅ Register router in `main.py`
18. ✅ Run full test suite
19. ✅ Verify architecture compliance

---

## API Endpoints Design

### Intent Endpoints

```
GET    /intents                    # List all intents
GET    /intents/{intent_id}        # Get intent with facts
POST   /intents                    # Create new intent
PATCH  /intents/{intent_id}/name   # Update intent name
PATCH  /intents/{intent_id}/description
PATCH  /intents/{intent_id}/output-format
PATCH  /intents/{intent_id}/output-structure
PATCH  /intents/{intent_id}/context
PATCH  /intents/{intent_id}/constraints
DELETE /intents/{intent_id}        # Delete intent
```

### Fact Endpoints

```
POST   /intents/{intent_id}/facts           # Add fact to intent
PATCH  /intents/{intent_id}/facts/{fact_id}/value  # Update fact value
DELETE /intents/{intent_id}/facts/{fact_id}        # Remove fact from intent
```

---

## Domain Events

All business actions must publish domain events:

- `IntentCreatedEvent` - When intent is created
- `IntentUpdatedEvent` - When intent is updated (any field)
- `IntentDeletedEvent` - When intent is deleted
- `FactAddedEvent` - When fact is added to intent
- `FactUpdatedEvent` - When fact value is updated
- `FactRemovedEvent` - When fact is removed from intent

---

## Testing Strategy

### Unit Tests
- **Models:** Business logic, validation rules
- **Service:** Business logic with mocked repository
- **Repository:** Data access with mocked storage

### Integration Tests
- **Service + Repository:** Full data flow
- **Service + Events:** Event publishing verification

### API Tests
- **Full HTTP stack:** End-to-end request/response
- **Error handling:** 404, 400, validation errors
- **Edge cases:** Empty data, missing fields

### Coverage Targets
- Models: 90%+
- Service: 85%+
- Repository: 80%+
- Overall: 80%+

---

## Architecture Compliance Checklist

- [ ] Domain models in `models.py` with business logic
- [ ] Database models in `db_models.py` with audit fields
- [ ] API DTOs in `schemas.py` (no sensitive data)
- [ ] Service layer in `service.py` (ports)
- [ ] Repository layer in `repository.py` (secondary adapter)
- [ ] Router layer in `router.py` (primary adapter)
- [ ] Domain events in `events.py`
- [ ] Events published for all business actions
- [ ] Public API exported in `__init__.py`
- [ ] No cross-domain internal imports
- [ ] Three model types properly separated
- [ ] No business logic in router
- [ ] No HTTP concerns in service

---

## Next Steps

1. Start with Phase 1: Write tests for domain models
2. Implement domain models to pass tests
3. Continue with TDD cycle for each phase
4. Verify all user stories are implemented
5. Ensure all tests pass and coverage targets met

