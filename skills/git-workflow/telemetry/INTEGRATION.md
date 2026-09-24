# Integration guide: git-workflow

## Principle

Instrument high-value semantic boundaries only. Do not turn the target `SKILL.md` into an event-by-event logging checklist.

## Minimum semantic surface

1. Establish a run when the target skill is actually selected or when a target-owned entry script begins.
2. Emit `decision` only for branches that materially change workflow, safety, or verification.
3. Emit `verification`, `failure`, and `retry` around evidence-bearing checks.
4. Emit `user.correction` only when a correction is explicitly observed; never infer one.
5. Close the run with `run.finished` and an outcome.

The recorder prints the `run_id` on `start`. Pass that ID explicitly to later semantic events. Full commands may be supplied to `--command`; the recorder hashes them instead of storing them under the default policy.

## Wired instrumentation

`SKILL.md`'s `## Telemetry` section wires the following semantic events into
this skill's actual named sections (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before inspecting the repository | `run.started` | `task_category` (Trigger/exclusion operation class) |
| After Repository state (inspect before editing) | `decision` (`phase=inspect`) | `detached_head_or_active_operation`, `protected_branch_detected`, `preexisting_changes_present` |
| After Changes and staging (post-staging inspection) | `verification` (`phase=stage`) | `staged_scope`, `secrets_or_unrelated_found`, `whitespace_or_mode_anomalies` |
| Before Destructive local operations or Remote operations | `decision` (`phase=mutate`) | `operation_class`, `explicit_approval_obtained`, `force_with_lease_used` |
| Before returning the result | `run.finished` | `task_category`, `mutations_performed`, `conflicts_encountered` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's
runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11` — the Trigger/exclusion operation list (inspection, branching, synchronization, staging, merge, rebase, recovery) — became the `task_category` enum.
- `SKILL.md:32-33` — "Stop and report detached HEAD, unresolved conflicts, or an active merge/rebase/cherry-pick/revert/bisect" — became `detached_head_or_active_operation`.
- `SKILL.md:45-46` — "Do not work directly on a protected or default branch" — became `protected_branch_detected`.
- `SKILL.md:57-58` — "avoid `git add -A`, `git add .`, and `commit -a` in a dirty or mixed-scope worktree" — became `staged_scope`.
- `SKILL.md:63-64` — "Verify the staged snapshot contains no credentials, local environment files ... or unrelated changes" — became `secrets_or_unrelated_found`.
- `SKILL.md:81-89` — the Destructive local operations approval requirement — became `explicit_approval_obtained` for `operation_class=destructive_local`.
- `SKILL.md:101-103` — "Never use raw `--force`; an approved rewrite requires `--force-with-lease`" — became `force_with_lease_used`.

### Execution candidates

- None: this skill runs plain `git` commands rather than bundled scripts; their results are captured through the `inspect`/`stage`/`mutate` events above instead of per-command instrumentation.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. While a semantic run is open (between `start` and `finish`, or an auto-detected interruption), `hook_capture.py` attaches matching-session hook evidence to that run with `attribution: correlated` instead of leaving it stranded in the `ambient` bucket forever — this is what lets analysis join actual tool/command execution (exit codes, command classes, retries) to the skill's own decisions. Hook events outside any open run, or from a different session, remain `ambient` and are excluded from analysis by default.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
