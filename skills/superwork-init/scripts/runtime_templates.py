from __future__ import annotations

from pathlib import Path


TEMPLATES_ROOT = Path(__file__).resolve().parent.parent / "templates"


def guides_index_template(test_hints: list[str]) -> str:
    content = (TEMPLATES_ROOT / "guides-index.md.tmpl").read_text(encoding="utf-8")
    hint_lines = "\n".join(f"- `{hint}`" for hint in test_hints)
    return content.replace("{{ test_hints }}", hint_lines)


def layered_guides_files(test_hints: list[str]) -> dict[str, str]:
    return {
        ".superwork/spec/guides/index.md": guides_index_template(test_hints),
        ".superwork/spec/guides/code-reuse-thinking-guide.md": """# Code Reuse Thinking Guide

## Goal

Reduce duplicated logic before it spreads across the project.

## Checklist

- Search for an existing helper before creating a new one
- Prefer extending a stable pattern over adding a near-duplicate
- Record the chosen abstraction in the relevant layer doc when it becomes durable
""",
        ".superwork/spec/guides/cross-layer-thinking-guide.md": """# Cross-Layer Thinking Guide

## Goal

Make contracts explicit when behavior crosses frontend, backend, and shared boundaries.

## Checklist

- Trace the data shape from entry to output
- Call out validation, error, and fallback behavior
- Update both sides of the contract when one side changes
""",
        ".superwork/spec/guides/cross-platform-thinking-guide.md": """# Cross-Platform Thinking Guide

## Goal

Keep tooling and scripts understandable across local machines and CI.

## Checklist

- Prefer `python3` for Python scripts
- Prefer portable paths and repository-relative commands
- Record shell or platform assumptions before relying on them
""",
    }


def layered_shared_files(scope_label: str) -> dict[str, str]:
    return {
        "index.md": f"""# Shared Development Guidelines

## Scope

Durable shared rules for {scope_label}.

## Guidelines Index

| Guide | Description |
|---|---|
| [Directory Structure](./directory-structure.md) | Where shared modules and helpers belong |
| [Quality Guidelines](./quality-guidelines.md) | Reuse, testing, and contract rules |

## Pre-Development Checklist

- Read only context candidates marked `required`
- Load these guides only when changing shared contracts or utilities
""",
        "directory-structure.md": f"""# Shared Directory Structure

## Purpose

Document how reusable code should be organized for {scope_label}.

## Rules

- Keep shared modules narrowly reusable
- Avoid moving feature-specific code into shared directories too early
- Record ownership or boundary rules when multiple packages depend on the same module
""",
        "quality-guidelines.md": f"""# Shared Quality Guidelines

## Purpose

Capture contract and verification standards for {scope_label}.

## Rules

- Check all known consumers before changing a shared contract
- Update consumers together when a new contract intentionally breaks old behavior
- Record migration notes when breaking behavior is intentional
""",
    }
