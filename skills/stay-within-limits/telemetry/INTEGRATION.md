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

## Static candidates from the target

These are inspection hints, not runtime facts.

### Decision candidates

- `README.md:7` — runs work in bounded waves, and pauses before it crosses the limit instead of
- `README.md:12` — - Checks 5-hour and weekly usage before substantial work and between waves.
- `README.md:14` — - Pauses new work when either window reaches 95% of its limit.
- `README.md:15` — - Resumes only after re-checking that the actual window or block is clear.
- `README.md:16` — - Makes wake prompts self-contained so work can continue after a long pause.
- `README.md:22` — ## When To Use It
- `README.md:33` — When Codex CLI does not expose a better first-party usage signal, use:
- `README.md:47` — rule to reschedule if the limit is still too high. If more delegated work
- `README.md:60` — Use `--update-instructions` when you want the 5-hour and weekly limit convention
- `SKILL.md:11` — Check before launching substantial work and between bounded waves. If the user
- `SKILL.md:12` — has not selected a threshold, use 95% only when a first-party signal reports a
- `SKILL.md:17` — 1. Run a bounded wave of work. Default to at most 3 parallel subagents unless
- `SKILL.md:22` — 4. If any reported window is at or above the chosen threshold, stop launching
- `SKILL.md:23` — work and schedule a self-contained resume when that window should clear.
- `SKILL.md:24` — 5. On resume, re-check the real window or block before continuing. Do not trust

### Verification candidates

- `README.md:31` — ## Codex CLI Usage Check
- `README.md:41` — previous check rather than trusting elapsed time alone.
- `README.md:46` — plan, the 95% pause threshold, the wave throttle, the exact usage check, and the
- `SKILL.md:11` — Check before launching substantial work and between bounded waves. If the user
- `SKILL.md:21` — 3. Check current usage with a first-party host signal.
- `SKILL.md:24` — 5. On resume, re-check the real window or block before continuing. Do not trust
- `SKILL.md:56` — waits. Each wakeup should re-check usage, reschedule if still over budget, and
- `SKILL.md:62` — - The check-then-reschedule rule.
- `SKILL.md:64` — - The first-party usage signal to check.
- `SKILL.md:85` — the source of that reading, when you scheduled or expect the next check, and

### Execution candidates

- None detected statically.

## Hook evidence

`hooks.repo.json` / `hooks.plugin.json` are merge snippets. They are optional and must not overwrite an existing hook configuration blindly. Hook events remain `ambient` until correlated to a target run.

## Eval traces

For a controlled eval that intentionally invokes this target skill, capture `codex exec --json` and import it with `--attribution confirmed`. Use `candidate` for traces where target invocation is uncertain.
