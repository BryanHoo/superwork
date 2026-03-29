# Code Reuse Thinking Guide

> **Purpose**: Stop and think before creating new code - does it already exist?

---

## The Problem

**Duplicated code is the #1 source of inconsistency bugs.**

When you copy-paste or rewrite existing logic:
- Bug fixes don't propagate
- Behavior diverges over time
- Codebase becomes harder to understand

---

## Before Writing New Code

### Step 1: Search First

```bash
# Search for similar function names
grep -r "functionName" .

# Search for similar logic
grep -r "keyword" .
```

### Step 2: Ask These Questions

| Question | If Yes... |
|----------|-----------|
| Does a similar function exist? | Use or extend it |
| Is this pattern used elsewhere? | Follow the existing pattern |
| Could this be a shared utility? | Create it in the right place |
| Am I copying code from another file? | **STOP** - extract to shared |

---

## Common Duplication Patterns

### Pattern 1: Copy-Paste Functions

**Bad**: Copying a validation function to another file

**Good**: Extract to shared utilities, import where needed

### Pattern 2: Similar Components

**Bad**: Creating a new component that's 80% similar to existing

**Good**: Extend existing component with props/variants

### Pattern 3: Repeated Constants

**Bad**: Defining the same constant in multiple files

**Good**: Single source of truth, import everywhere

---

## When to Abstract

**Abstract when**:
- Same code appears 3+ times
- Logic is complex enough to have bugs
- Multiple people might need this

**Don't abstract when**:
- Only used once
- Trivial one-liner
- Abstraction would be more complex than duplication

---

## After Batch Modifications

When you've made similar changes to multiple files:

1. **Review**: Did you catch all instances?
2. **Search**: Run grep to find any missed
3. **Consider**: Should this be abstracted?

## Refinement Pass with `superwork-code-simplifier`

When the behavior is already correct but the touched code is still awkward:

1. Keep the scope to the code changed in the current task
2. Simplify structure, naming, and duplication without changing behavior
3. Re-run the narrowest checks
4. Continue to the normal quality pass

Use this for:

- non-behavioral cleanup after green
- reducing avoidable nesting
- replacing awkward local abstractions with clearer code

Do not use it to sneak in feature work or contract changes.

---

## Checklist Before Commit

- [ ] Searched for existing similar code
- [ ] No copy-pasted logic that should be shared
- [ ] Constants defined in one place
- [ ] Similar patterns follow same structure

---

## Template File Registration (Superwork-specific)

When adding new files to `src/templates/superwork/scripts/`:

**CRITICAL**: New script files must be registered in THREE places:

1. **`src/templates/superwork/index.ts`**:
   - Add `export const xxxScript = readTemplate("scripts/path/file.py");`
   - Add to `getAllScripts()` Map

2. **`src/commands/update.ts`**:
   - Add to import statement
   - Add to `collectTemplateFiles()` Map

**Why this matters**: Without registration, `superwork update` won't sync the file to user projects. Bug fixes and features won't propagate.

### Quick Checklist for New Scripts

```bash
# After adding a new .py file, verify:
grep -l "newFileName" src/templates/superwork/index.ts  # Should match
grep -l "newFileName" src/commands/update.ts          # Should match
```
