from __future__ import annotations

import json
import subprocess
import tempfile
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
WRITING_PLANS_SKILL = REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md"


class LayeredSpecLayoutTest(unittest.TestCase):
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

    def test_bootstrap_creates_layered_layout_for_single_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)

            self.bootstrap_spec(root)

            self.assertTrue((root / ".superwork" / "spec" / "frontend" / "index.md").exists())
            self.assertTrue(
                (root / ".superwork" / "spec" / "frontend" / "component-guidelines.md").exists()
            )
            self.assertTrue((root / ".superwork" / "spec" / "backend" / "index.md").exists())
            self.assertFalse((root / ".superwork" / "spec" / "root").exists())

    def test_bootstrap_creates_config_v2_without_workflow_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)

            payload = self.bootstrap_spec(root)

            config_path = root / ".superwork" / "config.json"
            self.assertTrue(config_path.exists())
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["schemaVersion"], 2)
            self.assertEqual(config["packageManager"], "npm")
            self.assertEqual(
                config["artifactPaths"],
                {
                    "designs": ".superwork/prd",
                    "plans": ".superwork/plans",
                    "specs": ".superwork/spec",
                },
            )
            self.assertFalse((root / ".superwork" / "workflow.md").exists())
            self.assertIn(".superwork/config.json", payload["created"])

    def test_bootstrap_python_repo_uses_python_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_file(root / "pyproject.toml", "[project]\nname = \"demo\"\nversion = \"0.1.0\"\n")
            self.write_file(
                root / "tests" / "test_demo.py",
                "import unittest\n\nclass DemoTest(unittest.TestCase):\n    pass\n",
            )

            self.bootstrap_spec(root)

            config = json.loads((root / ".superwork" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["packageManager"], "none")
            self.assertEqual(
                config["verification"],
                ["python3 -m unittest discover -s tests -p 'test_*.py' -v"],
            )

    def test_bootstrap_empty_repo_does_not_invent_node_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            self.bootstrap_spec(root)

            config = json.loads((root / ".superwork" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["packageManager"], "none")
            self.assertEqual(config["verification"], [])

    def test_bootstrap_prefers_declared_node_package_manager(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_file(
                root / "package.json",
                json.dumps(
                    {
                        "name": "declared-manager",
                        "packageManager": "yarn@4.2.0",
                        "scripts": {"test": "vitest", "lint": "eslint ."},
                    }
                ),
            )
            self.write_file(root / "package-lock.json", "{}\n")

            self.bootstrap_spec(root)

            config = json.loads((root / ".superwork" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["packageManager"], "yarn")
            self.assertEqual(config["verification"], ["yarn test", "yarn run lint"])

    def test_bootstrap_uses_uv_for_pyproject_pytest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_file(
                root / "pyproject.toml",
                "[project]\nname = \"demo\"\nversion = \"0.1.0\"\n\n[tool.pytest.ini_options]\naddopts = \"-q\"\n",
            )
            self.write_file(root / "uv.lock", "version = 1\n")
            self.write_file(root / "tests" / "test_demo.py", "def test_demo():\n    assert True\n")

            self.bootstrap_spec(root)

            config = json.loads((root / ".superwork" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["packageManager"], "uv")
            self.assertEqual(config["verification"], ["uv run python3 -m pytest"])

    def test_generated_guides_do_not_copy_generic_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            guides = (root / ".superwork" / "spec" / "guides" / "index.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn(".superwork/workflow.md", guides)
            self.assertNotIn("superwork-code-simplifier", guides)
            self.assertNotIn("superwork-update-spec", guides)
            self.assertIn(".superwork/config.json", guides)

    def test_get_context_reports_ready_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            result = self.run_command(
                "python3", str(GET_CONTEXT_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["runtime"]["status"], "ready")
            self.assertEqual(payload["runtime"]["path"], ".superwork/config.json")
            self.assertNotIn("workflow", payload)

    def test_get_context_reports_missing_runtime_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)

            result = self.run_command(
                "python3", str(GET_CONTEXT_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["runtime"]["status"], "missing")
            self.assertFalse((root / ".superwork").exists())

    def test_get_context_reads_layered_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            result = self.run_command(
                "python3", str(GET_CONTEXT_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn(".superwork/spec/guides/index.md", payload["spec"]["recommendedReads"])
            self.assertIn(".superwork/spec/frontend/index.md", payload["spec"]["recommendedReads"])
            self.assertIn(".superwork/spec/backend/index.md", payload["spec"]["recommendedReads"])

    def test_get_context_scopes_recommended_reads_by_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.init_git_repo(root)
            self.write_file(
                root / "src" / "components" / "Button.tsx",
                "export const Button = () => 'changed';\n",
            )

            result = self.run_command(
                "python3", str(GET_CONTEXT_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            recommended_reads = set(payload["spec"]["recommendedReads"])
            self.assertIn(".superwork/spec/guides/index.md", recommended_reads)
            self.assertIn(".superwork/spec/frontend/index.md", recommended_reads)
            self.assertNotIn(".superwork/spec/backend/index.md", recommended_reads)

    def test_get_context_includes_untracked_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.init_git_repo(root)
            self.write_file(root / "server" / "new_handler.ts", "export const handler = true;\n")

            result = self.run_command(
                "python3", str(GET_CONTEXT_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("server/new_handler.ts", payload["spec"]["changedFiles"])
            self.assertEqual(payload["changeDetection"]["status"], "ready")

    def test_get_context_reports_git_detection_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)

            result = self.run_command(
                "python3", str(GET_CONTEXT_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["changeDetection"]["status"], "unavailable")
            self.assertTrue(payload["changeDetection"]["error"])

    def test_check_specs_matches_untracked_frontend_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.init_git_repo(root)
            self.write_file(root / "src" / "components" / "Input.tsx", "export const Input = () => null;\n")

            result = self.run_command(
                "python3", str(CHECK_SPECS_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("src/components/Input.tsx", payload["changedFiles"])
            relevant_paths = {item["path"] for item in payload["relevantSpecs"]}
            self.assertIn(".superwork/spec/frontend/index.md", relevant_paths)
            self.assertIn(".superwork/spec/frontend/component-guidelines.md", relevant_paths)

    def test_update_spec_targets_layered_guideline_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.init_git_repo(root)
            self.write_file(
                root / "src" / "components" / "Button.tsx",
                "export const Button = () => 'changed';\n",
            )

            result = self.run_command(
                "python3", str(UPDATE_SPEC_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            targets = {item["path"]: item["action"] for item in payload["targets"]}
            self.assertEqual(
                targets.get(".superwork/spec/frontend/component-guidelines.md"), "update"
            )

    def test_update_spec_targets_untracked_frontend_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.init_git_repo(root)
            self.write_file(root / "src" / "components" / "Input.tsx", "export const Input = () => null;\n")

            result = self.run_command(
                "python3", str(UPDATE_SPEC_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            targets = {item["path"]: item["action"] for item in payload["targets"]}
            self.assertEqual(
                targets.get(".superwork/spec/frontend/component-guidelines.md"), "update"
            )

    def test_update_spec_returns_no_update_for_test_only_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.write_file(
                root / "src" / "components" / "Button.spec.tsx",
                "describe('Button', () => { it('works', () => {}); });\n",
            )
            self.bootstrap_spec(root)
            self.init_git_repo(root)
            self.write_file(
                root / "src" / "components" / "Button.spec.tsx",
                "describe('Button', () => { it('works better', () => {}); });\n",
            )

            result = self.run_command(
                "python3", str(UPDATE_SPEC_SCRIPT), "--root", str(root), "--format", "json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "no-update")
            self.assertEqual(payload["targets"], [])

    def test_preflight_plan_still_validates_required_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.write_file(
                root / ".superwork" / "plans" / "demo.md",
                """# Demo Implementation Plan

**Goal:** Build the demo change

**Suggested Spec Reads:**
- `.superwork/spec/guides/index.md` — shared rules

## Global Constraints

- Keep the API stable.

### Task 1: Update button

**Files:**

- Modify: `src/components/Button.tsx`

**Interfaces:**

- Consumes: `ButtonProps`
- Produces: `ButtonResult`

**Stop Conditions:**

- Stop if the interface is unclear.

- [ ] **Task Status:** pending

Run: `npm test`
Expected: PASS
""",
            )

            result = self.run_command(
                "python3",
                str(PREFLIGHT_PLAN_SCRIPT),
                "--root",
                str(root),
                "--plan",
                ".superwork/plans/demo.md",
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0, result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(
                payload["tasks"],
                [{"id": "Task 1", "title": "Update button", "status": "pending"}],
            )
            self.assertNotIn("authorizedUntil", payload)
            self.assertNotIn("executionAllowed", payload)

    def test_writing_plan_task_template_passes_preflight(self) -> None:
        skill_text = WRITING_PLANS_SKILL.read_text(encoding="utf-8")
        # 直接验证展示给模型的模板，避免写计划说明和预检规则再次独立演进。
        template_section = skill_text.split("## Exact Task Template", 1)[1]
        task_template = template_section.split("```markdown", 1)[1].split("```", 1)[0].strip()

        self.assertIn("\n**Files:**\n", task_template)
        self.assertIn("\n**Interfaces:**\n", task_template)
        self.assertIn("\n**Stop Conditions:**\n", task_template)
        self.assertNotIn("- **Files:**", task_template)
        self.assertNotIn("- **Interfaces:**", task_template)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            plan_text = f"""# Generated Implementation Plan

**Goal:** Validate the generated task contract

**Suggested Spec Reads:**

- `.superwork/spec/guides/index.md` - shared rules

**Architecture:** Keep the generated structure deterministic.

**Tech Stack:** Markdown and Python 3

## Global Constraints

- Keep task labels on standalone lines.

{task_template}
"""
            self.write_file(root / ".superwork" / "plans" / "generated.md", plan_text)

            result = self.run_command(
                "python3",
                str(PREFLIGHT_PLAN_SCRIPT),
                "--root",
                str(root),
                "--plan",
                ".superwork/plans/generated.md",
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertTrue(json.loads(result.stdout)["ok"])

    def test_preflight_plan_rejects_missing_stop_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.write_file(
                root / ".superwork" / "plans" / "bad.md",
                """# Bad Plan

**Goal:** Missing stop conditions

**Suggested Spec Reads:**
- `.superwork/spec/guides/index.md` — shared rules

## Global Constraints

- Keep behavior stable.

### Task 1: Invalid task

**Files:**

- Modify: `src/components/Button.tsx`

**Interfaces:**

- Consumes: `ButtonProps`
- Produces: `ButtonResult`

Expected: PASS
""",
            )

            result = self.run_command(
                "python3",
                str(PREFLIGHT_PLAN_SCRIPT),
                "--root",
                str(root),
                "--plan",
                ".superwork/plans/bad.md",
                "--format",
                "json",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing `**Stop Conditions:**`", result.stdout)

    def test_preflight_plan_rejects_missing_task_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.write_file(
                root / ".superwork" / "plans" / "missing-status.md",
                """# Missing Status Plan

**Goal:** Reject a plan that cannot be resumed

**Suggested Spec Reads:**
- `.superwork/spec/guides/index.md` - shared rules

## Global Constraints

- Keep behavior stable.

### Task 1: Update button

**Files:**

- Modify: `src/components/Button.tsx`

**Interfaces:**

- Consumes: `ButtonProps`
- Produces: `ButtonResult`

**Stop Conditions:**

- Stop if the interface is unclear.

Run: `npm test`
Expected: PASS
""",
            )

            result = self.run_command(
                "python3",
                str(PREFLIGHT_PLAN_SCRIPT),
                "--root",
                str(root),
                "--plan",
                ".superwork/plans/missing-status.md",
                "--format",
                "json",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing `Task Status` checkbox", result.stdout)


if __name__ == "__main__":
    unittest.main()
