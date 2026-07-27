from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.evals.run_skill_evals import (
    build_codex_command,
    create_fixture,
    evaluate_case,
    parse_jsonl_output,
    validate_cases,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = REPO_ROOT / "tests" / "evals" / "trigger_train.json"
VALIDATION_PATH = REPO_ROOT / "tests" / "evals" / "trigger_validation.json"


class SkillEvalRunnerTest(unittest.TestCase):
    def test_datasets_are_balanced_and_disjoint(self) -> None:
        train = json.loads(TRAIN_PATH.read_text(encoding="utf-8"))
        validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))

        validate_cases(train)
        validate_cases(validation)
        self.assertEqual(len(train), 12)
        self.assertEqual(len(validation), 8)
        self.assertEqual(sum(case["should_trigger"] for case in train), 6)
        self.assertEqual(sum(case["should_trigger"] for case in validation), 4)
        self.assertFalse({case["id"] for case in train} & {case["id"] for case in validation})

    def test_jsonl_parser_extracts_route_and_final_message(self) -> None:
        output = "\n".join(
            [
                json.dumps({"type": "item.completed", "item": {"text": "Superwork route: superwork-tdd - bounded change."}}),
                json.dumps({"type": "turn.completed", "final_response": "done"}),
            ]
        )

        parsed = parse_jsonl_output(output)

        self.assertEqual(parsed["route"], "superwork-tdd")
        self.assertEqual(parsed["finalMessage"], "done")

    def test_case_scoring_uses_trigger_rate_and_route_accuracy(self) -> None:
        case = {
            "id": "light-change",
            "query": "Change one function",
            "should_trigger": True,
            "expected_route": "superwork-tdd",
        }
        runs = [
            {"triggered": True, "route": "superwork-tdd"},
            {"triggered": True, "route": "superwork-tdd"},
            {"triggered": False, "route": None},
        ]

        result = evaluate_case(case, runs, threshold=0.5)

        self.assertTrue(result["passed"])
        self.assertEqual(result["triggerRate"], 2 / 3)
        self.assertEqual(result["routeAccuracy"], 2 / 3)

    def test_case_scoring_rejects_infrastructure_failures(self) -> None:
        case = {
            "id": "non-repository",
            "query": "Translate this sentence",
            "should_trigger": False,
        }
        runs = [{"triggered": False, "route": None, "exitCode": 1}]

        result = evaluate_case(case, runs, threshold=0.5)

        self.assertFalse(result["passed"])
        self.assertEqual(result["invalidRuns"], 1)

    def test_fixture_and_command_keep_live_eval_isolated_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "fixture"
            create_fixture(fixture, REPO_ROOT / "skills")

            command = build_codex_command("codex", fixture, "Implement one small change")

            self.assertTrue((fixture / ".agents" / "skills" / "superwork-start" / "SKILL.md").exists())
            self.assertTrue((fixture / ".superwork" / "config.json").exists())
            self.assertIn("--ephemeral", command)
            self.assertIn("read-only", command)
            self.assertIn("--ignore-user-config", command)


if __name__ == "__main__":
    unittest.main()
