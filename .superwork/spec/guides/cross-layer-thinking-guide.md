# Cross-Layer Thinking Guide

## Goal

Make contracts explicit when control moves between workflow skills.

## Checklist

- Define each phase input, output, stop condition, and default continuation
- Represent TDD as a callable implementation method, not a competing planning phase
- Keep phase transitions acyclic; method calls must return to their caller
- Update the contract, both participating skills, and scenario evals when a handoff changes
