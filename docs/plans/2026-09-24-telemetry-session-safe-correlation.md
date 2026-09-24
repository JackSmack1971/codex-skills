# Telemetry: session-safe run correlation

## Context

PR #135 ("join semantic runs to hook execution evidence fleet-wide", commit
`9f06fba`) added `state/active_run.json` so `hook_capture.py` can attach
ambient hook evidence (tool calls, exit codes, retries) to the semantic run
that was open when the hook fired, instead of stranding it in `ambient/`
forever. The documentation this PR shipped (`SCHEMA.md`, `INTEGRATION.md`)
describes this as a **session-scoped** join: "attaches matching-session hook
evidence to that run"; "hook events ... from a different session remain
ambient". The implementation does not actually enforce that scope, in two
ways:

1. **Single global pointer.** `state/active_run.json` is one file per
   sidecar, not one per session. If two independent sessions run the same
   skill concurrently (two terminals, two agents, a shared machine), the
   second session's `recorder.py start` sees the first session's still-open
   run as "stale" (different `run_id`) and auto-emits
   `run.finished(outcome=interrupted)` for it — even though that run is not
   interrupted, just concurrent. The second session's `start` then
   overwrites the pointer, so the first session's own hook events (and its
   own `finish`) are no longer correctly tracked.

2. **Session-check bypass.** In `hook_capture.py`:
   ```python
   correlated = bool(active) and (
       not active.get("session_id_hash") or active.get("session_id_hash") == session_hash
   )
   ```
   When the active run was started without a `--session-id` (so it has no
   recorded `session_id_hash`), the `not active.get("session_id_hash")`
   clause makes *any* session's hook events correlate to it. This is the
   opposite of "session-scoped" — it is precisely the cross-session leak the
   docs say cannot happen.

Both are real for this repo's own usage: `writing-plans/SKILL.md` and the
other skills' `SKILL.md`s invoke `recorder.py start` without threading a
`--session-id` through by default (it's an optional flag), so the common
case already hits gap #2, and any concurrent use of the same skill sidecar
(local dev + CI, two open terminals, etc.) hits gap #1.

## Fix

Make the active-run pointer **session-scoped** instead of global:

- Replace `state/active_run.json` with a small directory,
  `state/active_run/<bucket>.json`, one file per session bucket.
- `<bucket>` is the run's `session_id_hash` when a session id was supplied
  at `start`, or the literal `nosession` when it was not. This keeps the
  existing single-session behavior (and the validator's smoke test, which
  never passes `--session-id`) working unchanged, while giving every
  distinct session its own pointer.
- `recorder.py start`: only auto-interrupt a "stale" run if it lives in the
  *same* bucket as the run being started. A concurrent session's run is
  simply left alone.
- `recorder.py finish`: look up the bucket from the run's own recorded
  state (written at `start`), not from whatever `--session-id` the `finish`
  call happens to pass, and only clear that bucket's pointer.
- `hook_capture.py`: compute the incoming hook's bucket the same way
  (`session_id_hash` or `nosession`) and look up only that bucket's active
  run. Delete the `not active.get("session_id_hash")` bypass entirely —
  correlation now requires the hook and the run to share a bucket, full
  stop. A run with no session id can still only be correlated by hooks that
  also carry no session id (the pre-existing, intra-session default case),
  never by an unrelated session's hooks.
- `CLOSING_HOOKS` (`Stop`/`SessionEnd`) auto-interrupt logic in
  `hook_capture.py` moves to the same bucket-scoped lookup, and clears only
  that bucket's pointer.

This trades a small amount of recall (a hook payload that omits
`session_id` for a run that was started *with* one will no longer
correlate, and instead falls to `ambient/`) for correctness (no run is ever
falsely marked interrupted by a concurrent session, and no hook evidence is
ever attributed to a run outside its own session). That is the right
trade-off for telemetry: a missed correlation is recoverable from
`ambient/`; a false attribution corrupts the record silently.

No schema changes are needed (`attribution: correlated` / `ambient` and
`outcome: interrupted` already exist from PR #135). `SCHEMA.md` /
`INTEGRATION.md` wording is already accurate to the *intended* behavior; no
edits needed there beyond making the code match it. `state/` is
git-ignored, so the old `active_run.json` layout needs no migration — it is
simply superseded.

## Rollout

Every skill under `skills/*/telemetry/` carries a byte-identical copy of
`recorder.py` and `hook_capture.py` (confirmed via `md5sum` across all 50
sidecars). Apply the same code change to all 50 copies so they stay
identical, then re-run `validate_target_telemetry.py` (including its
subprocess start/event/finish smoke test) against every sidecar to confirm
nothing regressed.

## Verification

- Unit-level: a manual two-session scenario (two `start` calls with
  different `--session-id`s, interleaved `event`/`finish` calls, and a
  `Stop`-hook payload for each session) confirms neither run is marked
  interrupted by the other and each session's hook evidence lands only on
  its own run.
- Fleet-wide: `validate_target_telemetry.py` passes (0 errors, 0 warnings)
  for all 50 sidecars, including the existing smoke test.
