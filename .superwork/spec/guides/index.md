# Thinking Guides

## Scope

Shared rules for authoring, routing, packaging, and validating the Superwork skill bundle.

## Pre-Development Checklist

- Run `superwork-start/scripts/get_context.py` and use its embedded project facts
- Read only `candidateReads` marked `required`; load recommended spec guidance when task evidence makes it relevant
- Read applicable `AGENTS.md` instructions before changing files
- Treat `skills/superwork-start/references/workflow-contract.json` as the machine-readable workflow contract
- Continue routed change work through final verification by default
- Keep only `superwork-start` implicitly invocable; all phase skills require explicit handoff
- Load every target `SKILL.md` once per run and pass the structured handoff fields declared by the workflow contract
- Keep saved plans compact in one Markdown file and resume from the first unchecked `Task Status`
- Send clear development directly to TDD; use planning for material uncertainty, high risk, continuity, or an explicit plan request
- Stop after analysis, design, or planning only when the user explicitly requests that outcome or prohibits later actions
- Preserve explicit read-only instructions during final verification

## Verification Checklist

- Reuse a targeted TDD proof when it ran after the last relevant edit; run only missing, stale, or broader checks before completion
- `python3 -m unittest discover -s tests/evals -p 'test_*.py' -v`
- `python3 -m unittest discover -s tests/workflow -p 'test_*.py' -v`
- `python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v`
- Run `python3 tests/evals/run_skill_evals.py --split validation --runs 3` when Codex CLI authentication is valid and trigger behavior changes
- Validate all seven skill folders and `.codex-plugin/plugin.json`
- Confirm removed skill names and the old workflow/state model do not reappear in active skill content

## Update Triggers

- A skill responsibility, handoff, or continuation rule changes
- The workflow contract or scenario schema changes
- Plugin or `agents/openai.yaml` requirements change
- A repeated workflow failure needs a durable regression rule
- A description, trigger boundary, route marker, or eval threshold changes
