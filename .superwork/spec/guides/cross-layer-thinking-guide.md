# Superwork 边界契约指南

## 当前边界

本项目使用 `shared` 单层规范。需要同步核对的边界是技能说明、Python 工具输出、配置、规范索引和测试，不涉及应用前后端通信。

| 事实来源 | 消费方与检查点 |
| --- | --- |
| [config.json.tmpl](../../../skills/superwork-init/templates/config.json.tmpl) | 初始化产出 `schemaVersion: 2`；`get_context.py` 与 `check_specs.py` 读取配置 |
| [workflow-contract.json](../../../skills/superwork-start/references/workflow-contract.json) | 工作流测试校验技能声明、阶段转换和交接契约 |
| [superwork-writing-plans/SKILL.md](../../../skills/superwork-writing-plans/SKILL.md) | `preflight_plan.py` 预检单文件计划及任务声明 |
| [plugin.json](../../../.codex-plugin/plugin.json) | 插件通过 `./skills/` 分发技能；安装脚本同时复制 `_shared` |

## 检查清单

- 修改 JSON 输出时，检查字段、错误状态、CLI 参数及下游测试。
- 配置仅保存项目事实；通用工作流保留在 `skills/`，不复制到 `.superwork/`。
- 生成器和修复操作保留已有人工编写的规范、设计与计划。
- 修改技能接口时同步核对 `agents/openai.yaml`、工作流契约与相关测试。
