---
name: superwork-code-simplifier
description: Use when recently modified code in a project that uses `.superwork/` needs behavior-preserving simplification after targeted verification is already green and before final completion, especially when the implementation diff is medium or large.
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
- The current implementation diff is medium or large, even if it already passes tests

Do not use when:
- Behavior is still changing
- The targeted verification is not green yet
- You want to widen the scope into unrelated cleanup
- The work is pure formatting with no meaningful simplification decision
- The diff is truly small and you can explain why no simplification pass is needed

## Quick Reference

| Phase | Required Action | Stop If |
|---|---|---|
| Context | Read the relevant `.superwork` guides and layer rules | You are simplifying against memory only |
| Scope | Limit work to recently touched code and classify the diff as small vs medium or large | You call a medium or large diff "small" just to skip cleanup |
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

Classify the current change size before deciding whether this skill can be skipped.

Treat the diff as medium or large when any of these are true:

- multiple files were changed for the same behavior slice
- the change crosses package, layer, or API boundaries
- control flow, branching, or helper structure changed in more than one place
- GREEN introduced temporary duplication, awkward naming, or obvious wrapper code that still remains
- the resulting diff takes real effort to scan end-to-end confidently

When any medium or large signal is present, you must run this skill before `superwork-check`.
Only a truly small diff may skip this skill, and the skip reason must explain why no behavior-preserving cleanup remains.

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
- if the diff was medium or large, do not describe this skill as "skipped"

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "It already works, no need to re-run tests" | Then you cannot prove the cleanup preserved behavior |
| "While I'm here I'll clean nearby files too" | Scope creep makes regressions harder to reason about |
| "Shorter code is always simpler" | Dense code often hides logic and increases risk |
| "This refactor is harmless" | Behavior-preserving changes still need verification |
| "I'll do the cleanup before the feature works" | That mixes implementation and refinement into one unverified step |
| "This change is probably small enough to skip" | Medium or large diffs must run this skill, not rationalize around it |

## Red Flags

- simplifying before the first green verification
- editing unrelated files for opportunistic cleanup
- replacing explicit flow with clever compact expressions
- making contract changes under the label of simplification
- classifying a medium or large diff as "small" without concrete evidence
- saying "done" before `superwork-check`

If any of these appear, stop and return to the correct workflow stage.

## Integration

- Usually follows `superwork-tdd` or `superwork-debugging`
- Can be included as a planned refactor step inside `superwork-writing-plans`
- Must finish with `superwork-check`
