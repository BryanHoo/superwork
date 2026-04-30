---
name: superwork-code-simplifier
description: Use when recently modified code in a project that uses `.superwork/` needs behavior-preserving simplification after targeted verification is already green and before final completion.
---

# Superwork Code Simplifier

## Overview

Refine recently touched code for clarity and consistency without changing behavior.

**Core principle:** No simplification pass without a verified green baseline first.

## When to Use

Use when:
- A feature or bugfix is already working
- Recently modified code still has avoidable complexity
- You need a constrained cleanup before final completion
- The task would benefit from clearer names, flatter flow, or less duplication

Do not use when:
- Behavior is still changing
- The targeted verification is not green yet
- You want to widen the scope into unrelated cleanup
- The work is pure formatting with no meaningful simplification decision

## Quick Reference

| Phase | Required Action | Stop If |
|---|---|---|
| Context | Read the relevant `.superwork` guides and layer rules | You are simplifying against memory only |
| Scope | Limit work to recently touched code | You start cleaning unrelated files |
| Baseline | Confirm targeted verification already passes | You cannot prove current behavior |
| Simplify | Reduce complexity without changing outputs or contracts | You are adding new behavior or abstractions |
| Re-verify | Re-run the relevant checks after simplification | Green status is assumed instead of checked |
| Handoff | Route to `superwork-check` | You are about to claim completion directly |

## Implementation

### Step 1: Reload the Relevant Rules

Read:

- `.superwork/spec/guides/index.md`
- the package/layer indexes identified by `superwork-start` or `superwork-check`
- any concrete guideline docs that govern the touched files

Simplification is still implementation work. It must follow the same local rules as the original change.

### Step 2: Freeze the Scope

Work only on code that was recently modified for the current task.

Typical scope signals:

- files already changed in the current branch
- code touched during the current session
- the smallest surrounding block required to make the simplification coherent

Do not turn this skill into a repo-wide cleanup pass unless explicitly asked.

### Step 3: Confirm the Green Baseline

Before editing:

- identify the targeted verification command that already passed
- confirm the current code is behaviorally correct
- keep the simplification anchored to that proven behavior

If the code is not verified yet, return to `superwork-tdd` or `superwork-debugging` first.

### Step 4: Apply Behavior-Preserving Simplification

Prefer changes that:

- reduce unnecessary nesting
- remove redundant branches, variables, or wrappers
- improve names where the intent is unclear
- keep related logic together
- replace clever compactness with explicit control flow
- align the code with project conventions from `AGENTS.md`

Avoid changes that:

- alter outputs, contracts, or side effects
- introduce speculative abstractions
- combine unrelated responsibilities
- optimize for fewer lines instead of readability
- hide branching inside nested ternaries or dense one-liners

### Step 5: Re-Verify Immediately

After each meaningful simplification pass, re-run the most relevant checks.

At minimum:

- rerun the targeted test or regression command
- rerun broader verification when the simplified code crosses boundaries

If verification fails, stop treating the change as simplification and debug the regression directly.

### Step 6: Handoff

Once the code is simpler and the checks are green:

- summarize only meaningful structural changes
- route to `superwork-check`

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "It already works, no need to re-run tests" | Then you cannot prove the cleanup preserved behavior |
| "While I'm here I'll clean nearby files too" | Scope creep makes regressions harder to reason about |
| "Shorter code is always simpler" | Dense code often hides logic and increases risk |
| "This refactor is harmless" | Behavior-preserving changes still need verification |
| "I'll do the cleanup before the feature works" | That mixes implementation and refinement into one unverified step |

## Red Flags

- simplifying before the first green verification
- editing unrelated files for opportunistic cleanup
- replacing explicit flow with clever compact expressions
- making contract changes under the label of simplification
- saying "done" before `superwork-check`

If any of these appear, stop and return to the correct workflow stage.

## Integration

- Usually follows `superwork-tdd` or `superwork-debugging`
- Can be included as a planned refactor step inside `superwork-writing-plans`
- Must finish with `superwork-check`
