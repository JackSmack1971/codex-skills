#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
from common import target_fingerprint  # noqa: E402

SCHEMA = "skilltelemetry.event.v1"
SECRET_KEY_RE = re.compile(r"(?:api[_-]?key|secret|token|password|passwd|credential|authorization|cookie|private[_-]?key)", re.I)
SECRET_VALUE_RES = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]+=*", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


def redact(value: Any) -> tuple[Any, int]:
    count = 0
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if SECRET_KEY_RE.search(str(key)):
                out[str(key)] = "[REDACTED]"
                count += 1
            else:
                v, n = redact(item)
                out[str(key)] = v
                count += n
        return out, count
    if isinstance(value, list):
        out_list = []
        for item in value:
            v, n = redact(item)
            out_list.append(v)
            count += n
        return out_list, count
    if isinstance(value, str):
        text = value
        for pattern in SECRET_VALUE_RES:
            text, n = pattern.subn("[REDACTED]", text)
            count += n
        return text, count
    return value, count


def load_config(sidecar_root: Path) -> dict[str, Any]:
    config_path = sidecar_root / "config.json"
    return load_json(config_path) if config_path.exists() else {"content_policy": "metadata"}


def load_manifest(sidecar_root: Path) -> dict[str, Any]:
    return load_json(sidecar_root / "manifest.json")


def data_root(sidecar_root: Path, manifest: dict[str, Any]) -> Path:
    override = os.environ.get("SKILL_TELEMETRY_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    plugin_data = os.environ.get("PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data:
        target = manifest.get("target", {})
        name = str(target.get("name") or "skill")
        fp = str(target.get("fingerprint") or "unknown")[:12]
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "skill"
        return Path(plugin_data).expanduser().resolve() / "skill-telemetry" / f"{safe_name}-{fp}"
    return sidecar_root


def _salt(root: Path) -> str:
    path = root / "state" / "privacy_salt"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    value = secrets.token_hex(32)
    path.write_text(value + "\n", encoding="utf-8")
    return value


def hash_identifier(root: Path, value: str | None) -> str | None:
    if not value:
        return None
    salt = _salt(root)
    return hashlib.sha256((salt + "\0" + value).encode("utf-8", errors="replace")).hexdigest()


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def command_class(command: str) -> str | None:
    stripped = command.strip()
    if not stripped:
        return None
    first = re.split(r"\s+", stripped, maxsplit=1)[0].strip("'\"")
    return Path(first).name or None


def _elapsed_ms(started_at: str | None) -> float | None:
    if not started_at:
        return None
    try:
        start = datetime.fromisoformat(str(started_at).replace("Z", "+00:00"))
    except ValueError:
        return None
    return max(0.0, (datetime.now(timezone.utc) - start).total_seconds() * 1000.0)


def _run_state(root: Path, run_id: str) -> Path:
    return root / "state" / "runs" / f"{run_id}.json"


def _read_run_state(root: Path, run_id: str) -> dict[str, Any]:
    state = _run_state(root, run_id)
    if not state.exists():
        return {}
    try:
        return load_json(state)
    except (ValueError, json.JSONDecodeError):
        return {}


def _run_path(root: Path, run_id: str, date: str | None = None) -> Path:
    state = _run_state(root, run_id)
    if state.exists():
        try:
            rel = load_json(state).get("relative_path")
            if isinstance(rel, str):
                return root / rel
        except Exception:
            pass
    day = date or datetime.now(timezone.utc).date().isoformat()
    return root / "raw" / day / f"{run_id}.jsonl"


def _register_run(root: Path, run_id: str, path: Path, **extra: Any) -> None:
    """Persist (merging, never clobbering) this run's location and correlation metadata."""
    state = _run_state(root, run_id)
    state.parent.mkdir(parents=True, exist_ok=True)
    existing = _read_run_state(root, run_id)
    existing["relative_path"] = path.relative_to(root).as_posix()
    for key, value in extra.items():
        if value is not None:
            existing[key] = value
    state.write_text(json.dumps(existing, sort_keys=True) + "\n", encoding="utf-8")


NOSESSION_BUCKET = "nosession"


def session_bucket(session_hash: str | None) -> str:
    """Bucket key for the active-run pointer. Runs/hooks with no known session id all
    share the `nosession` bucket (preserving prior single-session behavior); a run/hook
    with a session id gets its own bucket, so unrelated sessions never see each other's
    active run."""
    return session_hash or NOSESSION_BUCKET


def _active_run_path(root: Path, bucket: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9]+", "-", bucket).strip("-") or NOSESSION_BUCKET
    return root / "state" / "active_run" / f"{safe}.json"


def get_active_run(root: Path, bucket: str) -> dict[str, Any] | None:
    """The most recently started run in this session's bucket that has not yet finished
    (or been marked interrupted). Scoped per-bucket so a concurrent, unrelated session
    never sees (or clobbers) another session's active run."""
    path = _active_run_path(root, bucket)
    if not path.exists():
        return None
    try:
        value = load_json(path)
    except (ValueError, json.JSONDecodeError):
        return None
    return value if value.get("run_id") else None


def set_active_run(root: Path, bucket: str, value: dict[str, Any] | None) -> None:
    path = _active_run_path(root, bucket)
    path.parent.mkdir(parents=True, exist_ok=True)
    if value is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _runs_index_path(root: Path) -> Path:
    return root / "state" / "runs_index.jsonl"


def append_run_index(root: Path, record: dict[str, Any]) -> None:
    """Durable run lookup table so a later session/day can find a run_id without holding the old shell variable."""
    append_jsonl(_runs_index_path(root), record)


def _fingerprint_drift_evidence(sidecar_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Recompute the target skill's live fingerprint so a stale sidecar (generated before a later
    SKILL.md edit) is visible on every run.started instead of silently trusting the stored manifest."""
    try:
        live_fingerprint, _ = target_fingerprint(sidecar_root.parent)
    except OSError:
        return {}
    stored_fingerprint = manifest.get("target", {}).get("fingerprint")
    if not stored_fingerprint:
        return {"live_fingerprint": live_fingerprint}
    return {
        "live_fingerprint": live_fingerprint,
        "fingerprint_stale": live_fingerprint != stored_fingerprint,
    }


def base_event(
    sidecar_root: Path,
    *,
    run_id: str,
    event: str,
    source_kind: str = "semantic",
    attribution: str = "semantic",
    session_id: str | None = None,
    turn_id: str | None = None,
    model: str | None = None,
) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    manifest = load_manifest(sidecar_root)
    config = load_config(sidecar_root)
    root = data_root(sidecar_root, manifest)
    target = manifest.get("target", {})
    evt: dict[str, Any] = {
        "schema": SCHEMA,
        "event_id": str(uuid.uuid4()),
        "run_id": run_id,
        "timestamp": utc_now(),
        "skill": {
            "name": target.get("name", "unknown"),
            "version": target.get("version"),
            "fingerprint": target.get("fingerprint", "unknown"),
        },
        "event": event,
        "source": {
            "kind": source_kind,
            "model": model,
            "session_id_hash": hash_identifier(root, session_id),
            "turn_id_hash": hash_identifier(root, turn_id),
        },
        "attribution": attribution,
        "privacy": {"content_policy": config.get("content_policy", "metadata"), "redactions": 0},
    }
    return evt, root, config


def emit(sidecar_root: Path, event: dict[str, Any]) -> Path:
    manifest = load_manifest(sidecar_root)
    root = data_root(sidecar_root, manifest)
    run_id = str(event["run_id"])
    path = _run_path(root, run_id)
    redacted, count = redact(event)
    redacted.setdefault("privacy", {})["redactions"] = count
    append_jsonl(path, redacted)
    _register_run(root, run_id, path)
    return path


def parse_evidence(text: str | None) -> dict[str, Any]:
    if not text:
        return {}
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("--evidence-json must decode to an object")
    return value


def _close_interrupted_run(sidecar_root: Path, root: Path, stale: dict[str, Any], *, reason: str) -> None:
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


def cmd_start(args: argparse.Namespace, sidecar_root: Path) -> int:
    run_id = args.run_id or str(uuid.uuid4())
    manifest = load_manifest(sidecar_root)
    root = data_root(sidecar_root, manifest)
    bucket = session_bucket(hash_identifier(root, args.session_id))

    stale = get_active_run(root, bucket)
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
    set_active_run(root, bucket, {
        "run_id": run_id,
        "started_at": event["timestamp"],
        "task_category": args.task_category,
        "model": args.model,
        "session_id_hash": event["source"]["session_id_hash"],
    })
    print(run_id)
    return 0


def cmd_event(args: argparse.Namespace, sidecar_root: Path) -> int:
    event, _, _ = base_event(
        sidecar_root,
        run_id=args.run_id,
        event=args.event,
        session_id=args.session_id,
        turn_id=args.turn_id,
        model=args.model,
    )
    evidence = parse_evidence(args.evidence_json)
    if args.operation:
        evidence["operation"] = args.operation
    if args.command_class:
        evidence["command_class"] = args.command_class
    if args.command:
        evidence["command_class"] = evidence.get("command_class") or command_class(args.command)
        evidence["command_sha256"] = hash_text(args.command)
    if args.artifact_ref:
        evidence["artifact_ref"] = args.artifact_ref
    event.update({
        "phase": args.phase,
        "task_category": args.task_category,
        "outcome": args.outcome,
        "failure_class": args.failure_class,
        "duration_ms": args.duration_ms,
        "exit_code": args.exit_code,
        "retry_count": args.retry_count,
        "evidence": evidence,
        "tags": sorted(set(args.tag or [])),
    })
    emit(sidecar_root, event)
    return 0


def cmd_finish(args: argparse.Namespace, sidecar_root: Path) -> int:
    manifest = load_manifest(sidecar_root)
    root = data_root(sidecar_root, manifest)
    state = _read_run_state(root, args.run_id)
    duration_ms = args.duration_ms if args.duration_ms is not None else _elapsed_ms(state.get("started_at"))

    event, _, _ = base_event(
        sidecar_root,
        run_id=args.run_id,
        event="run.finished",
        session_id=args.session_id,
        turn_id=args.turn_id,
        model=args.model,
    )
    event.update({
        "phase": args.phase,
        "outcome": args.outcome,
        "failure_class": args.failure_class,
        "duration_ms": duration_ms,
        "evidence": parse_evidence(args.evidence_json),
        "tags": sorted(set(args.tag or [])),
    })
    emit(sidecar_root, event)

    bucket = session_bucket(state.get("session_id_hash"))
    active = get_active_run(root, bucket)
    if active and str(active.get("run_id")) == args.run_id:
        set_active_run(root, bucket, None)
    append_run_index(root, {
        "run_id": args.run_id,
        "started_at": state.get("started_at"),
        "finished_at": event["timestamp"],
        "outcome": args.outcome,
        "task_category": state.get("task_category"),
    })
    return 0


def cmd_last_run(args: argparse.Namespace, sidecar_root: Path) -> int:
    """Durable lookup for `user.correction` linkage: find the most recent recorded run
    without needing the shell's $RUN_ID from the original session."""
    manifest = load_manifest(sidecar_root)
    root = data_root(sidecar_root, manifest)
    idx_path = _runs_index_path(root)
    if not idx_path.exists():
        return 1
    records: list[dict[str, Any]] = []
    with idx_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                records.append(value)
    if args.task_category:
        records = [r for r in records if r.get("task_category") == args.task_category]
    if args.outcome:
        records = [r for r in records if r.get("outcome") == args.outcome]
    if not records:
        return 1
    records.sort(key=lambda r: str(r.get("finished_at") or r.get("started_at") or ""))
    print(json.dumps(records[-1], sort_keys=True))
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--session-id")
    parser.add_argument("--turn-id")
    parser.add_argument("--model")
    parser.add_argument("--tag", action="append")


OUTCOME_CHOICES = ["success", "failure", "skipped", "unknown", "interrupted"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record privacy-aware semantic telemetry for this skill.")
    parser.add_argument("--sidecar-root", type=Path, default=Path(__file__).resolve().parent)
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--run-id")
    p_start.add_argument("--phase", default="start")
    p_start.add_argument("--task-category")
    p_start.add_argument(
        "--invocation", choices=["explicit", "implicit", "unknown"], default="unknown",
        help="explicit only if the user invoked this skill by name/slash command; implicit only if it was "
             "auto-selected from the task description; unknown (the default) otherwise. A skill cannot "
             "observe its own routing recall, so do not default this to explicit.",
    )
    add_common(p_start)

    p_event = sub.add_parser("event")
    p_event.add_argument("--run-id", required=True)
    p_event.add_argument("--event", required=True)
    p_event.add_argument("--phase")
    p_event.add_argument("--task-category")
    p_event.add_argument("--outcome", choices=OUTCOME_CHOICES)
    p_event.add_argument("--failure-class")
    p_event.add_argument("--duration-ms", type=float)
    p_event.add_argument("--exit-code", type=int)
    p_event.add_argument("--retry-count", type=int)
    p_event.add_argument("--operation")
    p_event.add_argument("--command-class")
    p_event.add_argument("--command", help="Hashed before storage; full command is not persisted under metadata policy.")
    p_event.add_argument("--artifact-ref")
    p_event.add_argument("--evidence-json")
    add_common(p_event)

    p_finish = sub.add_parser("finish")
    p_finish.add_argument("--run-id", required=True)
    p_finish.add_argument("--phase", default="finish")
    p_finish.add_argument("--outcome", choices=OUTCOME_CHOICES, default="success")
    p_finish.add_argument("--failure-class")
    p_finish.add_argument(
        "--duration-ms", type=float,
        help="Optional override. By default the recorder computes this itself from the run's "
             "recorded run.started timestamp, so callers do not need to track wall-clock time.",
    )
    p_finish.add_argument("--evidence-json")
    add_common(p_finish)

    p_last = sub.add_parser("last-run", help="Print the most recently completed/interrupted run as JSON, for durable correction linkage.")
    p_last.add_argument("--task-category")
    p_last.add_argument("--outcome", choices=OUTCOME_CHOICES)

    args = parser.parse_args()
    root = args.sidecar_root.resolve()
    if args.subcommand == "start":
        return cmd_start(args, root)
    if args.subcommand == "event":
        return cmd_event(args, root)
    if args.subcommand == "finish":
        return cmd_finish(args, root)
    if args.subcommand == "last-run":
        return cmd_last_run(args, root)
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"telemetry recorder error: {exc}", file=sys.stderr)
        raise SystemExit(2)
