"""Create and compare metadata-only routing baselines."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.analyze_routing_results import _available, _cases, _unknown, _unavailable


SCHEMA_VERSION = 1


def _actual(case: dict[str, Any]) -> str:
    return (case.get("actual_selected_skills") or ["UNKNOWN"])[0]


def _snapshot(case: dict[str, Any]) -> dict[str, Any]:
    available = _available(case)
    return {
        "expected_primary_skill": case.get("expected_primary_skill"),
        "actual_primary_skill": _actual(case) if available else None,
        "available": available,
        "unknown": _unknown(case),
        "unavailable": _unavailable(case),
        "primary_pass": case.get("primary_selection_verdict") == "PASS",
        "forbidden_activation": case.get("forbidden_activation_verdict") == "FAIL",
        "routing_pass": case.get("routing_verdict") == "PASS",
        "group_id": case.get("group_id") or case.get("counterfactual_group_id"),
        "case_kind": case.get("case_kind"),
        "core_boundary": case.get("core_boundary", str(case.get("source", "")).startswith("benchmarks/core/")),
    }


def create_baseline(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    cases: dict[str, dict[str, Any]] = {}
    runtime_versions: set[str] = set()
    codex_versions: set[str] = set()
    for artifact in artifacts:
        result = artifact.get("result", artifact)
        if result.get("version"):
            runtime_versions.add(result["version"])
        if result.get("codex_version"):
            codex_versions.add(result["codex_version"])
        for case in _cases(artifact):
            case_id = case.get("case_id")
            if case_id:
                cases[case_id] = _snapshot(case)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "routing-baseline",
        "artifact_policy": "metadata-only: no prompts, response bodies, transcripts, or secrets",
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_versions": sorted(runtime_versions),
            "codex_versions": sorted(codex_versions),
            "case_count": len(cases),
        },
        "cases": dict(sorted(cases.items())),
    }


def _ratio(count: int, total: int) -> dict[str, Any]:
    return {"count": count, "total": total, "rate": count / total if total else None}


def _metrics(cases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    eligible = [case for case in cases.values() if case.get("expected_primary_skill") is not None]
    observed = [case for case in eligible if case.get("available")]
    per_skill: dict[str, dict[str, Any]] = {}
    core_per_skill: dict[str, dict[str, Any]] = {}
    for skill in sorted({case["expected_primary_skill"] for case in eligible}):
        rows = [case for case in observed if case["expected_primary_skill"] == skill]
        per_skill[skill] = _ratio(sum(case["primary_pass"] for case in rows), len(rows))
        core_rows = [case for case in rows if case.get("core_boundary")]
        if core_rows:
            core_per_skill[skill] = _ratio(sum(case["primary_pass"] for case in core_rows), len(core_rows))
    confusions: Counter[tuple[str, str]] = Counter(
        (case["expected_primary_skill"], case["actual_primary_skill"])
        for case in observed
        if case.get("actual_primary_skill")
    )
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases.values():
        if case.get("group_id") and case.get("case_kind") == "counterfactual":
            groups[case["group_id"]].append(case)
    group_pass = {group: all(row["available"] and row["routing_pass"] for row in rows) for group, rows in groups.items()}
    return {
        "eligible": len(eligible),
        "observed": len(observed),
        "per_skill_accuracy": per_skill,
        "protected_core_accuracy": core_per_skill,
        "confusions": {f"{expected}->{actual}": count for (expected, actual), count in sorted(confusions.items()) if expected != actual},
        "forbidden_activations": _ratio(sum(case["forbidden_activation"] for case in observed), len(observed)),
        "unknown": _ratio(sum(case["unknown"] for case in eligible), len(eligible)),
        "unavailable": _ratio(sum(case["unavailable"] for case in eligible), len(eligible)),
        "counterfactual_groups": {"pass": sum(group_pass.values()), "total": len(group_pass), "results": dict(sorted(group_pass.items()))},
    }


def _delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    return {"baseline": baseline, "candidate": candidate, "delta": candidate["rate"] - baseline["rate"] if candidate["rate"] is not None and baseline["rate"] is not None else None}


def compare(baseline: dict[str, Any], candidate: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    if baseline.get("schema_version") != SCHEMA_VERSION or candidate.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"baseline and candidate must use schema_version {SCHEMA_VERSION}")
    policy = {"zero_new_forbidden_activations": True, "protected_core_max_accuracy_regression": 0.0, "unknown_unavailable_tolerance": 0.0, **(policy or {})}
    base_cases, cand_cases = baseline.get("cases", {}), candidate.get("cases", {})
    common = sorted(set(base_cases) & set(cand_cases))
    base = {case_id: base_cases[case_id] for case_id in common}
    cand = {case_id: cand_cases[case_id] for case_id in common}
    bm, cm = _metrics(base), _metrics(cand)
    skills = sorted(set(bm["per_skill_accuracy"]) | set(cm["per_skill_accuracy"]))
    per_skill = {}
    for skill in skills:
        before, after = bm["per_skill_accuracy"].get(skill, _ratio(0, 0)), cm["per_skill_accuracy"].get(skill, _ratio(0, 0))
        per_skill[skill] = _delta(after, before)
    base_edges, cand_edges = set(bm["confusions"]), set(cm["confusions"])
    new_forbidden = sorted(case_id for case_id in common if not base[case_id]["forbidden_activation"] and cand[case_id]["forbidden_activation"])
    groups = sorted(set(bm["counterfactual_groups"]["results"]) | set(cm["counterfactual_groups"]["results"]))
    group_changes = {group: {"baseline": bm["counterfactual_groups"]["results"].get(group), "candidate": cm["counterfactual_groups"]["results"].get(group), "delta": int(cm["counterfactual_groups"]["results"].get(group, False)) - int(bm["counterfactual_groups"]["results"].get(group, False))} for group in groups}
    runtime_changed = set(baseline.get("metadata", {}).get("runtime_versions", [])) != set(candidate.get("metadata", {}).get("runtime_versions", [])) or set(baseline.get("metadata", {}).get("codex_versions", [])) != set(candidate.get("metadata", {}).get("codex_versions", []))
    unknown_delta = _delta(cm["unknown"], bm["unknown"])
    unavailable_delta = _delta(cm["unavailable"], bm["unavailable"])
    violations = []
    if policy["zero_new_forbidden_activations"] and new_forbidden:
        violations.append({"policy": "zero_new_forbidden_activations", "case_ids": new_forbidden})
    protected_limit = float(policy["protected_core_max_accuracy_regression"])
    protected = {skill: item for skill, item in per_skill.items() if skill in set(policy.get("protected_core_skills", []))}
    core_before, core_after = bm["protected_core_accuracy"], cm["protected_core_accuracy"]
    for skill in sorted(set(core_before) | set(core_after)):
        before, after = core_before.get(skill, _ratio(0, 0)), core_after.get(skill, _ratio(0, 0))
        if before["rate"] is not None and after["rate"] is not None:
            protected[skill] = _delta(after, before)
    protected_bad = {skill: item["delta"] for skill, item in protected.items() if item["delta"] is not None and item["delta"] < -protected_limit}
    if protected_bad:
        violations.append({"policy": "protected_core_max_accuracy_regression", "skills": protected_bad})
    tolerance = float(policy["unknown_unavailable_tolerance"])
    if any(item["delta"] is not None and item["delta"] > tolerance for item in (unknown_delta, unavailable_delta)):
        violations.append({"policy": "unknown_unavailable_tolerance", "unknown": unknown_delta, "unavailable": unavailable_delta})
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "routing-baseline-comparison",
        "metadata": {"common_case_count": len(common), "baseline_only_case_count": len(set(base_cases) - set(cand_cases)), "candidate_only_case_count": len(set(cand_cases) - set(base_cases))},
        "runtime_comparison": {"material_version_change": runtime_changed, "baseline": {"runtime_versions": baseline.get("metadata", {}).get("runtime_versions", []), "codex_versions": baseline.get("metadata", {}).get("codex_versions", [])}, "candidate": {"runtime_versions": candidate.get("metadata", {}).get("runtime_versions", []), "codex_versions": candidate.get("metadata", {}).get("codex_versions", [])}, "causal_evidence": "flagged" if runtime_changed else "same-runtime"},
        "per_skill_accuracy_delta": per_skill,
        "new_confusion_edges": sorted(cand_edges - base_edges),
        "resolved_confusion_edges": sorted(base_edges - cand_edges),
        "forbidden_activation_regressions": new_forbidden,
        "counterfactual_group_changes": group_changes,
        "counterfactual_regressions": sorted(group for group, change in group_changes.items() if change["delta"] < 0),
        "counterfactual_improvements": sorted(group for group, change in group_changes.items() if change["delta"] > 0),
        "unknown_delta": unknown_delta,
        "unavailable_delta": unavailable_delta,
        "overall": {"baseline": bm, "candidate": cm},
        "policy": {"config": policy, "violations": violations, "status": "FAIL" if violations else "PASS"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("artifacts", nargs="+", type=Path)
    create.add_argument("--output", type=Path, required=True)
    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("baseline", type=Path)
    compare_parser.add_argument("candidate", type=Path)
    compare_parser.add_argument("--policy", type=Path)
    compare_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "create":
        result = create_baseline([json.loads(path.read_text(encoding="utf-8")) for path in args.artifacts])
    else:
        policy = json.loads(args.policy.read_text(encoding="utf-8")) if args.policy else None
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
        if candidate.get("kind") != "routing-baseline":
            candidate = create_baseline([candidate])
        result = compare(baseline, candidate, policy)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if args.command == "compare" and result["policy"]["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
