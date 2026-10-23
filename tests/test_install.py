import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "scripts/install.sh"
CONTRACT = REPO_ROOT / "skills/superwork-start/references/workflow-contract.json"


class InstallTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="superwork-install-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.prefix = self.root / "user with spaces"
        self.prefix.mkdir()
        self.archive = self.root / "superwork.tar.gz"
        self.expected = {"_shared", *json.loads(CONTRACT.read_text())["skills"]}
        # 使用与 GitHub 源码包相同的顶层结构，通过真实 curl/tar 测试完整下载解包链路。
        with tarfile.open(self.archive, "w:gz") as archive:
            archive.add(REPO_ROOT / "skills", arcname="superwork-main/skills", filter=self.filter_archive)

    @staticmethod
    def filter_archive(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
        if "__pycache__" in Path(info.name).parts or info.name.endswith(".pyc"):
            return None
        return info

    def install(self, *args: str, prefix: Path | None = None, environment: dict | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["SUPERWORK_ARCHIVE_URL"] = self.archive.as_uri()
        if environment:
            env.update(environment)
        # 从标准输入执行脚本，模拟 README 中 curl | bash；不依赖安装器旁边存在源码。
        return subprocess.run(
            ["/bin/bash", "-s", "--", "--prefix", str(prefix or self.prefix), *args],
            input=INSTALLER.read_text(), cwd=self.root, env=env,
            capture_output=True, text=True, check=False,
        )

    def assert_installed(self, agent_dir: str, prefix: Path | None = None) -> Path:
        target = (prefix or self.prefix) / agent_dir / "skills"
        self.assertFalse(target.is_symlink())
        self.assertEqual({p.name for p in target.iterdir()} - {"other-skill"}, self.expected)
        for name in self.expected:
            self.assertTrue((target / name).is_dir(), name)
            self.assertFalse((target / name).is_symlink(), name)
        return target

    def check_runtime(self, installed: Path) -> None:
        context = subprocess.run(
            [sys.executable, str(installed / "superwork-start/scripts/get_context.py"),
             "--root", str(self.prefix), "--format", "json"],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(context.returncode, 0, context.stderr)
        self.assertEqual(json.loads(context.stdout)["runtime"]["status"], "missing")
        preview = subprocess.run(
            [sys.executable, str(installed / "superwork-init/scripts/bootstrap_superwork.py"),
             "--root", str(self.prefix), "--dry-run"],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn(".superwork/config.json", preview.stdout)
        self.assertFalse((self.prefix / ".superwork").exists())
        # 从真实分发目录初始化并登记，覆盖新共享模块、模板与 CLI 的独立运行依赖。
        project = Path(tempfile.mkdtemp(prefix="parallel-project-", dir=self.root))
        bootstrap = subprocess.run(
            [sys.executable, str(installed / "superwork-init/scripts/bootstrap_superwork.py"),
             "--root", str(project)], capture_output=True, text=True,
        )
        self.assertEqual(bootstrap.returncode, 0, bootstrap.stderr)
        cli = installed / "superwork-start/scripts/parallel_task.py"
        register = subprocess.run(
            [sys.executable, str(cli), "register", "--root", str(project), "--id", "installed-task",
             "--owner", "test-session", "--goal", "测试独立安装", "--files", "src/new.py"],
            capture_output=True, text=True,
        )
        self.assertEqual(register.returncode, 0, register.stdout + register.stderr)
        self.assertEqual(json.loads(register.stdout)["parallel"]["tasks"][0]["id"], "installed-task")
        finish = subprocess.run(
            [sys.executable, str(cli), "finish", "--root", str(project), "--id", "installed-task",
             "--owner", "test-session"], capture_output=True, text=True,
        )
        self.assertEqual(finish.returncode, 0, finish.stdout + finish.stderr)
        self.assertFalse((project / ".superwork/parallel/installed-task.json").exists())

    def test_piped_install_defaults_to_agents_and_is_self_contained(self) -> None:
        other = self.prefix / ".agents/skills/other-skill"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text("用户的其他技能", encoding="utf-8")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = self.assert_installed(".agents")
        self.assertFalse((self.prefix / ".claude").exists())
        self.assertEqual((other / "SKILL.md").read_text(), "用户的其他技能")
        # 删除下载源后，安装结果仍须能独立导入共享模块并读取模板。
        self.archive.unlink()
        self.check_runtime(installed)

    def test_claude_shares_regular_files_using_hard_links(self) -> None:
        result = self.install("--claude")
        self.assertEqual(result.returncode, 0, result.stderr)
        canonical = self.assert_installed(".agents")
        claude = self.assert_installed(".claude")
        for source in canonical.rglob("*"):
            if source.is_file():
                target = claude / source.relative_to(canonical)
                self.assertFalse(target.is_symlink())
                self.assertTrue(source.samefile(target), str(target))
        self.check_runtime(canonical)
        self.check_runtime(claude)
        marker = canonical / "superwork-start/SKILL.md"
        identity = marker.stat().st_ino
        # 运行工作流产生的 __pycache__ 不应阻止重复安装或破坏现有硬链接。
        repeated = self.install("--claude")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual(marker.stat().st_ino, identity)
        self.assertTrue(marker.samefile(claude / "superwork-start/SKILL.md"))

    def test_conflicts_are_reported_before_installing_any_entry(self) -> None:
        cases = ((".agents", "superwork-start", "file"),
                 (".agents", "_shared", "directory"),
                 (".claude", "_shared", "broken-link"))
        for agent_dir, name, kind in cases:
            with self.subTest(agent_dir=agent_dir, kind=kind):
                prefix = self.root / kind
                target = prefix / agent_dir / "skills"
                target.mkdir(parents=True)
                conflict = target / name
                if kind == "file":
                    conflict.write_text("原有内容", encoding="utf-8")
                elif kind == "directory":
                    conflict.mkdir()
                    (conflict / "marker").write_text("原有内容", encoding="utf-8")
                else:
                    conflict.symlink_to(self.root / "missing")
                result = self.install("--claude", prefix=prefix)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(str(conflict), result.stderr)
                self.assertEqual(list(target.iterdir()), [conflict])
                other_agent = ".claude" if agent_dir == ".agents" else ".agents"
                self.assertFalse((prefix / other_agent).exists())
                if kind == "file":
                    self.assertEqual(conflict.read_text(), "原有内容")
                elif kind == "directory":
                    self.assertEqual(list(conflict.iterdir()), [conflict / "marker"])
                else:
                    self.assertTrue(conflict.is_symlink())

    def test_download_failure_and_incomplete_archive_do_not_install(self) -> None:
        failed = self.install(environment={"SUPERWORK_ARCHIVE_URL": (self.root / "missing").as_uri()})
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(list(self.prefix.iterdir()), [])
        with tarfile.open(self.archive, "w:gz") as archive:
            archive.add(REPO_ROOT / "skills/superwork-start", arcname="superwork-main/skills/superwork-start")
        incomplete = self.install()
        self.assertNotEqual(incomplete.returncode, 0)
        self.assertIn("_shared", incomplete.stderr)
        self.assertEqual(list(self.prefix.iterdir()), [])

    def test_installer_runs_without_python_or_git_on_path(self) -> None:
        self.assertTrue(os.access(INSTALLER, os.X_OK))
        commands = self.root / "bin"
        commands.mkdir()
        # 只提供下载、复制与硬链接所需的系统命令，验证安装器无需 Python 或 Git。
        for name, source in (("bash", "/bin/bash"), ("dirname", "/usr/bin/dirname"),
                             ("cat", "/bin/cat"), ("mkdir", "/bin/mkdir"), ("ln", "/bin/ln"),
                             ("cp", "/bin/cp"), ("rm", "/bin/rm"), ("curl", "/usr/bin/curl"),
                             ("tar", "/usr/bin/tar"), ("mktemp", "/usr/bin/mktemp"),
                             ("diff", "/usr/bin/diff"), ("find", "/usr/bin/find")):
            (commands / name).symlink_to(source)
        result = self.install("--claude", environment={"PATH": str(commands)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_installed(".agents")
        self.assert_installed(".claude")

    def test_invalid_arguments_are_rejected_without_installing(self) -> None:
        for args in (("--unknown",), ("--prefix",), ("--prefix", str(self.root / "missing"))):
            with self.subTest(args=args):
                result = self.install(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
        self.assertEqual(list(self.prefix.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
