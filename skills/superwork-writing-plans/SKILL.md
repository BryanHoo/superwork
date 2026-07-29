---
name: superwork-writing-plans
description: Use this skill to create a resumable implementation plan for a clear multi-file change or an approved heavy-task design. Define serial behavior slices, interfaces, stop conditions, and verification in one Markdown file, then continue to execution by default.
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

Save every plan as one Markdown file:

```text
.superwork/plans/YYYY-MM-DD-<topic>.md
```

Split an oversized request into separate bounded plans instead of creating a multi-file plan.

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

Use the heading grammar `### Task <number>: <title>` with sequential task numbers starting from 1. Copy the exact structure below for every task, replace its example values, and repeat the whole block for later tasks.

## Exact Task Template

```markdown
### Task 1: Implement bounded behavior

**Files:**

- Modify: `src/module.py`
- Test: `tests/test_module.py`

**Interfaces:**

- Consumes: `ExistingContract`
- Produces: `UpdatedContract`

**Behavior:**

- Define one bounded, falsifiable behavior slice.

**Stop Conditions:**

- Stop if a required interface or constraint is unresolved.

- [ ] **Task Status:** pending

Run: `python3 -m unittest tests.test_module -v`

Expected: the targeted behavior test passes.
```

Keep `**Files:**`, `**Interfaces:**`, and `**Stop Conditions:**` as standalone lines exactly as shown. Never prefix these labels with `- `. Keep exactly one `Task Status` marker in each task.

For every task:

- list exact create, modify, delete, and test paths under `Files`
- list exact consumed and produced contracts or artifacts under `Interfaces`
- define one bounded behavior slice and its test or falsifiable proof intent
- use exactly one status checkbox: `- [ ] **Task Status:** pending` or `- [x] **Task Status:** completed`
- provide one exact `Run:` command, one `Expected:` signal, and concrete stop conditions

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

After the plan passes preflight, read `../superwork-executing-plans/SKILL.md` in full and pass the structured handoff defined by `superwork-start`, including the exact plan path and preflight evidence. If the user explicitly asks for a plan only or says not to implement, save the plan, report its path and preflight result, and stop.
