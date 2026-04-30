---
name: superwork-executing-plans
description: Use when a written implementation plan in a `.superwork` project is ready to execute sequentially with verification checkpoints.
---

# Superwork Executing Plans

## Overview

Load a written plan, validate it, execute it step-by-step, keep the file state current, and route to completion checks.

**Core principle:** Execute exactly, verify continuously, stop immediately on blockers.

## Process

### Step 1: Load and Review Plan

1. Read the plan file completely
2. Identify gaps, contradictions, or missing prerequisites
3. Confirm the checklist state is usable for execution tracking
4. If major issues exist, stop and ask for clarification

### Step 2: Ensure Isolated Workspace

Before task execution:
- invoke `superwork-using-git-worktrees` if isolation is not already in place
- confirm branch/worktree context and baseline status

### Step 3: Execute Tasks Sequentially

For each task:
1. mark in-progress in the plan file
2. execute each checklist step in order
3. run stated verification commands
4. mark complete in the plan file only after verification passes

The written plan remains the source of truth throughout execution. Do not drift into an unsaved side plan.

### Step 4: Handle Blockers Correctly

Stop and ask for help when:
- dependency/setup is missing
- plan instruction is ambiguous
- verification fails repeatedly
- the real code differs from plan assumptions

Do not guess or silently rewrite the plan intent.

### Step 5: Completion Handoff

When all plan tasks pass verification:
- follow the post-green completion step already written in the plan
- invoke `superwork-check`
- let `superwork-check` own final cleanup and the `superwork-update-spec` decision

If the plan does not contain an explicit post-green handoff, update the plan before claiming execution is complete.

## Common Mistakes

| Mistake | Why It Fails | Correct Move |
|---|---|---|
| Skip plan review | Hidden gaps appear mid-implementation | Review before first edit |
| Skip setup isolation | Branch state becomes hard to reason about | Use worktree skill first |
| Execute from memory | Checklist state and verification history drift | Re-open and update the plan file |
| Continue through blockers | Produces unverified drift | Stop and clarify |
| Let the last task drift out of the plan | Completion rules move back into chat memory | Fix the plan's post-green handoff first |
| Claim done before check stage | Workflow remains incomplete | Route to `superwork-check` |

## Integration

- Consumes written plans from `superwork-writing-plans` or `superwork-tdd`
- Uses `superwork-using-git-worktrees` for isolation
- Expects the plan itself to encode the post-green cleanup/check handoff
- Must hand off to `superwork-check`
