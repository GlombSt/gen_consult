# SharpIntent Reference Data Model

## Entity Summary

| Entity | Description | Example |
|--------|-------------|---------|
| **Task** | The executable unit of work the reference describes how to complete successfully. | "Create keyword research report" |

| **TaskReference** | Complete knowledge structure for executing a task (holds all inputs, outputs, decisions, context, constraints, success criteria, failure modes). | Full reference for "Create keyword research report" |

| **Input** | What the task operates on — data, documents, or information. | Customer support tickets, list of competitor URLs |
| **Output** | What the task produces. | Privacy-safe reformulated query, keyword report |

| **Decision** | A choice that must be made to execute the task. | Keyword scope (narrow vs. broad), privacy level (strict vs. minimal) |

| **ContextRequirement** | Knowledge or information needed to execute the task well. | Understanding of target audience, knowledge of GDPR requirements |

| **Constraint** | Boundaries or limits on how the task may be executed. | Must comply with GDPR, max budget €5,000 |

| **Assumption** | A belief we're operating under that, if false, invalidates the approach. | "Target audience searches primarily in English" |


| **SuccessCriterion** | How to measure whether the task was done well. | "All keywords have search volume data" |
| **FailureMode** | A common way the task goes wrong. | "Keywords chosen are too generic, no traffic" |

| **InputSource** | Where or how to obtain an input. | Export from CRM, competitor site crawl |

| **TradeOffs** | What you gain or lose with a decision option. | "Faster but less accurate" |
| **BestPractice** | Domain wisdom for a decision option. | "Start narrow, expand after validation" |

| **RecommendationRule** | Conditional logic for suggesting options. | "If B2B → recommend long-tail keywords" |

| **HelperQuestion** | A quiz-style question to guide decision-making. | "What is your primary goal: traffic or conversions?" |
| **AcquisitionMethod** | A specific way to obtain context or knowledge. | Industry report, expert interview, web search |

---

# Task Entity

## What is a Task?

**A Task is the executable unit of work** that the reference framework describes how to complete successfully.

---

## Task Definition

Task = Goal + Method + Scope


## Core Entity: TaskReference
Complete knowledge structure for executing a task successfully.

**Contains:**
- Inputs: What you need to start
- Outputs: What you produce
- Decisions: Choices that must be made
- Context: Knowledge/information required
- Constraints: Boundaries that cannot be crossed
- Assumptions: Beliefs that, if false, invalidate the approach
- Success Criteria: How to measure success
- Failure Modes: Common ways tasks go wrong

---

## Input
What the task operates on (data, documents, information).

**Key fields:**
- `name`, `type`, `required`
- `recommendations`: How to obtain/provide good input
- `quality_requirements`: Standards for acceptable input
- `examples`: Concrete instances

**Recommendations include:**
- Preferred sources (where to get it)
- Pitfalls (common mistakes)
- Quality checks (validation)
- Fallback strategies (alternatives if unavailable)

---

## Output
What the task produces.

**Key fields:**
- `name`, `format`, `schema`
- `consumed_by`: Who/what uses this output
- `delivery_requirements`: How it must be delivered
- `examples`: Concrete instances

---

## Decision
A choice that must be made to execute the task.

**Key fields:**
- `question`: What must be decided?
- `why_matters`: Impact of this decision
- `options`: Possible choices (2-4 typically)
- `recommendation_logic`: How to suggest best option

**Each option includes:**
- `trade_offs`: Advantages/disadvantages
- `when_to_choose`: Conditions favoring this option
- `best_practices`: Domain wisdom
- `popularity`: What % of users choose this
- `suitable_for`: Beginner/intermediate/expert

**Recommendations driven by:**
- Rules (if X then recommend Y)
- Helper questions (quiz to guide user)
- Default option with reasoning

---

## ContextRequirement
Knowledge/information needed to execute task well.

**Key fields:**
- `name`, `why_needed`, `required`
- `how_to_obtain`: Acquisition guidance
- `absence_impact`: What happens without it

**Acquisition guidance includes:**
- Multiple methods (ranked by effort/quality)
- Step-by-step instructions
- Tools needed, time required
- Validation questions (do you have enough?)

---

## Constraint
Boundaries/limits on execution.

**Key fields:**
- `type`: Legal, technical, business, ethical
- `description`: What's the limit?
- `why_exists`: Reason for constraint
- `how_to_satisfy`: How to comply
- `violation_consequence`: What happens if violated
- `flexibility`: Hard (never) vs soft (trade-off)

---

## SuccessCriterion
How to measure if task was done well.

**Key fields:**
- `metric`: Measurable outcome
- `measurement_method`: How to measure
- `minimum_threshold`: Acceptable baseline
- `priority`: Critical/important/nice-to-have
- `conflicts_with`: Other criteria that can't both be optimized

---

## FailureMode
Common ways the task goes wrong.

**Key fields:**
- `what_goes_wrong`: Specific bad outcome
- `why_it_happens`: Root cause
- `how_to_detect`: Early warning signs
- `how_to_prevent`: Mitigation strategy
- `recovery_strategy`: What to do if it happens
- `frequency`: Common/occasional/rare

---

## Assumption
A belief we're operating under that, if false, invalidates the approach.

**Key fields:**
- `statement`: The assumption being made (e.g. "Target audience searches primarily in English")
- `criticality`: How important — critical / important / minor
- `impact_if_false`: What happens if this isn't true?

**Validation:**
- `how_to_verify`: Method to check (e.g. "Check Google Analytics language data")
- `verification_effort`: Time required (e.g. "5 minutes", "1 hour", "ongoing")

**Confidence:**
- `confidence`: 0–1, how sure are we this is true?
- `common_mistake`: Is this a frequently wrong assumption?

**Fallback:**
- `alternative_if_false`: Different approach needed if assumption doesn't hold

**Dependencies:**
- `affects`: Which decisions/constraints depend on this assumption?

**Source:**
- `based_on`: Origin of the assumption — "Industry standard", "Past experience", "Unstated belief"

---

## Supporting Structures

### InputSource
Where/how to obtain an input.
- `method`, `effort`, `reliability`, `cost`
- `when_to_use`, `instructions`

### TradeOffs
What you gain/lose with a decision option.
- `advantages`, `disadvantages`
- `cost_implications`, `time_implications`

### BestPractice
Domain wisdom for a decision option.
- `practice`, `source`, `confidence`, `context`

### RecommendationRule
Conditional logic for suggesting options.
- `condition`, `recommended_option`, `reasoning`, `confidence`

### HelperQuestion
Quiz question to guide decision-making.
- `question`, `answers` (each points to an option)

### AcquisitionMethod
Specific way to obtain context/knowledge.
- `method`, `steps`, `tools_needed`, `time_required`
- `difficulty`, `output_quality`, `best_for`

---

## Key Design Principles

1. **Decisions ≠ form fields** - Captures thinking required, not just data
2. **Context explains why** - Every requirement justified
3. **Recommendations are actionable** - Step-by-step, not vague advice
4. **Trade-offs are explicit** - No option is purely good/bad
5. **Failures are preventable** - Learn from common mistakes upfront
6. **Works for human or machine** - Structure supports both execution modes



## Distinguishing Core Entities

### The Key Question Each Answers

| Entity     | Core Question              | Nature                  |
|------------|----------------------------|-------------------------|
| Input      | What am I working WITH?    | Material/Data           |
| Context    | What do I need to KNOW?    | Knowledge/Understanding |
| Decision   | What must I CHOOSE?        | Choice/Strategy         |
| Constraint | What CAN'T I do?           | Boundary/Limit          |
| Assumption | What am I BELIEVING?       | Unstated belief/risk    |

### Detailed Distinctions

#### INPUT

- **What it is:** The raw material you process or operate on
- **Test:** Can you point to it? Does it exist as data/documents/information?
- **Examples:**
  - ✓ Customer support tickets (you read these)
  - ✓ Prisoner profile data (you use this)
  - ✓ List of competitor URLs (you analyze these)
  - ✗ "Knowledge of SEO" (this is context, not input)
  - ✗ "Must comply with GDPR" (this is constraint)
- **Key characteristic:** Consumed or transformed by the task

#### CONTEXT

- **What it is:** Background knowledge, understanding, or information that guides execution but isn't directly processed
- **Test:** Do you need to understand/know this to do the task well, but don't directly manipulate it?
- **Examples:**
  - ✓ Understanding of target audience behavior
  - ✓ Knowledge of industry best practices
  - ✓ Awareness of competitive landscape
  - ✓ Familiarity with legal requirements
  - ✗ The actual law document (that would be input if you read it)
  - ✗ Customer data (that's input you analyze)
- **Key characteristic:** Informs judgment and choices, not transformed

#### DECISION

- **What it is:** A choice between 2+ options that shapes how the task is executed
- **Test:** Could two people do this task differently based on different choices here?
- **Examples:**
  - ✓ How broad should keyword scope be? (narrow vs. broad)
  - ✓ Which privacy level to apply? (strict vs. balanced vs. minimal)
  - ✓ What content format to create? (blog vs. video vs. infographic)
  - ✗ "Need customer data" (that's input, not a choice)
  - ✗ "Must not violate GDPR" (that's constraint, no choice)
- **Key characteristic:** Has multiple valid options, each with different trade-offs

#### CONSTRAINT

- **What it is:** A non-negotiable boundary or limit on how the task can be executed
- **Test:** Is violating this unacceptable or very costly? Is there really no choice?
- **Examples:**
  - ✓ Must comply with GDPR (legal requirement)
  - ✓ Budget limit of €5,000 (resource limit)
  - ✓ Must complete within 3 months (time limit)
  - ✓ Cannot access customer financial data (access restriction)
  - ✗ "Should we prioritize speed or accuracy?" (that's a decision)
  - ✗ "Understanding of regulations" (that's context)
- **Key characteristic:** Eliminates options, not a choice to be made

#### ASSUMPTION

- **What it is:** A belief we're operating under that, if false, invalidates the approach
- **Test:** If this turned out to be wrong, would we need to significantly change our approach?
- **Examples:**
  - ✓ "Target audience searches primarily in English"
  - ✓ "Users have basic technical literacy"
  - ✓ "Budget will remain stable for 6 months"
  - ✓ "Competitor pricing data is accurate"
  - ✗ "Must comply with GDPR" (that's a constraint, not an assumption)
  - ✗ "Understanding of audience behavior" (that's context)
- **Key characteristic:** If false, requires rethinking the approach; often unstated

### Disambiguation Examples

#### Example 1: "Customer data"

- **As Input:** ✓  
  The actual CSV file of customer records. Used: You analyze it to find patterns.
- **As Context:** ✗  
  Doesn't fit — if you have the data, it's input.
- **As Decision:** ✗  
  Having data isn't a choice.
- **As Constraint:** Maybe  
  "Cannot access customer financial data" = constraint. But the data itself isn't the constraint.

#### Example 2: "GDPR compliance"

- **As Input:** ✗  
  GDPR regulation document could be input if you read it. But "compliance" itself isn't input.
- **As Context:** ✓  
  "Knowledge of GDPR requirements" = context. Understanding what GDPR requires.
- **As Decision:** ✗  
  Not a choice — you must comply.
- **As Constraint:** ✓  
  "Must comply with GDPR" = constraint. Sets boundary on what you can do.

**Resolution: Same topic, different aspects**

- Context: Understanding what GDPR requires
- Constraint: Must not violate GDPR rules

#### Example 3: "Target audience demographics"

- **As Input:** ✓  
  Demographic data file (age, location, income). Used: You analyze to inform keyword selection.
- **As Context:** ✓  
  Understanding of audience behavior/preferences. Knowledge of how they search.
- **As Decision:** ✗  
  Having demographics isn't a choice.
- **As Constraint:** ✗  
  Demographics don't limit what you can do.

**Resolution: Can be both!**

- Input: The data itself
- Context: Your understanding/interpretation of it

#### Example 4: "Budget for content creation"

- **As Input:** ✗  
  Budget isn't data you process.
- **As Context:** ✓  
  Knowing your budget informs choices.
- **As Decision:** Maybe  
  "How much to spend?" = decision. But once decided, becomes context.
- **As Constraint:** ✓  
  "Maximum budget: €5,000" = constraint. Hard limit on what's possible.

**Resolution:**

- Constraint: The limit itself
- Context: Awareness of that limit when planning
- Decision: How to allocate within that limit

#### Example 5: "Target audience uses Google"

- **As Input:** ✗  
  Not data you process.
- **As Context:** ✗  
  Not knowledge you apply — it's something you believe to be true.
- **As Decision:** ✗  
  Not a choice you're making.
- **As Constraint:** ✗  
  Doesn't limit what you can do.
- **As Assumption:** ✓  
  A belief that, if false (e.g. audience uses Bing or Baidu), invalidates your SEO approach.

**Resolution:**

- Assumption: "Target audience primarily uses Google for search"
- If false: Need to rethink keyword research strategy for different search engines

### The Relationship Flow

```
ASSUMPTION (if false, rethink everything below)
    ↓
CONSTRAINT
    ↓ (eliminates options)
DECISION
    ↓ (made using)
CONTEXT
    ↓ (applied to)
INPUT
    ↓ (produces)
OUTPUT
```

**Example flow:**

- Assumption: Target audience searches in English
- Constraint: Must comply with GDPR
- Decision: Choose strict privacy (not just minimum compliance)
- Context: Understanding of what constitutes PII in EU
- Input: User query with potential PII
- Output: Privacy-safe reformulated query

### Edge Cases & Rules

When something seems like multiple entities:

**Rule 1: If it's both data AND knowledge**

- Data aspect → Input
- Knowledge aspect → Context
- *Example: "Competitor analysis"* — Input: List of competitor URLs; Context: Understanding of competitive dynamics

**Rule 2: If it limits AND requires choice**

- Hard limit → Constraint
- Choice within limit → Decision
- *Example: "Budget management"* — Constraint: "Max €5,000"; Decision: "Spend €3k on content vs. €2k on promotion?"

**Rule 3: If it's both required AND a choice**

- Whether to obtain it → Decision
- The thing itself → Input or Context
- *Example: "Customer interviews"* — Decision: "Should we interview customers?"; Input: Interview transcripts (once obtained); Context: Insights learned from interviews

**Rule 4: If it's a belief that could be wrong**

- Known hard limit → Constraint
- Believed to be true but could be wrong → Assumption
- *Example: "Audience language"* — Constraint: "Content must be in English" (explicit requirement); Assumption: "Audience prefers English" (belief that could be false)

**When to split vs. combine:**

- **Split when:** Different aspects serve different purposes  
  e.g. "Market data" → Input (the data) + Context (understanding trends)
- **Combine when:** Inseparable in practice  
  e.g. "Legal compliance" as single Constraint, not split into "law" (context) and "can't violate" (constraint)

### Quick Decision Tree

```
Is it something that exists as data/documents?
├─ YES → INPUT
└─ NO ↓

Is it knowledge/understanding needed?
├─ YES → CONTEXT
└─ NO ↓

Does it eliminate options (no choice)?
├─ YES → CONSTRAINT
└─ NO ↓

Does it require choosing between options?
├─ YES → DECISION
└─ NO ↓

Is it a belief that, if false, would require rethinking?
├─ YES → ASSUMPTION
└─ NO → Something else (maybe Success Criteria or Failure Mode)
```

### Summary Table

| What          | Input                    | Context                  | Decision      | Constraint    | Assumption              |
|---------------|--------------------------|--------------------------|---------------|---------------|-------------------------|
| Form          | Data, documents, files   | Knowledge, understanding | Choice, option| Limit, boundary | Belief, premise        |
| Verb          | Process, analyze, use     | Know, understand         | Choose, decide| Must/cannot   | Assume, believe         |
| Question      | What data exists?        | What do I know?          | What do I choose? | What's forbidden? | What am I believing?   |
| Action        | Consumed/transformed      | Informs judgment         | Shapes approach | Eliminates options | Risks invalidation   |
| Example       | Customer tickets          | SEO best practices       | Keyword scope | GDPR compliance | "Audience speaks English" |
| Tangible?     | Yes (can point to it)     | No (in your head)        | No (a choice) | No (a rule)   | No (a belief)           |
| Changes task? | No (input is given)       | Yes (knowledge matters)  | Yes (choice matters) | Yes (limits what's possible) | Yes (if false, rethink) |



