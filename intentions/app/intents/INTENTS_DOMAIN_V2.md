# Intents Domain Model v2

## Overview

A unified domain model for capturing, sharpening, and executing user intents. Combines implementation needs with the conceptual framework for articulating what needs to be explicit.

---

## Entity Categories

### Core Entity
- **Intent** — the user's goal

### Structuring Entity
- **Aspect** — a domain/area of consideration that guides knowledge extraction (articulation entities may relate to an Aspect but belong to Intent)

### Articulation Entities
What needs to be made explicit for reliable execution:
- **Input** — what user provides/has
- **Choice** — decisions that need to be explicit
- **Pitfall** — failure modes to avoid
- **Assumption** — implicit beliefs that need stating
- **Quality** — success criteria and output format
- **Example** — concrete input→output demonstrations

### Execution & Learning Entities
The generate-execute-learn cycle:
- **Prompt** — generated, versioned instruction
- **Output** — what AI produced
- **Insight** — discoveries that feed back to Intent

---

## Entity Diagram

```
                         ┌─────────────────────────────────────┐
                         │              INTENT                 │
                         │   (the sharpened goal/task)         │
                         └───────────────────┬─────────────────┘
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               │                             │                             │
               ▼                             ▼                             ▼
     ┌───────────────────┐         ┌─────────────────┐           ┌─────────────────┐
     │      ASPECT       │         │  ARTICULATION   │           │   EXECUTION &   │
     │  (structuring)    │         │    ENTITIES     │           │    LEARNING     │
     └─────────┬─────────┘         └────────┬────────┘           └────────┬────────┘
               │                            │                             │
               │ discovered for      ┌──────┴──────┐              ┌───────┴───────┐
               │ (optional)          │             │              │               │
               │                     ▼             ▼              ▼               ▼
               │              ┌─────────┐   ┌──────────┐   ┌───────────┐   ┌────────┐
               └─ ─ ─ ─ ─ ─ ─▶│  INPUT  │   │  CHOICE  │   │  PROMPT   │   │ INSIGHT│
                              └─────────┘   └──────────┘   │(versioned)│   └────────┘
                              ┌─────────┐   ┌──────────┐   └─────┬─────┘        │
                              │ PITFALL │   │ASSUMPTION│         │              │
                              └─────────┘   └──────────┘         ▼              │
                              ┌─────────┐   ┌──────────┐   ┌───────────┐        │
                              │ QUALITY │   │ EXAMPLE  │   │  OUTPUT   │────────┘
                              └─────────┘   └──────────┘   └───────────┘  yields
                                    │                                    insights
                                    │
                    ─ ─ ─ ─ ─ ─ ─ ─ ┘  (dashed = optional association with Aspect)
```

---

## Entities

### Intent
**What it is:** The user's goal — what they want to accomplish,. The anchor entity. Everything else relates to Intent in order to refine, sharpen and disambiguate it.

**Role in the system:** The thing being sharpened. Holds the core description and accumulates the articulation work.

---

### Aspect
A domain or area of consideration relevant to the intent — a bounded scope for knowledge extraction.

**Role in the system:** 
- **Knowledge extraction scaffold:** Tells the LLM "explore this domain for insights" during sharpening
- **Completeness check:** Ensures all relevant areas are covered ("Have we addressed the SEO aspect?")
- **Discovery context:** Articulation entities (Input, Choice, etc.) may be discovered *for* an Aspect, creating an optional association
- **Prompt domain guidance:** Becomes the "Domain-Specific Guidance" section in the generated prompt

**Where Aspects come from:** Task templates (known task types), LLM inference (from task description), user addition (domain-specific).

**Example:** For "Create SEO content brief":
- Aspect: "Audience & Positioning" → assumptions about readers, tone choices discovered here
- Aspect: "SEO Constraints" → keyword inputs, density choices, stuffing pitfalls discovered here
- Aspect: "Content Structure" → quality criteria for length, sections discovered here

Without aspects, the LLM might surface insights randomly or miss entire areas. Aspects provide systematic coverage of the knowledge space.

---

### Input
What the user provides — data, documents, materials, context to be operated on. 
Makes explicit what the executor receives: format, quality requirements, how to obtain good input. 
Without this, executors work with inadequate material (garbage in, garbage out).

---

### Choice
A decision with multiple valid approaches and different trade-offs. Captures options, trade-offs, and the selected approach. 
Ambiguous choices lead to inconsistent results; explicit choices ensure the executor follows the intended path.

---

### Pitfall
Where things typically go wrong — failure modes, common mistakes, anti-patterns. 
"What not to do" guidance, often higher-leverage than "do" instructions. Experts know what fails; novices and LLMs don't.

---

### Assumption
Implicit beliefs that need stating — context obvious to the user but not automatically transferred. 
Includes domain knowledge, situational context, beliefs that could invalidate the approach. 
Unstated assumptions are a primary source of "that's not what I meant."

---

### Quality
How to know the result is good — success criteria, output format, structure, standards.
"I'll know it when I see it" doesn't scale; explicit criteria enable consistent results and objective evaluation.

---

### Example
Concrete input→output demonstration showing the transformation in practice. Provides few-shot learning material — examples often communicate intent more effectively than abstract descriptions.

**Structure:** `input_sample` (realistic specimen) + `output_sample` (desired result) + `explanation` (optional: what it demonstrates)

**Sources:** User-provided (past work), LLM-generated (during sharpening, user-validated), extracted from successful Outputs.

---

### Prompt
Generated instruction for the AI — produced from the sharpened intent, not authored directly. 
Versioned, readonly. A translation into executable form.

---

### Output
What was produced — the AI's response to a prompt. 
Readonly after creation, linked to its prompt. Enables comparison, evaluation, and learning.

---

### Insight
Discoveries surfacing during sharpening or from execution — things the user hadn't considered. Belongs directly to Intent but may reference a source entity.

**Sources (what triggered the insight):**
- **Sharpening** — LLM surfaces questions, gaps during articulation ("Have you considered X?")
- **Output** — discoveries from execution results ("This failed because Z")
- **Prompt** — learnings about the prompt itself ("This instruction was ambiguous")
- **Assumption** — challenged or invalidated beliefs ("We assumed X but Y happened")

The engine of improvement: helps articulate what users didn't know they needed to say, captures learnings for future iterations.

---

## Relationships

```
Intent
├── has many → Aspect (structuring)
├── has many → Input ─────────────┐
├── has many → Choice            │
├── has many → Pitfall           ├── may relate to → Aspect (optional)
├── has many → Assumption ───────┤
├── has many → Quality           │
├── has many → Example ──────────┘
├── has many → Insight ←─────────────────────────┐
│             └── may reference source:          │
│                 • Output (execution result)    │
│                 • Prompt (instruction issue)   │
│                 • Assumption (invalidated)     │
├── has many → Prompt (versioned)                │
│             └── produces many → Output ────────┘
└── receives feedback from ← Insight
```

**Core relationships:**
- Intent has many Aspects (structuring/discovery scope)
- Intent has many articulation entities directly (Input, Choice, Pitfall, Assumption, Quality, Example)
- Articulation entities may relate to an Aspect (optional — discovered *for* an aspect, but belong to Intent)
- Intent has many Insights (from sharpening, Output, Prompt, or Assumption)
- Insight may reference its source entity (Output, Prompt, Assumption)
- Intent has many Prompts (each is a version)
- Prompt produces many Outputs
- Insight feeds back to Intent (closing the loop)

**Aspect role in extraction:**
- LLM uses Aspects to systematically probe for articulation entities
- Articulation entities discovered during Aspect exploration get associated with that Aspect
- Aspects ensure completeness: "Have we covered all relevant areas?"
- Association is optional: simple intents may have articulation without aspects

**Insight sources:**
- Sharpening phase → Insight (LLM surfaces considerations during articulation)
- Output → Insight (discoveries from execution results)
- Prompt → Insight (learnings about instruction clarity/effectiveness)
- Assumption → Insight (challenged or invalidated beliefs)

**Example sources:**
- User-provided (from past work)
- LLM-generated (during sharpening, validated by user)
- Output → Example (successful outputs can become future examples)

---

## The Sharpening Flow

```
1. USER STATES GOAL
   └── Creates Intent with basic description

2. SYSTEM IDENTIFIES ASPECTS
   └── LLM infers relevant domains/areas to explore:
       • "For SEO content, we should consider: Audience, SEO Constraints, 
         Content Structure, Brand Voice..."
       └── Creates Aspects (can be from templates, LLM inference, or user)

3. SERVICE EXTRACTS KNOWLEDGE (iterative, guided by Aspects)
   └── For each Aspect, LLM probes systematically:
       • What inputs are needed? → Input (belongs to Intent, discovered for Aspect)
       • What decisions must be made? → Choice (belongs to Intent, discovered for Aspect)
       • What typically goes wrong? → Pitfall (belongs to Intent, discovered for Aspect)
       • What's assumed but not stated? → Assumption (belongs to Intent, discovered for Aspect)
       • How will we know it's done well? → Quality (belongs to Intent, discovered for Aspect)
       • Can you show me an example? → Example (belongs to Intent, discovered for Aspect)
       
   └── LLM generates Insights during conversation:
       • "Have you considered X?"
       • "What happens if Y?"
       • "This might conflict with Z"
       └── Creates Insight → incorporated into articulation

4. SYSTEM GENERATES PROMPT
   └── Translates sharpened intent into executable instruction:
       • Task Overview ← from Intent
       • Domain-Specific Guidance ← from Aspects (grouping associated articulation entities)
       • Key Requirements ← from Choices (all, optionally organized by Aspect)
       • Input Format ← from Inputs (all, optionally organized by Aspect)
       • Common Pitfalls ← from Pitfalls (all, optionally organized by Aspect)
       • Output Format ← from Quality (all, optionally organized by Aspect)
       • Examples ← from Examples (few-shot demonstrations)
       └── Creates Prompt (versioned)

5. AI PRODUCES OUTPUT
   └── Executes prompt, produces result
       └── Creates Output

6. USER/SYSTEM DISCOVERS INSIGHTS
   └── From Output: "This worked" / "This failed" / "Output missed X"
   └── From Prompt: "This instruction was unclear" / "Phrasing caused confusion"
   └── From Assumption: "We assumed X but Y happened"
       └── Creates Insight (referencing source) → feeds back to Intent

7. INTENT IMPROVES
   └── Incorporates insights, sharpens further, generates better prompt
       └── Cycle repeats
```

**Aspect role in the flow:**
- **Step 2:** Aspects define the knowledge extraction scope
- **Step 3:** Each Aspect guides systematic probing; discovered entities belong to Intent but associate with Aspect
- **Step 4:** Aspects become "Domain-Specific Guidance" sections in prompt (grouping associated entities)
- **Step 6:** Insights may reveal missing Aspects

**Two insight loops:**
- **Inner loop (sharpening):** Insights emerge as user articulates → immediately incorporated
- **Outer loop (execution):** Insights emerge from Output, Prompt, or Assumption → feed back for next iteration

---

## Design Principles

1. **Single model** — No separate "conceptual" vs "persistence" layers. These entities are both.

2. **Articulation-driven** — Entities (Input, Choice, Pitfall, Assumption, Quality, Example) exist to make implicit knowledge explicit, not as forms to fill out.

3. **Feedback loop** — Insight → Intent cycle enables continuous improvement based on actual use.

4. **Prompt as byproduct** — The prompt is generated from the sharpened intent, it is a natural result from clarity.

5. **Executor-agnostic** — The articulation work (Input, Choice, Example, etc.) is valuable whether the executor is an LLM, human, or agency.

---

## What Changed from v1

| v1 Entity | v2 Treatment | Rationale |
|-----------|--------------|-----------|
| Intent | **Kept** | Core entity, unchanged in purpose |
| Fact | **Dropped** | Too generic; replaced by specific entities |
| Prompt | **Kept** | Valuable for versioning and tracking |
| Output | **Kept** | Enables evaluation and learning |
| Insight | **Kept** | Critical for feedback loop |
| (none) | **Added: Aspect** | Knowledge extraction scaffold, optional grouping for articulation |
| (none) | **Added: Input** | Explicit input requirements |
| (none) | **Added: Choice** | Explicit decisions/trade-offs |
| (none) | **Added: Pitfall** | Explicit failure modes |
| (none) | **Added: Assumption** | Explicit implicit knowledge |
| (none) | **Added: Quality** | Explicit success criteria |
| (none) | **Added: Example** | Concrete input→output demonstrations |

**Key insights:** 
- "Fact" was doing too much work. Breaking it into purpose-specific entities (Input, Choice, Pitfall, Assumption, Quality, Example) provides structure for the sharpening process.
- "Aspect" guides knowledge extraction but doesn't own articulation entities — they belong to Intent and may optionally associate with the Aspect they were discovered for. This keeps the model flat while enabling organized discovery.
- "Example" enables few-shot learning in prompts — concrete demonstrations often communicate intent more effectively than abstract descriptions.

---

## Data Definitions

### Intent
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the intent |
| name | string | yes | Short, recognizable label for the intent |
| description | text | yes | Full articulation of what the user wants to accomplish |
| created_at | timestamp | yes | When the intent was first created |
| updated_at | timestamp | yes | When the intent was last modified |

---

### Aspect
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the aspect |
| intent_id | integer | yes | The intent this aspect belongs to (FK to Intent) |
| name | string | yes | Domain or area of consideration (e.g., "SEO", "Audience") |
| description | text | no | Explanation of what this aspect covers |
| created_at | timestamp | yes | When the aspect was first created |
| updated_at | timestamp | yes | When the aspect was last modified |

---

### Input
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the input |
| intent_id | integer | yes | The intent this input belongs to (FK to Intent) |
| aspect_id | integer | no | The aspect this input was discovered for (FK to Aspect) |
| name | string | yes | Short label identifying the input (e.g., "Source document") |
| description | text | yes | What this input is and why it's needed |
| format | string | no | Expected structure or encoding (e.g., "JSON", "PDF", "plain text") |
| required | boolean | yes | Whether the input is mandatory for execution (default: true) |
| created_at | timestamp | yes | When the input was first created |
| updated_at | timestamp | yes | When the input was last modified |

---

### Choice
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the choice |
| intent_id | integer | yes | The intent this choice belongs to (FK to Intent) |
| aspect_id | integer | no | The aspect this choice was discovered for (FK to Aspect) |
| name | string | yes | Short label for the decision point (e.g., "Tone selection") |
| description | text | yes | The decision that needs to be made and why it matters |
| options | text | no | Available alternatives with trade-offs (JSON array or prose) |
| selected_option | string | no | The chosen approach from the options |
| rationale | text | no | Justification for the selected option |
| created_at | timestamp | yes | When the choice was first created |
| updated_at | timestamp | yes | When the choice was last modified |

---

### Pitfall
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the pitfall |
| intent_id | integer | yes | The intent this pitfall belongs to (FK to Intent) |
| aspect_id | integer | no | The aspect this pitfall was discovered for (FK to Aspect) |
| description | text | yes | The failure mode, mistake, or anti-pattern to avoid |
| mitigation | text | no | How to prevent or handle this pitfall |
| created_at | timestamp | yes | When the pitfall was first created |
| updated_at | timestamp | yes | When the pitfall was last modified |

---

### Assumption
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the assumption |
| intent_id | integer | yes | The intent this assumption belongs to (FK to Intent) |
| aspect_id | integer | no | The aspect this assumption was discovered for (FK to Aspect) |
| description | text | yes | The implicit belief being made explicit |
| confidence | enum | no | Certainty level: `verified`, `likely`, `uncertain` |
| created_at | timestamp | yes | When the assumption was first created |
| updated_at | timestamp | yes | When the assumption was last modified |

---

### Quality
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the quality criterion |
| intent_id | integer | yes | The intent this quality belongs to (FK to Intent) |
| aspect_id | integer | no | The aspect this quality was discovered for (FK to Aspect) |
| criterion | text | yes | The standard or condition that defines success |
| measurement | text | no | How to verify or evaluate whether the criterion is met |
| priority | enum | no | Importance level: `must_have`, `should_have`, `nice_to_have` |
| created_at | timestamp | yes | When the quality was first created |
| updated_at | timestamp | yes | When the quality was last modified |

---

### Example
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the example |
| intent_id | integer | yes | The intent this example belongs to (FK to Intent) |
| aspect_id | integer | no | The aspect this example was discovered for (FK to Aspect) |
| sample | text | yes | Textual representation of a an example incl. good or bad  |
| explanation | text | no | Why this example is instructive or what it demonstrates |
| source | enum | no | Origin: `user_provided`, `llm_generated`, `from_output` |
| created_at | timestamp | yes | When the example was first created |
| updated_at | timestamp | yes | When the example was last modified |

---

### Prompt
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the prompt |
| intent_id | integer | yes | The intent this prompt was generated from (FK to Intent) |
| content | text | yes | The complete instruction text for the AI executor |
| version | integer | yes | Sequence number within the intent (increments with each generation) |
| created_at | timestamp | yes | When the prompt was generated |
| updated_at | timestamp | yes | Set once at creation (prompt is immutable after generation) |

---

### Output
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the output |
| prompt_id | integer | yes | The prompt that produced this output (FK to Prompt) |
| content | text | yes | The AI executor's response |
| created_at | timestamp | yes | When the output was produced |
| updated_at | timestamp | yes | Set once at creation (output is immutable after production) |

---

### Insight
| Attribute | Type | Required | Definition |
|-----------|------|----------|------------|
| id | integer | yes | Unique identifier for the insight |
| intent_id | integer | yes | The intent this insight feeds back to (FK to Intent) |
| content | text | yes | The discovery or learning being captured |
| source_type | enum | no | What triggered the insight: `sharpening`, `output`, `prompt`, `assumption` |
| source_output_id | integer | no | The output that surfaced this insight (FK to Output) |
| source_prompt_id | integer | no | The prompt that surfaced this insight (FK to Prompt) |
| source_assumption_id | integer | no | The assumption that was challenged (FK to Assumption) |
| status | enum | no | Processing state: `pending`, `incorporated`, `dismissed` |
| created_at | timestamp | yes | When the insight was first captured |
| updated_at | timestamp | yes | When the insight was last modified |
