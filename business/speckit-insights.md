# Spec-Kit Insights: Applying Specification Clarification to Task-Driven AI

**Purpose**: This document distills insights from the spec-kit project and adapts them for building user-friendly task clarification systems for AI agents and chatbots.

**Target Audience**: UX designers and product teams building AI task interfaces for non-technical users.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Concepts from Spec-Kit](#core-concepts-from-spec-kit)
3. [The Clarification Framework](#the-clarification-framework)
4. [UX Approaches](#ux-approaches)
5. [Implementation Concepts](#implementation-concepts)
6. [Metrics & Success Criteria](#metrics--success-criteria)
7. [Quick Reference: Patterns](#quick-reference-patterns)

---

## Executive Summary

### The Problem

When users ask AI systems to perform tasks, they often provide **incomplete or ambiguous instructions**. This leads to:
- AI making wrong assumptions
- Users receiving incorrect outputs
- Multiple iterations to get the desired result
- Frustration and decreased trust

**Example**: "Create a report on acquisition performance for last 4 weeks"

This seems clear but is actually ambiguous:
- Which metrics? (count, cost, conversion rate, revenue?)
- What format? (dashboard, PDF, CSV, email?)
- What breakdown? (by channel, by campaign, by time period?)
- What if data is missing? (error, warning, estimate?)

### The Solution

Spec-kit (a GitHub specification-driven development toolkit) uses a **systematic clarification framework** that:
1. **Analyzes requests** against a taxonomy of dimensions
2. **Identifies gaps** in clarity using priority scoring
3. **Asks targeted questions** (maximum 5) to resolve critical ambiguities
4. **Provides smart recommendations** based on best practices
5. **Validates completeness** before execution

This document adapts these techniques for **everyday users** through intuitive UX patterns that make clarification feel helpful rather than bureaucratic.

### Key Insight

**Clarification is not interrogation**—it's a collaborative refinement process where:
- AI does most of the thinking (provides defaults)
- Users validate or override (minimal cognitive load)
- Questions are sequential and contextual (not overwhelming)
- Improvement is visible (clarity scores, live previews)
- Users learn patterns over time (templates, examples)

---

## Core Concepts from Spec-Kit

### 1. Taxonomy-Based Coverage Analysis

Spec-kit evaluates specifications across **10 dimensions**. For smaller tasks, we can simplify to **5 core dimensions**:

| Dimension | What It Checks | Example Gap |
|-----------|----------------|-------------|
| **Goal & Scope** | What is being created? Why? What's excluded? | "Report on performance" → Performance of what? |
| **Content & Data** | What data/metrics? What calculations? What entities? | "Acquisition performance" → Which metrics matter? |
| **Format & Delivery** | How is output structured? How is it accessed? | "Create report" → Dashboard? PDF? Email? |
| **Quality & Constraints** | Performance limits? Error handling? Edge cases? | What if no data exists? What if generation fails? |
| **Context & Comparison** | What baseline? What time period? What segmentation? | "Last 4 weeks" → Compare to what? Breakdown by what? |

**Each dimension gets a status**:
- ✅ **Clear** (90-100% confidence): No clarification needed
- ⚠️ **Partial** (40-89% confidence): Some details present but incomplete
- ❌ **Missing** (0-39% confidence): Critical gap requiring clarification

### 2. Impact × Uncertainty Heuristic

Not all gaps are equal. Prioritize clarification by multiplying two factors:

**Priority Score = Impact × Uncertainty**

**Impact levels:**
- HIGH: Affects output accuracy, security, or user satisfaction
- MEDIUM: Affects convenience, performance, or aesthetics
- LOW: Affects minor details or preferences

**Uncertainty levels:**
- HIGH: AI has less than 30% confidence in default choice
- MEDIUM: AI has 30-70% confidence
- LOW: AI has more than 70% confidence

**Example**:
- "Which metrics?" = HIGH impact × HIGH uncertainty = **Ask first**
- "Font size for PDF?" = LOW impact × MEDIUM uncertainty = **Use default**

### 3. Sequential Questioning with Recommendations

Spec-kit asks questions **one at a time** with AI-provided recommendations.

**Example question format:**

Question 1: What metrics define "acquisition performance"?

💡 Recommended: Customer count + CPA + Conversion rate
   (Balanced view of efficiency and effectiveness)

Options:
- A) Count only
- B) Count + CPA + Conversion rate ✓
- C) Full funnel + LTV
- D) Custom: [your own answer]

**Why this works**:
- **Not overwhelming**: One question at a time, not a form
- **Guided**: AI recommends best practice, user can override
- **Educational**: User learns what matters over time
- **Fast**: Most users just accept recommendations

### 4. Incremental Integration

After each answer, the system:
1. **Updates the task specification** immediately
2. **Re-evaluates remaining gaps** (some may become irrelevant)
3. **Saves state atomically** (no data loss if interrupted)
4. **Shows progress** (2 of 3 questions answered)

This makes clarification feel like **collaborative refinement** rather than form-filling.

### 5. Explicit Ambiguity Markers

Spec-kit forces acknowledgment of unknowns:

❌ Bad: "System will authenticate users" (AI secretly guesses: email/password)
✅ Good: "System will authenticate users via [NEEDS CLARIFICATION: method not specified]"

For user-facing systems, translate this to:
- 🤷 "I'm not sure" indicators in previews
- ⚠️  Confidence badges on assumptions
- 💭 "Did you mean?" suggestions

### 6. Quality Validation ("Unit Tests for Requirements")

Spec-kit validates specifications with checklists that test **requirement quality**, not implementation:

❌ Wrong: "Verify the report displays correctly" (tests implementation)
✅ Right: "Are all metric definitions specified with formulas?" (tests requirement)

For task clarification:
- **Before execution**: "Do I have everything I need?"
- **Not after completion**: "Did it work?"

---

## The Clarification Framework

### Step-by-Step Process

#### Step 1: Parse & Analyze

User Input: "Create a report on acquisition performance for last 4 weeks"

AI Analysis:
- Goal: ✅ Clear (create report, measure performance)
- Time: ✅ Clear (last 4 weeks)
- Content: ⚠️ Partial (performance = ? metrics)
- Format: ❌ Missing (how to deliver?)
- Edge Cases: ❌ Missing (missing data? zero results?)

**Clarity Score: 45%** (2 of 5 dimensions clear)

#### Step 2: Prioritize Gaps

Priority Queue:
1. Content (HIGH impact × HIGH uncertainty = 9 points)
   → "Which metrics define performance?"

2. Format (MEDIUM impact × HIGH uncertainty = 6 points)
   → "How should I deliver this?"

3. Edge Cases (MEDIUM impact × MEDIUM uncertainty = 4 points)
   → "What if data is incomplete?"

#### Step 3: Generate Questions with Recommendations

For each high-priority gap, create a question with:
- Context: "I need to know..."
- Recommendation: "I suggest X because..."
- Options: Multiple choice OR short answer
- Default: What AI will use if user skips
- Reasoning: Why this matters

#### Step 4: Sequential Clarification

Ask questions one at a time:

Q1 → User answers → Update spec → Re-evaluate → Q2 → ...

Stop when:
- All HIGH priority gaps resolved, OR
- User signals completion ("good enough"), OR
- Maximum question limit reached (3-5 questions)

#### Step 5: Confirmation & Preview

Show what will be done:

📊 Acquisition Performance Report
- Metrics: Customer count, CPA, Conversion rate ✅
- Breakdown: By channel (paid, organic, referral, direct) ✅
- Format: Interactive dashboard with CSV/PDF export ✅
- Missing data: Show available + warning banner ✅
- Time range: Last 4 weeks vs. previous 4 weeks ✅

**Clarity Score: 95% 🟢**

▶️ Start working     ✏️ Refine details

### Applying to Different Task Types

#### Artifact Creation (Reports, Documents, Files)

**Key dimensions to clarify**:
1. **Content**: What data/sections? What calculations?
2. **Format**: Visual structure? File type? Export options?
3. **Delivery**: How accessed? Saved where? Sent to whom?
4. **Completeness**: What if data missing? Zero results? Generation fails?
5. **Context**: Comparisons? Time periods? Segmentation?

**Example clarifications**:
- "Metrics: Count + CPA + Conversion rate (not just count)"
- "Format: Dashboard with CSV export (not just CSV)"
- "Missing data: Show available + warning (not error out)"

#### Process Execution (Workflows, Automations)

**Key dimensions to clarify**:
1. **Triggers**: When should this run? What starts it?
2. **Steps**: What happens in what order? Any branching?
3. **Inputs**: What data is needed? From where?
4. **Outputs**: What gets created/updated? Where does it go?
5. **Error Handling**: What if a step fails? Retry? Alert? Rollback?

**Example clarifications**:
- "Trigger: Daily at 9am (not real-time)"
- "On failure: Retry 3 times then alert (not just fail silently)"

#### Data Transformation (ETL, Migrations, Cleanups)

**Key dimensions to clarify**:
1. **Source**: What data? From where? What filters?
2. **Transform**: What changes? What rules? What validations?
3. **Destination**: Where does it go? What format? Replace or append?
4. **Validation**: How to verify success? What are valid outputs?
5. **Safety**: Backup? Rollback? Dry-run first?

**Example clarifications**:
- "Transform: Deduplicate by email (case-insensitive)"
- "Safety: Dry-run first, then prompt for confirmation"

#### Analysis & Insights (Queries, Investigations)

**Key dimensions to clarify**:
1. **Question**: What specifically needs answering?
2. **Data Scope**: What data sources? Time range? Filters?
3. **Analysis Type**: Descriptive? Diagnostic? Predictive?
4. **Output Format**: Summary? Detailed? Visualizations?
5. **Confidence**: What if data is noisy? Incomplete? Contradictory?

**Example clarifications**:
- "Analysis: Find correlation, not causation"
- "Confidence: Flag insights with <70% confidence"

---

## UX Approaches

### Approach 1: "Clarity Coach" (Conversational Progressive Disclosure)

**Best for**: New users, complex tasks, high-stakes scenarios

#### User Experience

User: "Create a report on acquisition performance for last 4 weeks"

System shows:
```
💡 I can help with that! Let me make sure I understand...

Quick clarity check (2-3 questions): ⚡️
```

Then asks one question at a time:

```
1️⃣ What should this report show?

💡 I recommend: Customer count + Cost per acquisition + Conversion rate by channel
   (This gives you the full performance picture)

 ✓ Use recommendation
 📝 Something else: [_________________________]
 ⏭️  I'll specify this later
```

After each answer, immediately show progress and move to next question.

Final confirmation shows complete summary with all details filled in.

#### Key Principles

- **Maximum 3 questions** for quick tasks, 5 for complex
- **AI recommends first**, user validates or overrides
- **Plain language**, no technical jargon
- **Progress indication**: "2 of 3 questions"
- **Skip options**: Can defer decisions
- **Summary at end**: Clear recap before execution

#### When to Use

- ✅ User is new to the system
- ✅ Task is high-stakes (data migrations, production changes)
- ✅ Task is complex with many dimensions
- ✅ Educational value is important

#### When NOT to Use

- ❌ User is experienced and knows what they want
- ❌ Task is repetitive (use templates instead)
- ❌ Speed is critical (use defaults)

---

### Approach 2: "Clarity Score" (Gamified Real-Time Feedback)

**Best for**: Engaged users who want control, iterative refinement

#### User Experience

As user types, show live clarity score:

```
What do you need?
[Create a report on acquisition performance________]

Clarity Score: 🟡 45%
├─ ✅ Goal is clear
├─ ⚠️  Output format unclear
├─ ⚠️  Key metrics not specified
└─ ⚠️  Edge cases not addressed

 🎯 Let me help clarify (2 min)
 🚀 Good enough, start working
```

If user clicks "help clarify", show selective improvement options. After each answer, score updates visibly and user sees progress.

#### Key Principles

- **Visual feedback**: Score updates in real-time
- **Selective improvement**: User chooses what to clarify
- **Gamification**: Satisfying to increase score
- **Escape hatch**: Can start at any score level
- **Priority guidance**: Shows what matters most

#### Scoring Algorithm

Clarity Score = Weighted average of dimension scores

Dimension weights:
- Goal: 30% (most important)
- Content: 30%
- Format: 20%
- Quality: 10%
- Context: 10%

Each dimension scores:
- Clear (90-100%): 1.0
- Partial (40-89%): 0.5
- Missing (0-39%): 0.0

#### When to Use

- ✅ User is analytical and wants transparency
- ✅ Task has multiple iterations
- ✅ Learning and improvement over time is valued
- ✅ User enjoys progress tracking

#### When NOT to Use

- ❌ User finds metrics overwhelming
- ❌ One-off tasks where learning doesn't matter
- ❌ Users who prefer passive guidance

---

### Approach 3: "Preview-Driven Clarification" (Show, Don't Tell)

**Best for**: Visual thinkers, users who learn by example

#### User Experience

Immediately show a preview with visible assumptions:

```
Here's what I'll create based on your request:

📊 Acquisition Performance Report
┌───────────────────────────────────────────────────┐
│ 🤷 Metrics: [Not specified - I'll guess]           │
│    → Defaulting to: Total customer count           │
│    💭 Did you want: CPA? Conversion rate? Revenue? │
│                                                     │
│ 🤷 Format: [Not specified - I'll guess]            │
│    → Defaulting to: CSV file                       │
│    💭 Did you want: Dashboard? PDF? Email?         │
│                                                     │
│ ✅ Time range: Last 4 weeks (Clear!)               │
│                                                     │
│ ❓ Missing data handling: [Not specified]          │
│    → I'll show an error if data is incomplete      │
│    💭 Is that OK?                                  │
└───────────────────────────────────────────────────┘

 ✏️ This looks wrong - let's clarify
 ▶️ Good enough, proceed with defaults
```

If user clicks "let's clarify", focus on specific issues. Preview updates live after each selection.

#### Key Principles

- **Make assumptions visible**: User sees what AI will do
- **Highlight uncertainty**: Icons (🤷 ❓ ✅) show confidence levels
- **Live preview updates**: Changes reflect immediately
- **Selective refinement**: Fix only what's wrong
- **Explanation of defaults**: User learns best practices

#### Icon Legend

- ✅ Confident (>90%): I'm sure about this
- ⚠️  Partial (40-89%): I have some info but not complete
- 🤷 Uncertain (<40%): I'm guessing - please verify
- ❓ Missing: You didn't specify, using fallback
- 💭 Thinking: Consider these alternatives

#### When to Use

- ✅ User is visual and prefers concrete examples
- ✅ Task output has visual/structural components
- ✅ Users learn by seeing what will happen
- ✅ Anxiety about AI "black box" decisions

#### When NOT to Use

- ❌ Output format is not easily previewable (e.g., API calls)
- ❌ Preview would be overwhelming or complex
- ❌ Users prefer abstract descriptions to concrete examples

---

### Approach 4: "Example-Driven Refinement" (Learn From Similar Tasks)

**Best for**: Repetitive tasks, organizational knowledge sharing

#### User Experience

Search for similar past tasks:

```
I found 3 similar tasks others have done:

┌─────────────────────────────────────────────┐
│ 1. Marketing Dashboard Report               │ ⭐⭐⭐⭐⭐
│    └─ Customer count, CPA, conversion by channel
│    └─ Interactive dashboard with exports
│    └─ Weekly trends + previous period comparison
│    📋 Use as template
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 2. Simple Acquisition CSV                    │ ⭐⭐⭐
│    └─ Just customer count per day
│    └─ CSV export only
│    📋 Use as template
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 3. Executive Summary Report                  │ ⭐⭐⭐⭐
│    └─ Revenue focus with acquisition ROI
│    └─ PDF emailed weekly
│    📋 Use as template
└─────────────────────────────────────────────┘

 ✍️  Start from scratch instead
```

After selecting template, all details are pre-filled and user can edit only what's different.

#### Key Principles

- **Social proof**: See what worked for others (ratings, usage count)
- **Quick start**: Template fills in blanks automatically
- **Customize selectively**: Edit only what's different
- **Learning built-in**: Discover best practices organically
- **Template creation**: Users can save variations for reuse

#### Template Matching Logic

Similarity Score combines:
- Keyword overlap (30% weight): "report", "acquisition", "performance"
- Task category match (30%): Report generation, data analysis, etc.
- User context (20%): Same team, same department, same role
- Historical success (20%): Star rating, completion rate

Rank templates by similarity, show top 3-5. Include "Start from scratch" option for edge cases.

#### When to Use

- ✅ Organization has history of similar tasks
- ✅ Best practices exist and should be promoted
- ✅ Users benefit from seeing how others solved similar problems
- ✅ Consistency across team/organization is valued

#### When NOT to Use

- ❌ Task is novel with no similar precedents
- ❌ Privacy concerns with showing others' tasks
- ❌ Templates would constrain creativity undesirably

---

### Approach 5: "Checklist-Before-You-Go" (Final Quality Gate)

**Best for**: Quick validation, preventing common mistakes

#### User Experience

Right before execution, show a quick check:

```
Quick check before I start:

✅ I know WHAT to create
✅ I know WHEN (last 4 weeks)
⚠️  I'm not sure HOW to deliver it
⚠️  I don't know what to do if data is missing

This might lead to rework. Want to clarify?

 🎯 Yes, 2 quick questions (30 sec)
 🚀 No, just use your best judgment
```

If user chooses clarification, ask only the 1-2 most critical questions, then proceed.

#### Key Principles

- **Friction at right time**: Right before execution, not during input
- **Transparent reasoning**: Shows what's unclear and why
- **Opt-out available**: Can skip if confident
- **Quick resolution**: Maximum 2-3 questions
- **Prevents rework**: Catches issues before expensive work

#### When to Use

- ✅ User seems confident but task has hidden ambiguities
- ✅ Common failure patterns exist for this task type
- ✅ Execution is expensive (time, compute, or risk)
- ✅ Small time investment can prevent large waste

#### When NOT to Use

- ❌ Task is already highly clarified
- ❌ Execution is cheap and easily reversed
- ❌ Interrupting flow would be more costly than rework

---

### Approach 6: "Clarity Companion" (Hybrid - Recommended)

**Best for**: Adaptive system that works for all user types

This combines the best elements of all approaches with adaptive behavior based on clarity score.

#### Adaptive Flow

**Step 1**: Parse user input (invisible to user)
- Analyze against 5 dimensions
- Calculate clarity score (0-100%)
- Determine intervention level

**Step 2**: Adaptive intervention
- If Clarity ≥ 90%: Silent execution (no interruption)
- If Clarity 70-89%: Light touch (single quick check)
- If Clarity < 70%: Structured clarification (2-5 questions)

**Step 3**: Contextual clarification
- Use conversational flow (Approach 1)
- Show live score (Approach 2)
- Provide preview (Approach 3)

**Step 4**: Learn & improve
- Suggest templates (Approach 4)
- Save successful patterns

#### User Experience Examples

**High Clarity (90%+)**: Silent execution

User: "Create a CSV report with customer count, CPA, and conversion rate by channel for last 4 weeks. Email it to me."

System: "✅ Starting work on your acquisition report... Estimated completion: 2 minutes"

**Medium Clarity (70-89%)**: Light touch

User: "Create a report on acquisition performance for last 4 weeks"

System: "💡 Quick tip: I noticed you didn't specify the delivery method. I'll default to an interactive dashboard. Is that OK?"
- ✓ Yes, dashboard is fine
- 📧 Email as PDF instead
- ✏️ Let me clarify

**Low Clarity (<70%)**: Structured clarification

User: "Create a report on acquisition performance"

System: "I want to nail this! Let's clarify 2-3 things (1 min). Clarity: 🟡 45% → 🟢 Target 95%"
- 🎯 Start clarification (recommended)
- 🚀 Skip, use your best judgment

#### Learn & Improve Over Time

After successful completion:

```
🎉 Report completed successfully!

💾 Save this as a template?
   Name: [Marketing Acquisition Report___]

 ✓ Save template    ✗ No thanks

Next time, I'll suggest this template for similar requests!
```

#### Key Principles

- **Invisible when possible**: Don't interrupt confident users
- **Helpful when needed**: Intervene for unclear requests
- **Learns over time**: Gets smarter about user preferences
- **Adapts to expertise**: Heavy users get faster flows
- **Provides escape hatches**: Can always skip or customize

#### Adaptive Thresholds

**Clarity Thresholds** (adjustable per user):
- Silent: ≥ 90% (no intervention)
- Light: 70-89% (1 quick check)
- Structured: < 70% (2-5 questions)

**User Expertise Adjustment**:
- Novice: Thresholds +10% (more help)
- Intermediate: Standard thresholds
- Expert: Thresholds -10% (less interruption)

**Task Risk Adjustment**:
- Low risk: Thresholds -10% (more lenient)
- Medium risk: Standard thresholds
- High risk: Thresholds +10% (more careful)

---

## Implementation Concepts

### Backend: Clarity Analysis Engine

The system needs to analyze user input and determine what's missing. Core components:

#### Clarity Analyzer

Takes user input and task type, returns a clarity report containing:
- Overall clarity score (0-100%)
- Status for each dimension (clear/partial/missing)
- Prioritized list of gaps to address
- Recommended intervention level (silent/light/structured)

**Process**:
1. Parse input using natural language understanding
2. Evaluate each of the 5 dimensions
3. Calculate weighted average for overall score
4. Identify gaps where confidence is low
5. Prioritize gaps by Impact × Uncertainty

#### Dimension Evaluators

For each dimension, check specific aspects:

**Goal Evaluator**:
- Has action verb? (create, analyze, migrate, etc.)
- Has object/artifact? (report, dashboard, analysis)
- Has purpose/reason? (to measure, for stakeholders)
- Confidence: high if all three present

**Content Evaluator**:
- What task-specific specs are required?
- For reports: metrics, data sources, calculations
- For workflows: steps, inputs, outputs
- Calculate coverage: detected specs / required specs

**Format Evaluator**:
- Output structure specified? (CSV, PDF, dashboard)
- Delivery method specified? (download, email, display)
- Access method specified? (button, schedule, API)

**Quality Evaluator**:
- Error handling specified?
- Edge cases addressed?
- Performance constraints mentioned?

**Context Evaluator**:
- Time period specified?
- Comparison baseline specified?
- Segmentation/breakdown specified?

#### Gap Prioritization

For each gap (missing or partial dimension):
1. Assess impact on task success (high/medium/low)
2. Measure uncertainty (1.0 - confidence score)
3. Calculate priority score (impact × uncertainty)
4. Sort gaps by priority score
5. Take top 3-5 for questioning

### Question Generation

For each gap, generate:

**Question text** based on dimension and task type:
- Content + Report → "What metrics should this report show?"
- Format + Report → "How should I deliver this report?"
- Quality + Report → "What should I do if data is incomplete?"

**Recommendations** based on best practices:
- Most common choice among similar tasks (60%+ usage)
- Expert-recommended approach
- Safe fallback that's reversible

**Default** is the first recommendation

**Reasoning** explains why the default is recommended:
- "Balanced view of efficiency and effectiveness"
- "Flexibility for different workflows and audiences"
- "Transparency prevents misinterpretation"

### Template Matching

Find similar past tasks for reuse:

**Matching factors**:
- Keyword similarity (30%): Extract keywords from description
- Category match (30%): Report, workflow, analysis, etc.
- User context (20%): Same team, department, role
- Success rate (20%): Star rating, completion rate

Rank by combined similarity score, show top 3-5 templates.

### Adaptive Intervention

Determine how much clarification to apply:

**Thresholds start at**:
- Silent: ≥ 90% clarity
- Light: 70-89% clarity
- Structured: < 70% clarity

**Adjust based on user expertise**:
- Novice users: +10% to thresholds (more intervention)
- Intermediate: no adjustment
- Expert users: -10% to thresholds (less intervention)

**Adjust based on task risk**:
- Low risk tasks: -10% to thresholds (more lenient)
- Medium risk: no adjustment
- High risk: +10% to thresholds (more careful)

Calculate adjusted clarity score, then determine intervention level.

---

## Metrics & Success Criteria

### Key Metrics to Track

#### Clarity Metrics

**Average Clarity Score**:
- Initial (before clarification): Target >60%
- Final (after clarification): Target >90%
- Improvement delta: Target +30%

**Clarification Engagement Rate**:
- Percentage of users who engage with clarification prompts
- Target: 70-80% for structured flow, 40-50% for light touch

**Question Completion Rate**:
- Percentage of started clarification flows that complete
- Target: >85%

**Average Questions Answered**:
- Mean number of questions per clarification session
- Target: 2-3 questions

#### Task Success Metrics

**First-Time Success Rate**:
- Percentage of tasks that succeed without iteration
- Correlated with final clarity score
- Target: >85% for clarity >90%

**Iteration Count**:
- Average number of attempts to complete task
- Target: <1.5 iterations

**Rework Rate**:
- Percentage of tasks requiring significant changes after initial attempt
- Target: <15%

#### User Experience Metrics

**Time to Clarify**:
- Median time spent in clarification flow
- Target: <2 minutes for structured, <30 seconds for light

**User Satisfaction (NPS)**:
- "How satisfied were you with the clarification process?"
- Target: NPS >50

**Perceived Value**:
- "Did clarification help improve the result?"
- Target: >80% "yes"

**Friction Score**:
- "Was clarification interrupting or helpful?"
- Target: >70% "helpful"

#### Learning Metrics

**Template Creation Rate**:
- Percentage of successful tasks saved as templates
- Target: 20-30%

**Template Reuse Rate**:
- Percentage of tasks starting from templates
- Target: 40-50% after 3 months

**Expertise Progression**:
- How quickly users move from novice → expert
- Measured by decreasing clarification needs
- Target: 30% reduction in clarifications after 20 tasks

### Success Criteria by Approach

| Approach | Primary Success Metric | Target |
|----------|----------------------|--------|
| Conversational (1) | Question completion rate | >85% |
| Gamified (2) | Clarity score improvement | +35% average |
| Preview (3) | Perceived value | >85% helpful |
| Example-driven (4) | Template reuse rate | >50% |
| Checklist (5) | Time to clarify | <30 seconds |
| Hybrid (6) | First-time success rate | >90% |

### A/B Testing Framework

Test different approaches with user segments:

**Variants**:
- Control: No clarification (baseline)
- Light: Checklist-before-you-go
- Conversational: Full conversational flow
- Preview: Preview-driven clarification
- Hybrid: Adaptive hybrid approach

**Metrics to measure**:
- Clarity score improvement
- First-time success rate
- Time to complete
- User satisfaction
- Rework rate

**Determine winner** using multi-objective optimization:
- Task success rate (40% weight)
- User satisfaction (30% weight)
- Time efficiency (20% weight)
- Scalability (10% weight)

### Monitoring Dashboard

Key indicators to display:

**Real-Time Metrics**:
- Current avg clarity score: 72% ⚠️  (target: >75%)
- Clarification engagement: 68% ✓
- Question completion rate: 87% ✓
- First-time success rate: 81% ⚠️  (target: >85%)

**Trends (7 days)**:
- Clarity score: 72% → 76% ↗️  (+4%)
- Task success: 81% → 84% ↗️  (+3%)
- Avg questions: 2.8 → 2.3 ↗️  (-18%)

**User Segments**:
- Novices: 65% clarity, 2.9 questions
- Intermediate: 78% clarity, 2.1 questions
- Experts: 87% clarity, 0.8 questions

**Top Gaps (this week)**:
1. Format/Delivery (42% of clarifications)
2. Content/Metrics (31%)
3. Edge Cases (18%)
4. Context/Comparison (9%)

---

## Quick Reference: Patterns

### When to Ask Questions

**ASK if**:
- ✓ Impact is HIGH (affects output quality/accuracy)
- ✓ Uncertainty is HIGH (AI confidence <40%)
- ✓ Cost of assumption is HIGH (hard to fix later)
- ✓ Common failure pattern exists

**DON'T ASK if**:
- ✗ User already provided the information
- ✗ Default is safe and reversible
- ✗ Impact is LOW and uncertainty is LOW
- ✗ Would overwhelm user (>5 questions total)

### Question Quality Checklist

**Good questions are**:
- ✓ Specific: "Which metrics?" not "What do you want?"
- ✓ Actionable: Answer directly improves output
- ✓ Binary or Multiple-Choice: Easy to answer quickly
- ✓ Recommended: AI suggests best practice
- ✓ Explained: User understands why it matters

**Bad questions are**:
- ✗ Vague: "Any preferences?"
- ✗ Open-ended: "Describe your needs"
- ✗ Obvious: User already said this
- ✗ Overwhelming: Too many options
- ✗ Unexplained: No context for why asking

### Clarity Score Interpretation

- **90-100%**: Silent execution (no intervention)
- **70-89%**: Light touch (1 quick check)
- **50-69%**: Structured flow (2-3 questions)
- **<50%**: High-touch (up to 5 questions + examples)

### Recommendation Formula

**Good Default = Most Common × Best Practice × Safe Fallback**

- **Most Common**: What 60%+ of users choose
- **Best Practice**: What experts recommend
- **Safe Fallback**: Reversible, no data loss

**Example**:
"Dashboard with exports" =
  Most common (68% of users) +
  Best practice (flexibility) +
  Safe (user can export later)

### Progressive Disclosure Principles

1. **Start minimal**: Show only what user needs now
2. **Reveal incrementally**: Add detail as needed
3. **Make expansion obvious**: Clear "more options" affordance
4. **Preserve context**: Keep previous choices visible
5. **Allow backtracking**: Easy to change earlier answers

---

## Conclusion

The core insight from spec-kit is that **systematic clarification** dramatically improves task outcomes. By:

1. **Analyzing** requests against a structured taxonomy
2. **Prioritizing** gaps by impact and uncertainty
3. **Asking** targeted questions with smart recommendations
4. **Validating** completeness before execution
5. **Learning** from successful patterns

You can transform user-AI interaction from frustrating iteration to **collaborative refinement** that feels helpful rather than bureaucratic.

The key is **adaptive UX**: light touch for clear requests, structured guidance for ambiguous ones, and continuous learning to reduce friction over time.

### Next Steps for Implementation

1. **Start simple**: Implement basic clarity scoring (5 dimensions)
2. **Add light touch**: Single-question validation before execution
3. **Expand to structured**: Full conversational flow for low clarity
4. **Measure & iterate**: Track success rates, adjust thresholds
5. **Add learning**: Template matching and user expertise tracking

---

**Document Version**: 1.0
**Last Updated**: 2026-01-16
**Based on**: GitHub spec-kit project analysis and UX adaptation
