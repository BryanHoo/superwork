#!/usr/bin/env python3
"""Detect packages, layers, and recommended spec reads for `.superwork`."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


KNOWN_LAYERS = {"frontend", "backend", "shared"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("text", "json"), default="text")
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
    hints: list[str] = []
    package_json = root / "package.json"
    if package_json.exists():
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
        except json.JSONDecodeError:
            scripts = {}
        for name in ("test", "test:run", "lint", "typecheck", "build"):
            if name in scripts:
                command = package_manager if name == "test" else f"{package_manager} {name}"
                hints.append(command)
    if not hints:
        hints.append(f"{package_manager} test")
    return hints


def git_changed_files(root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def detect_layer(parts: tuple[str, ...]) -> str:
    if any(part in ("components", "pages", "app", "web", "ui", "hooks", "composables") for part in parts):
        return "frontend"
    if any(part in ("api", "server", "service", "services", "backend", "scripts", "db", "database") for part in parts):
        return "backend"
    return "shared"


def resolve_package_name(spec_root: Path, parts: tuple[str, ...]) -> str | None:
    package_names = [
        path.name
        for path in sorted(spec_root.iterdir())
        if path.is_dir() and path.name not in {"guides", *KNOWN_LAYERS}
    ]
    if not package_names:
        return "root" if (spec_root / "root").is_dir() else None
    for name in package_names:
        if name in parts:
            return name
    return "root" if "root" in package_names else None


def load_layout(spec_root: Path) -> dict[str, str]:
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


def collect_layer_root_context(
    root: Path,
    spec_root: Path,
    scope_layers: set[str] | None = None,
) -> tuple[list[dict[str, object]], list[str], list[str]]:
    packages = [{"name": "root", "layers": []}]
    package_indexes: list[str] = []
    recommended_reads: list[str] = []

    for layer_dir in sorted(spec_root.iterdir()):
        if not layer_dir.is_dir() or layer_dir.name == "guides":
            continue
        packages[0]["layers"].append(layer_dir.name)
        index_path = layer_dir / "index.md"
        if index_path.exists():
            rel = str(index_path.relative_to(root))
            package_indexes.append(rel)
            if scope_layers is None or layer_dir.name in scope_layers:
                recommended_reads.append(rel)

    return packages, package_indexes, recommended_reads


def collect_package_layer_context(
    root: Path,
    spec_root: Path,
    scoped_package_layers: set[tuple[str, str]] | None = None,
    wildcard_layers: set[str] | None = None,
) -> tuple[list[dict[str, object]], list[str], list[str]]:
    packages = []
    package_indexes: list[str] = []
    recommended_reads: list[str] = []
    wildcard_layers = wildcard_layers or set()

    for package_dir in sorted(spec_root.iterdir()):
        if not package_dir.is_dir() or package_dir.name == "guides":
            continue
        layers = []
        for layer_dir in sorted(package_dir.iterdir()):
            if not layer_dir.is_dir():
                continue
            layers.append(layer_dir.name)
            index_path = layer_dir / "index.md"
            if index_path.exists():
                rel = str(index_path.relative_to(root))
                package_indexes.append(rel)
                if scoped_package_layers is None:
                    recommended_reads.append(rel)
                elif (package_dir.name, layer_dir.name) in scoped_package_layers or layer_dir.name in wildcard_layers:
                    recommended_reads.append(rel)
        packages.append({"name": package_dir.name, "layers": layers})

    return packages, package_indexes, recommended_reads


def derive_layer_scope(changed_files: list[str]) -> set[str] | None:
    scope_layers: set[str] = set()
    for file_path in changed_files:
        parts = Path(file_path).parts
        # 忽略 `.superwork` 自身变更，避免会话启动阶段被流程文档改动误导。
        if not parts or parts[0] == ".superwork":
            continue
        scope_layers.add(detect_layer(parts))
    return scope_layers or None


def derive_package_layer_scope(spec_root: Path, changed_files: list[str]) -> tuple[set[tuple[str, str]] | None, set[str]]:
    scoped_package_layers: set[tuple[str, str]] = set()
    wildcard_layers: set[str] = set()

    for file_path in changed_files:
        parts = Path(file_path).parts
        if not parts or parts[0] == ".superwork":
            continue
        layer = detect_layer(parts)
        package = resolve_package_name(spec_root, parts)
        if package is None:
            wildcard_layers.add(layer)
            continue
        scoped_package_layers.add((package, layer))

    if not scoped_package_layers and not wildcard_layers:
        return None, set()
    return scoped_package_layers, wildcard_layers


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    package_manager = detect_package_manager(root)
    spec_root = root / ".superwork" / "spec"
    changed_files = git_changed_files(root)
    packages: list[dict[str, object]] = []
    package_indexes: list[str] = []
    recommended_reads: list[str] = []
    read_scope = "full"

    guides_index = spec_root / "guides" / "index.md"
    if guides_index.exists():
        recommended_reads.append(str(guides_index.relative_to(root)))

    # 从 `.superwork/spec` 反推布局，兼容旧结构和新的分层结构。
    if spec_root.exists():
        layout = load_layout(spec_root)
        if layout["mode"] == "layer-root":
            scope_layers = derive_layer_scope(changed_files)
            packages, package_indexes, package_reads = collect_layer_root_context(root, spec_root, scope_layers)
            if scope_layers:
                read_scope = "changed-files"
        else:
            scoped_package_layers, wildcard_layers = derive_package_layer_scope(spec_root, changed_files)
            packages, package_indexes, package_reads = collect_package_layer_context(
                root,
                spec_root,
                scoped_package_layers,
                wildcard_layers,
            )
            if scoped_package_layers is not None:
                read_scope = "changed-files"
        # 如果变更范围无法映射到任何 index，回退到全量索引，避免漏读。
        if changed_files and not package_reads:
            package_reads = package_indexes.copy()
            read_scope = "full-fallback"
        recommended_reads.extend(package_reads)

    payload = {
        "project": {
            "packageManager": package_manager,
            "testHints": detect_test_hints(root, package_manager),
            "packages": packages,
        },
        "spec": {
            "layout": load_layout(spec_root) if spec_root.exists() else None,
            "guidesIndex": str(guides_index.relative_to(root)) if guides_index.exists() else None,
            "packageIndexes": package_indexes,
            "recommendedReads": recommended_reads,
            "readScope": read_scope,
            "changedFiles": changed_files,
        },
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("Superwork context")
    print(f"- packageManager: {package_manager}")
    print("- packages:")
    for package in packages:
        print(f"  - {package['name']}: {', '.join(package['layers']) or 'none'}")
    print("- recommendedReads:")
    for item in recommended_reads:
        print(f"  - {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
