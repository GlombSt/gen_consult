# Task Entity

## What is a Task?

**A Task is the executable unit of work** that the reference framework describes how to complete successfully.

---

## Task Definition

```
Task = Goal + Method + Scope
```

**Task is NOT:**
- Just a goal ("improve SEO")
- Just a method ("use keyword research")
- Just an output ("create keyword list")

**Task IS:**
- A complete executable description: "Discover long-tail keywords for SEO content strategy"

---

## Task Anatomy

### Core Elements

| Element | Description | Example |
|---------|-------------|---------|
| **Verb** | The action being performed | Discover, Create, Analyze, Transform |
| **Object** | What is being acted upon | Keywords, Document, Plan, Report |
| **Qualifier** | Specificity/constraint | Long-tail, Privacy-preserving, Comprehensive |
| **Purpose** | Why/what for | For SEO, For compliance, For decision-making |
| **Context** | Domain/situation | In healthcare, For B2B SaaS, In German JVA |

### Task Statement Formula

```
[Verb] + [Qualifier] + [Object] + [Purpose] + [Context]

Examples:
- Discover long-tail keywords for SEO content for B2B SaaS
- Create privacy-preserving query transformation for customer support
- Generate comprehensive Vollzugsplan for prisoner in JVA Baden-Württemberg
- Analyze customer support tickets to identify product issues
```

---

## Task Characteristics

### 1. Bounded
Has clear start and end
- ✓ "Create keyword list" (ends when list complete)
- ✗ "Do SEO" (never-ending)

### 2. Executable
Can actually be performed
- ✓ "Analyze 100 support tickets"
- ✗ "Understand customers" (too vague)

### 3. Measurable
Success can be determined
- ✓ "Generate 50 qualified keywords"
- ✗ "Make good keywords" (what's "good"?)

### 4. Requires Judgment
Not purely mechanical
- ✓ "Select target keywords considering competition" (judgment needed)
- ✗ "Sort keywords alphabetically" (mechanical)

---

## Task vs Related Concepts

### Task vs Goal

| Task | Goal |
|------|------|
| Executable action | Desired outcome |
| "Create SEO content plan" | "Increase organic traffic" |
| How you work | What you achieve |
| Time-bound | Ongoing |

### Task vs Process

| Task | Process |
|------|---------|
| Single unit of work | Multiple tasks |
| "Write blog post" | "Content marketing" |
| Has one output | Has multiple outputs |
| Hours/days | Weeks/months |

### Task vs Activity

| Task | Activity |
|------|----------|
| Specific, bounded | General, ongoing |
| "Research 5 competitors" | "Market research" |
| Completable | Continuous |
| Creates artifact | Creates knowledge |

---

## Task Scope Levels

### Atomic Task (Too Small)
**Problem:** Not enough complexity to warrant framework

**Examples:**
- "Google one keyword"
- "Copy text to clipboard"
- "Send one email"

**Indicator:** Can be done in <5 minutes with no decisions

---

### Well-Scoped Task (Ideal)
**Sweet spot:** Requires decisions, has inputs/outputs, can fail if done wrong

**Examples:**
- "Discover long-tail keywords for SEO"
- "Create Vollzugsplan for prisoner"
- "Analyze quarterly support tickets"

**Indicator:** Takes hours to days, requires expertise, multiple valid approaches

---

### Project-Level Task (Too Large)
**Problem:** Actually multiple tasks combined

**Examples:**
- "Launch complete SEO strategy" (many tasks)
- "Redesign customer support system" (many tasks)
- "Build content marketing operation" (many tasks)

**Indicator:** Takes weeks/months, needs to be broken down

**Fix:** Split into component tasks:
- "Launch SEO strategy" →
  - Task 1: "Discover target keywords"
  - Task 2: "Create content calendar"
  - Task 3: "Optimize existing pages"

---

## Task Types (Domain-Independent)

### By Primary Action

**Information Extraction**
- Extract structured data from unstructured sources
- Examples: Analyze support tickets, Extract contract terms, Parse resumes

**Content Generation**
- Create new content based on requirements
- Examples: Write blog posts, Generate reports, Create presentations

**Transformation**
- Convert input from one form to another
- Examples: Translate text, Reformat data, Anonymize content

**Classification**
- Categorize inputs into defined groups
- Examples: Prioritize tickets, Tag content, Route inquiries

**Analysis**
- Examine data to derive insights
- Examples: Competitive analysis, Trend identification, Performance review

**Planning**
- Design approach or sequence for future work
- Examples: Content calendar, Project plan, Vollzugsplan

**Decision Support**
- Provide information/recommendations for decisions
- Examples: Vendor comparison, Investment analysis, Risk assessment

---

## Task Complexity Factors

### What Makes a Task Complex?

**1. Decision Count**
- Simple: 1-3 decisions
- Medium: 4-8 decisions
- Complex: 9+ decisions

**2. Constraint Types**
- Simple: Generic constraints (time, quality)
- Medium: Domain-specific constraints (industry standards)
- Complex: Multiple conflicting constraints (legal + technical + business)

**3. Context Requirements**
- Simple: Common knowledge sufficient
- Medium: Domain expertise helpful
- Complex: Specialized expertise required

**4. Failure Impact**
- Low: Easy to recover, low cost
- Medium: Rework needed, moderate cost
- High: Irreversible, severe consequences

**5. Stakeholder Count**
- Simple: Self or single stakeholder
- Medium: 2-3 stakeholders with aligned interests
- Complex: Multiple stakeholders with conflicting needs

---

## Task Data Model

```python
class Task:
    """The work to be done"""
    
    # Core identification
    id: str
    name: str  # "SEO keyword discovery"
    description: str  # Full explanation
    
    # Classification
    primary_action: str  # "extraction", "generation", "transformation", etc.
    domain: str  # "marketing", "legal", "healthcare"
    complexity: str  # "simple", "medium", "complex"
    jurisdiction: str # "Germany", "uk", "Bade Württemberg"
    
    # Execution parameters
    typical_duration: str  # "2-4 hours"
    required_expertise: str  # "beginner", "intermediate", "expert"
    can_be_automated: bool
    automation_difficulty: str  # If can be automated
    
    # What defines this task
    reference: TaskReference  # The full framework
    
    # Meta
    tags: List[str]  # For searchability
    similar_tasks: List[str]  # Related task IDs
    parent_process: Optional[str]  # If part of larger process
```

---

## Task Statement Quality

### Poor Task Statements

**Too Vague:**
- "Help with marketing" → What specifically?
- "Improve website" → Improve how?
- "Work on content" → What kind of work?

**Too Broad:**
- "Build content strategy" → Needs decomposition
- "Fix all SEO issues" → Too many sub-tasks
- "Transform business" → Not a task

**Missing Context:**
- "Create keywords" → For what? For whom?
- "Write document" → What type? What purpose?
- "Do research" → Research what? For what goal?

### Good Task Statements

**Clear & Bounded:**
- "Discover 50 long-tail keywords for B2B SaaS blog content"
- "Create privacy-safe reformulation of customer support queries"
- "Generate 6-month content calendar for organic social media"

**Characteristics:**
- Specific verb
- Measurable output
- Clear context
- Appropriate scope
- Implies decisions exist

---

## Task Discovery Questions

### To Help Users Define Their Task

**What questions help clarify the task:**

1. **Verb:** What action are you trying to perform?
   - Analyze? Create? Transform? Decide?

2. **Object:** What are you working on/with?
   - Documents? Data? People? Systems?

3. **Output:** What will exist when you're done?
   - A list? A plan? A decision? A document?

4. **Success:** How will you know it worked?
   - Metrics? Feedback? Compliance? Approval?

5. **Scope:** How big is this?
   - Hours? Days? Weeks? (If weeks → probably multiple tasks)

6. **Frequency:** How often does this happen?
   - One-time? Monthly? Ongoing? (Ongoing → might be process not task)

---

## Task Validation Checklist

**Before creating a reference framework, verify the task is:**

- [ ] **Specific enough** - Can describe what "done" looks like
- [ ] **Bounded enough** - Has clear start and end
- [ ] **Complex enough** - Requires decisions and judgment
- [ ] **Not too large** - Can complete in days not weeks
- [ ] **Executable** - Someone could actually do this
- [ ] **Measurable** - Success is determinable
- [ ] **Value-creating** - Produces useful output
- [ ] **Domain-appropriate** - Right level of abstraction for domain

---

## Examples by Domain

### Marketing
- Discover long-tail keywords for content strategy
- Create social media content calendar for Q2
- Analyze competitor positioning for new product launch
- Generate email campaign for product announcement

### Legal/Compliance
- Create Vollzugsplan for incoming prisoner (Baden-Württemberg)
- Review contract for GDPR compliance issues
- Generate privacy policy for new mobile app
- Assess regulatory risk for new business model

### Customer Support
- Analyze support tickets to identify top 5 product issues
- Create FAQ content from common customer questions
- Classify and route incoming support requests
- Generate response templates for common scenarios

### Software Development
- Analyze codebase for security vulnerabilities
- Create API documentation from code comments
- Generate test cases for new feature
- Review pull request for code quality issues

### HR/Recruiting
- Screen resumes for qualified candidates
- Create job description for senior role
- Generate interview guide for technical position
- Analyze employee feedback for engagement insights


---

## Summary

**A Task is:**
- A bounded unit of executable work
- Requires judgment and decisions
- Produces measurable output
- Complex enough to benefit from a reference framework
- Small enough to complete in reasonable time

**SharpIntent helps with tasks that:**
- Have multiple valid approaches
- Require domain knowledge
- Can fail if done incorrectly
- Benefit from structured thinking
- Need documentation for repeatability
