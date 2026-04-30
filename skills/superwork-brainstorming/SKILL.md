---
name: superwork-brainstorming
description: Use when feature work in a `.superwork` project needs design clarification, option comparison, or explicit user approval before implementation starts.
---

# Superwork Brainstorming

## Overview

Turn rough feature ideas into an approved, implementation-ready design before writing code.

**Core principle:** No implementation action before the design is explicit and approved.

## When to Use

Use when:
- requirements are still fuzzy
- multiple approaches are possible
- architecture or scope trade-offs are unclear
- the user asked to "think through" a feature first

Do not use when:
- the task is purely bug investigation (use `superwork-debugging`)
- the design is already approved and written (use `superwork-writing-plans`)

## Checklist

Complete these steps in order:

1. Explore project context (`.superwork/workflow.md`, related specs, relevant code)
2. Ask clarifying questions one at a time
3. Propose 2-3 approaches with trade-offs and one recommendation
4. Present the design in clear sections and collect approval
5. Write the design doc to `.superwork/prd/YYYY-MM-DD-<topic>-prd.md`
6. Self-review for ambiguity, contradictions, and missing scope boundaries
7. Ask the user to review the written PRD
8. Invoke `superwork-writing-plans`

## Process Flow

```dot
digraph superwork_brainstorming {
    "Explore context" [shape=box];
    "Ask clarifying questions" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Write design doc" [shape=box];
    "User reviews PRD?" [shape=diamond];
    "Invoke superwork-writing-plans" [shape=doublecircle];

    "Explore context" -> "Ask clarifying questions";
    "Ask clarifying questions" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Write design doc" [label="yes"];
    "Write design doc" -> "User reviews PRD?";
    "User reviews PRD?" -> "Write design doc" [label="changes requested"];
    "User reviews PRD?" -> "Invoke superwork-writing-plans" [label="approved"];
}
```

## Hard Gate

Do not invoke implementation skills, do not edit code, and do not scaffold files before design approval.

## Common Mistakes

| Mistake | Why It Fails | Correct Move |
|---|---|---|
| Jumping to code after one idea | Hidden assumptions become rework | Explore alternatives first |
| Skipping written PRD | Design gets lost between turns | Save to `.superwork/prd/...` |
| Moving ahead without user review | Plan may optimize the wrong goal | Wait for explicit approval |

## Integration

- Entry comes from `superwork-start` for design-heavy feature work
- Next step is always `superwork-writing-plans`
