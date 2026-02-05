---
name: models-as-source-of-truth
description: Pydantic models are the single source of truth; APIs, MCP tools, OpenAPI, and clients must follow their definitions and documented semantics. Use when defining/changing models, endpoints, or MCP tools.
---

# Pydantic Models as Source of Truth

## When to use

Apply this skill when: defining or changing Pydantic models (schemas); adding or changing API endpoints or request/response shapes; implementing or updating MCP tools; generating client types or OpenAPI; or when the user asks about model documentation or API/MCP consistency.

**Ground truth:** Model names, types, validation, and documented semantics. All consumers (HTTP API, MCP tools, OpenAPI, clients, docs) must be consistent with and directed by these models.

## Documenting models

- **Model:** Docstring with role and usage (e.g. request vs response).
- **Every field:** `Field(..., description="...")` with semantics and constraints (not just type). Descriptions are normative—changing them is a semantic change.

## Downstream consistency

- **APIs/OpenAPI:** Same field names, types, validation; descriptions from model `Field`s. Change model first, then route/OpenAPI.
- **MCP tools:** Parameters and results align with same models; tool descriptions use same semantic language.
- **Clients/docs:** Types and user-facing docs must not contradict model descriptions.

## Workflow

1. Define or change semantics in the Pydantic model first.
2. Propagate to router, MCP, OpenAPI, generated types.
3. Never add fields or semantics only in API/MCP without updating the model.

## Checklist

- [ ] Model docstring; every field has `Field(..., description=...)`.
- [ ] HTTP schemas and MCP tools match models.
- [ ] OpenAPI/client types updated when model semantics change.
