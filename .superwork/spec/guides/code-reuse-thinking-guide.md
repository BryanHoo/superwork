# Superwork 代码复用指南

## 已有复用边界

- [skills/_shared/repository.py](../../../skills/_shared/repository.py) 统一识别包管理器、验证命令和 Git 改动；初始化与上下文脚本应复用这些事实来源。
- [bootstrap_superwork.py](../../../skills/superwork-init/scripts/bootstrap_superwork.py) 从同技能目录下的 `templates/` 渲染配置与部分索引；模板占位符必须与调用参数保持一致。
- [yaml_subset.py](../../../tests/workflow/yaml_subset.py) 是工作流测试现有的 YAML 子集读取工具；扩展元数据检查前先确认它的支持范围。

## 检查清单

- 项目快速查找与语义检索优先使用 fast-context；语义查询使用英文。
- 增加包管理器或验证命令识别规则前，检查 `_shared/repository.py` 的已有实现与所有调用方。
- 调整模板后检查生成结果，避免模板与内联文案形成两套事实。
- 共享逻辑的关键分支和执行位置添加清楚、具体的中文注释。
