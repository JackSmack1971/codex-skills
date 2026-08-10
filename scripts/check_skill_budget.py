"""Check skill entrypoint budgets and local Markdown references."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "skills" / "context-budget.json"
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def fail(errors: list[str]) -> int:
    print("\n".join(errors))
    return 1


def main() -> int:
    errors: list[str] = []
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail([f"budget config unreadable: {exc}"])

    warning = config.get("warning_bytes")
    hard = config.get("hard_bytes")
    exceptions = config.get("exceptions")
    if not isinstance(warning, int) or not isinstance(hard, int) or warning <= 0 or warning >= hard:
        errors.append("warning_bytes and hard_bytes must be positive integers with warning_bytes < hard_bytes")
    if not isinstance(exceptions, list):
        errors.append("exceptions must be a list")
        exceptions = []

    exception_map: dict[str, dict[str, object]] = {}
    for item in exceptions:
        if not isinstance(item, dict):
            errors.append("exception records must be objects")
            continue
        skill = item.get("skill")
        maximum = item.get("max_bytes")
        reason = item.get("reason")
        documented_in = item.get("documented_in")
        if not isinstance(skill, str) or not skill or skill in exception_map:
            errors.append(f"invalid or duplicate exception skill: {skill!r}")
            continue
        if not isinstance(maximum, int) or maximum < hard:
            errors.append(f"{skill}: max_bytes must be an integer >= hard_bytes")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{skill}: exception reason is required")
        if not isinstance(documented_in, str) or not documented_in.endswith(".md"):
            errors.append(f"{skill}: documented_in must name a Markdown file")
        elif not (ROOT / documented_in).is_file():
            errors.append(f"{skill}: missing exception documentation {documented_in}")
        exception_map[skill] = item

    actual_skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    unknown = set(exception_map) - actual_skills
    errors.extend(f"exception names unknown skill: {name}" for name in sorted(unknown))

    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        skill = path.parent.name
        size = path.stat().st_size
        if size > hard:
            exception = exception_map.get(skill)
            if exception is None:
                errors.append(f"{skill}: {size} bytes exceeds hard threshold {hard}")
            elif size > exception.get("max_bytes", -1):
                errors.append(f"{skill}: {size} bytes exceeds exception max {exception['max_bytes']}")
            else:
                print(f"CONTEXT_BUDGET_EXCEPTION {skill}={size}")
        elif skill in exception_map:
            errors.append(f"{skill}: exception is only valid for an entrypoint above hard_bytes")
        if size > warning:
            print(f"CONTEXT_BUDGET_WARNING {skill}={size}")

        text = path.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not target.lower().endswith(".md"):
                continue
            resolved = (path.parent / target).resolve()
            if ROOT not in resolved.parents and resolved != ROOT:
                errors.append(f"{skill}: local Markdown link escapes repository: {target}")
            elif not resolved.is_file():
                errors.append(f"{skill}: missing local Markdown link: {target}")

    if errors:
        return fail(errors)
    print("CONTEXT_BUDGET_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
