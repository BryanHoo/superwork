---
name: superwork-executing-plans
description: Use when a medium or heavy non-bug task in a project that uses `.superwork/` already has a written implementation plan ready to execute, whether continuing immediately after saving it or resuming later.
---

# Executing Plans

## Overview

Announce the skill, load the saved plan file, start executing it immediately, and report when complete. This skill consumes written plans from the medium or heavy path, not light-task inline TDD work.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Announce and Enter Execution

1. Read plan file，计划文件在 `.superwork/plans/<filename>.md`
2. Announce the exact plan path you are executing from
3. Create TodoWrite from the saved tasks
4. Start the first task immediately

This is an execution entry step, not a review gate. Do not pause for approval, reassurance, or pre-execution debate once the saved plan exists.
If you notice doubts while loading the plan, record them briefly and keep moving into execution. Only stop once a real blocker prevents the next step from running.

### Step 2: Execute Tasks

For each task:

1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Complete Development

After all tasks complete and verified:

- Announce: "I'm routing completion through `superwork-check`."
- Route directly to `superwork-check`
- Let `superwork-check` decide whether `superwork-code-simplifier` must run
- Complete the explicit `superwork-update-spec` decision required at the end of `superwork-check`

## When to Stop and Ask for Help

**STOP executing immediately when:**

- Hit a blocker (missing dependency, test fails, instruction unclear)
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to the saved plan file when:**

- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember

- Announce the execution handoff, then start from the saved plan immediately
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Work on the current branch unless the user explicitly says otherwise

## Integration

**Required workflow skills:**

- **superwork-writing-plans** - Creates the plan this skill executes, either for immediate continuation or later handoff
- **superwork-code-simplifier** - May be invoked by `superwork-check` when medium or large diffs, or smaller diffs with cleanup needs, require a behavior-preserving simplification pass
- **superwork-check** - REQUIRED final verification stage after implementation tasks
- **superwork-update-spec** - REQUIRED explicit decision at the end of `superwork-check`
