#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from recorder import append_jsonl, command_class, data_root, hash_identifier, hash_text, load_config, load_manifest, redact


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
    run_id = "ambient-" + hashlib.sha256(f"{session_hash}:{turn_hash}".encode()).hexdigest()[:24]

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
        "attribution": "ambient",
        "outcome": "unknown",
        "evidence": evidence,
        "privacy": {"content_policy": config.get("content_policy", "metadata"), "redactions": 0},
    }
    redacted, count = redact(event)
    redacted["privacy"]["redactions"] = count
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
