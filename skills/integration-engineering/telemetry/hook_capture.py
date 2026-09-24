#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from recorder import (
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
)

CLOSING_HOOKS = {"Stop", "SessionEnd"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def find_first_number(value: Any, names: set[str]) -> int | float | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in names and isinstance(item, (int, float)):
                return item
        for item in value.values():
            found = find_first_number(item, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_first_number(item, names)
            if found is not None:
                return found
    return None


def _close_interrupted(sidecar: Path, root: Path, active: dict[str, Any], *, reason: str) -> None:
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
    set_active_run(root, None)


def main() -> int:
    sidecar = Path(__file__).resolve().parent
    manifest = load_manifest(sidecar)
    config = load_config(sidecar)
    root = data_root(sidecar, manifest)

    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        return 0

    event_name = str(payload.get("hook_event_name") or "unknown")
    session_id = str(payload.get("session_id") or "")
    turn_id = str(payload.get("turn_id") or "")
    session_hash = hash_identifier(root, session_id) or "nosession"
    turn_hash = hash_identifier(root, turn_id) or "noturn"

    # Correlate to the semantic run currently in flight for this sidecar (if any), rather than
    # stranding execution evidence in the `ambient` bucket forever. Scoped to the same session
    # when a session id is known, so unrelated concurrent sessions don't cross-attribute.
    active = get_active_run(root)
    correlated = bool(active) and (
        not active.get("session_id_hash") or active.get("session_id_hash") == session_hash
    )

    if event_name in CLOSING_HOOKS and correlated:
        _close_interrupted(sidecar, root, active, reason=f"hook:{event_name}")
        return 0

    target = manifest.get("target", {})
    evidence: dict[str, Any] = {"hook_event": event_name}

    prompt = payload.get("prompt")
    if isinstance(prompt, str):
        evidence["prompt_length"] = len(prompt)
        evidence["prompt_sha256"] = hash_text(prompt)

    tool_name = payload.get("tool_name")
    if isinstance(tool_name, str):
        evidence["tool_name"] = tool_name

    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            evidence["command_class"] = command_class(command)
            evidence["command_sha256"] = hash_text(command)
        evidence["tool_input_keys"] = sorted(str(k) for k in tool_input.keys())[:50]

    tool_response = payload.get("tool_response")
    if tool_response is not None:
        evidence["tool_response_present"] = True
        code = find_first_number(tool_response, {"exit_code", "exitcode", "status_code"})
        if code is not None:
            evidence["observed_status_code"] = code

    run_id = str(active["run_id"]) if correlated else (
        "ambient-" + hashlib.sha256(f"{session_hash}:{turn_hash}".encode()).hexdigest()[:24]
    )

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
        "event": "hook.observation",
        "source": {
            "kind": "hook",
            "model": payload.get("model"),
            "session_id_hash": session_hash,
            "turn_id_hash": turn_hash,
        },
        "attribution": "correlated" if correlated else "ambient",
        "outcome": "unknown",
        "evidence": evidence,
        "privacy": {"content_policy": config.get("content_policy", "metadata"), "redactions": 0},
    }
    redacted, count = redact(event)
    redacted["privacy"]["redactions"] = count
    if correlated:
        path = _run_path(root, run_id)
        append_jsonl(path, redacted)
        _register_run(root, run_id, path)
    else:
        day = datetime.now(timezone.utc).date().isoformat()
        append_jsonl(root / "ambient" / day / f"{run_id}.jsonl", redacted)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Hooks should fail open for telemetry collection. Do not block Codex work because logging failed.
        print(f"skill telemetry hook warning: {exc}", file=sys.stderr)
        raise SystemExit(0)
