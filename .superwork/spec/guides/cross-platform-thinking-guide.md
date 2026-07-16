# Cross-Platform Thinking Guide

## Goal

Keep tooling and scripts understandable across local machines and CI.

## Checklist

- Prefer `python3` for Python scripts
- Prefer portable paths and repository-relative commands
- Derive repository roots from `Path(__file__)`; never commit user-specific absolute paths
- Keep core `SKILL.md` instructions portable and isolate Codex policy in `agents/openai.yaml`
- Use only Python3 standard-library dependencies in bundled runtime scripts
