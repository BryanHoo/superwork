import json
import unittest
from collections import defaultdict, deque
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    REPO_ROOT / "skills" / "superwork-start" / "references" / "workflow-contract.json"
)
SCENARIOS_PATH = REPO_ROOT / "tests" / "workflow" / "scenarios.json"


class WorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))

    def test_contract_declares_target_skill_set(self) -> None:
        expected = set(self.contract["skills"])
        discovered = {
            path.parent.name
            for path in (REPO_ROOT / "skills").glob("superwork-*/SKILL.md")
        }

        self.assertEqual(discovered, expected)
        self.assertEqual(len(expected), 8)

    def test_only_start_is_implicit_entry(self) -> None:
        self.assertEqual(self.contract["implicitEntry"], "superwork-start")

        implicit_skills = []
        for skill in self.contract["skills"]:
            metadata_path = REPO_ROOT / "skills" / skill / "agents" / "openai.yaml"
            self.assertTrue(metadata_path.exists(), f"missing metadata: {metadata_path}")
            content = metadata_path.read_text(encoding="utf-8")
            if "allow_implicit_invocation: true" in content:
                implicit_skills.append(skill)
            else:
                self.assertIn("allow_implicit_invocation: false", content, skill)

        self.assertEqual(implicit_skills, ["superwork-start"])

    def test_plugin_manifest_packages_all_skills(self) -> None:
        manifest_path = REPO_ROOT / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "superwork")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["interface"]["displayName"], "Superwork")
        self.assertEqual(manifest["version"].count("."), 2)

    def test_phase_transitions_are_acyclic(self) -> None:
        graph: dict[str, set[str]] = defaultdict(set)
        indegree: dict[str, int] = defaultdict(int)
        nodes: set[str] = set()

        for edge in self.contract["phaseTransitions"]:
            source = edge["from"]
            target = edge["to"]
            nodes.update((source, target))
            if target not in graph[source]:
                graph[source].add(target)
                indegree[target] += 1
            indegree.setdefault(source, 0)

        queue = deque(node for node in nodes if indegree[node] == 0)
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            # 拓扑遍历只检查阶段推进；TDD call/return 单独建模，避免把方法调用误判为流程环。
            for target in graph[node]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)

        self.assertEqual(visited, len(nodes), "phaseTransitions must be acyclic")

    def test_tdd_is_a_method_with_expected_callers(self) -> None:
        calls = self.contract["methodCalls"]
        self.assertEqual(
            {item["caller"] for item in calls if item["method"] == "superwork-tdd"},
            {"superwork-start", "superwork-executing-plans", "superwork-debugging"},
        )
        phase_nodes = {
            value
            for edge in self.contract["phaseTransitions"]
            for value in (edge["from"], edge["to"])
        }
        self.assertNotIn("superwork-tdd", phase_nodes)

    def test_skill_text_assigns_tdd_one_implementation_role(self) -> None:
        tdd = (REPO_ROOT / "skills" / "superwork-tdd" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        debugging = (
            REPO_ROOT / "skills" / "superwork-debugging" / "SKILL.md"
        ).read_text(encoding="utf-8")
        executing = (
            REPO_ROOT / "skills" / "superwork-executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        writing = (
            REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("not limited to light tasks", tdd)
        self.assertIn("Return to the caller", tdd)
        self.assertNotIn("NO LIGHT-TASK EXECUTION", tdd)
        self.assertIn("invoke `superwork-tdd`", debugging)
        self.assertIn("does not write the regression test", debugging)
        self.assertIn("invoke `superwork-tdd`", executing)
        self.assertIn("TDD method", writing)

    def test_contract_defaults_to_continuous_execution(self) -> None:
        self.assertEqual(
            self.contract["continuationPolicy"],
            {
                "default": "complete",
                "stopCondition": "explicit-user-instruction",
            },
        )
        self.assertNotIn("authorizationLevels", self.contract)
        self.assertNotIn("authorizationTerminals", self.contract)

    def test_start_continues_unless_user_explicitly_stops(self) -> None:
        content = (
            REPO_ROOT / "skills" / "superwork-start" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Continue by default", content)
        self.assertIn("explicit user instruction", content)
        self.assertNotIn("authorized_until", content)
        self.assertNotIn("authorization boundary", content.lower())

    def test_start_does_not_initialize_missing_runtime_implicitly(self) -> None:
        content = (
            REPO_ROOT / "skills" / "superwork-start" / "SKILL.md"
        ).read_text(encoding="utf-8")

        normalized = content.lower()
        self.assertIn("Do not invoke `superwork-init`", content)
        self.assertIn("read-only requests can finish without `.superwork/`", normalized)

    def test_design_and_plan_skills_continue_by_default(self) -> None:
        brainstorming = (
            REPO_ROOT / "skills" / "superwork-brainstorming" / "SKILL.md"
        ).read_text(encoding="utf-8")
        writing_plans = (
            REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Continue by default", brainstorming)
        self.assertIn("explicitly asks to stop after design", brainstorming)
        self.assertNotIn("authorized_until", brainstorming)
        self.assertNotIn("Authorized Until", writing_plans)
        self.assertIn("Stop Conditions", writing_plans)
        self.assertIn("invoke `superwork-executing-plans`", writing_plans)
        self.assertIn("explicitly asks for a plan only", writing_plans)

    def test_check_is_the_only_completion_skill(self) -> None:
        self.assertEqual(self.contract["completionSkill"], "superwork-check")
        self.assertNotIn("superwork-code-simplifier", self.contract["skills"])
        self.assertNotIn("superwork-update-spec", self.contract["skills"])

    def test_check_owns_one_internal_finalization_sequence(self) -> None:
        content = (REPO_ROOT / "skills" / "superwork-check" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        headings = [
            "### Step 1: Gather context",
            "### Step 2: Inspect the diff",
            "### Step 3: Review simplification",
            "### Step 4: Run fresh verification",
            "### Step 5: Decide spec",
            "### Step 6: Validate spec artifacts",
            "### Step 7: Report",
        ]
        positions = [content.index(heading) for heading in headings]

        self.assertEqual(positions, sorted(positions))
        self.assertIn("`no-change`", content)
        self.assertIn("`update`, `create`, or `no-update`", content)
        self.assertIn("explicit read-only request", content)
        self.assertNotIn("authorized_until", content)
        self.assertNotIn("route to `superwork-check`", content.lower())
        self.assertTrue(
            (REPO_ROOT / "skills" / "superwork-check" / "references" / "simplification-review.md").exists()
        )
        self.assertTrue(
            (REPO_ROOT / "skills" / "superwork-check" / "references" / "spec-update.md").exists()
        )

    def test_removed_skill_references_are_absent(self) -> None:
        forbidden = ("superwork-code-simplifier", "superwork-update-spec")
        offenders: list[str] = []
        candidates = list((REPO_ROOT / "skills").glob("superwork-*/SKILL.md"))
        candidates.extend((REPO_ROOT / "skills" / "superwork-init" / "templates").glob("*"))

        for path in candidates:
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            if any(value in content for value in forbidden):
                offenders.append(str(path.relative_to(REPO_ROOT)))

        self.assertEqual(offenders, [])

    def test_continuous_scenarios_require_tdd_and_complete_once(self) -> None:
        scenarios = [
            item for item in self.scenarios if item["expectedPath"][-1] == "superwork-check"
        ]
        self.assertGreaterEqual(len(scenarios), 1)

        for scenario in scenarios:
            if scenario["expectedRoute"] not in {"superwork-check"}:
                self.assertIn("superwork-tdd", scenario["requiredMethods"], scenario["id"])
            self.assertEqual(
                scenario["expectedPath"].count("superwork-check"),
                1,
                scenario["id"],
            )


if __name__ == "__main__":
    unittest.main()
