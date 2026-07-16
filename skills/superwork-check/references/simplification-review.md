# Simplification Review

Use this review only after the changed behavior has a green targeted baseline.

## Scope

Inspect recently changed code and the smallest surrounding block needed to understand it. Do not expand into repository-wide cleanup.

## Review Signals

- unnecessary nesting or branches
- duplicated logic introduced by the change
- names that hide intent
- redundant variables, wrappers, or adapters
- responsibilities mixed inside one changed unit
- clever compactness that is harder to verify than explicit flow

Diff size increases review depth but does not require manufacturing a code change.

## Outcomes

- `no-change`: the changed code is already clear and consistent; continue to fresh verification
- `changed`: apply one behavior-preserving cleanup, rerun the targeted proof, then continue
- `blocked`: the proposed cleanup changes behavior or scope; return it to implementation or debugging

Never call the finalization skill again from this review.
