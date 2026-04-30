import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/bryanhu/Develop/superwork")
BOOTSTRAP_SCRIPT = REPO_ROOT / "skills" / "superwork-init" / "scripts" / "bootstrap_superwork.py"
GET_CONTEXT_SCRIPT = REPO_ROOT / "skills" / "superwork-start" / "scripts" / "get_context.py"
CHECK_SPECS_SCRIPT = REPO_ROOT / "skills" / "superwork-check" / "scripts" / "check_specs.py"
UPDATE_SPEC_SCRIPT = REPO_ROOT / "skills" / "superwork-update-spec" / "scripts" / "update_spec.py"


class LayeredSpecLayoutTest(unittest.TestCase):
    def run_command(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args),
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
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

    def bootstrap_spec(self, root: Path) -> None:
        result = self.run_command(
            "python3",
            str(BOOTSTRAP_SCRIPT),
            "--root",
            str(root),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bootstrap_creates_layered_layout_for_single_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)

            result = self.run_command(
                "python3",
                str(BOOTSTRAP_SCRIPT),
                "--root",
                str(root),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / ".superwork" / "spec" / "frontend" / "index.md").exists())
            self.assertTrue(
                (root / ".superwork" / "spec" / "frontend" / "component-guidelines.md").exists()
            )
            self.assertTrue((root / ".superwork" / "spec" / "backend" / "index.md").exists())
            self.assertFalse((root / ".superwork" / "spec" / "root").exists())

    def test_workflow_does_not_reference_project_script_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")

            # 回归约束：初始化产物不能暗示在目标项目生成 scripts/*.py。
            self.assertNotIn("scripts/get_context.py", workflow_content)
            self.assertNotIn("scripts/check_specs.py", workflow_content)
            self.assertNotIn("scripts/update_spec.py", workflow_content)

    def test_workflow_and_guides_reference_superwork_code_simplifier(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")
            guides_content = (root / ".superwork" / "spec" / "guides" / "index.md").read_text(
                encoding="utf-8"
            )

            # 新增工作流入口后，运行时文档必须明确暴露该命令。
            self.assertIn("superwork-code-simplifier", workflow_content)
            self.assertIn("superwork-code-simplifier", guides_content)

    def test_workflow_and_guides_require_explicit_simplifier_skip_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")
            guides_content = (root / ".superwork" / "spec" / "guides" / "index.md").read_text(
                encoding="utf-8"
            )

            # 检查前不能静默跳过 simplifier；未执行时必须说明原因。
            self.assertIn("before `superwork-check`", workflow_content)
            self.assertIn("state why", workflow_content)
            self.assertIn("before final completion", guides_content)
            self.assertIn("state why", guides_content)

    def test_workflow_keeps_prd_and_plan_docs_under_superwork(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")

            # 设计稿与计划文档都必须统一留在 `.superwork/`，避免与 `.superwork/spec/` 混淆。
            self.assertIn(".superwork/prd/*.md", workflow_content)
            self.assertIn(".superwork/plans/*.md", workflow_content)
            self.assertNotIn(".superwork/specs/*.md", workflow_content)
            self.assertNotIn("docs/superwork/specs", workflow_content)
            self.assertNotIn("docs/superwork/plans", workflow_content)

    def test_workflow_and_guides_require_saved_plan_before_red(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")
            guides_content = (root / ".superwork" / "spec" / "guides" / "index.md").read_text(
                encoding="utf-8"
            )

            # direct feature 路径也必须先落盘计划，不能直接开始 RED。
            self.assertIn("before any RED or implementation work starts", workflow_content)
            self.assertIn("before the first RED test", workflow_content)
            self.assertIn("before the first RED test", guides_content)

    def test_superwork_skills_do_not_reference_docs_superwork_paths(self) -> None:
        skill_paths = [
            REPO_ROOT / "skills" / "superwork-brainstorming" / "SKILL.md",
            REPO_ROOT / "skills" / "superwork-tdd" / "SKILL.md",
            REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md",
        ]

        for skill_path in skill_paths:
            content = skill_path.read_text(encoding="utf-8")
            # 关键工作流技能应统一使用 `.superwork/` 路径约定。
            self.assertNotIn("docs/superwork", content, skill_path.as_posix())

    def test_get_context_reads_layered_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            result = self.run_command(
                "python3",
                str(GET_CONTEXT_SCRIPT),
                "--root",
                str(root),
                "--format",
                "json",
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
                "python3",
                str(GET_CONTEXT_SCRIPT),
                "--root",
                str(root),
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            recommended_reads = set(payload["spec"]["recommendedReads"])
            self.assertIn(".superwork/spec/guides/index.md", recommended_reads)
            self.assertIn(".superwork/spec/frontend/index.md", recommended_reads)
            self.assertNotIn(".superwork/spec/backend/index.md", recommended_reads)

    def test_check_specs_matches_layered_docs_for_changed_files(self) -> None:
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
                "python3",
                str(CHECK_SPECS_SCRIPT),
                "--root",
                str(root),
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
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
                "python3",
                str(UPDATE_SPEC_SCRIPT),
                "--root",
                str(root),
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            targets = {item["path"]: item["action"] for item in payload["targets"]}
            self.assertEqual(targets.get(".superwork/spec/frontend/component-guidelines.md"), "update")

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
                "python3",
                str(UPDATE_SPEC_SCRIPT),
                "--root",
                str(root),
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "no-update")
            self.assertEqual(payload["targets"], [])

    def test_superwork_check_requires_simplifier_decision_before_verification(self) -> None:
        content = (REPO_ROOT / "skills" / "superwork-check" / "SKILL.md").read_text(encoding="utf-8")

        # `superwork-check` 本身也必须要求显式执行或解释 simplifier 的跳过原因。
        self.assertIn("`superwork-code-simplifier`", content)
        self.assertIn("state why", content)
        self.assertIn("before verification", content)


if __name__ == "__main__":
    unittest.main()
