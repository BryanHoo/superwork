---
name: superwork-brainstorming
description: Use this skill to resolve architecture, requirements, scope, or cross-system trade-offs for a heavy Superwork change. Produce one bounded design, continue to planning by default, and stop after design only when the user explicitly limits the outcome.
---

# Superwork Brainstorming

## Purpose

Turn broad requirements into one bounded design that can be planned and implemented without repeated phase gates.

## Preconditions

- The request needs architecture, requirement, scope, or trade-off exploration.

## Hard Gate

Do not write implementation code or scaffold product files while designing. Planning and execution remain downstream responsibilities.

Before saving design artifacts, follow [parallel coordination](../superwork-start/references/parallel-coordination.md), loaded once per run. Reuse the caller's notice; direct entry establishes its own before writes. A validated design-only outcome releases its own notice; continuation carries it to planning.

## Process

1. Reuse current project facts and already-read guidance from the handoff. Inspect relevant repository changes, required indexes, and only the linked docs needed for the design decisions; on direct entry, obtain context through `superwork-start/scripts/get_context.py` first. Read applicable binding rules even when they are listed as recommended.
2. Identify whether the request contains multiple independent subsystems. Split it before detailed design when one document would not produce a coherent implementation plan.
3. Resolve uncertainty from repository evidence and reasonable assumptions. Ask one focused question only when a missing choice would materially change the outcome.
4. Present two or three viable approaches with trade-offs and a recommendation.
5. Present the recommended design in appropriately sized sections covering boundaries, interfaces, data flow, errors, and verification.
6. Write the selected design to `.superwork/prd/YYYY-MM-DD-<topic>-design.md`.
7. Self-review the written document for placeholders, contradictions, ambiguous requirements, scope, and stale file references. Fix issues inline.
8. Apply the continuation policy below.

## Design Artifact

Include:

- `Goal`
- actual `Suggested Spec Reads` or an explicit note that project specs are unavailable
- existing context
- recommended approach
- component responsibilities and interfaces
- error handling
- verification strategy
- non-goals
- success criteria

Do not auto-commit the design document.

## Continuation Policy

Continue by default after the design is self-reviewed: read `../superwork-writing-plans/SKILL.md` once per run in full and pass the structured handoff defined by `superwork-start`, with the design path and self-review evidence. If the user explicitly asks to stop after design or says not to plan or implement, save and report the design without loading the next skill.

## Boundaries

- Read project facts from config and specs; generic routing lives in the skill package.
- Do not invent spec paths merely to satisfy a template.
- Do not broaden the design into unrelated refactoring.
- Do not invoke implementation directly from brainstorming.
