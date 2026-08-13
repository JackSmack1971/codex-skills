"""Evidence-only grader for the routing benchmark."""

from __future__ import annotations

from typing import Any

from .runtime import classify_runtime

SELECTION_EVENTS = {"skill_selected", "skill_loaded"}


def selected_skills(events: list[dict[str, Any]]) -> tuple[list[str], bool]:
    """Return explicitly evidenced skills and whether telemetry was present."""
    skills: list[str] = []
    selection_telemetry = False
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("type") not in SELECTION_EVENTS:
            continue
        selection_telemetry = True
        name = event.get("name")
        if isinstance(name, str) and name.strip() and name not in skills:
            skills.append(name)
    return skills, selection_telemetry


def grade_routing(case: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    """Grade routing from a case contract and normalized runtime events.

    Response text is intentionally never inspected. Runtime health is reported
    independently so a successful execution cannot imply correct routing.
    """
    actual, selection_telemetry = selected_skills(events)
    malformed = any(
        not isinstance(event, dict)
        or (
            event.get("type") in SELECTION_EVENTS
            and (not isinstance(event.get("name"), str) or not event["name"].strip())
        )
        for event in events
    )
    expected = case.get("expected_primary_skill")
    alternatives = case.get("acceptable_alternative_skills", [])
    forbidden = case.get("forbidden_skills", [])
    sequence = case.get("expected_skill_sequence")
    evidence_state = "UNKNOWN" if selection_telemetry else "UNAVAILABLE" if not events else "UNKNOWN"
    reasons: list[str] = []
    if malformed:
        reasons.append("malformed_event")

    if expected is None:
        primary_verdict = "NOT_APPLICABLE"
    elif expected in actual:
        primary_verdict = "PASS"
        reasons.append("primary_selected")
    elif any(skill in actual for skill in alternatives):
        primary_verdict = "ACCEPTED"
        reasons.append("acceptable_alternative_selected")
    else:
        primary_verdict = evidence_state
        reasons.append("selection_evidence_unavailable" if primary_verdict != "FAIL" else "wrong_primary_selected")
        if actual:
            primary_verdict = "FAIL"
            reasons[-1] = "wrong_primary_selected"

    if not forbidden:
        forbidden_verdict = "NOT_APPLICABLE"
    elif not selection_telemetry:
        forbidden_verdict = evidence_state
        reasons.append("forbidden_activation_unverifiable")
    else:
        activated = sorted(set(actual) & set(forbidden))
        forbidden_verdict = "FAIL" if activated else "PASS"
        reasons.append("forbidden_skill_activated" if activated else "no_forbidden_skill_activated")

    if sequence is None:
        sequence_verdict = "NOT_SPECIFIED"
    elif not selection_telemetry:
        sequence_verdict = evidence_state
        reasons.append("sequence_evidence_unavailable")
    else:
        sequence_verdict = "PASS" if actual == sequence else "FAIL"
        reasons.append("expected_sequence_observed" if sequence_verdict == "PASS" else "unexpected_skill_sequence")

    alternative = "NOT_USED"
    if primary_verdict == "ACCEPTED":
        alternative = "ACCEPTED"
    elif alternatives and not actual and not selection_telemetry:
        alternative = evidence_state

    routing_verdict = "FAIL" if "FAIL" in {primary_verdict, forbidden_verdict, sequence_verdict} else "PASS"
    if routing_verdict == "PASS" and any(
        verdict in {"UNKNOWN", "UNAVAILABLE"}
        for verdict in (primary_verdict, forbidden_verdict, sequence_verdict)
    ):
        routing_verdict = evidence_state
    return {
        "case_id": case.get("case_id"),
        "expected_primary_skill": expected,
        "actual_selected_skills": actual,
        "selection_telemetry": selection_telemetry,
        "runtime_health": classify_runtime(events),
        "primary_selection_verdict": primary_verdict,
        "forbidden_activation_verdict": forbidden_verdict,
        "acceptable_alternative_handling": alternative,
        "expected_composition_sequence_verdict": sequence_verdict,
        "routing_verdict": routing_verdict,
        "reason_codes": sorted(set(reasons)),
    }
