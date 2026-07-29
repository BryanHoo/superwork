# Shared Quality Guidelines

## Purpose

Capture workflow correctness and validation standards for this project.

## Rules

- Add a failing regression assertion before changing deterministic workflow behavior
- Do not preserve compatibility with the removed `.superwork/workflow.md` route/state model
- Keep every `SKILL.md` focused and under 500 lines; move conditional detail to one-level references
- Start every skill description with user intent, state its trigger boundary, and keep it within 1024 characters
- Validate all skill frontmatter, all `agents/openai.yaml` policies, and the plugin manifest
- Maintain at least 20 balanced trigger eval queries split into fixed train and validation sets
- Run each live trigger query three times by default; treat timeouts, authentication failures, and nonzero exits as invalid runs rather than negative triggers
- Keep static workflow scenarios classified as `happy-path` or `guardrail`; do not present them as trigger negatives
- Compare substantial skill revisions with a previous-skill baseline when a snapshot is available
- Keep the complete task template in `superwork-writing-plans` synchronized with plan preflight through an end-to-end regression test; labels required by preflight must appear as exact standalone lines in that template
- Run fresh tests after simplification and after any spec artifact update
- Continue change requests through design, planning, implementation, and final verification without repeated phase gates
- Stop early or stay read-only only when the user input explicitly requests it
