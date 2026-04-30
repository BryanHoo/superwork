---
name: superwork-init
description: Use when a project does not have `.superwork/`, when onboarding a repository into the superwork workflow, or when required `.superwork` workflow/spec documents are missing.
---

# Superwork Init

## Overview

Bootstrap the project-local `.superwork/` runtime so future work follows an explicit workflow instead of memory.

**Core principle:** Generate durable runtime artifacts inside the project. Do not keep template storage inside `.superwork/`.

## When to Use

Use when:
- Starting superwork in a repository for the first time
- `.superwork/` is missing entirely
- `.superwork/workflow.md` or `.superwork/spec/` is incomplete
- Migrating an ad-hoc project to the superwork workflow

Do not use when:
- The project already has a healthy `.superwork/` and you are starting a normal task
- You only need to update one spec document
- You only need to continue an existing feature or bugfix

## Quick Reference

| Artifact | Minimum Result |
|---|---|
| `.superwork/workflow.md` | Explains init, start, brainstorming, worktrees, writing-plans, executing-plans, tdd, debugging, code-simplifier, check, update-spec |
| `.superwork/spec/guides/` | Shared principles, thinking guides, and global checklists |
| `.superwork/spec/<layer>/index.md` | Single-repo layer guide entry with linked sub-guides |
| `.superwork/spec/<package>/<layer>/index.md` | Multi-package layer guide entry with linked sub-guides |
| Runtime output boundary | Only `.superwork/**` docs/spec are generated into the target project |

## Initialization Contract

Create this structure:

```text
.superwork/
├── workflow.md
└── spec/
    ├── guides/
    │   ├── index.md
    │   └── *.md
    ├── <layer>/
    │   ├── index.md
    │   └── *.md
    └── <package>/
        └── <layer>/
            ├── index.md
            └── *.md
```

Generated files are runtime artifacts. Do not generate `.superwork/templates/`, `.superwork/scripts/`, or `scripts/*.py` in the target project.

## Implementation

### Step 1: Inspect Before Creating

Check whether `.superwork/` already exists.

- If it is complete, report that initialization is already done and stop.
- If it is partial, repair only missing or outdated pieces.
- Do not overwrite project-written specs without an explicit reason.

### Step 2: Read the Project Shape

Inspect the repository to determine:

- Package manager
  - Prefer `pnpm` when present
- Whether the root project is itself a package
- Whether there are child packages or apps
- Likely layers per package
  - `frontend`
  - `backend`
  - `shared`
  - additional layers only when clearly justified
- Existing test commands and verification commands

When package boundaries are ambiguous, choose the simplest stable package map and document the assumption in generated files.

### Step 3: Generate `.superwork/workflow.md`

`workflow.md` must explain:

1. When to use `superwork-init`
2. When to start with `superwork-start`
3. When to use `superwork-brainstorming` for design-heavy feature work
4. When to use `superwork-using-git-worktrees` for isolated execution
5. When to use `superwork-writing-plans` and `superwork-executing-plans`
6. Why direct feature implementation can still use `superwork-tdd`
7. Why bugfix work defaults to `superwork-debugging`
8. Why `superwork-code-simplifier` needs an explicit execute-or-skip decision before `superwork-check`
9. Why completion requires `superwork-check`
10. Why completion requires an explicit `superwork-update-spec` decision (`update/create/no-update`) instead of defaulting to doc updates

Keep it project-local and actionable. It should read like an operating manual, not a manifesto.

### Step 4: Generate Spec Indexes

Always create:

- `.superwork/spec/guides/index.md`
- supporting guide docs under `.superwork/spec/guides/`

For a single-repo project, create:

- `.superwork/spec/<layer>/index.md`
- multiple linked layer docs such as structure, quality, and contract guides

For a multi-package project, create:

- `.superwork/spec/<package>/<layer>/index.md`
- multiple linked layer docs under each package/layer

Each package/layer index must contain:

1. `Scope`
2. `Pre-Development Checklist`
3. `Verification Checklist`
4. `Update Triggers`

Each checklist item should point to real files or concrete future placeholders, not vague text like "read relevant docs".

### Step 5: Replace Templates with Real Project Rules

Carefully read the repository and rewrite every generated template section into project-true rules.

- Replace generic statements with concrete project conventions and boundaries
- Replace placeholder checklists with real file paths, commands, and quality gates
- Ensure each package/layer index reflects the actual architecture and ownership

Do not leave template wording as-is when real project facts are already available.

### Step 6: Verify No Template Content Remains

Before claiming initialization complete, verify that no template placeholders or boilerplate-only wording remains in `.superwork/` docs.

1. Check for unresolved placeholders or generic "fill me later" wording
2. Check that checklists and links point to real project artifacts
3. Check that workflow/spec text is project-specific rather than template-generic

If any template content remains, return to Step 5 and continue replacement.
Only pass when all runtime docs are project-true.

### Step 7: Hand Off

After successful bootstrap, direct the next development entry to `superwork-start`.

## Common Mistakes

| Mistake | Why It Fails | Correct Move |
|---|---|---|
| Creating `.superwork/templates/` | Duplicates template storage inside the project | Keep templates in the skill, generate only results |
| Copying a fixed spec tree blindly | Mismatches the real package structure | Inspect the repository first |
| Treating root and child packages as mutually exclusive | Monorepos often need both | Support a root project and nested packages when present |
| Generating `.superwork/scripts/` | Splits the source of truth for tooling | Keep scripts in the skill's `scripts/` directory and only generate `.superwork` docs/spec |
| Writing `scripts/bootstrap_superwork.py` into the target repo | Leaks skill implementation details into project runtime | Keep `bootstrap_superwork.py` inside `skills/superwork-init/scripts/` only |
| Overwriting existing specs | Destroys project memory | Repair missing pieces, preserve authored content |

## Red Flags

- "I'll just make `.superwork/` manually later"
- "One generic `frontend/` folder is enough for every repo"
- "The scripts should be copied into `.superwork/` too"
- "The indexes can say 'read the right files' without listing them"

If you hear those thoughts, stop and finish the bootstrap properly.

## Integration

- `superwork-start` is the normal next step after this skill
- `superwork-tdd`, `superwork-debugging`, `superwork-check`, and `superwork-update-spec` all assume `.superwork/` already exists
