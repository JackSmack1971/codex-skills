from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import SCHEMA_EVENT, append_jsonl, command_class, load_jsonl, read_json, utc_now


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def numeric_usage(value: Any) -> dict[str, int | float]:
    out: dict[str, int | float] = {}
    if not isinstance(value, dict):
        return out
    for key, item in value.items():
        if isinstance(item, (int, float)) and any(word in str(key).lower() for word in ("token", "cost", "cached")):
            out[str(key)] = item
        elif isinstance(item, dict):
            for sub_key, sub_value in numeric_usage(item).items():
                out[f"{key}.{sub_key}"] = sub_value
    return out


def exit_code_from(item: dict[str, Any]) -> int | None:
    for key in ("exit_code", "exitCode", "status_code", "statusCode"):
        val = item.get(key)
        if isinstance(val, int):
            return val
    return None


def normalized_base(manifest: dict[str, Any], run_id: str, attribution: str) -> dict[str, Any]:
    target = manifest.get("target", {})
    return {
        "schema": SCHEMA_EVENT,
        "event_id": str(uuid.uuid4()),
        "run_id": run_id,
        "timestamp": utc_now(),
        "skill": {
            "name": target.get("name", "unknown"),
            "version": target.get("version"),
            "fingerprint": target.get("fingerprint", "unknown"),
        },
        "source": {"kind": "codex_jsonl", "model": None, "session_id_hash": None, "turn_id_hash": None},
        "attribution": attribution,
        "privacy": {"content_policy": "metadata", "redactions": 0},
    }


def normalize_event(event: dict[str, Any], manifest: dict[str, Any], run_id: str, attribution: str, task_category: str | None) -> dict[str, Any] | None:
    typ = str(event.get("type") or "")
    base = normalized_base(manifest, run_id, attribution)
    base["task_category"] = task_category

    if typ in {"item.started", "item.completed"}:
        item = event.get("item")
        if not isinstance(item, dict):
            return None
        item_type = str(item.get("type") or "unknown")
        evidence: dict[str, Any] = {"codex_event_type": typ, "item_type": item_type}
        command = item.get("command")
        if isinstance(command, str):
            evidence["command_class"] = command_class(command)
            evidence["command_sha256"] = hash_text(command)
        for key in ("name", "tool_name", "server", "path"):
            value = item.get(key)
            if isinstance(value, str):
                if key == "path":
                    evidence["path_sha256"] = hash_text(value)
                else:
                    evidence[key] = value[:200]
        code = exit_code_from(item)
        status = item.get("status")
        outcome = "unknown"
        if typ == "item.completed":
            if code is not None:
                outcome = "success" if code == 0 else "failure"
            elif isinstance(status, str):
                low = status.lower()
                if low in {"completed", "success", "succeeded"}:
                    outcome = "success"
                elif low in {"failed", "error"}:
                    outcome = "failure"
        base.update({
            "event": "operation",
            "phase": "codex_trace",
            "outcome": outcome,
            "exit_code": code,
            "evidence": evidence,
        })
        return base

    if typ == "turn.completed":
        usage = numeric_usage(event)
        base.update({"event": "usage", "phase": "codex_trace", "outcome": "success", "evidence": {"usage": usage}})
        return base

    if "error" in typ.lower() or typ.lower().endswith("failed"):
        message = event.get("message") or event.get("error")
        evidence: dict[str, Any] = {"codex_event_type": typ}
        if isinstance(message, str):
            evidence["message_length"] = len(message)
            evidence["message_sha256"] = hash_text(message)
        elif isinstance(message, dict):
            evidence["error_keys"] = sorted(str(k) for k in message.keys())[:50]
        base.update({
            "event": "failure",
            "phase": "codex_trace",
            "outcome": "failure",
            "failure_class": "codex_trace_error",
            "evidence": evidence,
        })
        return base

    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Import codex exec --json JSONL into normalized skill telemetry.")
    parser.add_argument("trace", type=Path)
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--attribution", choices=["confirmed", "candidate"], default="candidate")
    parser.add_argument("--run-id")
    parser.add_argument("--task-category")
    args = parser.parse_args()

    sidecar = args.sidecar.resolve()
    manifest = read_json(sidecar / "manifest.json")
    events = load_jsonl(args.trace.resolve())
    run_id = args.run_id or str(uuid.uuid4())
    day = datetime.now(timezone.utc).date().isoformat()
    out = sidecar / "raw" / "imported" / day / f"{run_id}.jsonl"

    start = normalized_base(manifest, run_id, args.attribution)
    start.update({
        "event": "run.started",
        "phase": "codex_trace",
        "task_category": args.task_category,
        "outcome": "unknown",
        "evidence": {"source_trace_sha256": hashlib.sha256(args.trace.read_bytes()).hexdigest()},
    })
    append_jsonl(out, start)

    count = 0
    failures = 0
    for raw in events:
        normalized = normalize_event(raw, manifest, run_id, args.attribution, args.task_category)
        if normalized is not None:
            append_jsonl(out, normalized)
            count += 1
            failures += int(normalized.get("outcome") == "failure")

    finish = normalized_base(manifest, run_id, args.attribution)
    finish.update({
        "event": "run.finished",
        "phase": "codex_trace",
        "task_category": args.task_category,
        "outcome": "failure" if failures else "success",
        "evidence": {"normalized_events": count, "failure_events": failures},
    })
    append_jsonl(out, finish)
    print(json.dumps({"run_id": run_id, "output": str(out), "normalized_events": count, "failures": failures}, indent=2))


if __name__ == "__main__":
    main()
