---
name: superwork-debugging
description: Use when fixing a bug, failing test, regression, or unexpected behavior in a project that uses `.superwork/`, before proposing or applying fixes.
---

# Superwork Debugging

## Overview

Fix bugs by finding root cause first, then reproducing the issue with a failing test, then implementing one repair.

**Core principle:** No fixes without root-cause investigation first.

**Violating the letter of this process is violating the spirit of debugging.**

## When to Use

Use when:
- A test is failing unexpectedly
- A feature regressed
- The app behaves differently than intended
- A build, integration, or runtime path is broken
- A production issue needs a real fix

Do not use when:
- You are adding net-new behavior
- The work is purely planned feature development
- The project has not been initialized with `.superwork/`

## The Iron Law

```text
NO FIXES WITHOUT ROOT-CAUSE INVESTIGATION FIRST
```

If you have not completed the investigation, you cannot propose or apply the fix.

## Quick Reference

| Phase | Required Action | Success Criteria |
|---|---|---|
| Context | Read relevant `.superwork` rules and indexes | You know which rules and contracts apply |
| Reproduce | Make the issue happen reliably | You can state exact steps |
| Investigate | Read errors, compare patterns, trace data flow | You understand where and why it breaks |
| Hypothesis | Form one explanation and test it minimally | One cause is confirmed or rejected |
| Regression Test | Capture the bug with a failing test | The test proves the bug exists |
| Fix | Change one thing at the root cause | Bug is fixed without collateral damage |
| Simplify | Invoke `superwork-code-simplifier` after the fix is green, or state why it is skipped | Cleanup starts before the regression is proven fixed or is skipped silently |
| Handoff | Route to `superwork-check` | You are no longer relying on intuition |

## Implementation

### Step 1: Load the Relevant Rules

Read:

- `.superwork/spec/guides/index.md`
- the relevant package/layer indexes
- any concrete spec docs related to the broken path

The investigation should happen in the context of project rules, not just stack traces.

### Step 2: Reproduce the Problem Reliably

Establish:

- exact steps
- expected result
- actual result
- whether the issue is deterministic

If the problem is not reproducible yet, gather more evidence. Do not guess.

### Step 3: Investigate Before Fixing

Always do these before proposing a repair:

1. Read the full error or failure output
2. Check recent changes
3. Trace the data or control flow
4. Compare against a working pattern in the same codebase

For multi-layer systems, gather evidence at boundaries instead of guessing which layer is wrong.

### Step 4: Form One Hypothesis

State one cause clearly:

> I think X is the root cause because Y.

Then test the smallest possible change or observation that could confirm or reject it.

Do not stack multiple fixes.

### Step 5: Capture the Bug With a Failing Test

Before the real fix, add the smallest stable test that reproduces the bug.

Requirements:

- one bug behavior
- deterministic when possible
- failure proves the issue still exists

If no automated test framework exists, use the smallest reproducible script, but still make the failure concrete.

### Step 6: Fix One Root Cause

Apply one repair that addresses the confirmed cause.

Do not bundle:

- opportunistic refactors
- "cleanup while here"
- secondary fixes you did not prove necessary

### Step 7: Verify and Handoff

Verify:

- the regression test now passes
- related checks still pass
- no obvious new failures were introduced

Then route automatically to `superwork-check`.

Before `superwork-check`, make an explicit `superwork-code-simplifier` decision:

- run it when the repaired area still needs behavior-preserving cleanup
- otherwise, state why the current diff does not need `superwork-code-simplifier`

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The fix is obvious" | Symptoms are not root cause |
| "I'll try one quick patch first" | That is guess-and-check, not debugging |
| "I can skip the regression test" | Then you cannot prove the fix or prevent recurrence |
| "Three failed fixes means try harder" | Three failed fixes often means the model is wrong |
| "I already know the pattern" | Compare against a working example anyway |

## Red Flags

- proposing a fix before reproduction
- changing multiple things at once
- no regression test for the bug
- "one more attempt" after repeated failed fixes
- saying "probably fixed" before verification

If any of these appear, return to investigation.

## Integration

- `superwork-start` should have routed bug work here
- `superwork-code-simplifier` requires an explicit execute-or-skip decision after green verification
- `superwork-check` is REQUIRED after the fix is verified
- `superwork-update-spec` is triggered later through the check stage
