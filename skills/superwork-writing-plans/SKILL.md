---
name: superwork-writing-plans
description: Creates a saved implementation plan for a clear medium task or a heavy-task design. It defines behavior slices and verification without editing product code, then hands a valid plan to execution by default.
---

# Superwork Writing Plans

## Purpose

Create an executable plan that fixes boundaries, interfaces, verification, and stopping conditions while leaving context-dependent implementation choices to the executor.

## Inputs

Read:

- design artifact or clear task requirements
- `.superwork/config.json` when available
- relevant `.superwork/spec/**` indexes and linked concrete docs
- existing source and test patterns needed to name real files and interfaces

If the work is still a light, tightly bounded change, return it to `superwork-tdd`. If unresolved design choices remain, return it to `superwork-brainstorming`.

## Plan Location

Save a normal plan to:

```text
.superwork/plans/YYYY-MM-DD-<topic>.md
```

For a plan too large to read efficiently as one file, use an `overview.md` plus one file per independently verifiable task under `.superwork/plans/<topic>/`.

## Required Header

Every plan contains:

```markdown
# Feature Implementation Plan

**Goal:** One bounded outcome

**Suggested Spec Reads:**

- `real/path.md` — reason it applies

**Architecture:** Short implementation direction

**Tech Stack:** Relevant languages and tools

## Global Constraints

- Exact binding project rule
```

## Task Contract

Each task must include:

- `Files`: exact create, modify, delete, and test paths
- `Interfaces`: exact consumed and produced contracts or artifacts
- one bounded behavior slice
- test or falsifiable proof intent
- exact verification command and expected signal
- `Stop Conditions`: conditions that require plan repair, clarification, or debugging

Every code behavior slice is executed through the `superwork-tdd` TDD method. The plan defines the intended behavior and evidence; it does not duplicate that method's RED/GREEN/REFACTOR instructions.

Use complete code or command sequences only when the operation is fragile, order-sensitive, security-sensitive, or otherwise has one safe path. For normal implementation, prefer signatures, invariants, examples, and acceptance criteria over copying a speculative full implementation into the plan.

Do not add commit steps unless the user or project policy explicitly requests commits.

## Self-Review

Before handoff:

1. Map every approved requirement to at least one task.
2. Verify all paths and suggested reads exist or are explicitly created by an earlier task.
3. Check interface names and signatures across task boundaries.
4. Remove placeholders, duplicate instructions, speculative abstractions, and unnecessary complete-code blocks.
5. Confirm every task has verification evidence and stop conditions.
6. Run the bundled plan preflight and fix blocking issues.

## Continuation Policy

After the plan passes preflight, invoke `superwork-executing-plans` by default. If the user explicitly asks for a plan only or says not to implement, save the plan, report its path and preflight result, and stop.
