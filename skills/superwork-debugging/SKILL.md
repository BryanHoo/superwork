---
name: superwork-debugging
description: Reproduces a bug, gathers boundary evidence, and confirms one root-cause hypothesis before repair. After confirmation it invokes `superwork-tdd`; it does not own implementation sequencing or final verification.
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
- invoke `superwork-tdd` to create the failing regression proof and implement the repair
- do not stack unrelated fixes or opportunistic refactors
- after TDD returns green, confirm the original symptom is gone and route once to `superwork-check`

This skill does not write the regression test itself; TDD owns RED, GREEN, and REFACTOR. Debugging owns the evidence and hypothesis that make that RED trustworthy.

## Stop Conditions

- The issue is not reproducible and no boundary evidence isolates it.
- Required logs, credentials, data, or environment access are unavailable.
- Repeated rejected hypotheses indicate the current mental model is incomplete.
- The requested change is intentional new behavior rather than a bug.

Report the blocker and evidence instead of guessing a patch.
