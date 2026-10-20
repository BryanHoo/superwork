---
name: superwork-planning
description: Use this skill to resolve material design uncertainty, plan high-risk or cross-system work, or create an explicitly requested resumable plan. Keep same-session planning concise, persist one Markdown file only when continuity or approval requires it, then implement every code behavior through TDD.
---

# Superwork Planning

## Purpose

Resolve only the decisions that block safe implementation, then continue in the same context without a separate execution handoff.

## Entry

Use planning when at least one condition holds:

- architecture, scope, or a cross-system contract is unresolved
- the change is high risk or requires approval before implementation
- work must resume across sessions
- the user explicitly requests a design or plan

Do not use planning solely because several files will change. Clear development work goes directly to `superwork-tdd`.

## Process

1. Use project facts from `superwork-start`; load only required candidate reads and retrieve recommended guidance when concrete task evidence makes it relevant.
2. Inspect the smallest source, tests, history, or external evidence needed to resolve material uncertainty.
3. State the goal, scope, acceptance signal, key decisions, risks, and bounded behavior slices.
4. Ask one focused question only when a missing user choice would materially change the result.
5. Keep the plan in the current context by default. Save one Markdown file under `.superwork/plans/` only for explicit plan artifacts, approval gates, or cross-session continuity.
6. Stop after design or planning only when the user explicitly limits the outcome.

## Saved Plan

Store a resumable plan in one Markdown file using `### Task <number>: <title>` and exactly one `Task Status` checkbox per task. Include a falsifiable proof and stop condition for each behavior slice.

Do not create a separate design artifact unless the user explicitly requests one. Do not add commit or PR steps unless requested.

## Exact Saved Plan Template

```markdown
# Feature Implementation Plan

**Goal:** One verifiable outcome
**Scope:** Exact allowed boundary
**Acceptance:** Final observable signal

### Task 1: Implement bounded behavior

**Files:**

- Modify: `src/module.py`
- Test: `tests/test_module.py`

**Behavior:**

- Define one bounded, falsifiable behavior slice.

**Proof:** `python3 -m unittest tests.test_module -v`

**Stop Conditions:**

- Stop if a required product choice or independent behavior is unresolved.

- [ ] **Task Status:** pending
```

Add `**Interfaces:**` only when a real cross-task contract needs an exact signature or artifact name. Keep one Markdown file and repeat the complete task block for later tasks.

## Continue Through TDD

For implementation, read `../superwork-tdd/SKILL.md` once per run and reuse that method for every code behavior slice. Non-code-only changes use the smallest relevant deterministic proof.

After the final slice passes, read `../superwork-check/SKILL.md` once and pass completion evidence. Do not enter `superwork-executing-plans` for a plan created in the current run; that skill is reserved for resuming a previously saved plan.

## Stop Conditions

- A required product choice or external dependency remains unresolved.
- A behavior slice cannot be made falsifiable.
- Implementation reveals an independent scope that needs a separate plan.
