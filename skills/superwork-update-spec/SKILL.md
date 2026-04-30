---
name: superwork-update-spec
description: Use when implementation or debugging in a `.superwork` project introduced new rules, contracts, edge cases, or verification requirements that may need to be captured in `.superwork/spec/`.
---

# Superwork Update Spec

## Overview

Capture durable project knowledge in `.superwork/spec/` while the implementation context is still fresh.

**Core principle:** Always make the decision explicit, but only update spec for durable project knowledge.

## When to Use

Use when changes introduced or clarified:
- a new rule
- a new contract
- a new edge case
- a new testing requirement
- a new pitfall or failure mode
- a new package/layer convention

Do not use when the change is only:
- formatting
- renaming with no behavioral meaning
- internal cleanup with no lasting rule or contract

In the normal workflow, this skill is called by `superwork-check` to make an explicit decision, and may end with `no-update`.

## Quick Reference

| Change Type | Update? |
|---|---|
| New API/CLI/config contract | Yes |
| New validation or error behavior | Yes |
| Important bug lesson that should prevent recurrence | Yes |
| New required test category or assertion point | Yes |
| Pure formatting or file moves with no rule change | Usually no |

## Implementation

### Step 1: Ask the Project for Likely Targets

Run:

`<skill_dir>` means the directory containing this `SKILL.md` (skill root).

```bash
python3 <skill_dir>/scripts/update_spec.py --root . --format json
```

Use the output to identify:

- `decision`
- `targets`
- `ignoredChanges`
- `summary`

The script suggests likely spec targets. It does not own the final judgment.
If all detected changes are non-durable (for example tests, docs, lockfiles, or files already under `.superwork/spec/`), it should return `no-update`.

### Step 2: Make the Update Decision Explicit

Choose one of these outcomes:

- `update`
- `create`
- `no-update`

Never leave the decision implied.

If the answer is `no-update`, state why the change does not create durable project knowledge.

### Step 3: Update Concrete Spec Files

When updating or creating spec docs, keep them executable and specific.

Prefer adding concrete content to these sections:

- `Rules`
- `Contracts`
- `Good Examples`
- `Bad Examples`
- `Test Notes`
- `Update Notes`

Avoid vague lessons like "be careful here". Replace them with exact constraints, example inputs, expected outputs, or explicit verification points.

### Step 4: Keep the Indexes Usable

If you add or create a spec doc, update the relevant package/layer `index.md` when needed.

Make sure:

- the doc is reachable from the index
- `Pre-Development Checklist` points to it when appropriate
- `Verification Checklist` references it when appropriate
- `Update Triggers` reflect the new rule or contract

### Step 5: Report the Result

Report one of:

- what spec files were updated and why
- what file was created and why
- why no update was needed

Do not silently skip this stage.

## Common Mistakes

| Mistake | Why It Fails | Correct Move |
|---|---|---|
| Treating spec updates as optional cleanup | Knowledge is lost immediately | Make the decision now |
| Writing principle-only text | Future sessions cannot act on it | Add concrete rules, contracts, and examples |
| Updating only the leaf doc, not the index | Future readers cannot discover it | Update the index when discovery changes |
| Recording every tiny code change | Specs become noisy and ignored | Capture only durable rules and contracts |
| Saying "no update" without reason | Hides missing project memory | State the reason explicitly |

## Red Flags

- "The code itself is enough documentation"
- "I'll remember this edge case next time"
- "This bug lesson is too small to record"
- "I updated the spec doc, but not the index"
- "No update needed" with no written reason

These all mean the spec decision is incomplete.

## Integration

- `superwork-check` should call this for an explicit decision
- `superwork-start` benefits from every correct update made here
