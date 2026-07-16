# Thinking Guides

## Scope

Shared rules for authoring, routing, packaging, and validating the Superwork skill bundle.

## Pre-Development Checklist

- Read `.superwork/config.json`
- Read `.superwork/spec/shared/index.md`
- Read applicable `AGENTS.md` instructions before changing files
- Treat `skills/superwork-start/references/workflow-contract.json` as the machine-readable workflow contract
- Continue routed change work through final verification by default
- Keep only `superwork-start` implicitly invocable; all phase skills require explicit handoff
- Stop after analysis, design, or planning only when the user explicitly requests that outcome or prohibits later actions
- Preserve explicit read-only instructions during final verification

## Verification Checklist

- Run fresh verification before any completion claim
- Run `python3 -m unittest discover -s tests -p 'test_*.py' -v`
- Run `python3 -m unittest discover -s skills/superwork-init/tests -p 'test_*.py' -v`
- Validate all eight skill folders and `.codex-plugin/plugin.json`
- Confirm removed skill names and the old workflow/state model do not reappear in active skill content

## Update Triggers

- A skill responsibility, handoff, or continuation rule changes
- The workflow contract or scenario schema changes
- Plugin or `agents/openai.yaml` requirements change
- A repeated workflow failure needs a durable regression rule
