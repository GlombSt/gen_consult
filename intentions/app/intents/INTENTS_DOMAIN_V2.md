# Intents Domain Model v2

## Overview

A unified domain model for capturing, sharpening, and executing user intents. Combines implementation needs with the conceptual framework for articulating what needs to be explicit.

---

## Entity Categories

### Core Entity
- **Intent** — the user's goal

### Structuring Entity
- **Aspect** — a domain/area of consideration that guides knowledge extraction and groups articulation

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
                         └─────────────────┬───────────────────┘
                                           │
                         ┌─────────────────┼─────────────────┐
                         │                 │                 │
                         ▼                 ▼                 ▼
                   ┌───────────┐     ┌───────────┐     ┌───────────┐
                   │  ASPECT   │     │  ASPECT   │     │  ASPECT   │
                   │ (domain 1)│     │ (domain 2)│     │ (domain n)│
                   └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
                         │                 │                 │
          ┌──────────────┼──────────────┐  │                 │
          │              │              │  │                 │
          ▼              ▼              ▼  ▼                 ▼
     ┌─────────┐  ┌──────────┐  ┌─────────┐    (articulation entities
     │  INPUT  │  │  CHOICE  │  │ PITFALL │     grouped by aspect)
     └─────────┘  └──────────┘  └─────────┘
     ┌──────────────┐  ┌─────────┐  ┌─────────┐
     │  ASSUMPTION  │  │ QUALITY │  │ EXAMPLE │
     └──────────────┘  └─────────┘  └─────────┘

                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
                    │  ┌───────────────┐                          │
                    │  │    INSIGHT    │ ◄────────────────────────┤
                    │  │ (from sharpening                         │
                    │  │  or execution)│                          │
                    │  └───────┬───────┘                          │
                    │          │ feeds back                       │
                    │          ▼                                  │
                    │     to INTENT                               │
                    │                                             │
                    │                      generates              │
                    │                          │                  │
                    │                          ▼                  │
                    │                  ┌───────────────┐          │
                    │                  │    PROMPT     │          │
                    │                  │  (versioned)  │          │
                    │                  └───────┬───────┘          │
                    │                          │ produces         │
                    │                          ▼                  │
                    │                  ┌───────────────┐          │
                    │                  │    OUTPUT     │──────────┘
                    │                  └───────────────┘   yields
                    │                                     insights
                    └─────────────────────────────────────────────┘
```

---

## Entities

### Intent
**What it is:** The user's goal — what they want to accomplish. The anchor entity that everything else relates to. Intents are reusable across multiple instances/situations, not one-off requests.

**Role in the system:** The thing being sharpened. Holds the core description and accumulates the articulation work.

---

### Aspect
**What it is:** A domain or area of consideration relevant to the intent — a bounded scope for knowledge extraction and articulation grouping.

**Role in the system:** 
- **Knowledge extraction scaffold:** Tells the LLM "explore this domain for insights" during sharpening
- **Completeness check:** Ensures all relevant areas are covered ("Have we addressed the SEO aspect?")
- **Articulation grouping:** Organizes Inputs, Choices, Pitfalls, Assumptions, Quality under meaningful themes
- **Prompt domain guidance:** Becomes the "Domain-Specific Guidance" section in the generated prompt

**Where Aspects come from:**
- **Task templates** — known task types have standard aspects
- **LLM inference** — LLM suggests aspects based on task description
- **User addition** — user adds domain-specific aspects the LLM missed

**Example:** For "Create SEO content brief":
- Aspect: "Audience & Positioning" → contains assumptions about readers, tone choices
- Aspect: "SEO Constraints" → contains keyword inputs, density choices, stuffing pitfalls
- Aspect: "Content Structure" → contains quality criteria for length, sections, data points

**Why it matters:** Without aspects, the LLM might surface insights randomly or miss entire areas. Aspects provide systematic coverage of the knowledge space relevant to the task.

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
Discoveries surfacing during sharpening or from execution — things the user hadn't considered.

**Sources:**
- **Sharpening** — LLM surfaces questions, gaps, considerations ("Have you considered X?")
- **Execution** — discoveries from outputs ("This failed because Z")

The engine of improvement: helps articulate what users didn't know they needed to say, captures learnings for future iterations.

---

## Relationships

```
Intent
├── has many → Aspect
│             ├── has many → Input
│             ├── has many → Choice
│             ├── has many → Pitfall
│             ├── has many → Assumption
│             ├── has many → Quality
│             └── has many → Example
├── has many → Insight ←─────────────────────────┐
├── has many → Prompt (versioned)                │
│             └── produces many → Output         │
│                                 └── yields ────┘
└── receives feedback from ← Insight
```

**Core relationships:**
- Intent has many Aspects
- Aspect groups articulation entities (Input, Choice, Pitfall, Assumption, Quality, Example)
- Articulation entities belong to an Aspect (optional — can exist without aspect for simple intents)
- Intent has many Insights (from sharpening OR execution)
- Intent has many Prompts (each is a version)
- Prompt produces many Outputs
- Output can yield Insights (which attach to Intent)
- Insight feeds back to Intent (closing the loop)

**Aspect role in extraction:**
- LLM uses Aspects to systematically probe for articulation entities
- Each Aspect defines a bounded domain for knowledge extraction
- Aspects ensure completeness: "Have we covered all relevant areas?"

**Insight sources:**
- Sharpening phase → Insight (LLM surfaces considerations during articulation)
- Output → Insight (discoveries from actual execution results)

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

3. SERVICE EXTRACTS KNOWLEDGE PER ASPECT (iterative)
   └── For each Aspect, LLM probes systematically:
       • What inputs are needed for this aspect? → Input
       • What decisions must be made? → Choice
       • What typically goes wrong here? → Pitfall
       • What's assumed but not stated? → Assumption
       • How will we know this aspect is done well? → Quality
       • Can you show me an example? → Example
       
   └── LLM generates Insights during conversation:
       • "Have you considered X?"
       • "What happens if Y?"
       • "This might conflict with Z"
       └── Creates Insight → incorporated into articulation

4. SYSTEM GENERATES PROMPT
   └── Translates sharpened intent into executable instruction:
       • Task Overview ← from Intent
       • Domain-Specific Guidance ← from Aspects (name + grouped content)
       • Key Requirements ← from Choices
       • Input Format ← from Inputs
       • Common Pitfalls ← from Pitfalls
       • Output Format ← from Quality
       • Examples ← from Examples (few-shot demonstrations)
       └── Creates Prompt (versioned)

5. AI PRODUCES OUTPUT
   └── Executes prompt, produces result
       └── Creates Output

6. USER/SYSTEM DISCOVERS INSIGHTS FROM OUTPUT
   └── "This worked" / "This failed" / "Output missed X"
       └── Creates Insight → feeds back to Intent (may surface new Aspects)

7. INTENT IMPROVES
   └── Incorporates insights, sharpens further, generates better prompt
       └── Cycle repeats
```

**Aspect role in the flow:**
- **Step 2:** Aspects define the knowledge extraction scope
- **Step 3:** Each Aspect guides systematic probing
- **Step 4:** Aspects become "Domain-Specific Guidance" sections in prompt
- **Step 6:** Insights may reveal missing Aspects

**Two insight loops:**
- **Inner loop (sharpening):** Insights emerge as user articulates → immediately incorporated
- **Outer loop (execution):** Insights emerge from outputs → feed back for next iteration

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
| (none) | **Added: Aspect** | Knowledge extraction scaffold, domain grouping |
| (none) | **Added: Input** | Explicit input requirements |
| (none) | **Added: Choice** | Explicit decisions/trade-offs |
| (none) | **Added: Pitfall** | Explicit failure modes |
| (none) | **Added: Assumption** | Explicit implicit knowledge |
| (none) | **Added: Quality** | Explicit success criteria |
| (none) | **Added: Example** | Concrete input→output demonstrations |

**Key insights:** 
- "Fact" was doing too much work. Breaking it into purpose-specific entities (Input, Choice, Pitfall, Assumption, Quality, Example) provides structure for the sharpening process.
- "Aspect" provides bounded domains for systematic knowledge extraction and maps directly to prompt structure (Domain-Specific Guidance sections per GEPA research).
- "Example" enables few-shot learning in prompts — concrete demonstrations often communicate intent more effectively than abstract descriptions.
