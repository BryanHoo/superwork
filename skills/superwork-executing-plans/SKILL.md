---
name: superwork-executing-plans
description: Use this skill to resume a previously saved, preflighted Superwork plan from its first unchecked task. Preserve serial task state, stop on plan drift, load TDD once for all code behavior slices, and hand the completed plan to final verification once.
---

# Superwork Executing Plans

## Purpose

Resume a saved implementation plan without repeating same-session planning or redefining TDD and completion rules.

## Entry

1. Read the exact saved plan path.
2. Run:

   ```bash
   python3 <skill_dir>/scripts/preflight_plan.py --root . --plan <plan-path> --format json
   ```

3. Continue when `ok` is `true`.
4. Create task tracking from the returned task list and resume from the first unchecked task in document order.

## Execute Tasks

Before the first code task, read `../superwork-tdd/SKILL.md` once and reuse it for all code behavior slices. For each unchecked task in document order:

1. Mark it in progress.
2. Re-read that task's files, behavior, proof, optional interfaces, and stop conditions.
3. For a code behavior slice, pass the structured handoff to the loaded TDD method and wait for its RED/GREEN/REFACTOR evidence.
4. For a non-code slice, execute its smallest falsifiable proof before and after the edit.
5. Treat a TDD GREEN command as the task proof when it is equivalent and no later edit invalidated it. Do not rerun an equivalent proof; run only a distinct or stale task proof.
6. Change its `Task Status` checkbox to completed only after the expected signal is observed.

After all tasks pass, read `../superwork-check/SKILL.md` once and pass the structured handoff defined by `superwork-start`, including plan completion and verification evidence.

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
