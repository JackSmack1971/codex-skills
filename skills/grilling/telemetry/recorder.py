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


def _run_state(root: Path, run_id: str) -> Path:
    return root / "state" / "runs" / f"{run_id}.json"


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


def _register_run(root: Path, run_id: str, path: Path) -> None:
    state = _run_state(root, run_id)
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"relative_path": path.relative_to(root).as_posix()}) + "\n", encoding="utf-8")


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


def cmd_start(args: argparse.Namespace, sidecar_root: Path) -> int:
    run_id = args.run_id or str(uuid.uuid4())
    event, _, _ = base_event(
        sidecar_root,
        run_id=run_id,
        event="run.started",
        session_id=args.session_id,
        turn_id=args.turn_id,
        model=args.model,
    )
    event.update({
        "phase": args.phase,
        "task_category": args.task_category,
        "outcome": "unknown",
        "evidence": {"invocation": args.invocation},
        "tags": sorted(set(args.tag or [])),
    })
    emit(sidecar_root, event)
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
        "duration_ms": args.duration_ms,
        "evidence": parse_evidence(args.evidence_json),
        "tags": sorted(set(args.tag or [])),
    })
    emit(sidecar_root, event)
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--session-id")
    parser.add_argument("--turn-id")
    parser.add_argument("--model")
    parser.add_argument("--tag", action="append")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record privacy-aware semantic telemetry for this skill.")
    parser.add_argument("--sidecar-root", type=Path, default=Path(__file__).resolve().parent)
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--run-id")
    p_start.add_argument("--phase", default="start")
    p_start.add_argument("--task-category")
    p_start.add_argument("--invocation", choices=["explicit", "implicit", "unknown"], default="unknown")
    add_common(p_start)

    p_event = sub.add_parser("event")
    p_event.add_argument("--run-id", required=True)
    p_event.add_argument("--event", required=True)
    p_event.add_argument("--phase")
    p_event.add_argument("--task-category")
    p_event.add_argument("--outcome", choices=["success", "failure", "skipped", "unknown"])
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
    p_finish.add_argument("--outcome", choices=["success", "failure", "skipped", "unknown"], default="success")
    p_finish.add_argument("--failure-class")
    p_finish.add_argument("--duration-ms", type=float)
    p_finish.add_argument("--evidence-json")
    add_common(p_finish)

    args = parser.parse_args()
    root = args.sidecar_root.resolve()
    if args.subcommand == "start":
        return cmd_start(args, root)
    if args.subcommand == "event":
        return cmd_event(args, root)
    if args.subcommand == "finish":
        return cmd_finish(args, root)
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"telemetry recorder error: {exc}", file=sys.stderr)
        raise SystemExit(2)
