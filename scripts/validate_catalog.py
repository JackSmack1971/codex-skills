"""Validate the repository skill catalog using only the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CATALOG = SKILLS / "catalog.json"
VALID_LEVELS = {"prompt-only", "evaluated", "script-backed", "tested"}
REQUIRED = {
    "name",
    "path",
    "description",
    "category",
    "lifecycle_stage",
    "dependencies",
    "related_skills",
    "capability_level",
    "destructive_actions",
    "validation_artifacts",
}


def frontmatter_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^name:\s*[\"']?([^\"']+?)[\"']?\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def main() -> int:
    errors: list[str] = []
    actual = {
        p.parent.name: p.relative_to(ROOT).as_posix()
        for p in SKILLS.glob("*/SKILL.md")
    }
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"catalog unreadable: {exc}")
        return 1
    records = data.get("skills") if isinstance(data, dict) else None
    if not isinstance(records, list):
        print("catalog must contain a skills list")
        return 1

    names = [r.get("name") for r in records if isinstance(r, dict)]
    paths = [r.get("path") for r in records if isinstance(r, dict)]
    if len(names) != len(set(names)):
        errors.append("duplicate catalog names")
    if len(paths) != len(set(paths)):
        errors.append("duplicate catalog paths")
    catalog_names = set(names)
    aliases: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict):
            errors.append("non-object catalog record")
            continue
        missing = REQUIRED - record.keys()
        if missing:
            errors.append(f"{record.get('name', '<unknown>')}: missing {sorted(missing)}")
            continue
        name = record["name"]
        path = record["path"]
        if name not in actual:
            errors.append(f"extra or missing skill: {name}")
        elif path != actual[name]:
            errors.append(f"{name}: path must be {actual[name]}")
        skill_path = ROOT / path
        if not skill_path.is_file():
            errors.append(f"{name}: nonexistent catalog path")
        elif frontmatter_name(skill_path) != name:
            errors.append(f"{name}: frontmatter-name mismatch")
        if record["capability_level"] not in VALID_LEVELS:
            errors.append(f"{name}: invalid capability label")
        for field in ("dependencies", "related_skills"):
            for ref in record[field]:
                if ref not in catalog_names:
                    errors.append(f"{name}: nonexistent referenced skill {ref}")
        for artifact in record["validation_artifacts"]:
            if not (ROOT / artifact).is_file():
                errors.append(f"{name}: nonexistent validation artifact {artifact}")
        for alias in record.get("aliases", []):
            if not isinstance(alias, str) or not alias.strip():
                errors.append(f"{name}: aliases must be non-empty strings")
                continue
            if alias in aliases and aliases[alias] != name:
                errors.append(f"duplicate alias {alias}")
            aliases[alias] = name
        alias_of = record.get("alias_of")
        if alias_of is not None and (alias_of not in catalog_names or alias_of == name):
            errors.append(f"{name}: invalid alias_of {alias_of}")
        if alias_of is not None and alias_of not in catalog_names:
            errors.append(f"{name}: alias target is not cataloged")
    if set(actual) != catalog_names:
        errors.append("catalog does not exactly match direct skills")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"TOTAL_SKILLS={len(records)}")
    print("CATALOG_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
