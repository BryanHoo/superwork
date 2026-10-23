import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = REPO_ROOT / "skills/superwork-executing-plans/scripts/preflight_plan.py"


class PlanGuardrailsTest(unittest.TestCase):
    def preflight(self, *, drift=False, missing_spec=False, missing_constraints=False) -> dict:
        # 使用实际展示给模型的模板，确认优化读取和交接后仍能拦截跨任务契约错误。
        skill = (REPO_ROOT / "skills/superwork-writing-plans/SKILL.md").read_text()
        template = skill.split("## Exact Task Template", 1)[1].split("```markdown", 1)[1].split("```", 1)[0]
        first = template.replace("UpdatedContract", "convert(value: str): int")
        second = template.replace("Task 1:", "Task 2:").replace(
            "ExistingContract", "convert(value: bytes): int" if drift else "convert(value: str): int"
        )
        constraints = "" if missing_constraints else "## Global Constraints\n\n- Preserve the declared contracts.\n"
        plan = (
            "# Contract check\n\n**Goal:** Preserve interfaces\n\n"
            "**Suggested Spec Reads:**\n\n- `.superwork/spec/guides/index.md` - project rules\n\n"
            + constraints + first + second
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            if not missing_spec:
                index = root / ".superwork/spec/guides/index.md"
                index.parent.mkdir(parents=True)
                index.write_text("# Project rules\n")
            (root / "plan.md").write_text(plan)
            result = subprocess.run(
                [sys.executable, str(PREFLIGHT), "--root", str(root), "--plan", "plan.md", "--format", "json"],
                text=True, capture_output=True, check=False,
            )
            self.assertIn(result.returncode, (0, 1), result.stderr)
            return json.loads(result.stdout)

    def test_matching_interfaces_pass_but_signature_drift_fails(self) -> None:
        self.assertTrue(self.preflight()["ok"])
        rejected = self.preflight(drift=True)
        self.assertFalse(rejected["ok"])
        self.assertTrue(any("interface drift" in item["message"] for item in rejected["issues"]))

    def test_missing_spec_reference_is_rejected(self) -> None:
        rejected = self.preflight(missing_spec=True)
        self.assertFalse(rejected["ok"])
        self.assertTrue(any("spec path does not exist" in item["message"] for item in rejected["issues"]))

    def test_missing_global_constraints_are_rejected(self) -> None:
        rejected = self.preflight(missing_constraints=True)
        self.assertFalse(rejected["ok"])
        self.assertTrue(any("Global Constraints" in item["message"] for item in rejected["issues"]))


if __name__ == "__main__":
    unittest.main()
