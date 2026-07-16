---
name: superwork-check
description: Finalizes completed repository changes exactly once by reviewing simplification, running fresh verification, deciding durable spec updates, validating changed specs, and reporting evidence. It does not route to another completion skill.
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

Use its changed files, relevant specs, verification hints, runtime status, and risks. Read applicable spec indexes and concrete linked docs before judging the diff.

### Step 2: Inspect the diff

Review all current-task changes against the selected design or saved plan, project instructions, interfaces, and relevant specs. Separate unrelated user changes and preserve them.

Identify missing behavior, tests, edge cases, contract drift, and scope expansion before reporting success.

### Step 3: Review simplification

Read [references/simplification-review.md](references/simplification-review.md). Record exactly one outcome:

- `no-change`
- `changed`, followed by targeted re-verification
- `blocked`, returned to implementation or debugging with evidence

Diff size controls review depth, not whether code must change. This review never re-enters `superwork-check`.

During an explicitly read-only check, do not apply cleanup; report the concrete finding instead.

### Step 4: Run fresh verification

Run the commands that prove the claims being made now:

- targeted behavior or regression tests
- broader tests when the change crosses boundaries
- lint, typecheck, build, schema, packaging, or render checks when applicable

Use project commands from `.superwork/config.json` and relevant spec checklists. Earlier output is not fresh completion evidence.

### Step 5: Decide spec

Read [references/spec-update.md](references/spec-update.md), then run:

```bash
python3 <skill_dir>/scripts/update_spec.py --root . --format json
```

Use the script as a target suggestion, not the final judgment. Choose `update`, `create`, or `no-update` and state the reason. Do not record transient implementation details as durable rules.

During an explicitly read-only check, do not edit specs. Report an `update` or `create` recommendation as unapplied, or choose `no-update` when no durable knowledge changed.

### Step 6: Validate spec artifacts

After `update` or `create`, confirm the document is reachable from the relevant index, contains concrete rules or verification guidance, and passes available documentation or structure checks.

If spec files change after code verification, run the checks needed to validate those final artifacts before completion.

### Step 7: Report

Report findings before summary:

- failures or unresolved risks
- simplification outcome
- fresh commands and observed results
- spec outcome and changed spec paths
- remaining unverified surfaces

Do not claim completion when a required check failed, was skipped without reason, or remains stale.

## Boundaries

- Enter finalization once per completed task or plan.
- Do not call another completion skill and do not re-enter this skill.
- Do not force cleanup when the correct simplification outcome is `no-change`.
- Do not force a spec edit when the correct decision is `no-update`.
