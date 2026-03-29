---
name: superwork-code-simplifier
description: "Simplifies recently touched code for clarity, consistency, and maintainability without changing behavior. Use after a green test pass, during the Refactor step of TDD, when a change works but feels harder to read than necessary, or before running final Superwork checks."
---

# Code Simplifier

Refine code that already works so it is easier to read, easier to maintain, and more consistent with the project.

## Core Rule

Do not change behavior.

This skill is for structure, naming, duplication, and readability improvements after the code is already correct.

## When to Use

- After `$superwork-tdd-core` reaches green and you are in the Refactor step
- Before `$superwork-check` or `$superwork-finish-work` if the touched code is still too dense
- When recently modified code has avoidable nesting, duplication, or awkward naming
- When a refactor is intentionally non-behavioral

## Superwork Adaptation

Before simplifying:

1. Read the relevant `.superwork/spec/` docs for the files you touched
2. Limit the scope to code changed in the current task unless the user asks for a broader pass
3. Preserve existing contracts, tests, logging behavior, and public interfaces

After simplifying:

1. Re-run the narrowest checks that proved the behavior
2. If the task is still in progress, continue with `$superwork-check`
3. If the task is otherwise complete, continue with `$superwork-finish-work`

## Refinement Priorities

### 1. Preserve Exact Behavior

- Keep all outputs, side effects, error semantics, and contracts unchanged
- Do not mix cleanup with feature work
- Do not widen scope just because related code also looks messy

### 2. Follow Project Standards

- Match patterns documented in `.superwork/spec/`
- Prefer explicit code over compressed code
- Keep import structure, naming, and file organization consistent with nearby code

### 3. Improve Readability

- Reduce unnecessary nesting
- Remove redundant abstractions
- Consolidate closely related logic
- Replace unclear names with clearer names when safe
- Remove comments that only restate the code
- Avoid nested ternary expressions when a clearer `if` chain or helper is better

### 4. Keep Refactors Debuggable

- Prefer changes that are easy to review
- Keep helper extraction local unless shared reuse is clearly justified
- Avoid clever one-liners that hide control flow

## Working Process

1. Identify the recently modified code
2. Note the behavior that must remain unchanged
3. Simplify only the parts that improve clarity or consistency
4. Re-run focused verification
5. Hand off to `$superwork-check` or `$superwork-finish-work`

## Output

Report:

1. what code was simplified
2. what stayed behaviorally unchanged
3. what verification was re-run
