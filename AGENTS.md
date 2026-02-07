# Readable Code Instructions (for coding agents)

**Goal:** Produce code that a new engineer can understand and change safely with minimal context.

## Output rules

- Prefer **clarity over cleverness** unless explicitly asked to optimize.
- Keep changes **small and local**; avoid cascading edits.
- Match existing project style; if absent, follow common language conventions.
- If uncertain, choose the option that is **more explicit**.

## Structure

- Functions: **single purpose**, typically **≤ 30 lines**.
- Nesting depth: **≤ 3**. Use early returns to flatten control flow.
- Split work into phases:
  1) validate inputs
  2) transform/compute
  3) side effects (I/O, DB, network)
- Extract complex expressions into named variables.

## Naming

- Names must reveal intent; avoid non-standard abbreviations.
- Booleans: `is_`, `has_`, `can_`, `should_`.
- Functions: verbs (`parse…`, `build…`, `validate…`).
- Collections: plural nouns (`users`, `orderIds`).
- Units in names where relevant: `timeoutMs`, `sizeBytes`.

## Formatting

- Max line length: **100** (unless repo specifies otherwise).
- Use blank lines to separate logical blocks.
- Avoid nested ternaries and long chained expressions; break into steps.

## Comments & docs

- Comment **why**, not what.
- Public APIs: short docstring describing purpose, params, return, side effects.
- Explain non-obvious constraints, invariants, or business rules.

## Error handling

- **Fail fast** on invalid inputs; return/throw early with actionable messages.
- Do not swallow exceptions silently.
- Keep error formatting/logging separate from business logic.
- Prefer domain-specific error types where appropriate.

## Function interface

- Avoid > 3 parameters; use a config object/struct for grouped options.
- Avoid boolean flags that drastically change behavior; split into two functions.
- Avoid mutating input arguments unless the API contract requires it.

## "Refactor now" triggers

Refactor if any applies:

- function > 30 lines or > 10 cyclomatic complexity
- nesting > 3
- repeated code blocks
- variables like `tmp`, `data`, `result` without domain meaning
- you need comments to explain control flow

## Quick self-check (before finalizing)

- Can a reviewer understand the intent in **< 30 seconds**?
- Are names sufficient to narrate the code?
- Are edge cases validated up front?
- Are side effects isolated and obvious?

## Rationale

Complexity and nesting correlate with defects; readability and naming quality improve comprehension and maintainability (McCabe, Buse & Weimer, Parnas, Sweller).

## Project-specific

- **Backend (intentions/):** Also follow [intentions/PYTHON_IDIOM_STANDARDS.md](intentions/PYTHON_IDIOM_STANDARDS.md).
- **Other project rules:** [CLAUDE.md](CLAUDE.md), [intentions/AGENT_WORKFLOW.md](intentions/AGENT_WORKFLOW.md), [intentions/ARCHITECTURE_STANDARDS.md](intentions/ARCHITECTURE_STANDARDS.md).
