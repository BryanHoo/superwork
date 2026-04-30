---
name: superwork-tdd
description: Use when implementing a feature, behavior change, or planned refactor in a project that uses `.superwork/`, before writing implementation code.
---

# Superwork TDD

## Overview

Implement feature work with a test-first loop anchored to `.superwork` context by writing a plan file first and executing from that file.

**Core principle:** No implementation code without a saved TDD plan whose first executable step is a failing test.

**Violating the letter of the rules is violating the spirit of this skill.**

## When to Use

Use when:
- Adding a new feature
- Changing behavior intentionally
- Implementing a user-facing requirement
- Refactoring while preserving or clarifying behavior

Do not use when:
- The work is primarily debugging a bug or failing test
- The project has not been initialized with `.superwork/`
- The change is pure formatting with no behavior impact

If the task turns out to be a bug investigation, stop and switch to `superwork-debugging`.

## The Iron Law

```text
NO IMPLEMENTATION CODE WITHOUT A SAVED TDD PLAN FILE FIRST
```

Saved means a real file on disk under `.superwork/plans/`.

These do not count:
- a chat-only outline
- an inline tool plan
- a remembered step list
- "I'll save it right after the first RED test"

No exceptions:
- not for "small" features
- not for "obvious" changes
- not for "just wiring"
- not by drafting production code as "reference"
- not by writing the RED test before the plan file exists

## Quick Reference

| Phase | Required Action | Stop If |
|---|---|---|
| Context | Read relevant `.superwork` indexes and rules | You have not loaded the required reads |
| Plan | Save a written plan under `.superwork/plans/` | You are about to write any test or implementation code without a saved plan |
| Review | Verify the first executable task is RED | The plan starts with implementation or vague tasks |
| Execute | Invoke `superwork-executing-plans` with the saved plan | You are about to start RED from memory, chat state, or an unsaved plan |
| Verify | Let the plan drive targeted and broader checks | Verification is missing from the written tasks |
| Simplify | Invoke `superwork-code-simplifier` if green code still needs cleanup, otherwise state why it is skipped | Cleanup starts before behavior is verified or is skipped silently |
| Handoff | Route to `superwork-check` after plan execution | You are about to claim completion directly |

## Implementation

### Step 1: Load the Relevant Rules

Before planning, read:

- `.superwork/spec/guides/index.md`
- the package/layer index files identified by `superwork-start`
- any concrete spec docs listed by those indexes

Do not rely only on memory from a prior session.

### Step 2: Create the Plan File

Save a plan file to:

`.superwork/plans/YYYY-MM-DD-<feature-name>.md`

Create the directory if it does not exist.

Until this file is saved, you are still in pre-execution.
Do not write tests, scaffolding, TODO code, or scratch implementation before the file exists on disk.

The plan should:

- contain 3-7 concrete steps
- use checkbox tracking with `- [ ]`
- identify the first failing test step explicitly
- identify the implementation verification step explicitly
- include exact file paths and concrete commands
- include expected pass/fail signals for each verification step
- stay scoped to the current behavior slice

Reuse the `superwork-writing-plans` file format. For direct feature work, the tasks must stay TDD-shaped.

Good plan shape:

1. Add and run a failing test for the new behavior
2. Implement the smallest code to satisfy it
3. Re-run the targeted verification and record the expected green signal
4. Refine names or structure only if tests stay green
5. Run broader verification and hand off to `superwork-check`

### Step 3: Review the Plan Before Execution

Before any code change, confirm:

- the first executable task is RED, not implementation
- every implementation step has an adjacent verification command
- no task contains placeholders, memory-only intent, or "figure it out later" wording
- the last task routes to `superwork-check`
- you have not already started RED in chat state before saving the file

If the plan fails any of these checks, fix the file first.

### Step 4: Start Execution from the Plan File

After saving the plan:

- announce the plan path
- reopen or reread the saved file
- invoke `superwork-executing-plans`
- execute from the file, not from memory and not from an inline tool plan

Do not begin RED directly in chat state before or after the plan file exists. The saved file is the execution source of truth, and RED starts only from that file.

### Step 5: RED Inside Plan Execution

Write one minimal test for one behavior.

Requirements:

- clear behavior name
- real behavior, not a mock maze
- minimal setup
- failure proves the feature is missing or wrong

Then run the targeted test command and confirm:

- it fails
- it fails for the expected reason
- it is not a typo, import, or environment failure

If it passes immediately, you are testing existing behavior. Fix the test.

### Step 6: GREEN - Write Minimal Code

Write the smallest implementation that satisfies the failing test.

Do not:

- add extra options "for future use"
- refactor unrelated code
- widen scope because "you're already here"

If you need a second behavior, finish the first cycle first.

### Step 7: Verify GREEN

Run the targeted test again.

Confirm:

- the RED test now passes
- related tests still pass
- the output is clean enough to trust

If other tests fail, fix them before continuing.

### Step 8: REFACTOR Carefully

Only after green:

- remove duplication
- improve names
- extract helpers
- simplify structure

Every refactor must keep tests green.

### Step 9: Repeat or Handoff

If more behavior remains, start a fresh RED cycle.

Add the next behavior as a new checked task sequence in the same plan file or a follow-up plan file, then continue through `superwork-executing-plans`.

When the requested behavior is complete, make an explicit `superwork-code-simplifier` decision before `superwork-check`.

- invoke it when the recently touched code still needs behavior-preserving cleanup
- otherwise, state why the current diff does not need `superwork-code-simplifier`

Do not declare the work complete before the check stage.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "This is too small for TDD" | Small changes still regress behavior |
| "I'll write tests after the code" | Tests-after cannot prove the test catches the change |
| "The API is obvious, I'll just scaffold first" | Scaffolding production code before RED is still a violation |
| "I already know which files to edit" | Knowing the file is not the same as proving the behavior |
| "The plan can stay in my head" | Hidden plans drift immediately |
| "The inline tool plan is enough" | The executable source of truth must be the saved plan file |
| "I'll save the plan later after the first test" | That still starts execution without the required written workflow |
| "I'll just write the failing test first, then document the plan" | RED is execution and cannot start before the saved file exists |

## Red Flags

- writing production code before the saved plan file exists
- writing test code before the saved plan file exists
- starting execution from memory instead of reopening the saved plan
- a plan whose first executable task is implementation, not RED
- writing production code before the failing test
- a test that passes on first run
- adding options, flags, or abstractions not required by the current test
- saying "done" before `superwork-check`

If any of these happen, stop and return to the correct phase.

## Integration

- `superwork-start` should have already loaded the correct context
- `superwork-writing-plans` provides the canonical file format for the saved plan
- `superwork-executing-plans` is REQUIRED after saving the plan file
- `superwork-code-simplifier` needs an explicit execute-or-skip decision after green verification
- `superwork-check` is REQUIRED after completing the RED-GREEN-REFACTOR cycles
- `superwork-update-spec` is handled by `superwork-check`, not by this skill directly
