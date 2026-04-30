# superwork

> Project-local workflow for keeping context, plans, checks, and rules inside `.superwork/`.

`superwork` 是一套项目内工作流。它把上下文、设计、计划、实现、验证和规则都落到 `.superwork/`，让后续工作始终基于项目内文档推进，而不是靠记忆、口头约定或临时聊天状态。

## 概览

`superwork` 的核心约束很简单：先读 `.superwork`，再做事。

它的工作方式是：

- 用 `.superwork/workflow.md` 保存项目本地工作流
- 用 `.superwork/spec/` 保存规则、契约和检查项
- 用 `.superwork/prd/` 保存设计文档
- 用 `.superwork/plans/` 保存可执行计划
- 用 `superwork-start` 作为日常统一入口，自动把任务路由到合适的 skill

最小运行时结构通常是：

```text
.superwork/
├── workflow.md
├── prd/
├── plans/
└── spec/
```

## 使用

只需要记住两步。

### 1. 初始化项目

当项目第一次接入 `superwork`，或者 `.superwork/` 缺失、不完整时，执行：

```bash
superwork-init
```

`superwork-init` 只负责把 `.superwork/` 建起来，并补齐基础工作流与 spec 结构。

### 2. 后续所有任务都从 `start` 进入

初始化完成后，后续所有新任务、继续任务、切换任务，都执行：

```bash
superwork-start
```

`superwork-start` 是日常唯一入口。它会先读取 `workflow.md`、相关 `spec` 和项目上下文，然后自动判断后续应该走哪个 skill，比如：

- 需求不清或要比较方案：`superwork-brainstorming`
- 明确的功能开发或行为变更：`superwork-tdd`
- bug、回归、失败测试、异常行为：`superwork-debugging`
- 准备结束任务并做最终验证：`superwork-check`

也就是说，初始化之后，不需要手动记流程分支，统一从 `superwork-start` 进入。

## Skills

| Skill | 适用场景 | 作用 |
|---|---|---|
| `superwork-init` | 项目首次接入，或 `.superwork/` 缺失/损坏 | 初始化或修复 `.superwork/` 运行时结构与基础文档。 |
| `superwork-start` | 每次开工、继续任务、切换任务 | 读取上下文并把任务路由到正确流程。 |
| `superwork-brainstorming` | 需求不清、要比较方案、要先收敛设计 | 在实现前澄清需求、比较方案、收敛设计，并写出 PRD。 |
| `superwork-writing-plans` | 设计已确认，准备进入执行 | 把明确需求或已批准设计写成可执行计划。 |
| `superwork-executing-plans` | 已经有落盘计划 | 严格按计划逐步执行，并在关键点做验证。 |
| `superwork-tdd` | 明确的功能开发、行为变更、计划内重构 | 执行 test-first 流程，并要求先有落盘计划。 |
| `superwork-debugging` | bug、失败测试、回归、异常行为 | 先找 root cause，再补回归测试并修复。 |
| `superwork-code-simplifier` | 功能已验证通过，但改动偏大或复杂 | 做不改变行为的代码简化和整理。 |
| `superwork-check` | 准备宣称完成、交付、提交前 | 做最终验证、spec 对照和风险检查。 |
| `superwork-update-spec` | 新增了稳定规则、契约、边界条件、验证要求 | 把变更回写到 `.superwork/spec/`。 |
| `superwork-using-git-worktrees` | 需要隔离工作区执行计划 | 在独立 branch workspace 中开展后续实现。 |
