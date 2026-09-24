# Telemetry schema for writing-plans

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `0600e8928142fcec83644bbe9f88663696bb39f5d5e87f935e3a74cfe21ba8d0`

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
calls wired into `SKILL.md`'s Telemetry section. Several fields mirror
`scripts/plan_tools.py`'s own JSON output directly, since that script already
defines this skill's ground truth for validation.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`plan`, `task_list`, `implementation_design`) | Which kind of request the plan was written for. | Lets an improvement agent see whether `task_count`/`placeholder_hit_count` patterns differ by request type. |
| `decision` | `draft` | `sections_included` | array of enum (`goal`, `architecture`, `stack`, `files`, `test_first_steps`, `commands`, `expected_results`, `commit_boundary`) | Which of the required plan sections were actually written. | Directly measures whether the plan is "independently executable" per the required-sections list, or is missing one silently. |
| `decision` | `draft` | `scope_rejected` | boolean | Whether the request was rejected as combining unrelated subsystems. | Confirms the "reject specs that combine unrelated subsystems" rule is actually exercised, not just stated. |
| `verification` | `validate` | `validate_status` | enum (`PASS`, `FAIL`) | `plan_tools.py validate`'s own status field. | The primary quality gate for this skill; a `FAIL` that was not followed by a `retry` event is a process violation. |
| `verification` | `validate` | `placeholder_hit_count` | integer | `plan_tools.py validate`'s own placeholder-hit count. | Directly measures how often generated plans still contain forbidden placeholders (`TBD`, `TODO`, etc.) before repair. |
| `verification` | `validate` | `task_count` | integer | `plan_tools.py validate`'s own task count. | Outlier-low counts on a non-trivial feature suggest an under-specified plan; trend over time shows drift in plan granularity. |
| `verification` | `save` | `save_status` | enum (`SAVED`, `error`) | `plan_tools.py save`'s own outcome. | Separates plan-quality issues from save-path/filesystem issues. |
| `verification` | `save` | `output_location` | enum (`default`, `custom`) | Whether the plan was saved to `docs/superpowers/plans/` or a user-given location. | Tracks how often the default location convention is actually used vs. overridden. |
| `run.finished` | `finish` | `task_count` / `placeholder_hit_count` | integer | Final validated counts at close. | The closing snapshot an improvement agent aggregates across runs without replaying each `verification` event. |

An improvement agent should aggregate `placeholder_hit_count` before-repair
rates (from `validate`-phase events) to see whether plan drafting is
producing avoidable rework, watch `sections_included` for runs missing a
required section, and compare `task_count` distribution against
`task_category` to judge whether the Workflow guidance in `SKILL.md` needs
revision for a particular request type.
