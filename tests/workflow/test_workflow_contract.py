import json
import unittest
from collections import defaultdict, deque
from pathlib import Path

from tests.workflow.yaml_subset import load_mapping


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
            metadata = load_mapping(metadata_path)
            policy = metadata.get("policy")
            self.assertIsInstance(policy, dict)
            if policy.get("allow_implicit_invocation") is True:
                implicit_skills.append(skill)
            else:
                self.assertIs(policy.get("allow_implicit_invocation"), False, skill)

        self.assertEqual(implicit_skills, ["superwork-start"])

    def test_skill_metadata_and_descriptions_are_intent_first(self) -> None:
        for skill in self.contract["skills"]:
            skill_path = REPO_ROOT / "skills" / skill / "SKILL.md"
            content = skill_path.read_text(encoding="utf-8")
            frontmatter = content.split("---", 2)[1]
            fields = {}
            for line in frontmatter.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    fields[key.strip()] = value.strip()
            self.assertEqual(set(fields), {"name", "description"}, skill)
            self.assertEqual(fields["name"], skill)
            self.assertTrue(fields["description"].startswith("Use this skill to"), skill)
            self.assertLessEqual(len(fields["description"]), 1024, skill)

            metadata = load_mapping(REPO_ROOT / "skills" / skill / "agents" / "openai.yaml")
            interface = metadata.get("interface")
            self.assertIsInstance(interface, dict)
            self.assertIn(f"${skill}", interface["default_prompt"])

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

    def test_handoff_contract_is_structured_and_loads_target_skill(self) -> None:
        handoff = self.contract["handoffContract"]

        self.assertEqual(
            handoff["requiredFields"],
            ["target", "caller", "outcome", "evidence", "stopConditions", "returnTo"],
        )
        self.assertEqual(handoff["loadTargetSkill"], "read-full-skill-md")
        self.assertEqual(handoff["targetPath"], "../{target}/SKILL.md")

    def test_plan_execution_contract_is_single_file_and_serial(self) -> None:
        plan = self.contract["planContract"]

        self.assertEqual(plan["format"], "single-markdown-file")
        self.assertEqual(plan["taskHeading"], "### Task <number>: <title>")
        self.assertEqual(plan["executionOrder"], "first-unchecked-task")
        self.assertEqual(plan["statusMarker"], "Task Status")

    def test_phase_skills_load_declared_targets(self) -> None:
        for edge in self.contract["phaseTransitions"]:
            source = edge["from"]
            target = edge["to"]
            if source == "superwork-start":
                continue
            content = (REPO_ROOT / "skills" / source / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f"`../{target}/SKILL.md` in full", content, f"{source} -> {target}")

        for call in self.contract["methodCalls"]:
            caller = call["caller"]
            if caller == "superwork-start":
                continue
            content = (REPO_ROOT / "skills" / caller / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("`../superwork-tdd/SKILL.md` in full", content, caller)

    def test_tdd_supports_direct_use_without_reverting_existing_work(self) -> None:
        content = (REPO_ROOT / "skills" / "superwork-tdd" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("`user`", content)
        self.assertIn("Never revert pre-existing user changes", content)

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

    def test_start_does_not_initialize_missing_runtime_implicitly(self) -> None:
        targets = {edge["to"] for edge in self.contract["phaseTransitions"]}
        self.assertNotIn("superwork-init", targets)

    def test_design_and_plan_skills_continue_by_default(self) -> None:
        transitions = {(edge["from"], edge["to"]) for edge in self.contract["phaseTransitions"]}
        self.assertIn(("superwork-brainstorming", "superwork-writing-plans"), transitions)
        self.assertIn(("superwork-writing-plans", "superwork-executing-plans"), transitions)

    def test_plans_are_resumable_single_file_serial_artifacts(self) -> None:
        writing = (
            REPO_ROOT / "skills" / "superwork-writing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")
        executing = (
            REPO_ROOT / "skills" / "superwork-executing-plans" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("one Markdown file", writing)
        self.assertIn("`### Task <number>: <title>`", writing)
        self.assertIn("`Task Status`", writing)
        self.assertNotIn("overview.md", writing)
        self.assertIn("first unchecked task in document order", executing)
        self.assertNotIn("dependency-ready", executing)

    def test_plan_preflight_reports_the_declared_task_heading(self) -> None:
        plan = self.contract["planContract"]
        preflight = (
            REPO_ROOT / "skills" / "superwork-executing-plans" / "scripts" / "preflight_plan.py"
        ).read_text(encoding="utf-8")

        self.assertIn(f'TASK_HEADING_FORMAT = "{plan["taskHeading"]}"', preflight)

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
