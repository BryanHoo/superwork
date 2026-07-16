# Shared Quality Guidelines

## Purpose

Capture workflow correctness and validation standards for this project.

## Rules

- Add a failing regression assertion before changing deterministic workflow behavior
- Do not preserve compatibility with the removed `.superwork/workflow.md` route/state model
- Keep every `SKILL.md` focused and under 500 lines; move conditional detail to one-level references
- Validate all skill frontmatter, all `agents/openai.yaml` policies, and the plugin manifest
- Maintain at least 20 positive and 20 negative workflow scenarios
- Run fresh tests after simplification and after any spec artifact update
- Continue change requests through design, planning, implementation, and final verification without repeated phase gates
- Stop early or stay read-only only when the user input explicitly requests it
