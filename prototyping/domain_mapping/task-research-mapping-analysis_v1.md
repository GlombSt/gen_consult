# Mapping Analysis: Task Research → Intents Domain Model (v2)

## Overview

This analysis assesses how each piece of information from `task-research.md` maps to the domain model in `INTENTS_DOMAIN.md`, and identifies precision gaps in the domain model description.

---

## Part 1: Information Mapping Assessment

### 1. Role Definition

> "You are a research analyst collecting documented business work tasks where people attempted to use LLM prompts to achieve a concrete outcome and reported limitations, failure, or iteration."

| Element | Mappable? | Target | Intuitiveness | Notes |
|---------|-----------|--------|---------------|-------|
| "business work tasks" | ✅ Yes | `Intent` (as entity) | High | Direct alignment with Intent definition |
| "concrete outcome" | ✅ Yes | `Intent.output_format` + `Intent.output_structure` | Medium | Split across two properties is non-obvious |
| "attempted prompts" | ✅ Yes | `Prompt.content` | High | Direct match |
| "limitations, failure" | ⚠️ Partial | `Insight.content` | Low | Insight describes "discoveries during editing" — failure analysis is a stretch |
| "iteration" | ✅ Yes | `Prompt.version` + `Insight` | Medium | Version captures iteration; Insight captures learnings |

**Domain Precision Issue:** The `Insight` entity is described as "discoveries made during editing" — this is vague. Does "editing" mean editing the Intent? The Prompt? The Output? The relationship to failure/success isn't explicit.

---

### 2. Objective

> "Produce a table with exactly 100 entries of real business tasks..."

| Element | Mappable? | Target | Intuitiveness | Notes |
|---------|-----------|--------|---------------|-------|
| "produce a table" | ✅ Yes | `Intent.output_format` = "Markdown" + `Intent.output_structure` = table | High | Clean mapping |
| "exactly 100 entries" | ⚠️ Partial | `Intent.constraints` | Medium | Quantity constraints fit, but constraints is a single string |
| "real business tasks" | ✅ Yes | `Intent.description` | High | The tasks being researched are Intents |
| "non-coding, non-chat, non-meta" | ⚠️ Partial | `Intent.constraints` | Low | Exclusion criteria awkwardly fit in constraints |
| "task clearly explained" | ❌ No | — | — | Quality criterion with no model representation |

**Domain Precision Issue:** `Intent.constraints` is a single string. When there are multiple distinct constraints (quantity, exclusions, quality criteria), how should they be structured? The model doesn't clarify whether constraints should be free-form prose or structured (e.g., JSON, list).

---

### 3. Mandatory Source Quality Filter

> Sources must contain: step-by-step description, quoted prompt, worked example, or before/after comparison.

| Element | Mappable? | Target | Intuitiveness | Notes |
|---------|-----------|--------|---------------|-------|
| "step-by-step description of task" | ✅ Yes | `Intent.description` | High | Direct match |
| "quoted or paraphrased prompt" | ✅ Yes | `Prompt.content` | High | Direct match |
| "worked example of input" | ⚠️ Partial | `Fact.value` or `Intent.context` | Low | Unclear which is appropriate for examples |
| "expected output" | ⚠️ Partial | `Intent.output_structure` | Medium | "Expected" implies a specification, but output_structure is described as "organization" not "example content" |
| "before/after comparison" | ⚠️ Partial | `Output.content` + `Insight.content` | Low | Model captures output but not explicit comparison |

**Domain Precision Issues:**
1. **Fact vs. Context distinction is unclear.** The model says Facts are "static and explicit" while Context is "fluid and situational" — but a worked example could be either. Is an example a Fact (concrete data point) or Context (informing prompt generation)?
2. **No concept of "expected output" vs. "actual output."** The model has `Output` for what was produced, but no property captures what the user *wanted* to produce. This is a significant gap for mapping "before/after comparison."

---

### 4. Hard Exclusions

> ❌ Prompt engineering, meta discussions, generic tasks, coding, chat-only

| Element | Mappable? | Target | Intuitiveness | Notes |
|---------|-----------|--------|---------------|-------|
| Exclusion criteria | ⚠️ Partial | `Intent.constraints` | Low | Negative constraints ("do NOT...") fit awkwardly |

**Domain Precision Issue:** The model doesn't distinguish between positive constraints ("must be X") and negative constraints ("must NOT be Y"). The constraints property description only gives positive examples: "word limits, tone requirements, format specifications."

---

### 5. Task Category Definition

> Category = business activity, not prompt technique. Valid: "Customer complaint response drafting." Invalid: "Prompt templates."

| Element | Mappable? | Target | Intuitiveness | Notes |
|---------|-----------|--------|---------------|-------|
| "Category of task" | ⚠️ Partial | `Intent.name` | Medium | Name could serve as category, but semantic difference exists |
| Business activity examples | ✅ Yes | `Intent.description` | High | These are exactly what Intent captures |

**Domain Precision Issue:** `Intent.name` is described simply as "name of the intent" with no guidance on what makes a good name. Should it be a verb phrase ("Draft customer complaint response")? A noun phrase ("Customer complaint response drafting")? A short label or full description? The task-research doc distinguishes "category" from "task" — the model conflates them into name + description without clear guidance.

---

### 6. Row Requirements

#### 6.1 Category of Task
| Element | Mappable? | Target | Intuitiveness |
|---------|-----------|--------|---------------|
| "Concrete business activity" | ✅ Yes | `Intent.name` | Medium |

#### 6.2 Task Itself
| Element | Mappable? | Target | Intuitiveness |
|---------|-----------|--------|---------------|
| "Specific, outcome-oriented description" | ✅ Yes | `Intent.description` | High |
| "Must imply an artifact (email, doc...)" | ✅ Yes | `Intent.output_format` | High |

#### 6.3 Source Link
| Element | Mappable? | Target | Intuitiveness |
|---------|-----------|--------|---------------|
| "Stable URL" | ❌ No | — | — |
| "Page must explain task" | ❌ No | — | — |

**Domain Precision Issue:** No provenance tracking. If Intents are meant to be reusable ("not a one-off"), tracking where they came from (template library, user-created, imported) would be valuable. The model has no `source`, `origin`, or `reference` property.

#### 6.4 Niche Estimation
| Element | Mappable? | Target | Intuitiveness |
|---------|-----------|--------|---------------|
| "Common, Medium, or Niche" | ❌ No | — | — |

**Domain Precision Issue:** No classification/categorization system. The model can't represent metadata about the Intent itself (popularity, domain, difficulty).

---

### 7. Content-Density Safeguards

> Prefer multi-paragraph explanations, first-person accounts, screenshots/examples

| Element | Mappable? | Target | Intuitiveness | Notes |
|---------|-----------|--------|---------------|-------|
| "Task explanation spans multiple paragraphs" | ❌ No | — | — | Quality heuristic, not representable |
| "First-person accounts" | ❌ No | — | — | Source characteristic |
| "Screenshots, examples, pasted text" | ⚠️ Partial | `Fact.value` | Low | Examples could be Facts, but screenshots can't be |

**Domain Precision Issue:** `Fact.value` is typed as `string`. This excludes non-text artifacts (images, files, structured data). If Facts are "critical, specific information," shouldn't they support richer content types?

---

### 8. Output Rules

#### 8.1 Format Rules
| Element | Mappable? | Target | Intuitiveness |
|---------|-----------|--------|---------------|
| "Single Markdown table" | ✅ Yes | `Intent.output_format` + `Intent.output_structure` | High |
| "No prose before or after" | ✅ Yes | `Intent.constraints` | Medium |
| "Exactly 100 rows" | ⚠️ Partial | `Intent.constraints` | Medium |

#### 8.2 Content Rules
| Element | Mappable? | Target | Intuitiveness |
|---------|-----------|--------|---------------|
| "Each task must be distinct" | ⚠️ Partial | `Intent.constraints` | Low |
| "70% operational/decision-support" | ❌ No | — | — |
| "50% must involve constraints" | ⚠️ Partial | `Intent.constraints` | Low |

**Domain Precision Issue:** The model doesn't distinguish between constraints on the *output content* ("no prose") vs. constraints on the *collection of outputs* ("70% must be X"). The task-research doc has both types; the model's single `constraints` string can't cleanly separate them.

---

### 9. Final Self-Check

| Element | Mappable? | Target | Intuitiveness |
|---------|-----------|--------|---------------|
| "Can task be precisely restated?" | ✅ Yes | Validates `Intent.description` completeness | High |
| "Evidence of attempted prompt?" | ✅ Yes | `Prompt.content` + `Output.content` | High |
| "Is category a real business activity?" | ✅ Yes | Validates `Intent.name` | High |

---

## Part 2: Domain Model Precision Issues

### Issue 1: Fact vs. Context Boundary is Fuzzy

**Current descriptions:**
- Fact: "static and explicit"
- Context: "fluid and situational"

**Problem:** These are relative terms. Is "the company's tone guide" a Fact (explicit, doesn't change often) or Context (situational, informs generation)? The distinction breaks down for semi-stable reference information.

**Recommendation:** Clarify with concrete criteria:
- Facts: Information that must appear in or directly influence the output (e.g., specific names, numbers, quotes to include)
- Context: Background information that shapes how the task is approached but may not appear verbatim (e.g., audience profile, company policies)

---

### Issue 2: Insight's Relationship to Iteration is Unclear

**Current description:** "Discoveries made during editing that need to be translated into further information for the intent."

**Problems:**
1. "During editing" — editing what? The Intent, Prompt, or Output?
2. "Translated into further information" — what does this mean operationally? Does the Insight become a Fact? A Constraint?
3. The lifecycle is missing: Does an Insight remain after being "translated," or is it consumed/archived?

**Recommendation:** Define:
- When Insights are created (e.g., "when reviewing Output against expectations")
- How Insights are resolved (e.g., "by updating Intent properties or creating new Facts")
- Whether resolved Insights are retained for history or archived

---

### Issue 3: No Expected vs. Actual Output Distinction

**Problem:** The task-research doc references "before/after comparison" and "expected output." The model has:
- `Intent.output_format` and `output_structure` (specification)
- `Output.content` (actual result)

But there's no way to store an expected/ideal output example distinct from the specification.

**Recommendation:** Consider adding:
- `Intent.output_example` (optional string): A concrete example of what a good output looks like
- Or clarify that `Intent.output_structure` can contain examples

---

### Issue 4: Constraints is a Single String

**Problem:** Real-world constraints have multiple dimensions:
- Format constraints (word count, structure)
- Content constraints (tone, excluded topics)
- Quality constraints (accuracy requirements)
- Negative constraints (what to avoid)

A single string conflates these.

**Recommendation:** Either:
- Make `constraints` a structured type (list or object with categories)
- Add guidance that constraints should follow a specific format (e.g., bullet list)
- Add separate properties: `format_constraints`, `content_constraints`, etc.

---

### Issue 5: output_format vs. output_structure Overlap

**Current descriptions:**
- `output_format`: "technical representation or encoding (e.g., JSON, XML, CSV, plain text, Markdown, HTML)"
- `output_structure`: "organization and composition of the result's content, independent of its technical format"

**Problem:** The examples given for `output_structure` ("bullet points vs. paragraphs, table with specific columns") are often format-dependent. A "table with specific columns" is meaningful in Markdown but different in JSON. The "independence" claim is questionable.

**Recommendation:** Clarify the relationship:
- `output_format` determines the serialization (how it's encoded)
- `output_structure` is a template or schema within that format (what the content contains)
- Provide examples showing the same structure in different formats

---

### Issue 6: Intent Reusability vs. Instance Not Modeled

**Current description:** "The intent is most often used on multiple instances and situations. It is not a one-off."

**Problem:** If Intent is reusable across situations, how is each "use" represented? The model has:
- `Intent` → `Prompt` → `Output`

But if the same Intent (e.g., "Draft customer complaint response") is used 50 times, each with different Facts/Context, how is this structured? Does each use create new Facts, or does the Intent maintain stable Facts?

**Recommendation:** Clarify:
- Are Facts shared across all uses of an Intent, or scoped to individual executions?
- Should there be an "Execution" or "Run" entity that captures a specific use of an Intent?

---

### Issue 7: No User/Ownership Model

**Problem:** The task-research doc implies tasks are personal ("I tried to..."). The domain model has no user association.

**Recommendation:** If Intents are personal or have access control, this should be explicit in the domain model (even if implementation details are elsewhere).

---

### Issue 8: Intent.name Lacks Guidance

**Current description:** Simply "name of the intent"

**Problem:** No guidance on:
- Naming conventions (verb phrase? noun phrase?)
- Length expectations (short label vs. descriptive title?)
- Relationship to description (summary of description? distinct concept?)

**Recommendation:** Add examples and guidance for naming, e.g., "A short, action-oriented label (e.g., 'Draft Customer Complaint Response')"

---

## Part 3: Summary Tables

### Mapping Summary

| Status | Count | Information Elements |
|--------|-------|---------------------|
| ✅ Fully Mappable | 12 | Task descriptions, prompts, outputs, categories, format requirements |
| ⚠️ Partially Mappable | 13 | Examples (Fact vs Context unclear), constraints (single string), exclusions, iterations |
| ❌ Not Mappable | 7 | Source URLs, niche classification, quality heuristics, screenshots, distribution requirements |

### Intuitiveness Distribution

| Level | Count | Description |
|-------|-------|-------------|
| High (obvious, direct match) | 9 | Intent.description, Prompt.content, Output.content |
| Medium (requires interpretation) | 8 | output_format vs structure split, constraints as string |
| Low (awkward or unclear fit) | 8 | Fact vs Context, Insight for failures, negative constraints |
| N/A (not mappable) | 7 | Research metadata |

### Domain Precision Issues Identified

| Issue | Severity | Impact |
|-------|----------|--------|
| Fact vs Context boundary fuzzy | High | Users won't know where to put information |
| Insight lifecycle undefined | Medium | Unclear how iteration workflow operates |
| No expected output concept | Medium | Can't represent success criteria examples |
| Constraints is single string | Medium | Loses structure of multi-dimensional constraints |
| Intent reuse model unclear | High | Core concept ambiguity |
| output_format vs output_structure overlap | Low | Potential confusion, minor impact |
| Intent.name lacks guidance | Low | Inconsistent naming likely |
| No user model | Low | May be intentional, depends on scope |

---

## Recommendations

### For the Domain Model

1. **Clarify Fact vs Context** with concrete decision criteria and examples
2. **Define Insight lifecycle** — creation trigger, resolution process, retention policy
3. **Consider adding `expected_output_example`** to Intent or clarifying output_structure can contain examples
4. **Document constraints format guidance** or restructure into categories
5. **Clarify Intent reuse** — single Intent with varying Facts per execution, or Intent templates?
6. **Add Intent.name guidance** with examples and conventions

### For This Mapping Exercise

The core business task information (what, how, constraints, output) maps well. Research metadata (sources, classification) does not map, which is appropriate if the domain model is purely about Intent execution rather than Intent discovery/curation.

The main friction points are:
1. Determining whether information is a Fact or Context
2. Representing complex multi-part constraints
3. Capturing "what went wrong" insights vs. "what to do" improvements
4. Modeling expected vs. actual outputs for comparison
