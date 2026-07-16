---
name: superwork-executing-plans
description: Executes a preflighted saved plan. It tracks task order and plan drift, invokes `superwork-tdd` for code behavior slices, and hands completed work to one final check.
---

# Superwork Executing Plans

## Purpose

Coordinate a saved implementation plan without redefining design, TDD, debugging, or completion rules.

## Entry

1. Read the exact saved plan path.
2. Run:

   ```bash
   python3 <skill_dir>/scripts/preflight_plan.py --root . --plan <plan-path> --format json
   ```

3. Continue when `ok` is `true`.
4. Create task tracking from the saved task order and resume completed checkboxes instead of restarting work.

## Execute Tasks

For each dependency-ready task:

1. Mark it in progress.
2. Re-read that task's files, interfaces, expected signal, and stop conditions.
3. For a code behavior slice, invoke `superwork-tdd` and wait for its RED/GREEN/REFACTOR evidence.
4. For a non-code slice, execute its smallest falsifiable proof before and after the edit.
5. Run the task-level verification from the plan.
6. Mark the task complete only after the expected signal is observed.

After all tasks pass, route once to `superwork-check`.

## Plan Drift

Stop execution and repair the saved plan when:

- a referenced file, interface, or constraint is wrong
- implementation requires an unplanned independent behavior
- requirements or explicit user instructions changed
- verification repeatedly fails for a reason outside the current slice

Do not force execution through an invalid plan and do not silently redesign during implementation.

## Boundaries

- Work on the current branch unless the user explicitly requests another Git operation.
- Preserve unrelated user changes.
- Do not add commit steps unless requested by the user or project policy.
- Do not reproduce TDD internals; call the TDD method.
- Do not call completion more than once.
