---
name: superwork-check
description: Use this skill to finalize completed repository changes or answer an explicit readiness request. Reuse current TDD evidence, add only risk-relevant verification, load simplification or spec guidance conditionally, and report completion evidence exactly once unless the user explicitly requires read-only checking.
---

# Superwork Check

## Purpose

Produce trustworthy completion evidence in one internal sequence. Enter after implementation/debugging or when the user explicitly requests final verification of existing changes.

## Change Policy

Apply necessary in-scope simplification and durable spec updates only when the diff provides a concrete signal. For an explicit read-only request or an explicit instruction not to modify files, report recommended changes without applying them.

## Finalization Sequence

### Step 1: Gather context

Run:

```bash
python3 <skill_dir>/scripts/check_specs.py --root . --format json
```

Use its changed files, relevant spec candidates, verification hints, runtime status, and risks. Do not read every returned spec; load only the entries needed to judge a concrete changed contract or project rule.

### Step 2: Inspect diff and evidence

Review all current-task changes against the request, optional saved plan, project instructions, interfaces, and already loaded relevant specs. Separate unrelated user changes and preserve them.

Build an evidence ledger containing each TDD RED/GREEN command, the last relevant edit, and any broader check already run. Identify missing behavior, tests, edge cases, contract drift, and scope expansion before reporting success.

### Step 3: Review simplification when needed

Read [references/simplification-review.md](references/simplification-review.md) only when the changed code presents concrete duplication, excess nesting, speculative abstraction, or local complexity. Otherwise record `no-change` directly. Record exactly one outcome:

- `no-change`
- `changed`, followed by targeted re-verification
- `blocked`, returned to implementation or debugging with evidence

Diff size controls review depth, not whether code must change. This review never re-enters `superwork-check`.

During an explicitly read-only check, do not apply cleanup; report the concrete finding instead.

### Step 4: Complete verification

Accept a targeted TDD proof as current when it ran after the last relevant code or test edit. Do not rerun an equivalent targeted proof. Run only the commands still needed to prove the final state:

- a targeted behavior or regression test when the prior proof is stale or missing
- broader tests when the change crosses boundaries and they are not already current
- lint, typecheck, build, schema, packaging, or render checks when applicable

Use project commands from the gathered context and relevant spec checklists. Evidence from before the last relevant edit is stale.

### Step 5: Decide durable spec

Run the deterministic classifier first:

```bash
python3 <skill_dir>/scripts/update_spec.py --root . --format json
```

Use the script as a target suggestion, not the final judgment. Read [references/spec-update.md](references/spec-update.md) only when its decision is `update` or `create`. Choose `update`, `create`, or `no-update` and state the reason. Do not record transient implementation details as durable rules.

During an explicitly read-only check, do not edit specs. Report an `update` or `create` recommendation as unapplied, or choose `no-update` when no durable knowledge changed.

After `update` or `create`, confirm the document is reachable from the relevant index, contains concrete rules or verification guidance, and passes available documentation or structure checks. If spec files change after code verification, run only the checks needed to validate those final artifacts.

### Step 6: Report

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
