# Superwork

简体中文 · [English](README.en.md)

Superwork 是一组面向 Codex 和 Claude Code 的开发技能，将设计、规划、实现与验证串成连续工作流，适用于功能开发、缺陷修复和已有计划的接续。它根据任务复杂度选择起点，以 TDD 推进代码变更，并将项目约束与任务进度保存在仓库中。

## 工作流

AI 通过 `superwork-start` 识别需求类型，自动选择对应的执行路径：

| 任务类型 | 执行路径 |
| --- | --- |
| 小范围、边界明确的变更 | [TDD](skills/superwork-tdd/SKILL.md) → 最终检查 |
| 需求明确的多文件变更 | [编写计划](skills/superwork-writing-plans/SKILL.md) → [执行计划](skills/superwork-executing-plans/SKILL.md) → 最终检查 |
| 需求、架构或取舍尚未确定 | [设计](skills/superwork-brainstorming/SKILL.md) → 编写计划 → 执行计划 → 最终检查 |
| 缺陷或回归 | [排查根因](skills/superwork-debugging/SKILL.md) → TDD 修复 → 最终检查 |
| 已保存的计划 | 预检 → 顺序执行未完成任务 → 最终检查 |
| 只读分析或评审 | 收集证据后直接答复 |

每个代码行为切片都使用 RED → GREEN → REFACTOR，规划深度不影响这一要求；文档或配置使用适合的结构、构建或内容检查。[最终检查](skills/superwork-check/SKILL.md)负责必要的简化、项目验证和长期规范更新。验证结果只有在相关输入与环境未改变时才可复用。

## 安装

适用于 macOS / Linux，需要 Bash、curl 和 tar。运行工作流脚本还需 Python 3.11+。

复制以下命令即可安装，无需克隆仓库：

```bash
curl -fsSL https://raw.githubusercontent.com/BryanHoo/superwork/main/scripts/install.sh | bash
```

[安装脚本](scripts/install.sh)会下载并将全部技能与 `_shared` 共享依赖复制到 `~/.agents/skills/`，随后清理临时文件。安装结果可独立运行。

使用 Claude Code 时，建议通过硬链接复用默认安装：

```bash
curl -fsSL https://raw.githubusercontent.com/BryanHoo/superwork/main/scripts/install.sh | bash -s -- --claude
```

`--claude` 会同时安装到默认目录，并在 `~/.claude/skills/` 下建立相同的目录结构，为其中的文件逐个创建硬链接。两处文件共享内容，目录需位于同一文件系统。

技能发现路径如下，`<name>` 例如 `superwork-start`：

| 工具 | 用户级：脚本安装位置 | 项目级：相对项目目录 |
| --- | --- | --- |
| Codex | `~/.agents/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` |
| Claude Code | `~/.claude/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` |

安装会保留其他技能，已有相同内容可重复使用；同名条目内容不同或链接关系不符时，在写入前报告冲突。两种工具的项目级发现规则见 [Codex 官方文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)与 [Claude Code 官方文档](https://code.claude.com/docs/en/skills#choose-where-skills-load)。

## 使用

### 1. 首次接入：每个项目初始化一次

仅在项目首次使用 Superwork 时，在项目根目录开启代理会话，执行 `superwork-init`：

```text
使用 superwork-init 初始化当前项目，核对真实的验证命令，并将项目约束补充到规范中。
```

Codex 中可用 `$superwork-init`，Claude Code 中可用 `/superwork-init`。

初始化会识别包管理器、包与分层，生成 `.superwork/config.json` 和规范目录。核对 `verification` 命令与生成的规范后，后续任务和新会话都会复用这些项目上下文，无需重复初始化。

### 2. 日常开发：直接描述需求

项目接入后，直接向 AI 说明目标、范围与验收标准：

```text
为订单列表增加按状态筛选。
沿用现有查询接口，保留分页行为，并验证空结果与切换筛选条件后的表现。
```

AI 会自动调用 `superwork-start`，读取项目上下文，根据需求路由到设计、规划、实现或排错流程，并继续推进到最终验证。日常使用只需描述需求。

### 3. 控制执行与恢复任务

需要限制执行范围或恢复已有任务时，在请求中直接写明：

| 目标 | 请求示例 |
| --- | --- |
| 只做设计 | 设计权限模型，只输出设计，不规划、不实现。 |
| 只写计划 | 为已确定的分页方案编写计划，不实现。 |
| 修复缺陷 | 刷新后筛选条件丢失，请排查并修复。 |
| 恢复任务 | 继续执行 `.superwork/plans/2026-10-23-order-filter.md`。 |
| 只读验收 | 检查当前变更是否满足验收标准，不修改文件。 |

恢复任务时提供实际计划路径。执行器先检查计划结构、规范引用和接口声明，再从第一个未勾选的 `Task Status` 按顺序继续。新会话会重新加载约束并建立验证证据，完成勾选不能替代当前检查。发现计划与实际接口、需求或验证条件不符时，先修正计划。

### 4. 多会话并行开发

在同一项目目录开启多个 AI 会话，分别描述各自功能即可。所有会话先读取当前任务摘要；准备写入时读取 `.superwork/parallel.md`，并在 `parallel/<id>.json` 登记自己的修改范围与公共影响。小任务无需额外编写计划，单个计划内部仍顺序执行。

读取分三层：先看登记摘要，再读项目协作约定，只有发现相关影响时才打开对方计划与对应规范。扩大范围、修改公共部分、恢复任务和最终检查需要写入时，会重新检查最新登记。

- 范围独立时继续；交叉部分由一个任务负责，其他任务优先推进独立部分。
- 共享接口、数据库结构、依赖或测试资源也计入影响，不能只比较文件名。
- 无法确认归属或兼容性时，暂停受影响部分并记录原因；暂停记录仍保留其修改范围。
- 完成验证并把公共变更及证据留在计划后，AI 只删除自己的登记。失败、中断或暂停时保留；只读验收不替其他任务清理。

登记使用 `id`、`owner`、`goal`、`status`、`writePaths`、`sharedImpact`、`plan`、`reason`、`updatedAt`。其中 `writePaths` 是项目相对的明确文件或目录，`status` 为 `running` 或 `paused`。登记工具检查记录归属，使用每任务独立文件避免覆盖其他记录，并为临时 JSON 创建本地忽略规则。

旧版 schema 2 项目首次登记会补充缺失的协作说明，保留现有人工内容，无需重新初始化。此机制是文档协作约定，不是文件锁，不自动停止其他 AI；不同 clone 或 worktree 的登记不自动共享。

## 项目文件与约束

```text
.superwork/
├── config.json   # 项目事实：包管理器、包与分层、产物路径、验证命令
├── parallel.md   # 项目可定制的并行协作约定，写入任务必读
├── parallel/     # 本地临时登记：每个任务一个 JSON，完成后自行清理
├── spec/         # 长期规范：公共指南、分层规则及索引
├── prd/          # 设计文档
└── plans/        # 可恢复的单文件计划与任务状态
```

- `config.json` 当前使用 `schemaVersion: 2`。项目工具链变化后，同步维护包信息和 `verification` 命令。
- `spec/` 保存可长期复用的接口约定、目录规则和验证要求，通过索引关联；任务临时进度放在计划中。
- `parallel.md` 保存协作约定；`parallel/` 仅保存当前任务影响，不代替计划，也不提交临时登记。
- 计划使用 `YYYY-MM-DD-<topic>.md`，每项任务声明文件、输入输出接口、预期行为、停止条件与验证命令。手工编辑时遵循[计划模板](skills/superwork-writing-plans/SKILL.md#exact-task-template)。
- 配置版本不兼容时，明确请求修复现有 `.superwork/` 后再继续。

## 验证 Superwork 本身

在本仓库根目录运行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v
```

若修改技能描述或触发边界，另需有效的 Codex CLI 认证并运行真实触发评估：

```bash
python3 tests/evals/run_skill_evals.py --split validation --runs 3
```
