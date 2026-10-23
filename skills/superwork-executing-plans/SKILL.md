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
5. Load applicable rules from the plan's `Suggested Spec Reads` that are not already current in context. On a new run, reload binding guidance and re-establish verification evidence; completion checkboxes alone are not proof of the current state.

## Execute Tasks

Before the first code task, read `../superwork-tdd/SKILL.md` once per run in full and reuse it for later slices. Before reusing a verification result, read [the evidence policy](../superwork-check/references/verification-evidence.md) once per run. For each unchecked task in document order:

1. Mark it in progress.
2. Re-read that task's files, interfaces, expected signal, and stop conditions.
3. For a code behavior slice, pass the structured handoff to the loaded TDD method and wait for its RED/GREEN/REFACTOR evidence.
4. For a non-code slice, execute its smallest falsifiable proof before and after the edit.
5. Reuse TDD GREEN as task-level verification only when the evidence policy permits it and it proves the plan's exact `Expected` signal. Otherwise run the missing, distinct, or stale task-level verification. Record the observed result and why any reused evidence remains valid.
6. Change its `Task Status` checkbox to completed only after the expected signal is observed.

After all tasks pass, read `../superwork-check/SKILL.md` once per run in full and pass the structured handoff defined by `superwork-start`, including plan completion and the evidence ledger. When pausing or handing off to another executor, save evidence notes with the relevant task in the same plan; they aid recovery but require revalidation in the new run.

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
