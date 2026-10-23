# Thinking Guides

## Scope

Shared rules for authoring, routing, packaging, and validating the Superwork skill bundle.

## Pre-Development Checklist

- Use runtime facts embedded by context discovery; read required candidates including global and applicable shared indexes
- Scope guidance to intended files with `get_context.py --files <path> ...` before editing when Git changes do not represent the task
- Load linked reference docs when their constraints apply; reuse unchanged guidance already available in the current context
- Read applicable `AGENTS.md` instructions before changing files
- Treat `skills/superwork-start/references/workflow-contract.json` as the machine-readable workflow contract
- Continue routed change work through final verification by default
- Keep only `superwork-start` implicitly invocable; all phase skills require explicit handoff
- Load every target `SKILL.md` once per run in full and pass the structured handoff fields declared by the workflow contract; reload on changed instructions, a new run/executor, or unavailable context
- Keep saved plans in one Markdown file and resume from the first unchecked `Task Status`
- Stop after analysis, design, or planning only when the user explicitly requests that outcome or prohibits later actions
- Preserve explicit read-only instructions during final verification

## Verification Checklist

- Require current verification evidence before any completion claim; reuse equivalent proof only while relevant inputs and environment remain unchanged
- Run `python3 -m unittest discover -s tests -p 'test_*.py' -v` unless an equivalent result is already current
- Run `python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v` unless an equivalent result is already current
- Run `python3 tests/evals/run_skill_evals.py --split validation --runs 3` when Codex CLI authentication is valid and trigger behavior changes
- Validate all eight skill folders and `.codex-plugin/plugin.json`
- Confirm removed skill names and the old workflow/state model do not reappear in active skill content

## Update Triggers

- A skill responsibility, handoff, or continuation rule changes
- The workflow contract or scenario schema changes
- Plugin or `agents/openai.yaml` requirements change
- A repeated workflow failure needs a durable regression rule
- A description, trigger boundary, route marker, or eval threshold changes
