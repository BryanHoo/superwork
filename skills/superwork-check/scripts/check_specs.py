#!/usr/bin/env python3
"""Map changed files to likely `.superwork` specs and verification hints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2]
if str(SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILLS_ROOT))

from _shared.repository import collect_git_changes  # noqa: E402


KNOWN_LAYERS = {"frontend", "backend", "shared"}
RUNTIME_SCHEMA_VERSION = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def load_runtime(root: Path) -> tuple[str, list[str]]:
    config_path = root / ".superwork" / "config.json"
    if not config_path.exists():
        return "missing", []
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "unsupported-schema", []
    if not isinstance(payload, dict) or payload.get("schemaVersion") != RUNTIME_SCHEMA_VERSION:
        return "unsupported-schema", []
    verification = payload.get("verification")
    hints = [item for item in verification if isinstance(item, str)] if isinstance(verification, list) else []
    return "ready", hints


def detect_layer(file_path: str) -> str:
    parts = set(Path(file_path).parts)
    if parts & {"components", "pages", "app", "web", "ui", "frontend", "hooks", "composables"}:
        return "frontend"
    if parts & {"api", "server", "service", "services", "backend", "scripts", "db", "database"}:
        return "backend"
    return "shared"


def load_layout(spec_root: Path) -> dict[str, str]:
    # 优先读运行态元数据；缺失时再根据目录形状回退推断。
    layout_file = spec_root / ".layout.json"
    if layout_file.exists():
        try:
            payload = json.loads(layout_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            layout_type = payload.get("type")
            layout_mode = payload.get("mode")
            if isinstance(layout_type, str) and isinstance(layout_mode, str):
                return {"type": layout_type, "mode": layout_mode}

    top_dirs = [
        path.name
        for path in sorted(spec_root.iterdir())
        if path.is_dir() and path.name != "guides"
    ]
    if top_dirs and all(name in KNOWN_LAYERS for name in top_dirs):
        return {"type": "layered", "mode": "layer-root"}
    return {"type": "legacy", "mode": "package-layer"}


def guess_layer_doc(layer: str, file_path: str) -> str | None:
    # 用文件路径信号把改动尽量落到更具体的规范文档，而不是只回到 index。
    parts = set(Path(file_path).parts)
    if layer == "frontend":
        if parts & {"components", "component"}:
            return "component-guidelines.md"
        if parts & {"hooks", "hook", "composables"}:
            return "hook-guidelines.md"
        if parts & {"store", "stores", "state"}:
            return "state-management.md"
        if parts & {"types", "schema", "schemas", "zod"}:
            return "type-safety.md"
        if parts & {"pages", "app", "routes", "router", "views"}:
            return "directory-structure.md"
        return "quality-guidelines.md"
    if layer == "backend":
        if parts & {"scripts", "script", "cli", "bin"}:
            return "script-conventions.md"
        if parts & {"db", "database", "migration", "migrations", "prisma", "schema", "sql"}:
            return "database-guidelines.md"
        if parts & {"log", "logger", "logging"}:
            return "logging-guidelines.md"
        if parts & {"api", "server", "controller", "controllers", "route", "routes", "handler", "handlers", "middleware"}:
            return "error-handling.md"
        return "quality-guidelines.md"
    if parts & {"shared", "common", "lib", "utils"}:
        return "directory-structure.md"
    return "quality-guidelines.md"


def resolve_package_name(spec_root: Path, file_path: str) -> str | None:
    package_names = [
        path.name
        for path in sorted(spec_root.iterdir())
        if path.is_dir() and path.name not in {"guides", *KNOWN_LAYERS}
    ]
    if not package_names:
        return "root" if (spec_root / "root").is_dir() else None

    parts = Path(file_path).parts
    for name in package_names:
        if name in parts:
            return name
    return "root" if "root" in package_names else None


def add_spec_entry(
    root: Path,
    relevant: list[dict[str, str]],
    seen: set[str],
    path: Path,
    reason: str,
) -> None:
    if not path.exists():
        return
    rel = str(path.relative_to(root))
    if rel in seen:
        return
    relevant.append({"path": rel, "reason": reason})
    seen.add(rel)


def collect_relevant_specs(root: Path, changed_files: list[str]) -> list[dict[str, str]]:
    spec_root = root / ".superwork" / "spec"
    relevant: list[dict[str, str]] = []
    if not spec_root.exists():
        return relevant
    layout = load_layout(spec_root)
    seen: set[str] = set()

    if layout["mode"] == "layer-root":
        # 单仓库新布局：`.superwork/spec/<layer>/...`
        for layer_dir in sorted(spec_root.iterdir()):
            if not layer_dir.is_dir() or layer_dir.name == "guides":
                continue
            index_path = layer_dir / "index.md"
            if not changed_files:
                add_spec_entry(root, relevant, seen, index_path, f"matched layer {layer_dir.name}")
                continue
            for file_path in changed_files:
                if detect_layer(file_path) != layer_dir.name:
                    continue
                add_spec_entry(root, relevant, seen, index_path, f"matched layer {layer_dir.name}")
                guide_name = guess_layer_doc(layer_dir.name, file_path)
                if guide_name:
                    add_spec_entry(
                        root,
                        relevant,
                        seen,
                        layer_dir / guide_name,
                        f"matched layer guide {guide_name} for {file_path}",
                    )
    else:
        # 兼容旧布局和多包布局：`.superwork/spec/<package>/<layer>/...`
        for package_dir in sorted(spec_root.iterdir()):
            if not package_dir.is_dir() or package_dir.name == "guides":
                continue
            for layer_dir in sorted(package_dir.iterdir()):
                if not layer_dir.is_dir():
                    continue
                index_path = layer_dir / "index.md"
                if not changed_files:
                    add_spec_entry(
                        root,
                        relevant,
                        seen,
                        index_path,
                        f"matched package {package_dir.name} and layer {layer_dir.name}",
                    )
                    continue
                for file_path in changed_files:
                    package_name = resolve_package_name(spec_root, file_path)
                    if package_name not in {package_dir.name, None}:
                        continue
                    if detect_layer(file_path) != layer_dir.name:
                        continue
                    add_spec_entry(
                        root,
                        relevant,
                        seen,
                        index_path,
                        f"matched package {package_dir.name} and layer {layer_dir.name}",
                    )
                    if (spec_root / ".layout.json").exists():
                        guide_name = guess_layer_doc(layer_dir.name, file_path)
                        if guide_name:
                            add_spec_entry(
                                root,
                                relevant,
                                seen,
                                layer_dir / guide_name,
                                f"matched layer guide {guide_name} for {file_path}",
                            )
    return relevant


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    change_detection = collect_git_changes(root)
    changed_files = change_detection.files
    relevant_specs = collect_relevant_specs(root, changed_files)
    runtime_status, configured_hints = load_runtime(root)
    payload = {
        "runtimeStatus": runtime_status,
        "changeDetection": change_detection.to_dict(),
        "changedFiles": changed_files,
        "relevantSpecs": relevant_specs,
        "verificationHints": configured_hints
        or [
            "run related unit tests",
            "run lint for the changed package when available",
        ],
        "risks": (
            [change_detection.error]
            if change_detection.error
            else ([] if relevant_specs or not changed_files else ["no relevant spec index matched the changed files"])
        ),
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("Superwork spec check context")
    print("- changedFiles:")
    for item in changed_files:
        print(f"  - {item}")
    print("- relevantSpecs:")
    for item in relevant_specs:
        print(f"  - {item['path']}: {item['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
