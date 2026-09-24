# Integration guide: stay-within-limits

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
this skill's actual Core Loop steps (superseding the generic candidate scan
below, which is kept only as provenance for why these points were chosen).

| SKILL.md step | Event | Tailored evidence fields |
|---|---|---|
| Before Core Loop step 1 | `run.started` | `task_category` (pre-wave vs. between-wave vs. resume check) |
| After step 3 (check current usage) | `verification` (`phase=check_usage`) | `usage_signal_source`, `five_hour_window_pct`, `weekly_window_pct`, `threshold` |
| After step 4 (decide to stop/continue) | `decision` (`phase=throttle`) | `action_taken`, `threshold_breached_window`, `wave_size` |
| After scheduling a resume (Pausing And Resuming) | `operation` (`phase=schedule_resume`) | `wait_mechanism`, `wait_seconds`, `chained_wakeups` |
| Before ending the turn (after Reporting) | `run.finished` | `action_taken`, `usage_signal_source`, `paused_count` |
| When a user later disputes the pause/continue call | `user.correction` | `original_action`, `correction` |

See `SCHEMA.md`'s "Tailored signals for this skill" section for field types
and why each one matters to an improvement agent reviewing this skill's runs.

### Static candidates from the target (provenance only)

These are the inspection hints the fields above were derived from, not
additional instrumentation to add.

- `SKILL.md:11-12` — "Check before launching substantial work and between bounded waves" and the 95%-only-with-a-direct-signal rule — became `task_category` and `threshold`.
- `SKILL.md:17` — "Default to at most 3 parallel subagents" — became `wave_size`.
- `SKILL.md:21-24` — the usage-check, threshold-comparison, and re-check-on-resume steps — became the `check_usage` and `throttle` phase fields.
- `SKILL.md:29-33` — the Usage Signals priority order (first-party tool, `/status`, dashboard) and `UNKNOWN` fallback — became the `usage_signal_source` enum.
- `SKILL.md:49-57` — the `min(3600, secondsUntilWindowClears)` wake rule and 60-3600s clamp/chaining — became `wait_seconds`/`chained_wakeups`.
- `SKILL.md:70-76` — the Choosing The Wait Mechanism list (wake/resume tool, background sleep, cron) — became the `wait_mechanism` enum.

### Execution candidates

- None; this skill has no bundled scripts.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
