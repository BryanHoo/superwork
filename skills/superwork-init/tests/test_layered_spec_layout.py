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

            # simplifier 决策归 `superwork-check`，且未执行时必须说明原因。
            self.assertIn("Route finished implementation and bugfix work to `superwork-check`", workflow_content)
            self.assertIn(
                "Require `superwork-check` to own the explicit `superwork-code-simplifier` decision",
                workflow_content,
            )
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

    def test_workflow_distinguishes_design_docs_specs_and_plans(self) -> None:
        workflow_content = (
            REPO_ROOT / "skills" / "superwork-init" / "templates" / "workflow.md.tmpl"
        ).read_text(encoding="utf-8")
        brainstorming_content = (
            REPO_ROOT / "skills" / "superwork-brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        writing_plans_content = (
            REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Design docs: `.superwork/prd/*.md`", workflow_content)
        self.assertIn("Durable rules and contracts: `.superwork/spec/**/*.md`", workflow_content)
        self.assertIn("Plan artifacts: `.superwork/plans/*.md`", workflow_content)
        self.assertIn("stores heavy-task design docs", brainstorming_content)
        self.assertIn("stores durable project rules", brainstorming_content)
        self.assertIn("stores executable implementation plans", writing_plans_content)

    def test_workflow_and_guides_define_task_sizing_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")
            guides_content = (root / ".superwork" / "spec" / "guides" / "index.md").read_text(
                encoding="utf-8"
            )

            # 非 bug 任务必须按轻 / 中 / 重分级，并走对应链路。
            self.assertIn("light, medium, or heavy", workflow_content)
            self.assertIn("Route light tasks to `superwork-tdd`", workflow_content)
            self.assertIn("Route medium tasks to `superwork-writing-plans`", workflow_content)
            self.assertIn("Route heavy tasks by default to `superwork-brainstorming`", workflow_content)
            self.assertIn("Users may still invoke `superwork-brainstorming` manually", workflow_content)
            self.assertIn("Choose light / medium / heavy", guides_content)
            self.assertIn("Choose `superwork-tdd` for light work", guides_content)
            self.assertIn(
                "Choose `superwork-writing-plans` then `superwork-executing-plans` for medium work",
                guides_content,
            )
            self.assertIn(
                "Choose `superwork-brainstorming` then `superwork-writing-plans` then `superwork-executing-plans` as the default heavy-work path",
                guides_content,
            )
            self.assertIn("Allow manual `superwork-brainstorming` use", guides_content)

    def test_workflow_requires_route_announcement_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")

            # `superwork-start` 路由后必须显式说出路由和一句理由，不能静默切换。
            self.assertIn("must explicitly state the chosen route", workflow_content)
            self.assertIn("one short reason", workflow_content)

    def test_workflow_and_execution_do_not_reference_worktrees(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)

            workflow_content = (root / ".superwork" / "workflow.md").read_text(encoding="utf-8")
            executing_content = (
                REPO_ROOT / "skills" / "superwork-executing-plans" / "SKILL.md"
            ).read_text(encoding="utf-8")
            init_content = (REPO_ROOT / "skills" / "superwork-init" / "SKILL.md").read_text(
                encoding="utf-8"
            )

            # 所有任务都应直接在当前分支开发，不再要求或提及 worktree。
            self.assertNotIn("superwork-using-git-worktrees", workflow_content)
            self.assertNotIn("worktree", workflow_content)
            self.assertNotIn("superwork-using-git-worktrees", executing_content)
            self.assertNotIn("worktree", executing_content)
            self.assertNotIn("superwork-using-git-worktrees", init_content)
            self.assertIn("current branch", workflow_content)
            self.assertIn("current branch", executing_content)
            self.assertNotIn("main/master", executing_content)

    def test_light_task_path_uses_inline_tdd_without_saved_plan(self) -> None:
        workflow_content = (
            REPO_ROOT / "skills" / "superwork-init" / "templates" / "workflow.md.tmpl"
        ).read_text(encoding="utf-8")
        tdd_content = (REPO_ROOT / "skills" / "superwork-tdd" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        # 轻量任务必须走内联 TDD，而不是再强制落盘计划。
        self.assertIn("inline TDD plan", workflow_content)
        self.assertIn("do not require `.superwork/plans/*.md`", workflow_content)
        self.assertIn("without creating a saved plan document", tdd_content)
        self.assertIn("Do not create `.superwork/plans/*.md`", tdd_content)

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

    def test_update_spec_falls_back_to_existing_index_when_leaf_doc_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.init_git_repo(root)

            missing_guide = root / ".superwork" / "spec" / "frontend" / "component-guidelines.md"
            missing_guide.unlink()
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
            self.assertEqual(payload["decision"], "update")
            targets = {item["path"]: item["action"] for item in payload["targets"]}
            self.assertEqual(targets.get(".superwork/spec/frontend/index.md"), "update")
            self.assertNotIn(".superwork/spec/frontend/component-guidelines.md", targets)

    def test_update_spec_falls_back_to_existing_layer_doc_when_index_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.bootstrap_spec(root)
            self.init_git_repo(root)

            index_path = root / ".superwork" / "spec" / "frontend" / "index.md"
            guide_path = root / ".superwork" / "spec" / "frontend" / "component-guidelines.md"
            index_path.unlink()
            guide_path.unlink()
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
            self.assertEqual(payload["decision"], "update")
            self.assertEqual(len(payload["targets"]), 1)
            self.assertEqual(payload["targets"][0]["path"], ".superwork/spec/frontend/directory-structure.md")
            self.assertEqual(payload["targets"][0]["action"], "update")

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

        # `superwork-check` 本身必须拥有 simplifier 决策权，并要求显式执行或解释跳过原因。
        self.assertIn("`superwork-code-simplifier`", content)
        self.assertIn("owns the `superwork-code-simplifier` decision", content)
        self.assertIn("state why", content)
        self.assertIn("before verification", content)

    def test_medium_or_large_changes_must_run_simplifier(self) -> None:
        workflow_content = (
            REPO_ROOT / "skills" / "superwork-init" / "templates" / "workflow.md.tmpl"
        ).read_text(encoding="utf-8")
        guides_content = (
            REPO_ROOT / "skills" / "superwork-init" / "templates" / "guides-index.md.tmpl"
        ).read_text(encoding="utf-8")
        simplifier_content = (
            REPO_ROOT / "skills" / "superwork-code-simplifier" / "SKILL.md"
        ).read_text(encoding="utf-8")

        # 中大型改动不能只做口头跳过，规则源头和运行时模板都必须写死“必须执行”。
        self.assertIn("medium or large", workflow_content)
        self.assertIn("must run `superwork-code-simplifier`", workflow_content)
        self.assertIn("medium or large", guides_content)
        self.assertIn("must run `superwork-code-simplifier`", guides_content)
        self.assertIn("medium or large", simplifier_content)
        self.assertIn("must run this skill", simplifier_content)

    def test_executing_plans_completes_through_superwork_completion_stack(self) -> None:
        content = (
            REPO_ROOT / "skills" / "superwork-executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        # 执行计划完成后必须回到 superwork 的收尾链路，不能跳去外部 finishing skill。
        self.assertNotIn("finishing-a-development-branch", content)
        self.assertIn("superwork-code-simplifier", content)
        self.assertIn("Let `superwork-check` decide whether `superwork-code-simplifier` must run", content)
        self.assertIn("superwork-check", content)
        self.assertIn("superwork-update-spec", content)
        self.assertNotIn("Finish the `superwork-code-simplifier` stage before entering final verification", content)

    def test_heavy_path_orders_brainstorming_then_planning_then_execution(self) -> None:
        brainstorming_content = (
            REPO_ROOT / "skills" / "superwork-brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        writing_plans_content = (
            REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "`superwork-writing-plans` is the next step, and `superwork-executing-plans` starts only after that saved plan exists",
            brainstorming_content,
        )
        self.assertIn(
            "`superwork-brainstorming` -> design doc in `.superwork/prd/*.md` -> `superwork-writing-plans` -> plan in `.superwork/plans/*.md` -> `superwork-executing-plans`",
            writing_plans_content,
        )

    def test_writing_plans_commit_example_matches_global_commit_rule(self) -> None:
        content = (REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn('git commit -m "feat(example): 添加具体功能"', content)
        self.assertIn("Chinese subject", content)
        self.assertNotIn('git commit -m "feat: add specific feature"', content)


if __name__ == "__main__":
    unittest.main()
