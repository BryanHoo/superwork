#!/usr/bin/env python3
"""Generate a minimal `.superwork/` runtime for the current project.

Usage:
    python3 scripts/bootstrap_superwork.py
    python3 scripts/bootstrap_superwork.py --root /path/to/project
    python3 scripts/bootstrap_superwork.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".superwork",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "tmp",
    ".next",
    ".turbo",
}

KNOWN_LAYERS = ("frontend", "backend", "shared")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap `.superwork/` runtime artifacts for the current project."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Target project root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview generated files without writing them.",
    )
    return parser.parse_args()


def detect_package_manager(root: Path) -> str:
    if (root / "pnpm-lock.yaml").exists() or (root / "pnpm-workspace.yaml").exists():
        return "pnpm"
    if (root / "package-lock.json").exists():
        return "npm"
    if (root / "yarn.lock").exists():
        return "yarn"
    return "pnpm"


def detect_test_hints(root: Path, package_manager: str) -> list[str]:
    package_json = root / "package.json"
    hints: list[str] = []
    if package_json.exists():
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
        except json.JSONDecodeError:
            scripts = {}
        for name in ("test", "test:run", "lint", "typecheck", "build"):
            if name in scripts:
                hints.append(f"{package_manager} {name}")
    if not hints:
        hints.append(f"{package_manager} test")
    return hints


def detect_layers(base_dir: Path) -> list[str]:
    entries = {path.name.lower() for path in base_dir.iterdir() if path.is_dir()}
    layers: list[str] = []

    # 用目录启发式推断 layer，优先保持首版结果稳定且容易理解。
    frontend_signals = {"src", "app", "pages", "components", "public", "web", "ui"}
    backend_signals = {"api", "server", "service", "services", "backend"}
    shared_signals = {"shared", "common", "lib", "utils", "packages"}

    if entries & frontend_signals:
        layers.append("frontend")
    if entries & backend_signals:
        layers.append("backend")
    if entries & shared_signals:
        layers.append("shared")

    if not layers:
        layers.append("shared")

    return layers


def detect_packages(root: Path) -> list[dict[str, list[str] | str]]:
    packages: list[dict[str, list[str] | str]] = []
    packages.append({"name": "root", "layers": detect_layers(root)})

    for candidate in sorted(root.iterdir()):
        if not candidate.is_dir() or candidate.name in IGNORED_DIRS:
            continue
        if candidate.name.startswith("."):
            continue
        if not (
            (candidate / "package.json").exists()
            or (candidate / "pyproject.toml").exists()
            or (candidate / "pom.xml").exists()
            or (candidate / "Cargo.toml").exists()
        ):
            continue
        packages.append({"name": candidate.name, "layers": detect_layers(candidate)})

    deduped: dict[str, dict[str, list[str] | str]] = {}
    for package in packages:
        deduped[str(package["name"])] = package
    return list(deduped.values())


def load_template(template_name: str) -> str:
    # scripts/ 下的工具统一回到 skill 根目录读取模板，避免根目录散落脚本。
    template_path = Path(__file__).resolve().parent.parent / "templates" / template_name
    return template_path.read_text(encoding="utf-8")


def render_template(template_name: str, **values: str) -> str:
    content = load_template(template_name)
    for key, value in values.items():
        content = content.replace(f"{{{{ {key} }}}}", value)
    return content


def ensure_text(root: Path, path: Path, content: str, dry_run: bool, created: list[str]) -> None:
    if dry_run:
        created.append(str(path.relative_to(root)))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")
    created.append(str(path.relative_to(root)))


def build_spec_metadata(layout_type: str, mode: str) -> str:
    return json.dumps(
        {
            "type": layout_type,
            "mode": mode,
            "version": 1,
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def workflow_template(package_manager: str, packages: list[dict[str, list[str] | str]]) -> str:
    package_map = "\n".join(
        f"- `{item['name']}`: {', '.join(item['layers'])}" for item in packages
    )
    # workflow 仅输出项目运行时文档，不暴露或要求项目内存在技能脚本路径。
    return render_template(
        "workflow.md.tmpl",
        package_manager=package_manager,
        package_map=package_map,
    )


def guides_index_template(test_hints: list[str]) -> str:
    hint_lines = "\n".join(f"- `{hint}`" for hint in test_hints)
    return render_template(
        "guides-index.md.tmpl",
        test_hints=hint_lines,
    )


def package_index_template(package_name: str, layer: str, package_manager: str) -> str:
    verification_command = f"{package_manager} test"
    return render_template(
        "package-index.md.tmpl",
        package_name=package_name,
        layer=layer,
        layer_guideline=f"{layer}-guidelines.md",
        verification_command=verification_command,
    )


def package_guideline_template(package_name: str, layer: str) -> str:
    return render_template(
        "layer-guidelines.md.tmpl",
        package_name=package_name,
        layer=layer,
        layer_title=layer.title(),
    )


def layered_guides_files(test_hints: list[str]) -> dict[str, str]:
    return {
        # 运行时 guides index 统一从模板渲染，避免模板文件与内联文案双份漂移。
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


def layered_frontend_files(scope_label: str) -> dict[str, str]:
    return {
        "index.md": f"""# Frontend Development Guidelines

## Scope

Durable frontend rules for {scope_label}.

## Guidelines Index

| Guide | Description |
|---|---|
| [Directory Structure](./directory-structure.md) | Where pages, components, and UI state live |
| [Component Guidelines](./component-guidelines.md) | Reusable component patterns and boundaries |
| [Hook Guidelines](./hook-guidelines.md) | Hook naming, side effects, and composition |
| [State Management](./state-management.md) | Local, shared, and server state rules |
| [Quality Guidelines](./quality-guidelines.md) | Testing, accessibility, and review gates |
| [Type Safety](./type-safety.md) | Type contracts and validation rules |

## Pre-Development Checklist

- Read `.superwork/spec/guides/index.md`
- Read the most relevant guide above before implementation
- Confirm whether this change affects shared or backend contracts
""",
        "directory-structure.md": f"""# Frontend Directory Structure

## Purpose

Document where frontend code belongs for {scope_label}.

## Rules

- Keep route-level code close to route entry points
- Extract reusable UI into shared component directories only after a second use
- Record any non-obvious placement rule with a concrete example
""",
        "component-guidelines.md": f"""# Frontend Component Guidelines

## Purpose

Capture durable component patterns for {scope_label}.

## Rules

- Keep components focused on one UI responsibility
- Prefer explicit props over hidden shared state
- Record composition patterns that future sessions should reuse
""",
        "hook-guidelines.md": f"""# Frontend Hook Guidelines

## Purpose

Describe how hooks should read data, manage effects, and expose state in {scope_label}.

## Rules

- Keep side effects inside the smallest stable hook boundary
- Name hooks by the behavior they provide
- Document loading, error, and cleanup expectations
""",
        "state-management.md": f"""# Frontend State Management

## Purpose

Track where local, shared, and remote state should live in {scope_label}.

## Rules

- Keep transient UI state local by default
- Promote state only when multiple features need the same source of truth
- Record cache invalidation or synchronization rules when they become durable
""",
        "quality-guidelines.md": f"""# Frontend Quality Guidelines

## Purpose

Capture review and verification standards for {scope_label}.

## Rules

- Add or update tests when behavior changes
- Check accessibility impact for interactive UI changes
- Record repeated regressions so future tasks can avoid them
""",
        "type-safety.md": f"""# Frontend Type Safety

## Purpose

Define frontend type and validation expectations for {scope_label}.

## Rules

- Keep view models and API contracts explicit
- Validate unsafe input at the boundary where it enters the app
- Record any project-specific typing pattern that should be reused
""",
    }


def layered_backend_files(scope_label: str) -> dict[str, str]:
    return {
        "index.md": f"""# Backend Development Guidelines

## Scope

Durable backend rules for {scope_label}.

## Guidelines Index

| Guide | Description |
|---|---|
| [Directory Structure](./directory-structure.md) | Where handlers, services, and integrations live |
| [Script Conventions](./script-conventions.md) | Runtime and maintenance script rules |
| [Error Handling](./error-handling.md) | Validation, error translation, and failure handling |
| [Quality Guidelines](./quality-guidelines.md) | Testing, review, and reliability checks |
| [Logging Guidelines](./logging-guidelines.md) | Structured logging and observability rules |
| [Database Guidelines](./database-guidelines.md) | Schema, query, and migration guidance |

## Pre-Development Checklist

- Read `.superwork/spec/guides/index.md`
- Read the most relevant guide above before implementation
- Confirm whether the change updates a durable contract
""",
        "directory-structure.md": f"""# Backend Directory Structure

## Purpose

Document how backend code is organized for {scope_label}.

## Rules

- Keep transport, domain, and persistence concerns separated when practical
- Prefer existing module boundaries before creating new top-level folders
- Record any package-specific placement rules with examples
""",
        "script-conventions.md": f"""# Backend Script Conventions

## Purpose

Capture script-writing rules for {scope_label}.

## Rules

- Run Python scripts with `python3`
- Keep scripts repository-relative and safe to rerun
- Document required environment assumptions close to the script
""",
        "error-handling.md": f"""# Backend Error Handling

## Purpose

Describe validation, recovery, and error translation rules for {scope_label}.

## Rules

- Fail with clear, bounded error messages
- Normalize error handling at stable boundaries
- Record repeated failure modes and the expected response behavior
""",
        "quality-guidelines.md": f"""# Backend Quality Guidelines

## Purpose

Capture verification and reliability standards for {scope_label}.

## Rules

- Add or update targeted tests when behavior changes
- Prefer the narrowest verification command that proves the change
- Record recurring review comments as durable rules
""",
        "logging-guidelines.md": f"""# Backend Logging Guidelines

## Purpose

Describe what should be logged and how in {scope_label}.

## Rules

- Log with enough context to debug failures without leaking sensitive data
- Keep log levels consistent with operational importance
- Record any structured fields that downstream tools rely on
""",
        "database-guidelines.md": f"""# Backend Database Guidelines

## Purpose

Capture schema, query, and migration rules for {scope_label}.

## Rules

- Keep schema changes and verification steps explicit
- Prefer existing query and transaction patterns before adding new ones
- Record indexing, performance, and consistency assumptions when they matter
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
| [Quality Guidelines](./quality-guidelines.md) | Reuse, testing, and compatibility rules |

## Pre-Development Checklist

- Read `.superwork/spec/guides/index.md`
- Read both guides before changing shared contracts or utilities
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

Capture compatibility and verification standards for {scope_label}.

## Rules

- Check all known consumers before changing a shared contract
- Prefer backward-compatible changes when practical
- Record migration notes when breaking behavior is intentional
""",
    }


def layered_layer_runtime(scope_prefix: str, layer: str, scope_label: str) -> dict[str, str]:
    if layer == "frontend":
        files = layered_frontend_files(scope_label)
    elif layer == "backend":
        files = layered_backend_files(scope_label)
    else:
        files = layered_shared_files(scope_label)
    return {f"{scope_prefix}/{name}": content for name, content in files.items()}


def build_layered_runtime(
    packages: list[dict[str, list[str] | str]], test_hints: list[str]
) -> tuple[dict[str, str], str]:
    runtime = layered_guides_files(test_hints)
    child_packages = [package for package in packages if str(package["name"]) != "root"]

    # 新布局在单仓库下直接使用 layer 目录；多包时再引入 package 目录。
    if child_packages:
        for package in child_packages:
            package_name = str(package["name"])
            scope_label = f"package `{package_name}`"
            for layer in package["layers"]:
                runtime.update(
                    layered_layer_runtime(
                        f".superwork/spec/{package_name}/{layer}",
                        str(layer),
                        scope_label,
                    )
                )
        mode = "package-layer"
    else:
        root_package = next((package for package in packages if str(package["name"]) == "root"), None)
        root_layers = list(root_package["layers"]) if root_package else ["shared"]
        for layer in root_layers:
            runtime.update(layered_layer_runtime(f".superwork/spec/{layer}", str(layer), "this project"))
        mode = "layer-root"

    runtime[".superwork/spec/.layout.json"] = build_spec_metadata("layered", mode)
    return runtime, mode


def build_runtime_files(root: Path) -> tuple[dict[str, str], str]:
    package_manager = detect_package_manager(root)
    test_hints = detect_test_hints(root, package_manager)
    packages = detect_packages(root)

    runtime: dict[str, str] = {
        ".superwork/workflow.md": workflow_template(package_manager, packages),
    }
    layered_runtime, mode = build_layered_runtime(packages, test_hints)
    runtime.update(layered_runtime)
    return runtime, mode


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    runtime_files, spec_mode = build_runtime_files(root)

    created: list[str] = []
    for relative_path, content in runtime_files.items():
        ensure_text(root, root / relative_path, content, args.dry_run, created)

    payload = {
        "created": sorted(created),
        "detectedPackages": detect_packages(root),
        "spec": {
            "type": "layered",
            "mode": spec_mode,
        },
        "warnings": [],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
