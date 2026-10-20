from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BOOTSTRAP_SCRIPT = REPO_ROOT / "skills" / "superwork-init" / "scripts" / "bootstrap_superwork.py"
GET_CONTEXT_SCRIPT = REPO_ROOT / "skills" / "superwork-start" / "scripts" / "get_context.py"
CHECK_SPECS_SCRIPT = REPO_ROOT / "skills" / "superwork-check" / "scripts" / "check_specs.py"
UPDATE_SPEC_SCRIPT = REPO_ROOT / "skills" / "superwork-check" / "scripts" / "update_spec.py"
PREFLIGHT_PLAN_SCRIPT = (
    REPO_ROOT / "skills" / "superwork-executing-plans" / "scripts" / "preflight_plan.py"
)
PLANNING_SKILL = REPO_ROOT / "skills" / "superwork-planning" / "SKILL.md"


class SuperworkFixtureTestCase(unittest.TestCase):
    def run_command(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args),
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def init_git_repo(self, root: Path) -> None:
        self.run_command("git", "init", cwd=root)
        self.run_command("git", "add", ".", cwd=root)
        commit = self.run_command(
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "init",
            cwd=root,
        )
        self.assertEqual(commit.returncode, 0, commit.stderr)

    def create_single_repo_fixture(self, root: Path) -> None:
        self.write_file(
            root / "package.json",
            json.dumps(
                {
                    "name": "demo-app",
                    "scripts": {
                        "test": "vitest",
                        "lint": "eslint .",
                    },
                }
            ),
        )
        self.write_file(root / "src" / "components" / "Button.tsx", "export const Button = () => null;\n")
        self.write_file(root / "server" / "index.ts", "export const server = true;\n")

    def bootstrap_spec(self, root: Path) -> dict[str, object]:
        result = self.run_command("python3", str(BOOTSTRAP_SCRIPT), "--root", str(root))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)
