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

**Changes**:
1. Create `MCP_CLIENT_GUIDE.md` with:
   - "What is SharpIntent MCP Server?"
   - "Why use this?" (problem/solution)
   - Tool reference with examples
   - Common workflows
   - Configuration for multiple clients (Claude Desktop, VS Code, etc.)
   - Troubleshooting guide

2. Update README.md:
   - Link to client guide
   - Simplify MCP section to quick start

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
