"""Build deterministic metrics and confusion reports from routing result artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _ratio(count: int, total: int) -> dict[str, Any]:
    return {"count": count, "total": total, "rate": count / total if total else None}


def _cases(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    result = artifact.get("result", artifact)
    if isinstance(result, dict) and isinstance(result.get("cases"), list):
        return [case for case in result["cases"] if isinstance(case, dict)]
    return []


def _available(case: dict[str, Any]) -> bool:
    if case.get("selection_telemetry") is True or case.get("implicit_routing_status") == "AVAILABLE":
        return True
    return bool(case.get("actual_selected_skills"))


def _unknown(case: dict[str, Any]) -> bool:
    return not _available(case) and case.get("runtime_health") not in {"UNAVAILABLE", "FAIL"}


def _unavailable(case: dict[str, Any]) -> bool:
    return not _available(case) and case.get("runtime_health") == "UNAVAILABLE"


def analyze(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    cases = [case for artifact in artifacts for case in _cases(artifact)]
    eligible = [case for case in cases if case.get("expected_primary_skill") is not None]
    observed = [case for case in eligible if _available(case)]
    exact = lambda case: case.get("primary_selection_verdict") == "PASS"
    alternatives = lambda case: case.get("acceptable_alternative_handling") == "ACCEPTED" or case.get("primary_selection_verdict") == "ACCEPTED"
    metric = {
        "primary_selection_accuracy": _ratio(sum(exact(c) for c in observed), len(observed)),
        "unknown_rate": _ratio(sum(_unknown(c) for c in eligible), len(eligible)),
        "unavailable_rate": _ratio(sum(_unavailable(c) for c in eligible), len(eligible)),
        "false_activation_rate": _ratio(sum(bool(c.get("actual_selected_skills")) and not exact(c) and not alternatives(c) for c in observed), len(observed)),
        "forbidden_skill_activation_rate": _ratio(sum(bool(c.get("forbidden_skills")) and c.get("forbidden_activation_verdict") == "FAIL" for c in observed), sum(bool(c.get("forbidden_skills")) for c in observed)),
        "missed_specialist_rate": _ratio(sum(not exact(c) and not alternatives(c) for c in observed), len(observed)),
        "acceptable_alternative_rate": _ratio(sum(alternatives(c) for c in observed), len(observed)),
        "unnecessary_multi_skill_composition_rate": _ratio(sum(len(c.get("actual_selected_skills", [])) > 1 and c.get("expected_composition_sequence_verdict") in {None, "NOT_SPECIFIED", "FAIL"} for c in observed), len(observed)),
    }
    per_skill: dict[str, dict[str, Any]] = {}
    for skill in sorted({c["expected_primary_skill"] for c in eligible if c.get("expected_primary_skill")}):
        rows = [c for c in observed if c.get("expected_primary_skill") == skill]
        per_skill[skill] = {"accuracy": _ratio(sum(exact(c) for c in rows), len(rows)), "sample_count": len(rows)}

    confusions: dict[str, Counter[str]] = defaultdict(Counter)
    for case in observed:
        expected = case.get("expected_primary_skill")
        actual = (case.get("actual_selected_skills") or ["UNKNOWN"])[0]
        if expected:
            confusions[expected][actual] += 1
    confusion_counts = {expected: dict(sorted(counts.items())) for expected, counts in sorted(confusions.items())}
    confusion_rates = {expected: {actual: _ratio(count, len([c for c in observed if c.get("expected_primary_skill") == expected])) for actual, count in sorted(counts.items())} for expected, counts in sorted(confusions.items())}
    top_confusions = sorted(
        ({"expected": expected, "actual": actual, "count": count} for expected, counts in confusions.items() for actual, count in counts.items() if actual != expected),
        key=lambda edge: (-edge["count"], edge["expected"], edge["actual"]),
    )

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        group = case.get("group_id") or case.get("counterfactual_group_id")
        if group and (case.get("case_kind") == "counterfactual" or "counterfactual_group_id" in case):
            groups[group].append(case)
    group_pass = sum(all(_available(c) and c.get("routing_verdict") == "PASS" for c in rows) for rows in groups.values())
    return {
        "schema_version": 1,
        "metadata": {
            "artifact_count": len(artifacts),
            "case_count": len(cases),
            "runtime_versions": sorted({version for artifact in artifacts for version in [artifact.get("result", artifact).get("version")] if version}),
            "codex_versions": sorted({version for artifact in artifacts for version in [artifact.get("result", artifact).get("codex_version")] if version}),
        },
        "metrics": metric,
        "per_skill": per_skill,
        "confusions": confusion_counts,
        "confusion_rates": confusion_rates,
        "high_confusion_boundaries": top_confusions,
        "counterfactual_groups": {"pass_rate": _ratio(group_pass, len(groups)), "groups": {name: all(_available(c) and c.get("routing_verdict") == "PASS" for c in rows) for name, rows in sorted(groups.items())}},
    }


def markdown_report(report: dict[str, Any]) -> str:
    m = report["metrics"]
    pct = lambda item: "n/a" if item["rate"] is None else f"{item['rate']:.1%}"
    lines = ["# Routing analysis", "", f"Cases: {report['metadata']['case_count']} across {report['metadata']['artifact_count']} artifact(s).", "", "## Metrics"]
    labels = [("primary_selection_accuracy", "Primary-selection accuracy"), ("unknown_rate", "UNKNOWN rate"), ("unavailable_rate", "UNAVAILABLE rate"), ("false_activation_rate", "False activation rate"), ("forbidden_skill_activation_rate", "Forbidden-skill activation rate"), ("missed_specialist_rate", "Missed specialist rate"), ("acceptable_alternative_rate", "Acceptable-alternative rate"), ("unnecessary_multi_skill_composition_rate", "Unnecessary multi-skill composition rate")]
    for key, label in labels:
        item = m[key]
        lines.append(f"- {label}: {item['count']}/{item['total']} ({pct(item)})")
    lines += ["", "## Highest-confusion boundaries and front-door/specialist misroutes", ""]
    for edge in report["high_confusion_boundaries"][:5]:
        total = report["per_skill"].get(edge["expected"], {}).get("accuracy", {}).get("total", 0)
        lines.append(f"- {edge['expected']} -> {edge['actual']}: {edge['count']}/{total}")
    lines += ["", "## Confusion graph"]
    for expected, actuals in report["confusion_rates"].items():
        total = report["per_skill"].get(expected, {}).get("accuracy", {}).get("total", 0)
        for actual, item in actuals.items():
            if actual != expected:
                lines.append(f"- {expected} -> {actual}: {item['count']}/{total} ({pct(item)})")
    lines += ["", f"Counterfactual group pass rate: {report['counterfactual_groups']['pass_rate']['count']}/{report['counterfactual_groups']['pass_rate']['total']} ({pct(report['counterfactual_groups']['pass_rate'])})", "", "Rates are descriptive; small samples do not establish statistical confidence.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()
    artifacts = [json.loads(path.read_text(encoding="utf-8")) for path in args.artifacts]
    report = analyze(artifacts)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_out.write_text(markdown_report(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
