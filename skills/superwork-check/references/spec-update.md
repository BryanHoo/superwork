# Spec Update Decision

Capture only durable project knowledge introduced or clarified by the completed change.

## Update Signals

- a new API, CLI, configuration, data, or cross-layer contract
- a stable validation or error behavior
- a recurring failure mode or important edge case
- a new required test category or verification point
- a new package or layer convention future work must preserve

Formatting, lockfiles, snapshots, mechanical renames, and implementation details without a lasting rule normally produce `no-update`.

## Outcomes

- `update`: add concrete rules, contracts, examples, or test notes to an existing spec
- `create`: create a focused spec only when no appropriate target exists, then link it from the relevant index
- `no-update`: state why the change adds no durable project knowledge

After `update` or `create`, verify links, required index references, and any documentation structure checks before final reporting.
