from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_trigger_overlap import (
    Profile,
    audit,
    discover_candidates,
    generated_cases,
    pair_distinctive_terms,
    semantic_words,
    validate_cases,
    words,
)


class RoutingBoundaryAuditorTests(unittest.TestCase):
    def test_semantic_normalization_preserves_explainable_equivalence(self):
        self.assertEqual(semantic_words("review repo docs"), {"audit", "docs", "codebase"})
        self.assertNotIn("the", words("review the repository"))

    def test_candidate_detection_combines_declarations_aliases_and_fixtures(self):
        profiles = {
            "alpha": Profile("alpha", "review repository", {"review", "repository"}, {"audit", "codebase"}),
            "beta": Profile("beta", "audit codebase", {"audit", "codebase"}, {"audit", "codebase"}),
        }
        records = [
            {"name": "alpha", "intentional_overlaps": ["beta"]},
            {"name": "beta", "intentional_overlaps": ["alpha"]},
        ]
        cases = [{"kind": "exclusion", "skill": "alpha", "route_to": "beta"}]

        candidates, declared, errors = discover_candidates(profiles, records, cases)

        self.assertEqual(errors, [])
        self.assertEqual(len(declared), 1)
        self.assertEqual(set(candidates[0].reasons), {"declared", "fixture"})

    def test_nonreciprocal_declaration_and_missing_contracts_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("alpha", "beta"):
                path = root / "skills" / name / "SKILL.md"
                path.parent.mkdir(parents=True)
                path.write_text(f"---\nname: {name}\ndescription: Route {name} work only.\n---\n", encoding="utf-8")
            catalog = {"skills": [
                {"name": "alpha", "path": "skills/alpha/SKILL.md", "intentional_overlaps": ["beta"]},
                {"name": "beta", "path": "skills/beta/SKILL.md"},
            ]}
            errors, _, _, _ = audit(catalog, {"version": 1, "cases": []}, root)
        self.assertTrue(any("schema version" in error for error in errors))
        self.assertTrue(any("non-reciprocal" in error for error in errors))

    def test_real_fixture_contract_passes(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / "skills/catalog.json").read_text(encoding="utf-8"))
        cases = json.loads((root / "tests/skill-routing-cases.json").read_text(encoding="utf-8"))
        errors, _, candidates, _ = audit(catalog, cases, root)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(candidates), 20)

    def test_discovered_candidate_requires_declaration_or_disposition(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / "skills/catalog.json").read_text(encoding="utf-8"))
        cases = json.loads((root / "tests/skill-routing-cases.json").read_text(encoding="utf-8"))
        cases["candidate_dispositions"] = []
        errors, _, _, _ = audit(catalog, cases, root)
        self.assertIn("undispositioned candidate overlap: visual-plan / visual-recap", errors)

    def test_distinctive_terms_are_specific_to_the_pair(self):
        left = Profile("left", "shared alpha", {"shared", "alpha"}, {"shared", "alpha"})
        right = Profile("right", "shared beta", {"shared", "beta"}, {"shared", "beta"})
        self.assertEqual(pair_distinctive_terms(left, right), ({"alpha"}, {"beta"}))
        review = Profile("review", "review", {"review"}, {"audit"})
        audit_profile = Profile("audit", "audit", {"audit"}, {"audit"})
        self.assertEqual(pair_distinctive_terms(review, audit_profile), (set(), set()))

    def test_only_curated_exclusions_satisfy_boundary_coverage(self):
        profiles = {
            "alpha": Profile("alpha", "alpha", {"alpha"}, {"alpha"}),
            "beta": Profile("beta", "beta", {"beta"}, {"beta"}),
        }
        case = {"id": "proposal", "skill": "alpha", "kind": "exclusion", "route_to": "beta",
                "source": "generated-proposal", "input": "beta"}
        errors, coverage = validate_cases([case], profiles)
        self.assertEqual(errors, [])
        self.assertEqual(coverage, {})

    def test_generation_is_stable_and_does_not_mutate_existing_cases(self):
        profiles = {
            "alpha": Profile("alpha", "alpha", {"alpha"}, {"alpha"}),
            "beta": Profile("beta", "beta", {"beta"}, {"beta"}),
        }
        from scripts.check_trigger_overlap import Candidate
        candidates = [Candidate("alpha", "beta", ("declared",), 0, 0)]
        existing: list[dict] = []
        first = generated_cases(candidates, profiles, existing)
        self.assertEqual(first, generated_cases(candidates, profiles, existing))
        self.assertEqual(existing, [])
        self.assertEqual(generated_cases(candidates, profiles, existing, {frozenset(("alpha", "beta"))}), [])


if __name__ == "__main__":
    unittest.main()
