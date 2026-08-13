"""Offline Codex distribution checks and an opt-in isolated CLI probe."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
try:
    from evals.codex.graders.runtime import classify_runtime, selected_skill
    from evals.codex.graders.routing import grade_routing
except ModuleNotFoundError:
    sys.path.insert(0, str(ROOT))
    from evals.codex.graders.runtime import classify_runtime, selected_skill
    from evals.codex.graders.routing import grade_routing
TASKS = ROOT / "evals/codex/tasks/runtime-cases.json"
INVARIANTS = ROOT / "evals/codex/expected_invariants/runtime.json"
ROUTING_CASES = ROOT / "benchmarks/routing/cases.json"
RESULTS = ROOT / "evals/codex/results"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def deterministic_checks() -> list[dict[str, str]]:
    expected = read_json(INVARIANTS)
    manifest = read_json(ROOT / ".codex-plugin/plugin.json")
    marketplace = read_json(ROOT / ".agents/plugins/marketplace.json")
    catalog = read_json(ROOT / "skills/catalog.json")
    skills = catalog["skills"]
    names = {record["name"] for record in skills}
    metadata = "".join(f"{record['name']} {record['description']}\n" for record in skills)
    fixture_cases = read_json(ROOT / "tests/skill-routing-cases.json")["cases"]
    benchmark_cases = [case for skill in read_json(ROOT / "benchmarks/core/manifest.json")["skills"] for case in skill["cases"]]
    checks: list[tuple[str, bool, str]] = [
        ("plugin-discoverability", marketplace["plugins"][0]["name"] == manifest["name"], "marketplace entry matches manifest"),
        ("bundled-skill-availability", len(skills) == expected["canonical_skill_count"] and len(names) == len(skills), f"{len(skills)} unique catalog skills"),
        ("front-doors", all(catalog["front_doors"].get(key, {}).get("owner") in names for key in expected["required_front_doors"]), "front-door owners exist"),
        ("named-specialists", all(name in names for name in expected["representative_specialists"]), "representative specialists exist"),
        ("routing-fixtures", bool(fixture_cases) and {case[0] for case in benchmark_cases} >= {"positive", "negative", "ambiguous"}, f"{len(fixture_cases)} routing fixtures plus core prompt cases"),
        ("initial-skill-list-budget", len(metadata) <= expected["initial_skill_list_budget_chars"], f"{len(metadata)} <= {expected['initial_skill_list_budget_chars']} chars"),
    ]
    return [{"id": case_id, "status": "PASS" if ok else "FAIL", "evidence": evidence} for case_id, ok, evidence in checks]


def codex_version(executable: str) -> str | None:
    executable = resolve_executable(executable)
    try:
        result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def resolve_executable(executable: str) -> str:
    if os.name == "nt" and executable == "codex":
        return shutil.which("codex.cmd") or executable
    return executable


def routing_command(executable: str) -> list[str]:
    return [
        resolve_executable(executable),
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "read-only",
        "--ask-for-approval",
        "never",
        "-C",
        str(ROOT),
        "-",
    ]


def parse_runtime_events(stdout: str) -> list[dict[str, Any]]:
    """Keep only direct, structured runtime events used by the graders."""
    events: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        if event_type in {"skill_selected", "skill_loaded"}:
            events.append({"type": event_type, "name": event.get("name")})
        elif event_type in {"error", "turn.failed", "turn.completed"}:
            events.append({"type": event_type})
    return events


def serialize_routing_result(case: dict[str, Any], grading: dict[str, Any], version: str, *, run_id: str | None = None, trial_id: str | None = None, captured_at_utc: str | None = None, git_commit: str | None = None) -> dict[str, Any]:
    prompt = case["prompt"].encode("utf-8")
    return {
        "case_id": case["case_id"],
        "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
        "prompt_length": len(prompt),
        "expected_primary_skill": grading["expected_primary_skill"],
        "actual_selected_skills": grading["actual_selected_skills"],
        "selection_telemetry": grading.get("selection_telemetry", bool(grading["actual_selected_skills"])),
        "acceptable_alternative_skills": case.get("acceptable_alternative_skills", []),
        "forbidden_skills": case.get("forbidden_skills", []),
        "case_kind": case.get("case_kind"),
        "group_id": case.get("group_id"),
        "expected_skill_sequence": case.get("expected_skill_sequence"),
        "primary_selection_verdict": grading["primary_selection_verdict"],
        "forbidden_activation_verdict": grading["forbidden_activation_verdict"],
        "acceptable_alternative_handling": grading["acceptable_alternative_handling"],
        "expected_composition_sequence_verdict": grading["expected_composition_sequence_verdict"],
        "routing_verdict": grading["routing_verdict"],
        "implicit_routing_status": "AVAILABLE" if grading.get("selection_telemetry", bool(grading["actual_selected_skills"])) else "UNAVAILABLE",
        "runtime_health": grading["runtime_health"],
        "reason_codes": grading["reason_codes"],
        "codex_version": version,
        "runtime_version": version,
        "run_id": run_id,
        "trial_id": trial_id,
        "captured_at_utc": captured_at_utc,
        "git_commit": git_commit,
    }


def select_routing_cases(cases: list[dict[str, Any]], *, case: str | None = None, group: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    selected = [item for item in cases if (case is None or item.get("case_id") == case) and (group is None or item.get("group_id") == group)]
    return selected[:limit] if limit is not None else selected


def git_commit() -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def live_probe(executable: str, *, case: str | None = None, group: str | None = None, limit: int | None = None) -> dict[str, Any]:
    run_id = uuid.uuid4().hex
    captured_at = datetime.now(timezone.utc).isoformat()
    commit = git_commit()
    version = codex_version(executable)
    if not version:
        return {"status": "UNAVAILABLE", "run_id": run_id, "captured_at_utc": captured_at, "git_commit": commit, "reason": "Codex CLI is not installed or cannot report its version."}
    with tempfile.TemporaryDirectory(prefix="codex-eval-") as isolated_home:
        executable = resolve_executable(executable)
        env = os.environ.copy()
        env["CODEX_HOME"] = isolated_home
        command = [executable, "plugin", "marketplace", "add", str(ROOT / ".agents/plugins")]
        add = subprocess.run(command, env=env, capture_output=True, text=True, check=False, timeout=30)
        if add.returncode:
            return {"status": "UNAVAILABLE", "version": version, "runtime_version": version, "codex_version": version, "run_id": run_id, "captured_at_utc": captured_at, "git_commit": commit, "reason": "isolated local marketplace registration failed"}

        results: list[dict[str, Any]] = []
        for case in select_routing_cases(read_json(ROUTING_CASES)["cases"], case=case, group=group, limit=limit):
            try:
                run = subprocess.run(
                    routing_command(executable),
                    input=case["prompt"],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=120,
                )
            except (OSError, subprocess.TimeoutExpired):
                results.append({"case_id": case["case_id"], "implicit_routing_status": "UNAVAILABLE", "codex_version": version, "runtime_version": version, "run_id": run_id, "trial_id": f"{run_id}:{case['case_id']}", "captured_at_utc": captured_at, "git_commit": commit})
                continue
            events = parse_runtime_events(run.stdout)
            if run.returncode and not events:
                events = [{"type": "error"}]
            results.append(serialize_routing_result(case, grade_routing(case, events), version, run_id=run_id, trial_id=f"{run_id}:{case['case_id']}", captured_at_utc=captured_at, git_commit=commit))
        verdicts = {item.get("routing_verdict") for item in results}
        status = "PASS" if results and verdicts == {"PASS"} else "FAIL" if "FAIL" in verdicts else "UNAVAILABLE"
        return {"status": status, "version": version, "runtime_version": version, "codex_version": version, "run_id": run_id, "captured_at_utc": captured_at, "git_commit": commit, "filters": {"case": case, "group": group, "limit": limit}, "cases": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--deterministic-only", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--output", type=Path, default=RESULTS / "latest.json")
    parser.add_argument("--case")
    parser.add_argument("--group")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    if args.live:
        report = {"mode": "live", "result": live_probe(args.codex, case=args.case, group=args.group, limit=args.limit)}
    else:
        report = {"mode": "deterministic", "cases": deterministic_checks()}
    RESULTS.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if args.live:
        return 0 if report["result"]["status"] in {"PASS", "UNAVAILABLE"} else 1
    return 0 if all(case["status"] == "PASS" for case in report["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
