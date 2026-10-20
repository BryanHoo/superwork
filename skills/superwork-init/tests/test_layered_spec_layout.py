from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from _support import (
    CHECK_SPECS_SCRIPT,
    GET_CONTEXT_SCRIPT,
    PLANNING_SKILL,
    PREFLIGHT_PLAN_SCRIPT,
    UPDATE_SPEC_SCRIPT,
    SuperworkFixtureTestCase,
)


class LayeredSpecLayoutTest(SuperworkFixtureTestCase):

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
            self.assertIn("get_context.py", guides)
            self.assertIn("candidateReads", guides)

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
            candidates = {item["path"]: item for item in payload["spec"]["candidateReads"]}
            self.assertEqual(candidates[".superwork/spec/guides/index.md"]["priority"], "recommended")
            self.assertEqual(candidates[".superwork/spec/frontend/index.md"]["priority"], "recommended")
            self.assertEqual(candidates[".superwork/spec/backend/index.md"]["priority"], "recommended")
            self.assertTrue(all(item["reason"] for item in candidates.values()))
            self.assertTrue(all(item["size"] > 0 for item in candidates.values()))
            self.assertNotIn("recommendedReads", payload["spec"])

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
            candidates = {item["path"]: item for item in payload["spec"]["candidateReads"]}
            self.assertEqual(candidates[".superwork/spec/frontend/index.md"]["priority"], "required")
            self.assertEqual(candidates[".superwork/spec/guides/index.md"]["priority"], "recommended")
            self.assertNotIn(".superwork/spec/backend/index.md", candidates)

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
**Scope:** Update button validation only
**Acceptance:** The focused button test passes

### Task 1: Update button

**Files:**

- Modify: `src/components/Button.tsx`

**Behavior:**

- Reject an empty button label.

**Proof:** `npm test`

**Stop Conditions:**

- Stop if the interface is unclear.

- [ ] **Task Status:** pending

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
                [
                    {
                        "id": "Task 1",
                        "title": "Update button",
                        "status": "pending",
                        "proof": "`npm test`",
                    }
                ],
            )
            self.assertNotIn("authorizedUntil", payload)
            self.assertNotIn("executionAllowed", payload)

    def test_planning_task_template_passes_preflight(self) -> None:
        skill_text = PLANNING_SKILL.read_text(encoding="utf-8")
        # 直接验证展示给模型的模板，避免写计划说明和预检规则再次独立演进。
        template_section = skill_text.split("## Exact Saved Plan Template", 1)[1]
        plan_template = template_section.split("```markdown", 1)[1].split("```", 1)[0].strip()

        self.assertIn("**Goal:**", plan_template)
        self.assertIn("**Scope:**", plan_template)
        self.assertIn("**Acceptance:**", plan_template)
        self.assertIn("\n**Files:**\n", plan_template)
        self.assertIn("\n**Behavior:**\n", plan_template)
        self.assertIn("\n**Proof:**", plan_template)
        self.assertIn("\n**Stop Conditions:**\n", plan_template)
        self.assertNotIn("Suggested Spec Reads", plan_template)
        self.assertNotIn("Global Constraints", plan_template)
        self.assertNotIn("**Interfaces:**", plan_template)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.write_file(root / ".superwork" / "plans" / "generated.md", plan_template)

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
**Scope:** Update one button
**Acceptance:** The focused test passes

### Task 1: Invalid task

**Files:**

- Modify: `src/components/Button.tsx`

**Behavior:**

- Reject an empty label.

**Proof:** `npm test`

- [ ] **Task Status:** pending
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
**Scope:** Update one button
**Acceptance:** The focused test passes

### Task 1: Update button

**Files:**

- Modify: `src/components/Button.tsx`

**Behavior:**

- Reject an empty label.

**Proof:** `npm test`

**Stop Conditions:**

- Stop if the interface is unclear.

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
