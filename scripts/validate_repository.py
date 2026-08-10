"""Run the repository's deterministic, offline validation checks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> bool:
    print(f"== {label} ==")
    result = subprocess.run(command, cwd=ROOT, text=True)
    return result.returncode == 0


def check_python_syntax() -> bool:
    print("== Python syntax ==")
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (OSError, SyntaxError) as exc:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
    if errors:
        print("\n".join(errors))
        return False
    print("PYTHON_SYNTAX_OK")
    return True


def check_tracked_cache_artifacts() -> bool:
    print("== Tracked Python cache artifacts ==")
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=False
    )
    if result.returncode:
        print(result.stderr.decode(errors="replace").strip())
        return False
    bad = [
        name.decode()
        for name in result.stdout.split(b"\0")
        if name and ("__pycache__" in name.decode() or name.decode().endswith((".pyc", ".pyo")))
    ]
    if bad:
        print("\n".join(f"tracked cache artifact: {name}" for name in bad))
        return False
    print("PYTHON_CACHE_ARTIFACTS_OK")
    return True


def check_committed_whitespace() -> bool:
    print("== Committed whitespace ==")
    result = subprocess.run(
        ["git", "grep", "-nI", "-E", r"[[:blank:]]+$", "HEAD", "--"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        print(result.stdout.strip())
        return False
    if result.returncode != 1:
        print(result.stderr.strip())
        return False
    print("COMMITTED_WHITESPACE_OK")
    return True


def main() -> int:
    checks = [
        ("catalog", [sys.executable, "scripts/validate_catalog.py"]),
        ("trigger and alias declarations", [sys.executable, "scripts/check_trigger_overlap.py"]),
        ("context budget and Markdown links", [sys.executable, "scripts/check_skill_budget.py"]),
    ]
    passed = True
    for label, command in checks:
        passed = run(label, command) and passed
    passed = check_tracked_cache_artifacts() and passed
    passed = check_python_syntax() and passed
    passed = check_committed_whitespace() and passed
    passed = run("Working-tree whitespace", ["git", "diff", "--check"]) and passed
    print("OPTIONAL_SKILL_TESTS=not-run (repository validation is offline and dependency-free)")
    if not passed:
        print("REPOSITORY_VALIDATION_FAILED")
        return 1
    print("REPOSITORY_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
