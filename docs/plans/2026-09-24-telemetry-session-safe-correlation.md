# Telemetry Session-Safe Correlation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the telemetry fleet's hook-to-run correlation (added in commit `1d8691e`, "join semantic runs to hook execution evidence fleet-wide") actually session-scoped instead of vacuously true, make the active-run pointer safe under concurrent Codex sessions on the same skill, stop telemetry's own recorder/hook-capture invocations from polluting behavioral analysis, and resolve — rather than assume — a set of unverified Codex-CLI-version-specific hook-contract claims before acting on them.

**Architecture:** All 50 skills under `skills/*/telemetry/` are byte-identical generated sidecars (no shared library); the canonical source of truth for this repo is `skills/improve/telemetry/`, and every code/schema change is made there first, verified in isolation, then propagated to the other 49 skills with a small Python fan-out script and re-verified fleet-wide with the existing `tools/validate_target_telemetry.py` (which spawns real `recorder.py start`/`event`/`finish` subprocesses as a smoke test). Session-scoping is achieved without any unverified Codex environment variable: `hook_capture.py` already receives a real `session_id` on every hook invocation (this was true before this plan and is exercised by the existing code), so it now also drops a small local pointer (`state/current_session.json`, storing only the salted hash, never the raw id) that `recorder.py start` reads as a fallback when the caller doesn't pass `--session-id` explicitly — which is the normal case today.

**Tech Stack:** Python 3.12 (stdlib only, no new dependencies), the repo's existing `unittest`-based test suite (`python -m unittest discover -s tests`, run by `.github/workflows/validate-skills.yml`), and the telemetry sidecar's own `tools/validate_target_telemetry.py` fleet-wide smoke harness.

**Constraints from `AGENTS.md`:** Do not move or duplicate `skills/` packages into the control-plane. Do not add hooks/lifecycle rules/MCP servers/permission settings to the inert control-plane skeleton (`.codex/`, `.agents/`) without a change that explicitly reviews and activates that behavior — Task 4 below is gated on this and defaults to *not* touching `.codex/`/`.agents/` unless the user explicitly signs off after the verification step.

**Explicitly out of scope (flagged, not planned):** A proposed "one Codex plugin with a central hook dispatcher, restructure the fleet as a plugin" (originally item 1 of the source critique). That is a repository-distribution-model change that touches exactly the control-plane boundary `AGENTS.md` protects, and it invalidates the "one sidecar per skill, self-contained, portable, `repo` mode" design the fleet currently uses. It needs its own explicit go/no-go decision from the user before any plan is written for it — do not fold it into this plan.

---

### Task 1: Write a regression test harness for the telemetry recorder/hook_capture, covering today's (buggy) behavior first

There is currently no automated test for any of this — the prior session's verification was manual `bash`/subprocess probing. Before changing behavior, pin down today's actual (buggy) behavior in a real test so the fix has a red→green transition to point at.

**Files:**
- Create: `tests/test_telemetry_recorder.py`

**Step 1: Write the failing test**

```python
"""Regression tests for the telemetry sidecar's recorder.py / hook_capture.py.

Runs the *canonical* sidecar (skills/improve/telemetry) as real subprocesses against
a temporary SKILL_TELEMETRY_DATA_DIR, exactly like tools/validate_target_telemetry.py's
own smoke test does. These are the sidecar's only automated regression tests; the fleet
propagation script (docs/plans/2026-09-24-telemetry-session-safe-correlation.md, Task 6)
copies the canonical files byte-for-byte to the other 49 skills, so testing the canonical
copy is testing the fleet.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIDECAR = REPO_ROOT / "skills" / "improve" / "telemetry"


def run_recorder(env: dict[str, str], *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SIDECAR / "recorder.py"), *args],
        cwd=SIDECAR,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
    )


def run_hook(env: dict[str, str], payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SIDECAR / "hook_capture.py")],
        cwd=SIDECAR,
        env=env,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=10,
    )


def read_run_events(data_dir: Path, run_id: str) -> list[dict]:
    files = list(data_dir.rglob(f"{run_id}.jsonl"))
    assert len(files) == 1, f"expected exactly one raw file for {run_id}, found {files}"
    return [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines() if line.strip()]


class SessionScopedCorrelationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._tmp.name)
        self.env = {**__import__("os").environ, "SKILL_TELEMETRY_DATA_DIR": str(self.data_dir)}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_hook_from_a_different_session_does_not_correlate_to_an_unrelated_active_run(self) -> None:
        """A run started in session A must not absorb a PostToolUse hook event that
        actually happened in unrelated session B. This is the cross-attribution bug:
        recorder.py start is never given --session-id by SKILL.md wiring today, so the
        active run's session_id_hash is null, and hook_capture.py's old guard
        (`not active.get("session_id_hash") or ...`) treated "null" as "match anything"."""
        start = run_recorder(self.env, "start", "--task-category", "test")
        self.assertEqual(start.returncode, 0, start.stderr)
        run_id = start.stdout.strip()

        # A hook event from a real, unrelated Codex session (session_id "session-B") fires
        # while run_id's active-run pointer carries no session binding.
        hook = run_hook(self.env, {
            "hook_event_name": "PostToolUse",
            "session_id": "session-B",
            "turn_id": "turn-1",
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /unrelated"},
        })
        self.assertEqual(hook.returncode, 0, hook.stderr)

        events = read_run_events(self.data_dir, run_id)
        correlated = [e for e in events if e["event"] == "hook.observation" and e["attribution"] == "correlated"]
        self.assertEqual(
            correlated, [],
            "hook event from an unrelated session must not be attributed to this run",
        )
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_telemetry_recorder -v`
Expected: **FAIL** — `hook.observation` from `session-B` shows up as `correlated` against the run that has no session recorded, because today's guard treats a missing `session_id_hash` as "match any session."

**Step 3: Commit the red test on its own**

```bash
git add tests/test_telemetry_recorder.py
git commit -m "test(telemetry): pin down the cross-session correlation bug with a failing regression test"
```

(Committing the red test separately makes the next task's fix reviewable as a clean before/after.)

---

### Task 2: Make `recorder.py start` fall back to the freshest hook-observed session instead of leaving `session_id_hash` null

**Files:**
- Modify: `skills/improve/telemetry/recorder.py`

**Step 1: Add the session-pointer helpers**

Insert after the existing `_elapsed_ms` function (right before `def _run_state(root: Path, run_id: str) -> Path:`):

```python
def _current_session_path(root: Path) -> Path:
    return root / "state" / "current_session.json"


def get_current_session_hash(root: Path) -> str | None:
    """The freshest session_id_hash any hook has actually observed for this sidecar.
    recorder.py start falls back to this when the caller didn't pass --session-id
    (the normal case: SKILL.md wiring invokes `start` as a plain subprocess with no
    direct access to Codex's own session id). Populated by hook_capture.py, which
    does receive a real session_id on every hook invocation."""
    path = _current_session_path(root)
    if not path.exists():
        return None
    try:
        value = load_json(path)
    except (ValueError, json.JSONDecodeError):
        return None
    session_hash = value.get("session_id_hash")
    return session_hash if isinstance(session_hash, str) and session_hash else None


def set_current_session_hash(root: Path, session_id_hash: str) -> None:
    path = _current_session_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"session_id_hash": session_id_hash, "seen_at": utc_now()}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
```

**Step 2: Use the fallback in `cmd_start`**

In `cmd_start`, replace:

```python
    event, _, _ = base_event(
        sidecar_root,
        run_id=run_id,
        event="run.started",
        session_id=args.session_id,
        turn_id=args.turn_id,
        model=args.model,
    )
    evidence = {"invocation": args.invocation, **_fingerprint_drift_evidence(sidecar_root, manifest)}
```

with:

```python
    event, _, _ = base_event(
        sidecar_root,
        run_id=run_id,
        event="run.started",
        session_id=args.session_id,
        turn_id=args.turn_id,
        model=args.model,
    )
    if not args.session_id:
        # No explicit --session-id: fall back to the freshest session a hook has actually
        # observed for this sidecar, rather than leaving source.session_id_hash null (which
        # previously made hook correlation match any session — see Task 1's regression test).
        fallback_hash = get_current_session_hash(root)
        if fallback_hash:
            event["source"]["session_id_hash"] = fallback_hash
    evidence = {"invocation": args.invocation, **_fingerprint_drift_evidence(sidecar_root, manifest)}
```

This must run *after* `base_event(...)` (which needs `root` already computed a few lines above it in `cmd_start` — confirm `root = data_root(sidecar_root, manifest)` still precedes this block; it does, unchanged from the existing function).

**Step 3: Run the still-red test**

Run: `python -m unittest tests.test_telemetry_recorder -v`
Expected: still **FAIL** — `recorder.py start` now has a fallback source, but `hook_capture.py`'s correlation guard hasn't been fixed yet (Task 3), so it's still vacuously matching. This step only proves the fallback plumbing doesn't crash; add a quick manual check instead of expecting green yet:

```bash
cd skills/improve/telemetry
TD=$(mktemp -d)
SKILL_TELEMETRY_DATA_DIR="$TD" python3 recorder.py start --task-category test
cat "$TD/state/current_session.json" 2>&1 || echo "(none yet — expected, no hook has fired)"
```

**Step 4: Commit**

```bash
git add skills/improve/telemetry/recorder.py
git commit -m "feat(telemetry): recorder.py start falls back to the last hook-observed session"
```

---

### Task 3: Make `hook_capture.py` correlation session-scoped and safe under concurrent sessions

This is the core fix. It replaces the single global `state/active_run.json` with a per-session-scope file (`state/active_runs/<scope>.json`), so two concurrent Codex sessions invoking the same skill can no longer interrupt each other's runs, and it makes `hook_capture.py` write the session pointer Task 2 reads.

**Files:**
- Modify: `skills/improve/telemetry/recorder.py`
- Modify: `skills/improve/telemetry/hook_capture.py`

**Step 1: Re-scope the active-run pointer in `recorder.py`**

Replace the existing:

```python
def _active_run_path(root: Path) -> Path:
    return root / "state" / "active_run.json"


def get_active_run(root: Path) -> dict[str, Any] | None:
    """The most recently started run for this sidecar that has not yet finished (or been marked interrupted)."""
    path = _active_run_path(root)
    if not path.exists():
        return None
    try:
        value = load_json(path)
    except (ValueError, json.JSONDecodeError):
        return None
    return value if value.get("run_id") else None


def set_active_run(root: Path, value: dict[str, Any] | None) -> None:
    path = _active_run_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if value is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
```

with:

```python
SCOPE_UNKNOWN = "_unscoped"


def _active_run_path(root: Path, scope: str) -> Path:
    safe_scope = re.sub(r"[^A-Za-z0-9_-]+", "-", scope).strip("-") or SCOPE_UNKNOWN
    return root / "state" / "active_runs" / f"{safe_scope}.json"


def get_active_run(root: Path, scope: str) -> dict[str, Any] | None:
    """The most recently started, not-yet-finished run *for this session scope*. Scoping
    by session_id_hash (falling back to SCOPE_UNKNOWN only when no session is known at all)
    is what stops one Codex session's run from being auto-interrupted or hook-correlated by
    another concurrent session invoking the same skill."""
    path = _active_run_path(root, scope)
    if not path.exists():
        return None
    try:
        value = load_json(path)
    except (ValueError, json.JSONDecodeError):
        return None
    return value if value.get("run_id") else None


def set_active_run(root: Path, scope: str, value: dict[str, Any] | None) -> None:
    path = _active_run_path(root, scope)
    path.parent.mkdir(parents=True, exist_ok=True)
    if value is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
```

**Step 2: Update every caller of `get_active_run`/`set_active_run` in `recorder.py` to pass a scope**

In `cmd_start`, replace:

```python
    stale = get_active_run(root)
    if stale and str(stale.get("run_id")) != run_id:
        _close_interrupted_run(sidecar_root, root, stale, reason="next_run_started")

    event, _, _ = base_event(
        sidecar_root,
        run_id=run_id,
        event="run.started",
        session_id=args.session_id,
        turn_id=args.turn_id,
        model=args.model,
    )
    if not args.session_id:
        fallback_hash = get_current_session_hash(root)
        if fallback_hash:
            event["source"]["session_id_hash"] = fallback_hash
    evidence = {"invocation": args.invocation, **_fingerprint_drift_evidence(sidecar_root, manifest)}
    event.update({
        "phase": args.phase,
        "task_category": args.task_category,
        "outcome": "unknown",
        "evidence": evidence,
        "tags": sorted(set(args.tag or [])),
    })
    path = emit(sidecar_root, event)
    _register_run(
        root, run_id, path,
        started_at=event["timestamp"],
        task_category=args.task_category,
        model=args.model,
        session_id_hash=event["source"]["session_id_hash"],
    )
    set_active_run(root, {
        "run_id": run_id,
        "started_at": event["timestamp"],
        "task_category": args.task_category,
        "model": args.model,
        "session_id_hash": event["source"]["session_id_hash"],
    })
    print(run_id)
    return 0
```

with:

```python
    session_id_hash = hash_identifier(root, args.session_id) if args.session_id else get_current_session_hash(root)
    scope = session_id_hash or SCOPE_UNKNOWN

    stale = get_active_run(root, scope)
    if stale and str(stale.get("run_id")) != run_id:
        _close_interrupted_run(sidecar_root, root, scope, stale, reason="next_run_started")

    event, _, _ = base_event(
        sidecar_root,
        run_id=run_id,
        event="run.started",
        session_id=args.session_id,
        turn_id=args.turn_id,
        model=args.model,
    )
    if session_id_hash and not args.session_id:
        event["source"]["session_id_hash"] = session_id_hash
    evidence = {"invocation": args.invocation, **_fingerprint_drift_evidence(sidecar_root, manifest)}
    event.update({
        "phase": args.phase,
        "task_category": args.task_category,
        "outcome": "unknown",
        "evidence": evidence,
        "tags": sorted(set(args.tag or [])),
    })
    path = emit(sidecar_root, event)
    _register_run(
        root, run_id, path,
        started_at=event["timestamp"],
        task_category=args.task_category,
        model=args.model,
        session_id_hash=event["source"]["session_id_hash"],
    )
    set_active_run(root, scope, {
        "run_id": run_id,
        "started_at": event["timestamp"],
        "task_category": args.task_category,
        "model": args.model,
        "session_id_hash": event["source"]["session_id_hash"],
    })
    print(run_id)
    return 0
```

(Note this drops the duplicate `if not args.session_id: fallback_hash = ...` block added in Task 2, folding it into the single `session_id_hash = ...` line computed up top — Task 2's version is superseded by this one. Remove the old standalone block from Task 2 when applying this step; don't leave both.)

Update `_close_interrupted_run`'s signature to take and use `scope`:

```python
def _close_interrupted_run(sidecar_root: Path, root: Path, scope: str, stale: dict[str, Any], *, reason: str) -> None:
    """Auto-close a run that never received a `finish` before a new run started, so an
    agent crash or abandoned run is distinguishable from a run that is still legitimately open."""
    run_id = str(stale.get("run_id"))
    started_at = stale.get("started_at")
    event, _, _ = base_event(
        sidecar_root,
        run_id=run_id,
        event="run.finished",
        source_kind="semantic",
        attribution="correlated",
    )
    event.update({
        "phase": "interrupted",
        "outcome": "interrupted",
        "failure_class": "run_not_finished",
        "duration_ms": _elapsed_ms(started_at),
        "evidence": {"detected_by": reason, "task_category": stale.get("task_category")},
        "tags": ["auto_interrupted"],
    })
    emit(sidecar_root, event)
    append_run_index(root, {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": event["timestamp"],
        "outcome": "interrupted",
        "task_category": stale.get("task_category"),
    })
    set_active_run(root, scope, None)
```

(Added the trailing `set_active_run(root, scope, None)` — previously the caller in `cmd_start` immediately overwrote the same singleton file with the new run, so an explicit clear wasn't needed; now that each scope has its own file and `_close_interrupted_run` may be called from `hook_capture.py` too in Task's next step, closing it out explicitly is required.)

In `cmd_finish`, replace:

```python
    emit(sidecar_root, event)

    active = get_active_run(root)
    if active and str(active.get("run_id")) == args.run_id:
        set_active_run(root, None)
    append_run_index(root, {
```

with:

```python
    emit(sidecar_root, event)

    scope = state.get("session_id_hash") or SCOPE_UNKNOWN
    active = get_active_run(root, scope)
    if active and str(active.get("run_id")) == args.run_id:
        set_active_run(root, scope, None)
    append_run_index(root, {
```

Add `import re` is already present in `recorder.py` (it's used by `command_class`/`hash_identifier`'s salt handling already) — confirm before skipping; if for some reason it's missing, add `import re` to the top-level imports.

**Step 3: Rewrite `hook_capture.py`'s correlation logic**

Replace the whole file's correlation section. The new imports line becomes:

```python
from recorder import (
    SCOPE_UNKNOWN,
    _elapsed_ms,
    _run_path,
    _register_run,
    append_jsonl,
    append_run_index,
    command_class,
    data_root,
    get_active_run,
    hash_identifier,
    hash_text,
    load_config,
    load_manifest,
    redact,
    set_active_run,
    set_current_session_hash,
)
```

Replace `_close_interrupted`'s signature and body to take `scope` and clear the right file:

```python
def _close_interrupted(sidecar: Path, root: Path, scope: str, active: dict[str, Any], *, reason: str) -> None:
    manifest = load_manifest(sidecar)
    config = load_config(sidecar)
    target = manifest.get("target", {})
    run_id = str(active.get("run_id"))
    started_at = active.get("started_at")
    event = {
        "schema": "skilltelemetry.event.v1",
        "event_id": str(uuid.uuid4()),
        "run_id": run_id,
        "timestamp": utc_now(),
        "skill": {
            "name": target.get("name", "unknown"),
            "version": target.get("version"),
            "fingerprint": target.get("fingerprint", "unknown"),
        },
        "event": "run.finished",
        "phase": "interrupted",
        "outcome": "interrupted",
        "failure_class": "session_ended_before_finish",
        "duration_ms": _elapsed_ms(started_at),
        "source": {
            "kind": "hook",
            "model": None,
            "session_id_hash": active.get("session_id_hash"),
            "turn_id_hash": None,
        },
        "attribution": "correlated",
        "evidence": {"detected_by": reason, "task_category": active.get("task_category")},
        "tags": ["auto_interrupted"],
        "privacy": {"content_policy": config.get("content_policy", "metadata"), "redactions": 0},
    }
    redacted, count = redact(event)
    redacted["privacy"]["redactions"] = count
    path = _run_path(root, run_id)
    append_jsonl(path, redacted)
    _register_run(root, run_id, path)
    append_run_index(root, {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": event["timestamp"],
        "outcome": "interrupted",
        "task_category": active.get("task_category"),
    })
    set_active_run(root, scope, None)
```

Replace `main()`'s body from the point it computes `session_hash`/`turn_hash` onward:

```python
    session_hash = hash_identifier(root, session_id) or "nosession"
    turn_hash = hash_identifier(root, turn_id) or "noturn"

    # Every hook invocation carries a real session_id from Codex; record the freshest one so
    # `recorder.py start` (invoked as a plain subprocess with no direct Codex session context)
    # can bind a new run to it when the caller doesn't pass --session-id explicitly.
    if session_id:
        set_current_session_hash(root, session_hash)

    # Correlate strictly by this hook's own real session — no "unknown session matches
    # anything" fallback. A run only ever gets hook evidence from the session that actually
    # started it.
    active = get_active_run(root, session_hash)
    correlated = active is not None

    if event_name in CLOSING_HOOKS and correlated:
        _close_interrupted(sidecar, root, session_hash, active, reason=f"hook:{event_name}")
        return 0
```

(This drops the old `not active.get("session_id_hash") or active.get("session_id_hash") == session_hash` guard entirely — scoping the *lookup itself* by `session_hash` makes that guard unnecessary and removes the vacuous-match hole Task 1's test caught.)

Further down, replace:

```python
    run_id = str(active["run_id"]) if correlated else (
        "ambient-" + hashlib.sha256(f"{session_hash}:{turn_hash}".encode()).hexdigest()[:24]
    )
```

(unchanged — still correct) and replace the final correlated-write branch:

```python
    if correlated:
        path = _run_path(root, run_id)
        append_jsonl(path, redacted)
        _register_run(root, run_id, path)
```

(also unchanged — `_register_run` doesn't need a scope, only the active-run *pointer* does).

**Step 4: Run the test from Task 1 — it should now pass**

Run: `python -m unittest tests.test_telemetry_recorder -v`
Expected: **PASS**.

**Step 5: Add the concurrency-safety test and confirm it passes too**

Append to `tests/test_telemetry_recorder.py`:

```python
    def test_two_concurrent_sessions_do_not_interrupt_each_others_runs(self) -> None:
        """Session A starts a run; before it finishes, session B starts a run for the same
        skill. Today (singleton state/active_run.json) B's start marks A's run interrupted
        and clobbers the pointer. With session-scoped active-run state, both must stay open
        and correlate independently."""
        # Prime the current_session pointer as session A, start A's run.
        run_hook(self.env, {"hook_event_name": "SessionStart", "session_id": "session-A"})
        start_a = run_recorder(self.env, "start", "--task-category", "a")
        run_a = start_a.stdout.strip()

        # Prime as session B, start B's run.
        run_hook(self.env, {"hook_event_name": "SessionStart", "session_id": "session-B"})
        start_b = run_recorder(self.env, "start", "--task-category", "b")
        run_b = start_b.stdout.strip()

        events_a = read_run_events(self.data_dir, run_a)
        self.assertTrue(
            all(e.get("outcome") != "interrupted" for e in events_a),
            f"session A's run was wrongly auto-interrupted by session B's start: {events_a}",
        )

        # A PostToolUse from session A now correlates only to A's run, not B's.
        run_hook(self.env, {
            "hook_event_name": "PostToolUse",
            "session_id": "session-A",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest -q"},
        })
        events_a = read_run_events(self.data_dir, run_a)
        events_b = read_run_events(self.data_dir, run_b)
        self.assertTrue(any(e["event"] == "hook.observation" and e["attribution"] == "correlated" for e in events_a))
        self.assertFalse(any(e["event"] == "hook.observation" for e in events_b))
```

Run: `python -m unittest tests.test_telemetry_recorder -v`
Expected: **PASS**.

**Step 6: Commit**

```bash
git add skills/improve/telemetry/recorder.py skills/improve/telemetry/hook_capture.py tests/test_telemetry_recorder.py
git commit -m "fix(telemetry): session-scope hook correlation and the active-run pointer

Closes two real bugs in the prior merge (1d8691e):
- hook_capture.py's correlation guard treated a null session_id_hash (the
  normal case, since SKILL.md never passes --session-id to recorder.py
  start) as 'match any session', so hook evidence from an unrelated Codex
  session could attribute to this skill's run.
- state/active_run.json was a single global pointer per skill, so two
  concurrent sessions invoking the same skill would interrupt and clobber
  each other's runs.

recorder.py start now falls back to the freshest session hook_capture.py has
observed (state/current_session.json, storing only the salted hash) when
the caller doesn't pass --session-id, and the active-run pointer is now
keyed per session (state/active_runs/<scope>.json) instead of a singleton."
```

---

### Task 4: Stop telemetry's own recorder/hook_capture commands from being counted as skill behavior

**Files:**
- Modify: `skills/improve/telemetry/hook_capture.py`
- Modify: `skills/improve/telemetry/tools/analyze_telemetry.py`
- Modify: `tests/test_telemetry_recorder.py`

**Step 1: Write the failing test**

Append to `tests/test_telemetry_recorder.py`:

```python
    def test_hook_evidence_for_the_telemetry_recorders_own_commands_is_flagged(self) -> None:
        """A PostToolUse hook fires for every Bash call the agent makes — including the
        `python recorder.py event ...` calls SKILL.md itself instructs the agent to run.
        Those must not look like the skill's own external command execution."""
        start = run_recorder(self.env, "start", "--task-category", "test")
        run_id = start.stdout.strip()
        run_hook(self.env, {
            "hook_event_name": "PostToolUse",
            "session_id": "nosession",
            "tool_name": "Bash",
            "tool_input": {"command": f'python "{SIDECAR}/recorder.py" event --run-id {run_id} --event decision'},
        })
        events = read_run_events(self.data_dir, run_id)
        hook_events = [e for e in events if e["event"] == "hook.observation"]
        self.assertTrue(hook_events, "expected a correlated hook.observation for the recorder.py call")
        self.assertTrue(hook_events[0]["evidence"].get("telemetry_internal") is True)
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_telemetry_recorder -v`
Expected: **FAIL** — `evidence` has no `telemetry_internal` key today.

**Step 3: Implement in `hook_capture.py`**

Add near the top (after the existing `CLOSING_HOOKS` constant):

```python
import re

TELEMETRY_SELF_COMMAND_RE = re.compile(r"(?:^|[\\/])(?:recorder|hook_capture)\.py\b")
```

In `main()`, where `tool_input` is inspected:

```python
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            evidence["command_class"] = command_class(command)
            evidence["command_sha256"] = hash_text(command)
            if TELEMETRY_SELF_COMMAND_RE.search(command):
                evidence["telemetry_internal"] = True
        evidence["tool_input_keys"] = sorted(str(k) for k in tool_input.keys())[:50]
```

(only the `if TELEMETRY_SELF_COMMAND_RE.search(command): evidence["telemetry_internal"] = True` line is new).

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_telemetry_recorder -v`
Expected: **PASS**.

**Step 5: Exclude flagged evidence from the analyzer's thrash-detection**

In `tools/analyze_telemetry.py`, inside `analyze(...)`, the thrash-detection loop currently reads:

```python
        hashes = [
            e.get("evidence", {}).get("command_sha256")
            for e in items
            if isinstance(e.get("evidence"), dict) and e.get("evidence", {}).get("command_sha256")
        ]
```

Replace with:

```python
        hashes = [
            e.get("evidence", {}).get("command_sha256")
            for e in items
            if isinstance(e.get("evidence"), dict)
            and e.get("evidence", {}).get("command_sha256")
            and not e.get("evidence", {}).get("telemetry_internal")
        ]
```

(This only affects command-repetition/thrash detection. `telemetry_internal` events are still stored and still count for incomplete-run/latency findings — they just don't get mistaken for the skill repeating a real command.)

**Step 6: Add a small analyzer-level test**

Append a new test class to `tests/test_telemetry_recorder.py`:

```python
class AnalyzeTelemetryExcludesTelemetryInternalTests(unittest.TestCase):
    def test_repeated_telemetry_internal_commands_do_not_trigger_a_thrash_finding(self) -> None:
        tools_dir = SIDECAR / "tools"
        with tempfile.TemporaryDirectory() as td:
            env = {**__import__("os").environ, "SKILL_TELEMETRY_DATA_DIR": td}
            start = run_recorder(env, "start", "--task-category", "test")
            run_id = start.stdout.strip()
            for _ in range(3):
                run_hook(env, {
                    "hook_event_name": "PostToolUse",
                    "session_id": "nosession",
                    "tool_name": "Bash",
                    "tool_input": {"command": f'python "{SIDECAR}/recorder.py" event --run-id {run_id} --event decision'},
                })
            run_recorder(env, "finish", "--run-id", run_id, "--outcome", "success")

            out = Path(td) / "findings.jsonl"
            result = subprocess.run(
                [sys.executable, str(tools_dir / "analyze_telemetry.py"), str(SIDECAR), "--data-root", td, "--out", str(out)],
                cwd=SIDECAR, env=env, text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertFalse(
                any(f["finding_type"] == "retry_or_command_thrashing" for f in findings),
                f"repeated telemetry-internal commands should not surface as thrashing: {findings}",
            )
```

Run: `python -m unittest tests.test_telemetry_recorder -v`
Expected: **PASS**.

**Step 7: Commit**

```bash
git add skills/improve/telemetry/hook_capture.py skills/improve/telemetry/tools/analyze_telemetry.py tests/test_telemetry_recorder.py
git commit -m "fix(telemetry): flag and exclude the recorder's own commands from thrash detection

Every recorder.py/hook_capture.py invocation SKILL.md instructs the agent to
run is itself a Bash tool call, so it generates its own PostToolUse hook
evidence. Left unflagged, that self-observation could look like the skill
repeating a real command. Tag it evidence.telemetry_internal=true and
exclude it from analyze_telemetry.py's repeated-command/thrash detection."
```

---

### Task 5: Verify (don't assume) the remaining Codex-CLI-version-specific hook-contract claims

The source critique for this plan asserted several specific Codex CLI hook-contract facts — an `Interrupt` hook event, `SessionEnd`/`Interrupt` default/max timeouts of 1s/3s, and a `commandWindows` field for Windows command overrides. **None of these have a primary source in this repository** (`.codex/hooks/` and `.codex-plugin/plugin.json` contain no hook schema documentation — verified empty), and the critique's own citations are bracketed reference markers with no resolvable URLs in the text handed to this plan. Do not implement version-specific hook-schema details on an unverified third-party claim.

**Files:**
- No code changes in this task — it is a research gate. It produces either a follow-up task (if confirmed) or a documented open question (if not).

**Step 1: Search for a primary, authoritative source**

Use `WebSearch`/`WebFetch` (load via `ToolSearch` if not already available) to look for the current official Codex CLI documentation covering: the full list of supported hook event names (specifically whether `Interrupt` exists alongside `Stop`/`SessionEnd`/`SessionStart`/`PostToolUse`/`UserPromptSubmit`), the default and maximum timeout for each hook type, and whether hook command definitions support a `commandWindows` (or equivalently named) override for Windows.

**Step 2: Record the outcome**

- **If confirmed from an official/primary source:** write a short follow-up task list (as a new file, `docs/plans/<date>-telemetry-hook-contract-followup.md`, using this same plan format) covering: adding `Interrupt` to `CLOSING_HOOKS` in `hook_capture.py` with a distinct `failure_class` from `Stop`/`SessionEnd` (per the source critique's suggested `outcome=interrupted` immediately on `Interrupt`, vs. only-if-still-open on `SessionEnd`); correcting the `timeout` values in `hooks.repo.json`/`hooks.plugin.json` to whatever the primary source actually specifies (do not copy the critique's `1`/`3` numbers without the primary source confirming them); and adding a Windows command override in the same two files if the field name is confirmed. Do **not** implement any of this in the current task — hand it to the user as a reviewable follow-up, since it also touches whether `.codex/hooks/` (currently an empty placeholder per `AGENTS.md`'s "inert control-plane" rule) needs to register anything, which is a control-plane activation decision the user should confirm.
- **If not confirmed / no primary source reachable in this environment:** leave all hook timeout/event-name behavior unchanged. Add one sentence to `skills/improve/telemetry/INTEGRATION.md`'s "Hook evidence" section (and propagate fleet-wide per Task 6) noting the open question, e.g.: *"An `Interrupt` hook and stricter `SessionEnd` timeout bounds have been proposed for future Codex CLI versions but are unverified against a primary source as of this sidecar's generation; `Stop`/`SessionEnd` remain the only run-closing hooks until confirmed."* Do not silently drop the concern — surface it so a future pass can pick it up once verifiable.

**Step 3: Commit whatever was produced (a follow-up plan file, or the one-sentence doc note — not both)**

```bash
git add docs/plans/ skills/*/telemetry/INTEGRATION.md   # whichever applies
git commit -m "docs(telemetry): record verification outcome for the Codex hook-contract claims"
```

---

### Task 6: Propagate the canonical fixes to all 50 skills and refresh validation

**Files:**
- No new files to hand-edit — write and run a one-off fan-out script (not committed, matches the pattern already used for the prior merge).

**Step 1: Confirm the canonical files changed in Tasks 2–4 are the only ones that need to fan out**

```bash
cd /home/user/codex-skills
git diff --stat 1d8691e~1..HEAD -- skills/improve/telemetry
```

Expect: `recorder.py`, `hook_capture.py`, `tools/analyze_telemetry.py` (and, only if Task 5 produced a doc note, `INTEGRATION.md`).

**Step 2: Fan out the code files**

Write a scratch script (put it under your scratchpad directory, not committed):

```python
#!/usr/bin/env python3
"""Propagate the canonical (skills/improve/telemetry) recorder.py, hook_capture.py, and
tools/analyze_telemetry.py to every other skill's telemetry sidecar. These files are
confirmed byte-identical across the fleet before each change, so a straight copy is safe."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path("/home/user/codex-skills")
CANON = ROOT / "skills/improve/telemetry"
FILES = ["recorder.py", "hook_capture.py", "tools/analyze_telemetry.py"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    skills = sorted(p.parent for p in ROOT.glob("skills/*/telemetry") if p.is_dir())
    changed = 0
    for skill_dir in skills:
        sidecar = skill_dir / "telemetry"
        if sidecar == CANON:
            continue
        for rel in FILES:
            src, dst = CANON / rel, sidecar / rel
            if sha(dst) != sha(src):
                dst.write_bytes(src.read_bytes())
                changed += 1
    print(f"updated {changed} files across {len(skills) - 1} skills")


if __name__ == "__main__":
    main()
```

Run it: `python3 /path/to/scratchpad/propagate_code.py` — expect `updated 147 files across 49 skills` (49 skills × 3 files), or `98` if Task 5 didn't touch `analyze_telemetry.py`.

If Task 5 produced an `INTEGRATION.md` doc-note addition, propagate that one sentence with a targeted string replace across all 50 `INTEGRATION.md` files (same pattern as the prior merge's `propagate_docs.py` — verify the exact old-text substring is present and identical in all 50 files first with `grep -c` before replacing, exactly as done for the `1d8691e` merge).

**Step 3: Run the fleet-wide validator**

```bash
cd /home/user/codex-skills
fail=0
for d in skills/*/telemetry; do
  out=$(python3 "$d/tools/validate_target_telemetry.py" "$d" 2>&1)
  status=$(echo "$out" | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])" 2>/dev/null)
  errors=$(echo "$out" | python3 -c "import json,sys; print(json.load(sys.stdin)['errors'])" 2>/dev/null)
  if [ "$errors" != "0" ]; then echo "FAIL: $d"; echo "$out"; fail=1; fi
done
echo "fleet validation done, fail=$fail"
```

Expected: `fail=0` for all 50 skills (each spawns real `start`/`event`/`finish` subprocesses via the validator's own smoke test).

**Step 4: Run the full repo test suite the CI workflow runs**

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/validate_skill_packages.py
```

All three must pass clean — this is exactly what `.github/workflows/validate-skills.yml`'s `validate` job runs (plus the routing/benchmark steps, which this plan's changes don't touch).

**Step 5: Clean up bytecode artifacts and commit**

```bash
find skills -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
git add -A skills/
git status --short | grep -v "^ M skills/" && echo "STOP: unexpected paths touched" || echo "clean, only skills/ modified"
git commit -m "fix(telemetry): propagate session-safe correlation fixes to all 50 skills

Fans out the canonical recorder.py/hook_capture.py/analyze_telemetry.py
changes from skills/improve/telemetry to the other 49 skills (confirmed
byte-identical before this change) and re-runs the fleet-wide
validate_target_telemetry.py smoke test (0 errors across all 50) plus the
repo's own unittest/validate_repository/validate_skill_packages checks."
```

**Step 6: Push**

```bash
git push -u origin claude/inspiring-johnson-raf0ge
```

(This branch already has an open PR — JackSmack1971/codex-skills#135 was merged; this plan targets a fresh PR on the same branch name if it still exists, or a new branch off current `main` if that branch was deleted post-merge. Check `git branch -a` and `git log origin/main -1` first; if `claude/inspiring-johnson-raf0ge` no longer exists or is behind `main`, recreate it from `main` per this repo's stated convention for a merged branch: `git fetch origin main && git checkout -B claude/inspiring-johnson-raf0ge origin/main`, then re-apply Tasks 1–6 on top of current `main` rather than on stale history.)

---

## Summary of what this plan intentionally does NOT do

- **Central telemetry dispatcher / plugin restructure.** Real scalability concern (50 skills × `PostToolUse` hooks all firing on every Bash call), but it's a distribution-model change that needs its own explicit decision from the user given `AGENTS.md`'s control-plane constraints — not something to fold into a bug-fix plan.
- **`Interrupt` hook, hook timeout corrections, `commandWindows`.** Gated behind Task 5's verification step; implemented only if a primary source confirms the claims, as a separate follow-up plan.
- **Trimming `SKILL.md`'s telemetry wiring for context economy** (the "Astra progressive disclosure" suggestion). The per-event `--evidence-json` blocks in `SKILL.md` are the actual runnable instrumentation contract, not restatable boilerplate — removing them without a replacement mechanism would degrade the semantic telemetry quality that's the system's strongest asset. This is a legitimate design conversation but not a bug, and not scoped here.
- **The `codex exec --json --full-auto` → `--sandbox workspace-write` flag concern.** Checked: `--full-auto` does not appear anywhere in this repository's docs or scripts. No action needed.
