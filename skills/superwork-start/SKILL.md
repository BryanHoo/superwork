---
name: superwork-start
description: Routes repository work by problem type and planning depth. Use as the normal Superwork entry for analysis, implementation, bug fixing, verification, or resuming a saved plan; it selects one downstream phase and lets the workflow continue to completion by default.
---

# Superwork Start

## Purpose

Choose one auditable first step. This is the only normal implicit entry in the Superwork skill set.

## Process

### Step 1: Interpret the requested outcome

Continue by default from the selected route through implementation and final verification.

Stop after an intermediate artifact only when an explicit user instruction says to do so, such as “only analyze”, “先给方案，不要实现”, “write a plan only”, or “do not modify files”. A read-only explanation or review is complete when its requested evidence has been reported; do not invent repository changes for it.

### Step 2: Load available project context

Run:

```bash
python3 <skill_dir>/scripts/get_context.py --root . --format json
```

Use `runtime.status` as follows:

- `ready`: read `.superwork/config.json`, `.superwork/spec/guides/index.md`, every `recommendedReads` path, and concrete docs linked by those indexes
- `missing`: continue read-only work without runtime artifacts; report initialization as a blocker only when a required write workflow cannot proceed
- `unsupported-schema`: report the runtime mismatch and require an explicit repair request before changing runtime files

Do not invoke `superwork-init` unless the user explicitly asks to initialize, onboard, adopt, or repair Superwork. Read-only requests can finish without `.superwork/`.

If implementation requires Superwork artifacts but runtime is missing, explain the required initialization instead of silently writing workflow files.

### Step 3: Classify the work

Classify in this order:

1. explicit final verification, readiness, or fresh-check request -> `superwork-check`
2. existing saved plan requested for continuation -> `superwork-executing-plans`
3. read-only analysis, review, explanation, or an acknowledgement that requests no next action -> finish directly after gathering evidence
4. bug, regression, failing test, or unexpected behavior -> `superwork-debugging`
5. non-bug work -> choose planning depth:
   - light: one file or a tightly bounded behavior slice -> call `superwork-tdd`
   - medium: clear multi-file coordination -> `superwork-writing-plans`
   - heavy: unresolved requirements, architecture, or cross-system trade-offs -> `superwork-brainstorming`

Task size chooses planning depth only. It does not decide whether implementation uses TDD.

### Step 4: State and invoke one route

Before handoff, report the selected route and one short reason tied to the request and repository evidence.

Then invoke exactly one route. Do not reproduce downstream implementation rules here.

## Handoff Contract

```text
light:  start -> TDD method -> check
medium: start -> writing-plans -> executing-plans -> TDD method per code slice -> check
heavy:  start -> brainstorming -> writing-plans -> executing-plans -> TDD method per code slice -> check
bug:    start -> debugging -> TDD method for the confirmed regression -> check
```

Continue across these transitions until final verification. Stop early only for an explicit user instruction, a skill stop condition, or a concrete blocker that cannot be resolved safely.

## Output Example

```text
Routing to superwork-writing-plans: this is a clear multi-file change; after preflight the workflow will continue through execution and final verification.
```

## Boundaries

- Do not initialize `.superwork/` implicitly.
- Respect explicit user instructions that limit the requested outcome or prohibit writes.
- Do not select multiple competing destination skills.
- Do not pull TDD, debugging, planning, or completion details into this entry skill.
