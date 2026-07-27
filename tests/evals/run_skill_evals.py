#!/usr/bin/env python3
"""Run repeatable Superwork trigger and route evaluations with Codex CLI."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_RE = re.compile(r"Superwork route:\s*(direct-response|superwork-[a-z-]+)\s*-")
REQUIRED_CASE_FIELDS = {"id", "query", "should_trigger"}


def validate_cases(cases: object) -> None:
    if not isinstance(cases, list) or not cases:
        raise ValueError("eval dataset must be a non-empty list")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or not REQUIRED_CASE_FIELDS <= set(case):
            raise ValueError("each eval case requires id, query, and should_trigger")
        if not isinstance(case["id"], str) or case["id"] in seen:
            raise ValueError(f"duplicate or invalid eval id: {case.get('id')}")
        seen.add(case["id"])
        if not isinstance(case["query"], str) or not case["query"].strip():
            raise ValueError(f"eval query must be non-empty: {case['id']}")
        if not isinstance(case["should_trigger"], bool):
            raise ValueError(f"should_trigger must be boolean: {case['id']}")
        if case["should_trigger"] and not isinstance(case.get("expected_route"), str):
            raise ValueError(f"triggering case requires expected_route: {case['id']}")
        if not case["should_trigger"] and "expected_route" in case:
            raise ValueError(f"non-triggering case cannot set expected_route: {case['id']}")


def _collect_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in _collect_strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _collect_strings(item)]
    return []


def parse_jsonl_output(output: str) -> dict[str, object]:
    route: str | None = None
    final_message = ""
    events: list[dict[str, Any]] = []
    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        events.append(event)
        strings = _collect_strings(event)
        for text in strings:
            match = ROUTE_RE.search(text)
            if match:
                route = match.group(1)
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str):
                final_message = text
        response = event.get("final_response")
        if isinstance(response, str):
            final_message = response
    return {"route": route, "finalMessage": final_message, "eventCount": len(events)}


def evaluate_case(
    case: dict[str, object],
    runs: list[dict[str, object]],
    threshold: float,
) -> dict[str, object]:
    invalid_runs = [run for run in runs if run.get("exitCode", 0) != 0]
    trigger_count = sum(run.get("triggered") is True for run in runs)
    expected_route = case.get("expected_route")
    route_count = sum(run.get("route") == expected_route for run in runs) if expected_route else 0
    trigger_rate = trigger_count / len(runs)
    route_accuracy = route_count / len(runs) if expected_route else None
    if case["should_trigger"]:
        passed = trigger_rate >= threshold and route_accuracy is not None and route_accuracy >= threshold
    else:
        passed = trigger_rate < threshold
    passed = passed and not invalid_runs
    return {
        "id": case["id"],
        "shouldTrigger": case["should_trigger"],
        "expectedRoute": expected_route,
        "triggerRate": trigger_rate,
        "routeAccuracy": route_accuracy,
        "invalidRuns": len(invalid_runs),
        "passed": passed,
        "runs": runs,
    }


def create_fixture(fixture: Path, skills_root: Path) -> None:
    fixture.mkdir(parents=True, exist_ok=False)
    installed_skills = fixture / ".agents" / "skills"
    installed_skills.mkdir(parents=True)
    for skill_dir in sorted(skills_root.glob("superwork-*")):
        if (skill_dir / "SKILL.md").exists():
            (installed_skills / skill_dir.name).symlink_to(skill_dir.resolve(), target_is_directory=True)

    # fixture 只提供路由所需的最小项目事实，不承载任何真实用户代码。
    config = {
        "schemaVersion": 2,
        "packageManager": "none",
        "packages": [{"name": "root", "layers": ["shared"]}],
        "artifactPaths": {
            "designs": ".superwork/prd",
            "plans": ".superwork/plans",
            "specs": ".superwork/spec",
        },
        "verification": [],
    }
    config_path = fixture / ".superwork" / "config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    guides = fixture / ".superwork" / "spec" / "guides" / "index.md"
    guides.parent.mkdir(parents=True)
    guides.write_text("# Eval Guides\n\n- Keep evaluation read-only.\n", encoding="utf-8")
    shared = fixture / ".superwork" / "spec" / "shared" / "index.md"
    shared.parent.mkdir(parents=True)
    shared.write_text("# Eval Shared Rules\n\n- Use the smallest valid route.\n", encoding="utf-8")
    (fixture / "src").mkdir()
    (fixture / "src" / "validator.py").write_text("def validate(value):\n    return bool(value)\n", encoding="utf-8")
    plan = fixture / ".superwork" / "plans" / "demo.md"
    plan.parent.mkdir(parents=True)
    plan.write_text(
        "# Demo Plan\n\n- [ ] **Task Status:** pending\n\nExpected: PASS\n",
        encoding="utf-8",
    )


def build_codex_command(codex_bin: str, fixture: Path, prompt: str) -> list[str]:
    return [
        codex_bin,
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--cd",
        str(fixture),
        prompt,
    ]


def run_once(codex_bin: str, fixture: Path, prompt: str, timeout: int) -> dict[str, object]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            build_codex_command(codex_bin, fixture, prompt),
            check=False,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except subprocess.TimeoutExpired as error:
        return {
            "triggered": False,
            "route": None,
            "exitCode": None,
            "durationMs": round((time.monotonic() - started) * 1000),
            "error": f"timed out after {error.timeout} seconds",
        }
    parsed = parse_jsonl_output(completed.stdout)
    return {
        "triggered": parsed["route"] is not None,
        "route": parsed["route"],
        "exitCode": completed.returncode,
        "durationMs": round((time.monotonic() - started) * 1000),
        "eventCount": parsed["eventCount"],
        "finalMessage": parsed["finalMessage"],
        "error": completed.stderr.strip() or None,
    }


def run_suite(
    cases: list[dict[str, object]],
    skills_root: Path,
    codex_bin: str,
    runs_per_case: int,
    threshold: float,
    timeout: int,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="superwork-eval-") as temp_dir:
        fixture = Path(temp_dir) / "fixture"
        create_fixture(fixture, skills_root)
        results = []
        for case in cases:
            runs = [run_once(codex_bin, fixture, str(case["query"]), timeout) for _ in range(runs_per_case)]
            results.append(evaluate_case(case, runs, threshold))
    return {
        "passed": all(result["passed"] for result in results),
        "passedCases": sum(result["passed"] for result in results),
        "totalCases": len(results),
        "cases": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live Superwork trigger and route evaluations.")
    parser.add_argument("--split", choices=("train", "validation", "all"), default="all")
    parser.add_argument("--skills-root", type=Path, default=REPO_ROOT / "skills")
    parser.add_argument("--baseline-skills-root", type=Path)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = {
        "train": REPO_ROOT / "tests" / "evals" / "trigger_train.json",
        "validation": REPO_ROOT / "tests" / "evals" / "trigger_validation.json",
    }
    selected = paths if args.split == "all" else {args.split: paths[args.split]}
    cases = [case for path in selected.values() for case in json.loads(path.read_text(encoding="utf-8"))]
    validate_cases(cases)
    if args.limit is not None:
        cases = cases[: args.limit]
    if args.runs < 1 or args.timeout < 1 or not 0 < args.threshold <= 1:
        raise SystemExit("runs and timeout must be positive; threshold must be in (0, 1]")

    report: dict[str, object] = {
        "config": {
            "split": args.split,
            "runs": args.runs,
            "threshold": args.threshold,
            "timeout": args.timeout,
        },
        "current": run_suite(
            cases,
            args.skills_root.resolve(),
            args.codex_bin,
            args.runs,
            args.threshold,
            args.timeout,
        ),
    }
    if args.baseline_skills_root:
        report["baseline"] = run_suite(
            cases,
            args.baseline_skills_root.resolve(),
            args.codex_bin,
            args.runs,
            args.threshold,
            args.timeout,
        )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["current"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
