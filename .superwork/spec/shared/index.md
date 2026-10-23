# Superwork 共享层规范

## 适用范围

`root/shared` 覆盖 `skills/`、`scripts/`、`tests/`、插件元数据和项目文档；本仓库没有独立子包或应用服务层。

| 规范 | 内容 |
| --- | --- |
| [目录结构](./directory-structure.md) | 技能、共享模块、测试与运行产物的归属 |
| [质量要求](./quality-guidelines.md) | 真实验证入口、契约与变更检查 |
| [公共指南](../guides/index.md) | 代码复用、边界与平台约束 |

配置使用 [schema version 2](../../config.json)，规范布局为 `layered/layer-root`，记录在 [.layout.json](../.layout.json)。
