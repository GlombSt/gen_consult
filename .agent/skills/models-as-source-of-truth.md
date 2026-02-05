---
name: models-as-source-of-truth
description: Ensures Pydantic schemas and API/MCP docs follow the project's source-of-truth chain (DOMAIN.md → schemas.py → OpenAPI/MCP). Use when defining or changing schemas, endpoints, or MCP tools.
---

# Pydantic Models and Schema Documentation

**Full rules:** `intentions/ARCHITECTURE_STANDARDS.md` (Schema Documentation Requirements, Single Source of Truth for Documentation). This skill is a short trigger and checklist; follow the standards for details.

## When to use

Apply when: defining or changing Pydantic schemas (`schemas.py`); adding or changing API endpoints or request/response shapes; implementing or updating MCP tools; or when the user asks about model documentation or API/MCP consistency.

## Source-of-truth chain (no conflict)

1. **`*_DOMAIN.md`** — Source of truth for field meanings and descriptions. Update first when semantics change.
2. **`schemas.py`** — Field descriptions must match `*_DOMAIN.md`. Single source for API and MCP: OpenAPI and MCP tool parameter docs derive from Pydantic `Field` descriptions.
3. **`service.py`** — Single source for operation descriptions (docstrings → MCP tool descriptions, API endpoint descriptions).

Never add semantics only in API or MCP without updating the domain doc and/or schemas.

## Workflow

1. Change semantics in `*_DOMAIN.md` if needed.
2. Update `schemas.py` so `Field(..., description=...)` matches; update `service.py` docstrings for operations.
3. OpenAPI and MCP derive from schemas/service; ensure no hand-written docs contradict them.

## Checklist

- [ ] Schema field descriptions match `*_DOMAIN.md`; no generic placeholders.
- [ ] Model docstring and every field has `Field(..., description=...)`.
- [ ] HTTP/MCP and client types aligned with schemas; docs updated if semantics changed.
