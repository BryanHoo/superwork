---
name: superwork-check
description: Use when changes in a `.superwork` project are ready for verification, before claiming completion, handing off work, or moving to the next task.
---

# Superwork Check

## Overview

Verify that the changes satisfy fresh evidence requirements and the relevant `.superwork` specs before any completion claim.

**Core principle:** No completion claims without fresh verification evidence and spec review.

**Violating the letter of this rule is violating the spirit of this rule.**

## When to Use

Use when:
- finishing a feature cycle from `superwork-tdd`
- finishing a bugfix from `superwork-debugging`
- preparing to report work as complete
- preparing to hand off work for review or commit

Do not use when:
- the implementation or debugging loop is still actively incomplete
- the project has not been initialized with `.superwork/`

## The Iron Law

```text
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE AND SPEC REVIEW
```

If you did not run the relevant checks now, you cannot say the work is complete now.

## Quick Reference

| Claim | Required Evidence |
|---|---|
| "Skipped `superwork-code-simplifier`" | explicit reason the current diff does not need behavior-preserving cleanup |
| "Tests pass" | fresh test command output |
| "Bug is fixed" | regression test passes and original symptom is gone |
| "Code follows project rules" | relevant spec indexes and docs reviewed against the diff |
| "Ready to hand off" | verification commands completed and risks reported |
| "Done" | all above, plus `superwork-update-spec` decision completed |

## Implementation

### Step 1: Decide `superwork-code-simplifier` Before Verification

Before running the check itself:

- inspect the current diff and recently touched code
- invoke `superwork-code-simplifier` if behavior-preserving cleanup is still needed
- otherwise, state why the current diff does not need `superwork-code-simplifier`

Do not enter verification with this decision left implicit.

### Step 2: Gather Structured Spec Context

Run:

`<skill_dir>` means the directory containing this `SKILL.md` (skill root).

```bash
python3 <skill_dir>/scripts/check_specs.py --root . --format json
```

Use it to identify:

- changed files
- relevant spec indexes or docs
- verification hints
- risk hints

If the script cannot provide JSON, use the human-readable output and note that the bootstrap needs repair later.

If the bootstrap tooling itself is missing or misplaced, switch to `superwork-init` and repair `.superwork/` there.

### Step 3: Read the Relevant Specs

Read:

- `.superwork/spec/guides/index.md`
- each relevant package/layer index from `<skill_dir>/scripts/check_specs.py`
- each concrete spec doc referenced by those indexes that applies to the changed area

Do not treat the index alone as enough if it points to deeper docs.

### Step 4: Run Fresh Verification

Run the commands that actually prove the claims you want to make.

Typical categories:

- targeted tests
- broader regression tests when needed
- lint
- typecheck
- build or packaging checks when relevant

Use project-local commands and package manager hints from `<skill_dir>/scripts/get_context.py`.

### Step 5: Review Against the Specs

Compare the actual diff and behavior against:

- required rules
- contracts
- examples
- verification checklist items

Look specifically for:

- spec violations
- missing tests
- uncovered edge cases
- cross-layer contract drift

### Step 6: Report Findings First

If you find issues, report them before summaries.

Include:

- what failed
- what was verified successfully
- what remains risky

Do not hide uncertainty behind positive phrasing.

### Step 7: Complete `superwork-update-spec` Decision

Do not stop after verification.

After the check is complete, run `superwork-update-spec` once to force an explicit decision:
- `update`
- `create`
- `no-update`

Do not default to doc updates. Use `no-update` when no durable rule/contract/edge-case/test requirement was introduced.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The targeted test passed, so we're done" | One check does not prove spec compliance or broader readiness |
| "I ran those commands earlier" | Earlier evidence is stale evidence |
| "The diff is small, review is unnecessary" | Small diffs still violate contracts |
| "The cleanup is probably unnecessary" | Then state why before verification instead of skipping silently |
| "The user can decide whether to update specs later" | This workflow requires the decision now |
| "I know the code is fine" | Confidence is not verification |

## Red Flags

- saying "done" before running fresh commands
- entering `superwork-check` without a `superwork-code-simplifier` decision
- reading no spec files during a `.superwork` workflow
- trusting only memory of earlier verification
- reporting success before listing failures or risks
- stopping before `superwork-update-spec` decision

Any of these means the check is incomplete.

## Integration

- `superwork-tdd` and `superwork-debugging` both hand off here
- `superwork-update-spec` decision is REQUIRED at the end of this stage
