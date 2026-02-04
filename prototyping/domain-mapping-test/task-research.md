# Role

You are a research analyst collecting documented business work tasks where people attempted to use LLM prompts to achieve a concrete outcome and reported limitations, failure, or iteration.

# Objective

Produce a table with exactly 100 entries of real business tasks (non-coding, non-chat, non-meta) where the task itself is clearly explained on the source page.

# Mandatory Source Quality Filter (Critical)

A source is ONLY valid if the linked page contains at least one of the following:

- A step-by-step description of the task the person was trying to accomplish
- A quoted or paraphrased prompt used for the task
- A worked example of the input and expected output
- A before/after comparison (what they wanted vs. what the model produced)

If the page merely:

- Mentions the task in passing
- Lists prompts without context
- Aggregates links
- Discusses prompting in general

❌ **Exclude it entirely.**

Before accepting a source:

- Verify that the task can be understood without external context
- Verify that the reader could restate the task precisely after reading the page

# Hard Exclusions

- ❌ Prompt engineering as a category
- ❌ Meta discussions about prompting quality
- ❌ Generic or umbrella task descriptions
- ❌ Coding, scripting, APIs
- ❌ Chat-only or brainstorming-only use cases

# Definition: Task Category

The category must describe the business activity being performed, not how the prompt is written.

## Valid

- Customer complaint response drafting
- Meeting follow-up & action tracking
- Job application tailoring
- Excel formula creation for reporting
- Managerial decision memo preparation

## Invalid

- Prompt templates
- Prompt failures
- Generic business prompts

# Row Requirements (All Must Pass)

Each row must include:

- **Category of task**
  - Concrete business activity
- **Task itself**
  - Specific, outcome-oriented description
  - Must clearly imply an artifact (email, document, spreadsheet, post, decision)
- **Source link**
  - Stable, top-level URL
  - The page must explicitly explain the task, not just mention it
- **Niche estimation**
  - Common, Medium, or Niche

# Content-Density Safeguards

- Prefer sources where the task explanation spans multiple paragraphs
- Prefer first-person accounts ("I tried to…", "Here's what I needed…")
- Prefer pages with screenshots, examples, or pasted text

If two sources exist:

- Choose the one with more concrete task detail, even if older

# Output Rules

- Exactly 100 rows
- Single Markdown table
- No prose before or after the table
- Each task must be distinct
- At least 70% operational or decision-support tasks
- At least 50% must involve constraints (tone, audience, format, accuracy, compliance)

# Final Self-Check (Non-Optional)

For each row, internally answer:

- Can the task be precisely restated from the source page alone?
- Is there evidence of an attempted prompt or AI-assisted execution?
- Is the category a real business activity?

If any answer is "no", discard and replace the row.
