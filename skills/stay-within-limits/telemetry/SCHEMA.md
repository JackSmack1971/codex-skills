# Telemetry schema for stay-within-limits

Schema version: `skilltelemetry.event.v1`

Target fingerprint: `7d208766421dc884ff3ff8379847746ac6f78f9fad292bac5fde362c025485a1`

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

These fields populate the `evidence` object via the `recorder.py` calls
wired into `SKILL.md`'s Telemetry section. They measure this skill's core
job — checking real usage and throttling correctly — not just that the Core
Loop ran.

| Event | phase | Field | Type | Meaning | Why it matters for improvement |
|---|---|---|---|---|---|
| `run.started` | `start` | `task_category` | enum (`pre_wave_check`, `between_wave_check`, `resume_check`) | Which Core-Loop entry point triggered this check. | Lets an improvement agent see whether pauses/failures cluster around a particular check point (e.g. resume checks skipping the real re-check). |
| `verification` | `check_usage` | `usage_signal_source` | enum (`first_party_tool`, `status_command`, `dashboard_link`, `unknown`) | Which tier of the Usage Signals order was actually used. | Confirms the skill is preferring higher-priority signals rather than falling straight to `unknown`, per the stated signal order. |
| `verification` | `check_usage` | `five_hour_window_pct` / `weekly_window_pct` | number or null | The observed usage percentage per window, when available. | Tracks how close to the threshold real runs typically operate, useful for tuning the default threshold. |
| `verification` | `check_usage` | `threshold` | number | The threshold in effect for this run. | Confirms the 95%-only-with-a-direct-signal rule is being honored rather than a threshold being assumed. |
| `decision` | `throttle` | `action_taken` | enum (`continued`, `paused`) | Whether the loop stopped launching new work. | The primary calibration signal for whether throttling triggers when it should. |
| `decision` | `throttle` | `threshold_breached_window` | enum (`five_hour`, `weekly`, `none`) | Which window (if any) triggered the pause. | Distinguishes which usage window is actually driving pauses in practice. |
| `decision` | `throttle` | `wave_size` | integer | Number of parallel subagents in the wave that was throttled or allowed. | Flags whether the default 3-subagent throttle is being overridden and whether that correlates with breaches. |
| `operation` | `schedule_resume` | `wait_mechanism` | enum (`wake_tool`, `background_sleep`, `cron`) | Which wait mechanism was chosen per the Choosing The Wait Mechanism section. | Confirms wake/resume tools are preferred over polling per that section's rules. |
| `operation` | `schedule_resume` | `wait_seconds` / `chained_wakeups` | integer / boolean | The scheduled wait and whether it had to be chained past the 60-3600s clamp. | Long, frequently-chained waits indicate the window-clearing estimate is systematically off. |
| `run.finished` | `finish` | `action_taken`, `usage_signal_source`, `paused_count` | enum / integer | Final action and how many times this run paused. | Cross-run aggregation of how often work is interrupted and why. |
| `user.correction` | — | `original_action`, `correction` | enum (`continued`, `paused`) / enum (`paused_unnecessarily`, `failed_to_pause`) | A user later reporting the throttle decision was wrong in either direction. | The ground-truth signal for calibrating the threshold and signal-source preference — without it, `action_taken` counts only show what the skill decided, not whether it was right. |

An improvement agent should compare `action_taken` against
`usage_signal_source` (pauses based on `unknown` sources are lower-confidence
than first-party-tool pauses) and join `decision` (`phase=throttle`) against
later `user.correction` events to decide whether the default threshold or
signal-source ordering in `SKILL.md` needs revision.
