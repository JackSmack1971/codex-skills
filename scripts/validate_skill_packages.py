"""Validate every canonical skill as an isolated, standalone package."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
RESOURCE = re.compile(r"(?:scripts|references)/[A-Za-z0-9._/-]+")
EXTERNAL = re.compile(r"^(?:[a-z]+:)?//|^mailto:|^#", re.I)
HARDCODED_SKILL_COMMAND = re.compile(
    r"\b(?:python(?:3)?|py)\s+(?:\"|')?(?:\.agents/skills/|\.codex/skills/|\$HOME/\.agents/skills/|~/\.agents/skills/)",
    re.I,
)


def _contained(root: Path, raw: str) -> Path | None:
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def package_errors(package: Path) -> list[str]:
    errors: list[str] = []
    skill_file = package / "SKILL.md"
    if not skill_file.is_file():
        return [f"{package.name}: SKILL.md is missing"]
    prefix = package.name

    markdown = [skill_file, *sorted((package / "references").rglob("*.md"))] if (package / "references").is_dir() else [skill_file]
    for document in markdown:
        text = document.read_text(encoding="utf-8")
        relative = document.relative_to(package).as_posix()
        if HARDCODED_SKILL_COMMAND.search(text):
            errors.append(f"{prefix}/{relative}: executable command hard-codes a skill installation root")
        for raw in LINK.findall(text):
            target = raw.strip().split("#", 1)[0].strip("<>")
            if not target or EXTERNAL.match(target):
                continue
            resolved = _contained(package, str(document.parent.relative_to(package) / target))
            if resolved is None:
                errors.append(f"{prefix}/{relative}: link escapes package: {target}")
            elif not resolved.exists():
                errors.append(f"{prefix}/{relative}: missing linked resource: {target}")

    text = skill_file.read_text(encoding="utf-8")
    for code in re.findall(r"`([^`]+)`", text):
        for target in RESOURCE.findall(code):
            resolved = _contained(package, target)
            if resolved is None:
                errors.append(f"{prefix}: resource escapes package: {target}")
            elif not resolved.exists():
                errors.append(f"{prefix}: missing bundled resource: {target}")
    return sorted(set(errors))


def validate(skills_root: Path = ROOT / "skills") -> list[str]:
    errors: list[str] = []
    packages = sorted(path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())
    with tempfile.TemporaryDirectory(prefix="isolated-skills-") as directory:
        isolated = Path(directory)
        for package in packages:
            target = isolated / package.name
            shutil.copytree(package, target)
            errors.extend(package_errors(target))
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills_root", nargs="?", type=Path, default=ROOT / "skills")
    args = parser.parse_args(argv)
    errors = validate(args.skills_root)
    if errors:
        print("\n".join(errors))
        print("STANDALONE_SKILL_VALIDATION_FAILED")
        return 1
    print("STANDALONE_SKILL_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
