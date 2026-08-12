"""Offline Codex distribution checks and an opt-in isolated CLI probe."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
try:
    from evals.codex.graders.runtime import classify_runtime, selected_skill
except ModuleNotFoundError:
    sys.path.insert(0, str(ROOT))
    from evals.codex.graders.runtime import classify_runtime, selected_skill
TASKS = ROOT / "evals/codex/tasks/runtime-cases.json"
INVARIANTS = ROOT / "evals/codex/expected_invariants/runtime.json"
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
    if os.name == "nt" and executable == "codex":
        executable = shutil.which("codex.cmd") or executable
    try:
        result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def live_probe(executable: str) -> dict[str, Any]:
    version = codex_version(executable)
    if not version:
        return {"status": "UNAVAILABLE", "reason": "Codex CLI is not installed or cannot report its version."}
    with tempfile.TemporaryDirectory(prefix="codex-eval-") as isolated_home:
        if os.name == "nt" and executable == "codex":
            executable = shutil.which("codex.cmd") or executable
        env = os.environ.copy()
        env["CODEX_HOME"] = isolated_home
        command = [executable, "plugin", "marketplace", "add", str(ROOT / ".agents/plugins")]
        add = subprocess.run(command, env=env, capture_output=True, text=True, check=False, timeout=30)
        if add.returncode:
            return {"status": "UNAVAILABLE", "version": version, "reason": "isolated local marketplace registration failed", "stderr": add.stderr[-500:]}
        listed = subprocess.run([executable, "plugin", "list", "--available", "--json"], env=env, capture_output=True, text=True, check=False, timeout=30)
        if listed.returncode:
            return {"status": "FAIL", "version": version, "reason": "isolated plugin listing failed", "stderr": listed.stderr[-500:]}
        try:
            payload = json.loads(listed.stdout)
        except json.JSONDecodeError:
            return {"status": "FAIL", "version": version, "reason": "plugin list did not produce JSON"}
        text = json.dumps(payload)
        status = "PASS" if "codex-skills" in text else "FAIL"
        return {"status": status, "version": version, "marketplace_listing": payload, "selection_evidence": "UNKNOWN"}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--deterministic-only", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args()
    if args.live:
        report = {"mode": "live", "result": live_probe(args.codex)}
    else:
        report = {"mode": "deterministic", "cases": deterministic_checks()}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if args.live:
        return 0 if report["result"]["status"] in {"PASS", "UNAVAILABLE"} else 1
    return 0 if all(case["status"] == "PASS" for case in report["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
