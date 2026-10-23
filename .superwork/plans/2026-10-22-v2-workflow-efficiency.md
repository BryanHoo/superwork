# V2 Workflow Efficiency Implementation Plan

**Goal:** 在 v2 上引入技能一次加载、有效证据复用和按需参考资料读取。

**Suggested Spec Reads:**

- `.superwork/spec/guides/index.md` — 路由、交接和最终验收规则
- `.superwork/spec/shared/quality-guidelines.md` — 回归验证和计划模板约束
- `.superwork/spec/shared/directory-structure.md` — 技能与工具归属

**Architecture:** 保留八技能、三级路由、持久化计划及接口预检；在 schema 2 上增量增加上下文候选，并集中声明读取缓存与验证证据的失效条件。

**Tech Stack:** Markdown、JSON、Python 3.14、unittest。

## Global Constraints

- 在 `feat/v2` 上工作；不提交或推送。
- 保留设计到计划到执行的交接及每个代码切片的 TDD。
- 保留计划的 Global Constraints、Suggested Spec Reads、Interfaces、Run、Expected 和预检。
- 保留 schemaVersion 2 和 recommendedReads 输出兼容性。
- 公共约束必读；技能或上下文失效后重新加载；证据不可确认时重新验证。

### Task 1: 按目标范围返回上下文候选

**Files:**

- Modify: `skills/superwork-start/scripts/get_context.py`
- Create: `tests/workflow/test_context_candidates.py`

**Interfaces:**

- Consumes: `runtime-schema-2`
- Produces: `context-candidates-v2`

**Behavior:**

- 输出带优先级、原因和大小的候选，支持通过 --files 在编辑前定位规范，保留公共和共享约束以及无法映射时的保守回退。

**Stop Conditions:**

- Stop if existing runtime or recommendedReads consumers require a schema migration.

- [x] **Task Status:** completed

Run: `python3 -m unittest tests.workflow.test_context_candidates -v`

Expected: clean、changed、planned、shared、monorepo、fallback 和 missing-runtime 场景通过。

### Task 2: 统一技能加载与证据复用约束

**Files:**

- Modify: `skills/superwork-start/SKILL.md`
- Modify: `skills/superwork-start/references/workflow-contract.json`
- Modify: `skills/superwork-brainstorming/SKILL.md`
- Modify: `skills/superwork-writing-plans/SKILL.md`
- Modify: `skills/superwork-executing-plans/SKILL.md`
- Modify: `skills/superwork-tdd/SKILL.md`
- Modify: `skills/superwork-debugging/SKILL.md`
- Modify: `skills/superwork-check/SKILL.md`
- Modify: `skills/superwork-init/SKILL.md`
- Create: `skills/superwork-check/references/verification-evidence.md`
- Modify: `tests/workflow/test_workflow_contract.py`
- Create: `tests/workflow/test_plan_guardrails.py`

**Interfaces:**

- Consumes: `context-candidates-v2`
- Produces: `bounded-reuse-policy-v2`

**Behavior:**

- 同一运行复用完整技能内容；指令改变或上下文丢失时重读。验证复用必须满足同一行为、命令范围、工作区与输入状态，禁止跨执行者直接信任结果。
- 保留 v2 路由和接口预检，用可执行计划回归验证接口漂移及规范引用仍被拒绝。

**Stop Conditions:**

- Stop if an optimization removes a v2 planning, TDD, interface, or completion gate.

- [x] **Task Status:** completed

Run: `python3 -m unittest discover -s tests/workflow -p 'test_*.py' -v`

Expected: workflow contract、context candidates 和 plan guardrail tests 通过。

### Task 3: 同步项目规则并完成验证

**Files:**

- Modify: `skills/superwork-init/templates/guides-index.md.tmpl`
- Modify: `skills/superwork-check/references/simplification-review.md`
- Modify: `.superwork/spec/guides/index.md`
- Modify: `.superwork/spec/shared/index.md`
- Modify: `.superwork/spec/shared/quality-guidelines.md`

**Interfaces:**

- Consumes: `bounded-reuse-policy-v2`
- Produces: `verified-v2-workflow`

**Behavior:**

- 项目规范和初始化模板采用同一读取与证据有效性规则，最终检查当前代码、规范与计划状态。

**Stop Conditions:**

- Stop if required verification fails or any v2 plan contract has regressed.

- [x] **Task Status:** completed

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v && python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v`

Expected: 全部测试通过，八技能和 schema 2 保持一致。

## Completion Evidence

- Task 1 RED: `python3 -m unittest tests.workflow.test_context_candidates -v` 首次因缺少 candidateReads 和 --files 支持失败；实现后 7 项通过。
- Task 2 RED: handoff 和 phase skill 两项既有契约测试在要求一次加载时失败；更新规则后通过。
- Final: `python3 -m unittest discover -s tests -p 'test_*.py' -v`，38 项通过，退出码 0。
- Final: `python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v`，21 项通过，退出码 0。
- 以上测试在当前工作区、最终代码和规范修改后使用 Python 3.14 执行；子进程使用同一 PATH，临时 Git fixture 不访问生产环境。
- 八个技能均通过 skill-creator 的 quick_validate.py；该独立格式检查使用安装了 PyYAML 的系统 Python 3。
- 对照回归确认：相同接口签名的计划通过，接口漂移、缺失全局约束和不存在的规范引用均被拒绝。
- 规则走查确认：等效当前结果可复用；依赖或环境变化、跨执行者、明确重跑请求、以局部测试代替全量检查时必须重新验证。此项为规则审阅，不计为真实模型行为测试。
- Simplification: no-change，未引入额外实现阶段或执行器。
- Spec: update，公共指南与 shared 质量约束已记录新规则。
- 路由、触发描述、八技能集合及 schema 2 保留；未运行真实模型触发或开发成功率评测。
