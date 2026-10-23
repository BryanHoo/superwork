import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills/superwork-start/scripts/parallel_task.py"


class ParallelTasksTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="superwork parallel ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.directory = self.root / ".superwork/parallel"
        self.directory.parent.mkdir()
        (self.directory.parent / "config.json").write_text('{"schemaVersion": 2}\n')
        (self.directory.parent / "parallel.md").write_text("# 项目自己的协作约定\n", encoding="utf-8")

    def command(self, action: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), action, "--root", str(self.root), *args],
            capture_output=True, text=True, timeout=20,
        )

    def success(self, action: str, *args: str) -> dict:
        result = self.command(action, *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def register(self, task: str = "feature-a", owner: str = "session-a") -> dict:
        return self.success(
            "register", "--id", task, "--owner", owner, "--goal", "增加筛选",
            "--files", "src/orders.ts", "--impact", "扩展 OrderQuery 可选字段",
        )

    def test_missing_directory_is_empty_and_read_only(self) -> None:
        payload = self.success("list")
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["tasks"], [])
        self.assertFalse(self.directory.exists())

    def test_registration_preserves_project_guide_and_other_tasks(self) -> None:
        self.register()
        self.register("feature-b", "session-b")
        payload = self.success("list")
        self.assertEqual([task["id"] for task in payload["tasks"]], ["feature-a", "feature-b"])
        self.assertEqual(payload["tasks"][0]["sharedImpact"], ["扩展 OrderQuery 可选字段"])
        self.assertEqual(
            (self.directory.parent / "parallel.md").read_text(encoding="utf-8"),
            "# 项目自己的协作约定\n",
        )

    def test_legacy_runtime_gets_only_missing_guide_and_local_ignore(self) -> None:
        guide = self.directory.parent / "parallel.md"
        guide.unlink()
        config = (self.directory.parent / "config.json").read_bytes()
        self.register()
        self.assertTrue(guide.is_file())
        self.assertEqual((self.directory.parent / "config.json").read_bytes(), config)
        self.assertFalse((self.directory.parent / "spec").exists())
        subprocess.run(["git", "init", str(self.root)], check=True, capture_output=True)
        ignored = subprocess.run(["git", "check-ignore", ".superwork/parallel/feature-a.json"],
                                 cwd=self.root, capture_output=True, text=True)
        self.assertEqual(ignored.returncode, 0, ignored.stderr)

    def test_independent_processes_register_without_losing_records(self) -> None:
        # 两个独立进程同时登记不同任务，公告板不能像共享数组一样丢失其中一个更新。
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda i: self.register(f"task-{i}", f"owner-{i}"), range(2)))
        self.assertEqual(len(results), 2)
        self.assertEqual(len(self.success("list")["tasks"]), 2)

    def test_duplicate_id_never_overwrites_an_existing_record(self) -> None:
        self.register()
        before = (self.directory / "feature-a.json").read_bytes()
        result = self.command(
            "register", "--id", "feature-a", "--owner", "session-b",
            "--goal", "其他任务", "--files", "src/other.ts",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.directory / "feature-a.json").read_bytes(), before)

    def test_update_and_finish_refuse_a_different_owner(self) -> None:
        self.register()
        for action in ("update", "finish"):
            with self.subTest(action=action):
                result = self.command(action, "--id", "feature-a", "--owner", "session-b")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.success("list")["tasks"][0]["owner"], "session-a")

    def test_pause_requires_reason_and_finish_only_removes_own_task(self) -> None:
        self.register()
        self.register("feature-b", "session-b")
        result = self.command("update", "--id", "feature-a", "--owner", "session-a", "--status", "paused")
        self.assertNotEqual(result.returncode, 0)
        self.success("update", "--id", "feature-a", "--owner", "session-a",
                     "--status", "paused", "--reason", "等待公共接口")
        tasks = self.success("list")["tasks"]
        self.assertEqual(tasks[0]["reason"], "等待公共接口")
        self.success("update", "--id", "feature-a", "--owner", "session-a",
                     "--status", "running", "--files", "src/orders.ts", "src/query.ts")
        tasks = self.success("list")["tasks"]
        self.assertEqual(tasks[0]["writePaths"], ["src/orders.ts", "src/query.ts"])
        self.assertIsNone(tasks[0]["reason"])
        self.success("finish", "--id", "feature-a", "--owner", "session-a")
        self.assertEqual([task["id"] for task in self.success("list")["tasks"]], ["feature-b"])

    def test_invalid_record_is_reported_alongside_valid_tasks(self) -> None:
        self.register()
        (self.directory / "broken.json").write_text("{broken", encoding="utf-8")
        result = self.command("list")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["tasks"][0]["id"], "feature-a")
        self.assertEqual(payload["errors"][0]["path"], ".superwork/parallel/broken.json")

    @unittest.skipIf(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
                     "requires normal POSIX directory permissions")
    def test_unreadable_registry_is_reported_instead_of_empty(self) -> None:
        self.register()
        self.directory.chmod(0)
        try:
            result = self.command("list")
        finally:
            self.directory.chmod(0o700)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["errors"][0]["path"], ".superwork/parallel")

    def test_paths_and_record_ids_cannot_escape_the_project(self) -> None:
        for task, path in (("../escaped", "src/a.ts"), ("safe", "../escaped.ts"),
                           ("safe", str(self.root.parent / "escaped.ts")), ("safe", "src/*.ts")):
            with self.subTest(task=task, path=path):
                result = self.command("register", "--id", task, "--owner", "session-a",
                                      "--goal", "测试边界", "--files", path)
                self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.success("list")["tasks"], [])

    def test_symlink_record_is_not_followed_or_deleted(self) -> None:
        self.register()
        outside = self.root / "outside.json"
        outside.write_bytes((self.directory / "feature-a.json").read_bytes())
        (self.directory / "feature-a.json").unlink()
        (self.directory / "feature-a.json").symlink_to(outside)
        result = self.command("finish", "--id", "feature-a", "--owner", "session-a")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(outside.exists())
        self.assertTrue((self.directory / "feature-a.json").is_symlink())

    def test_registration_does_not_initialize_a_missing_runtime(self) -> None:
        (self.directory.parent / "config.json").unlink()
        result = self.command("register", "--id", "feature-a", "--owner", "session-a",
                              "--goal", "任务", "--files", "src/a.ts")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.directory.exists())


if __name__ == "__main__":
    unittest.main()
