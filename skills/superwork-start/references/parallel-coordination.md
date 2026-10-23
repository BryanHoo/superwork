# Parallel Coordination

Read once per run before the first project write in a ready schema 2 project, including design, plan, code, test, or finalization edits. Reuse this reference and the caller's notice across skill handoffs. Read-only work inspects the context summary but never registers or cleans up another task. A missing runtime does not authorize initialization; keep the entry skill's existing missing-runtime policy.

## Read only what the decision needs

1. Inspect `parallel` from `get_context.py`. It contains notice summaries and read errors, not other plans' contents.
2. Read `.superwork/parallel.md` once for the current task; reload it if it changes. If absent in an existing schema 2 project, read [the bundled guide template](../../superwork-init/templates/parallel.md.tmpl); registration creates the missing project guide without reinitializing config or specs. Preserve project-authored content.
3. Compare intended files/directories **and** public behavior/resources with other notices. Open another task's plan and applicable linked rules only when overlap, dependencies, or uncertainty require them. Do not bulk-load all plans.

The project guide owns avoidance and pause decisions. Paths are literal and directory claims include descendants. Unknown or unreadable notices are not an empty board. Pause writes whose independence cannot be established; preserve others' records and edits. Notices are cooperative declarations, not locks or a scheduler, and are visible only in the same project directory.

## Register one notice for the whole outcome

Resolve `<start_skill_dir>` from this reference's parent skill directory, not the project's working directory. Execute the helper without reading its implementation. Choose a unique lowercase `id` and a stable `owner` token for this executor; record them in the handoff's `evidence.parallelTask`. Do not assume a platform exposes a session-id environment variable.

Before the first project edit:

```bash
python3 <start_skill_dir>/scripts/parallel_task.py register --root . \
  --id <unique-task-id> --owner <executor-token> --goal "<bounded outcome>" \
  --files <file-or-directory> <another-path> \
  --impact "<public interface, behavior or resource affected>" \
  --plan <existing-or-planned-plan-path>
```

Omit `--impact` when none applies and `--plan` when no saved plan is needed. Include planned design/plan/spec writes in the scope; the notice itself is managed metadata. A small task does not need an artificial plan. Registration fails rather than replacing an existing id and returns the latest board: inspect it before editing, including tasks registered concurrently.

Pass `{id, owner, recordPath}` under `evidence.parallelTask` through the existing handoff. When pausing or changing runs, persist that identity and recovery notes in the existing plan, if any. A nested skill reuses that notice. A resumed executor may reuse it only when identity and handoff are explicit and the original writer has stopped; never infer ownership from a similar goal or age. Otherwise leave the original notice and resolve the ownership conflict before overlapping writes.

## Refresh, narrow, or pause

Before scope expansion, public/shared edits, resumption, or finalization edits, get fresh summaries:

```bash
python3 <start_skill_dir>/scripts/parallel_task.py list --root .
```

Update your full intended scope **before** expanding it; `--files` and repeatable `--impact` replace their respective lists. Inspect the returned board again. Do not cache mutable task state across these checkpoints.

```bash
python3 <start_skill_dir>/scripts/parallel_task.py update --root . \
  --id <task-id> --owner <executor-token> --files <full-current-scope>
```

Continue independent parts when possible and note blocked parts in your plan. If no independent work remains, preserve the notice and update it with `--status paused --reason "<dependency and affected part>"`. Resume with `--status running` only after reading the current board and actual dependency implementation. A paused notice still reserves its declared scope; do not automatically expire or delete it. An interrupted process may leave a `running` notice: its timestamp alone does not prove abandonment.

## Finish after verification

After `superwork-check` passes required verification and artifact checks, persist actual shared changes and evidence in the existing plan so dependents can inspect them after the notice disappears. Then remove only this outcome's notice:

```bash
python3 <start_skill_dir>/scripts/parallel_task.py finish --root . \
  --id <task-id> --owner <executor-token>
```

The helper verifies the owner before removal. Do not release a caller's notice after an individual TDD slice or phase. On an explicitly bounded design/plan-only request, the owning skill may finish its own notice after validating that requested artifact. On failure or pause retain it and report the blocker; read-only verification never removes it. A cleanup failure must be reported rather than claiming the notice was released.
