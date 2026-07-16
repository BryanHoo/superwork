# Superwork Skills Workflow Redesign

**Goal:** 将 Superwork 收敛为职责单一、默认连续执行、可通过契约和场景验证的 8 个 skills。

**Suggested Spec Reads:**

- `.superwork/spec/guides/index.md` — 工作流与验证总规则
- `.superwork/spec/shared/quality-guidelines.md` — 回归测试和质量要求
- `.superwork/spec/guides/cross-layer-thinking-guide.md` — 跨 skill handoff 约束

## 核心决策

1. `superwork-start` 是唯一隐式入口，只选择第一个下游 route。
2. change、build、fix 类请求默认从 route 连续执行到 `superwork-check`。
3. 只有用户输入明确要求只分析、只设计、只写计划、不要实现或不要修改文件时，流程才提前停止或保持只读。
4. `superwork-tdd` 是实现方法，不是独立规划阶段；调用完成后返回原 caller。
5. `superwork-check` 是唯一最终化 skill，统一完成简化审查、fresh verification 和 spec 决策。
6. `.superwork/config.json` 和 `.superwork/spec/**` 保存项目事实；通用流程只存在于 skill package 和 workflow contract。

## Skill 职责

| Skill | 单一职责 | 默认后续 |
| --- | --- | --- |
| `superwork-init` | 显式初始化或修复项目 runtime | 返回入口 |
| `superwork-start` | 读取上下文并选择第一个 route | 一个下游 route |
| `superwork-brainstorming` | 收敛重型需求并写设计 | `superwork-writing-plans` |
| `superwork-writing-plans` | 写可预检的实施计划 | `superwork-executing-plans` |
| `superwork-executing-plans` | 按计划协调行为切片 | `superwork-check` |
| `superwork-tdd` | 对一个行为切片执行 RED/GREEN/REFACTOR | 返回 caller |
| `superwork-debugging` | 复现问题并确认根因 | TDD 修复后进入 check |
| `superwork-check` | 一次性最终化和证据报告 | 完成 |

## Route 规则

| 请求类型 | 首个 route |
| --- | --- |
| 解释、评审、分析且没有变更请求 | `direct-response` |
| 明确的 final verification | `superwork-check` |
| 已保存计划的继续执行 | `superwork-executing-plans` |
| bug、regression、failing test | `superwork-debugging` |
| 单文件或紧凑行为切片 | `superwork-tdd` |
| 清晰的多文件协调 | `superwork-writing-plans` |
| 需求、架构或跨系统取舍未收敛 | `superwork-brainstorming` |

任务规模只决定规划深度，不决定是否使用 TDD。

## 连续执行规则

- 入口只报告 route 和理由，不维护阶段状态。
- brainstorming 自检设计后默认进入 writing-plans。
- writing-plans 通过 preflight 后默认进入 executing-plans。
- executing-plans 完成全部任务后只进入一次 check。
- 用户输入中的明确限制优先；到达其要求的产物后停止。
- 无法安全推断的实质选择、失败的 preflight、计划漂移或外部阻塞仍可停止流程。

## Plan 与 Preflight

计划必须包含：

- 真实的 `Suggested Spec Reads`
- `Global Constraints`
- 每个 task 的 `Files`、`Interfaces` 和 `Stop Conditions`
- 可证伪的 verification command 与 `Expected:` signal

`preflight_plan.py` 只返回结构质量：

```json
{
  "plan": "/absolute/path/to/plan.md",
  "ok": true,
  "issues": [],
  "warnings": []
}
```

## Workflow Contract 与场景

`workflow-contract.json` 固定：

- 8 个 skills
- 唯一隐式入口
- `continuationPolicy.default=complete`
- 无环的 phase transitions
- TDD method calls 和 caller return
- 唯一 completion skill

场景 eval 至少包含 20 个 positive 和 20 个 negative cases，覆盖每个 route、明确提前停止、默认完成、禁止动作和一次性最终化。

## 非目标

- 不自动执行 Git branch、commit、push 或 PR 操作。
- 不把 `.superwork/` 缺失当作隐式初始化请求。
- 不恢复已删除的 skill 或旧 workflow/state 多事实源。
- 不为旧计划格式添加兼容分支。

## 成功标准

- 活动 skills、contract、preflight、metadata、spec 和场景不再依赖旧阶段边界模型。
- 变更请求默认连续到 fresh verification。
- 明确只读或提前停止的用户输入得到严格遵守。
- 全部 workflow、runtime、plugin 和 skill validators 通过。
