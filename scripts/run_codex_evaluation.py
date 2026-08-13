"""Offline Codex distribution checks and an opt-in isolated CLI probe."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
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
MEASUREMENT_METHOD = "injected-skill-marker-v1"
MARKER_PREFIX = "CODEX_EVAL_MARKER_V1"
SELECTION_MARKER = "CODEX_ROUTING_SELECTED"
SELECTION_MARKER_PATTERN = re.compile(rf"^{re.escape(SELECTION_MARKER)}:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", re.IGNORECASE)


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
        result = subprocess.run([executable, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=10)
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
        "--sandbox",
        "read-only",
        "-C",
        str(ROOT),
    ]


def marker_command(skill: str, nonce: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill) or not re.fullmatch(r"[a-f0-9]{16,}", nonce):
        raise ValueError("skill must be a slug and nonce must be lowercase hexadecimal")
    return f'''python -c "import sys; assert sys.argv[1:] == ['{nonce}', '{skill}']; print('{MARKER_PREFIX}:{skill}:{nonce}')" {nonce} {skill}'''


def stage_skill_text(text: str, skill: str, nonce: str) -> str:
    marker = marker_command(skill, nonce)
    if not text.startswith("---\n"):
        raise ValueError(f"SKILL.md for {skill} has no frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError(f"SKILL.md for {skill} has unterminated frontmatter")
    frontmatter = text[:end + 4]
    body = text[end + 4:]
    instruction = f"\n\nEvaluation instrumentation: before any other action, execute this routing marker command for {skill} and {nonce}:\n\n{marker}\n"
    return frontmatter + instruction + body


def instrumented_prompt(prompt: str) -> str:
    return prompt


def auth_status_command(executable: str) -> list[str]:
    return [resolve_executable(executable), "login", "status"]


def marketplace_add_command(executable: str, marketplace_root: Path) -> list[str]:
    return [resolve_executable(executable), "plugin", "marketplace", "add", str(marketplace_root)]


def plugin_install_command(executable: str, marketplace: str) -> list[str]:
    return [resolve_executable(executable), "plugin", "add", f"codex-skills@{marketplace}"]


def plugin_list_command(executable: str) -> list[str]:
    return [resolve_executable(executable), "plugin", "list", "--json"]


def eval_home_path(codex_home: str | Path | None) -> Path | None:
    raw = codex_home or os.environ.get("CODEX_EVAL_HOME")
    return Path(raw).expanduser() if raw else None


def command_details(result: subprocess.CompletedProcess[str]) -> str:
    details = (result.stderr or result.stdout or "").strip()
    return details[:4000] or f"exit code {result.returncode}"


def run_setup_command(command: list[str], *, env: dict[str, str], timeout: int) -> tuple[subprocess.CompletedProcess[str] | None, str | None]:
    try:
        return subprocess.run(command, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=timeout), None
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def unavailable(*, version: str, run_id: str, captured_at: str, commit: str | None, stage: str, reason: str, status: str = "PLUGIN_UNAVAILABLE") -> dict[str, Any]:
    return {
        "status": status,
        "version": version,
        "runtime_version": version,
        "codex_version": version,
        "run_id": run_id,
        "captured_at_utc": captured_at,
        "git_commit": commit,
        "setup_failure": stage,
        "reason": reason,
        "measurement_method": MEASUREMENT_METHOD,
    }


def stage_local_marketplace(directory: Path, nonce: str | None = None) -> Path:
    marketplace_root = directory / "marketplace"
    plugin_root = marketplace_root / "plugins" / "codex-skills"
    plugin_root.mkdir(parents=True)
    shutil.copytree(ROOT / "skills", plugin_root / "skills")
    nonce = nonce or uuid.uuid4().hex
    for skill_file in (plugin_root / "skills").rglob("SKILL.md"):
        skill_file.write_text(stage_skill_text(skill_file.read_text(encoding="utf-8"), skill_file.parent.name, nonce), encoding="utf-8")
    (plugin_root / ".codex-plugin").mkdir()
    shutil.copy2(ROOT / ".codex-plugin" / "plugin.json", plugin_root / ".codex-plugin" / "plugin.json")
    marketplace_file = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    marketplace_file.parent.mkdir(parents=True)
    marketplace_file.write_text(json.dumps({
        "name": "codex-skills-eval",
        "interface": {"displayName": "Codex Skills Evaluation"},
        "plugins": [{
            "name": "codex-skills",
            "source": {"source": "local", "path": "./plugins/codex-skills"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    }), encoding="utf-8")
    return marketplace_root


def plugin_is_exposed(payload: Any, name: str = "codex-skills") -> bool:
    if isinstance(payload, dict):
        if payload.get("name") == name and payload.get("installed", True) and payload.get("enabled", True):
            return True
        return any(plugin_is_exposed(value, name) for value in payload.values())
    if isinstance(payload, list):
        return any(plugin_is_exposed(value, name) for value in payload)
    return False


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def parse_runtime_events(stdout: str | None, marker_commands: str | dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Keep only direct, structured runtime events used by the graders."""
    events: list[dict[str, Any]] = []
    for line in (stdout or "").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        if event_type in {"skill_selected", "skill_loaded"}:
            events.append({"type": event_type, "name": event.get("name")})
        elif isinstance(event_type, str) and event_type.startswith("item.") and isinstance(event.get("item"), dict):
            item = event["item"]
            if item.get("type") == "command_execution" and marker_commands:
                commands = ({marker_commands: re.search(r"print\('" + re.escape(MARKER_PREFIX) + r":([a-z0-9-]+):", marker_commands).group(1)}
                            if isinstance(marker_commands, str)
                            else {value: name for name, value in marker_commands.items()})
                for command in _strings(item):
                    for expected, name in commands.items():
                        if expected in command:
                            events.append({"type": "skill_selected", "name": name, "source": MEASUREMENT_METHOD})
        elif event_type in {"error", "turn.failed", "turn.completed"}:
            events.append({"type": event_type})
    return events


def calibration_status(runtime_events: list[dict[str, Any]], marker_events: list[dict[str, Any]]) -> str:
    if classify_runtime(runtime_events) in {"FAIL", "UNAVAILABLE"}:
        return "RUNTIME_FAILURE"
    return "ROUTING_AVAILABLE" if any(event.get("name") == "testing-qa" for event in marker_events) else "INSTRUMENTATION_UNAVAILABLE"


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
        "measurement_method": MEASUREMENT_METHOD,
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


def live_probe(executable: str, *, case: str | None = None, group: str | None = None, limit: int | None = None, codex_home: str | Path | None = None) -> dict[str, Any]:
    run_id = uuid.uuid4().hex
    captured_at = datetime.now(timezone.utc).isoformat()
    commit = git_commit()
    version = codex_version(executable)
    if not version:
        return {"status": "RUNTIME_FAILURE", "run_id": run_id, "captured_at_utc": captured_at, "git_commit": commit, "reason": "Codex CLI is not installed or cannot report its version.", "measurement_method": MEASUREMENT_METHOD}
    persistent_home = eval_home_path(codex_home)
    if persistent_home is None:
        return unavailable(version=version, run_id=run_id, captured_at=captured_at, commit=commit, stage="authentication", status="RUNTIME_FAILURE", reason="authentication unavailable: pass --codex-home PATH or set CODEX_EVAL_HOME to a persistent home, then run `codex login` there")
    persistent_home.mkdir(parents=True, exist_ok=True)
    executable = resolve_executable(executable)
    env = os.environ.copy()
    env["CODEX_HOME"] = str(persistent_home)
    auth, auth_error = run_setup_command(auth_status_command(executable), env=env, timeout=30)
    if auth_error or auth is None or auth.returncode:
        if auth_error:
            detail = auth_error
        elif auth is None:
            detail = "authentication command returned no result"
        else:
            detail = command_details(auth)
        return unavailable(version=version, run_id=run_id, captured_at=captured_at, commit=commit, stage="authentication", status="RUNTIME_FAILURE", reason=f"authentication unavailable: {detail}; authenticate this dedicated home with `CODEX_HOME={persistent_home} codex login`")
    with tempfile.TemporaryDirectory(prefix="codex-eval-") as staging:
        nonce = uuid.uuid4().hex
        marketplace_root = stage_local_marketplace(Path(staging), nonce)
        add, add_error = run_setup_command(marketplace_add_command(executable, marketplace_root), env=env, timeout=30)
        if add_error or add is None or add.returncode:
            return unavailable(version=version, run_id=run_id, captured_at=captured_at, commit=commit, stage="marketplace_registration", reason=f"marketplace registration failed: {add_error or command_details(add)}")
        install, install_error = run_setup_command(plugin_install_command(executable, "codex-skills-eval"), env=env, timeout=60)
        if install_error or install is None or install.returncode:
            return unavailable(version=version, run_id=run_id, captured_at=captured_at, commit=commit, stage="plugin_installation", reason=f"plugin installation failed: {install_error or command_details(install)}")
        listing, listing_error = run_setup_command(plugin_list_command(executable), env=env, timeout=30)
        try:
            listed = json.loads(listing.stdout) if listing is not None else None
        except json.JSONDecodeError:
            listed = None
        if listing_error or listing is None or listing.returncode or not plugin_is_exposed(listed):
            return unavailable(version=version, run_id=run_id, captured_at=captured_at, commit=commit, stage="plugin_exposure", reason=f"plugin not exposed to execution: {listing_error or command_details(listing)}")

        marker_commands = {skill_file.parent.name: marker_command(skill_file.parent.name, nonce) for skill_file in (marketplace_root / "plugins/codex-skills/skills").rglob("SKILL.md")}
        calibration_command = marker_commands["testing-qa"]
        try:
            calibration = subprocess.run(routing_command(executable), input="$testing-qa", env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"status": "RUNTIME_FAILURE", "version": version, "runtime_version": version, "codex_version": version, "run_id": run_id, "captured_at_utc": captured_at, "git_commit": commit, "measurement_method": MEASUREMENT_METHOD, "reason": f"calibration execution failed: {type(exc).__name__}: {exc}"}
        calibration_events = parse_runtime_events(calibration.stdout, calibration_command)
        calibration_result = calibration_status(parse_runtime_events(calibration.stdout), calibration_events)
        if calibration_result != "ROUTING_AVAILABLE":
            return {"status": calibration_result, "version": version, "runtime_version": version, "codex_version": version, "run_id": run_id, "captured_at_utc": captured_at, "git_commit": commit, "measurement_method": MEASUREMENT_METHOD, "reason": "explicit $testing-qa calibration did not produce its injected command marker"}

        results: list[dict[str, Any]] = []
        for routing_case in select_routing_cases(read_json(ROUTING_CASES)["cases"], case=case, group=group, limit=limit):
            try:
                run = subprocess.run(
                    routing_command(executable),
                    input=instrumented_prompt(routing_case["prompt"]),
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                    timeout=120,
                )
            except (OSError, subprocess.TimeoutExpired):
                results.append({"case_id": routing_case["case_id"], "implicit_routing_status": "UNAVAILABLE", "runtime_health": "UNAVAILABLE", "reason_codes": ["routing_telemetry_unavailable"], "codex_version": version, "runtime_version": version, "run_id": run_id, "trial_id": f"{run_id}:{routing_case['case_id']}", "captured_at_utc": captured_at, "git_commit": commit, "measurement_method": MEASUREMENT_METHOD})
                continue
            events = parse_runtime_events(run.stdout, marker_commands)
            if run.returncode and not events:
                events = [{"type": "error"}]
            results.append(serialize_routing_result(routing_case, grade_routing(routing_case, events), version, run_id=run_id, trial_id=f"{run_id}:{routing_case['case_id']}", captured_at_utc=captured_at, git_commit=commit))
        verdicts = {item.get("routing_verdict") for item in results}
        status = "RUNTIME_FAILURE" if any(item.get("runtime_health") in {"FAIL", "UNAVAILABLE"} for item in results) else "ROUTING_AVAILABLE" if results and verdicts == {"PASS"} else "ROUTING_FAIL" if "FAIL" in verdicts else "RUNTIME_FAILURE"
        return {"status": status, "version": version, "runtime_version": version, "codex_version": version, "run_id": run_id, "captured_at_utc": captured_at, "git_commit": commit, "measurement_method": MEASUREMENT_METHOD, "filters": {"case": case, "group": group, "limit": limit}, "cases": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--deterministic-only", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--output", type=Path, default=RESULTS / "latest.json")
    parser.add_argument("--codex-home", help="Persistent, dedicated CODEX_HOME authenticated for evaluation (or CODEX_EVAL_HOME).")
    parser.add_argument("--case")
    parser.add_argument("--group")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    if args.live:
        report = {"mode": "live", "result": live_probe(args.codex, case=args.case, group=args.group, limit=args.limit, codex_home=args.codex_home)}
    else:
        report = {"mode": "deterministic", "cases": deterministic_checks()}
    RESULTS.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if args.live:
        return 0 if report["result"]["status"] in {"ROUTING_AVAILABLE", "PLUGIN_UNAVAILABLE", "INSTRUMENTATION_UNAVAILABLE"} else 1
    return 0 if all(case["status"] == "PASS" for case in report["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
