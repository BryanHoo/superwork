---
name: superwork-writing-plans
description: Use when an approved design or clear requirements in a `.superwork` project must be converted into an executable implementation plan before coding.
---

# Superwork Writing Plans

## Overview

Create a concrete, task-by-task plan that can be executed with minimal ambiguity.

**Core principle:** Every task must be explicit enough to execute and verify without guesswork.

## Preconditions

- Design spec is approved (usually from `superwork-brainstorming`)
- Work is prepared in an isolated workspace (`superwork-using-git-worktrees`)

## Plan Location

Save to:

`.superwork/plans/YYYY-MM-DD-<feature-name>.md`

## Required Header

Every plan starts with:

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superwork-executing-plans` to execute this plan task-by-task with checkbox tracking (`- [ ]`).

**Goal:** [One sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [Key libraries/tools]
```

## Task Rules

- break work into small steps (2-5 minutes)
- include exact file paths for each task
- include concrete verification commands
- include expected pass/fail signals
- include an explicit post-green completion step before `superwork-check`; require medium or large result diffs to run `superwork-code-simplifier`, and require truly small skips to explain why
- keep DRY, YAGNI, and test-first sequencing
- for `superwork-tdd`, make the first executable checklist item an explicit failing test step, and save the plan file before that step begins
- do not treat a chat-only outline or inline tool plan as the saved plan artifact

## No Placeholders

Never write:
- `TODO`, `TBD`, `implement later`
- vague steps like "add error handling"
- "write tests" without actual test content
- "same as previous task" shortcuts

## Self-Review

Before finishing the plan:
1. verify every spec requirement is mapped to tasks
2. scan for placeholder wording
3. verify naming/type consistency across tasks
4. if the plan will be used by `superwork-tdd`, verify RED starts in the file, not before the file exists

## Handoff

After saving the plan:
- announce the path
- invoke `superwork-executing-plans`

## Integration

- Typically follows `superwork-brainstorming`
- The same saved file format is reused by `superwork-tdd` for direct feature work
- Must encode the post-green completion handoff that `superwork-executing-plans` will follow
- Must hand off to `superwork-executing-plans`
