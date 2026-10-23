#!/usr/bin/env python3
"""List, register, update, or finish one owner's lightweight task notice."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2]
if str(SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILLS_ROOT))

from _shared.parallel import (  # noqa: E402
    TASK_ID,
    ensure_guide,
    ensure_local_ignore,
    parallel_context,
    publish_text,
    read_record,
    registry_path,
    validate_record,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("list", "register", "update", "finish"):
        command = commands.add_parser(action)
        command.add_argument("--root", type=Path, default=Path.cwd())
        if action == "list":
            continue
        command.add_argument("--id", required=True)
        command.add_argument("--owner", required=True)
        if action == "finish":
            continue
        command.add_argument("--goal", required=action == "register")
        command.add_argument("--files", nargs="+", required=action == "register")
        command.add_argument("--impact", action="append", help="Repeat for public interface or resource impacts")
        command.add_argument("--plan")
        if action == "update":
            command.add_argument("--status", choices=("running", "paused"))
            command.add_argument("--reason")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        if args.action == "list":
            context = parallel_context(root)
            print(json.dumps(context, ensure_ascii=False, indent=2))
            return 0 if context["status"] == "ready" else 1

        # 登记是现有项目的任务产物，不授予初始化缺失或不兼容运行配置的权限。
        config = json.loads((root / ".superwork/config.json").read_text(encoding="utf-8"))
        if not isinstance(config, dict) or config.get("schemaVersion") != 2:
            raise ValueError("parallel writes require a ready schemaVersion 2 runtime")
        if not TASK_ID.fullmatch(args.id):
            raise ValueError("invalid task id")
        if not args.owner.strip():
            raise ValueError("owner must not be empty")
        path = registry_path(root) / f"{args.id}.json"
        if args.action == "register":
            record = {"id": args.id, "owner": args.owner, "status": "running",
                      "sharedImpact": [], "plan": None, "reason": None}
        else:
            record = read_record(root, path)
            if record["owner"] != args.owner:
                raise ValueError("owner mismatch; leave the other executor's record untouched")
            if args.action == "finish":
                path.unlink()
                print(json.dumps({"ok": True, "removed": args.id}, ensure_ascii=False))
                return 0

        for argument, field in (("goal", "goal"), ("files", "writePaths"),
                                ("impact", "sharedImpact"), ("plan", "plan"),
                                ("status", "status"), ("reason", "reason")):
            value = getattr(args, argument, None)
            if value is not None:
                record[field] = value
        if record["status"] == "running":
            record["reason"] = None
        record["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        record = validate_record(root, record, args.id)
        ensure_guide(root)
        ensure_local_ignore(root)
        publish_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                     create=args.action == "register")
        # 登记后再次返回整个公告板，提醒执行者处理同时到达的其他任务；脚本不代替语义判断。
        context = parallel_context(root)
        print(json.dumps({"ok": context["status"] == "ready", "task": record, "parallel": context},
                         ensure_ascii=False, indent=2))
        return 0 if context["status"] == "ready" else 1
    except (OSError, ValueError, UnicodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
