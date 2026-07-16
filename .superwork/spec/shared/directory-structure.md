# Shared Directory Structure

## Purpose

Define ownership boundaries for the Superwork plugin, skills, tests, and project runtime artifacts.

## Rules

- Store plugin distribution metadata only in `.codex-plugin/plugin.json`
- Store one skill per `skills/<skill-name>/SKILL.md` with optional one-level `agents/`, `references/`, `scripts/`, and `templates/`
- Store the machine workflow contract under `skills/superwork-start/references/`
- Store cross-skill contract and scenario tests under `tests/workflow/`
- Store project facts and durable rules under `.superwork/config.json` and `.superwork/spec/`
- Do not restore empty skill directories for removed workflow phases
