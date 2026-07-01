#!/usr/bin/env python3
"""Run a fast structural preflight before executing a saved superwork plan."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PLACEHOLDER_PATTERNS = (
    "TBD",
    "TODO",
    "implement later",
    "fill in details",
    "Add appropriate error handling",
    "add validation",
    "handle edge cases",
    "Similar to Task",
)
TASK_BLOCK_RE = re.compile(r"^### Task .+?(?=^### Task |\Z)", re.MULTILINE | re.DOTALL)
SECTION_RE_TEMPLATE = r"^## {title}\s*$\n(?P<body>.*?)(?=^## |\Z)"
SPEC_PATH_RE = re.compile(r"`(\.superwork/spec/[^`]+)`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def extract_section(text: str, title: str) -> str | None:
    match = re.search(SECTION_RE_TEMPLATE.format(title=re.escape(title)), text, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    return match.group("body").strip()


def extract_labeled_block(text: str, label: str) -> str | None:
    pattern = re.compile(
        rf"^\*\*{re.escape(label)}:\*\*\s*$\n(?P<body>.*?)(?=^\*\*|^## |^\-\-\-$|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return None
    return match.group("body").strip()


def extract_bullets(section_text: str | None) -> list[str]:
    if not section_text:
        return []
    bullets: list[str] = []
    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def extract_task_section(task_text: str, marker: str) -> str | None:
    pattern = re.compile(
        rf"^\*\*{re.escape(marker)}:\*\*\s*$\n(?P<body>.*?)(?=^\*\*|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(task_text)
    if not match:
        return None
    return match.group("body").strip()


def normalize_interface_name(interface_line: str) -> str | None:
    value = interface_line.strip()
    if not value or value == "[exact function, type, file contract, or artifact this task depends on]":
        return None
    # 用最保守的名字抽取方式检测跨任务接口漂移，避免做复杂语义解析。
    token = value.split("(", 1)[0].split(":", 1)[0].split(" ", 1)[0].strip("`")
    return token or None


def collect_interface_map(lines: list[str]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for line in lines:
        name = normalize_interface_name(line)
        if not name:
            continue
        mapping.setdefault(name, set()).add(line.strip())
    return mapping


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    plan_path = (root / args.plan).resolve() if not args.plan.is_absolute() else args.plan.resolve()
    issues: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not plan_path.exists():
        issues.append({"severity": "error", "message": f"plan file not found: {plan_path}"})
        return emit(args.format, plan_path, issues, warnings)

    plan_text = plan_path.read_text(encoding="utf-8")

    suggested_reads = extract_bullets(extract_labeled_block(plan_text, "Suggested Spec Reads"))
    constraint_lines = extract_bullets(extract_section(plan_text, "Global Constraints"))
    task_blocks = TASK_BLOCK_RE.findall(plan_text)

    if not suggested_reads:
        issues.append({"severity": "error", "message": "missing `Suggested Spec Reads` section or bullet entries"})
    for rel_path in SPEC_PATH_RE.findall("\n".join(suggested_reads)):
        if not (root / rel_path).exists():
            issues.append({"severity": "error", "message": f"referenced spec path does not exist: {rel_path}"})

    if not constraint_lines:
        issues.append({"severity": "error", "message": "missing `## Global Constraints` bullets"})

    for placeholder in PLACEHOLDER_PATTERNS:
        if placeholder in plan_text:
            issues.append({"severity": "error", "message": f"placeholder text found: {placeholder}"})

    if not task_blocks:
        issues.append({"severity": "error", "message": "plan contains no `### Task` blocks"})

    produced_map: dict[str, set[str]] = {}

    for index, task_text in enumerate(task_blocks, start=1):
        files_section = extract_task_section(task_text, "Files")
        interfaces_section = extract_task_section(task_text, "Interfaces")

        if not files_section:
            issues.append({"severity": "error", "message": f"Task {index} is missing `**Files:**`"})
        if not interfaces_section:
            issues.append({"severity": "error", "message": f"Task {index} is missing `**Interfaces:**`"})
            continue

        interface_lines = extract_bullets(interfaces_section)
        consumes = [line.removeprefix("Consumes:").strip() for line in interface_lines if line.startswith("Consumes:")]
        produces = [line.removeprefix("Produces:").strip() for line in interface_lines if line.startswith("Produces:")]

        if not consumes:
            issues.append({"severity": "error", "message": f"Task {index} is missing `Consumes`"})
        if not produces:
            issues.append({"severity": "error", "message": f"Task {index} is missing `Produces`"})

        # 当前任务可以消费旧接口并产出新接口，所以只检查“消费方”是否和更早任务产出的接口漂移。
        for line in consumes:
            name = normalize_interface_name(line)
            if not name:
                continue
            produced_values = produced_map.get(name)
            if produced_values and line not in produced_values:
                issues.append(
                    {
                        "severity": "error",
                        "message": f"interface drift for `{name}`: consumes `{line}` but earlier tasks produce {sorted(produced_values)}",
                    }
                )
            if not produced_values:
                warnings.append(
                    {
                        "severity": "warning",
                        "message": f"consumed interface `{name}` is not produced by an earlier task in this plan; verify it already exists in the codebase",
                    }
                )

        for name, values in collect_interface_map(produces).items():
            produced_map.setdefault(name, set()).update(values)

    for name, values in produced_map.items():
        if len(values) > 1:
            issues.append(
                {
                    "severity": "error",
                    "message": f"interface `{name}` is produced with conflicting signatures: {sorted(values)}",
                }
            )

    return emit(args.format, plan_path, issues, warnings)


def emit(
    output_format: str,
    plan_path: Path,
    issues: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> int:
    payload = {
        "plan": str(plan_path),
        "ok": not issues,
        "issues": issues,
        "warnings": warnings,
    }
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Plan preflight: {plan_path}")
        print("Status: PASS" if payload["ok"] else "Status: FAIL")
        if issues:
            print("Issues:")
            for item in issues:
                print(f"- {item['message']}")
        if warnings:
            print("Warnings:")
            for item in warnings:
                print(f"- {item['message']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
