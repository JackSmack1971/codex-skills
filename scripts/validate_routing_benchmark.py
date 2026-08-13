"""Validate the deterministic routing benchmark contract and coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "benchmarks/routing/schema.json"
CASES = ROOT / "benchmarks/routing/cases.json"
STATE = ROOT / "docs/skill-state.json"
REQUIRED_SOURCES = {"tests/skill-routing-cases.json", "benchmarks/core/behavioral-cases.json"}
REQUIRED_GROUPS = {
    "testing-qa-vs-test-driven-development",
    "review-agent-vs-pr-review",
    "product-discovery-vs-mvp-scope-vs-product-spec",
    "feature-implementation-vs-vertical-slice",
    "skill-creator-vs-context7-skill-wizard",
    "context-doctor-vs-skill-auditor-vs-improve",
    "git-commit-vs-git-workflow-vs-github-issue-to-pr",
}
KINDS = {"positive", "exclusion", "ambiguous", "counterfactual"}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: dict[str, Any], state: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not _nonempty_string(data.get("artifact_policy")) or "metadata-only" not in data["artifact_policy"]:
        errors.append("artifact_policy must declare metadata-only output")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources or not all(_nonempty_string(item) for item in sources):
        errors.append("sources must be a non-empty list of paths")
    else:
        for source in sources:
            if not (root / source).is_file():
                errors.append(f"source does not exist: {source}")
        missing = REQUIRED_SOURCES - set(sources)
        errors.extend(f"required source missing: {source}" for source in sorted(missing))

    skills = {item.get("name") for item in state.get("skills", []) if isinstance(item, dict)}
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]
    ids: set[str] = set()
    groups: dict[str, list[dict[str, Any]]] = {}
    source_counts: dict[str, int] = {}
    for case in cases:
        if not isinstance(case, dict):
            errors.append("case must be an object")
            continue
        case_id = case.get("case_id")
        label = case_id if _nonempty_string(case_id) else "<case>"
        if not _nonempty_string(case_id):
            errors.append("case_id must be a non-empty string")
        elif case_id in ids:
            errors.append(f"duplicate case_id: {case_id}")
        else:
            ids.add(case_id)
        for field in ("prompt", "source", "source_case_id"):
            if not _nonempty_string(case.get(field)):
                errors.append(f"{label}: {field} must be a non-empty string")
        kind = case.get("case_kind")
        if kind not in KINDS:
            errors.append(f"{label}: invalid case_kind")
        for field in ("acceptable_alternative_skills", "forbidden_skills"):
            value = case.get(field)
            if not isinstance(value, list) or any(not _nonempty_string(item) for item in value):
                errors.append(f"{label}: {field} must be a list of skill names")
            elif len(value) != len(set(value)):
                errors.append(f"{label}: {field} contains duplicates")
        primary = case.get("expected_primary_skill")
        if primary is not None and not _nonempty_string(primary):
            errors.append(f"{label}: expected_primary_skill must be a skill name or null")
        sequence = case.get("expected_skill_sequence")
        if sequence is not None and (not isinstance(sequence, list) or not sequence or any(not _nonempty_string(item) for item in sequence)):
            errors.append(f"{label}: expected_skill_sequence must be a non-empty list of skill names")
        alternatives = case.get("acceptable_alternative_skills", [])
        forbidden = case.get("forbidden_skills", [])
        referenced = ([primary] if primary else []) + alternatives + forbidden + (sequence or [])
        errors.extend(f"{label}: unknown skill {skill}" for skill in sorted(set(referenced) - skills))
        overlap = ({primary} if primary else set()) | set(alternatives) | set(sequence or [])
        overlap &= set(forbidden)
        errors.extend(f"{label}: skill is both expected and forbidden: {skill}" for skill in sorted(overlap))
        group = case.get("group_id")
        if group is not None:
            if not _nonempty_string(group):
                errors.append(f"{label}: group_id must be a non-empty string")
            else:
                groups.setdefault(group, []).append(case)
        source = case.get("source")
        source_counts[source] = source_counts.get(source, 0) + 1
        if source not in sources:
            errors.append(f"{label}: source is not declared: {source}")
        if kind == "positive" and primary is None:
            errors.append(f"{label}: positive case requires expected_primary_skill")
        if kind == "counterfactual" and group is None:
            errors.append(f"{label}: counterfactual case requires group_id")

    for group in sorted(REQUIRED_GROUPS):
        members = groups.get(group, [])
        if len(members) < 2:
            errors.append(f"{group}: requires at least 2 cases")
        if not any(case.get("case_kind") == "counterfactual" for case in members):
            errors.append(f"{group}: requires a counterfactual case")
        skills_in_group = {case.get("expected_primary_skill") for case in members} - {None}
        if len(skills_in_group) < 2:
            errors.append(f"{group}: requires at least 2 expected routes")
    if not source_counts.get("tests/skill-routing-cases.json"):
        errors.append("routing fixture source has no cases")
    if not source_counts.get("benchmarks/core/behavioral-cases.json"):
        errors.append("Core behavioral source has no cases")
    return sorted(set(errors))


def main() -> int:
    try:
        data = json.loads(CASES.read_text(encoding="utf-8"))
        state = json.loads(STATE.read_text(encoding="utf-8"))
        json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"routing benchmark unreadable: {exc}")
        return 1
    errors = validate(data, state)
    if errors:
        print("\n".join(errors))
        print("ROUTING_BENCHMARK_VALIDATION_FAILED")
        return 1
    print(f"ROUTING_BENCHMARK_VALIDATED={len(data['cases'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
