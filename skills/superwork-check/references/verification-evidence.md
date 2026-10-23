# Verification Evidence

Read this policy before reusing a verification result. A current result can satisfy both a TDD slice and its planned or final verification; a phase transition alone does not invalidate it.

## Evidence Ledger

For each result record the exact command and working directory, observed output and exit status, behavior and input scope covered, and when it ran relative to relevant edits. Include dependency, configuration, environment, and fixture state when they affect the result. Keep the ledger in the handoff; persist recovery notes with the task in an existing saved plan when pausing or changing executors.

## Reuse Conditions

Reuse a passing result only when all of these hold:

- It was observed in the current run and workspace, and its output remains available.
- It proves the requested behavior and expected signal with the same command scope, options, environment, and fixtures, or demonstrably equivalent coverage. A narrower test cannot satisfy a broader suite, build, lint, or typecheck requirement.
- It ran after the last relevant code, test, dependency, configuration, generated-input, or fixture change; no subsequent edit or environment change invalidated its inputs. Include transitive dependencies and other contributors' edits.
- No flaky failure, unresolved concern, or explicit request for a fresh rerun requires another execution.

If equivalence or input freshness cannot be established, rerun the affected check. Do not infer validity solely from a timestamp, unchanged HEAD, a task checkbox, or another agent's summary.

## Invalidation and Completion

After simplification or another relevant edit, rerun the affected proof. Run missing integration and broader checks when boundaries were crossed, plus all required project gates that lack valid evidence.

On a new run, executor, or workspace, use saved evidence as recovery context and re-establish the relevant verification baseline. Context compaction alone need not invalidate a result if its output and input-state evidence remain available; otherwise revalidate it.

Changing a spec requires validation of the final document and its links. Rerun code checks only if the changed spec affects executable behavior, acceptance requirements, or their inputs.

Report reused and newly executed checks separately, with observed results, reuse reasons, and remaining unverified surfaces. Failed, missing, or stale required evidence blocks completion.
