---
name: superwork-brainstorming
description: Produces a bounded design for heavy or explicitly design-oriented work after `superwork-start` routes here. It hands the design to planning by default and never implements code itself.
---

# Superwork Brainstorming

## Purpose

Turn broad requirements into one bounded design that can be planned and implemented without repeated phase gates.

## Preconditions

- The request needs architecture, requirement, scope, or trade-off exploration.

## Hard Gate

Do not write implementation code or scaffold product files while designing. Planning and execution remain downstream responsibilities.

## Process

1. Inspect the repository, recent changes, `.superwork/config.json`, relevant spec indexes, and concrete linked docs when available.
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

Continue by default by invoking `superwork-writing-plans` after the design is self-reviewed. If the user explicitly asks to stop after design or says not to plan or implement, save and report the design without invoking the next skill.

## Boundaries

- Read project facts from config and specs; generic routing lives in the skill package.
- Do not invent spec paths merely to satisfy a template.
- Do not broaden the design into unrelated refactoring.
- Do not invoke implementation directly from brainstorming.
