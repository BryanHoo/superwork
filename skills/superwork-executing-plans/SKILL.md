---
name: superwork-executing-plans
description: Use this skill to execute or resume a preflighted Superwork plan from its first unchecked task. Preserve serial task state, stop on plan drift, use TDD for each code behavior slice, and hand the completed plan to final verification once.
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
4. Create task tracking from the returned task list and resume from the first unchecked task in document order.

## Execute Tasks

For each unchecked task in document order:

1. Mark it in progress.
2. Re-read that task's files, interfaces, expected signal, and stop conditions.
3. For a code behavior slice, read `../superwork-tdd/SKILL.md` in full, pass the structured handoff, and wait for its RED/GREEN/REFACTOR evidence.
4. For a non-code slice, execute its smallest falsifiable proof before and after the edit.
5. Run the task-level verification from the plan.
6. Change its `Task Status` checkbox to completed only after the expected signal is observed.

After all tasks pass, read `../superwork-check/SKILL.md` in full and pass the structured handoff defined by `superwork-start`, including plan completion and verification evidence.

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
