# Superwork

[简体中文](README.md) · English

Superwork is a set of development skills for Codex and Claude Code. It connects design, planning, implementation, and verification into a continuous workflow for feature development, bug fixes, and resuming saved plans. It selects a starting point according to task complexity, applies TDD to code changes, and keeps project constraints and task progress in the repository.

## Workflow

The AI uses `superwork-start` to identify the request type and automatically choose an execution path:

| Task | Execution path |
| --- | --- |
| Small change with clear boundaries | [TDD](skills/superwork-tdd/SKILL.md) → final check |
| Clear change spanning multiple files | [Write plan](skills/superwork-writing-plans/SKILL.md) → [execute plan](skills/superwork-executing-plans/SKILL.md) → final check |
| Unresolved requirements, architecture, or trade-offs | [Design](skills/superwork-brainstorming/SKILL.md) → write plan → execute plan → final check |
| Bug or regression | [Confirm root cause](skills/superwork-debugging/SKILL.md) → TDD repair → final check |
| Saved plan | Preflight → execute remaining tasks in order → final check |
| Read-only analysis or review | Gather evidence and respond directly |

Every code behavior slice uses RED → GREEN → REFACTOR regardless of planning depth. Documentation and configuration use suitable structural, build, or content checks. The [final check](skills/superwork-check/SKILL.md) covers necessary simplification, project verification, and durable spec updates. Verification results can be reused only while relevant inputs and the environment remain unchanged.

## Installation

For macOS / Linux. Requires Bash, curl, and tar. Workflow scripts also require Python 3.11+.

Copy this command to install; no repository clone is required:

```bash
curl -fsSL https://raw.githubusercontent.com/BryanHoo/superwork/main/scripts/install.sh | bash
```

The [installer](scripts/install.sh) downloads and copies every skill and the `_shared` dependency into `~/.agents/skills/`, then removes its temporary files. The installation runs independently of the download.

For Claude Code, reuse the default installation through hard links:

```bash
curl -fsSL https://raw.githubusercontent.com/BryanHoo/superwork/main/scripts/install.sh | bash -s -- --claude
```

`--claude` installs to the default directory and recreates the directory structure under `~/.claude/skills/`, with a hard link for each file. Files share their content across both locations, which must reside on the same filesystem.

Skill discovery paths, where `<name>` is a skill such as `superwork-start`:

| Tool | User scope: installer destination | Project scope: relative to the project directory |
| --- | --- | --- |
| Codex | `~/.agents/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` |
| Claude Code | `~/.claude/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` |

Other skills are preserved, and identical existing content is reused. Conflicting content or link relationships are reported before any installation entries are written. See the official [Codex documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills#choose-where-skills-load) for project discovery rules.

## Usage

### 1. First-time setup: initialize each project once

Only when first adopting Superwork in a project, start an agent session at the project root and invoke `superwork-init`:

```text
Use superwork-init to initialize this project. Check the actual verification
commands and capture project constraints in the specs.
```

Use `$superwork-init` in Codex or `/superwork-init` in Claude Code.

Initialization detects the package manager, packages, and layers, then generates `.superwork/config.json` and the spec structure. Review the `verification` commands and generated specs. Later tasks and new sessions reuse this project context, so initialization does not need to be repeated.

### 2. Everyday development: describe the request

Once the project is set up, tell the AI the goal, scope, and acceptance criteria:

```text
Add a status filter to the order list.
Reuse the existing query API, preserve pagination, and verify empty results
and behavior when switching filters.
```

The AI automatically invokes `superwork-start`, loads project context, routes the request to design, planning, implementation, or debugging, and continues through final verification. For everyday use, simply describe what you need.

### 3. Control execution and resume work

State any execution limit or request to resume saved work directly:

| Goal | Example request |
| --- | --- |
| Design only | Design the permission model. Stop after the design; do not plan or implement. |
| Plan only | Plan the agreed pagination approach. Do not implement. |
| Fix a bug | Filters disappear after refresh. Investigate and fix the issue. |
| Resume work | Continue `.superwork/plans/2026-10-23-order-filter.md`. |
| Read-only review | Verify the current changes against the acceptance criteria. Do not modify files. |

Supply the actual saved plan path when resuming. The executor checks plan structure, spec references, and interface declarations, then continues from the first unchecked `Task Status` in order. A new session reloads constraints and re-establishes verification evidence; checked tasks do not prove the current state. Repair the plan first if its interfaces, requirements, or verification conditions no longer match reality.

### 4. Develop across parallel sessions

Start multiple AI sessions in the same project directory and describe each outcome. Every session first inspects task summaries. Before writing, it reads `.superwork/parallel.md` and registers its intended paths and shared impact in its own `parallel/<id>.json`. Small tasks need no artificial plan; tasks inside each saved plan remain serial.

Read summaries first, the project agreement before writes, and another task's plan and applicable specs only when relevant impact requires them. Refresh notices before scope expansion, shared edits, resumption, or finalization edits.

- Continue independent work. Assign overlapping changes to one task while others advance unaffected parts.
- Consider public behavior, database schemas, dependencies, and test resources as well as filenames.
- Pause affected work when ownership or compatibility is unclear and record why. Paused notices retain their scope.
- After verification, preserve shared changes and evidence in the existing plan, then remove only your notice. Retain it on failure, interruption, or pause. Read-only checks do not clean up other tasks.

Records contain `id`, `owner`, `goal`, `status`, `writePaths`, `sharedImpact`, `plan`, `reason`, and `updatedAt`. Paths are literal project-relative files or directories; status is `running` or `paused`. The helper checks ownership, keeps separate files per task, and adds a local ignore file for temporary JSON records.

An existing schema 2 project gets its missing agreement at first registration without reinitialization or overwriting authored content. These are cooperative notices, not file locks or process control. Separate clones and worktrees do not automatically share notices.

## Project files and constraints

```text
.superwork/
├── config.json   # Project facts: tooling, packages, layers, artifact paths, checks
├── parallel.md   # Project-editable cooperation agreement, read before writes
├── parallel/     # Local per-task JSON notices, removed after verified completion
├── spec/         # Durable rules: shared guides, layer rules, and indexes
├── prd/          # Design documents
└── plans/        # Resumable single-file plans and task status
```

- `config.json` currently uses `schemaVersion: 2`. Update package facts and `verification` commands when the project's toolchain changes.
- `spec/` holds lasting interface contracts, directory rules, and verification requirements linked through indexes. Keep temporary task progress in the plan.
- `parallel.md` holds the cooperation agreement; `parallel/` holds current impact notices, does not replace plans, and keeps temporary records out of commits.
- Plans use `YYYY-MM-DD-<topic>.md`. Each task declares files, input and output interfaces, expected behavior, stop conditions, and a verification command. Follow the [task template](skills/superwork-writing-plans/SKILL.md#exact-task-template) when editing a plan manually.
- If the configuration version is incompatible, explicitly request repair of the existing `.superwork/` before continuing.

## Verify Superwork itself

From this repository's root, run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v
```

When changing skill descriptions or trigger boundaries, also run the live trigger evaluation with valid Codex CLI authentication:

```bash
python3 tests/evals/run_skill_evals.py --split validation --runs 3
```
