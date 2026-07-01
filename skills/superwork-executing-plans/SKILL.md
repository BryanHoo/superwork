---
name: superwork-executing-plans
description: Use when a medium or heavy non-bug task in a project that uses `.superwork/` already has a written implementation plan ready to execute, whether continuing immediately after saving it or resuming later.
---

# Executing Plans

## Overview

Announce the skill, load the saved plan file, run one execution preflight pass against the plan and relevant specs, then start executing it immediately and report when complete. This skill consumes written plans from the medium or heavy path, not light-task inline TDD work.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Announce and Enter Execution

1. Read plan file，计划文件在 `.superwork/plans/<filename>.md`
2. Announce the exact plan path you are executing from
3. Run the execution preflight once before any code changes
4. Create TodoWrite from the saved tasks
5. Start the first task immediately

Use the skill-internal preflight script:

`<skill_dir>` means the directory containing this `SKILL.md`.

```bash
python3 <skill_dir>/scripts/preflight_plan.py --root . --plan .superwork/plans/<filename>.md --format json
```

The preflight owns one fast pass over:

- internal plan contradictions
- conflicts between `Global Constraints`, task `Interfaces`, and referenced spec paths
- obvious non-executable plan issues such as missing required sections, placeholders, or missing spec files

This is an execution entry step, not a human approval gate. Do not pause for approval, reassurance, or pre-execution debate once the saved plan exists.
If the preflight reports blocking issues, fix the plan or reroute before editing code. If it passes, move straight into execution.

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
- Preflight finds a structural or spec-alignment issue that must be repaired
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember

- Announce the execution handoff, then start from the saved plan immediately
- Run one execution preflight before the first task
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
