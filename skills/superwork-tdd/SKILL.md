---
name: superwork-tdd
description: Use this skill to implement one bounded behavior slice with RED, GREEN, and behavior-preserving REFACTOR. Apply it to a direct small change, a saved-plan task, or a confirmed bug repair; return evidence to the caller and leave root-cause analysis, planning depth, and finalization to their owners.
---

# Superwork TDD

## Purpose

Provide one implementation method for every code behavior change. TDD is not limited to light tasks; task size only determines how much design and planning happens before this method is called.

## Inputs

The caller provides:

- one bounded behavior slice
- relevant files, contracts, and project rules
- a falsifiable expected outcome
- the verification command or the smallest reliable way to derive it
- the caller identity: `user`, `superwork-start`, `superwork-executing-plans`, or `superwork-debugging`

Do not use this skill while root cause is unknown or architecture is unresolved. Return those cases to debugging or design/planning.

## Method

### 1. Define the proof

State the smallest observable behavior that distinguishes success from failure. For code behavior, prefer an automated test. For documentation, configuration, or copy, use a focused lint, render, build, snapshot, schema check, or search assertion.

### 2. Establish RED

Write the smallest proof and run it. Confirm it fails for the intended missing or broken behavior, not because of syntax, fixture, environment, or unrelated failures.

Do not add production implementation for the current slice before a valid RED. Never revert pre-existing user changes; isolate the proof around them.

### 3. Reach minimal GREEN

Implement only what the current proof requires. Do not add speculative flags, abstractions, compatibility branches, or unrelated cleanup.

Run the targeted proof again and confirm it passes.

### 4. REFACTOR on green

Improve names, duplication, nesting, or local structure only when the result is clearer and behavior remains unchanged. Re-run the targeted proof after each meaningful refactor.

### 5. Return to the caller

Return:

- RED command and intended failure reason
- GREEN command and pass signal
- files changed
- any refactor performed
- remaining risks or broader checks still owned by the caller

`superwork-start` sends a completed light slice to `superwork-check`. `superwork-executing-plans` resumes the next saved-plan task. `superwork-debugging` confirms the regression repair and then hands completion to `superwork-check`. A direct `user` call reads `../superwork-check/SKILL.md` in full after GREEN unless the user explicitly limits the outcome.

## Stop Conditions

- RED cannot be made to fail for the intended reason.
- The behavior slice requires unresolved architecture or additional independent behavior.
- A failure is flaky, environmental, or contradicts the confirmed debugging hypothesis.
- GREEN requires widening the approved scope.

Stop and return evidence to the caller instead of guessing.
