---
name: stay-within-limits
description: "Keep long-running or parallel work within usage limits by checking between waves and pausing safely."

---

# Stay Within Limits

Keep long-running agent work inside the account's current usage windows. Usage
windows and allowances are version-sensitive; do not assume a fixed plan limit.
Check before launching substantial work and between bounded waves. If the user
has not selected a threshold, use 95% only when a first-party signal reports a
direct percentage for the relevant window.

## Core Loop

1. Run a bounded wave of work. Default to at most 3 parallel subagents unless
   the user or host gives a different throttle.
2. Wait for the wave to finish. Do not interrupt in-flight subagents just to
   save budget; that usually loses work.
3. Check current usage with a first-party host signal.
4. If any reported window is at or above the chosen threshold, stop launching
   work and schedule a self-contained resume when that window should clear.
5. On resume, re-check the real window or block before continuing. Do not trust
   elapsed wall-clock time alone.

## Usage Signals

Use signals in this order:

1. A first-party structured usage or budget tool exposed by the current host.
2. In an active Codex CLI session, the `/status` command.
3. The first-party Codex usage dashboard linked from the current official
   [Codex pricing documentation](https://developers.openai.com/codex/pricing).

`/status` is an interactive Codex command, not a shell command. If this agent
cannot observe its output and no structured first-party meter exists, record
the current usage state as **UNKNOWN** and ask the user to provide or confirm
the first-party reading before an automated pause/resume decision depends on
it.

Do not install or execute a third-party usage meter merely to infer Codex quota
state. Do not convert cost, tokens, messages, elapsed time, or another
provider's blocks into a Codex percentage unless current first-party
documentation supplies that mapping for the account.

## Pausing And Resuming

When a wake/resume tool is available, schedule a wakeup for:

```txt
min(3600, secondsUntilWindowClears)
```

If the runtime clamps wake delays to 60-3600 seconds, chain wakeups for longer
waits. Each wakeup should re-check usage, reschedule if still over budget, and
continue only when the window is safely below the threshold.

Make wake prompts self-contained. Include:

- The remaining plan.
- The check-then-reschedule rule.
- The selected threshold and wave throttle.
- The first-party usage signal to check.
- The previous block/window identifier when available.
- The next verification steps.
- The next wave's handoff packets, including scope, verification commands, and
  stop conditions, if delegation will resume.

## Choosing The Wait Mechanism

- Use a wake/resume tool when the agent needs instructions attached to the
  future resume and the host supports it.
- Use a background sleep or watcher for fixed timers and things a process can
  observe directly.
- Use cron or recurring schedules only for recurring fresh-session work.

Avoid short-interval polling for things the host will notify you about, such as
background task or subagent completion. For budget pauses, a prompt-cache miss
after a long sleep is acceptable; preserving the limit matters more.

## Reporting

If you pause, tell the user which window is over threshold, the observed usage,
the source of that reading, when you scheduled or expect the next check, and
what work remains. If usage is UNKNOWN, say so rather than claiming the work is
within budget. Keep enough state in the wake prompt that the next turn can
resume without relying on conversation momentum.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before step 1 of the Core Loop, start a run:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<pre_wave_check|between_wave_check|resume_check>" --invocation explicit)
   ```
   If `python3` is unavailable, use `python`.
2. After step 3 (check current usage with a first-party host signal),
   record what was observed:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase check_usage --outcome <success|failure> \
     --evidence-json '{"usage_signal_source":"<first_party_tool|status_command|dashboard_link|unknown>","five_hour_window_pct":<N|null>,"weekly_window_pct":<N|null>,"threshold":<N>}'
   ```
3. After step 4 (decide whether to stop launching work), record the
   throttle decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase throttle \
     --evidence-json '{"action_taken":"<continued|paused>","threshold_breached_window":"<five_hour|weekly|none>","wave_size":<N>}'
   ```
4. If paused, after scheduling the resume (Pausing And Resuming), record the
   wait mechanism chosen:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event operation --phase schedule_resume \
     --evidence-json '{"wait_mechanism":"<wake_tool|background_sleep|cron>","wait_seconds":<N>,"chained_wakeups":<true|false>}'
   ```
5. Before ending the turn (after Reporting), close the run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"action_taken":"<continued|paused>","usage_signal_source":"<first_party_tool|status_command|dashboard_link|unknown>","paused_count":<N>}'
   ```
   Use `--outcome failure` with a `--failure-class` (e.g. `usage_unknown`)
   when no first-party signal was observable and usage had to be recorded as
   UNKNOWN instead of a confident pause/resume decision.

If a user later reports that this run paused unnecessarily or, conversely,
kept working past the real limit, record it as its own event so throttling
calibration drift is visible without re-running the loop:
```bash
python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event user.correction \
  --evidence-json '{"original_action":"<continued|paused>","correction":"<paused_unnecessarily|failed_to_pause>"}'
```

