# Superwork Skills Best Practices Implementation Plan

**Goal:** 修复 Superwork skills 的触发、交接、计划恢复、项目探测和真实行为验证缺口，同时保留默认自动推进语义。

**Suggested Spec Reads:**

- `.superwork/spec/guides/index.md` - 工作流入口、验证命令和 handoff 规则
- `.superwork/spec/shared/quality-guidelines.md` - skill 结构、回归测试和真实 eval 约束
- `.superwork/spec/shared/directory-structure.md` - skill、共享脚本和测试资产的归属

**Architecture:** 保留一个隐式 router 和七个显式 phase skills；用结构化 handoff 与完整目标 skill 读取替代模糊调用；计划统一为可恢复的单文件串行格式；共享仓库探测器为 start、init 和 check 提供一致事实；Codex eval 在隔离只读 fixture 中验证真实触发和路由。

**Tech Stack:** Markdown skills、JSON contracts/evals、Python 3 标准库、`unittest`、Codex CLI JSONL。

## Global Constraints

- 保留 `superwork-check` 默认应用范围内简化和 spec 更新的自动推进语义。
- 保留用户工作树中已有的无关改动。
- 所有 Python 命令使用 `python3`，所有子进程设置超时并使用非交互模式。
- 不增加旧计划格式或旧 workflow/state 模型的兼容分支。
- 不执行 Git branch、commit、push 或 PR 操作。

### Task 1: 统一计划恢复与 skill handoff 契约

**Files:**

- Modify: `skills/superwork-start/SKILL.md`
- Modify: `skills/superwork-start/references/workflow-contract.json`
- Modify: `skills/superwork-brainstorming/SKILL.md`
- Modify: `skills/superwork-writing-plans/SKILL.md`
- Modify: `skills/superwork-executing-plans/SKILL.md`
- Modify: `skills/superwork-debugging/SKILL.md`
- Modify: `skills/superwork-init/SKILL.md`
- Modify: `skills/superwork-tdd/SKILL.md`
- Modify: `skills/superwork-executing-plans/scripts/preflight_plan.py`
- Modify: `tests/workflow/test_workflow_contract.py`
- Modify: `skills/superwork-init/tests/test_layered_spec_layout.py`

**Interfaces:**

- Consumes: `workflow-contract-v3`
- Produces: `workflow-contract-v4`

**Stop Conditions:**

- Stop if a target skill cannot be resolved from the plugin bundle or a valid serial plan cannot be resumed deterministically.

- [x] **Task Status:** completed

Run: `python3 -m unittest tests.workflow.test_workflow_contract skills.superwork-init.tests.test_layered_spec_layout -v`

Expected: 计划状态、串行恢复、结构化 handoff 和直接 TDD 调用契约全部通过。

### Task 2: 统一仓库事实和变更探测

**Files:**

- Create: `skills/_shared/__init__.py`
- Create: `skills/_shared/repository.py`
- Modify: `skills/superwork-start/scripts/get_context.py`
- Modify: `skills/superwork-init/scripts/bootstrap_superwork.py`
- Modify: `skills/superwork-check/scripts/check_specs.py`
- Modify: `skills/superwork-check/scripts/update_spec.py`
- Modify: `skills/superwork-init/tests/test_layered_spec_layout.py`

**Interfaces:**

- Consumes: `workflow-contract-v4`
- Produces: `repository-facts-v4`

**Stop Conditions:**

- Stop if a non-Node repository still receives an invented Node verification command or untracked files are absent from context.

- [x] **Task Status:** completed

Run: `python3 -m unittest skills.superwork-init.tests.test_layered_spec_layout -v`

Expected: Python、Node 和无工具仓库得到真实 verification，所有变更探测器覆盖未跟踪文件并报告 Git 错误。

### Task 3: 建立真实触发 eval 和结构化 metadata 校验

**Files:**

- Create: `tests/evals/trigger_train.json`
- Create: `tests/evals/trigger_validation.json`
- Create: `tests/evals/__init__.py`
- Create: `tests/evals/run_skill_evals.py`
- Create: `tests/evals/test_eval_runner.py`
- Create: `tests/workflow/yaml_subset.py`
- Modify: `tests/workflow/scenarios.json`
- Modify: `tests/workflow/test_scenarios.py`
- Modify: `tests/workflow/test_workflow_contract.py`
- Modify: `skills/*/agents/openai.yaml`
- Modify: `skills/*/SKILL.md`

**Interfaces:**

- Consumes: `repository-facts-v4`
- Produces: `skill-eval-v1`

**Stop Conditions:**

- Stop if eval 会写入被测仓库、无法区分 should-trigger/should-not-trigger，或无法输出逐次运行证据。

- [x] **Task Status:** completed

Run: `python3 -m unittest tests.evals.test_eval_runner tests.workflow.test_scenarios tests.workflow.test_workflow_contract -v`

Expected: eval 数据集、JSONL 解析、触发率判定、YAML 结构和 intent-first descriptions 全部通过。

### Task 4: 同步 durable spec 并完成最终验证

**Files:**

- Modify: `.superwork/spec/guides/index.md`
- Modify: `.superwork/spec/shared/quality-guidelines.md`
- Modify: `.superwork/spec/shared/directory-structure.md`
- Modify: `.gitignore`
- Test: `.superwork/config.json`
- Test: `tests/**`
- Test: `skills/superwork-init/tests/**`

**Interfaces:**

- Consumes: `skill-eval-v1`
- Produces: `completion-evidence-v4`

**Stop Conditions:**

- Stop if任一静态测试、官方 skill validator、有效 live eval smoke 或最终 diff 检查失败；认证和网络基础设施失败必须记录为 invalid，不得伪装成 skill 结果。

- [x] **Task Status:** completed

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: 全量测试、官方 validators 和最终 spec 检查通过；隔离 live eval 返回行为结果或可诊断的 invalid 基础设施证据。
