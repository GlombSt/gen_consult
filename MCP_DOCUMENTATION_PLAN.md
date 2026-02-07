# MCP Server Documentation - Gap Analysis & Plan

> **Status**: Draft for review
> **Created**: 2026-02-07
> **Purpose**: Analyze current MCP server documentation and plan improvements

---

## Executive Summary

This document analyzes the SharpIntent MCP server against:
1. MCP specification (all protocol features)
2. INTENTS_DOMAIN_V2.md (domain model alignment)
3. business_plan.md (business value alignment)
4. Best practices from top MCP servers

**Key Finding**: The MCP server has a solid technical foundation but doesn't expose the intelligence layer (quality assessment, guidance, optimization) that differentiates SharpIntent.

---

## 1. MCP Server Documentation Quality

### Strengths
- ✅ Well-documented in README.md with clear setup instructions
- ✅ HTTP transport configuration for Claude Desktop is clear
- ✅ Security considerations are explicitly documented
- ✅ Architecture follows hexagonal principles correctly

### Gaps
- ❌ **No standalone MCP Server documentation file** - Embedded in general README
- ❌ **Missing tool descriptions in client-friendly format** - No example tool calls/responses
- ❌ **No MCP capability summary** - Missing "What can you do?" section for clients
- ❌ **No workflow guidance** - Clients don't know the recommended usage patterns

---

## 2. Alignment with Domain Model (INTENTS_DOMAIN_V2.md)

### Strong Alignment
- ✅ Intent as composition (aspects + articulation entities) correctly implemented
- ✅ Examples intentionally omitted from MCP surface (as documented)
- ✅ Full entity relationships preserved
- ✅ Execution & learning cycle (Prompt → Output → Insight) exposed

### Gaps
- ❌ **Aspect discovery guidance missing** - Domain doc describes aspects as "knowledge extraction scaffolds" but MCP doesn't help identify them
- ❌ **No sharpening flow documentation** - The 7-step sharpening flow isn't translated to MCP client guidance
- ❌ **Quality grading not exposed** - Business plan mentions "quality assessment" but no MCP tool for this
- ❌ **No prompt generation tool** - Domain describes "automatic prompt derivation" but clients must use `add_prompt` manually

---

## 3. Alignment with Business Plan (business_plan.md)

### Business Value Proposition
> "SharpIntent supports structured task clarification before using Generative AI. Users are guided to make relevant parameters explicit, receive hints on missing information, and get risk assessment."

### Critical Gaps Between Business Vision and MCP Server

| Business Capability | MCP Server Status | Gap Severity |
|---------------------|-------------------|--------------|
| Structured task clarification | ✅ Exposed via `create_intent` + `update_intent_articulation` | Minor: No guided workflow |
| User guidance (hints on missing info) | ❌ Not exposed | **CRITICAL** |
| Quality/completeness metrics | ❌ Not exposed | **CRITICAL** |
| Risk assessment (when AI unsuitable) | ❌ Not exposed | **CRITICAL** |
| Prompt optimization | ❌ Not exposed (manual `add_prompt` only) | **CRITICAL** |
| Success estimation | ❌ Not exposed | **CRITICAL** |

**Observation**: MCP server currently exposes **data management** (CRUD) but not the **intelligence layer** that makes SharpIntent valuable.

---

## 4. MCP Protocol Feature Analysis

Based on MCP Specification 2025-11-25:

### Currently Implemented

**✅ Tools (9 tools)**
- Intent CRUD: create, get, list, delete
- Intent updates: name, description, articulation
- Execution: add_prompt, add_output, add_insight

### Not Implemented

**❌ Resources** (Read-only data access)
- MCP supports exposing data as readable resources (like documents)
- Could expose: intents list, individual intents, domain model reference
- Would enable AI to reference intents as context without tool calls

**❌ Prompts** (Workflow templates)
- MCP supports pre-defined prompt templates with variables
- Could expose: guided sharpening workflow, quality review, insight extraction
- Would make workflows discoverable and reusable

**❌ Enhanced Tool Metadata**
- Output schemas (show return structure)
- Icons (visual recognition in clients)
- Business-value descriptions (vs technical descriptions)

---

## 5. Benchmarking Against Best Practices

Analyzed official Anthropic MCP servers and industry leaders:

### Best-in-Class Examples

**Filesystem Server**:
- 15 tools clearly categorized (Read-Only vs Write)
- One-line descriptions per tool
- Multiple config examples (NPX, Docker, VS Code)
- Explicit security considerations

**Sequential Thinking Server**:
- Clear problem/solution framing
- Detailed parameter documentation
- "Ideal Use Cases" section
- Configuration options documented

**Memory Server**:
- Domain model explanation upfront
- 9 well-named tools organized by operation type
- Clear separation of concerns

### What Makes Documentation Excellent

From analysis of top servers:
1. **Clear navigation structure**
2. **Multiple installation methods** (NPX, Docker, VS Code)
3. **Use-case-driven organization** ("What can I do?" not "What functions exist?")
4. **Natural language examples** (suggested queries)
5. **Security warnings** prominently displayed
6. **Troubleshooting/FAQ** section

---

## 6. Proposed Improvements (For Discussion)

### Option A: Documentation Only (Conservative)

**Scope**: Improve documentation without code changes

**Standards**: Follow `MCP_DOCUMENTATION_STANDARDS.md` - derive from single sources of truth

**Changes**:
1. Create `MCP_CLIENT_GUIDE.md` with:
   - "What is SharpIntent MCP Server?"
   - "Why use this?" (problem/solution)
   - Tool reference with examples (derived from `schemas.py` and `service.py`)
   - Common workflows (references `INTENTS_DOMAIN_V2.md`)
   - Configuration for multiple clients (Claude Desktop, VS Code, etc.)
   - Troubleshooting guide

2. Update README.md:
   - Link to client guide
   - Simplify MCP section to quick start

**Key Principle**: No duplication - reference schemas, service docstrings, and domain model

**Pros**:
- Quick to implement (documentation only)
- No code changes required
- Improves discoverability immediately

**Cons**:
- Doesn't close gap with business value proposition
- Misses MCP protocol features (resources, prompts)
- Clients still need to figure out workflows themselves

---

### Option B: Full Protocol Implementation (Comprehensive)

**Scope**: Leverage all MCP protocol features + comprehensive documentation

**Code Changes**:

1. **Add MCP Resources** (5 resources):
   - `sharpintent://intents/active` - List all intents
   - `sharpintent://intent/{id}` - Full intent
   - `sharpintent://intent/{id}/articulation` - Just articulation
   - `sharpintent://intent/{id}/execution-history` - Timeline
   - `sharpintent://domain-model` - Reference docs

2. **Add MCP Prompts** (5 workflow templates):
   - `sharpen_intent_guided` - Step-by-step sharpening
   - `create_intent_from_task` - Task to intent conversion
   - `review_intent_quality` - Quality assessment
   - `extract_insights_from_output` - Learning extraction
   - `export_intent_as_prompt` - Prompt generation

3. **Enhance Tool Metadata**:
   - Add output schemas to all tools
   - Rewrite descriptions in business language
   - Optional: Add icons

4. **Documentation**:
   - Create `MCP_CLIENT_GUIDE.md` (comprehensive)
   - Update README.md with links
   - Add configuration examples for all major clients

**Pros**:
- Leverages full MCP protocol
- Makes workflows discoverable
- Better alignment with business value
- Industry best practices

**Cons**:
- Significant implementation effort (8-12 hours)
- Requires code changes and testing
- May expose features not yet fully developed (quality assessment, prompt generation)

---

### Option C: Hybrid Approach (Recommended?)

**Scope**: Essential documentation + strategic MCP features

**Phase 1 - Documentation (Quick Win)**:
1. Create `MCP_CLIENT_GUIDE.md` with:
   - Clear capability summary
   - Tool reference with examples
   - Common workflows (using existing tools)
   - Configuration examples
   - Troubleshooting

**Phase 2 - MCP Resources (Low Effort, High Value)**:
1. Implement resources (read-only, reuses existing service layer)
2. Enables contextual reference without tool calls

**Phase 3 - Consider Later**:
- MCP Prompts (requires defining workflows explicitly)
- Intelligence layer tools (quality assessment, etc.)

**Pros**:
- Quick initial improvement
- Incremental approach
- Can pause after Phase 1 if sufficient

**Cons**:
- Still doesn't fully close business value gap
- May create expectation for more features

---

## 7. Questions for Decision

### A. Scope
Which option resonates with you?
- [ ] Option A: Documentation only
- [ ] Option B: Full protocol implementation
- [ ] Option C: Hybrid approach
- [ ] Other: _____________

### B. Timeline
What's the urgency?
- [ ] Needed soon (next 1-2 weeks)
- [ ] Medium term (1 month)
- [ ] Low priority (when time permits)

### C. Audience Priority
Who is the primary audience?
- [ ] Internal testing / validation
- [ ] Early adopters / beta users
- [ ] Demonstration / sales purposes
- [ ] Production customers

### D. Business Value Gap
Should the MCP server expose intelligence features?
- [ ] Yes - Quality assessment, prompt generation, etc.
- [ ] No - Keep it as data access layer for now
- [ ] Partial - Some guidance, not full intelligence

### E. Simplification
What can we remove from the plan?
- Anything that feels like it "goes too far"?
- Features that aren't essential?
- Documentation sections that are overkill?

---

## 8. Next Steps

**After your review**:
1. You edit this document with your feedback
2. We discuss and align on scope
3. I create focused implementation plan
4. Execute approved scope

**Please mark up this document with**:
- ✂️ = Remove this
- ⭐ = Prioritize this
- ❓ = Question about this
- ✏️ = Your edits/comments

---

## 9. References for Implementation

### Current Implementation Files

**MCP Server Implementation:**
- `intentions/app/intents/mcp_server.py` - Main MCP server with tool definitions
  - Implements `@server.list_tools()` and `@server.call_tool()`
  - Contains tool schema generation and routing logic
  - Uses service layer as port (hexagonal architecture)

- `intentions/app/intents/mcp_sdk_http.py` - HTTP/SSE transport layer
  - Wraps `StreamableHTTPSessionManager` from MCP Python SDK
  - Handles ASGI/FastAPI integration
  - Implements origin validation and security

- `intentions/app/intents/mcp_http.py` - Legacy HTTP transport (deprecated, for reference)

- `intentions/mcp_server.py` - Stdio transport entry point (deprecated, kept for compatibility)

**Service Layer (The Port):**
- `intentions/app/intents/service.py` - Business logic functions
  - All MCP tools call these service functions
  - Service layer is the single source of truth for operations
  - Read service docstrings for operation descriptions

**Schemas (API Contract):**
- `intentions/app/intents/schemas.py` - Pydantic models for all requests/responses
  - `IntentCreateRequest`, `IntentResponse`, `IntentResponseForMCP`, etc.
  - Single source of truth for parameter documentation
  - Use `model_json_schema()` to generate JSON schemas for MCP tools

**Domain Models:**
- `intentions/app/intents/models.py` - Domain models with business logic
- `intentions/app/intents/db_models.py` - SQLAlchemy ORM models

**Repository (Data Access):**
- `intentions/app/intents/repository.py` - Database operations

**FastAPI Integration:**
- `intentions/app/main.py` - FastAPI app with MCP endpoint at `/mcp`
  - Mounts `mcp_sdk_asgi_app` for MCP protocol handling

### Domain Documentation

**Core Domain Model:**
- `intentions/app/intents/INTENTS_DOMAIN_V2.md` - **CRITICAL REFERENCE**
  - Complete domain model with entity definitions
  - Relationships between Intent, Aspect, and articulation entities
  - The 7-step sharpening flow (lines 214-265)
  - Design principles and rationale
  - Data definitions for all entities (lines 317-462)

**Domain Implementation Plan:**
- `intentions/app/intents/IMPLEMENTATION_PLAN_V2.md` - V2 migration notes

**Business Context:**
- `business/financing/Gründungszuschuss/output/business_plan.md` - Business value proposition
  - Core capabilities (lines 51-68)
  - Problem statement (lines 29-36)
  - User guidance and quality assessment as key features

### Architecture Standards

**Mandatory Reading:**
- `intentions/ARCHITECTURE_STANDARDS.md` - **MUST FOLLOW**
  - Hexagonal architecture rules
  - Layer responsibilities (Router → Service → Repository)
  - Three model types (DB, Domain, DTO)
  - Cross-domain communication via service layer
  - Event publishing requirements

- `intentions/ARCHITECTURE_GUIDE.md` - Detailed examples and patterns
  - Communication patterns
  - Service layer design
  - Domain event usage

**MCP-Specific Standards:**
- `intentions/MCP_DOCUMENTATION_STANDARDS.md` - **MUST FOLLOW for MCP docs**
  - Single source of truth principle
  - Documentation architecture (schemas → service → domain)
  - How to avoid duplication
  - Pydantic models as primary source
  - Service docstrings as operation descriptions
  - Domain model as conceptual reference

**Development Workflow:**
- `intentions/DEVELOPMENT_STANDARDS.md` - TDD workflow, code quality checklist
- `intentions/TESTING_STANDARDS.md` - Coverage requirements (80%+), test patterns

**Related Standards:**
- `intentions/LOGGING_STANDARDS.md` - Structured logging with PII protection
- `intentions/EXCEPTION_HANDLING_STANDARDS.md` - Error handling patterns

### MCP Specification and Examples

**Official MCP Specification:**
- **MCP Spec 2025-11-25**: https://modelcontextprotocol.io/specification/2025-11-25
  - Tools: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
  - Resources: https://modelcontextprotocol.io/specification/2025-11-25/server/resources
  - Prompts: https://modelcontextprotocol.io/specification/2025-11-25/server/prompts

- **TypeScript Schema**: https://github.com/modelcontextprotocol/specification/blob/main/schema/2025-11-25/schema.ts
  - Canonical type definitions for all MCP protocol types

**MCP Python SDK:**
- **GitHub**: https://github.com/modelcontextprotocol/python-sdk
- **PyPI**: `mcp` package
- **Key Imports**:
  ```python
  import mcp.types as types  # Protocol types
  from mcp.server.lowlevel import Server  # Server implementation
  from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
  from mcp.server.transport_security import TransportSecuritySettings
  ```

**Official Reference Servers (Benchmarks):**
- **Filesystem**: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
  - 15 tools, clear categorization, excellent security docs

- **Memory**: https://github.com/modelcontextprotocol/servers/tree/main/src/memory
  - Knowledge graph, domain model explanation upfront

- **Sequential Thinking**: https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking
  - Problem/solution framing, detailed parameter docs, use cases

- **Git**: https://github.com/modelcontextprotocol/servers/tree/main/src/git
  - Read/search/manipulate Git repositories

- **Fetch**: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch
  - Single tool, clear parameter docs, security warnings

**All Official Servers**: https://github.com/modelcontextprotocol/servers

**Documentation Best Practices:**
- Nordic APIs: https://nordicapis.com/5-examples-of-excellent-mcp-server-documentation/
  - Analysis of Figma, GitLab, PandaDoc, SmartBear, Webflow MCP docs
  - What makes excellent documentation

### Testing Infrastructure

**Existing MCP Tests:**
- `intentions/tests/mcp/test_intents_mcp_server.py` - Current MCP server tests
  - Examples of tool call testing
  - Fixtures for MCP client setup

**Test Requirements:**
- 80%+ coverage overall (see `intentions/TESTING_STANDARDS.md`)
- Integration tests for all new MCP features
- Test both success and error cases

**Test Fixtures:**
- Database: In-memory SQLite (automatic in tests)
- MCP Client: Mock or real client for integration tests

### Project Context

**Root Documentation:**
- `CLAUDE.md` - **Project-wide guidance for AI assistants**
  - Multi-project repository structure
  - Hexagonal architecture principles
  - Backend = hexagon, frontend = adapter
  - GitHub CLI usage requirements

- `AGENTS.md` - Readable code conventions for coding agents
  - Simplicity, structure, naming conventions

- `intentions/PYTHON_IDIOM_STANDARDS.md` - Python-specific idioms

**CI/CD:**
- `CI.md` - CI workflow triggers and configuration
- `.github/workflows/` - GitHub Actions workflows

**Current README:**
- `intentions/README.md` - Lines 409-664 contain current MCP server documentation
  - This is what we're improving/replacing

### Key Concepts for Implementation

**Hexagonal Architecture in MCP Context:**
```
MCP Server (mcp_server.py) = PRIMARY ADAPTER
    ↓ calls
Service Layer (service.py) = PORT (public API)
    ↓ uses
Repository (repository.py) = SECONDARY ADAPTER
    ↓ accesses
Database
```

**Three Model Types:**
1. **DB Models** (`db_models.py`) - SQLAlchemy ORM, database schema
2. **Domain Models** (`models.py`) - Business logic, rich behavior
3. **API DTOs** (`schemas.py`) - Request/response, validation, MCP tool schemas

**Critical Design Decisions:**
- Examples are intentionally omitted from MCP surface (see INTENTS_DOMAIN_V2.md line 24)
- Intent is a composition: Intent owns Aspects and articulation entities
- Articulation entities may optionally relate to an Aspect (discovered for)
- Service layer publishes domain events for all business actions

**MCP-Specific Patterns:**
- Tool schemas: Use `_pydantic_to_json_schema()` helper in `mcp_server.py`
- Tool descriptions: Extract from service layer docstrings (single source of truth)
- Error handling: Rollback transaction, log error, re-raise (see lines 364-372 in `mcp_server.py`)

### External Resources

**Model Context Protocol Community:**
- Official docs: https://modelcontextprotocol.io/
- GitHub discussions: https://github.com/modelcontextprotocol/specification/discussions
- Claude Desktop setup: https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop

**MCP Tools and Clients:**
- `mcp-remote` (NPX package): HTTP/SSE proxy for stdio MCP servers
- Claude Desktop: Primary MCP client
- VS Code Cline: MCP-enabled coding assistant
- Continue.dev: MCP-enabled AI assistant

### Implementation Checklist References

When implementing, consult:
1. ✅ `MCP_DOCUMENTATION_STANDARDS.md` - **Follow single source of truth principle**
2. ✅ `ARCHITECTURE_STANDARDS.md` - Ensure hexagonal architecture compliance
3. ✅ `INTENTS_DOMAIN_V2.md` - Understand domain model deeply
4. ✅ `schemas.py` - Use existing schemas, maintain consistency
5. ✅ MCP Spec (tools/resources/prompts) - Follow protocol correctly
6. ✅ Official reference servers - Match quality and patterns
7. ✅ `DEVELOPMENT_STANDARDS.md` - Follow TDD workflow
8. ✅ `TESTING_STANDARDS.md` - Write comprehensive tests

---

## Appendix: MCP Specification Summary

**Protocol Features**:
- **Tools**: Executable functions (we have 9)
- **Resources**: Read-only data with URIs (we have 0)
- **Prompts**: Pre-defined templates (we have 0)
- **Sampling**: Server-initiated LLM calls (advanced, not needed)
- **Roots**: Filesystem boundaries (not applicable)
- **Elicitation**: Runtime context requests (not needed)

**Transport**: HTTP/SSE (✅ implemented via Streamable HTTP)

**Best Practice Docs**:
- Clear problem/solution framing
- Use-case-driven organization
- Multiple client configurations
- Security considerations upfront
- Troubleshooting guide

---

**Document Owner**: @steffen.glomb
**Status**: Awaiting review and direction
