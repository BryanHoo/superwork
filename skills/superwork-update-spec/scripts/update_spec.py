#!/usr/bin/env python3
"""Suggest `.superwork/spec` update targets based on recent changes."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


KNOWN_LAYERS = {"frontend", "backend", "shared"}
NON_DURABLE_PARTS = {
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
    "fixture",
    "fixtures",
    "mock",
    "mocks",
    "__snapshots__",
    "snapshots",
    "docs",
    "doc",
}
NON_DURABLE_EXTENSIONS = {
    ".md",
    ".mdx",
    ".txt",
    ".rst",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".mp4",
    ".mp3",
    ".woff",
    ".woff2",
    ".map",
}
NON_DURABLE_FILENAMES = {
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "cargo.lock",
}
DURABLE_SIGNAL_PARTS = {
    "api",
    "apis",
    "route",
    "routes",
    "controller",
    "controllers",
    "handler",
    "handlers",
    "server",
    "service",
    "services",
    "db",
    "database",
    "migration",
    "migrations",
    "schema",
    "schemas",
    "contract",
    "contracts",
    "protocol",
    "interface",
    "interfaces",
    "config",
    "configs",
}
DURABLE_SIGNAL_NAME_MARKERS = (
    "contract",
    "schema",
    "migration",
    "openapi",
    "swagger",
    "route",
    "endpoint",
    "interface",
    "protocol",
    "config",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


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


def load_layout(spec_root: Path) -> dict[str, str]:
    # 优先读运行态元数据；缺失时再根据目录结构推断，避免手写项目失配。
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


def guess_layer_doc(layer: str, parts: tuple[str, ...]) -> str:
    # 回写时尽量落到最接近改动语义的规范文档，减少所有规则都堆到一个文件里。
    part_set = set(parts)
    if layer == "frontend":
        if part_set & {"components", "component"}:
            return "component-guidelines.md"
        if part_set & {"hooks", "hook", "composables"}:
            return "hook-guidelines.md"
        if part_set & {"store", "stores", "state"}:
            return "state-management.md"
        if part_set & {"types", "schema", "schemas", "zod"}:
            return "type-safety.md"
        if part_set & {"pages", "app", "routes", "router", "views"}:
            return "directory-structure.md"
        return "quality-guidelines.md"
    if layer == "backend":
        if part_set & {"scripts", "script", "cli", "bin"}:
            return "script-conventions.md"
        if part_set & {"db", "database", "migration", "migrations", "prisma", "schema", "sql"}:
            return "database-guidelines.md"
        if part_set & {"log", "logger", "logging"}:
            return "logging-guidelines.md"
        if part_set & {"api", "server", "controller", "controllers", "route", "routes", "handler", "handlers", "middleware"}:
            return "error-handling.md"
        return "quality-guidelines.md"
    if part_set & {"shared", "common", "lib", "utils"}:
        return "directory-structure.md"
    return "quality-guidelines.md"


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


def classify_change_for_spec(file_path: str) -> tuple[bool, str]:
    parts = Path(file_path).parts
    if not parts:
        return False, "empty path"

    # 已在 spec 内的改动不需要再次触发 spec 更新建议。
    if len(parts) >= 2 and parts[0] == ".superwork" and parts[1] == "spec":
        return False, "already inside .superwork/spec"

    name = Path(file_path).name.lower()
    suffix = Path(file_path).suffix.lower()

    if name in NON_DURABLE_FILENAMES:
        return False, "lockfile change"
    if suffix in NON_DURABLE_EXTENSIONS:
        return False, f"non-durable extension {suffix}"
    if any(marker in name for marker in (".spec.", ".test.", "_spec.", "_test.")):
        return False, "test-only filename pattern"
    if any(part in NON_DURABLE_PARTS for part in parts):
        return False, "test/docs/mock fixture path"

    # 只有命中“高信号”契约变更位置时才建议 spec 更新，避免每次代码改动都扩写文档。
    normalized_parts = {part.lower() for part in parts}
    if normalized_parts & DURABLE_SIGNAL_PARTS:
        return True, "matched durable signal path"
    if any(marker in name for marker in DURABLE_SIGNAL_NAME_MARKERS):
        return True, "matched durable signal filename"

    # 其余代码改动默认不触发，交给技能最终人工判断是否例外更新。
    return False, "no durable signal for spec updates"


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    changed_files = git_changed_files(root)
    spec_root = root / ".superwork" / "spec"
    if not spec_root.exists():
        payload = {
            "decision": "no-update",
            "targets": [],
            "ignoredChanges": [],
            "summary": ["spec root is missing, run superwork-init before updating spec"],
        }
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        print("Superwork spec update suggestion")
        print("- decision: no-update")
        print("  - spec root is missing, run superwork-init before updating spec")
        return 0

    layout = load_layout(spec_root)
    targets = []
    ignored_changes = []
    seen: set[str] = set()

    # 这里只做建议，不替代 skill 对“是否真的要更新 spec”的最终判断。
    for file_path in changed_files:
        parts = Path(file_path).parts
        if not parts:
            continue
        can_update, reason = classify_change_for_spec(file_path)
        if not can_update:
            ignored_changes.append({"path": file_path, "reason": reason})
            continue
        layer = detect_layer(parts)
        if layout["mode"] == "layer-root":
            # 单仓库新布局：直接写到 layer 目录下。
            target_path = spec_root / layer / guess_layer_doc(layer, parts)
        else:
            # 多包或旧布局：先确定 package，再决定规范文档落点。
            package = resolve_package_name(spec_root, parts) or (parts[0] if len(parts) > 1 else "root")
            guide_name = guess_layer_doc(layer, parts) if layout["type"] == "layered" else f"{layer}-guidelines.md"
            target_path = spec_root / package / layer / guide_name
        rel = str(target_path.relative_to(root))
        if rel in seen:
            continue
        seen.add(rel)
        targets.append(
            {
                "path": rel,
                "action": "update" if target_path.exists() else "create",
                "reason": f"changed file {file_path} may introduce durable {layer} rules",
            }
        )

    has_create_target = any(target["action"] == "create" for target in targets)
    payload = {
        "decision": ("create" if has_create_target else "update") if targets else "no-update",
        "targets": targets,
        "ignoredChanges": ignored_changes,
        "summary": [],
    }
    if targets:
        payload["summary"].append("capture durable rules, contracts, edge cases, or verification requirements")
    else:
        payload["summary"].append("no durable spec update detected from changed files")
    if ignored_changes:
        payload["summary"].append(f"ignored {len(ignored_changes)} non-durable change(s)")

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("Superwork spec update suggestion")
    print(f"- decision: {payload['decision']}")
    for target in targets:
        print(f"  - {target['path']}: {target['action']} ({target['reason']})")
    for ignored in ignored_changes:
        print(f"  - ignored {ignored['path']}: {ignored['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
