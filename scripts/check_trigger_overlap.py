"""Audit deterministic routing boundaries using canonical skill metadata.

This is an explainable, offline contract rather than an imitation of model
routing.  It combines lexical and lightweight semantic candidate discovery,
checks every declared boundary pair, measures distinctive terms, and validates
or proposes routing cases.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "skills" / "catalog.json"
CASES = ROOT / "tests" / "skill-routing-cases.json"
STOPWORDS = set("a an and are as at be by for from in into is it of on or the this to with use when".split())
SEMANTIC_GROUPS = (
    {"pr", "pull", "request", "merge"},
    {"test", "testing", "qa", "verification", "validate", "validation"},
    {"build", "create", "generate", "implement", "scaffold"},
    {"inspect", "review", "audit", "evaluate"},
    {"repository", "repo", "codebase"},
    {"documentation", "docs", "guide"},
    {"feature", "capability", "behavior"},
)
SEMANTIC_CANON = {term: sorted(group)[0] for group in SEMANTIC_GROUPS for term in group}


@dataclass
class Profile:
    name: str
    description: str
    tokens: set[str]
    semantic_tokens: set[str]
    distinctive: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Candidate:
    left: str
    right: str
    reasons: tuple[str, ...]
    lexical_similarity: float
    semantic_similarity: float


def words(text: str) -> set[str]:
    return {
        word for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2 and word not in STOPWORDS
    }


def semantic_words(text: str) -> set[str]:
    return {SEMANTIC_CANON.get(word, word) for word in words(text)}


def similarity(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


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


def declared_pairs(records: list[dict]) -> tuple[set[frozenset[str]], list[str]]:
    errors: list[str] = []
    pairs: set[frozenset[str]] = set()
    names = {record.get("name") for record in records}
    declarations = {record.get("name"): set(record.get("intentional_overlaps", [])) for record in records}
    for name, others in declarations.items():
        for other in others:
            if other not in names or other == name:
                errors.append(f"{name}: intentional overlap references invalid skill {other}")
                continue
            pairs.add(frozenset((name, other)))
            if name not in declarations.get(other, set()):
                errors.append(f"non-reciprocal intentional overlap: {name} / {other}")
    return pairs, errors


def build_profiles(records: list[dict], root: Path = ROOT) -> tuple[dict[str, Profile], list[str]]:
    profiles: dict[str, Profile] = {}
    errors: list[str] = []
    for record in records:
        name, relative = record.get("name"), record.get("path")
        path = root / relative if isinstance(relative, str) else root
        if not isinstance(name, str) or not path.is_file():
            errors.append(f"invalid catalog record: {name or '<unknown>'}")
            continue
        description = frontmatter_description(path)
        if not description:
            errors.append(f"{name}: missing SKILL.md frontmatter description")
            continue
        profiles[name] = Profile(name, description, words(description), semantic_words(description))
    frequency = Counter(token for profile in profiles.values() for token in profile.tokens)
    for profile in profiles.values():
        profile.distinctive = {token for token in profile.tokens if frequency[token] <= 2}
    return profiles, errors


def pair_distinctive_terms(left: Profile, right: Profile) -> tuple[set[str], set[str]]:
    """Return terms that distinguish each member of this specific boundary."""
    left_terms = {term for term in left.tokens if SEMANTIC_CANON.get(term, term) not in right.semantic_tokens}
    right_terms = {term for term in right.tokens if SEMANTIC_CANON.get(term, term) not in left.semantic_tokens}
    return left_terms, right_terms


def reviewed_dispositions(case_data: dict, names: set[str]) -> tuple[dict[frozenset[str], dict], list[str]]:
    """Validate explicit decisions for discovered pairs that are not boundaries."""
    dispositions: dict[frozenset[str], dict] = {}
    errors: list[str] = []
    records = case_data.get("candidate_dispositions", [])
    if not isinstance(records, list):
        return {}, ["candidate_dispositions must be a list"]
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"candidate disposition {index}: must be an object")
            continue
        pair = record.get("pair")
        status = record.get("status")
        reason = record.get("reason")
        if (not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(name, str) for name in pair)
                or pair[0] == pair[1] or not set(pair) <= names):
            errors.append(f"candidate disposition {index}: invalid pair")
            continue
        key = frozenset(pair)
        if key in dispositions:
            errors.append(f"duplicate candidate disposition: {' / '.join(sorted(key))}")
        if status not in {"reviewed", "dismissed"}:
            errors.append(f"candidate disposition {' / '.join(sorted(key))}: invalid status")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"candidate disposition {' / '.join(sorted(key))}: reason is required")
        dispositions[key] = record
    return dispositions, errors

def discover_candidates(
    profiles: dict[str, Profile], records: list[dict], cases: list[dict]
) -> tuple[list[Candidate], set[frozenset[str]], list[str]]:
    declared, errors = declared_pairs(records)
    reasons: dict[frozenset[str], set[str]] = defaultdict(set)
    for pair in declared:
        reasons[pair].add("declared")
    for record in records:
        if record.get("alias_of") in profiles and record.get("name") in profiles:
            reasons[frozenset((record["name"], record["alias_of"]))].add("alias")
    for case in cases:
        if case.get("kind") == "exclusion" and case.get("skill") in profiles and case.get("route_to") in profiles:
            reasons[frozenset((case["skill"], case["route_to"]))].add("fixture")
    for left, right in combinations(sorted(profiles), 2):
        lexical = similarity(profiles[left].tokens, profiles[right].tokens)
        semantic = similarity(profiles[left].semantic_tokens, profiles[right].semantic_tokens)
        shared = len(profiles[left].tokens & profiles[right].tokens)
        if shared >= 4 and lexical >= 0.25:
            reasons[frozenset((left, right))].add("lexical")
        if semantic >= 0.30 and len(profiles[left].semantic_tokens & profiles[right].semantic_tokens) >= 4:
            reasons[frozenset((left, right))].add("semantic")
    candidates = []
    for pair, why in reasons.items():
        left, right = sorted(pair)
        candidates.append(Candidate(
            left, right, tuple(sorted(why)),
            similarity(profiles[left].tokens, profiles[right].tokens),
            similarity(profiles[left].semantic_tokens, profiles[right].semantic_tokens),
        ))
    return sorted(candidates, key=lambda item: (item.left, item.right)), declared, errors


def score_route(text: str, profiles: dict[str, Profile]) -> tuple[list[str], int]:
    lexical, semantic = words(text), semantic_words(text)
    scores = {
        name: (2 * len(lexical & profile.tokens)) + len(semantic & profile.semantic_tokens)
        for name, profile in profiles.items()
    }
    best_score = max(scores.values(), default=0)
    return sorted(name for name, score in scores.items() if score == best_score), best_score


def validate_cases(cases: list[dict], profiles: dict[str, Profile]) -> tuple[list[str], dict[frozenset[str], set[tuple[str, str]]]]:
    errors: list[str] = []
    coverage: dict[frozenset[str], set[tuple[str, str]]] = defaultdict(set)
    seen: dict[str, str] = {}
    counts: Counter[tuple[str, str]] = Counter()
    ids: set[str] = set()
    for case in cases:
        case_id, skill, kind, text = case.get("id"), case.get("skill"), case.get("kind"), case.get("input")
        route_to = case.get("route_to", skill)
        if not isinstance(case_id, str) or case_id in ids:
            errors.append(f"duplicate or missing routing case id: {case_id or '<unknown>'}")
        ids.add(case_id)
        if (skill not in profiles or route_to not in profiles or kind not in {"positive", "exclusion"}
                or not isinstance(text, str) or not text.strip() or (kind == "exclusion" and route_to == skill)):
            errors.append(f"invalid routing case: {case_id or '<unknown>'}")
            continue
        expected = skill if kind == "positive" else route_to
        best, best_score = score_route(text, profiles)
        if best_score == 0 or best != [expected]:
            errors.append(f"{case_id}: expected unique deterministic route {expected}, got {best or 'none'}")
        normalized = " ".join(text.lower().split())
        if normalized in seen:
            label = "contradictory expected mappings" if seen[normalized] != expected else "duplicate routing example"
            errors.append(f"{label}: {case_id}")
        seen[normalized] = expected
        counts[(skill, kind)] += 1
        if kind == "exclusion" and case.get("source") == "curated":
            coverage[frozenset((skill, route_to))].add((skill, route_to))
            boundary = case.get("boundary")
            if boundary is not None and (not isinstance(boundary, list) or len(boundary) != 2 or frozenset(boundary) != frozenset((skill, route_to))):
                errors.append(f"{case_id}: boundary must match skill and route_to")
    involved = {name for pair in coverage for name in pair}
    for name in involved:
        if counts[(name, "positive")] < 3:
            errors.append(f"{name}: fewer than 3 positive routing examples")
        if counts[(name, "exclusion")] < 2:
            errors.append(f"{name}: fewer than 2 exclusion routing examples")
    return errors, coverage


def audit(catalog: dict, case_data: dict, root: Path = ROOT) -> tuple[list[str], list[str], list[Candidate], dict[str, Profile]]:
    errors: list[str] = []
    warnings: list[str] = []
    if case_data.get("version") != 2:
        errors.append("routing cases schema version must be 2")
    contracts = set(case_data.get("contracts", []))
    required = {"unique deterministic evidence", "pairwise boundary evidence", "distinctive-term evidence"}
    if not required <= contracts:
        errors.append("routing cases must declare all routing-boundary contracts")
    records, cases = catalog.get("skills", []), case_data.get("cases", [])
    profiles, profile_errors = build_profiles(records, root)
    errors.extend(profile_errors)
    names = set(profiles)
    alias_targets: dict[str, str] = {}
    for record in records:
        name, target = record.get("name"), record.get("alias_of")
        if target is not None and (target not in names or target == name):
            errors.append(f"invalid alias target: {name} -> {target}")
        for alias in record.get("aliases", []):
            key = alias.lstrip("/")
            if key in names and next((item.get("alias_of") for item in records if item.get("name") == key), None) != name:
                errors.append(f"alias does not resolve to target: {alias} -> {name}")
            if key in alias_targets and alias_targets[key] != name:
                errors.append(f"alias maps to multiple skills: {alias}")
            alias_targets[key] = name
    candidates, declared, declaration_errors = discover_candidates(profiles, records, cases)
    errors.extend(declaration_errors)
    dispositions, disposition_errors = reviewed_dispositions(case_data, names)
    errors.extend(disposition_errors)
    candidate_pairs = {frozenset((candidate.left, candidate.right)) for candidate in candidates}
    for pair in dispositions.keys() - candidate_pairs:
        errors.append(f"candidate disposition does not match a discovered pair: {' / '.join(sorted(pair))}")
    case_errors, coverage = validate_cases(cases, profiles)
    errors.extend(case_errors)
    for candidate in candidates:
        pair = frozenset((candidate.left, candidate.right))
        directions = coverage.get(pair, set())
        alias = any(record.get("name") in pair and record.get("alias_of") in pair for record in records)
        if pair not in declared and pair not in dispositions:
            errors.append(f"undispositioned candidate overlap: {candidate.left} / {candidate.right}")
        if "declared" in candidate.reasons and not alias:
            required_directions = {(candidate.left, candidate.right), (candidate.right, candidate.left)}
            if not required_directions <= directions:
                errors.append(f"incomplete pairwise boundary cases: {candidate.left} / {candidate.right}")
        left_terms, right_terms = pair_distinctive_terms(profiles[candidate.left], profiles[candidate.right])
        if not left_terms or not right_terms:
            warnings.append(f"weak distinctive-term boundary: {candidate.left} / {candidate.right}")
    return errors, warnings, candidates, profiles


def generated_cases(
    candidates: list[Candidate], profiles: dict[str, Profile], existing: list[dict],
    excluded_pairs: set[frozenset[str]] | None = None,
) -> list[dict]:
    covered = {
        (case.get("skill"), case.get("route_to")) for case in existing
        if case.get("kind") == "exclusion" and case.get("source") == "curated"
    }
    proposals: list[dict] = []
    for candidate in candidates:
        if frozenset((candidate.left, candidate.right)) in (excluded_pairs or set()):
            continue
        for source, destination in ((candidate.left, candidate.right), (candidate.right, candidate.left)):
            if (source, destination) in covered:
                continue
            _, destination_terms = pair_distinctive_terms(profiles[source], profiles[destination])
            terms = sorted(destination_terms)[:4]
            if not terms:
                continue
            text = f"Route this request using {' '.join(terms)}."
            best, score = score_route(text, profiles)
            if score and best == [destination]:
                proposals.append({
                    "id": f"generated-{source}-to-{destination}", "skill": source,
                    "kind": "exclusion", "route_to": destination,
                    "boundary": [source, destination], "source": "generated-proposal", "input": text,
                })
    return proposals


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--cases", type=Path, default=CASES)
    parser.add_argument("--generate-cases", type=Path, metavar="PATH")
    parser.add_argument("--report-json", action="store_true")
    args = parser.parse_args(argv)
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        case_data = json.loads(args.cases.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input unreadable: {exc}")
        return 1
    errors, warnings, candidates, profiles = audit(catalog, case_data, args.catalog.resolve().parents[1])
    if args.generate_cases:
        dispositions, _ = reviewed_dispositions(case_data, set(profiles))
        payload = {"version": 1, "source": "routing-boundary-auditor", "proposals": generated_cases(
            candidates, profiles, case_data.get("cases", []), set(dispositions)
        )}
        args.generate_cases.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.report_json:
        print(json.dumps({
            "status": "fail" if errors else "pass", "errors": errors, "warnings": warnings,
            "candidates": [{**candidate.__dict__, "distinctive": dict(zip(
                (candidate.left, candidate.right),
                map(sorted, pair_distinctive_terms(profiles[candidate.left], profiles[candidate.right])),
            ))} for candidate in candidates],
        }, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        if errors:
            print("\n".join(errors))
        else:
            print(f"ROUTING_BOUNDARIES_OK ({len(candidates)} candidates, {len(warnings)} warnings)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
