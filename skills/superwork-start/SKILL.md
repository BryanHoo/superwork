---
name: superwork-start
description: Use this skill to route repository work through Superwork when `.superwork/config.json` exists or the user explicitly requests Superwork. Send clear development directly to TDD, use planning only for material uncertainty or continuity, and preserve read-only, debugging, resume, and verification boundaries.
---

# Superwork Start

## Purpose

Choose the smallest valid route. This is the only normal implicit entry in the Superwork skill set.

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

- `ready`: use the embedded runtime and project facts; read only `candidateReads` marked `required`, then load `recommended` paths or linked concrete docs only when task evidence makes them relevant
- `missing`: if the user explicitly requested Superwork, report initialization as required before an artifact-backed write workflow; otherwise leave Superwork routing and continue the repository request normally without workflow artifacts
- `unsupported-schema`: report the runtime mismatch and require an explicit repair request before changing runtime files

Do not invoke `superwork-init` unless the user explicitly asks to initialize, onboard, adopt, or repair Superwork. Read-only requests can finish without `.superwork/`.

Never block ordinary repository work merely because an implicitly selected Superwork runtime is missing.

### Step 3: Classify the work

Classify in this order:

1. explicit final verification, readiness, or fresh-check request -> `superwork-check`
2. existing saved plan requested for continuation -> `superwork-executing-plans`
3. read-only analysis, review, explanation, or an acknowledgement that requests no next action -> finish directly after gathering evidence
4. bug, regression, failing test, or unexpected behavior -> `superwork-debugging`
5. non-bug work:
   - unresolved architecture, material scope or contract choices, high-risk work, cross-session continuity, or an explicit plan request -> `superwork-planning`
   - otherwise -> call `superwork-tdd`, even when the clear change spans several files

Every development route uses TDD. File count alone never triggers planning.

### Step 4: State and invoke one route

Before handoff, report `Superwork route: <route> - <reason>.` using one short reason tied to the request and repository evidence.

Then read `../<route>/SKILL.md` once per run and continue with exactly one route. Do not reproduce downstream implementation rules here.

Pass a handoff with `target`, `caller`, `outcome`, `evidence`, `stopConditions`, and `returnTo`. Treat `skills/superwork-start/references/workflow-contract.json` as the machine-readable source for this contract.

## Handoff Contract

```text
clear:    start -> TDD method -> check
planned:  start -> planning -> TDD method per code slice -> check
resume:   start -> executing-plans -> TDD method per code slice -> check
bug:      start -> debugging -> TDD method for the confirmed regression -> check
```

Continue across these transitions until final verification. Stop early only for an explicit user instruction, a skill stop condition, or a concrete blocker that cannot be resolved safely.

## Output Example

```text
Superwork route: superwork-planning - material interface choices remain unresolved.
```

## Boundaries

- Do not initialize `.superwork/` implicitly.
- Respect explicit user instructions that limit the requested outcome or prohibit writes.
- Do not select multiple competing destination skills.
- Do not pull TDD, debugging, planning, or completion details into this entry skill.
