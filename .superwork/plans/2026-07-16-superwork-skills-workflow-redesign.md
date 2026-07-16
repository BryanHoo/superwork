# Superwork Skills Workflow Redesign Implementation Plan

**Goal:** 将 Superwork 重构为 8 个职责清晰且默认连续执行到最终验证的 skills。

**Suggested Spec Reads:**

- `.superwork/spec/guides/index.md` — 工作流总规则与验证命令
- `.superwork/spec/shared/quality-guidelines.md` — 回归测试和质量约束
- `.superwork/spec/guides/cross-layer-thinking-guide.md` — handoff 与 method call 规则

**Architecture:** `superwork-start` 选择首个 route；设计、计划和执行默认单向衔接；`superwork-tdd` 作为实现方法返回 caller；`superwork-check` 唯一完成最终化。

**Tech Stack:** Markdown skills、JSON contract/scenarios、Python 3 validators、`unittest`。

## Global Constraints

- 保留用户工作树中的无关改动。
- 仅在用户输入明确要求提前停止或只读时中断默认流程。
- 所有代码行为改动先建立 RED，再达到 GREEN。
- 不增加旧 workflow/state 模型的兼容分支。
- 不自动执行 Git branch、commit、push 或 PR 操作。

### Task 1: 收敛 skill 集合与职责

**Files:**

- Modify: `skills/superwork-*/SKILL.md`
- Delete: `skills/superwork-code-simplifier/**`
- Delete: `skills/superwork-update-spec/**`

**Interfaces:**

- Consumes: `legacy-skill-set: ten overlapping skills`
- Produces: `skill-set-v3: eight single-responsibility skills`

**Stop Conditions:**

- Stop if a removed skill still owns behavior that has no target owner.

- [x] **Step 1: 删除重复 skill 并迁移唯一职责**

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: 发现的 skill 集合严格等于 contract 中的 8 个 skills。

### Task 2: 建立默认连续执行契约

**Files:**

- Modify: `skills/superwork-start/SKILL.md`
- Modify: `skills/superwork-brainstorming/SKILL.md`
- Modify: `skills/superwork-writing-plans/SKILL.md`
- Modify: `skills/superwork-executing-plans/SKILL.md`
- Modify: `skills/superwork-check/SKILL.md`
- Modify: `skills/superwork-start/references/workflow-contract.json`

**Interfaces:**

- Consumes: `skill-set-v3: eight single-responsibility skills`
- Produces: `continuation-policy-v3: complete by default and stop on explicit user instruction`

**Stop Conditions:**

- Stop if phase transitions form a cycle or completion can be entered more than once.

- [x] **Step 1: 删除阶段状态并串联默认 handoff**

Run: `python3 -m unittest tests.workflow.test_workflow_contract -v`

Expected: contract、入口和下游 skills 共同证明默认连续执行且流程无环。

### Task 3: 简化计划 preflight

**Files:**

- Modify: `skills/superwork-executing-plans/scripts/preflight_plan.py`
- Modify: `skills/superwork-init/tests/test_layered_spec_layout.py`

**Interfaces:**

- Consumes: `continuation-policy-v3: complete by default and stop on explicit user instruction`
- Produces: `plan-preflight-v3: structural quality result without phase state`

**Stop Conditions:**

- Stop if malformed plans can pass or valid plans require unrelated metadata.

- [x] **Step 1: 只保留结构、接口和验收信号检查**

Run: `python3 -m unittest skills.superwork-init.tests.test_layered_spec_layout -v`

Expected: 完整计划通过，缺少 `Stop Conditions` 的计划失败，payload 只包含结构质量结果。

### Task 4: 更新场景、metadata 与 durable spec

**Files:**

- Modify: `tests/workflow/scenarios.json`
- Modify: `tests/workflow/test_scenarios.py`
- Modify: `.codex-plugin/plugin.json`
- Modify: `skills/*/agents/openai.yaml`
- Modify: `.superwork/spec/**`

**Interfaces:**

- Consumes: `plan-preflight-v3: structural quality result without phase state`
- Produces: `workflow-evidence-v3: scenarios metadata and specs aligned with continuous execution`

**Stop Conditions:**

- Stop if any route loses positive/negative coverage or metadata enables another implicit entry.

- [x] **Step 1: 同步场景 schema、插件描述和项目规则**

Run: `python3 -m unittest tests.workflow.test_scenarios tests.workflow.test_workflow_contract -v`

Expected: 至少 40 个场景通过，所有 route 均有正反覆盖，默认完成路径只进入一次 check。

### Task 5: 完成 fresh verification

**Files:**

- Test: `tests/workflow/test_workflow_contract.py`
- Test: `tests/workflow/test_scenarios.py`
- Test: `skills/superwork-init/tests/test_layered_spec_layout.py`

**Interfaces:**

- Consumes: `workflow-evidence-v3: scenarios metadata and specs aligned with continuous execution`
- Produces: `completion-evidence-v3: fresh full-suite and validator results`

**Stop Conditions:**

- Stop if any required command fails or stale workflow wording remains in active artifacts.

- [x] **Step 1: 运行全量测试和 validators**

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: 全部 workflow tests PASS，随后 runtime、plugin 和 skill validators PASS。
