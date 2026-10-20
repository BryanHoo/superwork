from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from _support import SuperworkFixtureTestCase


class RuntimeBootstrapTest(SuperworkFixtureTestCase):
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

    def test_bootstrap_creates_config_v3_without_workflow_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)

            payload = self.bootstrap_spec(root)

            config_path = root / ".superwork" / "config.json"
            self.assertTrue(config_path.exists())
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["schemaVersion"], 3)
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

    def test_bootstrap_replaces_previous_runtime_with_current_generated_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_single_repo_fixture(root)
            self.write_file(
                root / ".superwork" / "config.json",
                json.dumps({"schemaVersion": 2, "packageManager": "none"}),
            )
            self.write_file(
                root / ".superwork" / "spec" / "guides" / "index.md",
                "# Thinking Guides\n\n- Read every spec before development.\n",
            )

            payload = self.bootstrap_spec(root)

            config = json.loads((root / ".superwork" / "config.json").read_text(encoding="utf-8"))
            guides = (root / ".superwork" / "spec" / "guides" / "index.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(config["schemaVersion"], 3)
            self.assertIn("candidateReads", guides)
            self.assertIn(".superwork/config.json", payload["created"])
            self.assertIn(".superwork/spec/guides/index.md", payload["created"])

    def test_bootstrap_generated_shared_index_uses_just_in_time_reads(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            self.bootstrap_spec(root)

            shared_index = (root / ".superwork" / "spec" / "shared" / "index.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Read only", shared_index)
            self.assertNotIn("Read both guides", shared_index)

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


if __name__ == "__main__":
    unittest.main()
