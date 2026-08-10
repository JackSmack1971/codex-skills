"""Check the catalog's explicit routing boundaries using only the standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "skills" / "catalog.json"
CASES = ROOT / "tests" / "skill-routing-cases.json"
CLUSTERS = [
    {"grill-me", "grilling"},
    {"pr-review", "review-agent"},
    {"testing-qa", "test-driven-development"},
    {"skill-creator", "context7-skill-wizard"},
    {"product-discovery", "product-spec", "mvp-scope"},
]
STOPWORDS = set("a an and are as at by for from in into is it of on or the this to with use when".split())


def words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2 and word not in STOPWORDS}


def declared_pairs(records: list[dict]) -> set[frozenset[str]]:
    pairs: set[frozenset[str]] = set()
    names = {record["name"] for record in records}
    for record in records:
        for other in record.get("intentional_overlaps", []):
            if other not in names:
                raise ValueError(f"{record['name']}: intentional overlap references {other}")
            pairs.add(frozenset((record["name"], other)))
    return pairs


def main() -> int:
    errors: list[str] = []
    try:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"input unreadable: {exc}")
        return 1

    records = catalog.get("skills", [])
    names = {record.get("name") for record in records}
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
        if skill not in names or kind not in {"positive", "exclusion"} or not isinstance(text, str) or not text.strip():
            errors.append(f"invalid routing case: {case.get('id', '<unknown>')}")
            continue
        expected = (skill,) if kind == "positive" else ()
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
    for index, left in enumerate(records):
        for right in records[index + 1 :]:
            pair = frozenset((left["name"], right["name"]))
            left_words, right_words = words(left["description"]), words(right["description"])
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
