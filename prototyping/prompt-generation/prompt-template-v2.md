# SharpIntent Prompt Template v2
## Informed by GEPA (Genetic-Pareto Prompt Optimizer) Research

This template structure is derived from analyzing how prompts evolve through reflective optimization. The patterns come from the GEPA paper (arXiv:2507.19457) which demonstrated that well-structured prompts with explicit guidance outperform vague instructions.

---

## Template Structure

A sharpened intent translates into a prompt with these sections:

```
┌─────────────────────────────────────────┐
│ 1. TASK OVERVIEW                        │ ← From: Task entity
├─────────────────────────────────────────┤
│ 2. INPUT FORMAT                         │ ← From: Inputs entity
├─────────────────────────────────────────┤
│ 3. OUTPUT FORMAT                        │ ← From: Quality entity
├─────────────────────────────────────────┤
│ 4. KEY REQUIREMENTS & APPROACH          │ ← From: Choices entity
├─────────────────────────────────────────┤
│ 5. DOMAIN-SPECIFIC GUIDANCE             │ ← From: Assumptions entity
├─────────────────────────────────────────┤
│ 6. COMMON PITFALLS TO AVOID             │ ← From: Pitfalls entity
├─────────────────────────────────────────┤
│ 7. EXAMPLE FORMAT (optional)            │ ← Concrete demonstration
└─────────────────────────────────────────┘
```

---

## Section-by-Section Guidance

### 1. TASK OVERVIEW
**Source:** Task entity (sharpened goal)

**What GEPA-optimized prompts do:**
- State the task in one clear sentence
- Explain the broader context/purpose
- Specify what success looks like at a high level

**Template:**
```
## Task Overview

You are given [input description]. Your objective is to [core action] 
that [outcome/purpose].

The result must [key success criterion] while [key constraint].
```

**Example (from GEPA's PUPA prompt):**
> "You receive a user query that may contain sensitive, private, or personally 
> identifiable information (PII). Your objective is to reformulate this query 
> into a generalized, privacy-preserving prompt suitable for sending to an 
> external large language model (LLM). The reformulated prompt must enable 
> the external LLM to fulfill the user's original intent effectively while 
> rigorously protecting all user privacy."

---

### 2. INPUT FORMAT
**Source:** Inputs entity

**What GEPA-optimized prompts do:**
- Explicitly describe what the input contains
- Flag what might be present that needs handling
- Set expectations for input variability

**Template:**
```
## Input Format

- [Field 1]: [Description of what it contains]
- [Field 2]: [Description of what it contains]

The input might contain:
- [Variation 1 that needs specific handling]
- [Variation 2 that needs specific handling]
```

**Example (from GEPA's HotpotQA prompt):**
> "**Input Understanding:**
> - 'question' is the original multi-hop question posed by the user.
> - 'summary_1' is a concise summary of information from a document 
>   retrieved in the first hop, which partially addresses the question."

---

### 3. OUTPUT FORMAT
**Source:** Quality entity (success criteria)

**What GEPA-optimized prompts do:**
- Specify exact structure expected
- Define what each output part should contain
- Give concrete format examples

**Template:**
```
## Output Format

Your output must include:

**Part (a) [Name]:**
[What this part contains and its purpose]

**Part (b) [Name]:**
[What this part contains and its purpose]

Format requirements:
- [Structural requirement 1]
- [Structural requirement 2]
```

**Example (from GEPA's PUPA prompt):**
> "**Output Format:**
> - Part (a) Reasoning: Provide a concise paragraph that explains how you 
>   identified sensitive information, what strategies you applied to protect 
>   privacy, and how the reformulated prompt preserves the original intent.
> - Part (b) LLM Request: A concise, carefully constructed privacy-safe prompt 
>   that removes or anonymizes all PII and proprietary details."

---

### 4. KEY REQUIREMENTS & APPROACH
**Source:** Choices entity (decisions made explicit)

**What GEPA-optimized prompts do:**
- Number each requirement explicitly
- Provide rationale for why each matters
- Include practical "how to" strategies

**Template:**
```
## Key Requirements

1. **[Requirement Name]:**
   - [What to do]
   - [Why it matters]
   - [How to achieve it]

2. **[Requirement Name]:**
   - [What to do]
   - [Why it matters]
   - [How to achieve it]

### Practical Strategy

- [Step-by-step approach]
- [Decision points and how to handle them]
```

**Example (from GEPA's HoVer prompt):**
> "**Key Requirements:**
> 1. **Target Missing Evidence**: Identify and explicitly ask about the 
>    unverified or unconfirmed details in the summary that are critical 
>    to the claim.
> 2. **Correct Historical/Domain-Specific Anomalies**: Address discrepancies 
>    like anachronisms or misattributions.
> 3. **Link to Summary Context**: Ensure the query references the summary's 
>    key points."

---

### 5. DOMAIN-SPECIFIC GUIDANCE
**Source:** Assumptions entity (what the executor needs to know)

**What GEPA-optimized prompts do:**
- Include niche factual information
- Specify domain conventions and terminology
- Note exceptions and special cases

**Template:**
```
## Domain-Specific Guidance

**[Domain Area 1]:**
- [Specific guidance]
- [Technical detail that matters]
- [Exception or special case]

**[Domain Area 2]:**
- [Specific guidance]
- [Why this domain works differently]
```

**Example (from GEPA's IFBench prompt):**
> "**Domain-Specific Guidance:**
> - **Names and nicknames:** Provide only the specific nickname or name 
>   when asked, without extra phrasing.
> - **Nationality and identity distinctions:** Use the most precise terms 
>   aligned with factual correctness (e.g., English vs. British).
> - **Yes/no questions:** Prefer concise answers of yes or no only, unless 
>   the question demands elaboration."

---

### 6. COMMON PITFALLS TO AVOID
**Source:** Pitfalls entity

**What GEPA-optimized prompts do:**
- List specific failure modes
- Explain what goes wrong and why
- Provide the correct alternative

**Template:**
```
## Common Pitfalls to Avoid

- **Do not** [specific mistake]. Instead, [correct approach].
- **Do not** [specific mistake]. This causes [problem]. Instead, [correct approach].
- **Avoid** [pattern that seems right but isn't]. [Why it fails].
```

**Example (from GEPA's PUPA prompt):**
> "**Common Pitfalls to Avoid:**
> - Do not merely lightly obscure or partially redact sensitive details; 
>   full anonymization or abstraction is required.
> - Do not repeat any user-supplied PII or proprietary content verbatim.
> - Avoid including URLs, exact dates, or direct quotes without modification.
> - Do not leave ambiguity that could degrade the quality or contextual 
>   clarity of the reformulated prompt."

---

### 7. EXAMPLE FORMAT (Optional)
**Source:** Derived from all entities

**What GEPA-optimized prompts do:**
- Show concrete input → output examples
- Demonstrate the reasoning process
- Illustrate edge cases

**Template:**
```
## Example

**Input:**
[Example input]

**Output:**
[Example output showing correct format]

**Why this works:**
[Brief explanation of what makes this example correct]
```

---

## Complete Template

```markdown
# [Task Name]

## Task Overview

[One sentence stating the core task]

[2-3 sentences on context, purpose, and high-level success criteria]

## Input Format

- **[Field 1]**: [Description]
- **[Field 2]**: [Description]

The input might contain [variations to handle].

## Output Format

Your output must include:

**Part (a) [Name]:** [What it contains]

**Part (b) [Name]:** [What it contains]

Format: [Structural requirements]

## Key Requirements

1. **[Requirement 1]**: [What + Why + How]
2. **[Requirement 2]**: [What + Why + How]
3. **[Requirement 3]**: [What + Why + How]

### Practical Strategy

- [Step 1]
- [Step 2]
- [Decision point and how to handle]

## Domain-Specific Guidance

**[Domain Area]:**
- [Specific detail that matters]
- [Convention or exception]

## Common Pitfalls to Avoid

- **Do not** [mistake]. Instead, [correct approach].
- **Avoid** [failure pattern]. [Why it fails].

## Example (Optional)

**Input:** [Example]
**Output:** [Example]
**Why this works:** [Explanation]
```

---

## Key Insights from GEPA Research

### Why structured prompts outperform vague ones:

1. **Explicit > Implicit**: Prompts that spell out requirements perform better than those assuming the model will "figure it out"

2. **Pitfalls are high-leverage**: Explicitly stating what NOT to do often improves results more than adding more "do" instructions

3. **Domain knowledge must be injected**: Models don't reliably apply domain expertise unless explicitly told

4. **Examples demonstrate format**: Showing the expected output structure reduces format errors significantly

5. **Reasoning sections improve accuracy**: Asking for explicit reasoning (like Part (a) in PUPA) helps the model think through the problem

### The evolution pattern:

GEPA's research shows prompts evolve from:

```
Simple: "Do X"
     ↓
Better: "Do X by following steps Y"
     ↓
Best: "Do X by following steps Y, avoiding pitfalls Z, 
      using domain knowledge W, producing format V"
```

The improvement comes from making implicit expectations explicit.

---

## Mapping to Iceberg Entities

| Entity | Prompt Section | What it contributes |
|--------|----------------|---------------------|
| **Task** | Task Overview | Core instruction, purpose, success definition |
| **Inputs** | Input Format | What's provided, variations to expect |
| **Choices** | Key Requirements | Decisions made explicit, approach specified |
| **Pitfalls** | Common Pitfalls | Failure modes to avoid, anti-patterns |
| **Quality** | Output Format | Structure, format, completeness criteria |
| **Assumptions** | Domain-Specific Guidance | Context the executor needs, exceptions |

The sharpening process surfaces content for each section. The prompt template structures it for effective execution.
