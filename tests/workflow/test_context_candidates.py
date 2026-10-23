import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills/superwork-start/scripts/get_context.py"


class ContextCandidatesTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write(".superwork/config.json", json.dumps({"schemaVersion": 2}))
        self.write(".superwork/spec/guides/index.md", "# 全局约束\n")
        for layer in ("frontend", "backend", "shared"):
            self.write(f".superwork/spec/{layer}/index.md", f"# {layer}\n")
        self.git("init")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "fixture")

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def context(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--format", "json", *args],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def priorities(self, payload: dict) -> dict:
        candidates = payload["spec"]["candidateReads"]
        self.assertEqual(len(candidates), len({item["path"] for item in candidates}))
        for item in candidates:
            self.assertTrue(item["reason"])
            self.assertEqual(item["size"], (self.root / item["path"]).stat().st_size)
        return {item["path"]: item["priority"] for item in candidates}

    def test_clean_repo_keeps_global_and_shared_rules_required(self) -> None:
        payload = self.context()
        priorities = self.priorities(payload)
        self.assertEqual(payload["runtime"]["status"], "ready")
        self.assertEqual(priorities[".superwork/spec/guides/index.md"], "required")
        self.assertEqual(priorities[".superwork/spec/shared/index.md"], "required")
        self.assertEqual(priorities[".superwork/spec/frontend/index.md"], "recommended")
        self.assertEqual(priorities[".superwork/spec/backend/index.md"], "recommended")
        self.assertEqual(set(payload["spec"]["recommendedReads"]), set(priorities))

    def test_changed_file_requires_matching_and_shared_rules(self) -> None:
        self.write("src/components/Button.tsx", "export const Button = true;\n")
        payload = self.context()
        priorities = self.priorities(payload)
        self.assertEqual(payload["spec"]["readScope"], "changed-files")
        self.assertEqual(priorities[".superwork/spec/frontend/index.md"], "required")
        self.assertEqual(priorities[".superwork/spec/shared/index.md"], "required")
        self.assertEqual(priorities[".superwork/spec/backend/index.md"], "recommended")

    def test_target_files_scope_before_edit_and_ignore_unrelated_dirty_files(self) -> None:
        self.write("server/unrelated.py", "pass\n")
        payload = self.context("--files", "src/components/New.tsx")
        priorities = self.priorities(payload)
        self.assertEqual(payload["spec"]["readScope"], "target-files")
        self.assertEqual(payload["spec"]["scopeFiles"], ["src/components/New.tsx"])
        self.assertIn("server/unrelated.py", payload["spec"]["changedFiles"])
        self.assertEqual(priorities[".superwork/spec/frontend/index.md"], "required")
        self.assertEqual(priorities[".superwork/spec/backend/index.md"], "recommended")

    def test_unmatched_scope_falls_back_without_skipping_rules(self) -> None:
        (self.root / ".superwork/spec/backend/index.md").unlink()
        payload = self.context("--files", "server/worker.py")
        self.assertEqual(payload["spec"]["readScope"], "full-fallback")
        self.assertEqual(set(self.priorities(payload).values()), {"required"})

    def test_monorepo_requires_only_matching_package_and_its_shared_rules(self) -> None:
        # 两个包使用相同 layer，防止按需读取意外扩大到其他包或漏掉本包共享约束。
        for layer in ("frontend", "backend", "shared"):
            (self.root / f".superwork/spec/{layer}/index.md").unlink()
            (self.root / f".superwork/spec/{layer}").rmdir()
        for package in ("shop", "admin"):
            for layer in ("frontend", "shared"):
                self.write(f".superwork/spec/{package}/{layer}/index.md", "# 包级规则\n")
        payload = self.context("--files", "packages/shop/components/Button.tsx")
        priorities = self.priorities(payload)
        self.assertEqual(priorities[".superwork/spec/shop/frontend/index.md"], "required")
        self.assertEqual(priorities[".superwork/spec/shop/shared/index.md"], "required")
        self.assertEqual(priorities[".superwork/spec/admin/frontend/index.md"], "recommended")
        self.assertEqual(priorities[".superwork/spec/admin/shared/index.md"], "recommended")

    def test_missing_runtime_remains_read_only(self) -> None:
        config = self.root / ".superwork/config.json"
        config.unlink()
        payload = self.context()
        self.assertEqual(payload["runtime"]["status"], "missing")
        self.priorities(payload)
        self.assertFalse(config.exists())

    def test_target_outside_repository_is_rejected(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--files", "../outside.py"],
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
