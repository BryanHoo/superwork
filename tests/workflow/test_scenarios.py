import json
import unittest
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_PATH = REPO_ROOT / "tests" / "workflow" / "scenarios.json"
REQUIRED_FIELDS = {
    "id",
    "caseType",
    "prompt",
    "repositoryState",
    "expectedEntry",
    "expectedRoute",
    "expectedPath",
    "requiredMethods",
    "forbiddenActions",
}


class WorkflowScenarioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))

    def test_has_balanced_scenario_inventory(self) -> None:
        self.assertGreaterEqual(len(self.scenarios), 40)
        positive = [item for item in self.scenarios if item.get("caseType") == "positive"]
        negative = [item for item in self.scenarios if item.get("caseType") == "negative"]
        self.assertGreaterEqual(len(positive), 20)
        self.assertGreaterEqual(len(negative), 20)

    def test_ids_and_fields_are_valid(self) -> None:
        ids = [item.get("id") for item in self.scenarios]
        self.assertEqual(len(ids), len(set(ids)))

        for item in self.scenarios:
            self.assertEqual(set(item), REQUIRED_FIELDS, item.get("id"))
            self.assertIn(item["caseType"], {"positive", "negative"})
            self.assertEqual(item["expectedEntry"], "superwork-start")
            self.assertIsInstance(item["expectedPath"], list)
            self.assertIsInstance(item["requiredMethods"], list)
            self.assertIsInstance(item["forbiddenActions"], list)

    def test_each_route_has_positive_and_negative_neighbors(self) -> None:
        coverage: dict[str, set[str]] = defaultdict(set)
        for item in self.scenarios:
            coverage[item["expectedRoute"]].add(item["caseType"])

        expected_routes = {
            "direct-response",
            "superwork-brainstorming",
            "superwork-writing-plans",
            "superwork-tdd",
            "superwork-debugging",
            "superwork-check",
            "superwork-executing-plans",
        }
        self.assertEqual(set(coverage), expected_routes)
        for route in expected_routes:
            self.assertEqual(coverage[route], {"positive", "negative"}, route)

    def test_continuous_paths_finalize_once(self) -> None:
        for item in self.scenarios:
            if item["expectedPath"][-1] != "superwork-check":
                continue
            self.assertEqual(item["expectedPath"].count("superwork-check"), 1, item["id"])
            if item["expectedRoute"] != "superwork-check":
                self.assertIn("superwork-tdd", item["requiredMethods"], item["id"])


if __name__ == "__main__":
    unittest.main()
