<p align="center">
<picture>
<source srcset="assets/superwork.png" media="(prefers-color-scheme: dark)">
<source srcset="assets/superwork.png" media="(prefers-color-scheme: light)">
<img src="assets/superwork.png" alt="Superwork Logo" width="500" style="image-rendering: -webkit-optimize-contrast; image-rendering: crisp-edges;">
</picture>
</p>

<p align="center">
<strong>A multi-platform AI coding framework that rules</strong><br/>
<sub>Supports Claude Code and Codex.</sub>
</p>

<p align="center">
<a href="./README_CN.md">简体中文</a> •
<a href="https://docs.trysuperwork.app/">Docs</a> •
<a href="https://docs.trysuperwork.app/guide/ch02-quick-start">Quick Start</a> •
<a href="https://docs.trysuperwork.app/guide/ch13-multi-platform">Supported Platforms</a> •
<a href="https://docs.trysuperwork.app/guide/ch08-real-world">Use Cases</a>
</p>

<p align="center">
<a href="https://www.npmjs.com/package/@bryanhu/superwork"><img src="https://img.shields.io/npm/v/@bryanhu/superwork.svg?style=flat-square&color=2563eb" alt="npm version" /></a>
<a href="https://www.npmjs.com/package/@bryanhu/superwork"><img src="https://img.shields.io/npm/dw/@bryanhu/superwork?style=flat-square&color=cb3837&label=downloads" alt="npm downloads" /></a>
<a href="https://github.com/mindfold-ai/Superwork/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-16a34a.svg?style=flat-square" alt="license" /></a>
<a href="https://github.com/mindfold-ai/Superwork/stargazers"><img src="https://img.shields.io/github/stars/mindfold-ai/Superwork?style=flat-square&color=eab308" alt="stars" /></a>
<a href="https://docs.trysuperwork.app/"><img src="https://img.shields.io/badge/docs-trysuperwork.app-0f766e?style=flat-square" alt="docs" /></a>
<a href="https://discord.com/invite/tWcCZ3aRHc"><img src="https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord" /></a>
<a href="https://github.com/mindfold-ai/Superwork/issues"><img src="https://img.shields.io/github/issues/mindfold-ai/Superwork?style=flat-square&color=e67e22" alt="open issues" /></a>
<a href="https://github.com/mindfold-ai/Superwork/pulls"><img src="https://img.shields.io/github/issues-pr/mindfold-ai/Superwork?style=flat-square&color=9b59b6" alt="open PRs" /></a>
<a href="https://deepwiki.com/mindfold-ai/Superwork"><img src="https://img.shields.io/badge/Ask-DeepWiki-blue?style=flat-square" alt="Ask DeepWiki" /></a>
<a href="https://chatgpt.com/?q=Explain+the+project+mindfold-ai/Superwork+on+GitHub"><img src="https://img.shields.io/badge/Ask-ChatGPT-74aa9c?style=flat-square&logo=openai&logoColor=white" alt="Ask ChatGPT" /></a>
</p>

<p align="center">
<img src="assets/superwork-demo.gif" alt="Superwork workflow demo" width="100%">
</p>

## Why Superwork?

| Capability | What it changes |
| --- | --- |
| **Auto-injected specs** | Write conventions once in `.superwork/spec/`, then let Superwork inject the relevant context into each session instead of repeating yourself. |
| **Task-centered workflow** | Keep PRDs, implementation context, review context, and task status in `.superwork/tasks/` so AI work stays structured. |
| **Parallel agent execution** | Run multiple AI tasks side by side with git worktrees instead of turning one branch into a traffic jam. |
| **Project memory** | Journals in `.superwork/workspace/` preserve what happened last time, so each new session starts with real context. |
| **Team-shared standards** | Specs live in the repo, so one person’s hard-won workflow or rule can benefit the whole team. |
| **Multi-platform setup** | Bring the same Superwork structure to Claude Code and Codex instead of rebuilding your workflow per tool. |

## Quick Start

```bash
# 1. Install Superwork
npm install -g @bryanhu/superwork@latest

# 2. Initialize in your repo
superwork init -u your-name

# 3. Or initialize with the platforms you actually use
superwork init --claude --codex -u your-name
```

- `-u your-name` creates `.superwork/workspace/your-name/` for personal journals and session continuity.
- Platform flags can be mixed and matched. Current options include `--claude` and `--codex`.
- For platform-specific setup, entry commands, and upgrade paths, use the docs:
  [Quick Start](https://docs.trysuperwork.app/guide/ch02-quick-start) •
  [Supported Platforms](https://docs.trysuperwork.app/guide/ch13-multi-platform) •
  [Real-World Scenarios](https://docs.trysuperwork.app/guide/ch08-real-world)

### Default Workflow Entrypoints

After initialization, the lightweight day-to-day flow is:

- Claude Code small changes: `/superwork:before-dev` -> `/superwork:tdd-core` -> `/superwork:check`
- Claude Code planned work: `/superwork:brainstorm` -> `/superwork:spec-plan` -> `/superwork:execute-plan`
- Claude Code bugs: `/superwork:debug-root-cause` -> `/superwork:tdd-core` -> `/superwork:break-loop`
- Codex small changes: `$before-dev` -> `$tdd-core` -> `$check`
- Codex planned work: `$brainstorm` -> `$spec-plan` -> `$execute-plan`
- Codex bugs: `$debug-root-cause` -> `$tdd-core` -> `$break-loop`

Use `/superwork:finish-work` before commit in either tool.

## Use Cases

### Teach AI your project once

Put coding standards, file structure rules, review habits, and workflow preferences into Markdown specs. Superwork loads the relevant pieces automatically so you do not have to re-explain the repo every time.

### Run multiple AI tasks in parallel

Use git worktrees and Superwork task structure to split work cleanly across agents. Different tasks can move forward at the same time without stepping on each other’s branches or local state.

### Turn project history into usable memory

Task PRDs, checklists, and workspace journals make previous decisions available to the next session. Instead of starting from blank context, the next agent can pick up where the last one left off.

### Keep one workflow across tools

If your team uses more than one AI coding tool, Superwork gives you one shared structure for specs, tasks, and process. The platform-specific wiring changes, but the workflow stays recognizable.

## How It Works

Superwork keeps the core workflow in `.superwork/` and generates the platform-specific entry points you need around it.

```text
.superwork/
├── spec/                    # Project standards, patterns, and guides
├── tasks/                   # Task PRDs, context files, and status
├── workspace/               # Journals and developer-specific continuity
├── workflow.md              # Shared workflow rules
└── scripts/                 # Utilities that power the workflow
```

Depending on the platforms you enable, Superwork also creates tool-specific integration files such as `.claude/`, `AGENTS.md`, `.agents/`, and `.codex/`. For Codex, Superwork installs both project skills under `.agents/skills/` and project-scoped config/custom agents under `.codex/`.

Platform entrypoints stay aligned across tools:

- Claude Code gets slash commands such as `/superwork:spec-plan`, `/superwork:execute-plan`, `/superwork:tdd-core`, and `/superwork:debug-root-cause`.
- Codex gets the matching project skills `$spec-plan`, `$execute-plan`, `$tdd-core`, and `$debug-root-cause`.
- Both tools still share the same `.superwork/` task model, specs, journals, and workflow rules.

At a high level, the workflow is simple:

1. Define standards in specs.
2. Start or refine work from a task PRD.
3. Let Superwork inject the right context for the current task.
4. Use checks, journals, and worktrees to keep quality and continuity intact.

## Spec Templates & Marketplace

Specs ship as empty templates by default — they are meant to be customized for your project's stack and conventions. You can fill them from scratch, or start from a community template:

```bash
# Fetch templates from a custom registry
superwork init --registry https://github.com/your-org/your-spec-templates
```

Browse available templates and learn how to publish your own on the [Spec Templates page](https://docs.trysuperwork.app/templates/specs-index).

## What's New

- **v0.3.6**: task lifecycle hooks, custom template registries (`--registry`), parent-child subtasks, fix PreToolUse hook for CC v2.1.63+.
- **v0.3.5**: hotfix for delete migration manifest field name.
- **v0.3.4**: record-session task awareness and platform maintenance updates.
- **v0.3.1**: background watch mode for `superwork update`, improved `.gitignore` handling, docs refresh.
- **v0.3.0**: platform support expanded from 2 to 10, Windows compatibility, remote spec templates, `/superwork:brainstorm`.

## FAQ

<details>
<summary><strong>How is this different from <code>CLAUDE.md</code> or <code>AGENTS.md</code>?</strong></summary>

Those files are useful, but they tend to become monolithic. Superwork adds structure around them: layered specs, task context, workspace memory, and platform-aware workflow wiring.

</details>

<details>
<summary><strong>Is Superwork only for Claude Code?</strong></summary>

No. Superwork currently supports Claude Code and Codex. The detailed setup and entry command for each tool lives in the supported platforms guide.

</details>

<details>
<summary><strong>Do I have to write every spec file manually?</strong></summary>

No. Many teams start by letting AI draft specs from existing code and then tighten the important parts by hand. Superwork works best when you keep the high-signal rules explicit and versioned.

</details>

<details>
<summary><strong>Can teams use this without constant conflicts?</strong></summary>

Yes. Personal workspace journals stay separate per developer, while shared specs and tasks stay in the repo where they can be reviewed and improved like any other project artifact.

</details>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mindfold-ai/Superwork&type=Date)](https://star-history.com/#mindfold-ai/Superwork&Date)

## Community & Resources

- [Official Docs](https://docs.trysuperwork.app/) - Product docs, setup guides, and architecture
- [Quick Start](https://docs.trysuperwork.app/guide/ch02-quick-start) - Get Superwork running in a repo fast
- [Supported Platforms](https://docs.trysuperwork.app/guide/ch13-multi-platform) - Platform-specific setup and command details
- [Real-World Scenarios](https://docs.trysuperwork.app/guide/ch08-real-world) - See how the workflow plays out in practice
- [Changelog](https://docs.trysuperwork.app/changelog/v0.3.6) - Track current releases and updates
- [Tech Blog](https://docs.trysuperwork.app/blog) - Product thinking and technical writeups
- [GitHub Issues](https://github.com/mindfold-ai/Superwork/issues) - Report bugs or request features
- [Discord](https://discord.com/invite/tWcCZ3aRHc) - Join the community

<p align="center">
<a href="https://github.com/mindfold-ai/Superwork">Official Repository</a> •
<a href="https://github.com/mindfold-ai/Superwork/blob/main/LICENSE">AGPL-3.0 License</a> •
Built by <a href="https://github.com/mindfold-ai">Mindfold</a>
</p>
