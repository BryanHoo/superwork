# Superwork 目录结构

| 路径 | 职责与约束 |
| --- | --- |
| `skills/superwork-*/SKILL.md` | 技能入口、触发范围与行为契约 |
| `skills/superwork-*/agents/openai.yaml` | 各技能的展示与默认提示元数据 |
| `skills/_shared/repository.py` | 多技能复用的工具链检测与 Git 改动收集 |
| `skills/superwork-init/scripts/`、`templates/` | 项目运行配置与分层规范生成 |
| `skills/superwork-start/scripts/get_context.py` | 项目事实、规范与候选任务上下文 |
| `skills/superwork-start/references/workflow-contract.json` | 通用工作流契约的仓库内来源 |
| `skills/superwork-executing-plans/scripts/preflight_plan.py` | 已保存计划的结构与接口预检 |
| `skills/superwork-check/scripts/` | 改动相关规范定位和规范更新工具 |
| `scripts/install.sh` | 安装全部技能及 `_shared`；可选 Claude 硬链接 |
| `tests/workflow/` | 上下文、计划护栏、场景与契约测试 |
| `tests/evals/` | 触发数据集、评估运行器及其单元测试 |
| `tests/test_install.py` | 独立安装、冲突与硬链接行为测试 |
| `skills/superwork-init/tests/` | 初始化布局与工具协作集成测试 |
| `.codex-plugin/plugin.json` | 插件分发元数据 |
| `.superwork/config.json`、`spec/` | 本项目事实与长期规范 |
| `.superwork/prd/`、`plans/` | 本项目设计和单文件任务计划 |

技能自身的脚本与模板留在该技能目录；跨技能工具放在 `_shared`。通用工作流仍由技能维护，禁止在 `.superwork/` 生成工作流副本、脚本或模板。设计与计划采用 `YYYY-MM-DD-<topic>.md` 文件名，临时任务进度不放入长期规范。

[README.md](../../../README.md) 与 [README.en.md](../../../README.en.md) 分别面向中文和英文读者，公共使用方式与命令变更时应同步核对。
