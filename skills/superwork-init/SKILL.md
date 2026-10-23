---
name: superwork-init
description: Use this skill to initialize, onboard, or repair the project-local `.superwork/` runtime only when the user explicitly requests it. Detect real project tooling, generate configuration and durable spec structure, and preserve existing authored artifacts.
---

# Superwork Init

## Purpose

Create project-local facts and durable specs without copying the generic Superwork workflow into the target repository.

Initialization changes repository files. Run it only when the user explicitly asks to initialize, onboard, or repair `.superwork/`.

## Runtime Contract

Generate:

```text
.superwork/
├── config.json
├── parallel.md
├── spec/
├── prd/
└── plans/
```

`config.json` contains only project facts:

- `schemaVersion`
- `packageManager`
- detected packages and layers
- artifact paths
- project verification commands

Do not generate route/state blocks, scripts, templates, or copies of the generic workflow.

`parallel.md` is a small, project-editable cooperation agreement, not a route/state definition. Preserve existing authored content. Task notices under `parallel/` are created lazily by write tasks, kept local with their own ignore file, and removed only by their owner after verification. Existing schema 2 projects can add the missing guide at first registration without reinitializing config or specs.

When repairing an already-ready runtime, follow [parallel coordination](../superwork-start/references/parallel-coordination.md) before writes and release only your own notice after validating the repair. First initialization of a missing runtime does not create a notice before that runtime exists; incompatible-runtime repair remains explicit and must preserve existing notices.

## Process

1. Inspect the repository, package markers, layers, tests, and existing `.superwork/` files.
2. If the runtime is already schema version 2 and complete, report that no repair is needed.
3. Run the bundled bootstrap script:

   ```bash
   python3 <skill_dir>/scripts/bootstrap_superwork.py --root .
   ```

4. Replace generic generated spec wording with project-true paths, commands, contracts, and checklists.
5. Verify `config.json` parses, `schemaVersion` is `2`, spec links resolve, and no generic workflow copy was generated.
6. When the user also requested development, read `../superwork-start/SKILL.md` once per run in full and pass a structured handoff containing the initialized runtime evidence. Otherwise report initialization and stop.

## Preservation Rules

- Preserve existing authored design, plan, and spec content.
- Repair missing or generated runtime artifacts without overwriting unrelated project knowledge.
- Do not add compatibility branches for the removed workflow-copy model.
- Do not start implementation merely because initialization succeeded.

## Completion Evidence

Report:

- files created or repaired
- detected package manager and package/layer map
- verification commands recorded in config
- any spec sections still requiring project-specific refinement
