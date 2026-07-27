---
name: superwork-debugging
description: Use this skill to diagnose a bug, regression, failing test, or unexpected behavior before repair. Reproduce the symptom, confirm one root cause with boundary evidence, then hand the smallest regression behavior to TDD and final verification.
---

# Superwork Debugging

## Purpose

Turn a symptom into a confirmed root cause and a precise regression behavior before any repair is attempted.

## Root-Cause Process

1. Read the applicable config, spec indexes, concrete rules, full error output, and recent relevant changes.
2. Reproduce the symptom reliably and record exact steps, expected behavior, actual behavior, and determinism.
3. Trace data and control flow across boundaries. Compare the broken path with a working pattern in the same repository.
4. State one hypothesis: “X is the root cause because Y evidence.”
5. Test the smallest observation that can confirm or reject that hypothesis.
6. Repeat with a revised single hypothesis only when evidence rejects the current one.

Do not propose or apply a repair before the root cause is confirmed.

## Repair Handoff

After confirmation:

- define the smallest regression behavior that must remain fixed
- read `../superwork-tdd/SKILL.md` in full and pass the structured handoff defined by `superwork-start` to create the failing regression proof and implement the repair
- do not stack unrelated fixes or opportunistic refactors
- after TDD returns green, confirm the original symptom is gone, then read `../superwork-check/SKILL.md` in full and pass the finalization handoff once

This skill does not write the regression test itself; TDD owns RED, GREEN, and REFACTOR. Debugging owns the evidence and hypothesis that make that RED trustworthy.

## Stop Conditions

- The issue is not reproducible and no boundary evidence isolates it.
- Required logs, credentials, data, or environment access are unavailable.
- Repeated rejected hypotheses indicate the current mental model is incomplete.
- The requested change is intentional new behavior rather than a bug.

Report the blocker and evidence instead of guessing a patch.
