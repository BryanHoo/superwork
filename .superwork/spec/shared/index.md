# Shared Development Guidelines

## Scope

Durable contracts for the Superwork skill bundle and its deterministic tooling.

## Guidelines Index

| Guide | Description |
|---|---|
| [Directory Structure](./directory-structure.md) | Ownership of plugin, skill, test, and runtime artifacts |
| [Quality Guidelines](./quality-guidelines.md) | Workflow, metadata, test, and completion requirements |

## Pre-Development Checklist

- Read required context candidates first
- Load both guides only when changing a skill boundary, workflow contract, script, or plugin metadata

## Verification Checklist

- Confirm runtime config uses `schemaVersion: 3`
- Confirm the seven-skill set matches `workflow-contract.json`
- Confirm only `superwork-start` is implicitly invocable
- Confirm clear development goes directly to TDD, planning invokes TDD in the same run, and saved-plan resumes enter check once

## Update Triggers

- A skill is added, removed, renamed, or changes responsibility
- A script moves between skill ownership boundaries
- The runtime schema, plugin manifest, or invocation policy changes
