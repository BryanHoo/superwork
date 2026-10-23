"""Read lightweight task notices without loading other agents' plans."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path


DIRECTORY = ".superwork/parallel"
GUIDE = ".superwork/parallel.md"
TASK_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,79}\Z")


def project_path(root: Path, value: str) -> str:
    """Validate a literal project-relative path, including paths not yet created."""
    path = Path(value)
    # 登记范围使用明确的文件或目录，不把通配符误当成已经覆盖的真实文件。
    if not value.strip() or path.is_absolute() or ".." in path.parts or any(c in value for c in "*?[]\\"):
        raise ValueError(f"expected a literal project-relative path: {value}")
    try:
        (root / path).resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"path is outside project: {value}") from error
    return path.as_posix()


def validate_record(root: Path, data: object, task_id: str) -> dict:
    if not TASK_ID.fullmatch(task_id):
        raise ValueError("id must use 1-80 lowercase letters, digits, hyphens or underscores")
    if not isinstance(data, dict) or data.get("id") != task_id:
        raise ValueError("record id must match its filename")
    for field in ("owner", "goal", "updatedAt"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"missing non-empty {field}")
    if data.get("status") not in ("running", "paused"):
        raise ValueError("status must be running or paused")
    reason = data.get("reason")
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise ValueError("reason must be a non-empty description or null")
    if data["status"] == "paused" and reason is None:
        raise ValueError("paused tasks require a reason")
    paths = data.get("writePaths")
    if not isinstance(paths, list) or not paths or not all(isinstance(path, str) for path in paths):
        raise ValueError("writePaths must contain project-relative files or directories")
    impacts = data.get("sharedImpact")
    if not isinstance(impacts, list) or not all(isinstance(item, str) and item.strip() for item in impacts):
        raise ValueError("sharedImpact must be a list of non-empty descriptions (or [])")
    plan = data.get("plan")
    if plan is not None and not isinstance(plan, str):
        raise ValueError("plan must be a project-relative path or null")
    # 摘要只暴露协作字段，不读计划正文，也不透传未知的大块上下文。
    return {
        "id": task_id,
        "owner": data["owner"],
        "goal": data["goal"],
        "status": data["status"],
        "writePaths": list(dict.fromkeys(project_path(root, path) for path in paths)),
        "sharedImpact": impacts,
        "plan": project_path(root, plan) if plan is not None else None,
        "reason": data.get("reason"),
        "updatedAt": data["updatedAt"],
    }


def registry_path(root: Path) -> Path:
    directory = root / DIRECTORY
    # 单项目目录协作不允许登记目录跳转到其他工作区；跨 worktree 共享不在此版本中推断。
    if directory.is_symlink() or not directory.resolve().is_relative_to(root.resolve()):
        raise ValueError("parallel directory must stay inside the current project")
    return directory


def read_record(root: Path, path: Path) -> dict:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("task record must be a regular JSON file")
    return validate_record(root, json.loads(path.read_text(encoding="utf-8")), path.stem)


def parallel_context(root: Path) -> dict:
    payload = {
        "status": "ready",
        "directory": DIRECTORY,
        "guide": GUIDE if (root / GUIDE).is_file() else None,
        "tasks": [],
        "errors": [],
    }
    try:
        directory = registry_path(root)
        # pathlib.glob 会吞掉部分扫描错误；使用 iterdir 区分“目录缺失”和“无权读取”。
        paths = sorted(path for path in directory.iterdir() if path.suffix == ".json")
    except FileNotFoundError:
        paths = []
    except (OSError, ValueError) as error:
        payload["errors"].append({"path": DIRECTORY, "error": str(error)})
        paths = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            payload["tasks"].append({**read_record(root, path), "recordPath": relative})
        except FileNotFoundError:
            # 其他执行者完成后可以删除自己的记录；扫描中的正常消失不应伪装成损坏记录。
            continue
        except (OSError, ValueError, UnicodeError) as error:
            payload["errors"].append({"path": relative, "error": str(error)})
    if payload["errors"]:
        payload["status"] = "error"
    return payload


def publish_text(path: Path, content: str, *, create: bool) -> None:
    """Publish complete bytes; exclusive creation never replaces another task."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".parallel-", suffix=".tmp")
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
        if create:
            # 完整文件发布为新名字；目标已存在时失败，不能把其他执行者的登记覆盖掉。
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def ensure_guide(root: Path) -> None:
    guide = root / GUIDE
    if guide.exists():
        if not guide.is_file():
            raise ValueError("parallel guide is not a file")
        return
    template = Path(__file__).resolve().parents[1] / "superwork-init/templates/parallel.md.tmpl"
    try:
        # 旧版 schema 2 项目只补协作说明，不重跑初始化或改写已有人工内容。
        publish_text(guide, template.read_text(encoding="utf-8"), create=True)
    except FileExistsError:
        pass


def ensure_local_ignore(root: Path) -> None:
    try:
        # 忽略运行中的 JSON 与原子写入临时文件；不修改项目根目录已有的忽略规则。
        publish_text(registry_path(root) / ".gitignore", "*.json\n.parallel-*.tmp\n", create=True)
    except FileExistsError:
        pass
