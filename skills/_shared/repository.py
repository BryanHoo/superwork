"""Detect repository tooling and Git changes without inventing project commands."""

from __future__ import annotations

import json
import os
import subprocess
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path


GIT_TIMEOUT_SECONDS = 10
IGNORED_WALK_DIRS = {
    ".git",
    ".superwork",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "venv",
}


@dataclass(frozen=True)
class ChangeDetection:
    status: str
    files: list[str]
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _read_package_json(root: Path) -> dict[str, object]:
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    try:
        payload = json.loads(package_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def detect_package_manager(root: Path) -> str:
    package = _read_package_json(root)
    declared = package.get("packageManager")
    if isinstance(declared, str):
        manager = declared.split("@", 1)[0]
        if manager in {"npm", "pnpm", "yarn", "bun"}:
            return manager

    # 显式声明优先；多 lockfile 仓库按 npm、pnpm、yarn、bun 的稳定顺序收敛。
    markers = (
        ("package-lock.json", "npm"),
        ("npm-shrinkwrap.json", "npm"),
        ("pnpm-lock.yaml", "pnpm"),
        ("pnpm-workspace.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lock", "bun"),
        ("bun.lockb", "bun"),
    )
    for marker, manager in markers:
        if (root / marker).exists():
            return manager
    if (root / "package.json").exists():
        return "npm"
    if (root / "uv.lock").exists():
        return "uv"
    if (root / "poetry.lock").exists():
        return "poetry"
    return "none"


def _python_test_directories(root: Path) -> list[str]:
    directories: set[str] = set()
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_WALK_DIRS]
        if any(name.startswith("test_") and name.endswith(".py") for name in filenames):
            directories.add(str(Path(current).relative_to(root)))
    return sorted(directories, key=lambda value: (value.count(os.sep), value))


def _pyproject_uses_pytest(root: Path) -> bool:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return False
    try:
        payload = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return False
    tool = payload.get("tool")
    return isinstance(tool, dict) and isinstance(tool.get("pytest"), dict)


def detect_verification_commands(root: Path, package_manager: str) -> list[str]:
    package = _read_package_json(root)
    scripts = package.get("scripts")
    if package_manager in {"npm", "pnpm", "yarn", "bun"} and isinstance(scripts, dict):
        commands: list[str] = []
        for name in ("test", "test:run", "lint", "typecheck", "build"):
            if name not in scripts:
                continue
            separator = " " if name == "test" else " run "
            commands.append(f"{package_manager}{separator}{name}")
        return commands

    if (root / "Cargo.toml").exists():
        return ["cargo test"]
    if (root / "go.mod").exists():
        return ["go test ./..."]
    if (root / "pom.xml").exists():
        return ["mvn test"]
    if (root / "gradlew").exists():
        return ["./gradlew test"]

    python_markers = (
        "pyproject.toml",
        "pytest.ini",
        "setup.cfg",
        "setup.py",
        "requirements.txt",
    )
    python_tests = _python_test_directories(root)
    if any((root / marker).exists() for marker in python_markers) or python_tests:
        python_command = {
            "uv": "uv run python3",
            "poetry": "poetry run python3",
        }.get(package_manager, "python3")
        if (root / "pytest.ini").exists() or (root / "conftest.py").exists() or _pyproject_uses_pytest(root):
            return [f"{python_command} -m pytest"]
        return [
            f"{python_command} -m unittest discover -s {directory} -p 'test_*.py' -v"
            for directory in python_tests
        ]
    return []


def collect_git_changes(root: Path) -> ChangeDetection:
    commands = (
        ["git", "-C", str(root), "diff", "--name-only", "HEAD"],
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
    )
    files: list[str] = []
    seen: set[str] = set()
    try:
        for command in commands:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=GIT_TIMEOUT_SECONDS,
            )
            if completed.returncode != 0:
                error = completed.stderr.strip() or f"git exited with status {completed.returncode}"
                return ChangeDetection(status="unavailable", files=[], error=error)
            for raw_line in completed.stdout.splitlines():
                file_path = raw_line.strip()
                if file_path and file_path not in seen:
                    files.append(file_path)
                    seen.add(file_path)
    except FileNotFoundError:
        return ChangeDetection(status="unavailable", files=[], error="git executable not found")
    except subprocess.TimeoutExpired:
        return ChangeDetection(status="unavailable", files=[], error="git change detection timed out")
    return ChangeDetection(status="ready", files=files)
