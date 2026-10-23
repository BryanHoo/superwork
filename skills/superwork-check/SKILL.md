---
name: superwork-check
description: Use this skill to finalize completed repository changes or answer an explicit readiness request. Apply necessary in-scope simplification and durable spec updates by default, run fresh verification, validate final artifacts, and report completion evidence exactly once unless the user explicitly requires read-only checking.
---

# Superwork Check

## Purpose

Produce trustworthy completion evidence in one internal sequence. Enter after implementation/debugging or when the user explicitly requests final verification of existing changes.

## Change Policy

Apply necessary in-scope simplification and durable spec updates, then re-verify the resulting artifacts. For an explicit read-only request or an explicit instruction not to modify files, report recommended changes without applying them.

## Finalization Sequence

### Step 1: Gather context

Run:

```bash
python3 <skill_dir>/scripts/check_specs.py --root . --format json
```

Use its changed files, relevant spec candidates, verification hints, runtime status, and risks. Reuse already-read current project guidance; load missing global and applicable shared indexes, plus indexes and linked rules needed to judge the changed contracts. Do not read every returned reference merely because it is listed. On direct entry, use `superwork-start/scripts/get_context.py` for required context candidates.

Follow [parallel coordination](../superwork-start/references/parallel-coordination.md), loaded once per run before any finalization edit. Reuse the caller's notice and refresh current impacts before simplification or spec writes; on direct entry establish a notice only if this check will edit files. Explicitly read-only checks inspect summaries without registration or cleanup.

### Step 2: Inspect the diff

Review all current-task changes against the selected design or saved plan, project instructions, interfaces, and relevant specs. Separate unrelated user changes and preserve them.

Collect the TDD and task evidence ledger, including commands, results, covered inputs, and subsequent relevant edits. Identify missing behavior, tests, edge cases, contract drift, and scope expansion before reporting success.

### Step 3: Review simplification

Read [references/simplification-review.md](references/simplification-review.md) only when the diff shows duplication, excess nesting, unclear responsibilities, or other concrete complexity. Otherwise record `no-change` directly. Record exactly one outcome:

- `no-change`
- `changed`, followed by targeted re-verification
- `blocked`, returned to implementation or debugging with evidence

Diff size controls review depth, not whether code must change. This review never re-enters `superwork-check`.

During an explicitly read-only check, do not apply cleanup; report the concrete finding instead.

### Step 4: Run fresh verification

Before reusing earlier results, read [references/verification-evidence.md](references/verification-evidence.md) once per run and apply its freshness and equivalence conditions. Reuse valid TDD or task evidence; do not rerun an equivalent check solely because execution entered finalization. Run the commands still needed to prove the final state:

- targeted behavior or regression tests whose evidence is missing or invalidated
- broader tests when the change crosses boundaries and current evidence does not cover them
- lint, typecheck, build, schema, packaging, or render checks when applicable

Use project commands from the gathered config and relevant spec checklists. A targeted pass does not waive broader required gates. An explicit request to rerun checks requires fresh execution.

### Step 5: Decide spec

Run the target classifier first:

```bash
python3 <skill_dir>/scripts/update_spec.py --root . --format json
```

Use the script as a target suggestion, not the final judgment. Read [references/spec-update.md](references/spec-update.md) only when the classifier suggests `update` or `create`, or the diff reveals a durable contract, rule, or recurring failure mode despite a `no-update` suggestion. Choose `update`, `create`, or `no-update` and state the reason. Do not record transient implementation details as durable rules.

During an explicitly read-only check, do not edit specs. Report an `update` or `create` recommendation as unapplied, or choose `no-update` when no durable knowledge changed.

### Step 6: Validate spec artifacts

After `update` or `create`, confirm the document is reachable from the relevant index, contains concrete rules or verification guidance, and passes available documentation or structure checks.

If spec files change after code verification, run the checks needed to validate those final artifacts before completion.

### Step 7: Report

After required gates pass, persist shared-impact handoff and verification evidence in the existing plan, then finish only the notice identified by `evidence.parallelTask` using the coordination reference. Preserve it on failure or pause; do not remove notices during read-only checks. Report cleanup errors without claiming the notice was released.

Report findings before summary:

- failures or unresolved risks
- simplification outcome
- newly executed and reused commands, observed results, and reasons reused evidence remains valid
- spec outcome and changed spec paths
- remaining unverified surfaces

Do not claim completion when a required check failed, was skipped without reason, or remains stale.

## Boundaries

- Enter finalization once per completed task or plan.
- Do not call another completion skill and do not re-enter this skill.
- Do not force cleanup when the correct simplification outcome is `no-change`.
- Do not force a spec edit when the correct decision is `no-update`.
