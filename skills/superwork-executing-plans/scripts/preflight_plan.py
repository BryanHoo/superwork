#!/usr/bin/env python3
"""Run a compact structural preflight before resuming a saved Superwork plan."""

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
TASK_HEADING_FORMAT = "### Task <number>: <title>"
TASK_BLOCK_RE = re.compile(
    r"^### (?P<id>Task (?P<number>\d+)): (?P<title>.+?)\s*$\n(?P<body>.*?)(?=^### Task \d+: |\Z)",
    re.MULTILINE | re.DOTALL,
)
TASK_STATUS_RE = re.compile(
    r"^- \[(?P<checked>[ xX])\] \*\*Task Status:\*\* (?P<status>pending|completed)\s*$",
    re.MULTILINE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def extract_inline_field(text: str, label: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(label)}:\*\*\s+(?P<value>\S.*)$", text, re.MULTILINE)
    return match.group("value").strip() if match else None


def extract_task_section(task_text: str, marker: str) -> str | None:
    pattern = re.compile(
        rf"^\*\*{re.escape(marker)}:\*\*\s*$\n(?P<body>.*?)(?=^\*\*|^- \[[ xX]\] \*\*Task Status|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(task_text)
    return match.group("body").strip() if match else None


def extract_bullets(section_text: str | None) -> list[str]:
    if not section_text:
        return []
    return [
        line[2:].strip()
        for raw_line in section_text.splitlines()
        if (line := raw_line.strip()).startswith("- ") and line[2:].strip()
    ]


def validate_header(plan_text: str, issues: list[dict[str, str]]) -> None:
    for label in ("Goal", "Scope", "Acceptance"):
        if not extract_inline_field(plan_text, label):
            issues.append({"severity": "error", "message": f"missing `**{label}:**` value"})


def validate_status(
    task_text: str,
    task_number: int,
    issues: list[dict[str, str]],
) -> str | None:
    matches = list(TASK_STATUS_RE.finditer(task_text))
    if not matches:
        issues.append(
            {"severity": "error", "message": f"Task {task_number} is missing `Task Status` checkbox"}
        )
        return None
    if len(matches) > 1:
        issues.append(
            {"severity": "error", "message": f"Task {task_number} has multiple `Task Status` checkboxes"}
        )
        return None

    match = matches[0]
    status = match.group("status")
    checked = match.group("checked").lower() == "x"
    if checked != (status == "completed"):
        issues.append(
            {"severity": "error", "message": f"Task {task_number} has inconsistent `Task Status` checkbox"}
        )
        return None
    return status


def validate_task_sections(
    task_text: str,
    task_number: int,
    issues: list[dict[str, str]],
) -> None:
    for label in ("Files", "Behavior", "Stop Conditions"):
        section = extract_task_section(task_text, label)
        if not extract_bullets(section):
            issues.append(
                {"severity": "error", "message": f"Task {task_number} is missing `**{label}:**` bullets"}
            )
    if not extract_inline_field(task_text, "Proof"):
        issues.append({"severity": "error", "message": f"Task {task_number} is missing `**Proof:**`"})


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    plan_path = (root / args.plan).resolve() if not args.plan.is_absolute() else args.plan.resolve()
    issues: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not plan_path.exists():
        issues.append({"severity": "error", "message": f"plan file not found: {plan_path}"})
        return emit(args.format, plan_path, issues, warnings, [])

    plan_text = plan_path.read_text(encoding="utf-8")
    validate_header(plan_text, issues)

    for placeholder in PLACEHOLDER_PATTERNS:
        if placeholder in plan_text:
            issues.append({"severity": "error", "message": f"placeholder text found: {placeholder}"})

    task_matches = list(TASK_BLOCK_RE.finditer(plan_text))
    if not task_matches:
        issues.append(
            {
                "severity": "error",
                "message": f"plan contains no task blocks; expected `{TASK_HEADING_FORMAT}`",
            }
        )

    tasks: list[dict[str, str]] = []
    for expected_number, task_match in enumerate(task_matches, start=1):
        actual_number = int(task_match.group("number"))
        if actual_number != expected_number:
            issues.append(
                {
                    "severity": "error",
                    "message": f"Task numbering must be sequential; expected {expected_number}, found {actual_number}",
                }
            )

        task_text = task_match.group(0)
        validate_task_sections(task_text, expected_number, issues)
        status = validate_status(task_text, expected_number, issues)
        proof = extract_inline_field(task_text, "Proof")
        if status and proof:
            tasks.append(
                {
                    "id": task_match.group("id"),
                    "title": task_match.group("title").strip(),
                    "status": status,
                    "proof": proof,
                }
            )

    return emit(args.format, plan_path, issues, warnings, tasks)


def emit(
    output_format: str,
    plan_path: Path,
    issues: list[dict[str, str]],
    warnings: list[dict[str, str]],
    tasks: list[dict[str, str]],
) -> int:
    payload = {
        "plan": str(plan_path),
        "ok": not issues,
        "issues": issues,
        "warnings": warnings,
        "tasks": tasks,
    }
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Plan preflight: {plan_path}")
        print("Status: PASS" if payload["ok"] else "Status: FAIL")
        for heading, entries in (("Issues", issues), ("Warnings", warnings)):
            if entries:
                print(f"{heading}:")
                for item in entries:
                    print(f"- {item['message']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
