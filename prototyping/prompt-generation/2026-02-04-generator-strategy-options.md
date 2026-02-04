# Generator Strategy Options

**Date:** 2026-02-04

## Key Decision: Reasoning Strategies as Implementation Detail

Chain-of-Thought (CoT), Tree-of-Thought (ToT), and similar reasoning strategies are **implementation options at prompt generation time** — not domain model entities.

### Why This Separation Works

| Layer | Concern | Example |
|-------|---------|---------|
| **Domain (user-facing)** | "I want reasoning shown in output" | Quality entity: "Include step-by-step reasoning" |
| **Generator (implementation)** | "Use CoT to improve accuracy" | Generator injects "think step by step" |

**The user shouldn't need to know prompting techniques.** The system applies best practices based on task characteristics.

### What the Generator Can Infer From

- **Task complexity** — multi-step reasoning suggests CoT
- **Task type** — planning/exploration suggests ToT
- **Quality requirements** — if user wants reasoning visible, use explicit CoT
- **Intent domain** — math/logic problems benefit from CoT

### Domain Model Implications

- No need for a "ReasoningStrategy" entity
- If user wants visible reasoning → **Quality** spec (output format)
- If user wants better accuracy via internal reasoning → generator optimization (invisible to user)

This keeps the domain model focused on *what the user is articulating* and leaves technique selection to the system.

---

## Available Reasoning/Prompting Strategies

### Core Techniques

| Technique | How it works | Best for |
|-----------|--------------|----------|
| **Chain-of-Thought (CoT)** | "Think step by step" — linear reasoning | Math, logic, multi-step problems |
| **Tree-of-Thought (ToT)** | Explore multiple paths, backtrack | Planning, puzzles, creative exploration |
| **Graph-of-Thought (GoT)** | Non-linear reasoning with connections between thoughts | Complex problems with interdependencies |
| **Self-Consistency** | Generate multiple CoT paths, vote on answer | When confidence matters |
| **Reflection/Self-Critique** | Generate, critique, revise | Quality improvement, catching errors |
| **ReAct** | Reasoning + Acting (interleave thoughts with tool use) | Agentic tasks, research, multi-step with tools |
| **Plan-and-Solve** | First plan steps, then execute each | Complex multi-phase tasks |
| **Least-to-Most** | Break into subproblems, solve smallest first | Compositional problems |
| **Step-Back** | Abstract the problem first, then solve | Problems requiring high-level insight |
| **Analogical Reasoning** | "Think of a similar problem you know" | Novel problems, transfer learning |
| **Decomposition** | Explicit subtask breakdown | Large tasks needing structure |
| **Verification/Validation** | Generate then verify/prove correctness | Math proofs, code, factual accuracy |
| **Few-Shot Prompting** | Provide examples (covered by Example entity) | Pattern demonstration |
| **Zero-Shot** | Direct instruction, no examples | Simple/clear tasks |

### Emerging/Specialized Techniques

| Technique | How it works |
|-----------|--------------|
| **Skeleton-of-Thought** | Generate skeleton, fill in parallel |
| **Thread-of-Thought** | Chaotic context handling |
| **Contrastive CoT** | Include "wrong" examples to avoid |
| **Maieutic Prompting** | Socratic, recursive explanation |

---

## Generator Decision Tree

A simple heuristic for strategy selection:

```
Task Type Assessment
│
├── Simple transformation
│   └── Zero-shot
│
├── Multi-step reasoning
│   └── Chain-of-Thought
│
├── High-stakes accuracy
│   └── Self-Consistency or Reflection
│
├── Exploration/planning
│   └── Tree-of-Thought
│
├── Tool use involved
│   └── ReAct
│
└── Complex with dependencies
    └── Plan-and-Solve or Decomposition
```

---

## Relationship to Domain Model

The **Example** entity in the domain model provides the material for Few-Shot prompting. The generator decides:

1. **Whether** to include examples (based on task complexity)
2. **How many** examples to include
3. **Which** reasoning strategy to layer on top

All other reasoning strategies are pure generator concerns — the user articulates *what* they want, the generator figures out *how* to prompt for it effectively.
