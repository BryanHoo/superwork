# Superwork 平台与环境指南

## Python 运行环境

[共享检测模块](../../../skills/_shared/repository.py) 使用标准库 `tomllib`，运行脚本与测试需要 Python 3.11+，统一以 `python3` 调用。

本次初始化发现默认 `/usr/bin/python3` 为 3.9.6；本机可用的兼容入口位于 `/opt/homebrew/opt/python@3.14/libexec/bin/python3`。本机执行示例：

```bash
export PATH="/opt/homebrew/opt/python@3.14/libexec/bin:$PATH"
python3 --version
```

此路径仅是本机环境事实；其他机器应提供自身的 Python 3.11+，无需依赖 Homebrew。

## 安装与路径

- [scripts/install.sh](../../../scripts/install.sh) 面向 macOS / Linux，使用 Bash、curl 和 tar；同时支持下载后执行与管道执行。
- 默认技能目标为 `~/.agents/skills/`；`--claude` 在 `~/.claude/skills/` 创建逐文件硬链接，两处必须位于同一文件系统。
- `--prefix` 用于替换安装根目录；测试使用临时目录，避免污染真实用户安装。
- Python 工具用 `pathlib.Path` 处理路径，跨技能依赖按脚本位置定位 `skills/_shared/`，不能依赖源码仓库的绝对路径。
- CLI 示例从仓库根目录执行；保留含空格路径的正确引用，不以系统 Python 3.9 的结果判断项目逻辑。
