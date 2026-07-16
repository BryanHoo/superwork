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

- [ ] **Step 1: Verify the behavior**

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
            self.assertNotIn("authorizedUntil", payload)
            self.assertNotIn("executionAllowed", payload)

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


if __name__ == "__main__":
    unittest.main()
