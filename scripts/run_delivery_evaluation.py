"""Run skill-specific, fixture-backed delivery artifact checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "benchmarks" / "core" / "delivery-behavioral-cases.json"


def checks_for(skill: str, artifact: dict) -> list[tuple[str, bool]]:
    if skill == "product-discovery":
        experiment = artifact["experiments"][0]
        return [("facts/evidence and assumptions are separate", bool(artifact["evidence"] and artifact["assumptions"])),
                ("riskiest assumption is named", bool(artifact["riskiest_assumptions"])),
                ("experiment has signal and decision rule", bool(experiment["signal"] and experiment["decision_rule"])),
                ("does not prescribe a solution", artifact["solution_design"] is None)]
    if skill == "product-spec":
        required = {"User", "Problem", "Journey", "Functional Requirements", "Non-Functional Requirements", "States and Errors", "Permissions", "Acceptance Criteria", "Analytics", "Out of Scope", "Open Questions"}
        return [("has the complete specification contract", required <= set(artifact["sections"])),
                ("covers observable states", {"loading", "empty", "success", "failure", "retry", "recovery"} <= set(artifact["states"])),
                ("acceptance criteria has given/when/then", all(set(row) >= {"given", "when", "then"} for row in artifact["acceptance_criteria"])),
                ("does not prescribe technology", artifact["technology_choice"] is None)]
    if skill == "acceptance-criteria":
        return [("criterion is observable Given/When/Then", all(set(row) >= {"given", "when", "then"} for row in artifact["criteria"])),
                ("criteria trace to requirements", bool(artifact["trace"])),
                ("does not prescribe implementation", artifact["implementation_steps"] is None)]
    if skill == "feature-implementation":
        return [("uses a concrete specification", bool(artifact["specification"])),
                ("inspects callers/data flow", len(artifact["callers_inspected"]) >= 2),
                ("reports changed files and verification", bool(artifact["changed_files"] and artifact["verification"])),
                ("records deferred work", isinstance(artifact["deferred_work"], list))]
    if skill == "testing-qa":
        return [("checks match the trust-boundary risk", "security" in artifact["checks"]),
                ("includes proportionate integration/release checks", {"integration", "release"} <= set(artifact["checks"])),
                ("reports unavailable tooling as UNKNOWN", "UNKNOWN" in artifact["tool_status"]["browser_runner"]),
                ("does not claim QA passed without full evidence", artifact["claimed_pass"] is False)]
    if skill == "review-agent":
        findings = artifact["findings"]
        return [("findings cite file and line", all(row["file"] and isinstance(row["line"], int) for row in findings)),
                ("findings are severity ordered", artifact["ordered_by_severity"]),
                ("review is read-only", artifact["read_only"] and not artifact["mutations"]),
                ("target availability is explicit", isinstance(artifact["target_available"], bool))]
    if skill == "git-workflow":
        return [("inspects status and refs before mutation", artifact["inspection_before_mutation"] and artifact["refs_inspected"]),
                ("reports repository state", bool(artifact["status"])),
                ("destructive targets are verified", artifact["destructive_target_verified"]),
                ("destructive work has explicit approval", artifact["approval"] == "explicit")]
    raise ValueError(f"unsupported skill: {skill}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="run one skill case")
    args = parser.parse_args()
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    cases = [case for case in data["cases"] if not args.case or case["skill"] == args.case]
    if not cases:
        print("FAIL no matching cases")
        return 1
    failed = 0
    for case in cases:
        checks = checks_for(case["skill"], case["artifact"])
        bad = [name for name, passed in checks if not passed]
        failed += bool(bad)
        print(f"{'FAIL' if bad else 'PASS'} {case['skill']}: {len(checks) - len(bad)}/{len(checks)} checks" + (f"; {', '.join(bad)}" if bad else ""))
    print(f"RESULT {'FAIL' if failed else 'PASS'}: {len(cases) - failed}/{len(cases)} skills")
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
