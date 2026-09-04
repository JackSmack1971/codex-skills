"""Validate and optionally run safe behavioral evaluations for Core skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "benchmarks" / "core" / "behavioral-cases.json"
SCHEMA = ROOT / "benchmarks" / "core" / "behavioral-schema.json"
STATE = Path("docs/skill-state.json")
ALLOWED_TYPES = {"required_heading", "required_text", "forbidden_text", "required_file", "required_stop_behavior", "validator_exit_code"}
OVERLAP_GROUPS = {
    "review-agent-vs-pr-review": {"review-agent", "pr-review"},
    "feature-implementation-vs-vertical-slice": {"feature-implementation", "vertical-slice"},
    "feature-implementation-vs-test-driven-development": {"feature-implementation", "test-driven-development"},
    "testing-qa-vs-test-driven-development": {"testing-qa", "test-driven-development"},
    "skill-auditor-vs-context-doctor-vs-improve": {"skill-auditor", "context-doctor", "improve"},
    "git-workflow-vs-git-commit-vs-using-git-worktrees": {"git-workflow", "git-commit", "using-git-worktrees"},
    "skill-creator-vs-context7-skill-wizard-vs-plugin-creator": {"skill-creator", "context7-skill-wizard", "plugin-creator"},
}


def core_skill_names(root: Path = ROOT) -> set[str]:
    return {
        skill["name"]
        for skill in json.loads((root / STATE).read_text(encoding="utf-8"))["skills"]
        if skill.get("classification") == "Core"
    }


def load_cases(path: Path = CASES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_suite(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(data.get("artifact_policy"), str) or "metadata-only" not in data["artifact_policy"]:
        errors.append("artifact_policy must declare metadata-only output")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]
    ids: set[str] = set()
    by_skill: dict[str, list[dict]] = {}
    by_overlap: dict[str, set[str]] = {name: set() for name in OVERLAP_GROUPS}
    for case in cases:
        if not isinstance(case, dict):
            errors.append("case must be an object")
            continue
        required = {"case_id", "skill_name", "prompt", "expected_required_behaviors", "forbidden_behaviors", "polarity"}
        missing = required - set(case)
        if missing:
            errors.append(f"case missing: {', '.join(sorted(missing))}")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append("case_id must be a non-empty string")
        elif case_id in ids:
            errors.append(f"duplicate case_id: {case_id}")
        else:
            ids.add(case_id)
        for field in ("skill_name", "prompt"):
            if not isinstance(case.get(field), str) or not case[field]:
                errors.append(f"{case_id or '<case>'}: {field} must be a non-empty string")
        if case.get("polarity") not in {"positive", "negative", "ambiguous"}:
            errors.append(f"{case_id or '<case>'}: invalid polarity")
        for field in ("expected_required_behaviors", "forbidden_behaviors"):
            behaviors = case.get(field)
            if not isinstance(behaviors, list):
                errors.append(f"{case_id or '<case>'}: {field} must be a list")
                continue
            for behavior in behaviors:
                if not isinstance(behavior, dict) or set(behavior) - {"type", "value", "command"}:
                    errors.append(f"{case_id or '<case>'}: malformed behavior")
                    continue
                if behavior.get("type") not in ALLOWED_TYPES:
                    errors.append(f"{case_id or '<case>'}: unsupported behavior type")
                if not isinstance(behavior.get("value"), (str, int)) or behavior.get("value") == "":
                    errors.append(f"{case_id or '<case>'}: behavior value is required")
        skill = case.get("skill_name")
        if isinstance(skill, str):
            by_skill.setdefault(skill, []).append(case)
        overlap = case.get("overlap_group")
        if overlap not in {None, *OVERLAP_GROUPS}:
            errors.append(f"{case_id or '<case>'}: unknown overlap_group")
        if overlap in OVERLAP_GROUPS and isinstance(skill, str):
            by_overlap[overlap].add(skill)
    core = core_skill_names()
    if not core.issubset(by_skill):
        errors.append(f"behavioral corpus skill coverage mismatch: missing {sorted(core - set(by_skill))}")
    for skill in sorted(core):
        cases_for_skill = by_skill.get(skill, [])
        if len(cases_for_skill) < 6:
            errors.append(f"{skill}: requires at least 6 behavioral cases")
        polarities = {case.get("polarity") for case in cases_for_skill}
        for polarity in ("positive", "negative", "ambiguous"):
            if sum(case.get("polarity") == polarity for case in cases_for_skill) < 2:
                errors.append(f"{skill}: requires at least 2 {polarity} cases")
        for case in cases_for_skill:
            required = case.get("expected_required_behaviors", [])
            forbidden = case.get("forbidden_behaviors", [])
            if not required:
                errors.append(f"{case.get('case_id', skill)}: requires a checkable required behavior")
            if case.get("polarity") == "negative" and not forbidden:
                errors.append(f"{case.get('case_id', skill)}: negative case requires forbidden behavior")
    for overlap, skills in by_overlap.items():
        if skills != OVERLAP_GROUPS[overlap]:
            errors.append(f"{overlap}: missing discriminating cases for {sorted(OVERLAP_GROUPS[overlap] - skills)}")
    return errors


def evaluate_assertions(case: dict, output: str, exit_code: int, root: Path = ROOT) -> dict:
    checks = []
    for behavior in case["expected_required_behaviors"]:
        kind, value = behavior["type"], behavior["value"]
        if kind == "required_heading":
            passed = bool(re.search(rf"^#+\s+{re.escape(str(value))}\s*$", output, re.I | re.M))
        elif kind == "required_text":
            passed = str(value).lower() in output.lower()
        elif kind == "required_file":
            passed = (root / str(value)).is_file()
        elif kind == "required_stop_behavior":
            passed = str(value).lower() in output.lower()
        elif kind == "validator_exit_code":
            if behavior.get("command"):
                result = subprocess.run(behavior["command"], cwd=root, capture_output=True, check=False, timeout=60, encoding="utf-8", errors="replace")
                passed = result.returncode == int(value)
            else:
                passed = exit_code == int(value)
        else:
            passed = True
        checks.append({"category": "required", "type": kind, "passed": passed})
    for behavior in case["forbidden_behaviors"]:
        kind, value = behavior["type"], behavior["value"]
        if kind in {"forbidden_text", "required_stop_behavior"}:
            passed = str(value).lower() not in output.lower()
        elif kind == "required_file":
            passed = not (root / str(value)).is_file()
        elif kind == "validator_exit_code":
            if behavior.get("command"):
                result = subprocess.run(behavior["command"], cwd=root, capture_output=True, check=False, timeout=60, encoding="utf-8", errors="replace")
                passed = result.returncode != int(value)
            else:
                passed = exit_code != int(value)
        else:
            passed = True
        checks.append({"category": "forbidden", "type": kind, "passed": passed})
    return {"status": "pass" if all(item["passed"] for item in checks) else "fail", "checks": checks}


def codex_bin() -> str | None:
    return os.environ.get("CODEX_BIN") or shutil.which("codex") or shutil.which("codex.cmd") or shutil.which("codex.exe")


def skill_condition_prompt(case: dict) -> tuple[str, str]:
    skill_file = ROOT / "skills" / case["skill_name"] / "SKILL.md"
    instructions = skill_file.read_text(encoding="utf-8")
    digest = hashlib.sha256(instructions.encode()).hexdigest()
    prompt = (
        "Apply the following local Codex skill package instructions to the task. "
        f"Resolve bundled resources relative to {skill_file.parent}.\n\n"
        "<skill-instructions>\n"
        f"{instructions}\n"
        "</skill-instructions>\n\n"
        f"<task>\n{case['prompt']}\n</task>"
    )
    return prompt, digest


def run_case(case: dict, mode: str, timeout: int = 180) -> dict:
    binary = codex_bin()
    if not binary:
        return {"status": "unavailable", "mode": mode, "reason": "codex executable not found"}
    instruction_sha256 = None
    if mode == "baseline":
        prompt = case["prompt"]
    else:
        prompt, instruction_sha256 = skill_condition_prompt(case)
    output_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as output:
            output_path = Path(output.name)
        started = time.monotonic()
        result = subprocess.run([binary, "exec", "--ephemeral", "--ignore-user-config", "--json", "-s", "read-only", "-C", str(ROOT), "-o", str(output_path), prompt], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=timeout)
        duration_ms = round((time.monotonic() - started) * 1000)
        body = output_path.read_text(encoding="utf-8", errors="replace") if output_path.exists() else ""
        assertions = evaluate_assertions(case, body, result.returncode)
        command_events = 0
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and isinstance(event.get("type"), str) and event["type"].startswith("item.") and isinstance(event.get("item"), dict) and event["item"].get("type") == "command_execution":
                command_events += 1
        return {"status": "pass" if result.returncode == 0 and assertions["status"] == "pass" else "fail", "mode": mode, "exit_code": result.returncode, "skill_instruction_sha256": instruction_sha256, "response_sha256": hashlib.sha256(body.encode()).hexdigest(), "response_chars": len(body), "duration_ms": duration_ms, "command_events": command_events, "assertions": assertions}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "mode": mode, "reason": type(exc).__name__}
    finally:
        if output_path:
            output_path.unlink(missing_ok=True)


def summarize_paired(runtime: list[dict], minimum_pairs: int = 10) -> dict:
    pairs = [entry for entry in runtime if entry.get("explicit_invocation") and entry.get("baseline")]
    available = [entry for entry in pairs if entry["explicit_invocation"].get("status") in {"pass", "fail"} and entry["baseline"].get("status") in {"pass", "fail"}]
    total = len(available)

    def count(mode: str, status: str) -> int:
        return sum(entry[mode].get("status") == status for entry in available)

    explicit_pass = count("explicit_invocation", "pass")
    baseline_pass = count("baseline", "pass")
    explicit_rate = explicit_pass / total if total else None
    baseline_rate = baseline_pass / total if total else None
    uplift_pp = (explicit_rate - baseline_rate) * 100 if total else None
    base_errors = total - baseline_pass
    skill_errors = total - explicit_pass
    relative_error_reduction = (base_errors - skill_errors) / base_errors if base_errors else None

    def violations(mode: str) -> int:
        return sum(
            not check.get("passed", False)
            for entry in available
            for check in entry[mode].get("assertions", {}).get("checks", [])
            if check.get("category") == "forbidden"
        )

    base_violations = violations("baseline")
    skill_violations = violations("explicit_invocation")
    violation_reduction = (base_violations - skill_violations) / base_violations if base_violations else None

    def average(mode: str, field: str) -> float | None:
        values = [entry[mode][field] for entry in available if isinstance(entry[mode].get(field), (int, float))]
        return sum(values) / len(values) if values else None

    baseline_chars = average("baseline", "response_chars")
    explicit_chars = average("explicit_invocation", "response_chars")
    efficiency_gain = (baseline_chars - explicit_chars) / baseline_chars if baseline_chars else None
    baseline_duration = average("baseline", "duration_ms")
    explicit_duration = average("explicit_invocation", "duration_ms")
    baseline_commands = average("baseline", "command_events")
    explicit_commands = average("explicit_invocation", "command_events")
    material = bool(
        (uplift_pp is not None and uplift_pp >= 10)
        or (relative_error_reduction is not None and relative_error_reduction >= 0.25)
        or (violation_reduction is not None and violation_reduction >= 0.50)
        or (efficiency_gain is not None and efficiency_gain >= 0.20 and uplift_pp is not None and uplift_pp >= -2)
    )
    adequate = total >= minimum_pairs and len({entry["case_id"] for entry in available}) >= 3 and len(pairs) == total
    decision = "RETAIN" if adequate and material and skill_violations == 0 else "COMPRESS_OR_DELETE" if adequate else "INCONCLUSIVE"
    return {
        "decision": decision,
        "adequate_evidence": adequate,
        "minimum_paired_trials": minimum_pairs,
        "paired_trials": total,
        "distinct_cases": len({entry["case_id"] for entry in available}),
        "explicit_success_rate": explicit_rate,
        "baseline_success_rate": baseline_rate,
        "task_success_uplift_pp": uplift_pp,
        "relative_error_reduction": relative_error_reduction,
        "forbidden_behavior_violations": {"explicit": skill_violations, "baseline": base_violations, "relative_reduction": violation_reduction},
        "efficiency": {
            "primary_metric": "response_chars",
            "mean_response_chars_explicit": explicit_chars,
            "mean_response_chars_baseline": baseline_chars,
            "relative_gain": efficiency_gain,
            "mean_duration_ms_explicit": explicit_duration,
            "mean_duration_ms_baseline": baseline_duration,
            "mean_command_events_explicit": explicit_commands,
            "mean_command_events_baseline": baseline_commands,
        },
        "thresholds": {"task_success_uplift_pp": 10, "relative_error_reduction": 0.25, "forbidden_behavior_reduction": 0.50, "efficiency_gain": 0.20, "max_success_regression_pp_for_efficiency": 2, "critical_violations": 0},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id")
    parser.add_argument("--skill")
    parser.add_argument("--baseline", action="store_true", help="run without deliberately invoking the target skill")
    parser.add_argument("--paired", action="store_true", help="run matched no-skill and explicit-skill trials")
    parser.add_argument("--runs", type=int, default=1, help="repeat each selected case; paired decisions require at least 10 total pairs")
    parser.add_argument("--deterministic-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.runs < 1:
        parser.error("--runs must be positive")
    if args.baseline and args.paired:
        parser.error("--baseline and --paired are mutually exclusive")
    data = load_cases()
    errors = validate_suite(data)
    selected = [case for case in data.get("cases", []) if (not args.case_id or case.get("case_id") == args.case_id) and (not args.skill or case.get("skill_name") == args.skill)]
    if (args.case_id or args.skill) and not selected:
        errors.append("selection matched no cases")
    report = {"schema_version": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(), "artifact_policy": data["artifact_policy"], "deterministic": {"status": "pass" if not errors else "fail", "core_skill_count": len(core_skill_names()), "case_count": len(data.get("cases", [])), "errors": errors}, "runtime": []}
    if not errors and not args.deterministic_only:
        for case in selected or data["cases"]:
            for trial in range(1, args.runs + 1):
                if args.paired and trial % 2 == 0:
                    baseline = run_case(case, "baseline")
                    explicit = run_case(case, "explicit")
                else:
                    explicit = None if args.baseline else run_case(case, "explicit")
                    baseline = run_case(case, "baseline") if args.baseline or args.paired else None
                report["runtime"].append({"case_id": case["case_id"], "skill_name": case["skill_name"], "polarity": case["polarity"], "trial": trial, "explicit_invocation": explicit, "baseline": baseline})
    if args.paired:
        report["paired_evidence"] = {
            skill: summarize_paired([entry for entry in report["runtime"] if entry["skill_name"] == skill])
            for skill in sorted({entry["skill_name"] for entry in report["runtime"]})
        }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    runtime_failed = any(
        (entry.get("explicit_invocation") or {}).get("status") == "fail"
        or (entry.get("baseline") or {}).get("status") == "fail"
        for entry in report["runtime"]
    )
    return 0 if not errors and not runtime_failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
