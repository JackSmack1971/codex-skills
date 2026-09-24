# Telemetry schema for testing-qa

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `f3a8333959ec1a0cc89dc4a3bb7c49a62c66f89fc9a75653c9e18a3f720c0474`

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
- `candidate`: likely related but not proven.
- `ambient`: surrounding Codex lifecycle evidence; do not treat as causal.

## Privacy default

The default `metadata` policy stores hashes/classes/counts rather than raw prompts, commands, or tool-response bodies. Session and turn identifiers are locally salted before storage.

## Tailored signals for this skill

These fields are populated in the `evidence` object by the `recorder.py`
calls wired into `SKILL.md`'s Telemetry section. They measure whether this
skill actually chooses a proportionate test strategy and honestly reports
what it found, not just that a run happened.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`unit`, `integration`, `browser`, `performance`, `security`, `release_quality`, `mixed`) | Primary QA focus for this run. | Lets an improvement agent check whether one focus area systematically gets thinner coverage or more `unknown` outcomes. |
| `decision` | `scope` | `pyramid_layers` | array of enum (`unit`, `integration`, `e2e_browser`) | Which layers of the skill's own test pyramid were selected. | Detects drift toward always running the same layer regardless of risk, contradicting the "smallest strategy that proves the behavior" instruction. |
| `decision` | `scope` | `risk_level` | enum (`low`, `medium`, `high`) | Assessed risk driving the pyramid choice. | Lets an improvement agent check whether `pyramid_layers` actually scales with `risk_level`. |
| `verification` | `execute` | `commands_run` | array of enum (`test`, `lint`, `typecheck`, `security`, `build`, `browser`) | Which documented project commands were actually run. | Verifies the skill reuses the project's existing tooling rather than skipping categories silently. |
| `verification` | `execute` | `commands_unavailable` | integer | Count of commands reported as UNKNOWN rather than run. | Distinguishes "tooling genuinely missing" from silent skips; a rising count without matching `overall_status: unknown` is a red flag. |
| `verification` | `execute` | `regressions_found` / `pre_existing_failures` | integer | Failures classified as new regressions vs. pre-existing. | A persistent zero for `pre_existing_failures` on a mature codebase suggests the separation step is not actually being performed. |
| `verification` | `final_check` | `acceptance_criteria_checked`, `error_paths_checked`, `security_boundaries_checked`, `accessibility_checked`, `docs_checked` | boolean | Whether each of step 5's required pre-completion checks was performed. | Directly measures whether the skill follows its own completion checklist instead of treating step 5 as pro forma. |
| `run.finished` | `finish` | `overall_status` | enum (`pass`, `fail`, `unknown`) | Final QA verdict for the run. | The primary outcome signal; its distribution combined with `user.correction` reveals false-pass or false-unknown rates. |
| `user.correction` | — | `original_status`, `correction` | string | A maintainer later overturning this run's verdict. | The ground-truth signal for calibration — without it, `overall_status` only shows what the skill claimed, not whether it was right. |

An improvement agent should join `run.finished` events against later
`user.correction` events (same `run_id`) to estimate a false-pass rate per
`task_category`, and watch whether `pyramid_layers` and `commands_run`
actually track `risk_level` and the categories named in this skill's own
description — persistent mismatches point at a `SKILL.md` revision.
