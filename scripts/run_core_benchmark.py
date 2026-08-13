"""Run the reproducible Core-skill benchmark and emit a safe baseline report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "core" / "manifest.json"
STATE = Path("docs/skill-state.json")


def codex_bin() -> str | None:
    return os.environ.get("CODEX_BIN") or shutil.which("codex") or shutil.which("codex.cmd") or shutil.which("codex.exe")


def core_skills(root: Path = ROOT) -> set[str]:
    return {
        skill["name"]
        for skill in json.loads((root / STATE).read_text(encoding="utf-8"))["skills"]
        if skill.get("classification") == "Core"
    }


def validate_manifest(data: dict) -> list[str]:
    errors: list[str] = []
    expected = core_skills()
    records = data.get("skills", [])
    names = {item.get("name") for item in records}
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if names != expected:
        errors.append(f"skill coverage mismatch: expected {len(expected)}, got {len(names)}")
    for item in records:
        cases = item.get("cases", [])
        kinds = [case[0] for case in cases if isinstance(case, list) and len(case) == 2]
        if set(kinds) != {"positive", "negative", "ambiguous"}:
            errors.append(f"{item.get('name')}: requires positive, negative, and ambiguous cases")
        if not item.get("task"):
            errors.append(f"{item.get('name')}: task is required")
        for case in cases:
            if not isinstance(case, list) or len(case) != 2 or not all(isinstance(value, str) and value for value in case):
                errors.append(f"{item.get('name')}: malformed case")
    modes = data.get("modes", {})
    if modes.get("implicit_selection", {}).get("status") != "unavailable":
        errors.append("implicit selection must be explicitly unavailable until telemetry exists")
    return errors


def run_deterministic(data: dict) -> dict:
    errors = validate_manifest(data)
    case_count = sum(len(item.get("cases", [])) for item in data.get("skills", []))
    return {"status": "pass" if not errors else "fail", "skills": len(data.get("skills", [])), "cases": case_count, "errors": errors}


def codex_version() -> str | None:
    binary = codex_bin()
    if not binary:
        return None
    try:
        result = subprocess.run([binary, "--version"], capture_output=True, text=True, check=False, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() or result.stderr.strip() or None


def run_explicit(data: dict, runs: int) -> dict:
    version = codex_version()
    if not version:
        return {"status": "unavailable", "reason": "codex executable not found or version probe failed", "run_count": 0}
    sample = next(item for item in data["skills"] if item["name"] == "acceptance-criteria")
    prompt = sample["cases"][0][1] + " Return a concise answer; do not edit files."
    binary = codex_bin()
    results = []
    for _ in range(runs):
        try:
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as output:
                output_path = Path(output.name)
            result = subprocess.run(
                [binary, "exec", "--ephemeral", "--ignore-user-config", "--json", "-s", "read-only", "-C", str(ROOT), "-o", str(output_path), prompt],
                capture_output=True, text=True, check=False, timeout=180,
            )
            body = output_path.read_text(encoding="utf-8", errors="replace") if output_path.exists() else ""
            results.append({"status": "pass" if result.returncode == 0 else "fail", "exit_code": result.returncode, "response_sha256": hashlib.sha256(body.encode()).hexdigest(), "response_chars": len(body)})
        except (OSError, subprocess.TimeoutExpired) as exc:
            results.append({"error": type(exc).__name__})
        finally:
            if "output_path" in locals():
                output_path.unlink(missing_ok=True)
    return {"status": "measured", "skill": sample["name"], "task_id": "acceptance-criteria-positive", "model_runtime": version, "run_count": runs, "passed": sum(item.get("status") == "pass" for item in results), "failed": sum(item.get("status") == "fail" for item in results), "results": results, "criteria": "exit_code == 0; response reviewed by a human", "uncertainty": "One sample is a baseline, not a trigger-accuracy estimate."}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--deterministic-only", action="store_true")
    parser.add_argument("--output", type=Path, help="write the safe JSON report to this path")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = {"schema_version": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(), "manifest": str(MANIFEST.relative_to(ROOT)).replace(os.sep, "/"), "artifact_policy": "metadata-only: no response bodies, transcripts, secrets, or rollout data", "deterministic": run_deterministic(data), "measurement_modes": {"explicit_invocation": None, "implicit_selection": data["modes"]["implicit_selection"]}}
    if not args.deterministic_only and report["deterministic"]["status"] == "pass":
        report["measurement_modes"]["explicit_invocation"] = run_explicit(data, args.runs)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["deterministic"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
