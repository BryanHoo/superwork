# Shared Development Guidelines

## Scope

Durable contracts for the Superwork skill bundle and its deterministic tooling.

## Guidelines Index

| Guide | Description |
|---|---|
| [Directory Structure](./directory-structure.md) | Ownership of plugin, skill, test, and runtime artifacts |
| [Quality Guidelines](./quality-guidelines.md) | Workflow, metadata, test, and completion requirements |

## Pre-Development Checklist

- Read `.superwork/spec/guides/index.md`
- Read both guides before changing a skill boundary, workflow contract, script, or plugin metadata
- Reuse these guides within the same run while their content remains current and available

## Verification Checklist

- Confirm the eight-skill set matches `workflow-contract.json`
- Confirm only `superwork-start` is implicitly invocable
- Confirm all implementation paths call TDD and all completion paths enter check once
- Confirm schema 2, medium/heavy planning routes, mandatory plan interfaces, and spec-reference preflight remain intact

## Update Triggers

- A skill is added, removed, renamed, or changes responsibility
- A script moves between skill ownership boundaries
- The plugin manifest or invocation policy changes
