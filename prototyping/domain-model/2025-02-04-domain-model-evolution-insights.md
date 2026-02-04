# Domain Model Evolution: Insights and Decision Journey
**Date:** 2025-02-04

This document captures the thinking process and key insights from a domain modeling session for SharpIntent. The goal is to help future readers understand *why* the model evolved the way it did, not just *what* it became.

---

## Starting Point: Complexity Concern

The conversation began with a review of an existing reference domain model that had many entities: Task, TaskReference, Input, Output, Decision, ContextRequirement, Constraint, Assumption, SuccessCriterion, FailureMode — plus supporting structures like InputSource, TradeOffs, BestPractice, RecommendationRule, HelperQuestion, and AcquisitionMethod.

**The first question raised:** Is this too complicated? Specifically, the distinctions between Input, Decision, Constraint, Context, and Assumption seemed challenging to maintain. The original model had extensive disambiguation guides and decision trees just to help classify things correctly — a sign that the boundaries might be artificial or unclear.

---

## First Simplification Attempt: Prompt-Centric (Rejected)

The initial instinct was to simplify by working backward from the output: "What do we need to generate a good prompt?"

This led to a model like:
```
PROMPT = Task + Input + Output + Context + Rules + Quality Criteria
```

Six entities that map directly to prompt sections. Clean, simple.

**Why this was rejected:** The user pointed out that this approach has a bias — it starts from the end (prompt) and works backward. This is a "fill in the blanks" approach that isn't differentiated. The prompt should be a *byproduct*, not the organizing principle.

**Key insight:** Starting from the output format constrains thinking. If we want to differentiate the product, we need to start from how users naturally think.

---

## Second Attempt: User-Centric Cognitive Flow (Partially Rejected)

Flipping the perspective: "How do people actually think when approaching a task?"

Natural cognitive flow might be:
1. "I want to..." — fuzzy goal
2. "I have..." — taking stock of materials
3. "I'm not sure about..." — awareness of gaps
4. "I'm worried about..." — what could go wrong
5. "I could do it this way or that way..." — sensing options
6. "It's done when..." — completion sense

This led to entities like: Goal, Materials, Uncertainties, Concerns, Approaches, Success.

**Why this was partially rejected:** This framing assumes users need help figuring out what they want. But in reality, users *believe* they already know what they want. They're not uncertain about the goal — they're uncertain about the execution.

**Key insight:** Users are often domain experts. They don't need help with "what" — they need help with "how to communicate it precisely."

---

## The Iceberg Metaphor Emerges

A more accurate user mental model:
- "I know what I want" (confident) ✓
- "I know my domain" (often experts themselves)
- "I want reliable, quality results" (consistency matters)
- "I'm not sure what I need to make explicit" (the articulation gap)

This framing positions the service value as **bridging the articulation gap** — the difference between what's in the user's head (implicit, intuitive, assumed) and what needs to be explicit for reliable execution.

**Critical refinement:** The initial framing used language like "revealing what users don't see" or "showing blind spots." This was adjusted to be less condescending. Users aren't blind — they have expertise. The gap is about *communication*, not *knowledge*.

---

## Executor-Agnostic Value

Another important refinement: The value shouldn't be framed purely around LLMs.

Early versions focused heavily on "what the LLM needs" — but this limits the value proposition. A well-articulated task is valuable whether given to:
- An LLM (can't read minds, needs explicit instructions)
- A human contractor (different mental model, different assumptions)
- An agency (needs clear brief to deliver)
- The user themselves in 6 months (will have forgotten implicit context)

**Key insight:** LLMs made the articulation gap painfully visible (bad prompt → bad output, immediately). But the fundamental problem of implicit vs. explicit exists for any executor. LLMs are a catalyst, not the purpose.

The final framing became: "You know what you want. We help you say it precisely enough that anyone — or anything — can deliver it reliably."

---

## The Simplified Entity Model

From this thinking, six articulation entities emerged:

1. **Task** — the goal, sharpened and made precise
2. **Inputs** — what they have (and what needs to be known about it)
3. **Choices** — decisions that need to be explicit, not left to interpretation
4. **Pitfalls** — where things typically go wrong without guidance
5. **Quality** — criteria that need to be spelled out for consistent results
6. **Assumptions** — implicit beliefs that won't transfer automatically

Each entity represents a category of "what needs to be articulated" rather than a form field to fill out.

---

## GEPA Research Integration

A review of the GEPA paper (Genetic-Pareto prompt optimizer, arXiv:2507.19457) provided empirical support for certain prompt structures. Key findings:

1. **Structured prompts outperform vague ones** — explicit sections for Task Overview, Domain-Specific Guidance, Key Requirements, Common Pitfalls, etc.

2. **Pitfalls are high-leverage** — explicitly stating what NOT to do often improves results more than adding more "do" instructions

3. **Domain knowledge must be injected** — models don't reliably apply domain expertise unless explicitly told

4. **Examples demonstrate format** — showing expected output structure reduces format errors

The evolution pattern from GEPA's research shows prompts improving from simple instructions to detailed guidance with domain knowledge, pitfalls, and examples. This validated the articulation entity approach.

---

## Unifying with the Implementation Model

The existing implementation had a domain model (INTENTS_DOMAIN) with different entities: Intent, Fact, Prompt, Output, Insight. Comparing these models revealed:

**What the implementation had that the conceptual model lacked:**
- **Insight** — a feedback loop from outputs back to intent, enabling iterative refinement
- **Prompt and Output as entities** — tracking what was generated and produced

**What the conceptual model had that the implementation lacked:**
- **Structured articulation** — Fact was too generic, doing five jobs poorly
- **Pitfalls and Choices** — high-leverage concepts with no home

The user explicitly rejected having separate models for "persistence" and "UX" — translation mismatch between layers is a recurring problem. The goal became a single unified model.

---

## Insight Timing Correction

An important correction emerged: Insights don't just come from Outputs after execution. They also surface *during* the sharpening process.

As the user provides information and the LLM helps articulate, insights emerge:
- "Have you considered X?"
- "What happens if Y?"
- "This might conflict with Z"

This creates two insight loops:
- **Inner loop (sharpening):** Insights emerge during articulation → immediately incorporated
- **Outer loop (execution):** Insights emerge from outputs → feed back for next iteration

---

## The Aspect Discovery

A question arose about organizing potentially numerous articulation entity instances. An Intent might accumulate 15 Inputs, 8 Choices, 12 Pitfalls — this becomes unwieldy without structure.

The initial framing was organizational convenience (grouping related items). But a deeper insight emerged: **Aspects serve as boundaries for knowledge extraction**.

When the LLM helps sharpen an intent, it needs to know what domains/areas to probe. Without structure, the LLM might surface insights randomly or miss entire areas.

Aspects provide:
1. **Extraction scope** — tells LLM "explore this domain for insights"
2. **Completeness check** — "have we covered all relevant aspects?"
3. **Conversation structure** — guides the sharpening dialogue
4. **Grouping** — organizes resulting articulation entities

**Connection to prompts:** Aspects map directly to "Domain-Specific Guidance" sections in the generated prompt. This means the structuring element serves dual purpose — it guides extraction AND becomes prompt content.

---

## Role: Attribute vs. Inference

A final question: Prompts typically define a role for the LLM (e.g., "You are an SEO specialist"). Should this be an explicit attribute?

The analysis suggested Role is really *framing* — it sets expertise, tone, and perspective. It can often be derived from:
- The Intent description
- The Aspects involved
- Quality criteria about tone

**Decision:** Leave Role as a computed/inferred property rather than adding another attribute. The role can be composed from existing information at prompt generation time. If this proves insufficient, it can be added as an optional override later.

---

## Final Model Shape

The unified model has 10 entities across 4 categories:

**Core Entity:**
- Intent — the user's goal

**Structuring Entity:**
- Aspect — domain/area for knowledge extraction and grouping

**Articulation Entities:**
- Input — what user provides/has
- Choice — decisions that need to be explicit
- Pitfall — failure modes to avoid
- Assumption — implicit beliefs that need stating
- Quality — success criteria and output format

**Execution & Learning Entities:**
- Prompt — generated, versioned instruction
- Output — what AI produced
- Insight — discoveries that feed back (from sharpening OR execution)

---

## Key Takeaways for Future Development

1. **Value framing matters** — "articulation" not "revelation"; users are experts, not blind

2. **The prompt is a byproduct** — the articulation work is valuable regardless of output format

3. **Structured beats vague** — GEPA research supports explicit sections, especially for pitfalls and domain guidance

4. **Single model** — avoid separate conceptual/implementation models; translation mismatch is a persistent problem

5. **Aspects have dual purpose** — they're not just organizational; they guide knowledge extraction and become prompt content

6. **Two insight loops** — learning happens during sharpening AND after execution

7. **Start from user mental model** — not from output format, not from system needs

8. **LLMs are catalyst, not purpose** — the articulation gap exists for any executor; LLMs just made it visible
