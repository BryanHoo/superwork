---
name: superwork-init
description: Initializes or repairs the project-local `.superwork/` runtime after the user explicitly requests Superwork onboarding. Generates project configuration and specs, but does not start feature implementation.
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

## Process

1. Inspect the repository, package markers, layers, tests, and existing `.superwork/` files.
2. If the runtime is already schema version 2 and complete, report that no repair is needed.
3. Run the bundled bootstrap script:

   ```bash
   python3 <skill_dir>/scripts/bootstrap_superwork.py --root .
   ```

4. Replace generic generated spec wording with project-true paths, commands, contracts, and checklists.
5. Verify `config.json` parses, `schemaVersion` is `2`, spec links resolve, and no generic workflow copy was generated.
6. Hand normal development back to `superwork-start`.

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
