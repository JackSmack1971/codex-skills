# Telemetry schema for git-workflow

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `ae3ab7b1c75ce60719e7c0f6b0f3983c12b097ef9d524385fb7f907e09694940`

## Event classes

- `run.started`, `run.finished`
- `skill.invocation`
- `precondition`
- `decision`
- `operation`
- `verification`
- `failure`, `retry`
- `user.correction`, `agent.error`
- `eval.result`, `lesson.candidate`
- `hook.observation`, `usage`

## Attribution

- `semantic`: target-owned event with target fingerprint.
- `confirmed`: imported/correlated evidence known to exercise this skill.
- `correlated`: hook-observed execution evidence (tool calls, commands, exit codes) automatically attached to the semantic run that was open in the same session when it fired; included in analysis by default, but is a best-effort session-scoped join, not proof the tool call belongs to this skill's own logic.
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence outside any open run; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure whether the skill
actually inspected state before acting and gated risky operations the way
its own Repository state, Changes and staging, Destructive local
operations, and Remote operations sections require.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`inspection`, `branching`, `synchronization`, `staging`, `merge_or_rebase`, `recovery`) | Which Trigger/exclusion operation class this run performed. | Lets an improvement agent see whether one operation class (e.g. `recovery`) has a disproportionate failure or conflict rate. |
| `decision` | `inspect` | `detached_head_or_active_operation` | boolean | Whether a detached HEAD or an active merge/rebase/cherry-pick/revert/bisect was found. | Directly checks the Repository state rule to "stop and report" these conditions rather than proceeding. |
| `decision` | `inspect` | `protected_branch_detected` | boolean | Whether the current branch is protected or default. | Confirms the "do not work directly on a protected or default branch" rule is actually being checked. |
| `decision` | `inspect` | `preexisting_changes_present` | boolean | Whether pre-existing index or working-tree changes were found before editing. | Measures whether the skill is actually checking for changes it must preserve, not just proceeding blindly. |
| `verification` | `stage` | `staged_scope` | enum (`explicit_paths`, `explicit_hunks`, `broad_add_declined`) | How staging was scoped relative to the "avoid `git add -A`/`git add .`/`commit -a`" rule. | A run that never reports `explicit_paths`/`explicit_hunks` suggests broad staging is happening despite the rule. |
| `verification` | `stage` | `secrets_or_unrelated_found` | boolean | Whether the staged snapshot inspection caught credentials, env files, or unrelated changes. | Validates the post-staging inspection is substantive, not pro forma. |
| `verification` | `stage` | `whitespace_or_mode_anomalies` | boolean | Whether unexpected whitespace, line-ending, mode, rename, or binary changes were investigated. | Same rationale — confirms the Changes and staging checklist is actually being run. |
| `decision` | `mutate` | `operation_class` | enum (`destructive_local`, `remote_push_or_pr`, `routine`) | Which class of operation preceded this decision point. | Separates high-risk mutation classes from routine work when aggregating approval and outcome rates. |
| `decision` | `mutate` | `explicit_approval_obtained` | boolean | Whether explicit approval was obtained before a destructive or remote mutation. | The core safety signal — a `false` here on a `destructive_local`/`remote_push_or_pr` operation is a direct policy violation. |
| `decision` | `mutate` | `force_with_lease_used` | boolean or `"not_applicable"` | Whether an approved rewrite used `--force-with-lease` rather than raw `--force`. | Directly checks the "never use raw `--force`" rule. |
| `run.finished` | `finish` | `mutations_performed` / `conflicts_encountered` | boolean | Whether the run made repository changes and whether conflicts arose. | Aggregate view of run risk profile, useful for weighting which `task_category` values need the most scrutiny. |

An improvement agent should cross-tabulate `operation_class` against
`explicit_approval_obtained` and `force_with_lease_used` across runs to
confirm the Destructive local operations and Remote operations gates are
never bypassed, and watch `task_category` values with rising
`conflicts_encountered` rates for a needed Repository-state or
Branching-and-synchronization revision.
