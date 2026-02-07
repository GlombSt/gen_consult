# MCP Server Documentation Standards

> **Purpose**: Define how to document MCP servers using single sources of truth to maintain consistency and reduce duplication.
>
> **Scope**: General principles applicable to any MCP server implementation.

---

## Core Principle: Single Source of Truth

**Documentation should be derived from code, not duplicated.** Each piece of information has exactly one canonical source.

### Why This Matters

- ✅ **Consistency**: Documentation matches implementation automatically
- ✅ **Maintainability**: Update once, reflected everywhere
- ✅ **Accuracy**: No drift between docs and code
- ✅ **DRY**: Don't Repeat Yourself applies to documentation
- ✅ **Trust**: Generated docs are always current

---

## Documentation Architecture

```
┌─────────────────────────────────────────────────────┐
│           SINGLE SOURCES OF TRUTH                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Pydantic Models (schemas.py)                    │
│     └─> Tool input/output schemas                   │
│     └─> Field descriptions                          │
│     └─> Validation rules                            │
│                                                      │
│  2. Service Layer Docstrings (service.py)           │
│     └─> Operation descriptions                      │
│     └─> Business logic intent                       │
│     └─> Usage guidance                              │
│                                                      │
│  3. Domain Model Documentation (.md)                │
│     └─> Conceptual model                            │
│     └─> Entity relationships                        │
│     └─> Workflows and processes                     │
│                                                      │
│  4. MCP Protocol Types (mcp.types)                  │
│     └─> Standard protocol metadata                  │
│     └─> Tool/Resource/Prompt definitions            │
│                                                      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│          GENERATED DOCUMENTATION                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  • MCP Tool Metadata                                │
│  • API Reference                                    │
│  • Client Guide                                     │
│  • Interactive Docs                                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Single Source of Truth Mapping

### 1. Tool Input/Output Schemas → Pydantic Models

**Source**: `schemas.py` (Pydantic models)

**What It Defines**:
- Parameter names and types
- Required vs optional fields
- Field descriptions
- Validation rules
- Default values
- Examples

**How to Use**:
```python
# schemas.py - SINGLE SOURCE OF TRUTH
from pydantic import BaseModel, Field

class IntentCreateRequest(BaseModel):
    """Request schema for creating a new intent."""

    name: str = Field(
        ...,
        min_length=1,
        description="Short, recognizable label for the intent (e.g., 'Write blog post')"
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Full explanation of what you want to accomplish"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Write blog post",
                    "description": "Create an SEO-optimized blog post about AI"
                }
            ]
        }
    }
```

**Generate MCP Schema**:
```python
# mcp_server.py - DERIVED from schemas.py
def _pydantic_to_json_schema(pydantic_model: type) -> dict:
    """Convert Pydantic model to JSON Schema (MCP format)."""
    return pydantic_model.model_json_schema(mode="serialization")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    # Schema comes from Pydantic model
    create_intent_schema = _pydantic_to_json_schema(IntentCreateRequest)

    return [
        types.Tool(
            name="create_intent",
            description="Create a new intent",  # Can be enhanced, but schema is derived
            inputSchema=create_intent_schema,   # ← Single source of truth
        )
    ]
```

**Documentation Benefits**:
- Parameter docs in API reference come from `Field(description=...)`
- Examples come from `model_config["json_schema_extra"]["examples"]`
- Type information is automatically correct
- Validation rules are documented implicitly

---

### 2. Tool Descriptions → Service Layer Docstrings

**Source**: `service.py` (function docstrings)

**What It Defines**:
- What the operation does (business logic)
- When to use it
- What it returns (conceptually)
- Important notes or warnings

**How to Use**:
```python
# service.py - SINGLE SOURCE OF TRUTH
async def create_intent(
    request: IntentCreateRequest,
    repository: IntentRepository
) -> Intent:
    """
    Create a new intent to begin task clarification.

    An intent captures what you want to accomplish and serves as the foundation
    for systematic articulation. You can optionally include initial aspects and
    articulation entities (inputs, choices, pitfalls, assumptions, qualities).

    This operation publishes an IntentCreated event.

    Args:
        request: Intent creation parameters
        repository: Data access layer

    Returns:
        Created intent with all specified articulation entities

    Raises:
        ValueError: If name or description is empty
    """
    # Implementation...
```

**Use in MCP Server**:
```python
# mcp_server.py - DERIVED from service.py
import inspect

def _get_function_docstring(func) -> str:
    """Extract docstring from a function (single source of truth)."""
    return inspect.getdoc(func) or ""

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    # Description comes from service layer docstring
    create_intent_description = _get_function_docstring(service.create_intent)

    # Can enhance for MCP context, but core logic description is from service
    mcp_description = (
        "Start clarifying a new task by capturing what you want to accomplish. "
        "Optionally add aspects (domains to consider), inputs, choices, pitfalls, "
        "assumptions, and success criteria."
    )

    return [
        types.Tool(
            name="create_intent",
            description=mcp_description,  # Enhanced for MCP, but references service
            inputSchema=create_intent_schema,
        )
    ]
```

**Documentation Benefits**:
- Service layer docstring explains business logic once
- MCP tool description can reference or adapt it
- API docs can reference the same docstring
- No duplication between service and MCP descriptions

---

### 3. Domain Concepts → Domain Model Documentation

**Source**: `DOMAIN_MODEL.md` (markdown documentation)

**What It Defines**:
- Entity definitions and purpose
- Relationships between entities
- Workflows and processes
- Design principles and rationale
- Business rules

**How to Use**:
```markdown
<!-- INTENTS_DOMAIN_V2.md - SINGLE SOURCE OF TRUTH -->

## Intent

**What it is:** The user's goal — what they want to accomplish.
The anchor entity. Everything else relates to Intent to refine and disambiguate it.

**Role in the system:** The thing being sharpened. Holds the core description
and accumulates the articulation work.

**Relationships:**
- Intent has many Aspects (structuring/discovery scope)
- Intent has many articulation entities (Input, Choice, Pitfall, etc.)
- Intent has many Prompts (versioned instructions)
```

**Reference in Client Guide**:
```markdown
<!-- MCP_CLIENT_GUIDE.md - REFERENCES domain model -->

## What is an Intent?

An intent represents what you want to accomplish. See the complete
[domain model documentation](./INTENTS_DOMAIN_V2.md) for entity
definitions and relationships.

**Quick Summary**: Intent is the anchor entity that you sharpen by
adding aspects, inputs, choices, and success criteria.
```

**Expose as MCP Resource**:
```python
# mcp_server.py - EXPOSES domain model as resource
@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "myserver://domain-model":
        # Read from single source of truth
        domain_model_path = Path(__file__).parent / "DOMAIN_MODEL.md"
        return domain_model_path.read_text()
```

**Documentation Benefits**:
- Domain model explained once in detail
- MCP clients can reference it as a resource
- Client guides link to it
- No duplication of entity definitions

---

### 4. Tool Names & Categories → Service Layer Structure

**Source**: `service.py` (function organization)

**What It Defines**:
- Tool names (match service function names)
- Tool grouping (matches service module organization)
- Operation semantics (CRUD, etc.)

**How to Use**:
```python
# service.py - SINGLE SOURCE OF TRUTH for operation names
# Intent Management
async def create_intent(...) -> Intent: ...
async def get_intent(...) -> Intent | None: ...
async def list_intents(...) -> list[Intent]: ...
async def delete_intent(...) -> bool: ...

# Intent Refinement
async def update_intent_name(...) -> Intent | None: ...
async def update_intent_description(...) -> Intent | None: ...
async def update_intent_articulation(...) -> Intent | None: ...

# Execution & Learning
async def add_prompt(...) -> Prompt | None: ...
async def add_output(...) -> Output | None: ...
async def add_insight(...) -> Insight | None: ...
```

**Map to MCP Tools**:
```python
# mcp_server.py - DERIVED from service.py structure
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        # Intent Management (matches service.py grouping)
        types.Tool(name="create_intent", ...),
        types.Tool(name="get_intent", ...),
        types.Tool(name="list_intents", ...),
        types.Tool(name="delete_intent", ...),

        # Intent Refinement (matches service.py grouping)
        types.Tool(name="update_intent_name", ...),
        types.Tool(name="update_intent_description", ...),
        types.Tool(name="update_intent_articulation", ...),

        # Execution & Learning (matches service.py grouping)
        types.Tool(name="add_prompt", ...),
        types.Tool(name="add_output", ...),
        types.Tool(name="add_insight", ...),
    ]
```

**Document in Client Guide**:
```markdown
<!-- MCP_CLIENT_GUIDE.md - REFERENCES service.py structure -->

## Available Tools

### Intent Management
- `create_intent` - Start a new intent
- `get_intent` - Retrieve intent details
- `list_intents` - Browse all intents
- `delete_intent` - Remove an intent

### Intent Refinement
- `update_intent_name` - Change the intent name
- `update_intent_description` - Update what you want to accomplish
- `update_intent_articulation` - Add/update aspects, inputs, choices, etc.

### Execution & Learning
- `add_prompt` - Record a versioned prompt
- `add_output` - Save AI output
- `add_insight` - Capture learnings
```

**Documentation Benefits**:
- Tool names match service functions (1:1 mapping)
- Tool grouping reflects service organization
- Semantic consistency across layers
- Easy to find implementation for a tool

---

## Documentation Layers

### Layer 1: Generated (Automatic)

**Source**: Pydantic models + MCP protocol

**Output**:
- `/docs` endpoint (FastAPI Swagger UI)
- `/openapi.json` endpoint
- MCP `tools/list` response
- Interactive API explorers

**Implementation**:
```python
# Automatic from FastAPI + MCP SDK
app = FastAPI()  # Generates /docs and /openapi.json
server = Server("my-mcp-server")  # Generates MCP metadata
```

**Maintenance**: None - automatically stays current

---

### Layer 2: Client Reference (Semi-Automatic)

**Source**: Service docstrings + domain model + templates

**Output**:
- `MCP_CLIENT_GUIDE.md` (client-facing documentation)
- Tool reference with examples
- Workflow guides
- Configuration examples

**Implementation**:
```markdown
<!-- MCP_CLIENT_GUIDE.md - Uses references to sources of truth -->

## Tool Reference

### create_intent

**Source**: [`service.create_intent()`](./service.py#L123)

**Purpose**: {{ service.create_intent.__doc__ }}  <!-- Reference docstring -->

**Parameters**: See [`IntentCreateRequest`](./schemas.py#L45)  <!-- Reference schema -->

**Example**:
```json
{{ IntentCreateRequest.model_config.json_schema_extra.examples[0] }}  <!-- Reference example -->
```
```

**Maintenance**: Update when adding tools; content comes from sources

---

### Layer 3: Narrative (Manual)

**Source**: Human-written explanations

**Output**:
- "Why use this?" sections
- Use case narratives
- Tutorial walkthroughs
- Best practices
- Architecture diagrams

**Implementation**:
```markdown
<!-- MCP_CLIENT_GUIDE.md - Manual, but references sources -->

## Why Use SharpIntent?

**Problem**: Vague tasks lead to generic AI responses.

**Solution**: SharpIntent helps you articulate tasks systematically
using the [Intent Sharpening Flow](./INTENTS_DOMAIN_V2.md#sharpening-flow).

**Example Workflow**: See [Example 1: Complete Workflow](#example-1)
```

**Maintenance**: Update when UX or value prop changes

---

## Standards Checklist

### ✅ For Every MCP Tool

- [ ] **Schema defined in Pydantic model** (`schemas.py`)
  - Field descriptions use `Field(description=...)`
  - Examples in `model_config["json_schema_extra"]["examples"]`
  - Validation rules explicit

- [ ] **Business logic in service layer** (`service.py`)
  - Function docstring explains what/why
  - Docstring mentions domain events if any
  - Args and return type documented

- [ ] **Tool definition references schema** (`mcp_server.py`)
  - `inputSchema` generated from Pydantic model
  - `outputSchema` generated from Pydantic model (optional but recommended)
  - `description` adapts service docstring for MCP context

- [ ] **Client guide references sources** (`MCP_CLIENT_GUIDE.md`)
  - Links to schema file
  - Links to service function
  - Uses example from schema

### ✅ For Every MCP Resource

- [ ] **Content comes from file or database** (no duplication)
  - Domain model exposed as-is from `.md` file
  - Intent data comes from service layer
  - Timestamps/metadata from models

- [ ] **URI scheme documented** in client guide
  - Pattern explained
  - Examples provided
  - MIME type specified

### ✅ For Every MCP Prompt

- [ ] **Workflow defined in domain docs** first
  - Process documented in domain model
  - Steps clearly enumerated
  - Tools involved specified

- [ ] **Prompt template references domain** workflow
  - Message text explains workflow
  - Cites domain documentation
  - Uses appropriate tools in messages

### ✅ For Client Documentation

- [ ] **References, not duplicates**
  - Links to source files (schemas, service, domain model)
  - Embeds examples from sources
  - Updates when sources change

- [ ] **Explains "why", sources explain "what"**
  - Use cases and narratives are manual
  - Technical details come from code
  - Balance between DRY and readability

---

## Implementation Patterns

### Pattern 1: Schema-Driven Tool Documentation

```python
# Step 1: Define schema with rich metadata (SINGLE SOURCE)
class MyRequest(BaseModel):
    """Request for my operation."""

    field: str = Field(
        ...,
        min_length=1,
        description="Detailed field description with examples: 'foo', 'bar'"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"field": "example value"}]
        }
    }

# Step 2: Generate MCP schema (DERIVED)
@server.list_tools()
async def list_tools():
    schema = _pydantic_to_json_schema(MyRequest)
    return [types.Tool(name="my_tool", inputSchema=schema)]

# Step 3: Document in client guide (REFERENCES)
# MCP_CLIENT_GUIDE.md:
# **Parameters**: See [`MyRequest`](./schemas.py#L123)
```

### Pattern 2: Service-Driven Operation Documentation

```python
# Step 1: Document in service layer (SINGLE SOURCE)
async def my_operation(request: MyRequest, repo: MyRepo) -> MyResult:
    """
    Business logic description here.

    This operation does X, Y, Z. Use it when you need to...
    Publishes MyEvent.
    """
    pass

# Step 2: Reference in MCP tool (DERIVED)
@server.list_tools()
async def list_tools():
    description = inspect.getdoc(service.my_operation)
    # Optionally enhance for MCP context
    return [types.Tool(name="my_tool", description=description)]

# Step 3: Document in client guide (REFERENCES)
# MCP_CLIENT_GUIDE.md:
# **Source**: [`service.my_operation()`](./service.py#L456)
```

### Pattern 3: Domain Model as MCP Resource

```python
# Step 1: Write domain model once (SINGLE SOURCE)
# DOMAIN_MODEL.md - Complete domain documentation

# Step 2: Expose as MCP resource (NO DUPLICATION)
@server.read_resource()
async def read_resource(uri: str):
    if uri == "myserver://domain-model":
        path = Path(__file__).parent / "DOMAIN_MODEL.md"
        return path.read_text()  # Serve directly

# Step 3: Reference in client guide (LINK)
# MCP_CLIENT_GUIDE.md:
# See complete [domain model](./DOMAIN_MODEL.md) or
# access via resource: `myserver://domain-model`
```

---

## Anti-Patterns (Avoid)

### ❌ Anti-Pattern 1: Duplicated Field Descriptions

**Bad**:
```python
# schemas.py
class MyRequest(BaseModel):
    name: str = Field(..., description="The name")

# mcp_server.py
inputSchema = {
    "properties": {
        "name": {"description": "The name of the thing"}  # ← Duplicated!
    }
}
```

**Good**:
```python
# schemas.py - SINGLE SOURCE
class MyRequest(BaseModel):
    name: str = Field(..., description="The name of the thing")

# mcp_server.py - DERIVED
inputSchema = _pydantic_to_json_schema(MyRequest)  # ← Generated!
```

---

### ❌ Anti-Pattern 2: Hardcoded Tool Descriptions

**Bad**:
```python
# mcp_server.py
types.Tool(
    name="my_tool",
    description="This tool does X, Y, Z..."  # ← Hardcoded, will drift
)

# service.py
async def my_operation(...):
    """This operation does X, Y, Z..."""  # ← Duplicated!
```

**Good**:
```python
# service.py - SINGLE SOURCE
async def my_operation(...):
    """This operation does X, Y, Z..."""

# mcp_server.py - DERIVED
description = inspect.getdoc(service.my_operation) or "Fallback description"
types.Tool(name="my_tool", description=description)
```

---

### ❌ Anti-Pattern 3: Duplicated Domain Explanations

**Bad**:
```markdown
<!-- DOMAIN_MODEL.md -->
## Intent
An intent represents what you want to accomplish...

<!-- MCP_CLIENT_GUIDE.md -->
## What is an Intent?
An intent represents what you want to accomplish...  <!-- ← Duplicated! -->
```

**Good**:
```markdown
<!-- DOMAIN_MODEL.md - SINGLE SOURCE -->
## Intent
An intent represents what you want to accomplish...

<!-- MCP_CLIENT_GUIDE.md - REFERENCES -->
## What is an Intent?
See the complete [domain model documentation](./DOMAIN_MODEL.md#intent)
for entity definitions and relationships.

**Quick Summary**: Intent is the anchor entity...  <!-- Brief, then link -->
```

---

### ❌ Anti-Pattern 4: Examples in Multiple Places

**Bad**:
```python
# schemas.py
model_config = {"json_schema_extra": {"examples": [{"name": "Example 1"}]}}

# MCP_CLIENT_GUIDE.md
Example: `{"name": "Example 2"}`  # ← Different example!
```

**Good**:
```python
# schemas.py - SINGLE SOURCE
model_config = {"json_schema_extra": {"examples": [{"name": "Example 1"}]}}

# MCP_CLIENT_GUIDE.md - REFERENCES
Example: See [`MyRequest` examples](./schemas.py#L45)
# Or embed programmatically if using doc generator
```

---

## Maintenance Strategy

### When Schemas Change

1. **Update Pydantic model** (`schemas.py`) - Single source of truth
2. **MCP tool schemas** - Automatically updated (generated)
3. **API docs** - Automatically updated (FastAPI generates)
4. **Client guide** - May need updates if new fields are significant

**Effort**: Minimal (mostly automatic)

---

### When Service Logic Changes

1. **Update service docstring** (`service.py`) - Single source of truth
2. **MCP tool description** - Consider if it needs MCP-specific enhancement
3. **Client guide** - Update workflow examples if logic changes significantly

**Effort**: Low (mainly docstring + optional guide updates)

---

### When Domain Model Changes

1. **Update domain documentation** (`DOMAIN_MODEL.md`) - Single source of truth
2. **MCP resource** - Automatically serves updated file
3. **Client guide** - Review for broken links or outdated references

**Effort**: Low (domain doc + link check)

---

## Tools and Automation

### Recommended Tools

**Schema Validation**:
```bash
# Validate Pydantic models generate valid JSON schemas
pytest tests/test_schemas.py::test_json_schema_generation
```

**Documentation Links**:
```bash
# Check links in markdown are not broken
markdown-link-check *.md
```

**Docstring Coverage**:
```bash
# Ensure all service functions have docstrings
interrogate service.py --fail-under=100
```

**Consistency Checks**:
```python
# Test: MCP tool names match service function names
def test_mcp_tool_names_match_service():
    mcp_tools = get_mcp_tool_names()
    service_functions = get_service_function_names()
    assert mcp_tools == service_functions
```

### Optional: Documentation Generator

```python
# generate_mcp_docs.py - Auto-generate parts of client guide
import inspect
from schemas import IntentCreateRequest
from service import create_intent

def generate_tool_reference():
    """Generate tool reference section from sources of truth."""
    for tool_name, service_func in TOOL_MAPPING.items():
        schema_class = get_schema_for_tool(tool_name)

        print(f"### {tool_name}")
        print(f"**Source**: [`{service_func.__name__}()`](./service.py)")
        print(f"**Purpose**: {inspect.getdoc(service_func)}")
        print(f"**Parameters**: See [`{schema_class.__name__}`](./schemas.py)")
        print(f"**Example**:")
        print(f"```json")
        print(json.dumps(schema_class.model_config["json_schema_extra"]["examples"][0]))
        print(f"```")
```

---

## Compliance Test

Use this checklist to verify single-source-of-truth compliance:

### For Each Tool
- [ ] Input schema generated from Pydantic model (not hardcoded)
- [ ] Output schema generated from Pydantic model (if applicable)
- [ ] Tool description references or derives from service docstring
- [ ] Examples come from Pydantic `model_config` (not duplicated)
- [ ] Field descriptions come from `Field(description=...)` (not hardcoded)

### For Client Documentation
- [ ] Tool descriptions reference service layer (link or citation)
- [ ] Parameter docs reference schema file (link to source)
- [ ] Domain concepts reference domain model (link to doc)
- [ ] Examples use same data as schemas (no drift)
- [ ] Workflow descriptions reference domain documentation

### For Domain Model
- [ ] Exposed as MCP resource (reads from file, not duplicated)
- [ ] Entity definitions are in one place only
- [ ] Relationships documented once
- [ ] Client guide links to it (doesn't duplicate it)

---

## Summary

**Golden Rule**: If you update information in more than one place, it's not a single source of truth.

**Implementation Priority**:
1. **Schemas** - Richest source of truth for API contracts
2. **Service docstrings** - Canonical source for business logic
3. **Domain docs** - Conceptual model explained once
4. **Generated docs** - Automatic from sources
5. **Client guide** - References sources, adds narratives

**Maintenance Benefit**: When you change a schema field description, all documentation updates automatically or with minimal effort.

---

**Version**: 1.0.0
**Last Updated**: 2026-02-07
**Applies To**: All MCP server implementations in this repository
