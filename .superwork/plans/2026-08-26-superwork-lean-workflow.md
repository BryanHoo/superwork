# Superwork Lean Workflow Implementation Plan

**Goal:** 保留开发任务强制 TDD，同时减少项目文档预读、计划阶段交接和重复验证开销。
**Scope:** Superwork skills、workflow contract、deterministic scripts、workflow/eval tests 和 durable specs。
**Acceptance:** 全量静态测试与 init 测试通过，所有开发路径仍调用 TDD，初始上下文与规划阶段减少。

**Suggested Spec Reads:**

- `.superwork/spec/guides/index.md` - 工作流路由、验证和 spec 更新约束
- `.superwork/spec/shared/quality-guidelines.md` - skill、TDD、eval 和完成条件
- `.superwork/spec/shared/directory-structure.md` - skill、脚本、契约和测试资产归属

**Architecture:** 保留单一隐式入口和独立 TDD 方法；将设计与写计划合并为按需 planning，保存计划仅由恢复场景进入 executing-plans；上下文脚本输出带优先级的候选读取；最终检查复用 TDD 证据并按风险加载 spec 规则。

**Tech Stack:** Markdown skills、JSON workflow contract、Python 3 标准库、`unittest`、Codex CLI JSONL。

## Global Constraints

- 保留所有开发行为路径必须调用 `superwork-tdd` 的契约。
- 保留用户工作树中的无关改动，不执行 commit、branch、push 或 PR。
- 不增加被移除规划拓扑的兼容分支。
- 所有 Python 命令使用 `python3`。

### Task 1: 输出按需项目上下文

**Files:**

- Modify: `skills/superwork-start/scripts/get_context.py`
- Modify: `skills/superwork-start/SKILL.md`
- Modify: `skills/superwork-init/tests/test_layered_spec_layout.py`

**Interfaces:**

- Consumes: `context-v2`
- Produces: `candidate-reads-v3`

**Behavior:**

- 让上下文脚本返回带 `path`、`reason`、`priority` 和 `size` 的候选读取，入口只立即读取 required 项，其余文档按任务证据加载。

**Proof:** `python3 -m unittest skills.superwork-init.tests.test_layered_spec_layout -v`

**Stop Conditions:**

- Stop if missing runtime handling or changed-file scoping can no longer be represented without eagerly reading spec files.

- [x] **Task Status:** completed

Run: `python3 -m unittest skills.superwork-init.tests.test_layered_spec_layout -v`

Expected: context tests validate compact required facts and scoped candidate reads without mandatory full-index loading.

### Task 2: 收敛规划拓扑并保留强制 TDD

**Files:**

- Create: `skills/superwork-planning/SKILL.md`
- Create: `skills/superwork-planning/agents/openai.yaml`
- Delete: `skills/superwork-brainstorming/SKILL.md`
- Delete: `skills/superwork-brainstorming/agents/openai.yaml`
- Delete: `skills/superwork-writing-plans/SKILL.md`
- Delete: `skills/superwork-writing-plans/agents/openai.yaml`
- Modify: `skills/superwork-start/SKILL.md`
- Modify: `skills/superwork-start/references/workflow-contract.json`
- Modify: `skills/superwork-executing-plans/SKILL.md`
- Modify: `skills/superwork-tdd/SKILL.md`
- Modify: `tests/workflow/scenarios.json`
- Modify: `tests/workflow/test_scenarios.py`
- Modify: `tests/workflow/test_workflow_contract.py`
- Modify: `tests/evals/trigger_train.json`
- Modify: `tests/evals/trigger_validation.json`

**Interfaces:**

- Consumes: `workflow-contract-v2`
- Produces: `workflow-contract-v3`

**Behavior:**

- 让清晰开发直接进入 TDD，复杂或显式规划进入单一 planning；同会话 planning 直接调用 TDD，executing-plans 仅处理已保存计划恢复。

**Proof:** `python3 -m unittest tests.workflow.test_workflow_contract tests.workflow.test_scenarios tests.evals.test_eval_runner -v`

**Stop Conditions:**

- Stop if any development path can complete without TDD or more than one skill becomes implicitly invocable.

- [x] **Task Status:** completed

Run: `python3 -m unittest tests.workflow.test_workflow_contract tests.workflow.test_scenarios tests.evals.test_eval_runner -v`

Expected: seven-skill topology、planning route、saved-plan resume and mandatory TDD contracts all pass.

### Task 3: 精简持久化计划和验证交接

**Files:**

- Modify: `skills/superwork-planning/SKILL.md`
- Modify: `skills/superwork-executing-plans/SKILL.md`
- Modify: `skills/superwork-executing-plans/scripts/preflight_plan.py`
- Modify: `skills/superwork-start/references/workflow-contract.json`
- Modify: `skills/superwork-init/tests/test_layered_spec_layout.py`

**Interfaces:**

- Consumes: `workflow-contract-v3`
- Produces: `compact-plan-contract-v3`

**Behavior:**

- 将持久化计划缩减为 goal、scope、acceptance 和任务级 files、behavior、proof、stop conditions、status；interfaces 仅在真实跨任务契约存在时可选。

**Proof:** `python3 -m unittest skills.superwork-init.tests.test_layered_spec_layout tests.workflow.test_workflow_contract -v`

**Stop Conditions:**

- Stop if a compact plan cannot resume deterministically from the first unchecked task.

- [x] **Task Status:** completed

Run: `python3 -m unittest skills.superwork-init.tests.test_layered_spec_layout tests.workflow.test_workflow_contract -v`

Expected: compact template passes preflight, malformed resumable plans still fail, and TDD proof is not duplicated by the executor.

### Task 4: 按风险完成检查并扩展效率评估

**Files:**

- Modify: `skills/superwork-check/SKILL.md`
- Create: `skills/superwork-init/tests/_support.py`
- Create: `skills/superwork-init/tests/test_runtime_bootstrap.py`
- Modify: `skills/superwork-init/tests/test_layered_spec_layout.py`
- Modify: `tests/evals/run_skill_evals.py`
- Modify: `tests/evals/test_eval_runner.py`
- Modify: `.superwork/spec/guides/index.md`
- Modify: `.superwork/spec/shared/index.md`
- Modify: `.superwork/spec/shared/directory-structure.md`
- Modify: `.superwork/spec/shared/quality-guidelines.md`

**Interfaces:**

- Consumes: `compact-plan-contract-v3`
- Produces: `completion-evidence-v3`

**Behavior:**

- 让 check 复用最后一次代码修改后的 targeted TDD evidence，只补 broader checks；仅在高信号变更时读取 spec/simplification 参考，并让 eval 汇总耗时和事件数，遇到确定性认证失败时立即终止整套评估。

**Proof:** `python3 -m unittest discover -s tests -p 'test_*.py' -v`

**Stop Conditions:**

- Stop if completion can reuse evidence from before the final code edit or eval loses invalid-run detection.

- [x] **Task Status:** completed

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: full workflow tests pass with risk-driven finalization and efficiency metrics, then init tests also pass.
