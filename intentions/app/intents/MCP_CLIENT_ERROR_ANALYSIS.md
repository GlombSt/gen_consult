# MCP Client Error Analysis (from logs)

Analysis of errors seen when a client (e.g. OpenAI MCP) called the intents MCP server.

---

## Error 1: Partial articulation update (aspects only) — RESOLVED

**Log lines:** 823–824, 830–831 (and similar)

**Message (historical):**
```text
When aspects is supplied, inputs, choices, pitfalls, assumptions, and qualities must also be supplied (full articulation replace). Otherwise aspect_id on existing entities would be nulled when aspects are deleted.
```

**Root cause (corrected):** The Intent is the owner of articulation entities (Input, Choice, Pitfall, Assumption, Quality). The Aspect is not the owner; `aspect_id` on those entities is optional (“discovered for” an aspect). The server had incorrectly required a full replace when `aspects` was supplied, treating “aspect_id nulled when aspect is deleted” as data loss. Nulling `aspect_id` is correct: the entity remains; only the optional link is cleared (DB: ON DELETE SET NULL).

**Resolution:** The rule was removed. Clients may supply any subset of articulation fields (e.g. only `aspects`, or only `qualities`). When aspects are replaced, entities that referenced a removed aspect get `aspect_id` set to NULL; no full replace is required.

---

## Error 2: Quality schema mismatch (name/description vs criterion)

**Log lines:** 848–851

**Message:**
```text
qualities.0.criterion — Field required [type=missing, input_value={'name': 'Readability', 'description': '...'}, ...]
```
(Same for qualities 1–4.)

**Root cause:** The domain model defines **Quality** with a required `criterion` field (and optional `measurement`, `priority`, `aspect_id`). It does **not** have `name` or `description`. The client sent qualities shaped like other entities (e.g. Aspect, Input), using `name` and `description`, so Pydantic correctly reported missing `criterion`.

**Options:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Document only** | In the MCP tool description for `update_intent_articulation` (and any create that accepts qualities), state explicitly that each quality must have a `criterion` (string), and optionally `measurement`, `priority`, `aspect_id` — and that `name`/`description` are not used for Quality. | No schema change; single source of truth (criterion). | Clients may keep sending name/description until docs are used. |
| **B. Accept name/description and map** | In the API/schema layer, accept optional `name` and/or `description` for Quality and map to `criterion` (e.g. use `name` or `description` as criterion if `criterion` is missing). | Tolerates current client payloads. | Diverges from domain model; two ways to set the same thing; possible ambiguity. |
| **C. Better validation error** | Keep schema as-is but return a 400 (or MCP error) with a message like: “Quality uses 'criterion', not 'name'/'description'. Provide a single 'criterion' string (and optionally measurement, priority, aspect_id).” | Clear feedback; no schema drift. | Client must change payload. |

**Recommendation:** A + C: document the Quality shape in the MCP tool description and add a short, explicit validation message when qualities are sent with name/description but without criterion.

---

## Summary

| Error | Root cause | Status |
|-------|------------|--------|
| Partial articulation (aspects only) | Misunderstanding: Aspect was treated as owner; server required full replace when aspects supplied. | **Resolved:** Intent is owner; aspect_id optional. Partial updates (e.g. only aspects) allowed. |
| Quality validation | Client sent `name`/`description`; schema expects `criterion`. | Document Quality as `criterion` (+ optional fields) and improve error message (Options A + C for Error 2). |
