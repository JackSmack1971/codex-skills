"""Check deterministic routing-boundary evidence using discovery metadata.

This is a lexical boundary contract, not an imitation of model routing: each
case must have a unique highest overlap with the expected SKILL.md
frontmatter description. It catches stale descriptions and mislabeled cases.
"""

from __future__ import annotations

import json
import re
import sys
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "skills" / "catalog.json"
CASES = ROOT / "tests" / "skill-routing-cases.json"
CLUSTERS = [
    {"grill-me", "grilling"},
    {"pr-review", "review-agent"},
    {"feature-implementation", "vertical-slice", "test-driven-development", "testing-qa"},
    {"improve", "skill-auditor", "context-doctor"},
    {"git-commit", "git-workflow", "github-issue-to-pr", "using-git-worktrees"},
    {"skill-creator", "context7-skill-wizard", "plugin-creator"},
    {"product-discovery", "product-spec", "mvp-scope"},
]
STOPWORDS = set("a an and are as at by for from in into is it of on or the this to with use when".split())


def words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2 and word not in STOPWORDS}


def frontmatter_description(path: Path) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_frontmatter = False
    description: list[str] = []
    collecting = False
    for line in lines:
        if line.strip() == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        if not in_frontmatter:
            continue
        if collecting:
            if line.startswith((" ", "\t")):
                description.append(line.strip())
                continue
            break
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            if value in {">", ">-", ">+", "|", "|-", "|+"}:
                collecting = True
            else:
                return value.strip("\"'")
    return " ".join(description) if description else None


def declared_pairs(records: list[dict]) -> set[frozenset[str]]:
    pairs: set[frozenset[str]] = set()
    names = {record["name"] for record in records}
    for record in records:
        for other in record.get("intentional_overlaps", []):
            if other not in names:
                raise ValueError(f"{record['name']}: intentional overlap references {other}")
            pairs.add(frozenset((record["name"], other)))
    return pairs


def declarations_by_skill(records: list[dict]) -> dict[str, set[str]]:
    return {
        record["name"]: set(record.get("intentional_overlaps", []))
        for record in records
    }


def main() -> int:
    errors: list[str] = []
    try:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        case_data = json.loads(CASES.read_text(encoding="utf-8"))
        cases = case_data["cases"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"input unreadable: {exc}")
        return 1

    if case_data.get("contract") != "unique lexical evidence against SKILL.md frontmatter descriptions":
        errors.append("routing cases must declare the deterministic lexical evidence contract")
    records = catalog.get("skills", [])
    names = {record.get("name") for record in records}
    descriptions: dict[str, str] = {}
    for record in records:
        name = record.get("name")
        path = ROOT / record.get("path", "")
        if not isinstance(name, str) or not path.is_file():
            continue
        description = frontmatter_description(path)
        if not description:
            errors.append(f"{name}: missing SKILL.md frontmatter description")
        else:
            descriptions[name] = description
    alias_targets: dict[str, str] = {}
    for record in records:
        name = record["name"]
        target = record.get("alias_of")
        if target is not None:
            if target not in names or target == name:
                errors.append(f"invalid alias target: {name} -> {target}")
        for alias in record.get("aliases", []):
            key = alias.lstrip("/")
            if key in names and next((item.get("alias_of") for item in records if item.get("name") == key), None) != name:
                errors.append(f"alias does not resolve to target: {alias} -> {name}")
            if key in alias_targets and alias_targets[key] != name:
                errors.append(f"alias maps to multiple skills: {alias}")
            alias_targets[key] = name

    seen: dict[str, tuple[str, ...]] = {}
    counts: dict[str, dict[str, int]] = {name: {"positive": 0, "exclusion": 0} for name in names}
    for case in cases:
        skill = case.get("skill")
        kind = case.get("kind")
        text = case.get("input")
        route_to = case.get("route_to", skill)
        if (
            skill not in names
            or kind not in {"positive", "exclusion"}
            or not isinstance(text, str)
            or not text.strip()
            or route_to not in names
            or (kind == "exclusion" and route_to == skill)
            or skill not in descriptions
            or route_to not in descriptions
        ):
            errors.append(f"invalid routing case: {case.get('id', '<unknown>')}")
            continue
        expected_name = skill if kind == "positive" else route_to
        scores = {
            name: len(words(text) & words(description))
            for name, description in descriptions.items()
        }
        best_score = max(scores.values(), default=0)
        best = [name for name, score in scores.items() if score == best_score]
        if best_score == 0 or best != [expected_name]:
            errors.append(
                f"{case.get('id', '<unknown>')}: expected unique lexical route {expected_name}, got {best or 'none'}"
            )
        expected = (expected_name,)
        normalized = " ".join(text.lower().split())
        if normalized in seen:
            if seen[normalized] != expected:
                errors.append(f"contradictory expected mappings: {case.get('id', '<unknown>')}")
            else:
                errors.append(f"duplicate routing example: {case.get('id', '<unknown>')}")
        seen[normalized] = expected
        counts[skill][kind] += 1

    for cluster in CLUSTERS:
        for skill in cluster:
            if counts.get(skill, {}).get("positive", 0) < 3:
                errors.append(f"{skill}: fewer than 3 positive routing examples")
            if counts.get(skill, {}).get("exclusion", 0) < 2:
                errors.append(f"{skill}: fewer than 2 exclusion routing examples")

    try:
        overlaps = declared_pairs(records)
    except ValueError as exc:
        errors.append(str(exc))
        overlaps = set()
    declared_by = declarations_by_skill(records)
    for cluster in CLUSTERS:
        for left_name, right_name in combinations(sorted(cluster), 2):
            if (
                frozenset((left_name, right_name)) not in overlaps
                or right_name not in declared_by.get(left_name, set())
                or left_name not in declared_by.get(right_name, set())
            ):
                errors.append(f"missing intentional overlap declaration: {left_name} / {right_name}")
    for index, left in enumerate(records):
        for right in records[index + 1 :]:
            pair = frozenset((left["name"], right["name"]))
            left_words = words(descriptions.get(left["name"], ""))
            right_words = words(descriptions.get(right["name"], ""))
            union = left_words | right_words
            similarity = len(left_words & right_words) / len(union) if union else 0
            if len(left_words & right_words) >= 4 and similarity >= 0.45 and pair not in overlaps:
                errors.append(f"undeclared lexical overlap: {left['name']} / {right['name']}")

    if errors:
        print("\n".join(errors))
        return 1
    print("TRIGGER_BOUNDARIES_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
