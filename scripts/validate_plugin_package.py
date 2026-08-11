"""Validate this repository's root Codex plugin package offline."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ".codex-plugin/plugin.json"
MARKETPLACE = ".agents/plugins/marketplace.json"
REPOSITORY_URL = "https://github.com/JackSmack1971/codex-skills.git"
CANONICAL_SKILL_COUNT = 50
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: invalid JSON ({exc})")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: must be a JSON object")
        return None
    return value


def require_string(payload: dict[str, Any], key: str, label: str, errors: list[str]) -> str | None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{key}: must be a non-empty string")
        return None
    return value


def contained_path(root: Path, raw: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(raw, str) or not raw.startswith("./"):
        errors.append(f"{label}: must be a `./`-relative path")
        return None
    candidate = (root / raw[2:]).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label}: path escapes the repository")
        return None
    return candidate


def validate_manifest(root: Path, errors: list[str]) -> dict[str, Any] | None:
    manifest = load_object(root / MANIFEST, MANIFEST, errors)
    if manifest is None:
        return None
    name = require_string(manifest, "name", MANIFEST, errors)
    if name and NAME.fullmatch(name) is None:
        errors.append(f"{MANIFEST}.name: must be kebab-case")
    version = require_string(manifest, "version", MANIFEST, errors)
    if version and SEMVER.fullmatch(version) is None:
        errors.append(f"{MANIFEST}.version: must be semver")
    require_string(manifest, "description", MANIFEST, errors)

    skills = contained_path(root, manifest.get("skills"), f"{MANIFEST}.skills", errors)
    if skills != (root / "skills").resolve():
        errors.append(f"{MANIFEST}.skills: must resolve to `./skills/`")
    elif not skills.is_dir():
        errors.append("skills: canonical directory is missing")
    elif len(list(skills.glob("*/SKILL.md"))) != CANONICAL_SKILL_COUNT:
        errors.append(f"skills: expected {CANONICAL_SKILL_COUNT} canonical skill packages")

    path_fields = {"skills", "hooks", "mcpServers", "apps"}
    for key in path_fields & manifest.keys():
        if key != "skills" and isinstance(manifest[key], str):
            path = contained_path(root, manifest[key], f"{MANIFEST}.{key}", errors)
            if path is not None and not path.exists():
                errors.append(f"{MANIFEST}.{key}: referenced path does not exist")
    return manifest


def validate_marketplace(root: Path, manifest: dict[str, Any] | None, errors: list[str]) -> None:
    marketplace = load_object(root / MARKETPLACE, MARKETPLACE, errors)
    if marketplace is None:
        return
    require_string(marketplace, "name", MARKETPLACE, errors)
    interface = marketplace.get("interface")
    if not isinstance(interface, dict) or not isinstance(interface.get("displayName"), str) or not interface["displayName"].strip():
        errors.append(f"{MARKETPLACE}.interface.displayName: must be a non-empty string")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append(f"{MARKETPLACE}.plugins: must contain exactly one root plugin")
        return
    entry = plugins[0]
    if not isinstance(entry, dict):
        errors.append(f"{MARKETPLACE}.plugins[0]: must be an object")
        return
    plugin_name = manifest.get("name") if manifest else None
    if entry.get("name") != plugin_name:
        errors.append(f"{MARKETPLACE}.plugins[0].name: must match the root manifest")
    source = entry.get("source")
    if isinstance(source, dict) and source.get("source") == "local" and "path" in source:
        contained_path(root, source["path"], f"{MARKETPLACE}.plugins[0].source.path", errors)
    if not isinstance(source, dict) or source.get("source") != "url" or source.get("url") != REPOSITORY_URL:
        errors.append(f"{MARKETPLACE}.plugins[0].source: must be the intended Git-backed root repository")
    elif "path" in source:
        errors.append(f"{MARKETPLACE}.plugins[0].source.path: root Git source must not add a subdirectory")
    policy = entry.get("policy")
    if not isinstance(policy, dict):
        errors.append(f"{MARKETPLACE}.plugins[0].policy: must be an object")
    else:
        if policy.get("installation") not in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}:
            errors.append(f"{MARKETPLACE}.plugins[0].policy.installation: invalid value")
        if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
            errors.append(f"{MARKETPLACE}.plugins[0].policy.authentication: invalid value")
    category = entry.get("category")
    if not isinstance(category, str) or not category.strip():
        errors.append(f"{MARKETPLACE}.plugins[0].category: must be a non-empty string")


def validate_no_duplicate_skill_tree(root: Path, errors: list[str]) -> None:
    canonical = (root / "skills").resolve()
    for skill_md in root.rglob("SKILL.md"):
        if skill_md.resolve().parent.parent != canonical:
            errors.append(f"duplicate canonical skill tree: {skill_md.relative_to(root).as_posix()}")


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    manifest = validate_manifest(root, errors)
    validate_marketplace(root, manifest, errors)
    validate_no_duplicate_skill_tree(root, errors)
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(errors))
        print("PLUGIN_PACKAGE_VALIDATION_FAILED")
        return 1
    print("PLUGIN_PACKAGE_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
