# Telemetry schema for using-git-worktrees

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `dda5a928653a833c78a668832fde902ff188ecb81e4b99a781bc5956e04a01ca`

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

These fields are populated in the `evidence` object by the `recorder.py`
calls wired into `SKILL.md`'s Telemetry section. This is a mechanical skill,
so the fields track the real branch/worktree decision points the bundled
`scripts/worktree.py` subcommands make, not generic outcome labels.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`create_worktree`, `verify_only`, `cleanup`) | Which real-world worktree task was requested. | Lets an improvement agent see whether failures cluster on one task type (e.g. cleanup is riskier than creation). |
| `verification` | `detect` | `worktrees_dir_status` | enum (`FOUND_BOTH`, `FOUND_DOTWORKTREES`, `FOUND_WORKTREES`, `NOT_FOUND`) | `worktree.py detect`'s own status value. | Directly measures how often the skill has to establish a worktree location from scratch vs. reuse an existing convention. |
| `verification` | `detect` | `ignore_status` | enum (`IGNORED`, `NOT_IGNORED`) | `worktree.py verify-ignore`'s own status value. | A rising `NOT_IGNORED` rate flags a repeated gap the skill should be catching before creating worktrees, not just reporting. |
| `decision` | `create` | `branch_collision` | boolean | Whether the requested branch already existed. | Confirms the "stop on branch collision" rule (Failure/stop) is actually being checked before creation, not assumed clear. |
| `decision` | `create` | `create_status` | enum (`CREATED`, `BRANCH_EXISTS`, `ERROR`, `not_a_git_repo`) | `worktree.py create`'s own status value. | The primary success signal for the create step; a rising `ERROR`/`not_a_git_repo` rate points at environment assumptions the skill is not checking early enough. |
| `verification` | `validate` | `setup_status` | enum (`SETUP_COMPLETE`, `skipped`, `error`) | Whether the project's existing setup command ran. | Separates "no setup needed" from "setup silently skipped." |
| `verification` | `validate` | `test_status` | enum (`PASS`, `FAIL`, `NO_TEST_RUNNER`) | Baseline test result in the new worktree. | The primary signal that the worktree is actually usable, not just created. |
| `verification` | `validate` | `baseline_failures` | integer | Count of baseline test failures found. | Distinguishes a clean worktree from one inheriting pre-existing failures. |
| `run.finished` | `finish` | `worktree_created` | boolean | Whether a worktree was actually created this run. | Separates `verify_only`/`cleanup` runs from `create_worktree` runs in aggregate stats. |

An improvement agent should watch the rate of `create_status: ERROR` or
`not_a_git_repo` against `task_category` to see whether the skill is being
invoked outside its stated preconditions, and track `test_status: FAIL` or
`NO_TEST_RUNNER` rates to judge whether the "run its existing baseline
tests" step in `SKILL.md` needs a stronger stop condition.
