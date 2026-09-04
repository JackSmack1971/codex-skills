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

