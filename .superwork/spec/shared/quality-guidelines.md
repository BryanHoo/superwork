# Shared Quality Guidelines

## Purpose

Capture workflow correctness and validation standards for this project.

## Rules

- Add a failing regression assertion before changing deterministic workflow behavior
- Keep runtime config generation and consumers on `schemaVersion: 3`
- Do not preserve compatibility with the removed `.superwork/workflow.md` route/state model
- Keep every `SKILL.md` focused and under 500 lines; move conditional detail to one-level references
- Start every skill description with user intent, state its trigger boundary, and keep it within 1024 characters
- Validate all skill frontmatter, all `agents/openai.yaml` policies, and the plugin manifest
- Maintain at least 20 balanced trigger eval queries split into fixed train and validation sets
- Run each live trigger query three times by default; treat timeouts, authentication failures, and nonzero exits as invalid runs rather than negative triggers, and abort the remaining suite after a deterministic authentication failure
- Keep static workflow scenarios classified as `happy-path` or `guardrail`; do not present them as trigger negatives
- Compare substantial skill revisions with a previous-skill baseline when a snapshot is available
- Keep the compact saved-plan template in `superwork-planning` synchronized with plan preflight through an end-to-end regression test
- Keep TDD mandatory for production behavior, bug fixes, runtime configuration, and build or CI behavior; use focused deterministic proofs for non-code-only changes
- Reuse TDD GREEN as task and completion evidence when it ran after the last relevant edit; do not rerun an equivalent proof
- Return spec indexes as sized, prioritized context candidates and load only the candidates supported by task evidence
- Run focused tests after simplification and after any spec artifact update
- Continue change requests through design, planning, implementation, and final verification without repeated phase gates
- Stop early or stay read-only only when the user input explicitly requests it
