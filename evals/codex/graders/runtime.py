"""Evidence-only grading helpers for Codex runtime JSONL fixtures."""

from typing import Any


def classify_runtime(events: list[dict[str, Any]]) -> str:
    if not events:
        return "UNAVAILABLE"
    if any(not isinstance(event, dict) for event in events):
        return "FAIL"
    if any(event.get("type") in {"error", "turn.failed"} for event in events):
        return "FAIL"
    return "PASS"


def selected_skill(events: list[dict[str, Any]]) -> str:
    """Never infer implicit selection from response text."""
    for event in events:
        if (
            isinstance(event, dict)
            and event.get("type") in {"skill_selected", "skill_loaded"}
            and isinstance(event.get("name"), str)
            and event["name"].strip()
        ):
            return event["name"]
    return "UNKNOWN"
