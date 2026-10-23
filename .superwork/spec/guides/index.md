# Superwork 公共指南

## 项目范围

本仓库发布 Markdown 技能、Python 辅助脚本和 Bash 安装脚本。包管理器为 `none`，包与分层为 `root/shared`；没有 Node 包、前端应用或后端服务。

| 指南 | 使用场景 |
| --- | --- |
| [代码复用](./code-reuse-thinking-guide.md) | 修改共享检测器、技能脚本和测试工具 |
| [边界契约](./cross-layer-thinking-guide.md) | 修改配置、上下文、计划格式或安装产物 |
| [平台与环境](./cross-platform-thinking-guide.md) | 运行 Python 工具、修改 Bash 安装脚本 |
| [共享层索引](../shared/index.md) | 查询目录归属与验证要求 |

## 项目验证命令

从仓库根目录、在 Python 3.11+ 环境中执行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v
```

更改技能描述或触发边界时，另外执行真实触发评估；要求有效的 Codex CLI 认证：

```bash
python3 tests/evals/run_skill_evals.py --split validation --runs 3
```

验证入口与依赖要求以 [项目 README](../../../README.md) 为依据；项目配置见 [config.json](../../config.json)。
