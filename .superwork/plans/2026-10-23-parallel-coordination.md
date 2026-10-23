# 并行协作实施计划

**Goal:** 用根目录协作说明与每任务独立 JSON，让 AI 感知并行影响、主动避让并在验证完成后清理自身登记。

**Suggested Spec Reads:**

- `.superwork/spec/shared/index.md` — 共享工具、技能与验证入口。
- `.superwork/spec/shared/quality-guidelines.md` — 配置兼容、真实验证及中文注释。
- `.superwork/spec/shared/directory-structure.md` — 技能资源与运行产物归属。
- `.superwork/spec/guides/cross-layer-thinking-guide.md` — 初始化、上下文与技能契约同步。
- `.superwork/spec/guides/code-reuse-thinking-guide.md` — 共享实现与单一事实来源。
- `.superwork/spec/guides/cross-platform-thinking-guide.md` — Python 3.11+ 和可移植路径。

**Architecture:** 通用操作留在技能包；`.superwork/parallel.md` 是允许项目定制的轻量协作约定，`.superwork/parallel/<id>.json` 是本地临时登记。共享模块扫描并校验摘要，小型 CLI 负责独立登记与所有者校验；AI 判断语义影响，不引入调度器或自动 worktree。

**Tech Stack:** Python 3.11+ 标准库、Markdown、JSON、unittest。

## Global Constraints

- 保持运行配置 `schemaVersion: 2` 和现有单文件串行计划契约。
- 不增加隐式技能入口；不改变技能描述的触发范围。
- 按需读取、复用交接上下文；所有直接写入入口也需经过协作检查。
- 只读任务不登记；失败和暂停保留记录；验证完成后只清理自身记录。
- 不自动提交、切换分支或创建 worktree；不覆盖人工协作说明或其他任务记录。
- 脚本留在技能包内；关键逻辑使用中文注释；使用 Python 3.11+ 的 python3 执行验证。

### Task 1: 实现独立任务登记与所有者保护

**Files:**

- Create: `skills/_shared/parallel.py`
- Create: `skills/superwork-start/scripts/parallel_task.py`
- Create: `tests/workflow/test_parallel.py`

**Interfaces:**

- Consumes: `ParallelTaskRecord`
- Produces: `ParallelContext`
- Produces: `ParallelTaskCLI`

**Behavior:**

- 缺失登记目录是空列表，损坏登记是显式错误；独立任务并发登记互不覆盖。
- 校验任务标识、所有者、相对写入范围、暂停原因；创建不覆盖已有记录，更新和清理只允许匹配的所有者。

**Stop Conditions:**

- 如果需要跨 worktree 自动共享或全局调度，停止扩大范围。

- [x] **Task Status:** completed

Run: `python3 -m unittest tests.workflow.test_parallel -v`

Expected: 独立登记、可见性、错误处理和清理归属的行为验证通过。

Evidence: 首轮 RED 为登记 CLI 尚不存在；实现后运行 `python3 -m unittest tests.workflow.test_parallel -v`，10 项通过。后续增加旧项目补充与忽略行为，连同上下文验证共 20 项通过；Python 3.14，当前仓库及临时项目，exit 0。

### Task 2: 接入上下文摘要与初始化协作产物

**Files:**

- Modify: `skills/superwork-start/scripts/get_context.py`
- Modify: `skills/superwork-init/scripts/bootstrap_superwork.py`
- Create: `skills/superwork-init/templates/parallel.md.tmpl`
- Modify: `skills/superwork-init/tests/test_layered_spec_layout.py`
- Modify: `tests/workflow/test_context_candidates.py`
- Modify: `tests/test_install.py`
- Modify: `.gitignore`
- Create: `.superwork/parallel.md`

**Interfaces:**

- Consumes: `ParallelContext`
- Produces: `SuperworkContext.parallel`
- Produces: `ProjectParallelGuide`

**Behavior:**

- 上下文只返回登记字段摘要，不自动读取其他计划正文；报告目录错误，发现本地协作说明路径。
- 初始化生成协作说明并保留人工内容；旧版 schema 2 项目按需补充该说明，不重新初始化配置与规范。
- 分发后的脚本可独立运行，临时登记不进入 Git 提交。

**Stop Conditions:**

- 不为新增协作产物升级配置版本，不覆盖历史任务或人工规范。

- [x] **Task Status:** completed

Run: `python3 -m unittest tests.workflow.test_context_candidates tests.test_install -v && python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v`

Expected: 摘要按需读取、初始化保留、兼容旧项目与独立安装验证通过。

Evidence: 新增上下文字段与初始化说明缺失时先得到预期 RED；接入后上下文及登记测试通过，初始化布局 22 项通过，安装分发 6 项通过。独立安装实际执行初始化、登记和清理，不依赖源码下载目录。

### Task 3: 接入技能生命周期并同步文档与契约

**Files:**

- Modify: `skills/superwork-start/SKILL.md`
- Create: `skills/superwork-start/references/parallel-coordination.md`
- Modify: `skills/superwork-executing-plans/SKILL.md`
- Modify: `skills/superwork-writing-plans/SKILL.md`
- Modify: `skills/superwork-brainstorming/SKILL.md`
- Modify: `skills/superwork-debugging/SKILL.md`
- Modify: `skills/superwork-tdd/SKILL.md`
- Modify: `skills/superwork-check/SKILL.md`
- Modify: `skills/superwork-init/SKILL.md`
- Modify: `skills/superwork-start/references/workflow-contract.json`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `.superwork/spec/shared/directory-structure.md`
- Modify: `.superwork/spec/shared/quality-guidelines.md`
- Modify: `tests/workflow/test_workflow_contract.py`

**Interfaces:**

- Consumes: `ParallelTaskCLI`
- Consumes: `SuperworkContext.parallel`
- Consumes: `ProjectParallelGuide`
- Produces: `ParallelCoordinationLifecycle`

**Behavior:**

- 用一个条件加载的共享参考维护生命周期，技能仅链接必要检查点，不复制完整规则或强制读取所有计划。
- 开始、扩大范围、公共修改与恢复时重新检查；不确定时暂停交叉部分，完成最终验证后清理自身登记。
- 同步使用说明、机器契约和持久目录规则，明确软协作边界与同目录可见性。

**Stop Conditions:**

- 不改变既有路由语义，不增加消息服务、任务调度或自动 Git 操作。

- [x] **Task Status:** completed

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v && python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v`

Expected: 全部项目验证通过，技能 frontmatter 与文档链接有效；未修改触发描述时不要求额外触发评估。

## 最终交接与验证

- 本次登记身份：`id=parallel-coordination-7af3`，`owner=codex-7af3`，`recordPath=.superwork/parallel/parallel-coordination-7af3.json`；所有最终检查通过后由本执行者清理。
- 公共变更：上下文增加 `parallel` 摘要；新增登记 CLI；初始化与旧 schema 2 项目可补充协作说明；写入技能共享按需读取和所有者清理契约。保留既有路由与单计划顺序执行。
- 最终运行环境：仓库根目录，Python 3.14.9，通过兼容的 `python3` 入口运行。登记行为覆盖真实独立进程、项目路径、所有者保护、暂停恢复、Git 忽略及损坏/不可读状态。
- `python3 -m unittest discover -s tests -p 'test_*.py' -v`：59 项通过，exit 0；包含新增目录权限回归。修复权限扫描后重新执行，输入为最终代码状态。
- `python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v`：22 项通过，exit 0。
- `quick_validate.py`：8 个技能全部通过；校验器所需 PyYAML 安装在临时虚拟环境中，没有增加项目依赖。
- 文档相对链接 35 项有效，变更 JSON 解析通过；`git diff --check` 通过。技能触发描述未变更，未运行不适用于本次触发边界的真实触发评估。
- 简化检查：`no-change`；规则集中在项目协作约定与一份操作参考，叶子技能只链接相应检查点，没有新增调度系统。
- 规范处理：`update`，已同步共享目录和质量规范。登记不是文件锁，不保证独立 clone/worktree 间的可见性；未声称完成跨平台实机多 AI 调度验证。
