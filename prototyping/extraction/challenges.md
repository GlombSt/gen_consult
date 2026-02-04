# The Fundamental Challenge

LLMs extract based on pattern matching, not causal understanding.

**They can articulate:**
- ✓ Common patterns from training data
- ✓ Explicit documented knowledge
- ✓ Logical relationships

**They struggle with:**
- ✗ Domain-specific tacit knowledge
- ✗ Rare but critical edge cases
- ✗ Recently changed regulations
- ✗ Context-dependent exceptions

**Solution approach:**
- Use LLM for structure and common patterns
- Use search for domain-specific validation
- Use user as final validator with structured review UI
- Iterate based on usage data

> The reference doesn't need to be perfect initially — it needs to be good enough to guide thinking and improvable through use.

---

# Key Challenges

## 1. Boundary Confusion

LLM struggles to distinguish:

- **Input vs Context:** "Customer data" (input you process) vs "Knowledge of GDPR" (context you need)
- **Decision vs Constraint:** "Choose privacy level" (decision) vs "Must comply with GDPR" (constraint)
- **Context vs Assumption:** "Market understanding" (context) vs "Assumes market exists" (assumption)

**Mitigation:** Use contrastive examples in prompts, extract iteratively with refinement.

## 2. Granularity Control

LLM might generate:

- **Too coarse:** "Decide on strategy" (not actionable)
- **Too fine:** "Choose font size for heading" (too trivial)
- **Inconsistent:** Mix of high/low level items

**Mitigation:** Specify target abstraction level, use examples at desired granularity.

## 3. Domain Knowledge Gaps

For specialized tasks (Vollzugsplan, medical diagnosis):

- LLM may miss critical domain-specific constraints
- May hallucinate requirements that don't exist
- May use outdated regulatory information

**Mitigation:** Web search validation, confidence scoring, explicit "verify this" flags for domain-specific items.

## 4. Trade-off Articulation

LLM tends to:

- List only advantages (not disadvantages)
- Provide generic trade-offs ("faster but less accurate")
- Miss non-obvious second-order effects

**Mitigation:** Explicitly prompt for disadvantages, ask "what could go wrong if you choose this?"

## 5. Dependency Chain Complexity

Hard to extract:

- "Decision B only matters if you chose option X in Decision A"
- "Constraint C conflicts with Success Criterion D"
- Circular dependencies

**Mitigation:** Two-pass extraction (first extract components, second pass extract relationships).

## 6. Example Quality

LLM examples are often:

- **Too clean/idealized** (not messy like reality)
- **Generic** ("customer support ticket about billing")
- **Insufficient variety**

**Mitigation:** Prompt for edge cases, adversarial examples, real-world messiness.

## 7. Implicit Knowledge

Experts have tacit knowledge that's hard to extract:

- "Everyone knows you check X first"
- Heuristics that aren't written down
- Context-dependent rules ("usually do Y, except when Z")

**Mitigation:** Prompt with "what do beginners miss?" and "what unwritten rules exist?"

## 8. Confidence Calibration

LLM doesn't reliably know what it doesn't know:

- High confidence on hallucinated constraints
- Low confidence on well-known facts
- Inconsistent across domains

**Mitigation:** External validation (web search), cross-check against multiple extractions, user feedback loop.

## 9. Completeness Detection

Hard to know when you're done:

- Did we extract ALL critical decisions?
- Are there failure modes we missed?
- What about edge cases?

**Mitigation:** Iterative refinement, cross-check against similar tasks, user review with "what's missing?" prompts.

## 10. Consistency Across Components

Risk of:

- Input mentioned but never used in decisions
- Success criterion with no corresponding decision to influence it
- Constraint that doesn't actually constrain anything
- Orphaned components

**Mitigation:** Validation pass that checks all relationships, flags orphans.
