# The Iceberg Metaphor: SharpIntent Value Proposition

## User Mental Model

Users approach SharpIntent with a specific Goal:

- **"I know what I want"** (confident) ✓
- **"I know my domain"** (often experts themselves)
- **"I want reliable, quality results"** (consistency matters)
- **"I'm not sure what I need to make explicit"** (the articulation gap)

The gap isn't domain expertise — users often have that. The gap is between:
- What's in their head (implicit, intuitive, assumed)
- What needs to be explicit for reliable execution by anyone

This matters whether the executor is:
- An LLM (can't read minds, needs explicit instructions)
- A human contractor (different mental model, different assumptions)
- An agency (needs clear brief to deliver what you actually want)
- Themselves in 6 months (will have forgotten the implicit context)

## Core Value Proposition

**Your service helps turn implicit expertise into explicit specification.**

> "You know what you want. We help you say it precisely enough that anyone — or anything — can deliver it reliably."

The value is **articulation and sparring**. Users have the knowledge; the service helps sharpen and express it in a form that transfers.

---

## The Iceberg Framing

```
       ═══════════════════════
        What user brings:
        • Goal (confident)
        • Domain expertise
        • Materials to work with
        • Intuitive sense of quality
       ═══════════════════════  ← waterline (articulation gap)
        What service reveals:
        • What needs to be made explicit
        • Decisions that can't be left implicit
        • Assumptions that won't transfer automatically
        • Quality criteria that need to be spelled out
        • Edge cases that need guidance
        • Context that seems obvious but isn't
       ═══════════════════════
```

The waterline represents the **articulation gap** — the difference between what the user knows implicitly and what needs to be explicit for reliable execution.

**Why LLMs amplify this need (but didn't create it):**
- LLMs make the cost of poor articulation visible immediately
- LLMs can't course-correct interactively like a human might
- But the fundamental problem — implicit vs. explicit — exists for any executor
- A well-articulated task is valuable whether given to an LLM, contractor, or agency

---

## Entity Design: User Provides vs. Service Reveals

| User provides | Service reveals (for any executor) |
|---------------|-----------------------------------|
| **Goal** | → what needs to be explicit for precise understanding |
| **Domain expertise** | → which parts can't be assumed by others |
| **Materials** | → **Input requirements** that need to be spelled out |
| Intuitive quality sense | → explicit **Quality Criteria** for consistent results |
| Implicit assumptions | → **Assumptions** that need to be stated |
| Preferred approach | → **Choices** and trade-offs that matter |

---

## Simplified Entity Model

Based on the iceberg framing, six core entities emerge:

1. **Task** — their goal, sharpened and made precise
2. **Inputs** — what they have (and what needs to be known about it)
3. **Choices** — decisions that need to be explicit, not left to interpretation
4. **Pitfalls** — where things typically go wrong without guidance
5. **Quality** — criteria that need to be spelled out for consistent results
6. **Assumptions** — implicit beliefs that won't transfer automatically

The service helps make implicit knowledge explicit. The entities represent what needs to be articulated, not forms the user fills out.

**The output is flexible:** A sharpened intent can become a prompt for an LLM, a brief for a contractor, or a specification for an agency — the articulation work is valuable regardless of executor.


---

## Key Differentiator

Most prompt-building tools ask: "Tell me what the AI needs to know."

SharpIntent asks: "What's your goal?" — then helps you articulate it with enough precision for reliable execution.

The user brings domain expertise. The service helps structure and express it. The output — whether prompt, brief, or specification — is a byproduct of sharpened intent, not the organizing principle.

**LLMs are a catalyst, not the purpose:** LLMs made the articulation gap painfully visible (bad prompt → bad output, immediately). But the value of sharpened intent extends to any executor — human or machine.


---

## The Shift in Thinking: Conversation Journey

This document emerged through a progressive reframing of the domain model:

### Stage 1: Ontology-Driven (Original Model)

Started with a rich, academically precise domain model with many entities:
- Task, TaskReference, Input, Output, Decision, ContextRequirement, Constraint, Assumption, SuccessCriterion, FailureMode
- Plus supporting structures: InputSource, TradeOffs, BestPractice, RecommendationRule, HelperQuestion, AcquisitionMethod

**Problem identified:** The distinctions between Input, Decision, Constraint, Context, and Assumption were hard to maintain — lots of edge cases and "can be both" situations.

### Stage 2: Prompt-Centric (First Simplification)

Reframed around: "What do we need to generate a good prompt?"

```
PROMPT = Task + Input + Output + Context + Rules + Quality Criteria
```

Reduced to 6 entities that map directly to prompt sections.

**Problem identified:** This works backward from output (prompt) to input (user). It's a "fill in the blanks" approach — not differentiated.

### Stage 3: User-Centric (Cognitive Flow)

Flipped to: "How do people actually think when approaching a task?"

Natural cognitive flow:
1. "I want to..." — fuzzy goal
2. "I have..." — taking stock
3. "I'm not sure about..." — awareness of gaps
4. "I'm worried about..." — what could go wrong
5. "I could do it this way or that way..." — sensing options
6. "It's done when..." — completion sense

Led to entities like: Goal, Materials, Uncertainties, Concerns, Approaches, Success

**Problem identified:** This assumes users need help figuring out what they want. But users believe they already know what they want.

### Stage 4: Articulation-Centric (Iceberg Model) ← Current

Key insight: Users are:
- **Confident** about what they want
- **Knowledgeable** in their domain (often experts)
- **Uncertain** about what needs to be made explicit vs. can be left implicit
- **Focused** on reliable, quality results

The value isn't helping users articulate their goals — it's **surfacing what needs to be explicit for reliable execution**.

This shifts the service from:
- Interview → Guided articulation
- User fills in forms → Service helps make implicit knowledge explicit
- Output = prompt → Output = sharpened intent (prompt is one format)
- Collecting information → Structuring expertise for transfer