# Shared Directory Structure

## Purpose

Define ownership boundaries for the Superwork plugin, skills, tests, and project runtime artifacts.

## Rules

- Store plugin distribution metadata only in `.codex-plugin/plugin.json`
- Store one skill per `skills/<skill-name>/SKILL.md` with optional one-level `agents/`, `references/`, `scripts/`, and `templates/`
- Store plugin-wide deterministic repository helpers under `skills/_shared/`; do not register that directory as a skill
- Store skill-owned generation helpers beside their entry script under that skill's `scripts/` directory
- Store the machine workflow contract under `skills/superwork-start/references/`
- Store cross-skill contract and scenario tests under `tests/workflow/`
- Store live trigger datasets, the isolated Codex runner, and runner tests under `tests/evals/`
- Store each resumable plan in one compact Markdown file with goal, scope, acceptance, and one `Task Status` checkbox per task
- Store material uncertainty resolution and optional saved-plan authoring in `superwork-planning`; reserve `superwork-executing-plans` for resuming an existing plan
- Store project facts and durable rules under `.superwork/config.json` and `.superwork/spec/`
- Do not restore empty skill directories for removed workflow phases
