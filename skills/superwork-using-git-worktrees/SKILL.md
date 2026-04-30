---
name: superwork-using-git-worktrees
description: Use when implementation should run in an isolated branch workspace before plan execution in a `.superwork` project.
---

# Superwork Using Git Worktrees

## Overview

Create an isolated workspace with a clean baseline before implementation.

**Core principle:** deterministic directory selection + safety checks + baseline verification.

## Directory Selection

Use this priority:

1. Reuse `.worktrees/` if it exists
2. Else reuse `worktrees/` if it exists
3. Else check `AGENTS.md` or `CLAUDE.md` for project preference
4. Else ask user:

```text
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ~/.config/superwork/worktrees/<project-name>/ (global location)
```

## Safety Verification

For project-local directories (`.worktrees/` or `worktrees/`), verify ignore status first:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

If not ignored:
1. add ignore rule
2. commit the ignore fix
3. continue with worktree creation

## Creation Steps

1. Detect project root and name:

```bash
project="$(basename "$(git rev-parse --show-toplevel)")"
```

2. Create worktree on a new branch:

```bash
git worktree add "$path" -b "$branch_name"
cd "$path"
```

3. Run setup with project-appropriate tools (prefer `pnpm` for Node projects):

```bash
if [ -f pnpm-lock.yaml ] || [ -f pnpm-workspace.yaml ]; then pnpm install; fi
if [ -f package-lock.json ]; then npm install; fi
if [ -f Cargo.toml ]; then cargo build; fi
if [ -f requirements.txt ]; then python3 -m pip install -r requirements.txt; fi
if [ -f go.mod ]; then go mod download; fi
```

4. Verify clean baseline with project test command.

If baseline fails, report and ask whether to proceed.

## Completion Output

```text
Worktree ready at <full-path>
Baseline verification passed
Ready for plan execution
```

## Common Mistakes

| Mistake | Why It Fails | Correct Move |
|---|---|---|
| Skip ignore check | Worktree files can pollute git status | Always run `git check-ignore` first |
| Assume directory location | Breaks team consistency | Follow selection priority |
| Start coding on failing baseline | New failures become untraceable | Resolve or acknowledge baseline first |

## Integration

- Called by `superwork-writing-plans` and `superwork-executing-plans`
- Pairs with `superwork-check` after implementation completes

