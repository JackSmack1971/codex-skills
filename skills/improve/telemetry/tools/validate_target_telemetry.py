from __future__ import annotations

import argparse
import json
import os
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from common import SCHEMA_INSPECTION, SCHEMA_MANIFEST, load_jsonl, read_json

REQUIRED = [
    "manifest.json",
    "config.json",
    "inspection.json",
    "recorder.py",
    "hook_capture.py",
    "SCHEMA.md",
    "README.md",
    "INTEGRATION.md",
    "hooks.repo.json",
    "hooks.plugin.json",
    "tools/common.py",
    "tools/analyze_telemetry.py",
    "tools/derive_eval_cases.py",
    "tools/import_codex_trace.py",
    "tools/compare_telemetry.py",
    "tools/validate_target_telemetry.py",
    "schemas/event.schema.json",
    "schemas/manifest.schema.json",
    "schemas/inspection.schema.json",
    "schemas/finding.schema.json",
    "schemas/eval-candidate.schema.json",
]


def issue(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def smoke(root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="skilltelemetry-smoke-") as td:
        env = os.environ.copy()
        env["SKILL_TELEMETRY_DATA_DIR"] = td
        start = subprocess.run(
            [sys.executable, str(root / "recorder.py"), "start", "--task-category", "smoke", "--invocation", "explicit"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
        )
        if start.returncode != 0 or not start.stdout.strip():
            return [issue("error", "SMOKE_START", f"recorder start failed: {start.stderr.strip()}")]
        run_id = start.stdout.strip().splitlines()[-1]
        secret = "sk-THIS_SHOULD_NOT_SURVIVE_123456789"
        ev = subprocess.run(
            [
                sys.executable,
                str(root / "recorder.py"),
                "event",
                "--run-id", run_id,
                "--event", "verification",
                "--outcome", "success",
                "--command", f"example --api-key {secret}",
                "--evidence-json", json.dumps({"api_key": secret, "note": "ok"}),
            ],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
        )
        fin = subprocess.run(
            [sys.executable, str(root / "recorder.py"), "finish", "--run-id", run_id, "--outcome", "success"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
        )
        if ev.returncode != 0 or fin.returncode != 0:
            issues.append(issue("error", "SMOKE_EVENT", f"recorder event/finish failed: {ev.stderr.strip()} {fin.stderr.strip()}"))
            return issues
        files = list(Path(td).rglob(f"{run_id}.jsonl"))
        if len(files) != 1:
            issues.append(issue("error", "SMOKE_FILE", f"expected one run JSONL, found {len(files)}"))
            return issues
        raw_text = files[0].read_text(encoding="utf-8")
        if secret in raw_text:
            issues.append(issue("error", "SECRET_LEAK", "smoke secret survived telemetry redaction"))
        events = load_jsonl(files[0])
        if [e.get("event") for e in events] != ["run.started", "verification", "run.finished"]:
            issues.append(issue("error", "EVENT_SEQUENCE", "unexpected smoke event sequence"))
    return issues


def validate(root: Path, *, run_smoke: bool = True) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    for rel in REQUIRED:
        if not (root / rel).is_file():
            issues.append(issue("error", "MISSING_FILE", rel))

    for folder in ["raw", "ambient", "state", "derived", "evals/regressions"]:
        if not (root / folder).is_dir():
            issues.append(issue("error", "MISSING_DIR", folder))

    if issues:
        return {"status": "FAIL", "issues": issues}

    try:
        manifest = read_json(root / "manifest.json")
        config = read_json(root / "config.json")
        inspection = read_json(root / "inspection.json")
    except Exception as exc:
        return {"status": "FAIL", "issues": [issue("error", "JSON_PARSE", str(exc))]}

    if manifest.get("schema") != SCHEMA_MANIFEST:
        issues.append(issue("error", "MANIFEST_SCHEMA", "unsupported manifest schema"))
    if inspection.get("schema") != SCHEMA_INSPECTION:
        issues.append(issue("error", "INSPECTION_SCHEMA", "unsupported inspection schema"))
    if manifest.get("target", {}).get("fingerprint") != inspection.get("fingerprint"):
        issues.append(issue("error", "FINGERPRINT_MISMATCH", "manifest and inspection target fingerprints differ"))

    capture = manifest.get("capture", {})
    if capture.get("raw_prompt_text") is not False or capture.get("raw_command_text") is not False or capture.get("tool_response_body") is not False:
        issues.append(issue("error", "UNSAFE_CAPTURE_DEFAULT", "raw content capture must be disabled by default"))
    promotion = manifest.get("promotion", {})
    if promotion.get("auto_rewrite_target") is not False or promotion.get("auto_promote_evals") is not False:
        issues.append(issue("error", "UNSAFE_PROMOTION", "automatic target rewrite/eval promotion must be disabled"))
    if config.get("content_policy") != "metadata":
        issues.append(issue("warning", "CONTENT_POLICY", "default content policy is not metadata"))

    for folder in ["raw", "ambient", "state"]:
        gi = root / folder / ".gitignore"
        if not gi.is_file() or "*" not in gi.read_text(encoding="utf-8"):
            issues.append(issue("error", "RAW_NOT_IGNORED", f"{folder}/ is not protected by generated .gitignore"))

    python_files = [root / "recorder.py", root / "hook_capture.py"] + sorted((root / "tools").glob("*.py"))
    for py in python_files:
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            issues.append(issue("error", "PY_COMPILE", f"{py.relative_to(root)}: {exc}"))

    for schema_file in sorted((root / "schemas").glob("*.json")):
        try:
            json.loads(schema_file.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(issue("error", "SCHEMA_JSON", f"{schema_file.name}: {exc}"))

    for hook_file in [root / "hooks.repo.json", root / "hooks.plugin.json"]:
        try:
            hooks = read_json(hook_file)
            text = json.dumps(hooks)
            if "SkillInvocationStarted" in text or "SkillInvocationFinished" in text:
                issues.append(issue("error", "INVENTED_HOOK", f"{hook_file.name} claims unsupported first-class skill invocation hooks"))
            if "<REPO_RELATIVE" in text or "<PLUGIN_RELATIVE" in text:
                issues.append(issue("warning", "HOOK_PLACEHOLDER", f"{hook_file.name} needs final path integration before use"))
        except Exception as exc:
            issues.append(issue("error", "HOOK_JSON", f"{hook_file.name}: {exc}"))

    if run_smoke and not any(x["level"] == "error" for x in issues):
        issues.extend(smoke(root))

    errors = sum(1 for x in issues if x["level"] == "error")
    warnings = sum(1 for x in issues if x["level"] == "warning")
    status = "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {"status": status, "errors": errors, "warnings": warnings, "issues": issues}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a generated target-skill telemetry sidecar.")
    parser.add_argument("sidecar", type=Path)
    parser.add_argument("--no-smoke", action="store_true")
    args = parser.parse_args()
    result = validate(args.sidecar.resolve(), run_smoke=not args.no_smoke)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
