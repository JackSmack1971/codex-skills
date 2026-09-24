# Telemetry schema for taste-engine

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `0688401853295cd66b4a43bb2d1cd092103efe162dff7df01e4281e36f2a66fa`

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
calls wired into `SKILL.md`'s Telemetry section. They are the fields an
improvement agent should read to judge and improve this specific skill.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | `"advisory_suggestion"` \| `"state_update"` | Whether the run returned a proposed patch/token block or an explicit approved/rejected state update. | Shows whether the skill defaults to advisory output regardless of what was actually requested. |
| `verification` | `validate` | `opt_in_confirmed` | boolean | Whether explicit opt-in was confirmed before acting. | A false value that still led to output would mean the "opt-in only" boundary was violated. |
| `verification` | `validate` | `profile_provided` | boolean | Whether a real, user-supplied JSON profile was present. | A false value should correlate with a stopped run, not a completed one — validates the "never invent a profile" rule. |
| `verification` | `validate` | `legacy_config_avoided` | boolean | Whether the run avoided writing to a legacy runtime config file. | Direct check of the "never write to a legacy runtime config file" rule. |
| `decision` | `select` | `signal_categories` | array of enum (`fonts`, `colors`, `layout_density`, `aesthetic_direction`) | Which signal categories were actually pulled from the profile. | Reveals whether the skill narrows to one category repeatedly instead of covering the profile's real breadth. |
| `decision` | `select` | `signals_selected_count` | integer | Number of signals chosen. | Outlier-low counts on a rich profile suggest under-use of available signal. |
| `run.finished` | `finish` | `output_mode` | enum (`advisory_patch`, `design_token_block`, `state_update`) | Which output form was returned. | Checked against `task_category`: a mismatch (e.g. `state_update` requested but `advisory_patch` returned) is a concrete defect. |
| `run.finished` | `finish` | `state_mutated` | boolean | Whether the profile file was actually mutated. | Should be true only when an explicit approved/rejected update was requested; any other pattern is a boundary violation. |
| `user.correction` | — | `correction` | enum (`signals_rejected`, `signals_modified`, `profile_disputed`) | How a person adjusted or dismissed the suggestion afterward. | The ground-truth signal for whether selected signals actually matched the user's taste. |

An improvement agent should watch the rate of `opt_in_confirmed=false` or
`profile_provided=false` runs that still produced output (should be ~zero),
compare `output_mode`/`state_mutated` against the requested `task_category`
for mismatches, and join `decision` events against later `user.correction`
events to see which `signal_categories` are most often rejected or modified.
