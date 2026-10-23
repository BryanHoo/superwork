# Superwork 质量要求

## 验证入口

验证命令记录在 [config.json](../../config.json)，从仓库根目录使用 Python 3.11+ 执行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v
```

第一条覆盖安装、工作流和评估运行器单元测试；第二条覆盖初始化布局与工具协作。修改技能描述或触发边界时，按 [公共指南](../guides/index.md) 另跑真实触发评估；运行器单元测试不代表真实触发评估已通过。

## 项目契约检查

- 配置保持 `schemaVersion: 2`，包管理器、包与分层、产物路径及验证命令均反映真实仓库。
- `get_context.py --root . --format json` 应识别运行时为 `ready`；输出中的规范路径必须存在。
- 初始化或修复后解析所有 JSON，检查 Markdown 相对链接及 `spec/.layout.json`；保证 `spec/`、`prd/`、`plans/` 存在。
- `.superwork/` 只承载项目事实与持久知识，不包含通用工作流副本；历史人工内容和用户既有改动应保留。
- 检测失败应保留明确错误状态，不能当作空改动或验证成功。
- 验证结论注明实际命令和结果，不把可用命令、旧证据或测试夹具当作本次运行证据。

## 编写与提交

- 关键逻辑、边界处理和执行位置使用清晰、详细的中文注释，说明真实约束。
- 提交消息采用 `<type>(<scope>): <subject>`，scope 必填，subject 使用简体中文祈使句。
- 文档与配置变更采用结构、链接及内容检查；行为变更更新有意义的回归验证。
