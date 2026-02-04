# Content Brief: From Generic Prompts to Precision Intents

## Intent: write_content_article

---

## KNOWLEDGE INPUTS

### Core Claims

| Claim | Evidence | Source |
|-------|----------|--------|
| Prompts available online for keyword research are shallow and produce generic results | Aleyda Solis prompt: "Cluster the following keywords into groups based on their semantic relevance: [list]" — lacks context, output format, audience, purpose | Web research, January 2026 |
| The gap between online prompts and effective prompts is in the hidden parameters | Original prompt: 1 instruction. Our final template: 15+ parameters across context, scope, filters, output format, cognitive expansion | This conversation — direct comparison |
| LLMs cannot invent business-specific knowledge — users must provide it | "Write a section about why Intentive is better than PromptBase" without facts → hallucination. With key differentiators provided → accurate assembly | Demonstrated in conversation |
| Most prompts optimize for brevity, but brevity creates ambiguity | "Give me 50 keywords for my product" requires LLM to guess: what product? what audience? what intent distribution? what to exclude? | Conversation analysis |
| Structured parameter elicitation surfaces decisions users didn't know they had to make | User initially asked for "keyword research prompts." Through probing, we discovered: funnel distribution, messy keyword inclusion, audience exclusion, cognitive expansion types | Conversation progression |
| A meta-prompt can systematically generate high-quality intent templates | We created an "Intent Architect" prompt that follows 6 steps: understand task → identify hidden parameters → challenge obvious → define schema → write template → validate | Conversation output |

### Process Documentation

| Step | What Happened | Insight Surfaced |
|------|---------------|------------------|
| 1. Research | Searched for "best prompts for keyword research" | Found prompts rated 6-7/10 against best practices |
| 2. Assessment | Evaluated prompts against OpenAI/MIT guidelines | Identified: missing context, no output format, no constraints |
| 3. Initial prompt | Created improved version with role, context, format | Still missing: cognitive expansion, messy keywords, audience filtering |
| 4. Iteration | User pushed back: "looked shallow on specific knowledge side" | Realized: LLM needs facts provided, not just instructions |
| 5. Parameterization | Extracted all decision points into explicit parameters | 15+ parameters surfaced from what seemed like a simple task |
| 6. Meta-level | Created prompt that generates intent templates | Pattern becomes repeatable across any task type |

### Before/After Examples

**Example 1: Keyword Clustering Prompt**

*Before (typical online prompt):*
```
Cluster the following keywords into groups based on their semantic relevance: [list]
```

*After (parameterized intent):*
```
You are an SEO strategist specializing in *business_type* keyword discovery.

Generate a keyword research table with exactly *keyword_count* keywords...
- Target audience: *target_audience*
- Exclude terms: *exclude_terms*
- Include messy/pre-category keywords: *include_messy_keywords*
- Funnel distribution: *funnel_awareness_pct*% awareness, *funnel_consideration_pct*% consideration, *funnel_decision_pct*% decision
- Output format: table with columns [Keyword | Search Intent | Funnel Stage | Content Type | Priority | Cluster Name]
```

**Example 2: Content Section Writing**

*Before (typical approach):*
```
Write a section about prompt engineering best practices
```

*After (with knowledge inputs):*
```
Section heading: "Why Most Prompts Fail"
Section goal: Create problem awareness

Core claims to make:
- Claim: "Vague prompts produce vague outputs"
  Evidence: "In our testing, adding constraints improved output relevance by 60%"
  
- Claim: "Most users have never been taught prompt structure"  
  Evidence: "Only 12% of ChatGPT users have read any prompting guide"

Example to include:
  Before: "Write about our product"
  After: "Write a 200-word product description for [product], highlighting [benefits], for [audience], in [tone]"

Do not claim: [specific guardrails]
```

### Hidden Parameters We Discovered

| Seemed Obvious | Actually Required |
|----------------|-------------------|
| "Keywords for my product" | Product description, business type, target audience, geographic market, competitors |
| "50 keywords" | Funnel distribution (how many awareness vs decision?), keyword length range |
| "Good keywords" | Include messy/pre-category? Include frustration-driven searches? Emerging terminology? |
| "Relevant keywords" | Exclude which terms? Exclude which audience signals? |
| "Organized output" | Exact columns, value options for each column, cluster naming hints |
| "SEO keywords" | For which content types? Blog, landing page, comparison page? |

### Ambiguities That Remained

Even in our refined template, some decisions are still implicit:

| Ambiguity | Why It's Hard to Parameterize |
|-----------|------------------------------|
| What counts as "messy" in a given domain | Requires domain examples — we added *example_messy_keywords* but user must provide them |
| How to weight priority without volume data | "Perceived competitiveness" is subjective — honest about limitation |
| Optimal funnel distribution | We defaulted 40/40/20 — but this varies by business maturity, existing content |
| When a keyword is "too technical" | *exclude_audience_signals* helps but requires user judgment |
| Cluster granularity | How many clusters? How specific? Not parameterized — could be added |

### Key Quotes from Conversation

- "The prompt isn't the product. The parameter structure is."
- "You supply the 'what.' LLM supplies the 'how it's written.'"
- "Forcing users to answer: Who is this for? What should be excluded? What does 'messy' mean in my domain? ...makes them think sharper before they ever hit 'generate'."
- "Most prompts online are 'templates' only in the sense that you swap out the keyword list. What we built is a true parameterized intent."

### The Meta-Prompt Insight

We created a prompt that generates intent templates by:

1. **Understanding the task** — What is the actual outcome? What decisions are hidden?
2. **Identifying hidden parameters** — Context, scope, input knowledge, output format, quality criteria, constraints
3. **Challenging the obvious** — What would a lazy prompt produce? What would an expert do differently?
4. **Defining the schema** — Type, required, default, description, example for each parameter
5. **Writing the template** — With all parameters marked inline
6. **Validating** — Could two users with same inputs get consistent results?

---

## STRUCTURAL INPUTS

### Article Structure

```
1. Introduction
   - The promise vs reality of AI prompts
   - Why "prompt libraries" underdeliver

2. The Experiment
   - Starting point: researching keyword research prompts
   - What we found online (with examples)
   - Assessment against best practices

3. The Gap
   - Side-by-side comparison: online prompt vs parameterized intent
   - The hidden decisions inside "simple" tasks

4. Building a Real Intent
   - Walking through parameter extraction
   - The "cognitive expansion" discovery
   - Why users must provide knowledge, not just instructions

5. Remaining Ambiguities
   - Honest about what we couldn't parameterize
   - Where human judgment is still required

6. The Meta-Level
   - Can this process be systematized?
   - The Intent Architect approach

7. Conclusion
   - From prompt templates to intent specifications
   - The Intentive approach: clarity before execution
```

### Content Goals

| Goal | How to Achieve |
|------|----------------|
| Establish credibility | Show actual research, real prompt comparisons, specific ratings |
| Create "aha" moment | The before/after examples should be viscerally different |
| Demonstrate depth | Hidden parameters table shows the 10x complexity beneath simple tasks |
| Be honest about limits | Ambiguities section builds trust |
| Lead to product | Intent specification → Intentive's value proposition |

### Target Length

- Total: 2000-2500 words
- Introduction: 200 words
- The Experiment: 400 words
- The Gap: 400 words
- Building a Real Intent: 500 words
- Remaining Ambiguities: 250 words
- The Meta-Level: 300 words
- Conclusion: 150 words

---

## STYLE INPUTS

### Audience

- Primary: Marketing professionals, content creators, business users exploring AI tools
- Secondary: Solopreneurs, startup founders evaluating prompt tools
- Technical level: Comfortable with AI tools, not developers
- Mindset: Frustrated with generic AI outputs, looking for better approach

### Tone

- Confident but not arrogant
- Show-don't-tell: evidence over claims
- Conversational, not academic
- Acknowledge complexity without overwhelming
- Empathetic to the "why isn't this working?" frustration

### Voice

- First person plural ("we discovered", "our process")
- Direct address to reader ("you've probably experienced")
- Active voice
- Short paragraphs, scannable structure

### Do's and Don'ts

| Do | Don't |
|----|-------|
| Show real prompt examples | Use hypothetical "imagine if" scenarios |
| Admit limitations and ambiguities | Claim we solved everything |
| Use specific numbers (15 parameters, 6 steps) | Use vague qualifiers ("many", "various") |
| Reference the actual conversation process | Make it sound like we knew this from the start |
| End sections with forward momentum | Let sections trail off |

---

## SEO INPUTS

### Primary Keyword
- "prompt engineering for business users"

### Secondary Keywords
- "AI prompt templates"
- "keyword research prompts"
- "ChatGPT prompt optimization"
- "intent-based prompting"
- "parameterized prompts"

### Keyword Usage

- Include primary keyword in H1 and first 100 words
- Use secondary keywords in H2s where natural
- Don't force keywords — readability over density

---

## OUTPUT SPECIFICATION

### Format
- Markdown
- H1 for title, H2 for main sections, H3 for subsections
- Code blocks for prompt examples (before/after)
- Tables for comparisons and parameter lists
- Pull quotes for key insights

### Meta Elements to Generate
- Page title (max 60 characters)
- Meta description (max 155 characters)
- Suggested URL slug

### Call to Action
- End with invitation to explore Intentive's approach
- Soft CTA — "this is what we're building" not "sign up now"

---

## INSTRUCTION

Write the complete article following this brief. Maintain the evidence-based, show-don't-tell approach throughout. The reader should finish understanding:

1. Why their current prompts underperform
2. What "parameterized intent" means in practice
3. That this is a learnable, systematizable skill
4. That Intentive is building tools to make this easier

Generate the article now.
