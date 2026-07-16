# Code Reuse Thinking Guide

## Goal

Prevent workflow rules and deterministic parsing logic from diverging across skills.

## Checklist

- Keep generic routing in `workflow-contract.json`, not repeated prose in every phase skill
- Let each script own one context: start context, plan preflight, check context, or spec targeting
- Move detailed finalization rules into one-level `references/` files instead of new triggerable skills
- Add a regression test before duplicating or relocating deterministic parser behavior
